from sqlalchemy.orm import Session

from todo_app.models.db.money_flows import MoneyFlowKind, MoneyFlows


# データ取得する　.query()：参照するテーブルを指定　.all()：データすべて指定
def get_money_flows_all(session: Session) -> list[MoneyFlows]:
    return session.query(MoneyFlows).all()


def get_money_flow_by_id(session: Session, id: int) -> MoneyFlows:
    return session.query(MoneyFlows).where(MoneyFlows.id == id).first()


# 種別（income/expense）で絞って、発生日の新しい順に並べたレコード一覧を取り出す関数
def get_money_flows_by_kind(session: Session, kind: MoneyFlowKind) -> list[MoneyFlows]:
    return (
        session.query(MoneyFlows)
        .filter(
            MoneyFlows.kind == kind
        )  # 条件絞り込み：kindが受け取った引数（MoneyFlowKind.INCOMEなど）と等しい行だけに絞り込む
        .order_by(
            MoneyFlows.occurred_date.desc()
        )  # 並べ替え：occurred_dateを新しい順に（desc）する
        .all()
    )
