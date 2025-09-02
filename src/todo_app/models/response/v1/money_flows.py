from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Kind = Literal["expense", "income"]


# GETレスポンスを定義
class GetMoneyFlowResponseItem(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind


# POSTレスポンスを定義
class CreateMoneyFlowResponse(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind


# PUTレスポンスを定義
class UpdateMoneyFlowResponse(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind
