from datetime import datetime

from pydantic import BaseModel


# POSTリクエストを定義
class CreateMoneyFlowRequest(BaseModel):
    title: str
    amount: int
    occurred_date: datetime

# PUTリクエストを定義
class UpdateMoneyFlowRequest(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime

# DELETEリクエストを定義
class DeleteMoneyFlowRequest(BaseModel):
    id: int
