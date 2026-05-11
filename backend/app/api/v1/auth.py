from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.database import SessionLocal
from app.db.models.user import User 
from app.db.models.jwt_token import JWTToken
from app.db.models.user_session import UserSession 

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "gene_graph_secret_key_2026" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    confirmPassword: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def create_user_auth_data(db: Session, user: User, device_info: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode({"sub": user.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    
    
    new_token = JWTToken(
        user_id=user.id,
        token=encoded_jwt,
        expires_at=expire,
        device_info=device_info
    )
    
    
    new_session = UserSession(
        user_id=user.id,
        session_token=encoded_jwt,
        device_type=device_info,
        last_activity=datetime.utcnow()
    )
    
    db.add(new_token)
    db.add(new_session)
    db.commit()
    return encoded_jwt

# --- Endpoints ---

@router.post("/register")
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    new_user = User(
        email=user_data.email,
        password_hash=pwd_context.hash(user_data.password),
        full_name=user_data.fullName,
        role="doctor"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_user_auth_data(db, new_user, "Web Browser (Register)")

    return {
        "status": "success",
        "token": token,
        "user": {"id": new_user.id, "fullName": new_user.full_name, "email": new_user.email}
    }

@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not pwd_context.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_user_auth_data(db, user, "Web Browser (Login)")

    return {
        "status": "success",
        "token": token,
        "user": {"id": user.id, "fullName": user.full_name, "email": user.email}
    }


@router.post("/logout")
async def logout(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=400, detail="No token provided")
    
    
    token = authorization.replace("Bearer ", "")
    
    
    db.query(JWTToken).filter(JWTToken.token == token).delete()
    db.query(UserSession).filter(UserSession.session_token == token).delete()
    db.commit()
    
    return {"status": "success", "message": "Logged out successfully. Token revoked."}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
       
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    
    db_token = db.query(JWTToken).filter(JWTToken.token == token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Token revoked. Please login again.")

    return user 

# # from fastapi import APIRouter, HTTPException, status
# # from pydantic import BaseModel, EmailStr
# # from typing import Optional

# # router = APIRouter(prefix="/auth", tags=["Authentication"])

# # # --- Models (Data Validation) ---

# # class RegisterRequest(BaseModel):
# #     fullName: str
# #     email: EmailStr  # بيتأكد إن الصيغة إيميل حقيقي
# #     password: str
# #     confirmPassword: Optional[str] = None # اختياري للباك إند

# # class LoginRequest(BaseModel):
# #     email: EmailStr
# #     password: str

# # # --- Endpoints ---

# # @router.post("/register")
# # async def register(user_data: RegisterRequest):
# #     # في المستقبل هنا بنشيك لو الإيميل موجود في الداتابيز
# #     # if email_exists(user_data.email):
# #     #     raise HTTPException(status_code=400, detail="Email already registered")

# #     return {
# #         "status": "success",
# #         "token": "fake-jwt-token-for-registration",
# #         "user": {
# #             "name": user_data.fullName,
# #             "email": user_data.email
# #         }
# #     }

# # @router.post("/login")
# # async def login(credentials: LoginRequest):
# #     # هنا بنشيك على الباسورد والإيميل من الداتابيز
# #     # حالياً بنعمل محاكاة للنجاح (Mock Success)
# #     return {
# #         "status": "success",
# #         "token": "fake-jwt-token-for-login",
# #         "user": {
# #             "name": "Dr. Jane Smith", # ده هيرجع من الداتابيز فعلياً لاحقاً
# #             "email": credentials.email
# #         }
# #     } 
# from fastapi import APIRouter, HTTPException, status, Depends
# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from sqlalchemy.orm import Session
# from passlib.context import CryptContext

# # استيراد ملفات الداتابيز والموديلز بتاعتك
# from app.core.database import SessionLocal
# from app.db.models.user import User 

# router = APIRouter(prefix="/auth", tags=["Authentication"])

# # 1. إعداد نظام تشفير الباسورد (Bcrypt)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # 2. وظيفة الحصول على جلسة الداتابيز
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # --- Models (Pydantic للتحقق من البيانات القادمة من الفرونت) ---

# class RegisterRequest(BaseModel):
#     fullName: str
#     email: EmailStr
#     password: str

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# # --- Endpoints ---

# @router.post("/register")
# async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
#     # أ. التأكد إن الإيميل مش موجود قبل كدة في الداتابيز
#     existing_user = db.query(User).filter(User.email == user_data.email).first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="الإيميل مسجل بالفعل، حاول تسجيل الدخول"
#         )

#     # ب. تشفير الباسورد (عشان لو حد اخترق الداتا ما يشوفش الباسوردات)
#     hashed_password = pwd_context.hash(user_data.password)

#     # ج. إنشاء كائن المستخدم الجديد وربطه بالموديل
#     new_user = User(
#         email=user_data.email,
#         password_hash=hashed_password,
#         full_name=user_data.fullName,
#         role="doctor", # القيمة الافتراضية
#         is_active=True
#     )

#     # د. الحفظ الفعلي في PostgreSQL
#     try:
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="حدث خطأ أثناء حفظ البيانات")

#     return {
#         "status": "success",
#         "message": "تم إنشاء الحساب بنجاح",
#         "user": {
#             "id": new_user.id,
#             "email": new_user.email,
#             "fullName": new_user.full_name
#         }
#     }

# @router.post("/login")
# async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
#     # أ. البحث عن المستخدم في الداتابيز عن طريق الإيميل
#     user = db.query(User).filter(User.email == credentials.email).first()

#     # ب. التأكد من وجود المستخدم ومقارنة الباسورد المشفرة باللي اليوزر كتبها
#     if not user or not pwd_context.verify(credentials.password, user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="الإيميل أو كلمة المرور غير صحيحة"
#         )

#     # ج. لو البيانات صحيحة
#     return {
#         "status": "success",
#         "message": "تم تسجيل الدخول بنجاح",
#         "token": "fake-jwt-token", # مؤقتاً لحد ما نفعل الـ JWT
#         "user": {
#             "id": user.id,
#             "fullName": user.full_name,
#             "email": user.email
#         }
#     }

