from pydantic import BaseModel
from datetime import datetime
class DashboardSummaryResponse(BaseModel):
    total_income : float
    total_expense : float
    net_balance : float

    transaction_count : int
    categories_count : int
    active_budgets : int

class CategoryBreakdownResponse(BaseModel):
    category :str
    amount : float

class MonthlyTrendResponse(BaseModel):
    month : str
    income : float
    expense : float
    savings : float

class BudgetStatusResponse(BaseModel):
    category: str
    budget: float
    spent: float
    remaining: float
    percentage: float
    status: str
    month: str
    year : str

class RecentTransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    description: str | None
    created_at: datetime