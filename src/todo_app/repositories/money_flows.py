from sqlalchemy.orm import Session

from todo_app.models.db.money_flows import MoneyFlows


# データ取得する　.query()：参照するテーブルを指定　.all()：データすべて指定
def get_money_flows_all(session: Session) -> list[MoneyFlows]:
    return session.query(MoneyFlows).all()


def get_money_flow_by_id(session: Session, id: int) -> MoneyFlows:
    return session.query(MoneyFlows).where(MoneyFlows.id == id).first()
