from datetime import datetime

# PythonのEnum機能を使うためのインポート
from enum import Enum as PyEnum

# SQLAlchemyのEnum機能を使うためのインポート
from sqlalchemy import DateTime, Enum, Index, Integer, String

# SQLAlchemy 2.0形式（最新）の書き方　Mapped：カラムになるものであることを示す　mapped_column：カラムの条件を指定するもの
from sqlalchemy.orm import Mapped, mapped_column

from todo_app.logic.calculate.calculate_datetime import get_now
from todo_app.models.db.base import Base


# Python側のEnum定義
class MoneyFlowKind(PyEnum):
    EXPENSE = "expense"  # 支出
    INCOME = "income"  # 収入


class MoneyFlows(Base):
    __tablename__ = "money_flows"

    # SQLAlchemy 1.x スタイル（旧）の書き方
    # id = Column(Integer, primary_key=True, autoincrement=True)
    # title = Column(String(30), nullable=False)
    # amount = Column(Integer, nullable=False)
    # occurred_date = Column(DateTime, nullable=False)
    # created_at = Column(DateTime, default=get_now)
    # updated_at = Column(DateTime, default=get_now, onupdate=get_now)

    # SQLAlchemy 2.0形式（最新）の書き方
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_now, onupdate=get_now)

    # Enum型のカラム定義（追加）
    kind: Mapped[MoneyFlowKind] = mapped_column(
        Enum(
            MoneyFlowKind, name="money_flow_kind"
        ),  # DBの列の型にSQLAlchemyのEnumを使う（中身はPythonのMoneyFlowKindを渡す。name="money_flow_kind"はDB側の型名）
        nullable=False,  # NULLを禁止（必ず"expense"か"income"が入る）
        default=MoneyFlowKind.EXPENSE,  # アプリ側のデフォルト。Pythonで新規オブジェクトを作って、session.add()→commit()する時、もしkindを指定しなかったらSQLAlchemyが自動でEXPENSEを入れる
        server_default=MoneyFlowKind.EXPENSE.value,  # DB側のデフォルト。APIを通さずSQLで直接INSERTする場合でも、DBが"expense"を自動で入れてくれる
        index=True,  # 索引を張る指定。WHERE kind='income' のような絞り込み検索が速くなる
    )


# 発生月や収支で絞り込めるようにする。
# Index(...)：インデックスを作る関数。
# ix_money_flows_occurred_kind：インデックス名（慣例でix_から始める）
# MoneyFlows.occurred_date, MoneyFlows.kind：どの列をキーにするかの指定
Index("ix_money_flows_occurred_kind", MoneyFlows.occurred_date, MoneyFlows.kind)
