from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from todo_app.exceptions.business_error_exception import BusinessException
from todo_app.models.db.base import get_db
from todo_app.models.db.money_flows import MoneyFlowKind, MoneyFlows
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
from todo_app.repositories.money_flows import (
    get_money_flow_by_id,
    get_money_flows_all,
    get_money_flows_by_kind,
)

router = APIRouter()

# ★TODO: APIテスト実施の際に、BusinessExceptionのみでなく、他の例外（SystemException、DatabaseExceptioなど）の自作エラーも追加する。

@router.get("/{id}")
def get_money_flow(
    id: int, session: Annotated[Session, Depends(get_db)]
) -> GetMoneyFlowResponseItem:
    # データ１件取得する
    money_flow_item = get_money_flow_by_id(session, id=id)

    if money_flow_item is None:
        raise BusinessException("指定したIDが存在しません。")

    return GetMoneyFlowResponseItem(
        id=money_flow_item.id,
        title=money_flow_item.title,
        amount=money_flow_item.amount,
        occurred_date=money_flow_item.occurred_date,
        kind=money_flow_item.kind.value,
    )


@router.get("")
def get_money_flows(
    session: Annotated[Session, Depends(get_db)],
    kind: Literal["expense", "income"] | None = Query(
        default=None
    ),  # クエリパラメータで種別を受け取る。絞り込みは任意のため、指定がなければNone
) -> list[GetMoneyFlowResponseItem]:
    # kindがあるときは種別で絞る、ないときは全件取得
    money_flow_items = (
        get_money_flows_by_kind(session, MoneyFlowKind(kind))
        if kind
        else get_money_flows_all(session)
    )

    return [
        GetMoneyFlowResponseItem(
            id=item.id,
            title=item.title,
            amount=item.amount,
            occurred_date=item.occurred_date,
            kind=item.kind.value,
        )
        for item in money_flow_items
    ]


@router.post("")
def create_money_flows(
    body: CreateMoneyFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> CreateMoneyFlowResponse:
    new_money_flow = MoneyFlows(
        title=body.title,
        amount=body.amount,
        occurred_date=body.occurred_date,
        kind=MoneyFlowKind(body.kind),
    )

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
        kind=new_money_flow.kind.value,
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
    target_money_flow.kind = MoneyFlowKind(body.kind)

    try:
        session.commit()
    except Exception:
        session.rollback()
    return UpdateMoneyFlowResponse(
        id=target_money_flow.id,
        title=target_money_flow.title,
        amount=target_money_flow.amount,
        occurred_date=target_money_flow.occurred_date,
        kind=target_money_flow.kind.value,
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
