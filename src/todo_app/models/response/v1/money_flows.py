from datetime import datetime

from pydantic import BaseModel


# GETリクエストで返す形式を定義
class GetMoneyFlowResponseItem(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime

# POSTリクエストで返す形式を定義
class CreateMoneyFlowResponse(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime

# PUTリクエストで返す形式を定義
class UpdateMoneyFlowResponse(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime
