from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict
from bson import ObjectId
import os
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-12345678')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error for {request.url}: {exc}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Pydantic Models ==========

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    currency: Optional[str] = "USD"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    name: str
    email: str
    currency: str
    
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    currency: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict

class IncomeCreate(BaseModel):
    source: str
    amount: float
    date: str
    notes: Optional[str] = ""

class IncomeResponse(BaseModel):
    id: str
    source: str
    amount: float
    date: str
    notes: str
    created_at: str

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: str
    notes: Optional[str] = ""

class ExpenseResponse(BaseModel):
    id: str
    amount: float
    category: str
    date: str
    notes: str
    created_at: str

class BudgetCreate(BaseModel):
    category: str
    limit: float
    period: str = "monthly"

class BudgetResponse(BaseModel):
    id: str
    category: str
    limit: float
    period: str
    spent: float = 0.0

class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    remaining_balance: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float

class CategoryBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float
    budget_limit: Optional[float] = None
    over_budget: bool = False

# ========== Helper Functions ==========

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        user["id"] = str(user["_id"])
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

# ========== Authentication Routes ==========

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    logger.info(f"Registration attempt for email: {user_data.email}")
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        logger.warning(f"Email already registered: {user_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "currency": user_data.currency,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.users.insert_one(user)
    user["id"] = str(result.inserted_id)
    user.pop("password")
    user.pop("_id", None)
    
    access_token = create_access_token(data={"sub": user_data.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    user["id"] = str(user["_id"])
    user.pop("password")
    user.pop("_id", None)
    
    access_token = create_access_token(data={"sub": user_data.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# ========== Profile Routes ==========

@api_router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "name": current_user.get("name", ""),
        "email": current_user.get("email", ""),
        "currency": current_user.get("currency", "USD")
    }

@api_router.put("/profile")
async def update_profile(profile_data: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {}
    if profile_data.name:
        update_data["name"] = profile_data.name
    if profile_data.currency:
        update_data["currency"] = profile_data.currency
    
    if update_data:
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_data}
        )
    
    # Get updated user
    user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    user["id"] = str(user["_id"])
    user.pop("password")
    user.pop("_id", None)
    
    return {"message": "Profile updated successfully", "user": user}

# ========== Income Routes ==========

@api_router.post("/income", response_model=IncomeResponse)
async def create_income(income: IncomeCreate, current_user: dict = Depends(get_current_user)):
    income_data = {
        "user_id": str(current_user["id"]),
        "source": income.source,
        "amount": income.amount,
        "date": income.date,
        "notes": income.notes,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.income.insert_one(income_data)
    income_data["id"] = str(result.inserted_id)
    income_data.pop("_id", None)
    income_data.pop("user_id")
    
    return income_data

@api_router.get("/income", response_model=List[IncomeResponse])
async def get_income(current_user: dict = Depends(get_current_user)):
    income_list = await db.income.find({"user_id": current_user["id"]}).sort("date", -1).to_list(1000)
    return [serialize_doc(inc) for inc in income_list if inc.get("user_id") == current_user["id"]]

@api_router.delete("/income/{income_id}")
async def delete_income(income_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.income.delete_one({"_id": ObjectId(income_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted successfully"}

# ========== Expense Routes ==========

@api_router.post("/expenses", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    expense_data = {
        "user_id": str(current_user["id"]),
        "amount": expense.amount,
        "category": expense.category,
        "date": expense.date,
        "notes": expense.notes,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.expenses.insert_one(expense_data)
    expense_data["id"] = str(result.inserted_id)
    expense_data.pop("_id", None)
    expense_data.pop("user_id")
    
    return expense_data

@api_router.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(current_user: dict = Depends(get_current_user)):
    expenses_list = await db.expenses.find({"user_id": current_user["id"]}).sort("date", -1).to_list(1000)
    return [serialize_doc(exp) for exp in expenses_list if exp.get("user_id") == current_user["id"]]

@api_router.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.expenses.delete_one({"_id": ObjectId(expense_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

# ========== Budget Routes ==========

@api_router.post("/budget", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, current_user: dict = Depends(get_current_user)):
    # Check if budget already exists for this category
    existing = await db.budgets.find_one({"user_id": current_user["id"], "category": budget.category})
    
    if existing:
        # Update existing budget
        await db.budgets.update_one(
            {"_id": existing["_id"]},
            {"$set": {"limit": budget.limit, "period": budget.period}}
        )
        existing["limit"] = budget.limit
        existing["period"] = budget.period
        return serialize_doc(existing)
    
    budget_data = {
        "user_id": str(current_user["id"]),
        "category": budget.category,
        "limit": budget.limit,
        "period": budget.period,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.budgets.insert_one(budget_data)
    budget_data["id"] = str(result.inserted_id)
    budget_data.pop("_id", None)
    budget_data.pop("user_id")
    budget_data["spent"] = 0.0
    
    return budget_data

@api_router.get("/budget", response_model=List[BudgetResponse])
async def get_budgets(current_user: dict = Depends(get_current_user)):
    budgets_list = await db.budgets.find({"user_id": current_user["id"]}).to_list(1000)
    expenses_list = await db.expenses.find({"user_id": current_user["id"]}).to_list(1000)
    
    # Calculate spent amount per category
    category_spending = {}
    for exp in expenses_list:
        category = exp.get("category", "Other")
        category_spending[category] = category_spending.get(category, 0) + exp.get("amount", 0)
    
    result = []
    for budget in budgets_list:
        budget_dict = serialize_doc(budget)
        budget_dict["spent"] = category_spending.get(budget.get("category", ""), 0)
        result.append(budget_dict)
    
    return result

@api_router.delete("/budget/{budget_id}")
async def delete_budget(budget_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.budgets.delete_one({"_id": ObjectId(budget_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted successfully"}

# ========== Analytics Routes ==========

@api_router.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(current_user: dict = Depends(get_current_user)):
    # Get all income and expenses
    income_list = await db.income.find({"user_id": current_user["id"]}).to_list(1000)
    expenses_list = await db.expenses.find({"user_id": current_user["id"]}).to_list(1000)
    
    total_income = sum(inc.get("amount", 0) for inc in income_list)
    total_expenses = sum(exp.get("amount", 0) for exp in expenses_list)
    
    # Calculate monthly totals (current month)
    now = datetime.utcnow()
    current_month = now.strftime("%Y-%m")
    
    monthly_income = sum(inc.get("amount", 0) for inc in income_list if inc.get("date", "").startswith(current_month))
    monthly_expenses = sum(exp.get("amount", 0) for exp in expenses_list if exp.get("date", "").startswith(current_month))
    
    remaining_balance = total_income - total_expenses
    savings_rate = (monthly_income - monthly_expenses) / monthly_income * 100 if monthly_income > 0 else 0
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "remaining_balance": remaining_balance,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "savings_rate": round(savings_rate, 2)
    }

@api_router.get("/analytics/category-breakdown", response_model=List[CategoryBreakdown])
async def get_category_breakdown(current_user: dict = Depends(get_current_user)):
    expenses_list = await db.expenses.find({"user_id": current_user["id"]}).to_list(1000)
    budgets_list = await db.budgets.find({"user_id": current_user["id"]}).to_list(1000)
    
    # Calculate spending by category
    category_spending = {}
    for exp in expenses_list:
        category = exp.get("category", "Other")
        category_spending[category] = category_spending.get(category, 0) + exp.get("amount", 0)
    
    # Get budget limits
    budget_limits = {b.get("category"): b.get("limit") for b in budgets_list}
    
    # Calculate totals
    total_expenses = sum(category_spending.values())
    
    result = []
    for category, amount in category_spending.items():
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        budget_limit = budget_limits.get(category)
        over_budget = budget_limit is not None and amount > budget_limit
        
        result.append({
            "category": category,
            "amount": amount,
            "percentage": round(percentage, 2),
            "budget_limit": budget_limit,
            "over_budget": over_budget
        })
    
    # Sort by amount descending
    result.sort(key=lambda x: x["amount"], reverse=True)
    
    return result

@api_router.get("/analytics/monthly-trend")
async def get_monthly_trend(current_user: dict = Depends(get_current_user)):
    expenses_list = await db.expenses.find({"user_id": current_user["id"]}).to_list(1000)
    income_list = await db.income.find({"user_id": current_user["id"]}).to_list(1000)
    
    # Group by month
    monthly_data = {}
    
    for exp in expenses_list:
        month = exp.get("date", "")[:7]  # YYYY-MM
        if month not in monthly_data:
            monthly_data[month] = {"income": 0, "expenses": 0}
        monthly_data[month]["expenses"] += exp.get("amount", 0)
    
    for inc in income_list:
        month = inc.get("date", "")[:7]
        if month not in monthly_data:
            monthly_data[month] = {"income": 0, "expenses": 0}
        monthly_data[month]["income"] += inc.get("amount", 0)
    
    # Convert to list and sort
    result = [{"month": k, **v} for k, v in monthly_data.items()]
    result.sort(key=lambda x: x["month"])
    
    return result

@api_router.get("/")
async def root():
    return {"message": "Smart Expense Manager API", "status": "running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
