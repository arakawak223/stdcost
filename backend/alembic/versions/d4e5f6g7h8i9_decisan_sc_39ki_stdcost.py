"""decisan_sc_39ki_stdcost - 39期標準原価を決算用SCの値に更新

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-04-27 00:00:00.000000

Changes:
  1. CrudeProductType enum: HIpa, LP, press を追加（決算用SC仕掛品.xlsxの追加3品目）
  2. crude_products: HIpa / LP / press の3レコードを挿入
  3. crude_product_standard_costs: 39期の全レコードを決算用SC値に更新
     - R1/R2/R3 の値を実績按分値に置換
     - other を 1200 → 1080 に修正
     - HIpa(1283) / LP(2002.0805) / press(359.3024) を新規挿入
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd4e5f6g7h8i9'
down_revision: str = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 決算用SC仕掛品.xlsx「仕掛品標準単価一覧表（貼付）」の39期標準単価
# (code, prior_process, material, labor, overhead, total)
CRUDE_STD_DATA = [
    ("R1",    "0",        "296.3265", "251.1711", "30", "577.4976"),
    ("R2",    "0",        "541.3968", "269.5892", "60", "870.9860"),
    ("R3",    "0",        "531.7134", "476.8998", "90", "1098.6131"),
    ("R",     "878",      "0",        "0",        "30", "908"),
    ("Rri",   "908",      "14.1184",  "44",       "30", "996.1184"),
    ("RB",    "996.1184", "0",        "0.4",      "30", "1026.5184"),
    ("P",     "1026.5184","0",        "237",      "30", "1293.5184"),
    ("Rma",   "996.1184", "79",       "69.9",     "30", "1175.0184"),
    ("MP",    "1175.0184","0",        "168.3",    "30", "1373.3184"),
    ("RG",    "996.1184", "41",       "61.3",     "30", "1128.4184"),
    ("RGI",   "1128.4184","0",        "228.8",    "30", "1387.2184"),
    ("GP",    "1387.2184","0",        "105.9",    "30", "1523.1184"),
    ("LPA",   "996.1184", "0",        "469.5",    "30", "1495.6184"),
    ("Rshi",  "908",      "0",        "53",       "30", "991"),
    ("PE",    "991",      "0",        "192",      "30", "1213"),
    ("FEB",   "908",      "0",        "478",      "30", "1416"),
    ("T",     "1416",     "0",        "137",      "30", "1583"),
    ("RX",    "735",      "0",        "82",       "30", "847"),
    ("HI",    "1142",     "0",        "4",        "30", "1176"),
    ("HIR",   "1176",     "0",        "8",        "30", "1214"),
    ("PX",    "1214",     "0",        "96",       "30", "1340"),
    ("PXA",   "1340",     "0",        "424",      "30", "1794"),
    ("HIA",   "1176",     "0",        "48",       "30", "1254"),
    ("HIB",   "1254",     "0",        "0",        "30", "1284"),
    ("HIpa",  "1253",     "0",        "0",        "30", "1283"),
    ("HIBkai","1284",     "0",        "0",        "30", "1314"),
    ("X",     "1314",     "0",        "94",       "30", "1438"),
    ("XC",    "1438",     "832",      "114",      "30", "2414"),
    ("B",     "1284",     "0",        "141",      "30", "1455"),
    ("BM",    "1455",     "3792",     "503",      "30", "5780"),
    ("G",     "1293.5184","967.2",    "54",       "30", "2344.7184"),
    ("GA",    "2344.7184","0",        "0",        "30", "2374.7184"),
    ("GB",    "2374.7184","0",        "0",        "30", "2404.7184"),
    ("O",     "2404.7184","0",        "110",      "30", "2544.7184"),
    ("FB",    "2544.7184","333",      "85",       "30", "2992.7184"),
    ("plant", "1217",     "0",        "0",        "30", "1247"),
    ("LP",    "1972.0805","0",        "0",        "30", "2002.0805"),
    ("press", "0",        "0",        "0",        "0",  "359.3024"),
    ("other", "0",        "0",        "0",        "0",  "1080"),
]

NOTES = "Excel「決算用SC仕掛品.xlsx」39期標準単価（38期末実績確定）"


def upgrade() -> None:
    # --- 1. enum拡張（autocommit必要）---
    op.execute("COMMIT")
    for val in ("HIpa", "LP", "press"):
        op.execute(f"ALTER TYPE crudeproducttype ADD VALUE IF NOT EXISTS '{val}'")
    op.execute("BEGIN")

    # --- 2. 新規CrudeProduct挿入（HIpa, LP, press）---
    # HIpa: parent=HIB, process_stage=7
    op.execute("""
        INSERT INTO crude_products (id, code, name, crude_type, process_stage, parent_crude_product_id, unit, is_active, is_blend, notes, created_at, updated_at)
        SELECT gen_random_uuid(), 'HIpa', 'HIパ', 'HIpa', 7, p.id, 'kg', true, false,
               '決算用SC: HIB後工程派生品。標準単価 1283円/kg', now(), now()
        FROM crude_products p WHERE p.code = 'HIB'
        ON CONFLICT (code) DO NOTHING
    """)
    op.execute("""
        INSERT INTO crude_products (id, code, name, crude_type, unit, is_active, is_blend, notes, created_at, updated_at)
        VALUES (gen_random_uuid(), 'LP', 'LP', 'LP', 'kg', true, false,
                '決算用SC: 独立評価品目。標準単価 2002円/kg', now(), now())
        ON CONFLICT (code) DO NOTHING
    """)
    op.execute("""
        INSERT INTO crude_products (id, code, name, crude_type, unit, is_active, is_blend, notes, created_at, updated_at)
        VALUES (gen_random_uuid(), 'press', '圧搾カス', 'press', 'kg', true, false,
                '決算用SC: 圧搾残渣（内訳なし）。標準単価 359円/kg', now(), now())
        ON CONFLICT (code) DO NOTHING
    """)

    # --- 3. 39期標準原価を全件UPSERT（39期会計期間が無い場合はWHERE句で自然にno-op）---
    for code, prior, mat, labor, oh, total in CRUDE_STD_DATA:
        op.execute(f"""
            INSERT INTO crude_product_standard_costs (
                id, crude_product_id, period_id,
                material_cost, labor_cost, overhead_cost, prior_process_cost,
                total_cost, unit_cost, standard_quantity, notes,
                created_at, updated_at
            )
            SELECT
                gen_random_uuid(), cp.id, fp.id,
                {mat}, {labor}, {oh}, {prior},
                {total}, {total}, 1, '{NOTES}',
                now(), now()
            FROM crude_products cp, fiscal_periods fp
            WHERE cp.code = '{code}' AND fp.year = 39 AND fp.month = 1
            ON CONFLICT (crude_product_id, period_id) DO UPDATE SET
                material_cost = EXCLUDED.material_cost,
                labor_cost = EXCLUDED.labor_cost,
                overhead_cost = EXCLUDED.overhead_cost,
                prior_process_cost = EXCLUDED.prior_process_cost,
                total_cost = EXCLUDED.total_cost,
                unit_cost = EXCLUDED.unit_cost,
                notes = EXCLUDED.notes,
                updated_at = now()
        """)


def downgrade() -> None:
    # 新規3件のCrudeProductStandardCostを削除
    op.execute("""
        DELETE FROM crude_product_standard_costs
        WHERE crude_product_id IN (
            SELECT id FROM crude_products WHERE code IN ('HIpa', 'LP', 'press')
        )
    """)
    # 新規3件のCrudeProductを削除
    op.execute("DELETE FROM crude_products WHERE code IN ('HIpa', 'LP', 'press')")
    # NOTE: 既存標準原価値の旧値復元は行わない（変更前の値を保持していないため）
    # NOTE: enum値の削除はPostgreSQLでサポートされていない
