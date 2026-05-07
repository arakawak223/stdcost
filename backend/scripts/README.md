# backend/scripts/

ワンショットのデータ整備・変換ユーティリティを置く場所。
通常の本番処理は `app/services/` の関数経由で実施し、
ここのスクリプトは「手作業で 1 回だけ実行して状態を整える」用途。

## 在庫評価マスタ補完フロー (38期1月で実施済み)

`4.3期末全在庫` シートを取り込んだ際、`products` マスタに未登録の
`item_code` は `inventory_valuations.product_id = NULL` (孤立) となり、
標準単価が引けず `valuation_amount = 0` になる。これを解消する手順:

```bash
# 1. xlsb シートを xlsx に変換 (pyxlsb 必要: pip install pyxlsb)
cd backend
python -m scripts.convert_xlsb_sheet \
    --src 'docs/reference/第38期原価計算v8(最終))_260225.xlsb' \
    --sheet '4.3期末全在庫' \
    --dst /tmp/4_3_期末全在庫.xlsx

# 2. products マスタ補完 + StandardCost 整備 + 評価金額再計算
python -m scripts.supplement_inventory_masters \
    --period-id 1c533e58-25a8-4e87-9693-e07eb202611a \
    --inventory-xlsx /tmp/4_3_期末全在庫.xlsx \
    --sc-xlsx 'docs/reference/標準原価_製品_2603v5ー2.xlsx'
```

### 38期1月での実行結果 (2026-05-07)

| 区分 | レコード数 | priced | sum_valuation |
|---|---|---|---|
| product       | 344 | 339 (98.5%) | ¥356,274,037 |
| semi_finished |  92 |  25 (27.2%) | ¥19,985,014 |
| sub_material  | 718 | 712 (99.2%) | ¥97,131,194 |
| merchandise   | 762 | 626 (82.2%) | ¥39,021,475 |
| **合計**      |**1916**|**1702 (88.8%)**|**¥512,411,720**|

残りの `unit_price=0` (214件) は中間工程の半製品 (P/PE/T/MP 等) や
販促・内部利用の商品 (「資料セット用」等) で、現状 Excel に標準原価
データが存在しないため手動補正が必要。

補完したマスタは `notes` で追跡可能:
- `products.notes LIKE 'inventory orphan 補完%'`
- `standard_costs.notes LIKE '%4.3期末全在庫 L列単価%'`
- `standard_costs.notes LIKE '%製品標準原価シート%'`
