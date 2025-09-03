from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Kind = Literal["expense", "income"]

# ✴︎DB側で制約を設けるよりも、以下APIのリクエスト・レスポンスで制約を設ける方が一般的（こちらでmax_lengthなど指定可能）


# 同じ内容のため、BaseModelを継承した共通の親クラスを作成
class MoneyFlowBase(BaseModel):
    id: int
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind


# GETレスポンスを定義
class GetMoneyFlowResponseItem(MoneyFlowBase):
    pass  # MoneyFlowBaseのフィールドのみ


# POSTレスポンスを定義
class CreateMoneyFlowResponse(MoneyFlowBase):
    pass


# PUTレスポンスを定義
class UpdateMoneyFlowResponse(MoneyFlowBase):
    pass
