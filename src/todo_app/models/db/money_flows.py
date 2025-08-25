from datetime import datetime

from sqlalchemy import DateTime, Integer, String

# SQLAlchemy 2.0形式（最新）の書き方　Mapped：カラムになるものであることを示す　mapped_column：カラムの条件を指定するもの
from sqlalchemy.orm import Mapped, mapped_column

from todo_app.logic.calculate.calculate_datetime import get_now
from todo_app.models.db.base import Base


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
