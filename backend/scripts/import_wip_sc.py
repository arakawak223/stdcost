"""決算用SC仕掛品.xlsx から仕掛品(半製品) SC単価を取り込む CLI ラッパー。

ロジック本体は ``app/services/wip_sc_import.py`` にあり、API
(`POST /api/v1/imports/wip-sc`) もこのサービスを共有する。

使い方:
  cd backend
  python -m scripts.import_wip_sc \\
      --period-id 5ce52674-b54a-4ec1-817c-140cbd0dfd80 \\
      --xlsx /workspaces/stdcost/docs/reference/決算用SC仕掛品.xlsx
  # --commit を付けると DB に書き込み (省略時は dry-run でロールバック)
"""
import argparse
import asyncio
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select

from app.db.session import async_session_factory
from app.models.cost import InventoryCategory, InventoryValuation
from app.services.wip_sc_import import process_wip_sc_import


async def run(period_id: uuid.UUID, xlsx_path: str, commit: bool):
    print(f"=== Excel 取込 (period_id={period_id}) ===")
    with open(xlsx_path, "rb") as f:
        content = f.read()
    filename = os.path.basename(xlsx_path)

    async with async_session_factory() as db:
        batch = await process_wip_sc_import(
            db=db,
            file_content=content,
            filename=filename,
            period_id=period_id,
        )
        print(f"  status: {batch.status}")
        print(f"  total_rows: {batch.total_rows}")
        print(f"  success_rows: {batch.success_rows}")
        print(f"  error_rows: {batch.error_rows}")
        print(f"  notes: {batch.notes}")

        if commit:
            await db.commit()
            print("\n=== サマリ (commit 後) ===")
            for cat in (
                InventoryCategory.semi_finished,
                InventoryCategory.product,
                InventoryCategory.merchandise,
                InventoryCategory.crude_product,
                InventoryCategory.raw_material,
                InventoryCategory.sub_material,
            ):
                cnt_res = await db.execute(
                    select(
                        func.count(),
                        func.sum(InventoryValuation.valuation_amount),
                    ).where(
                        InventoryValuation.period_id == period_id,
                        InventoryValuation.category == cat,
                    )
                )
                cnt, total = cnt_res.one()
                priced_res = await db.execute(
                    select(func.count()).where(
                        InventoryValuation.period_id == period_id,
                        InventoryValuation.category == cat,
                        InventoryValuation.standard_unit_price > 0,
                    )
                )
                priced = priced_res.scalar()
                print(
                    f"  {cat.value}: 件数={cnt} priced={priced} "
                    f"total=¥{float(total or 0):,.0f}"
                )
        else:
            await db.rollback()
            print("\n[DRY-RUN] --commit を付与すると DB に書き込みます。")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--period-id", required=True)
    parser.add_argument(
        "--xlsx",
        default="/workspaces/stdcost/docs/reference/決算用SC仕掛品.xlsx",
    )
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("SECRET_KEY", "dev")
    os.environ.setdefault("ANTHROPIC_API_KEY", "dummy")
    asyncio.run(run(uuid.UUID(args.period_id), args.xlsx, args.commit))


if __name__ == "__main__":
    main()
