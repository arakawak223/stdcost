"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Package,
  Beaker,
  Building2,
  FlaskConical,
  Truck,
  Calendar,
  TrendingUp,
  Calculator,
  Upload,
  FileText,
  ListTree,
  SplitSquareVertical,
  Wallet,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "ダッシュボード", href: "/", icon: LayoutDashboard },
  { name: "製品マスタ", href: "/products", icon: Package },
  { name: "原体マスタ", href: "/crude-products", icon: Beaker },
  { name: "部門マスタ", href: "/cost-centers", icon: Building2 },
  { name: "原材料マスタ", href: "/materials", icon: FlaskConical },
  { name: "外注先マスタ", href: "/contractors", icon: Truck },
  { name: "会計期間", href: "/fiscal-periods", icon: Calendar },
];

const costNavigation = [
  { name: "BOM管理", href: "/bom", icon: ListTree },
  { name: "配賦ルール", href: "/allocation-rules", icon: SplitSquareVertical },
  { name: "予算管理", href: "/cost-budgets", icon: Wallet },
  { name: "標準原価計算", href: "/standard-costs", icon: Calculator },
];

const futureNavigation = [
  { name: "差異分析", href: "#", icon: TrendingUp, disabled: true },
  { name: "データ取込", href: "#", icon: Upload, disabled: true },
  { name: "監査ログ", href: "#", icon: FileText, disabled: true },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r bg-card">
        <div className="flex h-16 items-center border-b px-6">
          <h1 className="text-lg font-bold text-primary">StdCost</h1>
          <span className="ml-2 text-xs text-muted-foreground">標準原価計算</span>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          <div className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            マスタ管理
          </div>
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
          <div className="mb-2 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            原価計算
          </div>
          {costNavigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
          <div className="mb-2 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            分析・処理（Phase 3+）
          </div>
          {futureNavigation.map((item) => (
            <span
              key={item.name}
              className="flex cursor-not-allowed items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground/50"
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </span>
          ))}
        </nav>
        <div className="border-t p-4">
          <p className="text-xs text-muted-foreground">Phase 2 - BOM・標準原価エンジン</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
