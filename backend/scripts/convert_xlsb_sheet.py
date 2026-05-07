"""xlsb の指定シートを openpyxl 互換の xlsx に変換する。

inventory_import.py / inventory_movement_import.py は openpyxl ベースで、
.xlsb (Excel Binary Workbook) を直接開けない。第38期原価計算v8.xlsb 等の
.xlsb 元データを取り込むためにこのスクリプトでシート単位で変換する。

使い方:
  python -m scripts.convert_xlsb_sheet \\
      --src 'docs/reference/第38期原価計算v8(最終))_260225.xlsb' \\
      --sheet '4.3期末全在庫' \\
      --dst /tmp/4_3_期末全在庫.xlsx

依存:
  pip install pyxlsb  (pyxlsb は backend/pyproject.toml には含まれない)
"""
import argparse
from pathlib import Path

from openpyxl import Workbook
from pyxlsb import open_workbook


def convert_sheet(src: str, sheet_name: str, dst: str) -> int:
    """src(.xlsb)の sheet_name を読み取り、dst(.xlsx) として保存。返り値=書き込み行数。"""
    wb_out = Workbook()
    ws = wb_out.active
    ws.title = sheet_name[:31]  # Excelシート名は31文字制限

    rows_written = 0
    with open_workbook(src) as wb_in:
        with wb_in.get_sheet(sheet_name) as sheet:
            for row in sheet.rows():
                ws.append([c.v for c in row])
                rows_written += 1

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    wb_out.save(dst)
    return rows_written


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--src', required=True, help='元xlsbファイルパス')
    parser.add_argument('--sheet', required=True, help='変換対象シート名')
    parser.add_argument('--dst', required=True, help='出力xlsxファイルパス')
    args = parser.parse_args()

    n = convert_sheet(args.src, args.sheet, args.dst)
    print(f"変換完了: {args.src} [{args.sheet}] → {args.dst} ({n}行)")


if __name__ == '__main__':
    main()
