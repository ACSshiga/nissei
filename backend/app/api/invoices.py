from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from supabase import Client
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import io
import csv
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.auth import get_current_user, require_admin
from app.schemas.invoice import (
    Invoice,
    InvoicePreview,
    InvoiceItem,
)

router = APIRouter()

# 定数定義
INVOICE_STATUS_DRAFT = "draft"
INVOICE_STATUS_CLOSED = "closed"


@router.get("/preview", response_model=InvoicePreview)
def preview_invoice(
    year: int = Query(..., description="年"),
    month: int = Query(..., ge=1, le=12, description="月"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """指定月の請求書プレビュー（worklogsから実工数を集計）"""
    try:
        # 月範囲の計算
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        # worklogsから指定月の工数を取得（プロジェクト別に集計）
        worklogs_response = db.table("work_logs").select(
            "project_id, duration_minutes"
        ).gte("work_date", start_date).lt("work_date", end_date).execute()

        # プロジェクトIDごとに工数を集計
        project_hours = {}
        if worklogs_response.data:
            for log in worklogs_response.data:
                project_id = log["project_id"]
                minutes = log.get("duration_minutes", 0)
                if project_id not in project_hours:
                    project_hours[project_id] = 0
                project_hours[project_id] += minutes

        # プロジェクト情報を取得
        items = []
        if project_hours:
            project_ids = list(project_hours.keys())
            projects_response = db.table("projects").select(
                "id, management_no, machine_no"
            ).in_("id", project_ids).execute()

            if projects_response.data:
                for project in projects_response.data:
                    project_id = project["id"]
                    minutes = project_hours.get(project_id, 0)
                    hours = Decimal(minutes) / Decimal(60)

                    items.append(InvoiceItem(
                        id=UUID("00000000-0000-0000-0000-000000000000"),  # プレビュー用ダミー
                        invoice_id=UUID("00000000-0000-0000-0000-000000000000"),  # プレビュー用ダミー
                        project_id=UUID(project_id),
                        management_no=project.get("management_no", ""),
                        work_content=project.get("machine_no", ""),
                        total_hours=hours.quantize(Decimal("0.01")),
                        created_at=datetime.utcnow()
                    ))

        # 管理Noでソート
        items.sort(key=lambda x: x.management_no)

        # 既存の請求書を確認
        existing_invoice = db.table("invoices").select("*").eq(
            "year", year
        ).eq("month", month).execute()

        if existing_invoice.data:
            invoice = existing_invoice.data[0]
            return InvoicePreview(
                id=UUID(invoice["id"]),
                year=invoice["year"],
                month=invoice["month"],
                status=invoice["status"],
                closed_at=invoice.get("closed_at"),
                closed_by=UUID(invoice["closed_by"]) if invoice.get("closed_by") else None,
                created_at=datetime.fromisoformat(invoice["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(invoice["updated_at"].replace("Z", "+00:00")),
                items=items
            )
        else:
            # 新規プレビュー
            return InvoicePreview(
                id=UUID("00000000-0000-0000-0000-000000000000"),
                year=year,
                month=month,
                status=INVOICE_STATUS_DRAFT,
                closed_at=None,
                closed_by=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                items=items
            )

    except Exception as e:
        logger.error(f"Invoice preview failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="請求プレビューの取得に失敗しました"
        )


@router.post("/close", response_model=Invoice)
def close_invoice(
    year: int = Query(..., description="年"),
    month: int = Query(..., ge=1, le=12, description="月"),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """請求書を確定（管理者のみ）"""
    invoice_id = None
    is_new_invoice = False

    try:
        # プレビューデータを取得
        preview = preview_invoice(year=year, month=month, current_user=current_user, db=db)

        if not preview.items:
            raise HTTPException(status_code=400, detail="請求対象の工数がありません")

        # 既存の請求書を確認
        existing = db.table("invoices").select("*").eq(
            "year", year
        ).eq("month", month).execute()

        if existing.data:
            invoice_id = existing.data[0]["id"]
            # 確定済みの場合はエラー
            if existing.data[0]["status"] == INVOICE_STATUS_CLOSED:
                raise HTTPException(status_code=400, detail="既に確定済みの請求書です")

            # ステータスを確定に更新
            update_data = {
                "status": INVOICE_STATUS_CLOSED,
                "closed_at": datetime.utcnow().isoformat(),
                "closed_by": str(current_user["id"]),
                "updated_at": datetime.utcnow().isoformat()
            }
            db.table("invoices").update(update_data).eq("id", invoice_id).execute()

            # 既存の明細を削除
            db.table("invoice_items").delete().eq("invoice_id", invoice_id).execute()
        else:
            # 新規請求書を作成
            invoice_data = {
                "year": year,
                "month": month,
                "status": INVOICE_STATUS_CLOSED,
                "closed_at": datetime.utcnow().isoformat(),
                "closed_by": str(current_user["id"])
            }
            invoice_response = db.table("invoices").insert(invoice_data).execute()

            if not invoice_response.data:
                raise HTTPException(status_code=500, detail="請求書の作成に失敗しました")

            invoice_id = invoice_response.data[0]["id"]
            is_new_invoice = True

        # 明細を一括登録（N+1クエリ回避）
        items_data = [
            {
                "invoice_id": invoice_id,
                "project_id": str(item.project_id),
                "management_no": item.management_no,
                "work_content": item.work_content,
                "total_hours": float(item.total_hours)
            }
            for item in preview.items
        ]

        if items_data:
            db.table("invoice_items").insert(items_data).execute()

        # 確定した請求書を取得
        result = db.table("invoices").select("*").eq("id", invoice_id).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="請求書の取得に失敗しました")

        invoice = result.data[0]
        return Invoice(
            id=UUID(invoice["id"]),
            year=invoice["year"],
            month=invoice["month"],
            status=invoice["status"],
            closed_at=datetime.fromisoformat(invoice["closed_at"].replace("Z", "+00:00")) if invoice.get("closed_at") else None,
            closed_by=UUID(invoice["closed_by"]) if invoice.get("closed_by") else None,
            created_at=datetime.fromisoformat(invoice["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(invoice["updated_at"].replace("Z", "+00:00"))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invoice close failed: {e}", exc_info=True)
        # エラー時のロールバック相当処理（新規作成の場合のみ削除）
        if is_new_invoice and invoice_id:
            try:
                db.table("invoice_items").delete().eq("invoice_id", invoice_id).execute()
                db.table("invoices").delete().eq("id", invoice_id).execute()
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}", exc_info=True)

        raise HTTPException(
            status_code=500,
            detail="請求書の確定に失敗しました"
        )


@router.get("/export")
def export_invoice_csv(
    year: int = Query(..., description="年"),
    month: int = Query(..., ge=1, le=12, description="月"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """請求書CSVエクスポート"""
    # プレビューデータを取得
    preview = preview_invoice(year=year, month=month, current_user=current_user, db=db)

    if not preview.items:
        raise HTTPException(status_code=404, detail="請求対象の工数がありません")

    # CSV作成
    output = io.StringIO()
    writer = csv.writer(output)

    # ヘッダー
    writer.writerow(['管理No', '委託業務内容', '実工数'])

    # データ行
    for item in preview.items:
        writer.writerow([
            item.management_no,
            item.work_content,
            f"{item.total_hours}"
        ])

    # StreamingResponseで返す
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode('utf-8-sig')]),  # BOM付きUTF-8
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{year}-{month:02d}.csv"
        }
    )


@router.get("", response_model=List[Invoice])
def list_invoices(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """請求書一覧を取得"""
    invoices_response = db.table("invoices").select("*").order(
        "year", desc=True
    ).order("month", desc=True).execute()

    if not invoices_response.data:
        return []

    invoices = []
    for invoice in invoices_response.data:
        invoices.append(Invoice(
            id=UUID(invoice["id"]),
            year=invoice["year"],
            month=invoice["month"],
            status=invoice["status"],
            closed_at=datetime.fromisoformat(invoice["closed_at"].replace("Z", "+00:00")) if invoice.get("closed_at") else None,
            closed_by=UUID(invoice["closed_by"]) if invoice.get("closed_by") else None,
            created_at=datetime.fromisoformat(invoice["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(invoice["updated_at"].replace("Z", "+00:00"))
        ))

    return invoices


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: UUID,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """請求書を削除（管理者のみ、CASCADE）"""
    # 既存の請求書を確認
    existing = db.table("invoices").select("*").eq("id", str(invoice_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")

    # 明細を削除
    db.table("invoice_items").delete().eq("invoice_id", str(invoice_id)).execute()

    # 請求書を削除
    db.table("invoices").delete().eq("id", str(invoice_id)).execute()

    return {"message": "請求書を削除しました"}
