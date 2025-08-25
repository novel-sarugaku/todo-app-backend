from fastapi import APIRouter

from todo_app.loggers.custom_logger import logger

router = APIRouter()

@router.get("")
def healthcheck() -> str:
    # ここで設定したロガーを使う。docker desktopのapiコンテナのlogに表示される
    logger.info("ヘルスチェックの中身です")
    return "お疲れ様です！！"
