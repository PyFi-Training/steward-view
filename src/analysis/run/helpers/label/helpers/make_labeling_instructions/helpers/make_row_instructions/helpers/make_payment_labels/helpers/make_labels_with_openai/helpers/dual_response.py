from pydantic import BaseModel
from analysis.config import ExpenseCategory

class DualResponse(BaseModel):
    vendor: str
    category: ExpenseCategory