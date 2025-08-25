import logging  # Pythonに標準で備わっている

# handler：脳みそのようなもの
handler = logging.StreamHandler()
# %(levelname)s や %(message)sなど：LogRecord 属性
# %(levelname)s：メッセージのための文字のロギングレベル ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
log_format = "%(levelname)s : %(message)s"
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)

# loggingからCustomLoggerという子供を作成
logger = logging.getLogger("CustomLogger")
# CustomLoggerはhandlerを使って動くイメージ
logger.addHandler(handler)
# info以上のもの（'INFO', 'WARNING', 'ERROR', 'CRITICAL')を表示（'DEBUG'は出さない）
logger.setLevel(logging.INFO)
