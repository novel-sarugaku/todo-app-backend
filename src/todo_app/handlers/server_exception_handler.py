from fastapi.requests import Request
from fastapi.responses import JSONResponse


# リクエストの型はRequest（Exceptionが発生した際に）で、
# レスポンスはJSONResponse（JSON形式）で返すよう指定
def handler(request: Request, exc: Exception) -> JSONResponse:
    # JSONResponse（JSON形式）で返すときは必ず、status_codeとontentを設定する
    return JSONResponse(status_code=500, content="システムエラーが発生しました")
