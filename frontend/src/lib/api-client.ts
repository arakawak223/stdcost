const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }

  return res.json();
}

// Products
export type ProductType =
  | "semi_finished"
  | "in_house_product_dept"
  | "in_house_manufacturing"
  | "outsourced_in_house"
  | "outsourced"
  | "special"
  | "produce";

export interface Product {
  id: string;
  code: string;
  name: string;
  name_short: string | null;
  product_group: string | null;
  product_type: ProductType;
  sc_code: string | null;
  content_weight_g: string | null;
  product_symbol: string | null;
  gram_unit_price: string | null;
  unit: string;
  standard_lot_size: string;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  code: string;
  name: string;
  name_short?: string | null;
  product_group?: string | null;
  product_type?: ProductType;
  sc_code?: string | null;
  content_weight_g?: string | null;
  product_symbol?: string | null;
  unit?: string;
  standard_lot_size?: string;
  notes?: string | null;
}

export interface ProductUpdate {
  name?: string;
  name_short?: string | null;
  product_group?: string | null;
  product_type?: ProductType;
  sc_code?: string | null;
  content_weight_g?: string | null;
  product_symbol?: string | null;
  gram_unit_price?: string | null;
  unit?: string;
  standard_lot_size?: string;
  is_active?: boolean;
  notes?: string | null;
}

export const productsApi = {
  list: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    product_group?: string;
    product_type?: string;
    is_active?: boolean;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.per_page) searchParams.set("per_page", String(params.per_page));
    if (params?.search) searchParams.set("search", params.search);
    if (params?.product_group) searchParams.set("product_group", params.product_group);
    if (params?.product_type) searchParams.set("product_type", params.product_type);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<Product[]>(`/masters/products${qs ? `?${qs}` : ""}`);
  },
  count: (params?: { search?: string; product_group?: string; product_type?: string; is_active?: boolean }) => {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.set("search", params.search);
    if (params?.product_group) searchParams.set("product_group", params.product_group);
    if (params?.product_type) searchParams.set("product_type", params.product_type);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<{ count: number }>(`/masters/products/count${qs ? `?${qs}` : ""}`);
  },
  groups: () => fetchApi<string[]>("/masters/products/groups"),
  get: (id: string) => fetchApi<Product>(`/masters/products/${id}`),
  create: (data: ProductCreate) =>
    fetchApi<Product>("/masters/products", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: ProductUpdate) =>
    fetchApi<Product>(`/masters/products/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/products/${id}`, { method: "DELETE" }),
};

// Crude Products (原体/原液)
export type CrudeProductType = "R" | "HI" | "G" | "SP" | "GN" | "other";

export interface CrudeProduct {
  id: string;
  code: string;
  name: string;
  vintage_year: number | null;
  crude_type: CrudeProductType;
  aging_years: number | null;
  is_blend: boolean;
  blend_source_ids: string | null;
  unit: string;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CrudeProductCreate {
  code: string;
  name: string;
  vintage_year?: number | null;
  crude_type: CrudeProductType;
  aging_years?: number | null;
  is_blend?: boolean;
  unit?: string;
  notes?: string | null;
}

export interface CrudeProductUpdate {
  name?: string;
  vintage_year?: number | null;
  crude_type?: CrudeProductType;
  aging_years?: number | null;
  is_blend?: boolean;
  unit?: string;
  is_active?: boolean;
  notes?: string | null;
}

export const crudeProductsApi = {
  list: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    crude_type?: string;
    vintage_year?: number;
    is_active?: boolean;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.per_page) searchParams.set("per_page", String(params.per_page));
    if (params?.search) searchParams.set("search", params.search);
    if (params?.crude_type) searchParams.set("crude_type", params.crude_type);
    if (params?.vintage_year) searchParams.set("vintage_year", String(params.vintage_year));
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<CrudeProduct[]>(`/masters/crude-products${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<CrudeProduct>(`/masters/crude-products/${id}`),
  create: (data: CrudeProductCreate) =>
    fetchApi<CrudeProduct>("/masters/crude-products", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: CrudeProductUpdate) =>
    fetchApi<CrudeProduct>(`/masters/crude-products/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/crude-products/${id}`, { method: "DELETE" }),
};

// Cost Centers
export interface CostCenter {
  id: string;
  code: string;
  name: string;
  name_short: string | null;
  center_type: "manufacturing" | "product" | "indirect";
  parent_id: string | null;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export const costCentersApi = {
  list: (params?: { center_type?: string; is_active?: boolean }) => {
    const searchParams = new URLSearchParams();
    if (params?.center_type) searchParams.set("center_type", params.center_type);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<CostCenter[]>(`/masters/cost-centers${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<CostCenter>(`/masters/cost-centers/${id}`),
  create: (data: Omit<CostCenter, "id" | "created_at" | "updated_at">) =>
    fetchApi<CostCenter>("/masters/cost-centers", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<CostCenter>) =>
    fetchApi<CostCenter>(`/masters/cost-centers/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/cost-centers/${id}`, { method: "DELETE" }),
};

// Materials
export type MaterialCategory = "fruit" | "vegetable" | "grain" | "seaweed" | "other";

export interface Material {
  id: string;
  code: string;
  name: string;
  material_type: "raw" | "packaging" | "sub_material";
  category: MaterialCategory | null;
  unit: string;
  standard_unit_price: string;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export const materialsApi = {
  list: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    material_type?: string;
    category?: string;
    is_active?: boolean;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.per_page) searchParams.set("per_page", String(params.per_page));
    if (params?.search) searchParams.set("search", params.search);
    if (params?.material_type) searchParams.set("material_type", params.material_type);
    if (params?.category) searchParams.set("category", params.category);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<Material[]>(`/masters/materials${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<Material>(`/masters/materials/${id}`),
  create: (data: Omit<Material, "id" | "created_at" | "updated_at">) =>
    fetchApi<Material>("/masters/materials", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Material>) =>
    fetchApi<Material>(`/masters/materials/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/materials/${id}`, { method: "DELETE" }),
};

// Contractors (外注先)
export interface Contractor {
  id: string;
  code: string;
  name: string;
  name_short: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export const contractorsApi = {
  list: (params?: { search?: string; is_active?: boolean }) => {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.set("search", params.search);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<Contractor[]>(`/masters/contractors${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<Contractor>(`/masters/contractors/${id}`),
  create: (data: Omit<Contractor, "id" | "created_at" | "updated_at">) =>
    fetchApi<Contractor>("/masters/contractors", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Contractor>) =>
    fetchApi<Contractor>(`/masters/contractors/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/contractors/${id}`, { method: "DELETE" }),
};

// Fiscal Periods
export interface FiscalPeriod {
  id: string;
  year: number;
  month: number;
  start_date: string;
  end_date: string;
  status: "open" | "closing" | "closed";
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export const fiscalPeriodsApi = {
  list: (params?: { year?: number; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.year) searchParams.set("year", String(params.year));
    if (params?.status) searchParams.set("status", params.status);
    const qs = searchParams.toString();
    return fetchApi<FiscalPeriod[]>(`/masters/fiscal-periods${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<FiscalPeriod>(`/masters/fiscal-periods/${id}`),
  create: (data: Omit<FiscalPeriod, "id" | "created_at" | "updated_at">) =>
    fetchApi<FiscalPeriod>("/masters/fiscal-periods", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: { status?: string; notes?: string }) =>
    fetchApi<FiscalPeriod>(`/masters/fiscal-periods/${id}`, { method: "PUT", body: JSON.stringify(data) }),
};

// BOM (Bill of Materials)
export type BomType = "raw_material_process" | "product_process";

export interface BomLine {
  id: string;
  material_id: string | null;
  crude_product_id: string | null;
  quantity: string;
  unit: string;
  loss_rate: string;
  sort_order: number;
  notes: string | null;
  material: Material | null;
  crude_product: CrudeProduct | null;
}

export interface BomLineCreate {
  material_id?: string | null;
  crude_product_id?: string | null;
  quantity: string;
  unit: string;
  loss_rate?: string;
  sort_order?: number;
  notes?: string | null;
}

export interface BomHeader {
  id: string;
  product_id: string | null;
  crude_product_id: string | null;
  bom_type: BomType;
  effective_date: string;
  version: number;
  yield_rate: string;
  is_active: boolean;
  notes: string | null;
  lines: BomLine[];
  product: Product | null;
  crude_product_detail: CrudeProduct | null;
  created_at: string;
  updated_at: string;
}

export interface BomHeaderCreate {
  product_id?: string | null;
  crude_product_id?: string | null;
  bom_type: BomType;
  effective_date: string;
  version?: number;
  yield_rate?: string;
  is_active?: boolean;
  notes?: string | null;
  lines: BomLineCreate[];
}

export interface BomHeaderUpdate {
  product_id?: string | null;
  crude_product_id?: string | null;
  bom_type?: BomType;
  effective_date?: string;
  version?: number;
  yield_rate?: string;
  is_active?: boolean;
  notes?: string | null;
  lines?: BomLineCreate[];
}

export const bomApi = {
  list: (params?: {
    product_id?: string;
    crude_product_id?: string;
    bom_type?: string;
    is_active?: boolean;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.product_id) searchParams.set("product_id", params.product_id);
    if (params?.crude_product_id) searchParams.set("crude_product_id", params.crude_product_id);
    if (params?.bom_type) searchParams.set("bom_type", params.bom_type);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<BomHeader[]>(`/masters/bom${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<BomHeader>(`/masters/bom/${id}`),
  create: (data: BomHeaderCreate) =>
    fetchApi<BomHeader>("/masters/bom", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: BomHeaderUpdate) =>
    fetchApi<BomHeader>(`/masters/bom/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/bom/${id}`, { method: "DELETE" }),
};

// Allocation Rules
export type AllocationBasis =
  | "production_hours"
  | "raw_material_quantity"
  | "crude_quantity"
  | "weight_based"
  | "manual";

export interface AllocationRuleTarget {
  id: string;
  target_cost_center_id: string;
  ratio: string;
  target_cost_center: CostCenter | null;
}

export interface AllocationRule {
  id: string;
  name: string;
  source_cost_center_id: string;
  cost_element: string | null;
  basis: AllocationBasis;
  priority: number;
  is_active: boolean;
  notes: string | null;
  targets: AllocationRuleTarget[];
  source_cost_center: CostCenter | null;
  created_at: string;
  updated_at: string;
}

export interface AllocationRuleCreate {
  name: string;
  source_cost_center_id: string;
  cost_element?: string | null;
  basis?: AllocationBasis;
  priority?: number;
  is_active?: boolean;
  notes?: string | null;
  targets: { target_cost_center_id: string; ratio: string }[];
}

export const allocationRulesApi = {
  list: (params?: { is_active?: boolean }) => {
    const searchParams = new URLSearchParams();
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    const qs = searchParams.toString();
    return fetchApi<AllocationRule[]>(`/masters/allocation-rules${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<AllocationRule>(`/masters/allocation-rules/${id}`),
  create: (data: AllocationRuleCreate) =>
    fetchApi<AllocationRule>("/masters/allocation-rules", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<AllocationRuleCreate>) =>
    fetchApi<AllocationRule>(`/masters/allocation-rules/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/allocation-rules/${id}`, { method: "DELETE" }),
};

// Cost Budgets
export interface CostBudget {
  id: string;
  cost_center_id: string;
  period_id: string;
  labor_budget: string;
  overhead_budget: string;
  outsourcing_budget: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CostBudgetCreate {
  cost_center_id: string;
  period_id: string;
  labor_budget?: string;
  overhead_budget?: string;
  outsourcing_budget?: string;
  notes?: string | null;
}

export const costBudgetsApi = {
  list: (params?: { cost_center_id?: string; period_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.cost_center_id) searchParams.set("cost_center_id", params.cost_center_id);
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    const qs = searchParams.toString();
    return fetchApi<CostBudget[]>(`/masters/cost-budgets${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<CostBudget>(`/masters/cost-budgets/${id}`),
  create: (data: CostBudgetCreate) =>
    fetchApi<CostBudget>("/masters/cost-budgets", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<CostBudgetCreate>) =>
    fetchApi<CostBudget>(`/masters/cost-budgets/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) =>
    fetchApi<{ message: string }>(`/masters/cost-budgets/${id}`, { method: "DELETE" }),
};

// Standard Costs
export interface CrudeProductStandardCost {
  id: string;
  crude_product_id: string;
  period_id: string;
  material_cost: string;
  labor_cost: string;
  overhead_cost: string;
  prior_process_cost: string;
  total_cost: string;
  unit_cost: string;
  standard_quantity: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface StandardCost {
  id: string;
  product_id: string;
  period_id: string;
  crude_product_cost: string;
  packaging_cost: string;
  labor_cost: string;
  overhead_cost: string;
  outsourcing_cost: string;
  total_cost: string;
  unit_cost: string;
  lot_size: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CalculationResult {
  period_id: string;
  crude_products_calculated: number;
  products_calculated: number;
  total_crude_product_cost: string;
  total_product_cost: string;
  crude_product_costs: CrudeProductStandardCost[];
  product_costs: StandardCost[];
}

export const standardCostsApi = {
  calculate: (data: { period_id: string; product_ids?: string[]; simulate?: boolean }) =>
    fetchApi<CalculationResult>("/costs/standard/calculate", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  simulate: (data: { period_id: string; overrides?: Record<string, unknown> }) =>
    fetchApi<CalculationResult>("/costs/standard/simulate", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  list: (params?: { period_id?: string; product_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    if (params?.product_id) searchParams.set("product_id", params.product_id);
    const qs = searchParams.toString();
    return fetchApi<StandardCost[]>(`/costs/standard${qs ? `?${qs}` : ""}`);
  },
  listCrudeProducts: (params?: { period_id?: string; crude_product_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    if (params?.crude_product_id) searchParams.set("crude_product_id", params.crude_product_id);
    const qs = searchParams.toString();
    return fetchApi<CrudeProductStandardCost[]>(`/costs/standard/crude-products${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<StandardCost>(`/costs/standard/${id}`),
};

// Actual Costs
export type SourceSystem =
  | "geneki_db"
  | "sc_system"
  | "kanjyo_bugyo"
  | "tsuhan21"
  | "romu_db"
  | "product_db"
  | "manual";

export type CostElement =
  | "material"
  | "crude_product"
  | "packaging"
  | "labor"
  | "overhead"
  | "outsourcing"
  | "prior_process";

export interface ActualCost {
  id: string;
  product_id: string;
  cost_center_id: string;
  period_id: string;
  crude_product_cost: string;
  packaging_cost: string;
  labor_cost: string;
  overhead_cost: string;
  outsourcing_cost: string;
  total_cost: string;
  quantity_produced: string;
  source_system: SourceSystem;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CrudeProductActualCost {
  id: string;
  crude_product_id: string;
  period_id: string;
  material_cost: string;
  labor_cost: string;
  overhead_cost: string;
  prior_process_cost: string;
  total_cost: string;
  actual_quantity: string;
  source_system: SourceSystem;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export const actualCostsApi = {
  list: (params?: { period_id?: string; product_id?: string; cost_center_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    if (params?.product_id) searchParams.set("product_id", params.product_id);
    if (params?.cost_center_id) searchParams.set("cost_center_id", params.cost_center_id);
    const qs = searchParams.toString();
    return fetchApi<ActualCost[]>(`/costs/actual${qs ? `?${qs}` : ""}`);
  },
  listCrudeProducts: (params?: { period_id?: string; crude_product_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    if (params?.crude_product_id) searchParams.set("crude_product_id", params.crude_product_id);
    const qs = searchParams.toString();
    return fetchApi<CrudeProductActualCost[]>(`/costs/actual/crude-products${qs ? `?${qs}` : ""}`);
  },
};

// Variance Analysis
export type VarianceType = "price" | "quantity" | "efficiency" | "mix" | "volume";

export interface VarianceRecord {
  id: string;
  product_id: string;
  cost_center_id: string | null;
  period_id: string;
  variance_type: VarianceType;
  cost_element: string;
  standard_amount: string;
  actual_amount: string;
  variance_amount: string;
  variance_percent: string;
  is_favorable: boolean;
  is_flagged: boolean;
  flag_reason: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CostElementVariance {
  cost_element: string;
  standard_amount: string;
  actual_amount: string;
  variance_amount: string;
  variance_percent: string;
  is_favorable: boolean;
}

export interface ProductVarianceDetail {
  product_id: string;
  product_code: string;
  product_name: string;
  cost_center_id: string | null;
  cost_center_name: string | null;
  total_standard: string;
  total_actual: string;
  total_variance: string;
  total_variance_percent: string;
  is_favorable: boolean;
  elements: CostElementVariance[];
}

export interface VarianceAnalysisResult {
  period_id: string;
  products_analyzed: number;
  records_created: number;
  flagged_count: number;
  total_standard: string;
  total_actual: string;
  total_variance: string;
  details: ProductVarianceDetail[];
}

export interface VarianceSummaryItem {
  cost_element: string;
  total_standard: string;
  total_actual: string;
  total_variance: string;
  average_variance_percent: string;
  favorable_count: number;
  unfavorable_count: number;
  flagged_count: number;
}

export interface VarianceSummaryReport {
  period_id: string;
  total_products: number;
  total_records: number;
  total_flagged: number;
  overall_standard: string;
  overall_actual: string;
  overall_variance: string;
  by_element: VarianceSummaryItem[];
}

export const varianceApi = {
  analyze: (data: { period_id: string; product_ids?: string[]; threshold_percent?: number }) =>
    fetchApi<VarianceAnalysisResult>("/costs/variance/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  summary: (period_id: string) =>
    fetchApi<VarianceSummaryReport>(`/costs/variance/summary?period_id=${period_id}`),
  list: (params?: {
    period_id?: string;
    product_id?: string;
    cost_element?: string;
    is_flagged?: boolean;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    if (params?.product_id) searchParams.set("product_id", params.product_id);
    if (params?.cost_element) searchParams.set("cost_element", params.cost_element);
    if (params?.is_flagged !== undefined) searchParams.set("is_flagged", String(params.is_flagged));
    const qs = searchParams.toString();
    return fetchApi<VarianceRecord[]>(`/costs/variance${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<VarianceRecord>(`/costs/variance/${id}`),
  update: (id: string, data: { is_flagged?: boolean; flag_reason?: string; notes?: string }) =>
    fetchApi<VarianceRecord>(`/costs/variance/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// Imports
export type ImportStatus = "pending" | "processing" | "completed" | "failed";

export interface ImportError {
  id: string;
  row_number: number;
  column_name: string | null;
  error_message: string;
  raw_data: Record<string, unknown> | null;
}

export interface ImportBatch {
  id: string;
  file_name: string;
  source_system: string;
  status: ImportStatus;
  total_rows: number;
  success_rows: number;
  error_rows: number;
  period_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
  errors: ImportError[];
  created_at: string;
  updated_at: string;
}

export interface ImportUploadResponse {
  batch_id: string;
  status: ImportStatus;
  total_rows: number;
  success_rows: number;
  error_rows: number;
  errors: ImportError[];
  message: string;
}

async function fetchApiMultipart<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, options);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

export const importsApi = {
  upload: (data: { file: File; source_system: string; period_id: string }) => {
    const formData = new FormData();
    formData.append("file", data.file);
    formData.append("source_system", data.source_system);
    formData.append("period_id", data.period_id);
    return fetchApiMultipart<ImportUploadResponse>("/imports/upload", {
      method: "POST",
      body: formData,
    });
  },
  list: (params?: { source_system?: string; period_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.source_system) searchParams.set("source_system", params.source_system);
    if (params?.period_id) searchParams.set("period_id", params.period_id);
    const qs = searchParams.toString();
    return fetchApi<ImportBatch[]>(`/imports${qs ? `?${qs}` : ""}`);
  },
  get: (id: string) => fetchApi<ImportBatch>(`/imports/${id}`),
};

// AI Explanations (Phase 5)
export type ReviewStatus = "pending" | "approved" | "rejected";

export interface AIExplanation {
  id: string;
  context_type: string;
  context_id: string | null;
  prompt: string;
  response: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  review_status: ReviewStatus;
  reviewer_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AIExplanationResponse {
  explanation: AIExplanation;
  message: string;
}

export const aiApi = {
  explainVariance: (variance_record_id: string) =>
    fetchApi<AIExplanationResponse>("/ai/explain/variance", {
      method: "POST",
      body: JSON.stringify({ variance_record_id }),
    }),
  explainPeriod: (period_id: string) =>
    fetchApi<AIExplanationResponse>("/ai/explain/period", {
      method: "POST",
      body: JSON.stringify({ period_id }),
    }),
  ask: (data: { question: string; context_type?: string; context_id?: string }) =>
    fetchApi<AIExplanationResponse>("/ai/ask", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  listExplanations: (params?: { context_type?: string; review_status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.context_type) searchParams.set("context_type", params.context_type);
    if (params?.review_status) searchParams.set("review_status", params.review_status);
    const qs = searchParams.toString();
    return fetchApi<AIExplanation[]>(`/ai/explanations${qs ? `?${qs}` : ""}`);
  },
  getExplanation: (id: string) => fetchApi<AIExplanation>(`/ai/explanations/${id}`),
  updateExplanation: (id: string, data: { review_status?: ReviewStatus; reviewer_notes?: string }) =>
    fetchApi<AIExplanation>(`/ai/explanations/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};
