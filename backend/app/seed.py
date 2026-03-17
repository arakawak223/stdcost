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
from app.models.cost import StandardCost


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

    # Excelフロー図に基づく多段階加工チェーン
    # process_stage: DAG上の深さ（トポロジカルソートの順序指標）
    # parent_crude_product_id: 主要な前工程（後でIDを紐付け）
    crude_products = [
        # === R系メインライン: R1→R2→R3→R→Rリ→RB→P ===
        CrudeProduct(code="R1", name="一次仕込み（植物XX種類）", crude_type=CrudeProductType.R1, process_stage=1, unit="kg",
                     notes="BOM標準: 原材料費283 + 労務費103 + 経費30 = 416円/kg"),
        CrudeProduct(code="R2", name="二次仕込み", crude_type=CrudeProductType.R2, process_stage=2, unit="kg",
                     notes="BOM標準: 前工程費+原材料費533 + 労務費140 + 経費60 = 733円/kg"),
        CrudeProduct(code="R3", name="三次仕込み（R仕込中）", crude_type=CrudeProductType.R3, process_stage=3, unit="kg",
                     notes="BOM標準: 前工程費+原材料費535 + 労務費114 + 経費90 = 739円/kg"),
        CrudeProduct(code="R", name="レギュラー原体", crude_type=CrudeProductType.R, process_stage=4, unit="kg",
                     notes="BOM標準: 前工程費878 + 経費30 = 908円/kg"),
        CrudeProduct(code="Rri", name="Rリ（リンゴ添加）", crude_type=CrudeProductType.Rri, process_stage=5, unit="kg",
                     notes="BOM標準: 前工程費908 + 原材料費2 + 労務費254 + 経費30 = 1194円/kg"),
        CrudeProduct(code="RB", name="Rブレンド", crude_type=CrudeProductType.RB, process_stage=6, unit="kg",
                     notes="実績単価: 954円/kg"),
        CrudeProduct(code="P", name="P（定番製品用仕掛品）", crude_type=CrudeProductType.P, process_stage=7, unit="kg",
                     notes="BOM標準: 前工程費884 + 労務費282 + 経費30 = 1196円/kg"),
        # === R派生ライン ===
        CrudeProduct(code="Rma", name="Rマルベリー", crude_type=CrudeProductType.Rma, process_stage=6, unit="kg",
                     notes="Rリ + マルベリー原料。実績単価: 1048円/kg"),
        CrudeProduct(code="MP", name="マルベリー製品用仕掛品", crude_type=CrudeProductType.MP, process_stage=7, unit="kg",
                     notes="実績単価: 1180円/kg"),
        CrudeProduct(code="RG", name="Rジンジャー", crude_type=CrudeProductType.RG, process_stage=6, unit="kg",
                     notes="Rリ + ジンジャー。実績単価: 1052円/kg"),
        CrudeProduct(code="RGI", name="RGI", crude_type=CrudeProductType.RGI, process_stage=7, unit="kg"),
        CrudeProduct(code="GP", name="ジンジャープラス仕掛品", crude_type=CrudeProductType.GP, process_stage=8, unit="kg",
                     notes="実績単価: 1395円/kg"),
        CrudeProduct(code="LPA", name="LPA", crude_type=CrudeProductType.LPA, process_stage=6, unit="kg",
                     notes="Rリ派生。実績単価: 1752円/kg"),
        CrudeProduct(code="Rshi", name="Rシ（生姜系）", crude_type=CrudeProductType.Rshi, process_stage=5, unit="kg",
                     notes="R + 生姜系添加。実績単価: 1054円/kg"),
        CrudeProduct(code="PE", name="PE（生姜系製品用仕掛品）", crude_type=CrudeProductType.PE, process_stage=6, unit="kg",
                     notes="実績単価: 1150円/kg"),
        CrudeProduct(code="FEB", name="FEB", crude_type=CrudeProductType.FEB, process_stage=5, unit="kg",
                     notes="R派生。実績単価: 1462円/kg"),
        CrudeProduct(code="T", name="T（畜産用仕掛品）", crude_type=CrudeProductType.T, process_stage=6, unit="kg",
                     notes="FEB派生。実績単価: 1580円/kg"),
        CrudeProduct(code="RX", name="RX（植物用レギュラー）", crude_type=CrudeProductType.RX, process_stage=6, unit="kg",
                     notes="Rリ派生。実績単価: 1244円/kg"),
        # === HI系 ===
        CrudeProduct(code="HI", name="HI（ハイグレード）", crude_type=CrudeProductType.HI, process_stage=5, unit="kg",
                     notes="R派生のハイグレードライン。実績単価: 1142円/kg"),
        CrudeProduct(code="HIA", name="HI-A", crude_type=CrudeProductType.HIA, process_stage=6, unit="kg",
                     notes="実績単価: 1245円/kg"),
        CrudeProduct(code="HIB", name="HI-B", crude_type=CrudeProductType.HIB, process_stage=6, unit="kg",
                     notes="実績単価: 1362円/kg"),
        CrudeProduct(code="HIR", name="HIR", crude_type=CrudeProductType.HIR, process_stage=6, unit="kg"),
        CrudeProduct(code="HIBkai", name="HIB海", crude_type=CrudeProductType.HIBkai, process_stage=7, unit="kg"),
        # === その他原液 ===
        CrudeProduct(code="G", name="ゴールド", crude_type=CrudeProductType.G, process_stage=6, unit="kg",
                     notes="実績単価: 1221円/kg"),
        CrudeProduct(code="GA", name="GA", crude_type=CrudeProductType.GA, process_stage=7, unit="kg"),
        CrudeProduct(code="GB", name="GB", crude_type=CrudeProductType.GB, process_stage=7, unit="kg"),
        CrudeProduct(code="B", name="B", crude_type=CrudeProductType.B, process_stage=6, unit="kg"),
        CrudeProduct(code="O", name="O", crude_type=CrudeProductType.O, process_stage=6, unit="kg"),
        CrudeProduct(code="X", name="X", crude_type=CrudeProductType.X, process_stage=6, unit="kg"),
        CrudeProduct(code="XC", name="XC", crude_type=CrudeProductType.XC, process_stage=7, unit="kg"),
        CrudeProduct(code="BM", name="BM", crude_type=CrudeProductType.BM, process_stage=6, unit="kg"),
        CrudeProduct(code="FB", name="FB", crude_type=CrudeProductType.FB, process_stage=6, unit="kg"),
        CrudeProduct(code="PX", name="PX", crude_type=CrudeProductType.PX, process_stage=7, unit="kg"),
        CrudeProduct(code="PXA", name="PXA", crude_type=CrudeProductType.PXA, process_stage=8, unit="kg"),
        CrudeProduct(code="plant", name="植物用ブレンド", crude_type=CrudeProductType.plant, process_stage=6, unit="kg"),
    ]
    db.add_all(crude_products)
    await db.flush()

    # parent_crude_product_id を設定（主要な前工程の紐付け）
    cp_map = {cp.code: cp for cp in crude_products}
    parent_links = {
        "R2": "R1", "R3": "R2", "R": "R3",
        "Rri": "R", "RB": "Rri", "P": "RB",
        "Rma": "Rri", "MP": "Rma",
        "RG": "Rri", "RGI": "RG", "GP": "RGI",
        "LPA": "Rri", "RX": "Rri",
        "Rshi": "R", "PE": "Rshi",
        "FEB": "R", "T": "FEB",
        "HI": "R", "HIA": "HI", "HIB": "HI", "HIR": "HI", "HIBkai": "HIB",
        "G": "Rri", "GA": "G", "GB": "G",
        "B": "Rri", "O": "Rri", "X": "Rri", "XC": "X",
        "BM": "Rri", "FB": "Rri",
        "PX": "RB", "PXA": "PX",
        "plant": "Rri",
    }
    for child_code, parent_code in parent_links.items():
        child = cp_map.get(child_code)
        parent = cp_map.get(parent_code)
        if child and parent:
            child.parent_crude_product_id = parent.id

    await db.flush()
    print(f"  原体マスタ: {len(crude_products)}件 作成（多段階工程チェーン）")


async def seed_products(db: AsyncSession) -> None:
    existing = await db.execute(select(Product).limit(1))
    if existing.scalar_one_or_none():
        print("  製品マスタ: スキップ（既存データあり）")
        return

    # Excel「標準原価_製品_2603.xlsx」の全111製品を実SCコードで登録
    D = Decimal
    PRD = ProductType.in_house_product_dept

    products = [
        # === 5A (2品) ===
        Product(code="20051200013", name="MKF-Ⅰ 分包150g(AAAAA)", product_type=PRD, product_group="5A",
                sc_code="20051200013", content_weight_g=D("150"), product_symbol="5A", unit="個"),
        Product(code="20071100007", name="MKF-Ⅰ携帯ﾊﾟｯｸ 50g(5A)", product_type=PRD, product_group="5A",
                sc_code="20071100007", content_weight_g=D("50"), product_symbol="5A", unit="個"),
        # === B (4品) ===
        Product(code="20051200005", name="万田HI酵素 分包150g", product_type=PRD, product_group="B",
                sc_code="20051200005", content_weight_g=D("150"), product_symbol="B", unit="個"),
        Product(code="20071000005", name="試供品 HI酵素 5g", product_type=PRD, product_group="B",
                sc_code="20071000005", content_weight_g=D("5"), product_symbol="B", unit="個"),
        Product(code="20110800311", name="MANDA HI KOHSO", product_type=PRD, product_group="B",
                sc_code="20110800311", content_weight_g=D("145"), product_symbol="B", unit="個"),
        Product(code="20110800629", name="万田HI酵素 145g", product_type=PRD, product_group="B",
                sc_code="20110800629", content_weight_g=D("145"), product_symbol="B", unit="個"),
        # === BE (3品) ===
        Product(code="20200800016", name="万田酵素ｴｸｾﾚﾝﾄ 145g", product_type=PRD, product_group="BE",
                sc_code="20200800016", content_weight_g=D("145"), product_symbol="BE", unit="個"),
        Product(code="20200800017", name="万田酵素ｴｸｾﾚﾝﾄ 分包30g（2.5g×12包）", product_type=PRD, product_group="BE",
                sc_code="20200800017", content_weight_g=D("30"), product_symbol="BE", unit="個"),
        Product(code="20200800018", name="万田酵素ｴｸｾﾚﾝﾄ 分包450g", product_type=PRD, product_group="BE",
                sc_code="20200800018", content_weight_g=D("450"), product_symbol="BE", unit="個"),
        # === BM (1品) ===
        Product(code="20240100051", name="万田酵素 MANUKA HONEY Premium 分包77.5g", product_type=PRD, product_group="BM",
                sc_code="20240100051", content_weight_g=D("77.5"), product_symbol="BM", unit="個"),
        # === C (1品) ===
        Product(code="20110300008", name="Man-Koso CARAT 145g", product_type=PRD, product_group="C",
                sc_code="20110300008", content_weight_g=D("145"), product_symbol="C", unit="個"),
        # === D (2品) ===
        Product(code="20200200001", name="万田酵素超熟分包77.5g", product_type=PRD, product_group="D",
                sc_code="20200200001", content_weight_g=D("77.5"), product_symbol="D", unit="個"),
        Product(code="20200200003", name="万田酵素超熟分包2.5g×5", product_type=PRD, product_group="D",
                sc_code="20200200003", content_weight_g=D("12.5"), product_symbol="D", unit="個"),
        # === DC (2品) ===
        Product(code="20211100014", name="特選EXプラス分包70g(2.5g×28包)", product_type=PRD, product_group="DC",
                sc_code="20211100014", content_weight_g=D("70"), product_symbol="DC", unit="個"),
        Product(code="20211100015", name="特選EXプラス分包150g(2.5g×60包)", product_type=PRD, product_group="DC",
                sc_code="20211100015", content_weight_g=D("150"), product_symbol="DC", unit="個"),
        # === EB (4品) ===
        Product(code="20071200005", name="試供品 ｽｰﾊﾟｰ万田酵素(赤) 5g", product_type=PRD, product_group="EB",
                sc_code="20071200005", content_weight_g=D("5"), product_symbol="EB", unit="個"),
        Product(code="20231100072", name="ｽｰﾊﾟｰ万田酵素 分包 35g", product_type=PRD, product_group="EB",
                sc_code="20231100072", content_weight_g=D("35"), product_symbol="EB", unit="個"),
        Product(code="20231100073", name="ｽｰﾊﾟｰ万田酵素 分包150g", product_type=PRD, product_group="EB",
                sc_code="20231100073", content_weight_g=D("150"), product_symbol="EB", unit="個"),
        Product(code="20231100074", name="ｽｰﾊﾟｰ万田酵素 分包450g", product_type=PRD, product_group="EB",
                sc_code="20231100074", content_weight_g=D("450"), product_symbol="EB", unit="個"),
        # === FB (2品) ===
        Product(code="20220600066", name="ｺﾞｰﾙﾄﾞEX155g", product_type=PRD, product_group="FB",
                sc_code="20220600066", content_weight_g=D("155"), product_symbol="FB", unit="個"),
        Product(code="20221200022", name="ｺﾞｰﾙﾄﾞEX300g", product_type=PRD, product_group="FB",
                sc_code="20221200022", content_weight_g=D("300"), product_symbol="FB", unit="個"),
        # === G (2品) ===
        Product(code="20080100003", name="試供品 万田酵素 MJ(5g)", product_type=PRD, product_group="G",
                sc_code="20080100003", content_weight_g=D("5"), product_symbol="G", unit="個"),
        Product(code="20110800295", name="万田酵素 MJ", product_type=PRD, product_group="G",
                sc_code="20110800295", content_weight_g=D("90"), product_symbol="G", unit="個"),
        # === GP (5品) ===
        Product(code="20231100078", name="発酵しょうが 2.5g 支給用", product_type=PRD, product_group="GP",
                sc_code="20231100078", content_weight_g=D("2.5"), product_symbol="GP", unit="個"),
        Product(code="20230600044", name="万田酵素 ﾌﾟﾗｽ温 発酵しょうが 77.5g", product_type=PRD, product_group="GP",
                sc_code="20230600044", content_weight_g=D("77.5"), product_symbol="GP", unit="個"),
        Product(code="20230600045", name="万田酵素 ﾌﾟﾗｽ温 発酵しょうが 20g", product_type=PRD, product_group="GP",
                sc_code="20230600045", content_weight_g=D("20"), product_symbol="GP", unit="個"),
        Product(code="20230600046", name="試供品 ﾌﾟﾗｽ温発酵しょうが 2.5g", product_type=PRD, product_group="GP",
                sc_code="20230600046", content_weight_g=D("2.5"), product_symbol="GP", unit="個"),
        Product(code="20241200012", name="万田酵素ﾌﾟﾗｽ温発酵しょうが 75g 5g×15包", product_type=PRD, product_group="GP",
                sc_code="20241200012", content_weight_g=D("75"), product_symbol="GP", unit="個"),
        # === KOL (3品) ===
        Product(code="20231200033", name="万田酵素分包75g （中国虹越）", product_type=PRD, product_group="KOL",
                sc_code="20231200033", content_weight_g=D("75"), product_symbol="KOL", unit="個"),
        Product(code="20241100041", name="試供品 万田酵素分包5g(中国虹越)", product_type=PRD, product_group="KOL",
                sc_code="20241100041", content_weight_g=D("5"), product_symbol="KOL", unit="個"),
        Product(code="20250300087", name="万田酵素 分包150g (中国)", product_type=PRD, product_group="KOL",
                sc_code="20250300087", content_weight_g=D("150"), product_symbol="KOL", unit="個"),
        # === MP (7品) ===
        Product(code="20171000004", name="万田酵素 MULBERRY 分包 77.5g", product_type=PRD, product_group="MP",
                sc_code="20171000004", content_weight_g=D("77.5"), product_symbol="MP", unit="個"),
        Product(code="20171000006", name="万田酵素 MULBERRY 分包20g", product_type=PRD, product_group="MP",
                sc_code="20171000006", content_weight_g=D("20"), product_symbol="MP", unit="個"),
        Product(code="20171000010", name="万田酵素 MULBERRY ﾁｭｰﾌﾞﾀｲﾌﾟ 26×3本", product_type=PRD, product_group="MP",
                sc_code="20171000010", content_weight_g=D("78"), product_symbol="MP", unit="個"),
        Product(code="20181100045", name="万田酵素 MULBERRY 分包35g 2.5g×14包", product_type=PRD, product_group="MP",
                sc_code="20181100045", content_weight_g=D("35"), product_symbol="MP", unit="個"),
        Product(code="20200200034", name="万田酵素MULBERRY 分包 10g 2.5×4包", product_type=PRD, product_group="MP",
                sc_code="20200200034", content_weight_g=D("10"), product_symbol="MP", unit="個"),
        Product(code="20220100027", name="MULBERRY 2.5g 支給用", product_type=PRD, product_group="MP",
                sc_code="20220100027", content_weight_g=D("2.5"), product_symbol="MP", unit="個"),
        Product(code="20230900058", name="万田酵素 MULBERRY 分包12.5g", product_type=PRD, product_group="MP",
                sc_code="20230900058", content_weight_g=D("12.5"), product_symbol="MP", unit="個"),
        # === O (5品) ===
        Product(code="20060200007", name="万田酵素 金印145g", product_type=PRD, product_group="O",
                sc_code="20060200007", content_weight_g=D("145"), product_symbol="O", unit="個"),
        Product(code="20071000014", name="試供品 金印 5g", product_type=PRD, product_group="O",
                sc_code="20071000014", content_weight_g=D("5"), product_symbol="O", unit="個"),
        Product(code="20071100028", name="万田酵素 金印 分包150g", product_type=PRD, product_group="O",
                sc_code="20071100028", content_weight_g=D("150"), product_symbol="O", unit="個"),
        Product(code="20110800312", name="MANDA KOHSO GOLD 145g", product_type=PRD, product_group="O",
                sc_code="20110800312", content_weight_g=D("145"), product_symbol="O", unit="個"),
        Product(code="20140100011", name="Man-Koso GOLD 145g", product_type=PRD, product_group="O",
                sc_code="20140100011", content_weight_g=D("145"), product_symbol="O", unit="個"),
        # === P (14品) ===
        Product(code="20061200012", name="万田酵素 145g(販売店向け)", product_type=PRD, product_group="P",
                sc_code="20061200012", content_weight_g=D("145"), product_symbol="P", unit="個"),
        Product(code="20070300033", name="万田酵素 分包150g(販売店向け)", product_type=PRD, product_group="P",
                sc_code="20070300033", content_weight_g=D("150"), product_symbol="P", unit="個"),
        Product(code="20080100023", name="試供品 万田酵素 5g(販売店向け)", product_type=PRD, product_group="P",
                sc_code="20080100023", content_weight_g=D("5"), product_symbol="P", unit="個"),
        Product(code="20090100014", name="万田酵素 300g(販売店限定品)", product_type=PRD, product_group="P",
                sc_code="20090100014", content_weight_g=D("300"), product_symbol="P", unit="個"),
        Product(code="20090300004", name="万田酵素 分包50g", product_type=PRD, product_group="P",
                sc_code="20090300004", content_weight_g=D("50"), product_symbol="P", unit="個"),
        Product(code="20110300007", name="Man-Koso PREMIUM 145g", product_type=PRD, product_group="P",
                sc_code="20110300007", content_weight_g=D("145"), product_symbol="P", unit="個"),
        Product(code="20110800918", name="Man-Koso PREMIUM 分包150g", product_type=PRD, product_group="P",
                sc_code="20110800918", content_weight_g=D("150"), product_symbol="P", unit="個"),
        Product(code="20210700007", name="MKﾐｸｽﾁｬｰ(ﾍﾟｰｽﾄ) 1kg 中栓付き容器", product_type=PRD, product_group="P",
                sc_code="20210700007", content_weight_g=D("1000"), product_symbol="P", unit="個"),
        Product(code="20220100030", name="P 2.5g×2 支給用", product_type=PRD, product_group="P",
                sc_code="20220100030", content_weight_g=D("5"), product_symbol="P", unit="個"),
        Product(code="20221200036", name="植物発酵エキス 万田酵素", product_type=PRD, product_group="P",
                sc_code="20221200036", content_weight_g=D("1000"), product_symbol="P", unit="個"),
        Product(code="20230700024", name="万田酵素(宇宙用)", product_type=PRD, product_group="P",
                sc_code="20230700024", content_weight_g=D("5"), product_symbol="P", unit="個"),
        Product(code="20240400018", name="万田酵素（宇宙用）2.5g×4包 店頭販売用", product_type=PRD, product_group="P",
                sc_code="20240400018", content_weight_g=D("10"), product_symbol="P", unit="個"),
        Product(code="20240400019", name="万田酵素（宇宙用）2.5g×8包 ｲﾍﾞﾝﾄｺﾗﾎﾞ用", product_type=PRD, product_group="P",
                sc_code="20240400019", content_weight_g=D("20"), product_symbol="P", unit="個"),
        Product(code="20240400020", name="万田酵素(宇宙用) 2.5g×8包 通信販売用", product_type=PRD, product_group="P",
                sc_code="20240400020", content_weight_g=D("20"), product_symbol="P", unit="個"),
        # === PE (8品) ===
        Product(code="20170400004", name="試供品 万田酵素 GINGER 2.5g", product_type=PRD, product_group="PE",
                sc_code="20170400004", content_weight_g=D("2.5"), product_symbol="PE", unit="個"),
        Product(code="20170400005", name="万田酵素 GINGER 分包20g", product_type=PRD, product_group="PE",
                sc_code="20170400005", content_weight_g=D("20"), product_symbol="PE", unit="個"),
        Product(code="20170400006", name="万田酵素GINGER分包77.5g", product_type=PRD, product_group="PE",
                sc_code="20170400006", content_weight_g=D("77.5"), product_symbol="PE", unit="個"),
        Product(code="20170400017", name="万田酵素 GINGER 分包 35g", product_type=PRD, product_group="PE",
                sc_code="20170400017", content_weight_g=D("35"), product_symbol="PE", unit="個"),
        Product(code="20171000009", name="万田酵素GINGERﾁｭｰﾌﾞﾀｲﾌﾟ26×3本", product_type=PRD, product_group="PE",
                sc_code="20171000009", content_weight_g=D("78"), product_symbol="PE", unit="個"),
        Product(code="20181100042", name="万田酵素 GINGER2.5g×4包", product_type=PRD, product_group="PE",
                sc_code="20181100042", content_weight_g=D("10"), product_symbol="PE", unit="個"),
        Product(code="20190100014", name="万田酵素GINGER分包50g", product_type=PRD, product_group="PE",
                sc_code="20190100014", content_weight_g=D("50"), product_symbol="PE", unit="個"),
        Product(code="20220100028", name="GINGER 2.5g 支給用", product_type=PRD, product_group="PE",
                sc_code="20220100028", content_weight_g=D("2.5"), product_symbol="PE", unit="個"),
        # === PG (5品) ===
        Product(code="20050700013", name="万田酵素 ｊ 分包150g", product_type=PRD, product_group="PG",
                sc_code="20050700013", content_weight_g=D("150"), product_symbol="PG", unit="個"),
        Product(code="20080300003", name="試供品 万田酵素 ｊ 5g", product_type=PRD, product_group="PG",
                sc_code="20080300003", content_weight_g=D("5"), product_symbol="PG", unit="個"),
        Product(code="20091200010", name="MANDA CARE PLUS 75g(梅)", product_type=PRD, product_group="PG",
                sc_code="20091200010", content_weight_g=D("75"), product_symbol="PG", unit="個"),
        Product(code="20091200011", name="MANDA CARE PLUS 5g(梅)", product_type=PRD, product_group="PG",
                sc_code="20091200011", content_weight_g=D("5"), product_symbol="PG", unit="個"),
        Product(code="20221100028", name="万田酵素 j 分包50g", product_type=PRD, product_group="PG",
                sc_code="20221100028", content_weight_g=D("50"), product_symbol="PG", unit="個"),
        # === PR (2品) ===
        Product(code="20091200015", name="ﾅﾁｭﾗﾙ酵素ﾌﾞﾙｰﾍﾞﾘｰﾌﾟﾗｽ 分包150g", product_type=PRD, product_group="PR",
                sc_code="20091200015", content_weight_g=D("150"), product_symbol="PR", unit="個"),
        Product(code="20091200016", name="試供品 ﾅﾁｭﾗﾙ酵素ﾌﾞﾙｰﾍﾞﾘｰﾌﾟﾗｽ 5g", product_type=PRD, product_group="PR",
                sc_code="20091200016", content_weight_g=D("5"), product_symbol="PR", unit="個"),
        # === PSA (3品) ===
        Product(code="20120900082", name="NONI酵素 分包60g", product_type=PRD, product_group="PSA",
                sc_code="20120900082", content_weight_g=D("60"), product_symbol="PSA", unit="個"),
        Product(code="20130100001", name="NONI酵素 300g ファミリーサイズ", product_type=PRD, product_group="PSA",
                sc_code="20130100001", content_weight_g=D("300"), product_symbol="PSA", unit="個"),
        Product(code="20240600040", name="NONI酵素 分包14g 2g×7包", product_type=PRD, product_group="PSA",
                sc_code="20240600040", content_weight_g=D("14"), product_symbol="PSA", unit="個"),
        # === PX (8品) ===
        Product(code="20170400007", name="試供品 万田酵素 STANDARD 2.5g", product_type=PRD, product_group="PX",
                sc_code="20170400007", content_weight_g=D("2.5"), product_symbol="PX", unit="個"),
        Product(code="20170400008", name="万田酵素 STANDARD 分包20g", product_type=PRD, product_group="PX",
                sc_code="20170400008", content_weight_g=D("20"), product_symbol="PX", unit="個"),
        Product(code="20170400009", name="万田酵素STANDARD分包77.5g", product_type=PRD, product_group="PX",
                sc_code="20170400009", content_weight_g=D("77.5"), product_symbol="PX", unit="個"),
        Product(code="20170400016", name="万田酵素 STANDARD 分包35g", product_type=PRD, product_group="PX",
                sc_code="20170400016", content_weight_g=D("35"), product_symbol="PX", unit="個"),
        Product(code="20171000008", name="万田酵素STANDARDﾁｭｰﾌﾞﾀｲﾌﾟ26×3本", product_type=PRD, product_group="PX",
                sc_code="20171000008", content_weight_g=D("78"), product_symbol="PX", unit="個"),
        Product(code="20180500084", name="万田酵素 STANDARD 分包50g", product_type=PRD, product_group="PX",
                sc_code="20180500084", content_weight_g=D("50"), product_symbol="PX", unit="個"),
        Product(code="20181100040", name="万田酵素 STANDARD2.5g×4包", product_type=PRD, product_group="PX",
                sc_code="20181100040", content_weight_g=D("10"), product_symbol="PX", unit="個"),
        Product(code="20191200078", name="MANDA WELLNESS SUPERFOOD 31×2.5", product_type=PRD, product_group="PX",
                sc_code="20191200078", content_weight_g=D("77.5"), product_symbol="PX", unit="個"),
        # === PXM (3品) ===
        Product(code="20201100053", name="万田酵素MANUKA HONEY 分包77.5g", product_type=PRD, product_group="PXM",
                sc_code="20201100053", content_weight_g=D("77.5"), product_symbol="PXM", unit="個"),
        Product(code="20201100054", name="試供品 万田酵素MANUKA HONEY 分包2.5g", product_type=PRD, product_group="PXM",
                sc_code="20201100054", content_weight_g=D("2.5"), product_symbol="PXM", unit="個"),
        Product(code="20220700012", name="万田酵素 ﾏﾇｶﾊﾆｰBlend 50g", product_type=PRD, product_group="PXM",
                sc_code="20220700012", content_weight_g=D("50"), product_symbol="PXM", unit="個"),
        # === Q (1品) ===
        Product(code="20080700007", name="ﾊﾞｲｵ・EX 125g", product_type=PRD, product_group="Q",
                sc_code="20080700007", content_weight_g=D("125"), product_symbol="Q", unit="個"),
        # === T (4品) ===
        Product(code="20120500014", name="植物性発酵物（A飼料）1kg", product_type=PRD, product_group="T",
                sc_code="20120500014", content_weight_g=D("1000"), product_symbol="T", unit="個"),
        Product(code="20120800030", name="マンダアニモ 650g", product_type=PRD, product_group="T",
                sc_code="20120800030", content_weight_g=D("650"), product_symbol="T", unit="個"),
        Product(code="20241000066", name="馬用万田酵素 1kg", product_type=PRD, product_group="T",
                sc_code="20241000066", content_weight_g=D("1000"), product_symbol="T", unit="個"),
        Product(code="20250400005", name="馬用万田酵素 10kg", product_type=PRD, product_group="T",
                sc_code="20250400005", content_weight_g=D("10000"), product_symbol="T", unit="個"),
        # === V (4品) ===
        Product(code="20080700011", name="試供品 ｽｰﾊﾟｰ氣Ⅰ 5g", product_type=PRD, product_group="V",
                sc_code="20080700011", content_weight_g=D("5"), product_symbol="V", unit="個"),
        Product(code="20080800002", name="ｽｰﾊﾟｰ万田酵素氣Ⅰ 35g", product_type=PRD, product_group="V",
                sc_code="20080800002", content_weight_g=D("35"), product_symbol="V", unit="個"),
        Product(code="20081200016", name="ｽｰﾊﾟｰ氣Ⅰ 分包600g(150g×4箱)", product_type=PRD, product_group="V",
                sc_code="20081200016", content_weight_g=D("600"), product_symbol="V", unit="個"),
        Product(code="20110800272", name="ｽｰﾊﾟｰ万田酵素 氣Ⅰ", product_type=PRD, product_group="V",
                sc_code="20110800272", content_weight_g=D("175"), product_symbol="V", unit="個"),
        # === X (6品) ===
        Product(code="20060800006", name="試供品 万田31号 1ml×6", product_type=PRD, product_group="X",
                sc_code="20060800006", content_weight_g=D("7.8"), product_symbol="X", unit="個"),
        Product(code="20081200013", name="万田31号 100ml", product_type=PRD, product_group="X",
                sc_code="20081200013", content_weight_g=D("130"), product_symbol="X", unit="個"),
        Product(code="20081200014", name="万田31号 500ml", product_type=PRD, product_group="X",
                sc_code="20081200014", content_weight_g=D("650"), product_symbol="X", unit="個"),
        Product(code="20081200019", name="万田31号 1ﾘｯﾄﾙ", product_type=PRD, product_group="X",
                sc_code="20081200019", content_weight_g=D("1300"), product_symbol="X", unit="個"),
        Product(code="20230300008", name="健康農業のための万田酵素 500ml", product_type=PRD, product_group="X",
                sc_code="20230300008", content_weight_g=D("650"), product_symbol="X", unit="個"),
        Product(code="20241200064", name="万田ｸﾞﾘｰﾝｷｰﾊﾟｰ 200ml", product_type=PRD, product_group="X",
                sc_code="20241200064", content_weight_g=D("260"), product_symbol="X", unit="個"),
        # === XC (3品) ===
        Product(code="20160900041", name="万田31号500ml(韓国向)", product_type=PRD, product_group="XC",
                sc_code="20160900041", content_weight_g=D("650"), product_symbol="XC", unit="個"),
        Product(code="20160900042", name="万田31号1ﾘｯﾄﾙ(韓国向)", product_type=PRD, product_group="XC",
                sc_code="20160900042", content_weight_g=D("1300"), product_symbol="XC", unit="個"),
        Product(code="20200300074", name="万田31号50ml(韓国向け)", product_type=PRD, product_group="XC",
                sc_code="20200300074", content_weight_g=D("65"), product_symbol="XC", unit="個"),
        # === Y (3品) ===
        Product(code="20051000011", name="MANDA L5000 450g(海外向け)", product_type=PRD, product_group="Y",
                sc_code="20051000011", content_weight_g=D("450"), product_symbol="Y", unit="個"),
        Product(code="20120300038", name="Man-Koso LIFE 450g", product_type=PRD, product_group="Y",
                sc_code="20120300038", content_weight_g=D("450"), product_symbol="Y", unit="個"),
        Product(code="20240500062", name="試供品 MANDA L5000 5g", product_type=PRD, product_group="Y",
                sc_code="20240500062", content_weight_g=D("5"), product_symbol="Y", unit="個"),
        # === YA (1品) ===
        Product(code="20060100007", name="新･MKF-Ⅱ 30g", product_type=PRD, product_group="YA",
                sc_code="20060100007", content_weight_g=D("30"), product_symbol="YA", unit="個"),
        # === YC (1品) ===
        Product(code="20090100015", name="MKF-Ⅱ5A ﾘｷｯﾄﾞ 30g", product_type=PRD, product_group="YC",
                sc_code="20090100015", content_weight_g=D("30"), product_symbol="YC", unit="個"),
        # === ZA (2品) ===
        Product(code="20091200012", name="MANDA CARE PLUS 75g(ﾊﾟﾊﾟｲﾔ･ｺｺｱ)", product_type=PRD, product_group="ZA",
                sc_code="20091200012", content_weight_g=D("75"), product_symbol="ZA", unit="個"),
        Product(code="20091200013", name="MANDA CARE PLUS 5g(ﾊﾟﾊﾟｲﾔ･ｺｺｱ)", product_type=PRD, product_group="ZA",
                sc_code="20091200013", content_weight_g=D("5"), product_symbol="ZA", unit="個"),
    ]
    db.add_all(products)
    print(f"  製品マスタ: {len(products)}件 作成（Excel全製品SCコード）")


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

    # 万田発酵: 第37期～第39期（決算月は9月 → 10月始まり）
    periods = []
    for ki, base_year in [(37, 2023), (38, 2024), (39, 2025)]:
        for i in range(12):
            # 10月始まりの会計年度
            cal_year = base_year + (i + 10 - 1) // 12
            cal_month = (i + 10 - 1) % 12 + 1
            start = date(cal_year, cal_month, 1)
            last_day = calendar.monthrange(cal_year, cal_month)[1]
            end = date(cal_year, cal_month, last_day)

            if ki <= 37:
                status = PeriodStatus.closed
            elif ki == 38:
                if i < 4:
                    status = PeriodStatus.closed
                elif i == 4:
                    status = PeriodStatus.closing
                else:
                    status = PeriodStatus.open
            else:  # ki == 39
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
    """Seed BOM headers and lines: multi-stage crude product chain + product BOMs.

    BOM types:
      - raw_material_process: R1の仕込み（原料→原体）
      - crude_product_process: R2以降の多段工程（原体→原体）
      - product_process: 製品工程（原体→製品）
    """
    existing = await db.execute(select(BomHeader).limit(1))
    if existing.scalar_one_or_none():
        print("  BOMデータ: スキップ（既存データあり）")
        return

    mats = await _get_map(db, Material)
    cps = await _get_map(db, CrudeProduct)
    prods = await _get_map(db, Product)

    eff_date = date(2024, 10, 1)  # 第38期開始日

    # === 原料工程 (raw_material_process): R1 の仕込み ===
    # R1: 植物XX種類を投入 → BOM標準: 原材料費283円/kg
    r1_materials = [
        ("F01", "5.0", "kg", "0.02"), ("F02", "3.0", "kg", "0.02"), ("F03", "2.0", "kg", "0.03"),
        ("F05", "2.0", "kg", "0.02"), ("F06", "1.5", "kg", "0.03"), ("F08", "1.0", "kg", "0.02"),
        ("V01", "2.0", "kg", "0.01"), ("V02", "1.5", "kg", "0.01"), ("V05", "1.0", "kg", "0.01"),
        ("G01", "3.0", "kg", "0.01"), ("G03", "1.0", "kg", "0.01"),
        ("S01", "0.5", "kg", "0.02"), ("S02", "0.3", "kg", "0.02"),
        ("O01", "8.0", "kg", "0.005"),
    ]

    bom_count = 0

    async def _create_bom(cp_code: str, bom_type: BomType, lines_def: list, yield_rate: str = "0.9500") -> None:
        nonlocal bom_count
        cp = cps.get(cp_code)
        if not cp:
            return
        header = BomHeader(
            crude_product_id=cp.id, bom_type=bom_type,
            effective_date=eff_date, yield_rate=Decimal(yield_rate),
        )
        db.add(header)
        await db.flush()
        for i, line in enumerate(lines_def):
            if line[0].startswith("@"):
                # @CP_CODE: crude product input
                src_cp = cps.get(line[0][1:])
                if src_cp:
                    db.add(BomLine(header_id=header.id, crude_product_id=src_cp.id,
                                   quantity=Decimal(line[1]), unit="kg", sort_order=i + 1))
            else:
                # Material input
                mat = mats.get(line[0])
                if mat:
                    loss = line[3] if len(line) > 3 else "0.0000"
                    db.add(BomLine(header_id=header.id, material_id=mat.id,
                                   quantity=Decimal(line[1]), unit=line[2],
                                   loss_rate=Decimal(loss), sort_order=i + 1))
        bom_count += 1

    # R1: 原料→原体 (raw_material_process)
    await _create_bom("R1", BomType.raw_material_process, r1_materials)

    # === 原体工程 (crude_product_process): R2以降の多段工程 ===
    # R2: R1 + 追加原料
    await _create_bom("R2", BomType.crude_product_process, [
        ("@R1", "1.0"), ("O01", "2.0", "kg", "0.005"), ("F01", "1.0", "kg", "0.02"),
    ], "0.9700")
    # R3: R2 + 追加（三次仕込み）
    await _create_bom("R3", BomType.crude_product_process, [
        ("@R2", "1.0"), ("O01", "1.0", "kg", "0.005"),
    ], "0.9800")
    # R: R3 熟成完了
    await _create_bom("R", BomType.crude_product_process, [
        ("@R3", "1.0"),
    ], "0.9900")
    # Rリ: R + リンゴ
    await _create_bom("Rri", BomType.crude_product_process, [
        ("@R", "1.0"), ("F01", "0.01", "kg", "0.01"),
    ], "0.9800")
    # RB: Rリ ブレンド
    await _create_bom("RB", BomType.crude_product_process, [
        ("@Rri", "1.0"),
    ], "0.9900")
    # P: RB → 定番製品用仕掛品
    await _create_bom("P", BomType.crude_product_process, [
        ("@RB", "1.0"),
    ], "0.9800")
    # Rマ: Rリ + マルベリー原料
    await _create_bom("Rma", BomType.crude_product_process, [
        ("@Rri", "1.0"), ("O02", "0.05", "kg", "0.02"),
    ], "0.9800")
    # MP: Rマ → マルベリー製品用
    await _create_bom("MP", BomType.crude_product_process, [
        ("@Rma", "1.0"),
    ], "0.9800")
    # RG: Rリ + ジンジャー
    await _create_bom("RG", BomType.crude_product_process, [
        ("@Rri", "1.0"), ("O04", "0.10", "kg", "0.02"),
    ], "0.9800")
    # RGI: RG + 追加
    await _create_bom("RGI", BomType.crude_product_process, [
        ("@RG", "1.0"),
    ], "0.9900")
    # GP: RGI → ジンジャープラス
    await _create_bom("GP", BomType.crude_product_process, [
        ("@RGI", "1.0"),
    ], "0.9800")
    # LPA: Rリ派生
    await _create_bom("LPA", BomType.crude_product_process, [
        ("@Rri", "1.0"), ("F01", "0.50", "kg", "0.02"),
    ], "0.9800")
    # RX: Rリ派生（植物用）
    await _create_bom("RX", BomType.crude_product_process, [
        ("@Rri", "1.0"),
    ], "0.9800")
    # Rシ: R + 生姜系
    await _create_bom("Rshi", BomType.crude_product_process, [
        ("@R", "1.0"), ("O04", "0.10", "kg", "0.02"),
    ], "0.9800")
    # PE: Rシ → 生姜系製品用
    await _create_bom("PE", BomType.crude_product_process, [
        ("@Rshi", "1.0"),
    ], "0.9800")
    # FEB: R派生
    await _create_bom("FEB", BomType.crude_product_process, [
        ("@R", "1.0"), ("O01", "0.50", "kg", "0.005"),
    ], "0.9800")
    # T: FEB → 畜産用
    await _create_bom("T", BomType.crude_product_process, [
        ("@FEB", "1.0"),
    ], "0.9800")
    # HI: R派生 ハイグレード
    await _create_bom("HI", BomType.crude_product_process, [
        ("@R", "1.0"), ("O03", "0.05", "kg", "0.01"),
    ], "0.9800")
    # HIA: HI派生
    await _create_bom("HIA", BomType.crude_product_process, [
        ("@HI", "1.0"),
    ], "0.9900")
    # HIB: HI派生
    await _create_bom("HIB", BomType.crude_product_process, [
        ("@HI", "1.0"),
    ], "0.9900")
    # G: Rリ派生 ゴールド
    await _create_bom("G", BomType.crude_product_process, [
        ("@Rri", "1.0"), ("O03", "0.10", "kg", "0.01"),
    ], "0.9800")
    # B: Rリ派生
    await _create_bom("B", BomType.crude_product_process, [
        ("@Rri", "1.0"),
    ], "0.9800")
    # FB: Rリ派生
    await _create_bom("FB", BomType.crude_product_process, [
        ("@Rri", "1.0"),
    ], "0.9800")
    # BM: Rリ派生
    await _create_bom("BM", BomType.crude_product_process, [
        ("@Rri", "1.0"),
    ], "0.9800")
    # plant: Rリ派生 植物用ブレンド
    await _create_bom("plant", BomType.crude_product_process, [
        ("@Rri", "1.0"),
    ], "0.9800")

    await db.flush()
    print(f"  原体BOM: {bom_count}件 作成（多段階工程チェーン）")

    # === Stage 2: 製品BOM (product_process) ===
    # 製品BOM: 原体 + 資材 → 製品
    # 製品記号→原体の対応（Excelの前工程費グラム単価から推定）:
    #   5A→P系, B→HI, BE→G系, BM→特殊, C→Rshi系, D→B系, DC→G系
    #   EB→FB系, GP→GP, KOL→LPA, MP→MP, O→O, P→P, PE→PE, T→T, etc.

    # 製品記号 → 主要原体コードのマッピング
    symbol_to_crude = {
        "5A": "P", "B": "HI", "BE": "G", "BM": "BM", "C": "Rshi",
        "D": "B", "DC": "G", "EB": "FB", "FB": "FB", "G": "G",
        "GP": "GP", "KOL": "LPA", "MP": "MP", "O": "O", "P": "P",
        "PE": "PE", "PG": "P", "PR": "P", "PSA": "P", "PX": "PX",
        "PXM": "PXA", "Q": "P", "T": "T", "V": "B", "X": "X",
        "XC": "XC", "Y": "Rri", "YA": "Rri", "YC": "Rri", "ZA": "P",
    }

    # BOMを自動生成: 各製品の内容量(g)をkg換算して原体入力量とする
    product_bom_defs = {}
    for prod in prods.values():
        if not prod.content_weight_g or not prod.product_symbol:
            continue
        crude_code = symbol_to_crude.get(prod.product_symbol, "P")
        weight_kg = str((prod.content_weight_g / Decimal("1000")).quantize(Decimal("0.000001")))
        product_bom_defs[prod.code] = {
            "crude": [(crude_code, weight_kg)],
            "pkg": [("P01", "1.0", "0.01"), ("P06", "1.0", "0.01")],
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


async def seed_standard_costs_39(db: AsyncSession) -> None:
    """Excel「標準原価_製品_2603.xlsx」の39期標準原価データを投入。"""
    existing = await db.execute(select(StandardCost).limit(1))
    if existing.scalar_one_or_none():
        print("  標準原価データ: スキップ（既存データあり）")
        return

    # 39期第1月（2025年10月）の期間IDを取得
    result = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 39, FiscalPeriod.month == 1)
    )
    period_39 = result.scalar_one_or_none()
    if not period_39:
        print("  標準原価データ: スキップ（39期の会計期間なし）")
        return

    prods = await _get_map(db, Product)

    D = Decimal
    # Excel「製品標準原価_製品課生産分」シートの39期標準原価（1個あたり円）
    # (sc_code, 前工程費, 資材費, 労務費, 経費, 計)
    std_cost_data = [
        # 5A
        ("20051200013", 780, 90, 230, 60, 1160),
        ("20071100007", 260, 50, 160, 20, 490),
        # B
        ("20051200005", 200, 330, 330, 60, 920),
        ("20071000005", 10, 10, 10, 0, 30),
        ("20110800311", 200, 870, 400, 60, 1530),
        ("20110800629", 200, 290, 290, 60, 840),
        # BE
        ("20200800016", 250, 1000, 1430, 60, 2740),
        ("20200800017", 50, 90, 140, 10, 290),
        ("20200800018", 760, 1270, 1130, 190, 3350),
        # BM
        ("20240100051", 350, 40, 50, 30, 470),
        # C
        ("20110300008", 150, 1400, 730, 60, 2340),
        # D
        ("20200200001", 100, 160, 90, 30, 380),
        ("20200200003", 20, 160, 180, 10, 370),
        # DC
        ("20211100014", 180, 170, 160, 30, 540),
        ("20211100015", 380, 290, 290, 60, 1020),
        # EB
        ("20071200005", 10, 10, 10, 0, 30),
        ("20231100072", 50, 60, 150, 10, 270),
        ("20231100073", 200, 160, 310, 60, 730),
        ("20231100074", 610, 880, 1000, 190, 2680),
        # FB
        ("20220600066", 290, 1210, 430, 70, 2000),
        ("20221200022", 570, 1070, 750, 130, 2520),
        # G
        ("20080100003", 10, 10, 20, 0, 40),
        ("20110800295", 250, 390, 560, 40, 1240),
        # GP
        ("20231100078", 10, 0, 0, 0, 10),
        ("20230600044", 110, 30, 30, 30, 200),
        ("20230600045", 30, 30, 30, 10, 100),
        ("20230600046", 0, 0, 10, 0, 10),
        ("20241200012", 100, 530, 360, 30, 1020),
        # KOL
        ("20231200033", 100, 110, 420, 30, 660),
        ("20241100041", 10, 1150, 10, 0, 1170),
        ("20250300087", 200, 80, 290, 60, 630),
        # MP
        ("20171000004", 90, 30, 30, 30, 180),
        ("20171000006", 20, 20, 50, 10, 100),
        ("20171000010", 90, 300, 410, 30, 830),
        ("20181100045", 40, 40, 70, 10, 160),
        ("20200200034", 10, 130, 100, 0, 240),
        ("20220100027", 10, 0, 0, 0, 10),
        ("20230900058", 10, 10, 30, 10, 60),
        # O
        ("20060200007", 190, 710, 430, 60, 1390),
        ("20071000014", 10, 10, 10, 0, 30),
        ("20071100028", 200, 260, 280, 60, 800),
        ("20110800312", 190, 1590, 620, 60, 2460),
        ("20140100011", 190, 1980, 420, 60, 2650),
        # P
        ("20061200012", 180, 180, 270, 60, 690),
        ("20070300033", 190, 80, 240, 60, 570),
        ("20080100023", 10, 0, 10, 0, 20),
        ("20090100014", 380, 740, 840, 130, 2090),
        ("20090300004", 60, 320, 210, 20, 610),
        ("20110300007", 180, 500, 240, 60, 980),
        ("20110800918", 190, 1050, 370, 60, 1670),
        ("20210700007", 1270, 120, 2110, 430, 3930),
        ("20220100030", 10, 0, 0, 0, 10),
        ("20221200036", 1270, 120, 2730, 430, 4550),
        ("20230700024", 10, 150, 1700, 0, 1860),
        ("20240400018", 10, 290, 280, 0, 580),
        ("20240400019", 30, 50, 140, 10, 230),
        ("20240400020", 30, 130, 130, 10, 300),
        # PE
        ("20170400004", 10, 0, 10, 0, 20),
        ("20170400005", 20, 20, 20, 10, 70),
        ("20170400006", 90, 20, 30, 30, 170),
        ("20170400017", 40, 40, 80, 10, 170),
        ("20171000009", 90, 300, 350, 30, 770),
        ("20181100042", 10, 50, 120, 0, 180),
        ("20190100014", 60, 30, 30, 20, 140),
        ("20220100028", 0, 0, 0, 0, 0),
        # PG
        ("20050700013", 220, 330, 350, 60, 960),
        ("20080300003", 10, 10, 40, 0, 60),
        ("20091200010", 110, 110, 170, 30, 420),
        ("20091200011", 10, 20, 120, 0, 150),
        ("20221100028", 70, 130, 200, 20, 420),
        # PR
        ("20091200015", 270, 3110, 390, 60, 3830),
        ("20091200016", 10, 1530, 10, 0, 1550),
        # PSA
        ("20120900082", 110, 50, 170, 30, 360),
        ("20130100001", 540, 440, 640, 130, 1750),
        ("20240600040", 30, 90, 100, 10, 230),
        # PX
        ("20170400007", 10, 0, 10, 0, 20),
        ("20170400008", 30, 20, 30, 10, 90),
        ("20170400009", 100, 30, 40, 30, 200),
        ("20170400016", 40, 230, 80, 10, 360),
        ("20171000008", 100, 300, 380, 30, 810),
        ("20180500084", 60, 40, 40, 20, 160),
        ("20181100040", 10, 50, 150, 0, 210),
        ("20191200078", 100, 430, 290, 30, 850),
        # PXM
        ("20201100053", 310, 80, 60, 30, 480),
        ("20201100054", 10, 0, 10, 0, 20),
        ("20220700012", 200, 90, 60, 20, 370),
        # Q
        ("20080700007", 190, 390, 410, 50, 1040),
        # T
        ("20120500014", 1580, 160, 880, 430, 3050),
        ("20120800030", 1030, 120, 270, 280, 1700),
        ("20241000066", 1580, 110, 330, 430, 2450),
        ("20250400005", 15800, 1220, 4240, 42620, 63880),
        # V
        ("20080700011", 10, 10, 10, 0, 30),
        ("20080800002", 40, 100, 130, 10, 280),
        ("20081200016", 730, 1220, 1350, 260, 3560),
        ("20110800272", 210, 1570, 1610, 70, 3460),
        # X
        ("20060800006", 10, 10, 80, 0, 100),
        ("20081200013", 200, 160, 270, 60, 690),
        ("20081200014", 1020, 350, 340, 280, 1990),
        ("20081200019", 2050, 400, 360, 550, 3360),
        ("20230300008", 1020, 250, 220, 280, 1770),
        ("20241200064", 410, 170, 240, 110, 930),
        # XC
        ("20160900041", 1760, 520, 410, 280, 2970),
        ("20160900042", 3510, 410, 500, 550, 4970),
        ("20200300074", 180, 250, 220, 30, 680),
        # Y
        ("20051000011", 740, 750, 880, 190, 2560),
        ("20120300038", 740, 910, 1170, 190, 3010),
        ("20240500062", 10, 1070, 20, 0, 1100),
        # YA
        ("20060100007", 40, 160, 510, 10, 720),
        # YC
        ("20090100015", 160, 130, 360, 10, 660),
        # ZA
        ("20091200012", 170, 110, 190, 30, 500),
        ("20091200013", 10, 20, 40, 0, 70),
    ]

    count = 0
    for sc_code, mae, shizai, roumu, keihi, total in std_cost_data:
        prod = prods.get(sc_code)
        if not prod:
            continue
        db.add(StandardCost(
            product_id=prod.id,
            period_id=period_39.id,
            crude_product_cost=D(str(mae)),
            packaging_cost=D(str(shizai)),
            labor_cost=D(str(roumu)),
            overhead_cost=D(str(keihi)),
            outsourcing_cost=D("0"),
            total_cost=D(str(total)),
            unit_cost=D(str(total)),
            lot_size=D("1"),
            notes="Excel「標準原価_製品_2603.xlsx」39期標準原価",
        ))
        count += 1

    await db.flush()
    print(f"  39期標準原価: {count}件 作成")


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
        await seed_standard_costs_39(db)
        await db.commit()
    print("シードデータ投入完了")


if __name__ == "__main__":
    asyncio.run(main())
