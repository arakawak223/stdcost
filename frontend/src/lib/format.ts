/**
 * Japanese locale formatting utilities for 万田発酵 標準原価計算アプリ.
 */

/** Format number as Japanese Yen (e.g., ¥1,234,567) */
export function formatCurrency(amount: number | string): string {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  return `¥${num.toLocaleString("ja-JP", { maximumFractionDigits: 0 })}`;
}

/** Format number with thousands separator (e.g., 1,234.56) */
export function formatNumber(
  value: number | string,
  decimals: number = 0
): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return num.toLocaleString("ja-JP", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Format date as Japanese style (e.g., 2026年2月26日) */
export function formatJpDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

/** Format fiscal period (e.g., 第38期 第5月) */
export function formatFiscalPeriod(year: number, month: number): string {
  return `第${year}期 第${month}月`;
}

/** Format percentage (e.g., 12.3%) */
export function formatPercent(value: number | string, decimals: number = 1): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return `${num.toFixed(decimals)}%`;
}

/** Format datetime for display (e.g., 2026/02/26 14:30) */
export function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleString("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Period status labels in Japanese */
export const periodStatusLabels: Record<string, string> = {
  open: "オープン",
  closing: "締め処理中",
  closed: "クローズ",
};

/** Cost center type labels */
export const centerTypeLabels: Record<string, string> = {
  manufacturing: "製造部",
  product: "製品課",
  indirect: "間接",
};

/** Material type labels */
export const materialTypeLabels: Record<string, string> = {
  raw: "原料",
  packaging: "資材",
  sub_material: "副資材",
};

/** Material category labels */
export const materialCategoryLabels: Record<string, string> = {
  fruit: "果物",
  vegetable: "野菜",
  grain: "穀物",
  seaweed: "海藻",
  other: "その他",
};

/** Product type labels */
export const productTypeLabels: Record<string, string> = {
  semi_finished: "半製品",
  in_house_product_dept: "内製品(製品課)",
  in_house_manufacturing: "内製品(製造部)",
  outsourced_in_house: "外注内製",
  outsourced: "外注品",
  special: "特殊",
  produce: "産品",
};

/** Crude product type labels */
export const crudeProductTypeLabels: Record<string, string> = {
  R: "レギュラー",
  HI: "HI",
  G: "ゴールド",
  SP: "スペシャル",
  GN: "ジンジャー",
  other: "その他",
};

/** Source system labels */
export const sourceSystemLabels: Record<string, string> = {
  geneki_db: "原液DB",
  sc_system: "SC",
  kanjyo_bugyo: "勘定奉行",
  tsuhan21: "通販21",
  romu_db: "労務DB",
  product_db: "製品管理DB",
  manual: "手動入力",
};

/** Import status labels */
export const importStatusLabels: Record<string, string> = {
  pending: "待機中",
  processing: "処理中",
  completed: "完了",
  failed: "失敗",
};

/** Cost element labels */
export const costElementLabels: Record<string, string> = {
  material: "原材料費",
  crude_product: "原体原価",
  packaging: "資材費",
  labor: "労務費",
  overhead: "経費",
  outsourcing: "外注加工費",
  prior_process: "前工程費",
};

/** Variance type labels */
export const varianceTypeLabels: Record<string, string> = {
  price: "価格差異",
  quantity: "数量差異",
  efficiency: "能率差異",
  mix: "配合差異",
  volume: "操業度差異",
};

/** Review status labels */
export const reviewStatusLabels: Record<string, string> = {
  pending: "レビュー待ち",
  approved: "承認済み",
  rejected: "却下",
};
