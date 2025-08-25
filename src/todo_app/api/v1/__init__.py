from fastapi import APIRouter

from todo_app.api.v1.healthcheck import router as healthcheck_router
from todo_app.api.v1.money_flows import router as money_flows_router

router = APIRouter()
router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
router.include_router(money_flows_router, prefix="/money_flows", tags=["MoneyFlows"])
