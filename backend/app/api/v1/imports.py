"""Data Import API — ファイルアップロードとバッチ管理。"""

import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.audit import ImportBatch
from app.schemas.import_batch import ImportBatchRead, ImportErrorRead, ImportUploadResponse
from app.services.data_import import SOURCE_MAPPINGS, process_import

router = APIRouter()


@router.post("/upload", response_model=ImportUploadResponse)
async def upload_import_file(
    file: UploadFile,
    source_system: str = Form(...),
    period_id: uuid.UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """ファイルをアップロードし、実際原価データをインポートする。"""
    if source_system not in SOURCE_MAPPINGS:
        valid = ", ".join(SOURCE_MAPPINGS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"無効なソースシステム '{source_system}'。有効値: {valid}",
        )

    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が指定されていません")

    expected_type = SOURCE_MAPPINGS[source_system]["file_type"]
    if expected_type == "csv" and not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSVファイルをアップロードしてください")
    if expected_type == "xlsx" and not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Excelファイル (.xlsx) をアップロードしてください")

    content = await file.read()

    batch = await process_import(
        db=db,
        file_content=content,
        filename=file.filename,
        source_system=source_system,
        period_id=period_id,
    )

    errors = [
        ImportErrorRead.model_validate(e) for e in batch.errors
    ]

    if batch.error_rows > 0 and batch.success_rows > 0:
        message = f"{batch.success_rows}件成功、{batch.error_rows}件エラー"
    elif batch.error_rows > 0:
        message = f"インポート失敗: {batch.error_rows}件のエラー"
    else:
        message = f"{batch.success_rows}件のデータを正常にインポートしました"

    return ImportUploadResponse(
        batch_id=batch.id,
        status=batch.status,
        total_rows=batch.total_rows,
        success_rows=batch.success_rows,
        error_rows=batch.error_rows,
        errors=errors,
        message=message,
    )


@router.get("", response_model=list[ImportBatchRead])
async def list_import_batches(
    source_system: str | None = None,
    period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """インポートバッチ一覧を取得する。"""
    query = select(ImportBatch)
    if source_system:
        query = query.where(ImportBatch.source_system == source_system)
    if period_id:
        query = query.where(ImportBatch.period_id == period_id)
    query = query.order_by(ImportBatch.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{batch_id}", response_model=ImportBatchRead)
async def get_import_batch(batch_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """インポートバッチ詳細を取得する（エラー一覧含む）。"""
    result = await db.execute(
        select(ImportBatch).where(ImportBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="インポートバッチが見つかりません")
    return batch
