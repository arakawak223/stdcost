from fastapi import APIRouter

from app.api.v1 import (
    actual_costs,
    ai,
    allocation_rules,
    bom,
    contractors,
    cost_budgets,
    cost_centers,
    costs,
    crude_products,
    fiscal_periods,
    imports,
    inventory,
    materials,
    products,
    reconciliation,
    variances,
)

router = APIRouter(prefix="/api/v1")

router.include_router(products.router, prefix="/masters/products", tags=["製品マスタ"])
router.include_router(crude_products.router, prefix="/masters/crude-products", tags=["原体マスタ"])
router.include_router(cost_centers.router, prefix="/masters/cost-centers", tags=["部門マスタ"])
router.include_router(materials.router, prefix="/masters/materials", tags=["原材料マスタ"])
router.include_router(contractors.router, prefix="/masters/contractors", tags=["外注先マスタ"])
router.include_router(fiscal_periods.router, prefix="/masters/fiscal-periods", tags=["会計期間"])
router.include_router(bom.router, prefix="/masters/bom", tags=["BOM管理"])
router.include_router(allocation_rules.router, prefix="/masters/allocation-rules", tags=["配賦ルール"])
router.include_router(cost_budgets.router, prefix="/masters/cost-budgets", tags=["予算管理"])
router.include_router(costs.router, prefix="/costs/standard", tags=["標準原価計算"])
router.include_router(actual_costs.router, prefix="/costs/actual", tags=["実際原価"])
router.include_router(imports.router, prefix="/imports", tags=["データ取込"])
router.include_router(inventory.router, prefix="/inventory", tags=["在庫移動"])
router.include_router(variances.router, prefix="/costs/variance", tags=["差異分析"])
router.include_router(ai.router, prefix="/ai", tags=["AIアシスタント"])
router.include_router(reconciliation.router, prefix="/reconciliation", tags=["突合チェック"])
