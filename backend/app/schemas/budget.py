from pydantic import BaseModel, ConfigDict

class BudgetCreate(BaseModel):
    amount : float
    month  : int
    year   : int
    category_id : int


class BudgetResponse(BaseModel):
    id : int
    amount :float
    month :int
    year : int
    category_id : int

    model_config = ConfigDict(from_attributes= True)