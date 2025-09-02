from datetime import datetime
from typing import Literal

from pydantic import BaseModel

# "expense" か "income"のどちらかに限定される
Kind = Literal["expense", "income"]


# POSTリクエストを定義
class CreateMoneyFlowRequest(BaseModel):
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind = "expense"  # 送信側がkindを省略したら自動で"expense"が入る（＝支出扱い）


# PUTリクエストを定義
class UpdateMoneyFlowRequest(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind = "expense"


# DELETEリクエストを定義
class DeleteMoneyFlowRequest(BaseModel):
    id: int
