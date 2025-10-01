from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional, Dict, Any
from uuid import UUID
import uuid
from datetime import date

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.worklog import (
    WorkLogCreate,
    WorkLogUpdate,
    WorkLogResponse,
    WorkLogListResponse,
)

router = APIRouter()


@router.post("", response_model=WorkLogResponse, status_code=201)
def create_worklog(
    worklog_data: WorkLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """工数入力を新規作成"""
    # 案件の存在確認
    project_response = db.table("projects").select("id, actual_hours").eq("id", str(worklog_data.project_id)).execute()
    if not project_response.data:
        raise HTTPException(status_code=404, detail="案件が見つかりません")

    project = project_response.data[0]

    # 新規工数入力作成
    # データベースに存在するカラムのみを送信
    worklog_dict = worklog_data.model_dump(mode="json")
    new_worklog = {
        "id": str(uuid.uuid4()),
        "project_id": worklog_dict["project_id"],
        "work_date": worklog_dict["work_date"],
        "duration_minutes": worklog_dict["duration_minutes"],
        "user_id": current_user["id"],
    }
    # オプションフィールドは後でカラムを追加後に有効化
    # "start_time": worklog_dict.get("start_time"),
    # "end_time": worklog_dict.get("end_time"),
    # "work_content": worklog_dict.get("work_content"),

    worklog_response = db.table("worklogs").insert(new_worklog).execute()

    if not worklog_response.data:
        raise HTTPException(
            status_code=500,
            detail="工数入力の作成に失敗しました"
        )

    # 案件の実績工数を更新
    new_actual_hours = (project.get("actual_hours") or 0) + worklog_data.duration_minutes
    db.table("projects").update({"actual_hours": new_actual_hours}).eq("id", str(worklog_data.project_id)).execute()

    return worklog_response.data[0]


@router.get("", response_model=WorkLogListResponse)
def list_worklogs(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    project_id: Optional[UUID] = Query(None, description="案件IDでフィルタ"),
    work_date: Optional[date] = Query(None, description="作業日でフィルタ"),
    user_id: Optional[UUID] = Query(None, description="ユーザーIDでフィルタ"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """工数入力一覧を取得"""
    query = db.table("worklogs").select("*")

    # フィルタリング
    if project_id:
        query = query.eq("project_id", str(project_id))
    if work_date:
        query = query.eq("work_date", work_date.isoformat())
    if user_id:
        query = query.eq("user_id", str(user_id))

    # 総件数取得
    count_query = db.table("worklogs").select("id", count="exact")
    if project_id:
        count_query = count_query.eq("project_id", str(project_id))
    if work_date:
        count_query = count_query.eq("work_date", work_date.isoformat())
    if user_id:
        count_query = count_query.eq("user_id", str(user_id))

    count_response = count_query.execute()
    total = count_response.count if count_response.count is not None else 0

    # ページネーション
    offset = (page - 1) * per_page
    worklogs_response = query.order("work_date", desc=True).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()

    return WorkLogListResponse(
        worklogs=worklogs_response.data,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{worklog_id}", response_model=WorkLogResponse)
def get_worklog(
    worklog_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """工数入力詳細を取得"""
    response = db.table("worklogs").select("*").eq("id", str(worklog_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="工数入力が見つかりません")
    return response.data[0]


@router.put("/{worklog_id}", response_model=WorkLogResponse)
def update_worklog(
    worklog_id: UUID,
    worklog_data: WorkLogUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """工数入力を更新"""
    worklog_response = db.table("worklogs").select("*").eq("id", str(worklog_id)).execute()
    if not worklog_response.data:
        raise HTTPException(status_code=404, detail="工数入力が見つかりません")

    worklog = worklog_response.data[0]
    old_duration = worklog["duration_minutes"]

    # 更新データ（データベースに存在するカラムのみ）
    worklog_dict = worklog_data.model_dump(exclude_unset=True, mode="json")
    update_data = {}
    if "project_id" in worklog_dict:
        update_data["project_id"] = worklog_dict["project_id"]
    if "work_date" in worklog_dict:
        update_data["work_date"] = worklog_dict["work_date"]
    if "duration_minutes" in worklog_dict:
        update_data["duration_minutes"] = worklog_dict["duration_minutes"]
    # オプションフィールドは後でカラムを追加後に有効化
    # if "start_time" in worklog_dict:
    #     update_data["start_time"] = worklog_dict["start_time"]
    # if "end_time" in worklog_dict:
    #     update_data["end_time"] = worklog_dict["end_time"]
    # if "work_content" in worklog_dict:
    #     update_data["work_content"] = worklog_dict["work_content"]

    new_duration = update_data.get("duration_minutes", old_duration)

    # 作業時間が変更される場合、案件の実績工数を調整
    if new_duration != old_duration:
        project_response = db.table("projects").select("actual_hours").eq("id", worklog["project_id"]).execute()
        if project_response.data:
            project = project_response.data[0]
            new_actual_hours = (project.get("actual_hours") or 0) - old_duration + new_duration
            db.table("projects").update({"actual_hours": new_actual_hours}).eq("id", worklog["project_id"]).execute()

    # 更新
    response = db.table("worklogs").update(update_data).eq("id", str(worklog_id)).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="工数入力の更新に失敗しました")

    return response.data[0]


@router.delete("/{worklog_id}", status_code=204)
def delete_worklog(
    worklog_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """工数入力を削除"""
    worklog_response = db.table("worklogs").select("*").eq("id", str(worklog_id)).execute()
    if not worklog_response.data:
        raise HTTPException(status_code=404, detail="工数入力が見つかりません")

    worklog = worklog_response.data[0]

    # 案件の実績工数を減算
    project_response = db.table("projects").select("actual_hours").eq("id", worklog["project_id"]).execute()
    if project_response.data:
        project = project_response.data[0]
        new_actual_hours = (project.get("actual_hours") or 0) - worklog["duration_minutes"]
        db.table("projects").update({"actual_hours": new_actual_hours}).eq("id", worklog["project_id"]).execute()

    # 削除
    db.table("worklogs").delete().eq("id", str(worklog_id)).execute()
    return None


@router.get("/summary/{project_id}")
def get_worklog_summary(
    project_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """案件の工数集計を取得"""
    # 案件の存在確認
    project_response = db.table("projects").select("management_no, estimated_hours, actual_hours").eq("id", str(project_id)).execute()
    if not project_response.data:
        raise HTTPException(status_code=404, detail="案件が見つかりません")

    project = project_response.data[0]

    # 全工数データを取得
    worklogs_response = db.table("worklogs").select("user_id, duration_minutes, work_date").eq("project_id", str(project_id)).execute()
    worklogs = worklogs_response.data

    # ユーザー名を取得
    user_ids = list(set([w["user_id"] for w in worklogs]))
    users_map = {}
    if user_ids:
        users_response = db.table("users").select("id, username").in_("id", user_ids).execute()
        users_map = {u["id"]: u["username"] for u in users_response.data}

    # ユーザー別集計
    user_summary_dict = {}
    for worklog in worklogs:
        user_id = worklog["user_id"]
        if user_id not in user_summary_dict:
            user_summary_dict[user_id] = {
                "username": users_map.get(user_id, "Unknown"),
                "total_minutes": 0,
                "entry_count": 0
            }
        user_summary_dict[user_id]["total_minutes"] += worklog["duration_minutes"]
        user_summary_dict[user_id]["entry_count"] += 1

    user_summary = list(user_summary_dict.values())

    # 日別集計
    daily_summary_dict = {}
    for worklog in worklogs:
        work_date = worklog["work_date"]
        if work_date not in daily_summary_dict:
            daily_summary_dict[work_date] = {
                "work_date": work_date,
                "total_minutes": 0,
                "entry_count": 0
            }
        daily_summary_dict[work_date]["total_minutes"] += worklog["duration_minutes"]
        daily_summary_dict[work_date]["entry_count"] += 1

    daily_summary = sorted(daily_summary_dict.values(), key=lambda x: x["work_date"], reverse=True)

    return {
        "project_id": str(project_id),
        "management_no": project["management_no"],
        "estimated_hours": project.get("estimated_hours") or 0,
        "actual_hours": project.get("actual_hours") or 0,
        "by_user": user_summary,
        "by_date": daily_summary,
    }