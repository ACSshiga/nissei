from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from supabase import Client
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid
from datetime import datetime
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.material import (
    MaterialCreate,
    MaterialResponse,
    MaterialSearchParams,
)

router = APIRouter()


@router.post("/upload", response_model=MaterialResponse)
async def upload_material(
    file: UploadFile = File(...),
    title: str = Query(..., description="資料タイトル"),
    scope: str = Query(..., description="スコープレベル: machine, model, tonnage, series"),
    series: str = Query(..., description="シリーズ名（NEX, HMX等）"),
    machine_no: Optional[str] = Query(None, description="特定機番（scope=machineの場合）"),
    model: Optional[str] = Query(None, description="特定機種（scope=modelの場合）"),
    tonnage: Optional[int] = Query(None, description="トン数（scope=tonnageの場合）"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """資料アップロード"""
    try:
        # スコープバリデーション
        valid_scopes = ["machine", "model", "tonnage", "series"]
        if scope not in valid_scopes:
            raise HTTPException(
                status_code=400,
                detail=f"スコープは {', '.join(valid_scopes)} のいずれかを指定してください"
            )

        # スコープごとの必須パラメータチェック
        if scope == "machine" and not machine_no:
            raise HTTPException(status_code=400, detail="scope=machineの場合、machine_noは必須です")
        if scope == "model" and not model:
            raise HTTPException(status_code=400, detail="scope=modelの場合、modelは必須です")
        if scope == "tonnage" and not tonnage:
            raise HTTPException(status_code=400, detail="scope=tonnageの場合、tonnageは必須です")

        # ファイル保存（実際の運用ではMinIOやS3を使用）
        upload_dir = Path("./uploads/materials")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = f"materials/{file_id}{file_extension}"
        full_path = upload_dir / f"{file_id}{file_extension}"

        # ファイル書き込み
        content = await file.read()
        with open(full_path, "wb") as f:
            f.write(content)

        file_size = len(content)

        # DBに登録
        material_data = {
            "title": title,
            "machine_no": machine_no,
            "model": model,
            "scope": scope,
            "series": series,
            "tonnage": tonnage,
            "file_path": file_path,
            "file_size": file_size,
            "uploaded_by": current_user["id"],
        }

        result = db.table("materials").insert(material_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="資料の登録に失敗しました")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Material upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="資料のアップロードに失敗しました"
        )


@router.get("/search", response_model=List[MaterialResponse])
def search_materials(
    machine_no: Optional[str] = Query(None, description="機番で検索"),
    model: Optional[str] = Query(None, description="機種で検索"),
    series: Optional[str] = Query(None, description="シリーズで検索"),
    tonnage: Optional[int] = Query(None, description="トン数で検索"),
    scope: Optional[str] = Query(None, description="スコープで絞り込み"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    資料検索（階層的スコープ検索）

    優先度: machine > model > tonnage > series
    例: machine_no指定時は、そのmachine専用 + model共通 + tonnage共通 + series共通を全て返す
    """
    try:
        # 検索条件を構築
        query = db.table("materials").select("*")

        if scope:
            query = query.eq("scope", scope)

        # 階層検索ロジック
        if machine_no:
            # machine_no指定時: machine専用 OR (model一致 AND scope>=model) OR (tonnage一致 AND scope>=tonnage) OR (series一致 AND scope>=series)
            # Supabaseではor条件が複雑なため、複数クエリで取得して結合
            results = []

            # 1. machine専用資料
            machine_results = db.table("materials").select("*") \
                .eq("scope", "machine") \
                .eq("machine_no", machine_no).execute()
            results.extend(machine_results.data or [])

            # 2. model共通資料（machine_noからmodelを推定する必要があるため、projects等から取得）
            # 簡易実装: modelパラメータが指定されている場合のみ
            if model:
                model_results = db.table("materials").select("*") \
                    .eq("scope", "model") \
                    .eq("model", model).execute()
                results.extend(model_results.data or [])

            # 3. tonnage共通資料
            if tonnage:
                tonnage_results = db.table("materials").select("*") \
                    .eq("scope", "tonnage") \
                    .eq("tonnage", tonnage).execute()
                results.extend(tonnage_results.data or [])

            # 4. series共通資料
            if series:
                series_results = db.table("materials").select("*") \
                    .eq("scope", "series") \
                    .eq("series", series).execute()
                results.extend(series_results.data or [])

            # 重複削除（IDでユニーク化）
            unique_results = {item["id"]: item for item in results}.values()
            return list(unique_results)

        elif model:
            # model指定時: model専用 + tonnage共通 + series共通
            results = []

            model_results = db.table("materials").select("*") \
                .eq("scope", "model") \
                .eq("model", model).execute()
            results.extend(model_results.data or [])

            if tonnage:
                tonnage_results = db.table("materials").select("*") \
                    .eq("scope", "tonnage") \
                    .eq("tonnage", tonnage).execute()
                results.extend(tonnage_results.data or [])

            if series:
                series_results = db.table("materials").select("*") \
                    .eq("scope", "series") \
                    .eq("series", series).execute()
                results.extend(series_results.data or [])

            unique_results = {item["id"]: item for item in results}.values()
            return list(unique_results)

        elif tonnage:
            # tonnage指定時: tonnage専用 + series共通
            results = []

            tonnage_results = db.table("materials").select("*") \
                .eq("scope", "tonnage") \
                .eq("tonnage", tonnage).execute()
            results.extend(tonnage_results.data or [])

            if series:
                series_results = db.table("materials").select("*") \
                    .eq("scope", "series") \
                    .eq("series", series).execute()
                results.extend(series_results.data or [])

            unique_results = {item["id"]: item for item in results}.values()
            return list(unique_results)

        elif series:
            # series指定時: series専用のみ
            query = query.eq("series", series)
            result = query.execute()
            return result.data or []

        else:
            # パラメータなしの場合は全件取得
            result = query.order("created_at", desc=True).execute()
            return result.data or []

    except Exception as e:
        logger.error(f"Material search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="資料の検索に失敗しました"
        )


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """資料詳細を取得"""
    result = db.table("materials").select("*").eq("id", str(material_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="資料が見つかりません")

    return result.data[0]


@router.delete("/{material_id}")
def delete_material(
    material_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """資料を削除"""
    # 既存の資料を確認
    existing = db.table("materials").select("*").eq("id", str(material_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="資料が見つかりません")

    material = existing.data[0]

    # アップロードしたユーザーのみ削除可能（または管理者）
    if material["uploaded_by"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="この資料を削除する権限がありません")

    # ファイル削除（実際の運用ではMinIO等から削除）
    try:
        file_path = Path("./uploads") / material["file_path"]
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to delete file {material['file_path']}: {e}")

    # DB削除
    db.table("materials").delete().eq("id", str(material_id)).execute()

    return {"message": "資料を削除しました"}
