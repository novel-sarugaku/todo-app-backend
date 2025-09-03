from datetime import datetime
from typing import Literal

from pydantic import BaseModel

# "expense" か "income"のどちらかに限定される
Kind = Literal["expense", "income"]

# ✴︎DB側で制約を設けるよりも、以下APIのリクエスト・レスポンスで制約を設ける方が一般的（こちらでmax_lengthなど指定可能）


# 同じ内容のため、BaseModelを継承した共通の親クラスを作成
class MoneyFlowBase(BaseModel):
    title: str
    amount: int
    occurred_date: datetime
    kind: Kind = "expense"  # 今回特別：開発効率を上げるため、自動で"expense"が入るよう設定（＝支出扱い）。バグの発見が遅れる要因となるため、本来初期値の設定は非推奨


# POSTリクエストを定義
class CreateMoneyFlowRequest(MoneyFlowBase):
    pass  # MoneyFlowBaseのフィールドのみ


# PUTリクエストを定義
class UpdateMoneyFlowRequest(MoneyFlowBase):
    id: int  # MoneyFlowBaseのフィールド + idを追加


# DELETEリクエストを定義
class DeleteMoneyFlowRequest(BaseModel):
    id: int
