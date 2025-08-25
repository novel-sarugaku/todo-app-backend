from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from todo_app.exceptions.business_error_exception import BusinessException
from todo_app.models.db.base import get_db
from todo_app.models.db.money_flows import MoneyFlows
from todo_app.models.request.v1.money_flows import (
    CreateMoneyFlowRequest,
    DeleteMoneyFlowRequest,
    UpdateMoneyFlowRequest,
)
from todo_app.models.response.v1.money_flows import (
    CreateMoneyFlowResponse,
    GetMoneyFlowResponseItem,
    UpdateMoneyFlowResponse,
)
from todo_app.repositories.money_flows import get_money_flow_by_id, get_money_flows_all

router = APIRouter()

@router.get("/{id}")
def get_money_flow(id: int, session: Annotated[Session, Depends(get_db)]) -> GetMoneyFlowResponseItem:
    # データ１件取得する
    money_flow_item = get_money_flow_by_id(session, id=id)

    if money_flow_item is None:
        raise BusinessException("指定したIDが存在しません。")

    return GetMoneyFlowResponseItem(
        id=money_flow_item.id,
        title=money_flow_item.title,
        amount=money_flow_item.amount,
        occurred_date=money_flow_item.occurred_date,
    )

@router.get("")
def get_money_flows(session: Annotated[Session, Depends(get_db)]) -> list[GetMoneyFlowResponseItem]:
    # データすべて取得する　.query()：参照するテーブルを指定　.all()：データすべて指定
    money_flow_items = get_money_flows_all(session)

    return [
        GetMoneyFlowResponseItem(
            id=item.id,
            title=item.title,
            amount=item.amount,
            occurred_date=item.occurred_date,
        )
        for item in money_flow_items
    ]


@router.post("")
def create_money_flows(
    body: CreateMoneyFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> CreateMoneyFlowResponse:
    new_money_flow = MoneyFlows(title=body.title, amount=body.amount, occurred_date=body.occurred_date)

    session.add(new_money_flow)

    try:
        session.commit()
    except Exception:
        session.rollback()
    return CreateMoneyFlowResponse(
        id=new_money_flow.id,
        title=new_money_flow.title,
        amount=new_money_flow.amount,
        occurred_date=new_money_flow.occurred_date,
    )


@router.put("")
def update_money_flows(
    body: UpdateMoneyFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> UpdateMoneyFlowResponse:
    target_money_flow = get_money_flow_by_id(session, id=body.id)

    # 指定したIDが存在しなかった場合の自作エラー（BusinessException）を発動
    if target_money_flow is None:
        raise BusinessException("指定したIDが存在しません。")

    target_money_flow.title = body.title
    target_money_flow.amount = body.amount
    target_money_flow.occurred_date = body.occurred_date

    try:
        session.commit()
    except Exception:
        session.rollback()
    return UpdateMoneyFlowResponse(
        id=target_money_flow.id,
        title=target_money_flow.title,
        amount=target_money_flow.amount,
        occurred_date=target_money_flow.occurred_date,
    )

# status_code=204：成功したが、返す情報がない（返信コメントなし）
@router.delete("", status_code=204)
def delete_money_flows(
    body: DeleteMoneyFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> Response:
    target_money_flow = get_money_flow_by_id(session, id=body.id)
    # 指定したIDが存在しなかった場合の自作エラー（BusinessException）を発動
    if target_money_flow is None:
        # raise：Pythonでエラーを意図的に発生させるためのキーワード
        raise BusinessException("指定したIDが存在しません。")

    session.delete(target_money_flow)

    try:
        session.commit()
    except Exception:
        session.rollback()
    return Response(status_code=204)
