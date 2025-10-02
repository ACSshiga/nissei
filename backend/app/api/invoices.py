from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from supabase import Client
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid
from datetime import date, datetime
from decimal import Decimal
import io
import csv
import re
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.auth import get_current_user, require_admin
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoicePreviewResponse,
    InvoicePreviewItem,
)

router = APIRouter()


def validate_month_format(month: str) -> tuple[str, str]:
    """
    月パラメータを検証し、開始日と終了日を返す

    Args:
        month: YYYY-MM形式の文字列

    Returns:
        tuple[str, str]: (start_date, end_date) in YYYY-MM-DD format

    Raises:
        HTTPException: 不正な月形式の場合
    """
    if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', month):
        raise HTTPException(
            status_code=400,
            detail="月はYYYY-MM形式で指定してください（例: 2025-10）"
        )

    try:
        month_date = datetime.strptime(month, "%Y-%m")
        start_date = month_date.strftime("%Y-%m-01")

        # 次月の1日を計算
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1)
        end_date = next_month.strftime("%Y-%m-01")

        return start_date, end_date
    except ValueError as e:
        logger.error(f"Invalid month parameter: {month}, error: {e}")
        raise HTTPException(status_code=400, detail="不正な月形式です")


@router.get("/preview", response_model=InvoicePreviewResponse)
def preview_invoice(
    month: str = Query(..., description="YYYY-MM形式の月"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """指定月の請求書プレビュー（worklogsから実工数を集計）"""
    try:
        # 月パラメータを検証
        start_date, end_date = validate_month_format(month)

        # worklogsから指定月の工数を取得（プロジェクト別に集計）
        worklogs_response = db.table("worklogs").select("""
            project_id,
            duration_minutes
        """).gte("work_date", start_date).lt("work_date", end_date).execute()

        if not worklogs_response.data:
            return InvoicePreviewResponse(
                month=month,
                total_hours=Decimal("0.00"),
                items=[]
            )

        # プロジェクトIDごとに工数を集計
        project_hours = {}
        for log in worklogs_response.data:
            project_id = log["project_id"]
            minutes = log["duration_minutes"]
            if project_id not in project_hours:
                project_hours[project_id] = 0
            project_hours[project_id] += minutes

        # プロジェクト情報を取得（N+1問題対策：バッチクエリ）
        project_ids = list(project_hours.keys())
        if not project_ids:
            return InvoicePreviewResponse(
                month=month,
                total_hours=Decimal("0.00"),
                items=[]
            )

        # in_()で一括取得
        projects_response = db.table("projects").select(
            "id, management_no, machine_no"
        ).in_("id", project_ids).execute()

        projects_data = projects_response.data or []

        if not projects_data:
            return InvoicePreviewResponse(
                month=month,
                total_hours=Decimal("0.00"),
                items=[]
            )

        # 請求書明細を作成
        items = []
        total_minutes = 0

        for project in projects_data:
            project_id = project["id"]
            minutes = project_hours.get(project_id, 0)
            hours = Decimal(minutes) / Decimal(60)

            # 管理No.と号機No.を取得
            management_no = project.get("management_no", "")
            machine_no = project.get("machine_no", "")

            items.append(InvoicePreviewItem(
                management_no=management_no,
                machine_no=machine_no,
                actual_hours=hours.quantize(Decimal("0.01"))
            ))
            total_minutes += minutes

        total_hours = (Decimal(total_minutes) / Decimal(60)).quantize(Decimal("0.01"))

        # 管理Noでソート
        items.sort(key=lambda x: x.management_no)

        return InvoicePreviewResponse(
            month=month,
            total_hours=total_hours,
            items=items
        )

    except Exception as e:
        logger.error(f"Invoice preview failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="請求プレビューの取得に失敗しました"
        )


@router.post("/close", response_model=InvoiceResponse)
def close_invoice(
    month: str = Query(..., description="YYYY-MM形式の月"),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """請求書を確定（管理者のみ）"""
    try:
        # 月パラメータを検証
        validate_month_format(month)

        # プレビューデータを取得
        preview = preview_invoice(month=month, current_user=current_user, db=db)

        if not preview.items:
            raise HTTPException(status_code=400, detail="請求対象の工数がありません")

        # 請求書番号を生成（INV-YYYYMM-001形式）
        year_month = month.replace('-', '')

        # 同月の既存請求書を確認（SQLインジェクション対策：範囲検索を使用）
        existing_response = db.table("invoices").select("invoice_number") \
            .gte("invoice_number", f"INV-{year_month}-001") \
            .lte("invoice_number", f"INV-{year_month}-999").execute()

        seq = 1
        if existing_response.data:
            # 最大番号を取得
            max_num = 0
            for inv in existing_response.data:
                num_str = inv["invoice_number"].split('-')[-1]
                try:
                    num = int(num_str)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
            seq = max_num + 1

        invoice_number = f"INV-{year_month}-{seq:03d}"

        # 請求書明細データを準備（JSONB形式）
        items_jsonb = []
        for idx, item in enumerate(preview.items):
            items_jsonb.append({
                "management_no": item.management_no,
                "machine_no": item.machine_no,
                "actual_hours": str(item.actual_hours),  # Decimal精度保持のため文字列化
                "sort_order": idx,
            })

        # ストアドプロシージャを使用してトランザクション保証
        result = db.rpc(
            "create_invoice_with_items",
            {
                "p_invoice_number": invoice_number,
                "p_issue_date": str(date.today()),
                "p_total_amount": str(preview.total_hours),  # Decimal精度保持
                "p_status": "sent",
                "p_items": items_jsonb
            }
        ).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="請求書の作成に失敗しました")

        invoice_id = result.data

        # 作成した請求書を取得（明細含む）
        return get_invoice(invoice_id=UUID(invoice_id), current_user=current_user, db=db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invoice creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="請求書の作成に失敗しました"
        )


@router.get("/export")
def export_invoice_csv(
    month: str = Query(..., description="YYYY-MM形式の月"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """請求書CSVエクスポート"""
    # 月パラメータを検証
    validate_month_format(month)

    # プレビューデータを取得
    preview = preview_invoice(month=month, current_user=current_user, db=db)

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
            item.machine_no,
            f"{item.actual_hours}H"
        ])

    # StreamingResponseで返す
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode('utf-8-sig')]),  # BOM付きUTF-8
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{month}.csv"
        }
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """請求書詳細を取得"""
    # 請求書を取得
    invoice_response = db.table("invoices").select("*").eq("id", str(invoice_id)).execute()

    if not invoice_response.data:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")

    invoice = invoice_response.data[0]

    # 明細を取得
    items_response = db.table("invoice_items").select("*").eq(
        "invoice_id", str(invoice_id)
    ).order("sort_order").execute()

    invoice["items"] = items_response.data or []

    return invoice


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    status: Optional[str] = Query(None, description="ステータスフィルタ"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """請求書一覧を取得"""
    query = db.table("invoices").select("*")

    if status:
        query = query.eq("status", status)

    query = query.order("issue_date", desc=True)

    invoices_response = query.execute()

    if not invoices_response.data:
        return []

    # 各請求書の明細を取得
    for invoice in invoices_response.data:
        items_response = db.table("invoice_items").select("*").eq(
            "invoice_id", invoice["id"]
        ).order("sort_order").execute()
        invoice["items"] = items_response.data or []

    return invoices_response.data


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Client = Depends(get_db),
):
    """請求書を更新（管理者のみ、ステータス変更のみ）"""
    # 既存の請求書を確認
    existing = db.table("invoices").select("*").eq("id", str(invoice_id)).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")

    # 更新
    update_dict = invoice_data.model_dump(exclude_unset=True, mode="json")
    update_dict["updated_at"] = datetime.utcnow().isoformat()

    updated_response = db.table("invoices").update(update_dict).eq("id", str(invoice_id)).execute()

    if not updated_response.data:
        raise HTTPException(status_code=500, detail="請求書の更新に失敗しました")

    return get_invoice(invoice_id=invoice_id, current_user=current_user, db=db)


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

    # 削除（invoice_itemsも自動削除される）
    db.table("invoices").delete().eq("id", str(invoice_id)).execute()

    return {"message": "請求書を削除しました"}
