"""Pydantic v2 schemas for master data."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.master import (
    AllocationBasis,
    BomType,
    CostCenterType,
    CrudeProductType,
    MaterialCategory,
    MaterialType,
    PeriodStatus,
    ProductType,
)


# --- CostCenter ---

class CostCenterBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=100)
    name_short: str | None = Field(default=None, max_length=50)
    center_type: CostCenterType
    parent_id: uuid.UUID | None = None
    is_active: bool = True
    sort_order: int = 0


class CostCenterCreate(CostCenterBase):
    pass


class CostCenterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    name_short: str | None = Field(default=None, max_length=50)
    center_type: CostCenterType | None = None
    parent_id: uuid.UUID | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CostCenterRead(CostCenterBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Material ---

class MaterialBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    material_type: MaterialType
    category: MaterialCategory | None = None
    unit: str = Field(max_length=10)
    standard_unit_price: Decimal = Field(default=Decimal("0"), decimal_places=4)
    is_active: bool = True
    notes: str | None = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    material_type: MaterialType | None = None
    category: MaterialCategory | None = None
    unit: str | None = Field(default=None, max_length=10)
    standard_unit_price: Decimal | None = None
    is_active: bool | None = None
    notes: str | None = None


class MaterialRead(MaterialBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- CrudeProduct (原体/原液) ---

class CrudeProductBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    vintage_year: int | None = None
    crude_type: CrudeProductType
    aging_years: int | None = None
    is_blend: bool = False
    blend_source_ids: str | None = None
    unit: str = Field(default="kg", max_length=10)
    is_active: bool = True
    notes: str | None = None


class CrudeProductCreate(CrudeProductBase):
    pass


class CrudeProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    vintage_year: int | None = None
    crude_type: CrudeProductType | None = None
    aging_years: int | None = None
    is_blend: bool | None = None
    blend_source_ids: str | None = None
    unit: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None
    notes: str | None = None


class CrudeProductRead(CrudeProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Product ---

class ProductBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    name_short: str | None = Field(default=None, max_length=50)
    product_group: str | None = Field(default=None, max_length=50)
    product_type: ProductType = ProductType.in_house_product_dept
    sc_code: str | None = Field(default=None, max_length=30)
    content_weight_g: Decimal | None = None
    product_symbol: str | None = Field(default=None, max_length=20)
    gram_unit_price: Decimal | None = None
    unit: str = Field(default="個", max_length=10)
    standard_lot_size: Decimal = Field(default=Decimal("1"), decimal_places=4)
    is_active: bool = True
    notes: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    name_short: str | None = Field(default=None, max_length=50)
    product_group: str | None = Field(default=None, max_length=50)
    product_type: ProductType | None = None
    sc_code: str | None = Field(default=None, max_length=30)
    content_weight_g: Decimal | None = None
    product_symbol: str | None = Field(default=None, max_length=20)
    gram_unit_price: Decimal | None = None
    unit: str | None = Field(default=None, max_length=10)
    standard_lot_size: Decimal | None = None
    is_active: bool | None = None
    notes: str | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Contractor (外注先) ---

class ContractorBase(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    name_short: str | None = Field(default=None, max_length=50)
    is_active: bool = True
    notes: str | None = None


class ContractorCreate(ContractorBase):
    pass


class ContractorUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    name_short: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    notes: str | None = None


class ContractorRead(ContractorBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- FiscalPeriod ---

class FiscalPeriodBase(BaseModel):
    year: int
    month: int = Field(ge=1, le=12)
    start_date: date
    end_date: date
    status: PeriodStatus = PeriodStatus.open
    notes: str | None = None


class FiscalPeriodCreate(FiscalPeriodBase):
    pass


class FiscalPeriodUpdate(BaseModel):
    status: PeriodStatus | None = None
    notes: str | None = None


class FiscalPeriodRead(FiscalPeriodBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- BOM ---

class BomLineBase(BaseModel):
    material_id: uuid.UUID | None = None
    crude_product_id: uuid.UUID | None = None
    quantity: Decimal
    unit: str = Field(max_length=10)
    loss_rate: Decimal = Field(default=Decimal("0"))
    sort_order: int = 0
    notes: str | None = None


class BomLineCreate(BomLineBase):
    pass


class BomHeaderBase(BaseModel):
    product_id: uuid.UUID | None = None
    crude_product_id: uuid.UUID | None = None
    bom_type: BomType
    effective_date: date
    version: int = 1
    yield_rate: Decimal = Field(default=Decimal("1.0000"))
    is_active: bool = True
    notes: str | None = None


class BomHeaderCreate(BomHeaderBase):
    lines: list[BomLineCreate] = []


class BomHeaderUpdate(BaseModel):
    product_id: uuid.UUID | None = None
    crude_product_id: uuid.UUID | None = None
    bom_type: BomType | None = None
    effective_date: date | None = None
    version: int | None = None
    yield_rate: Decimal | None = None
    is_active: bool | None = None
    notes: str | None = None
    lines: list[BomLineCreate] | None = None


class BomLineRead(BomLineBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    material: MaterialRead | None = None
    crude_product: CrudeProductRead | None = None


class BomHeaderRead(BomHeaderBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    lines: list[BomLineRead] = []
    product: ProductRead | None = None
    crude_product_detail: CrudeProductRead | None = Field(default=None, alias="crude_product")
    created_at: datetime
    updated_at: datetime


# --- AllocationRule ---

class AllocationRuleTargetBase(BaseModel):
    target_cost_center_id: uuid.UUID
    ratio: Decimal


class AllocationRuleTargetCreate(AllocationRuleTargetBase):
    pass


class AllocationRuleTargetRead(AllocationRuleTargetBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    target_cost_center: CostCenterRead | None = None


class AllocationRuleBase(BaseModel):
    name: str = Field(max_length=100)
    source_cost_center_id: uuid.UUID
    basis: AllocationBasis = AllocationBasis.raw_material_quantity
    is_active: bool = True
    notes: str | None = None


class AllocationRuleCreate(AllocationRuleBase):
    targets: list[AllocationRuleTargetCreate] = []


class AllocationRuleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    source_cost_center_id: uuid.UUID | None = None
    basis: AllocationBasis | None = None
    is_active: bool | None = None
    notes: str | None = None
    targets: list[AllocationRuleTargetCreate] | None = None


class AllocationRuleRead(AllocationRuleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    targets: list[AllocationRuleTargetRead] = []
    source_cost_center: CostCenterRead | None = None
    created_at: datetime
    updated_at: datetime


# --- Pagination ---

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    pages: int
