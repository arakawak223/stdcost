"""v53_product_stdcost - 39期製品標準原価をv5-3「製品増減内訳表」AB列で突合・新規4件追加

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-04-29 00:00:00.000000

Changes:
  1. products: 新規4件を追加
     - 20191200088 おいしい青汁 3g×30本（製品課）
     - 20200300013 万田酵素STANDARD 粒 7粒×20包（その他）
     - (有償)20220500015 万田酵素ﾄﾞﾘﾝｸ 50ml(有償支給分)（外注）
     - (有償)20240800028 万田酵素ﾄﾞﾘﾝｸ ﾌﾟﾗｽ 710ml(有償支給分)（外注）
  2. standard_costs: 新規4件をUPSERT（39期1月）
  3. 値が異なる2件(20050300004, 20110800692)は v5-2 値を保持（変更なし）
"""
from typing import Sequence, Union

from alembic import op


revision: str = "e5f6g7h8i9j0"
down_revision: str = "d4e5f6g7h8i9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (code, name, product_type, product_group, sc_code, content_weight_g)
NEW_PRODUCTS = [
    ("20191200088",       "おいしい青汁 3g×30本",                    "in_house_product_dept", "青汁",  "20191200088",       "90"),
    ("20200300013",       "万田酵素STANDARD 粒 7粒×20包",            "special",               "その他", "20200300013",       "0"),
    ("(有償)20220500015", "万田酵素ﾄﾞﾘﾝｸ 50ml(有償支給分)",          "outsourced",            "外注",  "(有償)20220500015", "0"),
    ("(有償)20240800028", "万田酵素ﾄﾞﾘﾝｸ ﾌﾟﾗｽ 710ml(有償支給分)",    "outsourced",            "外注",  "(有償)20240800028", "0"),
]

# (code, crude_product_cost, packaging_cost, labor_cost, overhead_cost, outsourcing_cost, total)
NEW_STD_COSTS = [
    ("20191200088",       0, 0, 0, 0, 0,    784),
    ("20200300013",       0, 0, 0, 0, 0,    463),
    ("(有償)20220500015", 0, 0, 0, 0, 73,    73),
    ("(有償)20240800028", 0, 0, 0, 0, 3068, 3068),
]

NOTES = "Excel「標準原価_製品・資材_2603v5ー3.xlsx」製品増減内訳表 39期標準原価(決算用SC突合済)"


def upgrade() -> None:
    # --- 1. 新規製品マスタ INSERT (既存があればスキップ) ---
    for code, name, ptype, pgroup, sc_code, content_g in NEW_PRODUCTS:
        op.execute(f"""
            INSERT INTO products (
                id, code, name, product_type, product_group, sc_code,
                content_weight_g, unit, standard_lot_size, is_active,
                created_at, updated_at
            )
            VALUES (
                gen_random_uuid(), '{code}', '{name}', '{ptype}', '{pgroup}', '{sc_code}',
                {content_g}, '個', 1, true,
                now(), now()
            )
            ON CONFLICT (code) DO NOTHING
        """)

    # --- 2. 39期標準原価 UPSERT (39期1月が無い場合はWHERE句で自然にno-op) ---
    for code, mae, shz, ro, ke, ga, total in NEW_STD_COSTS:
        op.execute(f"""
            INSERT INTO standard_costs (
                id, product_id, period_id,
                crude_product_cost, packaging_cost, labor_cost, overhead_cost, outsourcing_cost,
                total_cost, unit_cost, lot_size, notes,
                created_at, updated_at
            )
            SELECT
                gen_random_uuid(), p.id, fp.id,
                {mae}, {shz}, {ro}, {ke}, {ga},
                {total}, {total}, 1, '{NOTES}',
                now(), now()
            FROM products p, fiscal_periods fp
            WHERE p.code = '{code}' AND fp.year = 39 AND fp.month = 1
            ON CONFLICT (product_id, period_id) DO UPDATE SET
                crude_product_cost = EXCLUDED.crude_product_cost,
                packaging_cost = EXCLUDED.packaging_cost,
                labor_cost = EXCLUDED.labor_cost,
                overhead_cost = EXCLUDED.overhead_cost,
                outsourcing_cost = EXCLUDED.outsourcing_cost,
                total_cost = EXCLUDED.total_cost,
                unit_cost = EXCLUDED.unit_cost,
                notes = EXCLUDED.notes,
                updated_at = now()
        """)


def downgrade() -> None:
    # 新規4件のStandardCost削除（39期1月に限定）
    codes = ", ".join(f"'{c}'" for c, *_ in NEW_PRODUCTS)
    op.execute(f"""
        DELETE FROM standard_costs
        WHERE product_id IN (SELECT id FROM products WHERE code IN ({codes}))
        AND period_id IN (SELECT id FROM fiscal_periods WHERE year = 39 AND month = 1)
    """)
    # 新規4件の製品削除
    op.execute(f"DELETE FROM products WHERE code IN ({codes})")
