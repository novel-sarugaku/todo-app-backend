from fastapi import HTTPException


# Exceptionの中のBusinessExceptionというエラー
# Exception > HTTPException > BusinessException
# HTTPExceptionを使う際は、tatus_code=やdetail=messageを記載するのがお決まり
class BusinessException(HTTPException):
    # self：クラス自身（＝BusinessException）記載するのがお決まり
    def __init__(self, message: str) -> None:
        # super：親クラス（＝HTTPException）
        super().__init__(status_code=422, detail=message)
