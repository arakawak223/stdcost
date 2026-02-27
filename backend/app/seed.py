"""Seed data for development based on 万田発酵 actual business data. Run: python -m app.seed"""

import asyncio
import calendar
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.master import (
    AllocationBasis,
    AllocationRule,
    BomHeader,
    BomLine,
    BomType,
    Contractor,
    CostBudget,
    CostCenter,
    CostCenterType,
    CrudeProduct,
    CrudeProductType,
    FiscalPeriod,
    Material,
    MaterialCategory,
    MaterialType,
    PeriodStatus,
    Product,
    ProductType,
)


async def seed_cost_centers(db: AsyncSession) -> None:
    existing = await db.execute(select(CostCenter).limit(1))
    if existing.scalar_one_or_none():
        print("  部門マスタ: スキップ（既存データあり）")
        return

    # 万田発酵の実際の部門構造: 製造部（原体原価計算）と製品課（製品原価計算）が中核
    centers = [
        CostCenter(code="MFG", name="製造部", name_short="製造", center_type=CostCenterType.manufacturing, sort_order=1),
        CostCenter(code="PRD", name="製品課", name_short="製品", center_type=CostCenterType.product, sort_order=2),
        CostCenter(code="QC", name="品質管理課", name_short="品管", center_type=CostCenterType.indirect, sort_order=3),
        CostCenter(code="ADM", name="管理部", name_short="管理", center_type=CostCenterType.indirect, sort_order=4),
        CostCenter(code="RND", name="試験研究部", name_short="試研", center_type=CostCenterType.indirect, sort_order=5),
    ]
    db.add_all(centers)
    await db.flush()
    print(f"  部門マスタ: {len(centers)}件 作成")


async def seed_materials(db: AsyncSession) -> None:
    existing = await db.execute(select(Material).limit(1))
    if existing.scalar_one_or_none():
        print("  原材料マスタ: スキップ（既存データあり）")
        return

    # 万田発酵の実際の原材料（果物・野菜・穀物・海藻・その他）
    materials = [
        # 果物
        Material(code="F01", name="リンゴ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("200.0000")),
        Material(code="F02", name="カキ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("300.0000")),
        Material(code="F03", name="バナナ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("150.0000")),
        Material(code="F04", name="パインアップル", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("250.0000")),
        Material(code="F05", name="ミカン", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("180.0000")),
        Material(code="F06", name="ブドウ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("350.0000")),
        Material(code="F07", name="モモ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("400.0000")),
        Material(code="F08", name="ナシ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("280.0000")),
        Material(code="F09", name="ビワ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("500.0000")),
        Material(code="F10", name="キウイ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("300.0000")),
        Material(code="F11", name="メロン", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("600.0000")),
        Material(code="F12", name="スイカ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("120.0000")),
        Material(code="F13", name="イチゴ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("800.0000")),
        Material(code="F14", name="レモン", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("250.0000")),
        Material(code="F15", name="ユズ", material_type=MaterialType.raw, category=MaterialCategory.fruit, unit="kg", standard_unit_price=Decimal("400.0000")),
        # 野菜
        Material(code="V01", name="ニンジン", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("100.0000")),
        Material(code="V02", name="ゴボウ", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("200.0000")),
        Material(code="V03", name="レンコン", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("300.0000")),
        Material(code="V04", name="ダイコン", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("80.0000")),
        Material(code="V05", name="キャベツ", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("70.0000")),
        Material(code="V06", name="ハクサイ", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("60.0000")),
        Material(code="V07", name="タマネギ", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("80.0000")),
        Material(code="V08", name="ジャガイモ", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("90.0000")),
        Material(code="V09", name="サツマイモ", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("120.0000")),
        Material(code="V10", name="トマト", material_type=MaterialType.raw, category=MaterialCategory.vegetable, unit="kg", standard_unit_price=Decimal("200.0000")),
        # 穀物
        Material(code="G01", name="玄米", material_type=MaterialType.raw, category=MaterialCategory.grain, unit="kg", standard_unit_price=Decimal("300.0000")),
        Material(code="G02", name="大麦", material_type=MaterialType.raw, category=MaterialCategory.grain, unit="kg", standard_unit_price=Decimal("200.0000")),
        Material(code="G03", name="大豆", material_type=MaterialType.raw, category=MaterialCategory.grain, unit="kg", standard_unit_price=Decimal("250.0000")),
        Material(code="G04", name="小麦", material_type=MaterialType.raw, category=MaterialCategory.grain, unit="kg", standard_unit_price=Decimal("180.0000")),
        Material(code="G05", name="トウモロコシ", material_type=MaterialType.raw, category=MaterialCategory.grain, unit="kg", standard_unit_price=Decimal("150.0000")),
        # 海藻
        Material(code="S01", name="ヒジキ", material_type=MaterialType.raw, category=MaterialCategory.seaweed, unit="kg", standard_unit_price=Decimal("800.0000")),
        Material(code="S02", name="ワカメ", material_type=MaterialType.raw, category=MaterialCategory.seaweed, unit="kg", standard_unit_price=Decimal("600.0000")),
        Material(code="S03", name="コンブ", material_type=MaterialType.raw, category=MaterialCategory.seaweed, unit="kg", standard_unit_price=Decimal("700.0000")),
        Material(code="S04", name="ノリ", material_type=MaterialType.raw, category=MaterialCategory.seaweed, unit="kg", standard_unit_price=Decimal("1500.0000")),
        # その他
        Material(code="O01", name="黒砂糖", material_type=MaterialType.raw, category=MaterialCategory.other, unit="kg", standard_unit_price=Decimal("400.0000")),
        Material(code="O02", name="ゴマ", material_type=MaterialType.raw, category=MaterialCategory.other, unit="kg", standard_unit_price=Decimal("600.0000")),
        Material(code="O03", name="ハチミツ", material_type=MaterialType.raw, category=MaterialCategory.other, unit="kg", standard_unit_price=Decimal("1200.0000")),
        Material(code="O04", name="ショウガ", material_type=MaterialType.raw, category=MaterialCategory.other, unit="kg", standard_unit_price=Decimal("350.0000")),
        # 資材
        Material(code="P01", name="ペーストパウチ(150g)", material_type=MaterialType.packaging, unit="個", standard_unit_price=Decimal("30.0000")),
        Material(code="P02", name="分包袋(2.5g)", material_type=MaterialType.packaging, unit="個", standard_unit_price=Decimal("5.0000")),
        Material(code="P03", name="ボトル(150ml)", material_type=MaterialType.packaging, unit="個", standard_unit_price=Decimal("45.0000")),
        Material(code="P04", name="化粧箱", material_type=MaterialType.packaging, unit="個", standard_unit_price=Decimal("80.0000")),
        Material(code="P05", name="段ボール箱", material_type=MaterialType.packaging, unit="個", standard_unit_price=Decimal("120.0000")),
        Material(code="P06", name="ラベル", material_type=MaterialType.packaging, unit="枚", standard_unit_price=Decimal("8.0000")),
    ]
    db.add_all(materials)
    print(f"  原材料マスタ: {len(materials)}件 作成")


async def seed_crude_products(db: AsyncSession) -> None:
    existing = await db.execute(select(CrudeProduct).limit(1))
    if existing.scalar_one_or_none():
        print("  原体マスタ: スキップ（既存データあり）")
        return

    # 万田発酵の原体（原液）: 年度+タイプで管理、3年以上熟成
    crude_products = [
        # 第38期仕込み
        CrudeProduct(code="38R", name="38期レギュラー原体", vintage_year=38, crude_type=CrudeProductType.R, aging_years=0, unit="kg"),
        CrudeProduct(code="38HI", name="38期HI原体", vintage_year=38, crude_type=CrudeProductType.HI, aging_years=0, unit="kg"),
        CrudeProduct(code="38G", name="38期ゴールド原体", vintage_year=38, crude_type=CrudeProductType.G, aging_years=0, unit="kg"),
        CrudeProduct(code="38GN", name="38期ジンジャー原体", vintage_year=38, crude_type=CrudeProductType.GN, aging_years=0, unit="kg"),
        # 第37期仕込み（熟成1年目）
        CrudeProduct(code="37R", name="37期レギュラー原体", vintage_year=37, crude_type=CrudeProductType.R, aging_years=1, unit="kg"),
        CrudeProduct(code="37HI", name="37期HI原体", vintage_year=37, crude_type=CrudeProductType.HI, aging_years=1, unit="kg"),
        CrudeProduct(code="37G", name="37期ゴールド原体", vintage_year=37, crude_type=CrudeProductType.G, aging_years=1, unit="kg"),
        # 第36期仕込み（熟成2年目）
        CrudeProduct(code="36R", name="36期レギュラー原体", vintage_year=36, crude_type=CrudeProductType.R, aging_years=2, unit="kg"),
        CrudeProduct(code="36HI", name="36期HI原体", vintage_year=36, crude_type=CrudeProductType.HI, aging_years=2, unit="kg"),
        CrudeProduct(code="36G", name="36期ゴールド原体", vintage_year=36, crude_type=CrudeProductType.G, aging_years=2, unit="kg"),
        # 第35期仕込み（熟成3年目、出荷可能）
        CrudeProduct(code="35R", name="35期レギュラー原体", vintage_year=35, crude_type=CrudeProductType.R, aging_years=3, unit="kg"),
        CrudeProduct(code="35HI", name="35期HI原体", vintage_year=35, crude_type=CrudeProductType.HI, aging_years=3, unit="kg"),
        CrudeProduct(code="35G", name="35期ゴールド原体", vintage_year=35, crude_type=CrudeProductType.G, aging_years=3, unit="kg"),
        # ブレンド品
        CrudeProduct(code="35RHI", name="35期R+HIブレンド", vintage_year=35, crude_type=CrudeProductType.R, aging_years=3, is_blend=True, unit="kg",
                     notes="35Rと35HIのブレンド"),
    ]
    db.add_all(crude_products)
    print(f"  原体マスタ: {len(crude_products)}件 作成")


async def seed_products(db: AsyncSession) -> None:
    existing = await db.execute(select(Product).limit(1))
    if existing.scalar_one_or_none():
        print("  製品マスタ: スキップ（既存データあり）")
        return

    # 万田発酵の製品ラインナップ
    products = [
        # 半製品（中間製品）
        Product(code="HP01", name="万田酵素ペースト原液", product_type=ProductType.semi_finished, product_group="半製品", unit="kg", sc_code="HP001"),
        Product(code="HP02", name="万田酵素ドリンク原液", product_type=ProductType.semi_finished, product_group="半製品", unit="kg", sc_code="HP002"),
        # 内製品（製品課）- メイン製品ライン
        Product(code="ME01", name="万田酵素スタンダード ペースト 150g", product_type=ProductType.in_house_product_dept, product_group="万田酵素", unit="個", sc_code="ME001", content_weight_g=Decimal("150"), product_symbol="MEP150"),
        Product(code="ME02", name="万田酵素スタンダード ペースト 75g", product_type=ProductType.in_house_product_dept, product_group="万田酵素", unit="個", sc_code="ME002", content_weight_g=Decimal("75"), product_symbol="MEP075"),
        Product(code="ME03", name="万田酵素スタンダード 分包 2.5g×31包", product_type=ProductType.in_house_product_dept, product_group="万田酵素", unit="個", sc_code="ME003", content_weight_g=Decimal("77.5"), product_symbol="MEB031"),
        Product(code="ME04", name="万田酵素スタンダード 分包 2.5g×60包", product_type=ProductType.in_house_product_dept, product_group="万田酵素", unit="個", sc_code="ME004", content_weight_g=Decimal("150"), product_symbol="MEB060"),
        Product(code="MG01", name="万田酵素GINGER ペースト 75g", product_type=ProductType.in_house_product_dept, product_group="万田酵素GINGER", unit="個", sc_code="MG001", content_weight_g=Decimal("75"), product_symbol="MGP075"),
        Product(code="MG02", name="万田酵素GINGER 分包 2.5g×31包", product_type=ProductType.in_house_product_dept, product_group="万田酵素GINGER", unit="個", sc_code="MG002", content_weight_g=Decimal("77.5"), product_symbol="MGB031"),
        Product(code="MH01", name="万田酵素MULBERRY ペースト 150g", product_type=ProductType.in_house_product_dept, product_group="万田酵素MULBERRY", unit="個", sc_code="MH001", content_weight_g=Decimal("150"), product_symbol="MHP150"),
        Product(code="MH02", name="万田酵素MULBERRY 分包 2.5g×31包", product_type=ProductType.in_house_product_dept, product_group="万田酵素MULBERRY", unit="個", sc_code="MH002", content_weight_g=Decimal("77.5"), product_symbol="MHB031"),
        Product(code="MD01", name="万田酵素ドリンク 50ml", product_type=ProductType.in_house_product_dept, product_group="ドリンク", unit="個", sc_code="MD001", content_weight_g=Decimal("50"), product_symbol="MDD050"),
        Product(code="MD02", name="万田酵素ドリンク 150ml", product_type=ProductType.in_house_product_dept, product_group="ドリンク", unit="個", sc_code="MD002", content_weight_g=Decimal("150"), product_symbol="MDD150"),
        # 内製品（製造部）
        Product(code="MM01", name="万田酵素 農業用1kg", product_type=ProductType.in_house_manufacturing, product_group="農業用", unit="個", sc_code="MM001", content_weight_g=Decimal("1000")),
        Product(code="MM02", name="万田酵素 農業用5kg", product_type=ProductType.in_house_manufacturing, product_group="農業用", unit="個", sc_code="MM002", content_weight_g=Decimal("5000")),
        # 外注品
        Product(code="OS01", name="万田酵素プラス温 粒 210粒", product_type=ProductType.outsourced, product_group="外注品", unit="個", sc_code="OS001"),
        Product(code="OS02", name="万田酵素ゼリータイプ 10g×31包", product_type=ProductType.outsourced, product_group="外注品", unit="個", sc_code="OS002"),
        # 外注内製
        Product(code="OI01", name="万田酵素化粧品 クリーム 30g", product_type=ProductType.outsourced_in_house, product_group="化粧品", unit="個", sc_code="OI001", content_weight_g=Decimal("30")),
        # 産品
        Product(code="PR01", name="万田31号（肥料）", product_type=ProductType.produce, product_group="産品", unit="袋", sc_code="PR001"),
    ]
    db.add_all(products)
    print(f"  製品マスタ: {len(products)}件 作成")


async def seed_contractors(db: AsyncSession) -> None:
    existing = await db.execute(select(Contractor).limit(1))
    if existing.scalar_one_or_none():
        print("  外注先マスタ: スキップ（既存データあり）")
        return

    contractors = [
        Contractor(code="CT01", name="外注加工A社", name_short="A社"),
        Contractor(code="CT02", name="外注加工B社", name_short="B社"),
        Contractor(code="CT03", name="外注加工C社", name_short="C社"),
    ]
    db.add_all(contractors)
    print(f"  外注先マスタ: {len(contractors)}件 作成")


async def seed_fiscal_periods(db: AsyncSession) -> None:
    existing = await db.execute(select(FiscalPeriod).limit(1))
    if existing.scalar_one_or_none():
        print("  会計期間: スキップ（既存データあり）")
        return

    # 万田発酵: 第37期と第38期（決算月は9月 → 10月始まり）
    periods = []
    for ki, base_year in [(37, 2023), (38, 2024)]:
        for i in range(12):
            # 10月始まりの会計年度
            cal_year = base_year + (i + 10 - 1) // 12
            cal_month = (i + 10 - 1) % 12 + 1
            start = date(cal_year, cal_month, 1)
            last_day = calendar.monthrange(cal_year, cal_month)[1]
            end = date(cal_year, cal_month, last_day)

            if ki == 37:
                status = PeriodStatus.closed
            elif i < 4:
                status = PeriodStatus.closed
            elif i == 4:
                status = PeriodStatus.closing
            else:
                status = PeriodStatus.open

            periods.append(FiscalPeriod(
                year=ki, month=i + 1, start_date=start, end_date=end, status=status,
                notes=f"第{ki}期 第{i+1}月（{cal_year}年{cal_month}月）",
            ))

    db.add_all(periods)
    print(f"  会計期間: {len(periods)}件 作成")


async def _get_map(db: AsyncSession, model, key_attr: str = "code") -> dict[str, object]:
    """Helper: load all rows and return {code: obj} mapping."""
    result = await db.execute(select(model))
    return {getattr(obj, key_attr): obj for obj in result.scalars().all()}


async def seed_bom_data(db: AsyncSession) -> None:
    """Seed BOM headers and lines for crude products (Stage 1) and products (Stage 2)."""
    existing = await db.execute(select(BomHeader).limit(1))
    if existing.scalar_one_or_none():
        print("  BOMデータ: スキップ（既存データあり）")
        return

    mats = await _get_map(db, Material)
    cps = await _get_map(db, CrudeProduct)
    prods = await _get_map(db, Product)

    eff_date = date(2024, 10, 1)  # 第38期開始日

    # === Stage 1: 原体BOM (raw_material_process) ===
    # Each crude product's BOM: which raw materials go in
    crude_bom_defs = {
        "38R": [
            ("F01", "5.0", "kg", "0.02"), ("F02", "3.0", "kg", "0.02"), ("F03", "2.0", "kg", "0.03"),
            ("V01", "2.0", "kg", "0.01"), ("V02", "1.5", "kg", "0.01"), ("G01", "3.0", "kg", "0.01"),
            ("S01", "0.5", "kg", "0.02"), ("O01", "8.0", "kg", "0.005"),
        ],
        "38HI": [
            ("F01", "6.0", "kg", "0.02"), ("F06", "4.0", "kg", "0.03"), ("F07", "3.0", "kg", "0.03"),
            ("F09", "2.0", "kg", "0.02"), ("V01", "2.0", "kg", "0.01"), ("G01", "4.0", "kg", "0.01"),
            ("S03", "1.0", "kg", "0.02"), ("O01", "10.0", "kg", "0.005"), ("O03", "1.0", "kg", "0.01"),
        ],
        "38G": [
            ("F01", "8.0", "kg", "0.02"), ("F06", "5.0", "kg", "0.03"), ("F07", "4.0", "kg", "0.03"),
            ("F09", "3.0", "kg", "0.02"), ("F11", "2.0", "kg", "0.03"), ("V01", "2.0", "kg", "0.01"),
            ("G01", "5.0", "kg", "0.01"), ("S01", "1.0", "kg", "0.02"), ("S03", "1.0", "kg", "0.02"),
            ("O01", "12.0", "kg", "0.005"), ("O03", "2.0", "kg", "0.01"),
        ],
        "38GN": [
            ("F01", "4.0", "kg", "0.02"), ("F02", "2.0", "kg", "0.02"), ("V01", "1.5", "kg", "0.01"),
            ("G01", "2.0", "kg", "0.01"), ("O01", "6.0", "kg", "0.005"), ("O04", "5.0", "kg", "0.02"),
        ],
        "37R": [
            ("F01", "5.0", "kg", "0.02"), ("F02", "3.0", "kg", "0.02"), ("F05", "2.0", "kg", "0.02"),
            ("V01", "2.0", "kg", "0.01"), ("V07", "1.0", "kg", "0.01"), ("G01", "3.0", "kg", "0.01"),
            ("S02", "0.5", "kg", "0.02"), ("O01", "8.0", "kg", "0.005"),
        ],
        "37HI": [
            ("F01", "6.0", "kg", "0.02"), ("F06", "4.0", "kg", "0.03"), ("F07", "3.0", "kg", "0.03"),
            ("V01", "2.0", "kg", "0.01"), ("G01", "4.0", "kg", "0.01"), ("S03", "1.0", "kg", "0.02"),
            ("O01", "10.0", "kg", "0.005"),
        ],
        "37G": [
            ("F01", "8.0", "kg", "0.02"), ("F06", "5.0", "kg", "0.03"), ("F09", "3.0", "kg", "0.02"),
            ("V01", "2.0", "kg", "0.01"), ("G01", "5.0", "kg", "0.01"), ("S01", "1.0", "kg", "0.02"),
            ("O01", "12.0", "kg", "0.005"), ("O03", "1.5", "kg", "0.01"),
        ],
        "36R": [
            ("F01", "5.0", "kg", "0.02"), ("F03", "2.5", "kg", "0.03"), ("F05", "2.0", "kg", "0.02"),
            ("V01", "2.0", "kg", "0.01"), ("G01", "3.0", "kg", "0.01"), ("S02", "0.5", "kg", "0.02"),
            ("O01", "8.0", "kg", "0.005"),
        ],
        "36HI": [
            ("F01", "6.0", "kg", "0.02"), ("F06", "4.0", "kg", "0.03"), ("F07", "3.0", "kg", "0.03"),
            ("V01", "2.0", "kg", "0.01"), ("G01", "4.0", "kg", "0.01"), ("O01", "10.0", "kg", "0.005"),
        ],
        "36G": [
            ("F01", "8.0", "kg", "0.02"), ("F06", "5.0", "kg", "0.03"), ("F07", "4.0", "kg", "0.03"),
            ("V01", "2.0", "kg", "0.01"), ("G01", "5.0", "kg", "0.01"), ("O01", "12.0", "kg", "0.005"),
        ],
        "35R": [
            ("F01", "5.0", "kg", "0.02"), ("F02", "3.0", "kg", "0.02"), ("F04", "2.0", "kg", "0.02"),
            ("V01", "2.0", "kg", "0.01"), ("G02", "2.0", "kg", "0.01"), ("S01", "0.5", "kg", "0.02"),
            ("O01", "8.0", "kg", "0.005"),
        ],
        "35HI": [
            ("F01", "6.0", "kg", "0.02"), ("F06", "4.0", "kg", "0.03"), ("F13", "2.0", "kg", "0.03"),
            ("V01", "2.0", "kg", "0.01"), ("G01", "4.0", "kg", "0.01"), ("S03", "1.0", "kg", "0.02"),
            ("O01", "10.0", "kg", "0.005"),
        ],
        "35G": [
            ("F01", "8.0", "kg", "0.02"), ("F06", "5.0", "kg", "0.03"), ("F07", "4.0", "kg", "0.03"),
            ("F09", "3.0", "kg", "0.02"), ("V01", "2.0", "kg", "0.01"), ("G01", "5.0", "kg", "0.01"),
            ("S01", "1.0", "kg", "0.02"), ("O01", "12.0", "kg", "0.005"),
        ],
    }

    bom_count = 0
    for cp_code, lines in crude_bom_defs.items():
        cp = cps.get(cp_code)
        if not cp:
            continue
        header = BomHeader(
            crude_product_id=cp.id,
            bom_type=BomType.raw_material_process,
            effective_date=eff_date,
            yield_rate=Decimal("0.9500"),
        )
        db.add(header)
        await db.flush()

        for i, (mat_code, qty, unit, loss) in enumerate(lines):
            mat = mats.get(mat_code)
            if not mat:
                continue
            db.add(BomLine(
                header_id=header.id,
                material_id=mat.id,
                quantity=Decimal(qty),
                unit=unit,
                loss_rate=Decimal(loss),
                sort_order=i + 1,
            ))
        bom_count += 1

    # Blend BOM: 35RHI uses 35R and 35HI as inputs
    blend_cp = cps.get("35RHI")
    r_cp = cps.get("35R")
    hi_cp = cps.get("35HI")
    if blend_cp and r_cp and hi_cp:
        header = BomHeader(
            crude_product_id=blend_cp.id,
            bom_type=BomType.raw_material_process,
            effective_date=eff_date,
            yield_rate=Decimal("0.9800"),
        )
        db.add(header)
        await db.flush()
        db.add(BomLine(header_id=header.id, crude_product_id=r_cp.id, quantity=Decimal("6.0"), unit="kg", sort_order=1))
        db.add(BomLine(header_id=header.id, crude_product_id=hi_cp.id, quantity=Decimal("4.0"), unit="kg", sort_order=2))
        bom_count += 1

    await db.flush()
    print(f"  原体BOM: {bom_count}件 作成")

    # === Stage 2: 製品BOM (product_process) ===
    # Product BOM: which crude products and packaging materials go in
    # Using 35R/35HI/35G (3+ years aged, ready for products)
    product_bom_defs = {
        "HP01": {"crude": [("35R", "100.0")], "pkg": []},
        "HP02": {"crude": [("35R", "50.0"), ("35HI", "50.0")], "pkg": []},
        "ME01": {"crude": [("35R", "0.150")], "pkg": [("P01", "1.0", "0.01"), ("P04", "1.0", "0.005"), ("P06", "1.0", "0.01")]},
        "ME02": {"crude": [("35R", "0.075")], "pkg": [("P01", "1.0", "0.01"), ("P04", "1.0", "0.005"), ("P06", "1.0", "0.01")]},
        "ME03": {"crude": [("35R", "0.0775")], "pkg": [("P02", "31.0", "0.01"), ("P04", "1.0", "0.005")]},
        "ME04": {"crude": [("35R", "0.150")], "pkg": [("P02", "60.0", "0.01"), ("P04", "1.0", "0.005")]},
        "MG01": {"crude": [("38GN", "0.075")], "pkg": [("P01", "1.0", "0.01"), ("P04", "1.0", "0.005"), ("P06", "1.0", "0.01")]},
        "MG02": {"crude": [("38GN", "0.0775")], "pkg": [("P02", "31.0", "0.01"), ("P04", "1.0", "0.005")]},
        "MH01": {"crude": [("35HI", "0.150")], "pkg": [("P01", "1.0", "0.01"), ("P04", "1.0", "0.005"), ("P06", "1.0", "0.01")]},
        "MH02": {"crude": [("35HI", "0.0775")], "pkg": [("P02", "31.0", "0.01"), ("P04", "1.0", "0.005")]},
        "MD01": {"crude": [("35R", "0.025"), ("35HI", "0.025")], "pkg": [("P03", "1.0", "0.01"), ("P06", "1.0", "0.01")]},
        "MD02": {"crude": [("35R", "0.075"), ("35HI", "0.075")], "pkg": [("P03", "1.0", "0.01"), ("P06", "1.0", "0.01")]},
        "MM01": {"crude": [("35R", "1.0")], "pkg": [("P05", "1.0", "0.005")]},
        "MM02": {"crude": [("35R", "5.0")], "pkg": [("P05", "1.0", "0.005")]},
        "OS01": {"crude": [("35G", "0.063")], "pkg": [("P04", "1.0", "0.005")]},
        "OS02": {"crude": [("35R", "0.100")], "pkg": [("P04", "1.0", "0.005")]},
        "OI01": {"crude": [("35G", "0.015")], "pkg": [("P04", "1.0", "0.005")]},
        "PR01": {"crude": [("35R", "0.500")], "pkg": [("P05", "1.0", "0.005")]},
    }

    prod_bom_count = 0
    for prod_code, bom_def in product_bom_defs.items():
        prod = prods.get(prod_code)
        if not prod:
            continue
        header = BomHeader(
            product_id=prod.id,
            bom_type=BomType.product_process,
            effective_date=eff_date,
            yield_rate=Decimal("1.0000"),
        )
        db.add(header)
        await db.flush()

        sort = 1
        for cp_code, qty in bom_def["crude"]:
            cp = cps.get(cp_code)
            if not cp:
                continue
            db.add(BomLine(
                header_id=header.id,
                crude_product_id=cp.id,
                quantity=Decimal(qty),
                unit="kg",
                sort_order=sort,
            ))
            sort += 1

        for mat_code, qty, loss in bom_def["pkg"]:
            mat = mats.get(mat_code)
            if not mat:
                continue
            db.add(BomLine(
                header_id=header.id,
                material_id=mat.id,
                quantity=Decimal(qty),
                unit=mat.unit,
                loss_rate=Decimal(loss),
                sort_order=sort,
            ))
            sort += 1
        prod_bom_count += 1

    await db.flush()
    print(f"  製品BOM: {prod_bom_count}件 作成")


async def seed_cost_budgets(db: AsyncSession) -> None:
    """Seed cost budgets for manufacturing dept and product dept."""
    existing = await db.execute(select(CostBudget).limit(1))
    if existing.scalar_one_or_none():
        print("  予算データ: スキップ（既存データあり）")
        return

    cc_map = await _get_map(db, CostCenter)
    mfg = cc_map.get("MFG")
    prd = cc_map.get("PRD")

    # Get 38th period fiscal periods
    result = await db.execute(select(FiscalPeriod).where(FiscalPeriod.year == 38))
    periods_38 = list(result.scalars().all())

    budget_count = 0
    for period in periods_38:
        if mfg:
            db.add(CostBudget(
                cost_center_id=mfg.id,
                period_id=period.id,
                labor_budget=Decimal("2500000.0000"),
                overhead_budget=Decimal("1800000.0000"),
                outsourcing_budget=Decimal("0.0000"),
                notes=f"第38期第{period.month}月 製造部予算",
            ))
            budget_count += 1

        if prd:
            db.add(CostBudget(
                cost_center_id=prd.id,
                period_id=period.id,
                labor_budget=Decimal("1500000.0000"),
                overhead_budget=Decimal("1200000.0000"),
                outsourcing_budget=Decimal("800000.0000"),
                notes=f"第38期第{period.month}月 製品課予算",
            ))
            budget_count += 1

    await db.flush()
    print(f"  予算データ: {budget_count}件 作成")


async def seed_allocation_rules(db: AsyncSession) -> None:
    """Seed allocation rules for manufacturing and product departments."""
    existing = await db.execute(select(AllocationRule).limit(1))
    if existing.scalar_one_or_none():
        print("  配賦ルール: スキップ（既存データあり）")
        return

    cc_map = await _get_map(db, CostCenter)
    mfg = cc_map.get("MFG")
    prd = cc_map.get("PRD")

    rules = []
    if mfg:
        # 製造部: 労務費は生産時間ベース、経費は原料使用数量ベース
        rules.append(AllocationRule(
            name="製造部 労務費配賦（生産時間）",
            source_cost_center_id=mfg.id,
            cost_element="labor",
            basis=AllocationBasis.production_hours,
            priority=10,
            notes="労務費を直接生産時間で原体に配賦",
        ))
        rules.append(AllocationRule(
            name="製造部 経費配賦（原料数量）",
            source_cost_center_id=mfg.id,
            cost_element="overhead",
            basis=AllocationBasis.raw_material_quantity,
            priority=10,
            notes="経費を原料使用数量で原体に配賦",
        ))

    if prd:
        # 製品課: 全要素を重量ベースで配賦
        rules.append(AllocationRule(
            name="製品課 配賦（重量基準）",
            source_cost_center_id=prd.id,
            cost_element=None,  # 全要素に適用
            basis=AllocationBasis.weight_based,
            priority=0,
            notes="労務費・経費・外注費を内容量(g)で製品に配賦",
        ))

    db.add_all(rules)
    await db.flush()
    print(f"  配賦ルール: {len(rules)}件 作成")


async def main() -> None:
    print("シードデータ投入開始...")
    async with async_session_factory() as db:
        await seed_cost_centers(db)
        await seed_materials(db)
        await seed_crude_products(db)
        await seed_products(db)
        await seed_contractors(db)
        await seed_fiscal_periods(db)
        await seed_bom_data(db)
        await seed_cost_budgets(db)
        await seed_allocation_rules(db)
        await db.commit()
    print("シードデータ投入完了")


if __name__ == "__main__":
    asyncio.run(main())
