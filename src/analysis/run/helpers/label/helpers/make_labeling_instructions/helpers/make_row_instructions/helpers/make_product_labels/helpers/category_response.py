from pydantic import BaseModel
from analysis.config import ExpenseCategory

class CategoryResponse(BaseModel):
    category: ExpenseCategory