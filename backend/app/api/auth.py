from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from datetime import timedelta
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from app.schemas.auth import UserCreate, UserResponse, Token, LoginRequest
from typing import Optional, Dict, Any
from uuid import UUID
import uuid

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db)
) -> Dict[str, Any]:
    """現在のユーザーを取得"""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Supabase Clientでユーザーを取得
    response = db.table("users").select("*").eq("id", user_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return response.data[0]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Client = Depends(get_db)):
    """新規ユーザー登録"""
    # メールアドレスの重複チェック
    existing_email = db.table("users").select("id").eq("email", user_data.email).execute()
    if existing_email.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています"
        )

    # ユーザー名の重複チェック
    existing_username = db.table("users").select("id").eq("username", user_data.username).execute()
    if existing_username.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています"
        )

    # パスワードのハッシュ化
    hashed_password = get_password_hash(user_data.password)

    # ユーザー作成
    new_user_data = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_admin": False
    }

    response = db.table("users").insert(new_user_data).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー登録に失敗しました"
        )

    return response.data[0]


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Client = Depends(get_db)):
    """ログイン"""
    # ユーザーを検索
    response = db.table("users").select("*").eq("email", login_data.email).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = response.data[0]

    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています"
        )

    # アクセストークンを生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "is_admin": user.get("is_admin", False)
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user