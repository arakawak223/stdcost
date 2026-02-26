"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Trash2, Plus } from "lucide-react";
import type { BomLineCreate, Material, CrudeProduct } from "@/lib/api-client";

interface BomLineEditorProps {
  lines: BomLineCreate[];
  onChange: (lines: BomLineCreate[]) => void;
  materials: Material[];
  crudeProducts: CrudeProduct[];
  bomType: "raw_material_process" | "product_process";
}

export function BomLineEditor({
  lines,
  onChange,
  materials,
  crudeProducts,
  bomType,
}: BomLineEditorProps) {
  const addLine = () => {
    onChange([
      ...lines,
      {
        material_id: null,
        crude_product_id: null,
        quantity: "0",
        unit: "kg",
        loss_rate: "0",
        sort_order: lines.length + 1,
      },
    ]);
  };

  const removeLine = (index: number) => {
    onChange(lines.filter((_, i) => i !== index));
  };

  const updateLine = (index: number, field: string, value: string) => {
    const updated = [...lines];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  };

  // For raw_material_process: materials (raw) are inputs
  // For product_process: crude_products and materials (packaging) are inputs
  const rawMaterials = materials.filter((m) => m.material_type === "raw");
  const packagingMaterials = materials.filter((m) => m.material_type === "packaging");

  return (
    <div className="space-y-2">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-8">#</TableHead>
            {bomType === "product_process" && (
              <TableHead>原体</TableHead>
            )}
            <TableHead>
              {bomType === "raw_material_process" ? "原材料" : "資材"}
            </TableHead>
            <TableHead className="w-28">数量</TableHead>
            <TableHead className="w-20">単位</TableHead>
            <TableHead className="w-24">ロス率</TableHead>
            <TableHead className="w-12"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {lines.map((line, index) => (
            <TableRow key={index}>
              <TableCell className="text-muted-foreground">{index + 1}</TableCell>
              {bomType === "product_process" && (
                <TableCell>
                  <select
                    className="w-full rounded border bg-background px-2 py-1 text-sm"
                    value={line.crude_product_id || ""}
                    onChange={(e) => {
                      updateLine(index, "crude_product_id", e.target.value || "");
                      if (e.target.value) updateLine(index, "material_id", "");
                    }}
                  >
                    <option value="">--</option>
                    {crudeProducts.map((cp) => (
                      <option key={cp.id} value={cp.id}>
                        {cp.code} - {cp.name}
                      </option>
                    ))}
                  </select>
                </TableCell>
              )}
              <TableCell>
                <select
                  className="w-full rounded border bg-background px-2 py-1 text-sm"
                  value={line.material_id || ""}
                  onChange={(e) => {
                    updateLine(index, "material_id", e.target.value || "");
                    if (e.target.value && bomType === "product_process") {
                      updateLine(index, "crude_product_id", "");
                    }
                  }}
                >
                  <option value="">--</option>
                  {(bomType === "raw_material_process" ? rawMaterials : packagingMaterials).map(
                    (m) => (
                      <option key={m.id} value={m.id}>
                        {m.code} - {m.name} ({m.unit})
                      </option>
                    )
                  )}
                </select>
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  step="0.000001"
                  value={line.quantity}
                  onChange={(e) => updateLine(index, "quantity", e.target.value)}
                  className="h-8"
                />
              </TableCell>
              <TableCell>
                <Input
                  value={line.unit}
                  onChange={(e) => updateLine(index, "unit", e.target.value)}
                  className="h-8"
                />
              </TableCell>
              <TableCell>
                <Input
                  type="number"
                  step="0.0001"
                  value={line.loss_rate || "0"}
                  onChange={(e) => updateLine(index, "loss_rate", e.target.value)}
                  className="h-8"
                />
              </TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeLine(index)}
                  className="h-8 w-8 p-0 text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Button variant="outline" size="sm" onClick={addLine}>
        <Plus className="mr-1 h-4 w-4" />
        行を追加
      </Button>
    </div>
  );
}
