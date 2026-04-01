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
from app.models.cost import CrudeProductStandardCost, StandardCost


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
    # Excel「BOM&原価標準 一覧」「フロー」シートに基づく前工程依存関係
    # 列D = その原体を作る際の入力（前工程原体）
    parent_links = {
        # R系メインライン: R1→R2→R3→R→Rリ→RB→P
        "R2": "R1", "R3": "R2", "R": "R3",
        "Rri": "R", "RB": "Rri", "P": "RB",
        # R派生
        "Rma": "Rri", "MP": "Rma",
        "RG": "Rri", "RGI": "RG", "GP": "RGI",
        "LPA": "Rri",
        "Rshi": "R", "PE": "Rshi",
        "FEB": "R", "T": "FEB",
        "RX": "R",
        # HI系（独立仕込み → HIR→PX→PXA, HIA→HIB→HIB海→X→XC, HIB→B→BM）
        "HIR": "HI", "PX": "HIR", "PXA": "PX",
        "HIA": "HI", "HIB": "HIA", "HIBkai": "HIB",
        "X": "HIBkai", "XC": "X",
        "B": "HIB", "BM": "B",
        # G系（独立仕込み → GA→GB→O→FB）
        "GA": "G", "GB": "GA", "O": "GB", "FB": "O",
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
        # === 半製品（11品）===
        Product(code="20110801158", name="PG 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801158", content_weight_g=D("5"), product_symbol="PG", unit="個"),
        Product(code="20110801159", name="ZA 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801159", content_weight_g=D("5"), product_symbol="ZA", unit="個"),
        Product(code="20110801161", name="BE 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801161", content_weight_g=D("5"), product_symbol="BE", unit="個"),
        Product(code="20110801164", name="ｊPG 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801164", content_weight_g=D("5"), product_symbol="PG", unit="個"),
        Product(code="20110801267", name="EB 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801267", content_weight_g=D("5"), product_symbol="EB", unit="個"),
        Product(code="20110801268", name="V 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801268", content_weight_g=D("5"), product_symbol="V", unit="個"),
        Product(code="20110801273", name="P 2.5g×2", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20110801273", content_weight_g=D("5"), product_symbol="P", unit="個"),
        Product(code="20170500057", name="GINGER 2.5g", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20170500057", content_weight_g=D("2.5"), product_symbol="PE", unit="個"),
        Product(code="20170500058", name="STANDARD 2.5g", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20170500058", content_weight_g=D("2.5"), product_symbol="PE", unit="個"),
        Product(code="20180700008", name="MULBERRY 2.5g", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20180700008", content_weight_g=D("2.5"), product_symbol="MP", unit="個"),
        Product(code="20230600090", name="発酵しょうが 2.5g", product_type=ProductType.semi_finished, product_group="半製品",
                sc_code="20230600090", content_weight_g=D("2.5"), product_symbol="GP", unit="個"),
        # === 製造部生産分（16品）===
        Product(code="20040100009", name="原料 万田酵素(植物用)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20040100009", content_weight_g=D("1000"), product_symbol="X", unit="kg"),
        Product(code="20040500003", name="ﾏﾝﾀﾞFｷｭｰﾌﾞ 5ﾘｯﾄﾙ", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20040500003", content_weight_g=D("6500"), product_symbol="PY", unit="kg"),
        Product(code="20050300004", name="低分子化万田酵素 1kg", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20050300004", content_weight_g=D("1000"), product_symbol="LPA", unit="kg"),
        Product(code="20081000015", name="原料 万田HI酵素(BG 混合品)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20081000015", content_weight_g=D("1000"), product_symbol="BG", unit="kg"),
        Product(code="20090700009", name="犬猫向け植物発酵ｴｷｽ(ｱｰｽ技研)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20090700009", content_weight_g=D("1000"), product_symbol="H", unit="kg"),
        Product(code="20090900007", name="原料 万田酵素金印(OF 混合品)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20090900007", content_weight_g=D("1000"), product_symbol="OF", unit="kg"),
        Product(code="20091200006", name="原料 万田酵素ﾌﾟﾗｽ温(PEA 混合品)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20091200006", content_weight_g=D("1000"), product_symbol="PEA", unit="kg"),
        Product(code="20110400012", name="MKﾐｸｽﾁｬｰ(ﾘｷｯﾄﾞ)(kg)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20110400012", content_weight_g=D("1000"), product_symbol="LPA", unit="kg"),
        Product(code="20110800692", name="原料 万田酵素", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20110800692", content_weight_g=D("1000"), product_symbol="P", unit="kg"),
        Product(code="20111001044", name="畜産用植物性発酵物(A飼料) バルク", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20111001044", content_weight_g=D("1000"), product_symbol="T", unit="kg"),
        Product(code="20180200004", name="原料 万田酵素 PXA (混合品)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20180200004", content_weight_g=D("1000"), product_symbol="PXA", unit="kg"),
        Product(code="20180500057", name="原料 万田酵素 MULBERRY MPA(混合)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20180500057", content_weight_g=D("1000"), product_symbol="MPA", unit="kg"),
        Product(code="20191100098", name="MKﾐｸｽﾁｬｰ(ﾍﾟｰｽﾄ) 20kg", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20191100098", content_weight_g=D("20000"), product_symbol="P", unit="kg"),
        Product(code="20210300049", name="MKﾐｸｽﾁｬｰ(ﾌﾞﾛｯｸﾀｲﾌﾟ)(kg)", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20210300049", content_weight_g=D("1000"), product_symbol="LPZ", unit="kg"),
        Product(code="20240100001", name="原料 万田酵素発酵しょうがGPA混合", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20240100001", content_weight_g=D("1000"), product_symbol="GPA", unit="kg"),
        Product(code="20220300014", name="MANDA HARVEST ｻﾝﾊﾞﾙｸ", product_type=ProductType.in_house_manufacturing, product_group="製造部",
                sc_code="20220300014", content_weight_g=D("1000"), product_symbol="X", unit="kg"),
        # === 製品内製（8品）===
        Product(code="20211100027", name="万田酵素MULBERRY 粒44.1g(30包入)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20211100027", content_weight_g=D("44.1"), product_symbol="内製", unit="個"),
        Product(code="20220100056", name="おいしい青汁 3g×30本(生産用)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20220100056", content_weight_g=D("90"), product_symbol="内製", unit="個"),
        Product(code="20220400011", name="万田酵素GINGER 粒44.1g(生産用)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20220400011", content_weight_g=D("44.1"), product_symbol="内製", unit="個"),
        Product(code="20220400012", name="万田酵素STANDARD 粒44.1g(生産用)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20220400012", content_weight_g=D("44.1"), product_symbol="内製", unit="個"),
        Product(code="20220400033", name="万田酵素STANDARD 粒 20包(生産用)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20220400033", content_weight_g=D("29.4"), product_symbol="内製", unit="個"),
        Product(code="20230600088", name="ﾌﾟﾗｽ温発酵しょうが粒44.1g(生産用)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20230600088", content_weight_g=D("44.1"), product_symbol="内製", unit="個"),
        Product(code="20250300060", name="万田ｱﾐﾉｱﾙﾌｧﾌﾟﾗｽ(1L)(生産用)", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20250300060", content_weight_g=D("1260"), product_symbol="内製", unit="個"),
        Product(code="20240200038", name="MANDA WELLNESS SUPERDRINK 30×3g", product_type=ProductType.outsourced_in_house, product_group="内製",
                sc_code="20240200038", content_weight_g=D("90"), product_symbol="内製", unit="個"),
        # === 外注品（87品）===
        Product(code="20180500083", name="STANDARD粒 7粒", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180500083", content_weight_g=D("0"), unit="個"),
        Product(code="20181100054", name="GINGER粒 7粒", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20181100054", content_weight_g=D("0"), unit="個"),
        Product(code="20211100018", name="MULBERRY粒 7粒", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20211100018", content_weight_g=D("0"), unit="個"),
        Product(code="20220900038", name="おいしい青汁ﾊﾞﾙｸ 3g(新)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220900038", content_weight_g=D("0"), unit="個"),
        Product(code="20230600089", name="ﾌﾟﾗｽ温 発酵しょうが粒 7粒", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20230600089", content_weight_g=D("0"), unit="個"),
        Product(code="20240200039", name="SUPERDRINKﾊﾞﾙｸ 3g(新)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240200039", content_weight_g=D("0"), unit="個"),
        Product(code="20250300059", name="ｱﾐﾉα+1260k", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250300059", content_weight_g=D("0"), unit="個"),
        Product(code="20020400014", name="ﾋﾟｸﾞﾓｰﾝ(A飼料) 5kg", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20020400014", content_weight_g=D("5000"), unit="個"),
        Product(code="20041100007", name="ﾊﾞﾙｸﾞｯﾄﾞ(A飼料) 5kg", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20041100007", content_weight_g=D("5000"), unit="個"),
        Product(code="20061200018", name="万田ｱﾐﾉｱﾙﾌｧ 500ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20061200018", content_weight_g=D("0"), unit="個"),
        Product(code="20061200019", name="万田ｱﾐﾉｱﾙﾌｧ 10kg", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20061200019", content_weight_g=D("10000"), unit="個"),
        Product(code="20061200026", name="万田ｱﾐﾉｱﾙﾌｧ 1ﾘｯﾄﾙ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20061200026", content_weight_g=D("0"), unit="個"),
        Product(code="20091100016", name="万田酵素ﾌﾟﾚﾐｱﾑ粒 105g(300粒)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20091100016", content_weight_g=D("105"), unit="個"),
        Product(code="20100300002", name="万田ｱﾐﾉｱﾙﾌｧ 100ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20100300002", content_weight_g=D("0"), unit="個"),
        Product(code="20100900003", name="MKﾐｸｽﾁｬｰ(ﾊﾟｳﾀﾞｰﾀｲﾌﾟ30) 1kg", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20100900003", content_weight_g=D("1000"), unit="個"),
        Product(code="20110100010", name="万田ｱﾐﾉｱﾙﾌｧﾌﾟﾗｽ 100ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20110100010", content_weight_g=D("0"), unit="個"),
        Product(code="20110100011", name="万田ｱﾐﾉｱﾙﾌｧﾌﾟﾗｽ 500ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20110100011", content_weight_g=D("0"), unit="個"),
        Product(code="20110100012", name="万田ｱﾐﾉｱﾙﾌｧﾌﾟﾗｽ 1ﾘｯﾄﾙ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20110100012", content_weight_g=D("0"), unit="個"),
        Product(code="20110800694", name="万田酵素 抽出液(kg)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20110800694", content_weight_g=D("1000"), unit="kg"),
        Product(code="20111000034", name="プロキュア 60g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20111000034", content_weight_g=D("60"), unit="個"),
        Product(code="20111000035", name="プロキュア 15g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20111000035", content_weight_g=D("15"), unit="個"),
        Product(code="20130400010", name="試供品 万田アミノアルファ 1ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20130400010", content_weight_g=D("0"), unit="個"),
        Product(code="20131000008", name="万田のどら焼き(10個入り)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20131000008", content_weight_g=D("0"), unit="個"),
        Product(code="20131000038", name="ｱﾐﾉｱﾙﾌｧ(韓国向) 500ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20131000038", content_weight_g=D("0"), unit="個"),
        Product(code="20131100025", name="植物用万田酵素ｽﾄﾚｰﾄﾀｲﾌﾟ 900ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20131100025", content_weight_g=D("0"), unit="個"),
        Product(code="20131100036", name="万田のどら焼き(ﾊﾞﾗ)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20131100036", content_weight_g=D("0"), unit="個"),
        Product(code="20140100068", name="ｱﾐﾉｱﾙﾌｧ(韓国向) 1ﾘｯﾄﾙ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20140100068", content_weight_g=D("0"), unit="個"),
        Product(code="20140700032", name="ﾍﾟｯﾄ用万田酵素ﾌｪﾙﾐｯｸ 30g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20140700032", content_weight_g=D("30"), unit="個"),
        Product(code="20140900033", name="ﾍﾟｯﾄ用万田酵素ﾌｪﾙﾐｯｸ 15g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20140900033", content_weight_g=D("15"), unit="個"),
        Product(code="20140900035", name="ﾍﾟｯﾄ用万田酵素ﾌｪﾙﾐｯｸ2.5g試供品", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20140900035", content_weight_g=D("2.5"), unit="個"),
        Product(code="20141200001", name="植物用万田酵素ｽﾄﾚｰﾄﾀｲﾌﾟ ｼｬﾜｰ式", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20141200001", content_weight_g=D("0"), unit="個"),
        Product(code="20170300006", name="保湿泡洗顔(180ml)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20170300006", content_weight_g=D("0"), unit="個"),
        Product(code="20170300007", name="保湿ﾊﾝﾄﾞｸﾘｰﾑ(30g)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20170300007", content_weight_g=D("30"), unit="個"),
        Product(code="20170300008", name="ﾋﾞｭｰﾃｨｰｾﾞﾘｰ 10g×15本", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20170300008", content_weight_g=D("150"), unit="個"),
        Product(code="20170300010", name="黒熟酢(300ml)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20170300010", content_weight_g=D("0"), unit="個"),
        Product(code="20170400035", name="万田酵素ﾌﾟﾚﾐｱﾑ粒 21g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20170400035", content_weight_g=D("21"), unit="個"),
        Product(code="20170500008", name="保湿泡洗顔詰め替え用(160ml)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20170500008", content_weight_g=D("0"), unit="個"),
        Product(code="20180200045", name="肌ごころ 84g×2個", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180200045", content_weight_g=D("168"), unit="個"),
        Product(code="20180200096", name="保湿泡ﾎﾞﾃﾞｨｳｫｯｼｭ 480ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180200096", content_weight_g=D("0"), unit="個"),
        Product(code="20180300016", name="ｴﾑﾌｫﾙﾃ ﾍﾞｰｽｾﾗﾑ 30ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180300016", content_weight_g=D("0"), unit="個"),
        Product(code="20180300020", name="ｴﾑﾌｫﾙﾃ ｳｪﾙｶﾑｷｯﾄ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180300020", content_weight_g=D("0"), unit="個"),
        Product(code="20180500120", name="保湿泡ﾎﾞﾃﾞｨｳｫｯｼｭ 詰め替え 450ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180500120", content_weight_g=D("0"), unit="個"),
        Product(code="20180600015", name="試供品 ｴﾑﾌｫﾙﾃ ﾍﾞｰｽｾﾗﾑ 1.5ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180600015", content_weight_g=D("0"), unit="個"),
        Product(code="20180600016", name="試供品 ｴﾑﾌｫﾙﾃ ﾓｲｽﾁｬｰﾛｰｼｮﾝ 2ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180600016", content_weight_g=D("0"), unit="個"),
        Product(code="20180600017", name="試供品 ｴﾑﾌｫﾙﾃ ｴｯｾﾝｽｴﾏﾙｼﾞｮﾝ 1.5ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180600017", content_weight_g=D("0"), unit="個"),
        Product(code="20180600018", name="試供品 ｴﾑﾌｫﾙﾃ ﾘｯﾁﾓｲｽﾄｸﾘｰﾑ 1g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20180600018", content_weight_g=D("1"), unit="個"),
        Product(code="20190400027", name="ﾋﾞｭｰﾃｨｰﾌﾟﾗｽｾﾞﾘｰﾓｱ 10g×30本", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20190400027", content_weight_g=D("300"), unit="個"),
        Product(code="20200200002", name="万田酵素 超熟 粒 分包 45.5g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20200200002", content_weight_g=D("45.5"), unit="個"),
        Product(code="20200200004", name="万田酵素 超熟 粒 分包 7.3g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20200200004", content_weight_g=D("7.3"), unit="個"),
        Product(code="20200400002", name="霧島黒豚ｶﾚｰ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20200400002", content_weight_g=D("0"), unit="個"),
        Product(code="20200600069", name="MANDA BUTTER CAKE", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20200600069", content_weight_g=D("0"), unit="個"),
        Product(code="20210200051", name="万田酵素くろあめ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20210200051", content_weight_g=D("0"), unit="個"),
        Product(code="20220100037", name="ｴﾑﾌｫﾙﾃﾘﾝｸﾙﾌﾞﾗｲﾄｴｯｾﾝｽ 20g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220100037", content_weight_g=D("20"), unit="個"),
        Product(code="20220100041", name="ｴﾑﾌｫﾙﾃﾘﾝｸﾙﾌﾞﾗｲﾄｴｯｾﾝｽ 1g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220100041", content_weight_g=D("1"), unit="個"),
        Product(code="20220200004", name="試供品 万田酵素 MULBERRY 2.5g(T)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220200004", content_weight_g=D("2.5"), unit="個"),
        Product(code="20220200005", name="試供品 万田酵素 GINGER 2.5g(T)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220200005", content_weight_g=D("2.5"), unit="個"),
        Product(code="20220200007", name="試供品 万田酵素 5g(販売店向け)(T)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220200007", content_weight_g=D("5"), unit="個"),
        Product(code="20220500015", name="万田酵素ﾄﾞﾘﾝｸﾀｲﾌﾟ 50ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220500015", content_weight_g=D("0"), unit="個"),
        Product(code="20220500001", name="お風呂の万田酵素 健酵入浴液300mL", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220500001", content_weight_g=D("0"), unit="個"),
        Product(code="20220600065", name="お風呂の万田酵素 健酵入浴液 30mL", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20220600065", content_weight_g=D("0"), unit="個"),
        Product(code="20231000064", name="ひと粒のちから 55g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20231000064", content_weight_g=D("55"), unit="個"),
        Product(code="20230300006", name="万田酵素から生まれたりんご酢とﾌﾞﾙｰﾍﾞﾘｰ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20230300006", content_weight_g=D("0"), unit="個"),
        Product(code="20240100003", name="水畜産用万田酵素ﾊﾟｳﾀﾞｰ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240100003", content_weight_g=D("0"), unit="個"),
        Product(code="20230900056", name="万田酵素が入った米麹甘酒", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20230900056", content_weight_g=D("0"), unit="個"),
        Product(code="20230900057", name="万田酵素 ｶｰﾌﾊﾞﾗﾝｽ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20230900057", content_weight_g=D("0"), unit="個"),
        Product(code="20231100077", name="試供品 ﾌﾟﾗｽ温発酵しょうが 2.5g(T)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20231100077", content_weight_g=D("2.5"), unit="個"),
        Product(code="20240800027", name="万田発酵ｵｰﾙｲﾝﾜﾝｼﾞｪﾙ 50g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240800027", content_weight_g=D("50"), unit="個"),
        Product(code="20250400008", name="万田発酵のすやすやﾗｲﾌ 15.4g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250400008", content_weight_g=D("15.4"), unit="個"),
        Product(code="20250400007", name="万田発酵のうるうるﾗｲﾌ 12.9g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250400007", content_weight_g=D("12.9"), unit="個"),
        Product(code="20250400006", name="万田発酵のくっきりﾗｲﾌ 10.2g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250400006", content_weight_g=D("10.2"), unit="個"),
        Product(code="20250400009", name="万田発酵のつるんとﾗｲﾌ 7.5g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250400009", content_weight_g=D("7.5"), unit="個"),
        Product(code="20230600096", name="万田酵素50ml瓶ﾄﾞﾘﾝｸ(無印)", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20230600096", content_weight_g=D("0"), unit="個"),
        Product(code="20240800028", name="万田酵素ﾄﾞﾘﾝｸ ﾌﾟﾗｽ 710ml", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240800028", content_weight_g=D("0"), unit="個"),
        Product(code="20240500048", name="Mforteﾓｲｽﾄｾﾗﾑﾏｽｸ27mL 10枚入り", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240500048", content_weight_g=D("0"), unit="個"),
        Product(code="20241000051", name="愛犬おもいの 万田酵素 口腔ｹｱ 50g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20241000051", content_weight_g=D("50"), unit="個"),
        Product(code="20241000052", name="愛猫おもいの 万田酵素 口腔ｹｱ 50g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20241000052", content_weight_g=D("50"), unit="個"),
        Product(code="20241000053", name="愛犬おもいの 万田酵素 関節ｹｱ 50g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20241000053", content_weight_g=D("50"), unit="個"),
        Product(code="20241000054", name="愛猫おもいの 万田酵素 関節ｹｱ 50g", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20241000054", content_weight_g=D("50"), unit="個"),
        Product(code="20250300003", name="試供品 愛犬おもいの万田酵素 口腔ｹｱ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250300003", content_weight_g=D("0"), unit="個"),
        Product(code="20250300004", name="試供品 愛猫おもいの万田酵素 口腔ｹｱ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250300004", content_weight_g=D("0"), unit="個"),
        Product(code="20250300005", name="試供品 愛犬おもいの万田酵素 関節ｹｱ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250300005", content_weight_g=D("0"), unit="個"),
        Product(code="20250300006", name="試供品 愛猫おもいの万田酵素 関節ｹｱ", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20250300006", content_weight_g=D("0"), unit="個"),
        Product(code="20240700084", name="MKﾐｸｽﾁｬｰ(ﾊﾟｳﾀﾞｰ30) 1kg", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240700084", content_weight_g=D("1000"), unit="個"),
        Product(code="20240700083", name="MKﾐｸｽﾁｬｰ(ﾊﾟｳﾀﾞｰ) 1kg", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20240700083", content_weight_g=D("1000"), unit="個"),
        Product(code="20241000056", name="ｴﾑﾌｫﾙﾃ ﾘﾝｸﾙﾌﾞﾗｲﾄｴｯｾﾝｽ 20g②", product_type=ProductType.outsourced, product_group="外注",
                sc_code="20241000056", content_weight_g=D("20"), unit="個"),
        # === その他（25品）===
        Product(code="20080700014", name="試供品 万田酵素分包 35g", product_type=ProductType.special, product_group="その他",
                sc_code="20080700014", content_weight_g=D("35"), unit="個"),
        Product(code="20110800273", name="ｽｰﾊﾟｰ万田酵素 氣Ⅰ(2本ｾｯﾄ)", product_type=ProductType.special, product_group="その他",
                sc_code="20110800273", content_weight_g=D("350"), unit="個"),
        Product(code="20110800287", name="業務用酵素 万田酵素 1kg", product_type=ProductType.special, product_group="その他",
                sc_code="20110800287", content_weight_g=D("1000"), unit="個"),
        Product(code="20161100033", name="秘蔵 万田酵素 145g", product_type=ProductType.special, product_group="その他",
                sc_code="20161100033", content_weight_g=D("145"), unit="個"),
        Product(code="20170400002", name="試供品 万田酵素 GINGER 粒", product_type=ProductType.special, product_group="その他",
                sc_code="20170400002", content_weight_g=D("0"), unit="個"),
        Product(code="20171000005", name="試供品 万田酵素 MULBERRY 2.5g", product_type=ProductType.special, product_group="その他",
                sc_code="20171000005", content_weight_g=D("2.5"), unit="個"),
        Product(code="20180100007", name="万田酵素MULBERRY 粒 44.1g", product_type=ProductType.special, product_group="その他",
                sc_code="20180100007", content_weight_g=D("44.1"), unit="個"),
        Product(code="20180100008", name="万田酵素STANDARD 粒 44.1g", product_type=ProductType.special, product_group="その他",
                sc_code="20180100008", content_weight_g=D("44.1"), unit="個"),
        Product(code="20180100009", name="万田酵素GINGER 粒 44.1g", product_type=ProductType.special, product_group="その他",
                sc_code="20180100009", content_weight_g=D("44.1"), unit="個"),
        Product(code="20180200007", name="試供品 万田酵素 STANDARD 粒", product_type=ProductType.special, product_group="その他",
                sc_code="20180200007", content_weight_g=D("0"), unit="個"),
        Product(code="20180200006", name="試供品 万田酵素 MULBERRY 粒", product_type=ProductType.special, product_group="その他",
                sc_code="20180200006", content_weight_g=D("0"), unit="個"),
        Product(code="20180300017", name="ｴﾑﾌｫﾙﾃ ﾓｲｽﾁｬｰﾛｰｼｮﾝ 120ml", product_type=ProductType.special, product_group="その他",
                sc_code="20180300017", content_weight_g=D("0"), unit="個"),
        Product(code="20180300018", name="ｴﾑﾌｫﾙﾃ ｴｯｾﾝｽｴﾏﾙｼﾞｮﾝ 60ml", product_type=ProductType.special, product_group="その他",
                sc_code="20180300018", content_weight_g=D("0"), unit="個"),
        Product(code="20180300019", name="ｴﾑﾌｫﾙﾃ ﾘｯﾁﾓｲｽﾄｸﾘｰﾑ 30g", product_type=ProductType.special, product_group="その他",
                sc_code="20180300019", content_weight_g=D("30"), unit="個"),
        Product(code="20211000062", name="植物用万田酵素 粒状ﾀｲﾌﾟ 300g", product_type=ProductType.special, product_group="その他",
                sc_code="20211000062", content_weight_g=D("300"), unit="個"),
        Product(code="20220500006", name="試供品 植物用万田酵素 粒状ﾀｲﾌﾟ 7g", product_type=ProductType.special, product_group="その他",
                sc_code="20220500006", content_weight_g=D("7"), unit="個"),
        Product(code="20230300009", name="健康農業のための万田酵素 試供品", product_type=ProductType.special, product_group="その他",
                sc_code="20230300009", content_weight_g=D("0"), unit="個"),
        Product(code="20230600087", name="試供品 ﾌﾟﾗｽ温発酵しょうが粒", product_type=ProductType.special, product_group="その他",
                sc_code="20230600087", content_weight_g=D("0"), unit="個"),
        Product(code="20230300007", name="植物発酵ｴｷｽ ｱﾚﾙｷﾞｰ特定原材料", product_type=ProductType.special, product_group="その他",
                sc_code="20230300007", content_weight_g=D("0"), unit="個"),
        Product(code="20240200017", name="植物発酵ｴｷｽ 万田酵素 20kg", product_type=ProductType.special, product_group="その他",
                sc_code="20240200017", content_weight_g=D("20000"), unit="個"),
        Product(code="20230600086", name="万田酵素ﾌﾟﾗｽ温発酵しょうが粒", product_type=ProductType.special, product_group="その他",
                sc_code="20230600086", content_weight_g=D("0"), unit="個"),
        Product(code="20240400033", name="ｴﾑﾌｫﾙﾃ ﾓｲｽﾄｾﾗﾑﾏｽｸ 27mL", product_type=ProductType.special, product_group="その他",
                sc_code="20240400033", content_weight_g=D("0"), unit="個"),
        Product(code="20240700045", name="万田酵素(宇宙用) 2.5g×4包", product_type=ProductType.special, product_group="その他",
                sc_code="20240700045", content_weight_g=D("10"), unit="個"),
        Product(code="20240900105", name="Mforteｻﾝﾌﾟﾙｾｯﾄ(4種)", product_type=ProductType.special, product_group="その他",
                sc_code="20240900105", content_weight_g=D("0"), unit="個"),
        Product(code="20241000009", name="ｴﾑﾌｫﾙﾃ ﾓｲｽﾄｾﾗﾑﾏｽｸ 27mL 1枚入り", product_type=ProductType.special, product_group="その他",
                sc_code="20241000009", content_weight_g=D("0"), unit="個"),
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
    # RX: R派生（植物用レギュラー）
    await _create_bom("RX", BomType.crude_product_process, [
        ("@R", "1.0"),
    ], "0.9800")
    # === HI系（独立仕込み: 植物XX種類(*2)） ===
    await _create_bom("HI", BomType.raw_material_process, r1_materials, "0.9500")
    # HIR: HI → HIR
    await _create_bom("HIR", BomType.crude_product_process, [
        ("@HI", "1.0"),
    ], "0.9900")
    # PX: HIR → PX
    await _create_bom("PX", BomType.crude_product_process, [
        ("@HIR", "1.0"),
    ], "0.9900")
    # PXA: PX → PXA
    await _create_bom("PXA", BomType.crude_product_process, [
        ("@PX", "1.0"),
    ], "0.9900")
    # HIA: HI → HIA
    await _create_bom("HIA", BomType.crude_product_process, [
        ("@HI", "1.0"),
    ], "0.9900")
    # HIB: HIA → HIB
    await _create_bom("HIB", BomType.crude_product_process, [
        ("@HIA", "1.0"),
    ], "0.9900")
    # HIB海: HIB → HIB海
    await _create_bom("HIBkai", BomType.crude_product_process, [
        ("@HIB", "1.0"),
    ], "0.9900")
    # X: HIB海 → X
    await _create_bom("X", BomType.crude_product_process, [
        ("@HIBkai", "1.0"),
    ], "0.9900")
    # XC: X → XC
    await _create_bom("XC", BomType.crude_product_process, [
        ("@X", "1.0"),
    ], "0.9900")
    # B: HIB → B
    await _create_bom("B", BomType.crude_product_process, [
        ("@HIB", "1.0"),
    ], "0.9900")
    # BM: B → BM
    await _create_bom("BM", BomType.crude_product_process, [
        ("@B", "1.0"),
    ], "0.9900")
    # === G系（独立仕込み: 植物XX種類(*3)） ===
    await _create_bom("G", BomType.raw_material_process, r1_materials, "0.9500")
    # GA: G → GA
    await _create_bom("GA", BomType.crude_product_process, [
        ("@G", "1.0"),
    ], "0.9900")
    # GB: GA → GB
    await _create_bom("GB", BomType.crude_product_process, [
        ("@GA", "1.0"),
    ], "0.9900")
    # O: GB → O
    await _create_bom("O", BomType.crude_product_process, [
        ("@GB", "1.0"),
    ], "0.9900")
    # FB: O → FB
    await _create_bom("FB", BomType.crude_product_process, [
        ("@O", "1.0"),
    ], "0.9900")
    # === 植物用ブレンド（独立: 前工程費=38期実績） ===
    await _create_bom("plant", BomType.raw_material_process, r1_materials, "0.9500")

    await db.flush()
    print(f"  原体BOM: {bom_count}件 作成（多段階工程チェーン）")

    # === Stage 2: 製品BOM (product_process) ===
    # 製品BOM: 原体 + 資材 → 製品
    # 製品記号 → 主要仕掛品原体コードのマッピング（フロー図の製品行に対応）
    symbol_to_crude = {
        "5A": "P", "B": "B", "BE": "B", "BM": "BM", "C": "Rshi",
        "D": "B", "DC": "B", "EB": "FB", "FB": "FB", "G": "G",
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


async def seed_crude_product_standard_costs_39(db: AsyncSession) -> None:
    """Excel「標準原価_原材・仕掛品_2603v5ー2.xlsx」BOM&原価標準一覧の全原体標準原価を投入。"""
    existing = await db.execute(select(CrudeProductStandardCost).limit(1))
    if existing.scalar_one_or_none():
        print("  原体標準原価: スキップ（既存データあり）")
        return

    result = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 39, FiscalPeriod.month == 1)
    )
    period_39 = result.scalar_one_or_none()
    if not period_39:
        print("  原体標準原価: スキップ（39期の会計期間なし）")
        return

    cps = await _get_map(db, CrudeProduct)
    D = Decimal

    # Excel「BOM&原価標準 一覧」シートの全原体39期標準原価
    # (原体code, 前工程費, 原材料費, 労務費, 経費, 計)  ※経費=30円/kg（共通配賦）
    crude_std_data = [
        # === Rメインライン: R1→R2→R3→R→Rリ→RB→P ===
        ("R1", "0", "283.2", "103", "30", "416.2"),
        ("R2", "0", "533", "140", "60", "733"),
        ("R3", "0", "536", "114", "90", "740"),
        ("R", "878", "0", "0", "30", "908"),
        ("Rri", "908", "14.1184", "44", "30", "996.1184"),
        ("RB", "996.1184", "0", "0.4", "30", "1026.5184"),
        ("P", "1026.5184", "0", "237", "30", "1293.5184"),
        # === Rリ派生 ===
        ("Rma", "996.1184", "79", "69.9", "30", "1175.0184"),  # マルベリー
        ("MP", "1175.0184", "0", "168.3", "30", "1373.3184"),
        ("RG", "996.1184", "41", "61.3", "30", "1128.4184"),   # ジンジャー
        ("RGI", "1128.4184", "0", "228.8", "30", "1387.2184"),
        ("GP", "1387.2184", "0", "105.9", "30", "1523.1184"),
        ("LPA", "996.1184", "0", "469.5", "30", "1495.6184"),  # 低分子
        # === R派生 ===
        ("Rshi", "908", "0", "53", "30", "991"),       # 生姜系
        ("PE", "991", "0", "192", "30", "1213"),
        ("FEB", "908", "0", "478", "30", "1416"),       # 畜産系
        ("T", "1416", "0", "137", "30", "1583"),
        ("RX", "735", "0", "82", "30", "847"),          # 植物用R
        # === HI系 ===
        ("HI", "1142", "0", "4", "30", "1176"),
        ("HIR", "1176", "0", "8", "30", "1214"),
        ("PX", "1214", "0", "96", "30", "1340"),
        ("PXA", "1340", "0", "424", "30", "1794"),
        ("HIA", "1176", "0", "48", "30", "1254"),
        ("HIB", "1254", "0", "0", "30", "1284"),
        ("HIBkai", "1284", "0", "0", "30", "1314"),
        # === X系 ===
        ("X", "1314", "0", "94", "30", "1438"),
        ("XC", "1438", "832", "114", "30", "2414"),     # 納豆菌添加
        # === B系 ===
        ("B", "1284", "0", "141", "30", "1455"),
        ("BM", "1455", "3792", "503", "30", "5780"),    # マヌカハニー
        # === G系: P→G→GA→GB→O→FB ===
        ("G", "1293.5184", "967.2", "54", "30", "2344.7184"),   # シャンピニオンエキス
        ("GA", "2344.7184", "0", "0", "30", "2374.7184"),
        ("GB", "2374.7184", "0", "0", "30", "2404.7184"),
        ("O", "2404.7184", "0", "110", "30", "2544.7184"),
        ("FB", "2544.7184", "333", "85", "30", "2992.7184"),
        # === その他 ===
        ("plant", "1217", "0", "0", "30", "1247"),
        ("other", "1200", "0", "0", "0", "1200"),
    ]

    count = 0
    for code, mae, mat, roumu, keihi, total in crude_std_data:
        cp = cps.get(code)
        if not cp:
            continue
        db.add(CrudeProductStandardCost(
            crude_product_id=cp.id,
            period_id=period_39.id,
            prior_process_cost=D(str(mae)),
            material_cost=D(str(mat)),
            labor_cost=D(str(roumu)),
            overhead_cost=D(str(keihi)),
            total_cost=D(str(total)),
            unit_cost=D(str(total)),
            standard_quantity=D("1"),
            notes="Excel「標準原価_原材・仕掛品_2603v5ー2.xlsx」39期標準原価",
        ))
        count += 1

    await db.flush()
    print(f"  原体標準原価: {count}件 作成")


async def seed_standard_costs_39(db: AsyncSession) -> None:
    """Excel「標準原価_製品_2603v5ー2.xlsx」製品標準原価シートの39期標準原価を全量投入。"""
    existing = await db.execute(select(StandardCost).limit(1))
    if existing.scalar_one_or_none():
        print("  標準原価データ: スキップ（既存データあり）")
        return

    result = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 39, FiscalPeriod.month == 1)
    )
    period_39 = result.scalar_one_or_none()
    if not period_39:
        print("  標準原価データ: スキップ（39期の会計期間なし）")
        return

    prods = await _get_map(db, Product)

    D = Decimal
    # Excel「製品標準原価」シート 39期標準原価（1個あたり円、ROUND済み整数）
    # (sc_code, 前工程費, 資材費, 労務費, 経費, 外注加工費, 計)
    std_cost_data = [
        # === 品（製品課等生産分）111品 ===
        ("20050700013", 225, 462, 349, 64, 0, 1100),
        ("20051000011", 738, 1043, 883, 193, 0, 2857),
        ("20051200005", 202, 466, 328, 64, 0, 1060),
        ("20051200013", 776, 122, 226, 64, 0, 1188),
        ("20060100007", 45, 221, 514, 13, 0, 793),
        ("20060200007", 192, 993, 425, 62, 0, 1672),
        ("20060800006", 12, 19, 83, 3, 0, 117),
        ("20061200012", 184, 249, 272, 62, 0, 767),
        ("20070300033", 190, 117, 243, 64, 0, 614),
        ("20071000005", 7, 9, 12, 2, 0, 30),
        ("20071000014", 7, 12, 14, 2, 0, 35),
        ("20071100007", 259, 70, 157, 21, 0, 507),
        ("20071100028", 198, 357, 281, 64, 0, 900),
        ("20071200005", 7, 10, 13, 2, 0, 32),
        ("20080100003", 14, 8, 20, 2, 0, 44),
        ("20080100023", 6, 4, 12, 2, 0, 24),
        ("20080300003", 7, 15, 41, 2, 0, 65),
        ("20080700007", 194, 538, 414, 54, 0, 1200),
        ("20080700011", 6, 8, 12, 2, 0, 28),
        ("20080800002", 42, 137, 129, 15, 0, 323),
        ("20081200013", 205, 226, 270, 56, 0, 757),
        ("20081200014", 1023, 495, 340, 279, 0, 2137),
        ("20081200016", 727, 1702, 1349, 257, 0, 4035),
        ("20081200019", 2045, 564, 363, 557, 0, 3529),
        ("20090100014", 380, 1028, 835, 129, 0, 2372),
        ("20090100015", 164, 181, 360, 13, 0, 718),
        ("20090300004", 63, 444, 209, 21, 0, 737),
        ("20091200010", 112, 159, 166, 32, 0, 469),
        ("20091200011", 7, 30, 121, 2, 0, 160),
        ("20091200012", 166, 159, 185, 32, 0, 542),
        ("20091200013", 11, 30, 44, 2, 0, 87),
        ("20091200015", 271, 254, 387, 64, 0, 976),
        ("20091200016", 9, 22, 12, 2, 0, 45),
        ("20110300007", 184, 705, 239, 62, 0, 1190),
        ("20110300008", 150, 1961, 727, 62, 0, 2900),
        ("20110800272", 212, 2198, 1606, 75, 0, 4091),
        ("20110800295", 250, 539, 564, 39, 0, 1392),
        ("20110800311", 196, 1217, 398, 62, 0, 1873),
        ("20110800312", 192, 2219, 623, 62, 0, 3096),
        ("20110800629", 196, 409, 292, 62, 0, 959),
        ("20110800918", 190, 1464, 366, 64, 0, 2084),
        ("20120300038", 738, 1267, 1171, 193, 0, 3369),
        ("20120500014", 1580, 219, 876, 429, 0, 3104),
        ("20120800030", 1027, 170, 274, 279, 0, 1750),
        ("20120900082", 108, 75, 172, 26, 0, 381),
        ("20130100001", 538, 608, 641, 129, 0, 1916),
        ("20140100011", 192, 2771, 419, 62, 0, 3444),
        ("20160900041", 1757, 727, 408, 279, 0, 3171),
        ("20160900042", 3514, 570, 500, 557, 0, 5141),
        ("20170400004", 3, 3, 11, 1, 0, 18),
        ("20170400005", 23, 29, 20, 9, 0, 81),
        ("20170400006", 89, 34, 27, 33, 0, 183),
        ("20170400007", 3, 3, 11, 1, 0, 18),
        ("20170400008", 25, 30, 28, 9, 0, 92),
        ("20170400009", 97, 40, 45, 33, 0, 215),
        ("20170400016", 44, 317, 81, 15, 0, 457),
        ("20170400017", 40, 62, 81, 15, 0, 198),
        ("20171000004", 91, 40, 26, 33, 0, 190),
        ("20171000006", 24, 29, 46, 9, 0, 108),
        ("20171000008", 98, 413, 377, 33, 0, 921),
        ("20171000009", 90, 413, 349, 33, 0, 885),
        ("20171000010", 92, 413, 413, 33, 0, 951),
        ("20180500084", 63, 51, 36, 21, 0, 171),
        ("20181100040", 13, 69, 148, 4, 0, 234),
        ("20181100042", 11, 69, 120, 4, 0, 204),
        ("20181100045", 41, 49, 75, 15, 0, 180),
        ("20190100014", 57, 47, 34, 21, 0, 159),
        ("20191200078", 97, 595, 286, 33, 0, 1011),
        ("20200200001", 105, 226, 92, 33, 0, 456),
        ("20200200003", 17, 225, 180, 5, 0, 427),
        ("20200200034", 12, 178, 97, 4, 0, 291),
        ("20200300074", 176, 348, 218, 28, 0, 770),
        ("20200800016", 246, 1390, 1433, 62, 0, 3131),
        ("20200800017", 51, 131, 142, 13, 0, 337),
        ("20200800018", 763, 1771, 1130, 193, 0, 3857),
        ("20201100053", 311, 113, 58, 33, 0, 515),
        ("20201100054", 10, 6, 11, 1, 0, 28),
        ("20210700007", 1266, 173, 2109, 429, 0, 3977),
        ("20211100014", 178, 242, 164, 30, 0, 614),
        ("20211100015", 381, 410, 294, 64, 0, 1149),
        ("20220100027", 3, 0, 3, 1, 0, 7),
        ("20220100028", 3, 1, 2, 1, 0, 7),
        ("20220100030", 6, 2, 3, 2, 0, 13),
        ("20231100078", 3, 0, 2, 1, 0, 6),
        ("20220600066", 294, 1684, 435, 66, 0, 2479),
        ("20220700012", 200, 125, 60, 21, 0, 406),
        ("20221100028", 75, 177, 201, 21, 0, 474),
        ("20221200022", 568, 1492, 754, 129, 0, 2943),
        ("20221200036", 1266, 173, 2732, 429, 0, 4600),
        ("20230300008", 1023, 355, 224, 279, 0, 1881),
        ("20230600044", 11, 37, 26, 33, 0, 107),
        ("20230600045", 28, 35, 26, 9, 0, 98),
        ("20230600046", 3, 6, 11, 1, 0, 21),
        ("20230700024", 6, 215, 1698, 2, 0, 1921),
        ("20231100072", 48, 85, 150, 15, 0, 298),
        ("20231100073", 204, 222, 307, 64, 0, 797),
        ("20231100074", 611, 1225, 999, 193, 0, 3028),
        ("20231200033", 98, 153, 422, 32, 0, 705),
        ("20240100051", 349, 60, 52, 33, 0, 494),
        ("20230900058", 15, 18, 30, 5, 0, 68),
        ("20240400018", 13, 398, 280, 4, 0, 695),
        ("20240400019", 25, 76, 140, 9, 0, 250),
        ("20240400020", 25, 185, 132, 9, 0, 351),
        ("20240500062", 8, 15, 18, 2, 0, 43),
        ("20240600040", 25, 125, 97, 6, 0, 253),
        ("20241000066", 1580, 149, 330, 429, 0, 2488),
        ("20241100041", 7, 17, 11, 2, 0, 37),
        ("20241200012", 105, 740, 357, 32, 0, 1234),
        ("20241200064", 409, 239, 242, 111, 0, 1001),
        ("20250300087", 195, 108, 289, 64, 0, 656),
        ("20250400005", 15801, 1697, 4236, 4286, 0, 26020),
        # === 半（半製品）11品 ===
        ("20110801158", 0, 0, 0, 0, 0, 66),
        ("20110801159", 0, 0, 0, 0, 0, 0),
        ("20110801161", 0, 0, 0, 0, 0, 0),
        ("20110801164", 0, 0, 0, 0, 0, 66),
        ("20110801267", 0, 0, 0, 0, 0, 32),
        ("20110801268", 0, 0, 0, 0, 0, 29),
        ("20110801273", 0, 0, 0, 0, 0, 13),
        ("20170500057", 0, 0, 0, 0, 0, 7),
        ("20170500058", 0, 0, 0, 0, 0, 19),
        ("20180700008", 0, 0, 0, 0, 0, 7),
        ("20230600090", 0, 0, 0, 0, 0, 8),
        # === 造（製造部生産分）16品 ===
        ("20040100009", 1573, 0, 34, 0, 0, 1607),
        ("20040500003", 0, 0, 0, 0, 0, 0),
        ("20050300004", 1752, 158, 40, 0, 0, 1950),
        ("20081000015", 2500, 0, 136, 0, 0, 2636),
        ("20090700009", 1127, 0, 157, 0, 0, 1284),
        ("20090900007", 1978, 0, 80, 0, 0, 2058),
        ("20091200006", 1303, 0, 32, 0, 0, 1335),
        ("20110400012", 1752, 158, 40, 0, 0, 1950),
        ("20110800692", 1266, 0, 17, 0, 0, 1283),
        ("20111001044", 1580, 0, 34, 0, 0, 1614),
        ("20180200004", 2088, 0, 43, 0, 0, 2131),
        ("20180500057", 1295, 0, 38, 0, 0, 1333),
        ("20191100098", 25314, 0, 332, 0, 0, 25646),
        ("20210300049", 760, 10, 208, 0, 0, 978),
        ("20240100001", 3132, 0, 73, 0, 0, 3205),
        ("20220300014", 1573, 0, 11, 0, 0, 1584),
        # === 内（製品内製）8品 ===
        ("20211100027", 127, 59, 180, 19, 0, 385),
        ("20220100056", 470, 53, 226, 39, 0, 788),
        ("20220400011", 538, 42, 180, 19, 0, 779),
        ("20220400012", 413, 61, 180, 19, 0, 673),
        ("20220400033", 275, 36, 150, 13, 0, 474),
        ("20230600088", 186, 59, 182, 19, 0, 446),
        ("20250300060", 663, 3, 138, 540, 0, 1344),
        ("20240200038", 454, 1623, 249, 39, 0, 2365),
        # === 外（外注品）87品 — 外注加工費のみ ===
        ("20180500083", 0, 0, 0, 0, 13, 13),
        ("20181100054", 0, 0, 0, 0, 13, 13),
        ("20211100018", 0, 0, 0, 0, 14, 14),
        ("20220900038", 0, 0, 0, 0, 17, 17),
        ("20230600089", 0, 0, 0, 0, 14, 14),
        ("20240200039", 0, 0, 0, 0, 19, 19),
        ("20250300059", 0, 0, 0, 0, 653007, 653007),
        ("20020400014", 0, 0, 0, 0, 2939, 2939),
        ("20041100007", 0, 0, 0, 0, 7161, 7161),
        ("20061200018", 0, 0, 0, 0, 475, 475),
        ("20061200019", 0, 0, 0, 0, 3121, 3121),
        ("20061200026", 0, 0, 0, 0, 641, 641),
        ("20091100016", 0, 0, 0, 0, 1058, 1058),
        ("20100300002", 0, 0, 0, 0, 198, 198),
        ("20100900003", 0, 0, 0, 0, 3418, 3418),
        ("20110100010", 0, 0, 0, 0, 191, 191),
        ("20110100011", 0, 0, 0, 0, 476, 476),
        ("20110100012", 0, 0, 0, 0, 651, 651),
        ("20110800694", 0, 0, 0, 0, 4792, 4792),
        ("20111000034", 0, 0, 0, 0, 866, 866),
        ("20111000035", 0, 0, 0, 0, 331, 331),
        ("20130400010", 0, 0, 0, 0, 32, 32),
        ("20131000008", 0, 0, 0, 0, 1595, 1595),
        ("20131000038", 0, 0, 0, 0, 480, 480),
        ("20131100025", 0, 0, 0, 0, 187, 187),
        ("20131100036", 0, 0, 0, 0, 158, 158),
        ("20140100068", 0, 0, 0, 0, 650, 650),
        ("20140700032", 0, 0, 0, 0, 711, 711),
        ("20140900033", 0, 0, 0, 0, 561, 561),
        ("20140900035", 0, 0, 0, 0, 299, 299),
        ("20141200001", 0, 0, 0, 0, 243, 243),
        ("20170300006", 0, 0, 0, 0, 477, 477),
        ("20170300007", 0, 0, 0, 0, 444, 444),
        ("20170300008", 0, 0, 0, 0, 512, 512),
        ("20170300010", 0, 0, 0, 0, 483, 483),
        ("20170400035", 0, 0, 0, 0, 273, 273),
        ("20170500008", 0, 0, 0, 0, 208, 208),
        ("20180200045", 0, 0, 0, 0, 349, 349),
        ("20180200096", 0, 0, 0, 0, 739, 739),
        ("20180300016", 0, 0, 0, 0, 757, 757),
        ("20180300020", 0, 0, 0, 0, 1081, 1081),
        ("20180500120", 0, 0, 0, 0, 544, 544),
        ("20180600015", 0, 0, 0, 0, 23, 23),
        ("20180600016", 0, 0, 0, 0, 19, 19),
        ("20180600017", 0, 0, 0, 0, 19, 19),
        ("20180600018", 0, 0, 0, 0, 21, 21),
        ("20190400027", 0, 0, 0, 0, 1296, 1296),
        ("20200200002", 0, 0, 0, 0, 655, 655),
        ("20200200004", 0, 0, 0, 0, 206, 206),
        ("20200400002", 0, 0, 0, 0, 243, 243),
        ("20200600069", 0, 0, 0, 0, 130, 130),
        ("20210200051", 0, 0, 0, 0, 166, 166),
        ("20220100037", 0, 0, 0, 0, 524, 524),
        ("20220100041", 0, 0, 0, 0, 86, 86),
        ("20220200004", 0, 0, 0, 0, 17, 17),
        ("20220200005", 0, 0, 0, 0, 17, 17),
        ("20220200007", 0, 0, 0, 0, 17, 17),
        ("20220500015", 0, 0, 0, 0, 51, 51),
        ("20220500001", 0, 0, 0, 0, 993, 993),
        ("20220600065", 0, 0, 0, 0, 106, 106),
        ("20231000064", 0, 0, 0, 0, 820, 820),
        ("20230300006", 0, 0, 0, 0, 67, 67),
        ("20240100003", 0, 0, 0, 0, 219, 219),
        ("20230900056", 0, 0, 0, 0, 77, 77),
        ("20230900057", 0, 0, 0, 0, 700, 700),
        ("20231100077", 0, 0, 0, 0, 17, 17),
        ("20240800027", 0, 0, 0, 0, 1221, 1221),
        ("20250400008", 0, 0, 0, 0, 747, 747),
        ("20250400007", 0, 0, 0, 0, 602, 602),
        ("20250400006", 0, 0, 0, 0, 382, 382),
        ("20250400009", 0, 0, 0, 0, 330, 330),
        ("20230600096", 0, 0, 0, 0, 185, 185),
        ("20240800028", 0, 0, 0, 0, 961, 961),
        ("20240500048", 0, 0, 0, 0, 3755, 3755),
        ("20241000051", 0, 0, 0, 0, 380, 380),
        ("20241000052", 0, 0, 0, 0, 380, 380),
        ("20241000053", 0, 0, 0, 0, 380, 380),
        ("20241000054", 0, 0, 0, 0, 380, 380),
        ("20250300003", 0, 0, 0, 0, 35, 35),
        ("20250300004", 0, 0, 0, 0, 35, 35),
        ("20250300005", 0, 0, 0, 0, 35, 35),
        ("20250300006", 0, 0, 0, 0, 35, 35),
        ("20240700084", 0, 0, 0, 0, 2751, 2751),
        ("20240700083", 0, 0, 0, 0, 4364, 4364),
        ("20241000056", 0, 0, 0, 0, 757, 757),
        # === 他（その他）25品 — 合計のみ ===
        ("20080700014", 0, 0, 0, 0, 0, 243),
        ("20110800273", 0, 0, 0, 0, 0, 8280),
        ("20110800287", 0, 0, 0, 0, 0, 2254),
        ("20161100033", 0, 0, 0, 0, 0, 5060),
        ("20170400002", 0, 0, 0, 0, 0, 16),
        ("20171000005", 0, 0, 0, 0, 0, 19),
        ("20180100007", 0, 0, 0, 0, 0, 400),
        ("20180100008", 0, 0, 0, 0, 0, 661),
        ("20180100009", 0, 0, 0, 0, 0, 744),
        ("20180200007", 0, 0, 0, 0, 0, 14),
        ("20180200006", 0, 0, 0, 0, 0, 10),
        ("20180300017", 0, 0, 0, 0, 0, 607),
        ("20180300018", 0, 0, 0, 0, 0, 622),
        ("20180300019", 0, 0, 0, 0, 0, 749),
        ("20211000062", 0, 0, 0, 0, 0, 232),
        ("20220500006", 0, 0, 0, 0, 0, 10),
        ("20230300009", 0, 0, 0, 0, 0, 205),
        ("20230600087", 0, 0, 0, 0, 0, 12),
        ("20230300007", 0, 0, 0, 0, 0, 2932),
        ("20240200017", 0, 0, 0, 0, 0, 19668),
        ("20230600086", 0, 0, 0, 0, 0, 453),
        ("20240400033", 0, 0, 0, 0, 0, 376),
        ("20240700045", 0, 0, 0, 0, 0, 583),
        ("20240900105", 0, 0, 0, 0, 0, 81),
        ("20241000009", 0, 0, 0, 0, 0, 376),
    ]

    count = 0
    for sc_code, mae, shizai, roumu, keihi, gaichuu, total in std_cost_data:
        prod = prods.get(sc_code)
        if not prod:
            continue
        if total == 0:
            continue
        db.add(StandardCost(
            product_id=prod.id,
            period_id=period_39.id,
            crude_product_cost=D(str(mae)),
            packaging_cost=D(str(shizai)),
            labor_cost=D(str(roumu)),
            overhead_cost=D(str(keihi)),
            outsourcing_cost=D(str(gaichuu)),
            total_cost=D(str(total)),
            unit_cost=D(str(total)),
            lot_size=D("1"),
            notes="Excel「標準原価_製品_2603v5ー2.xlsx」39期標準原価",
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
        await seed_crude_product_standard_costs_39(db)
        await seed_standard_costs_39(db)
        await db.commit()
    print("シードデータ投入完了")


if __name__ == "__main__":
    asyncio.run(main())
