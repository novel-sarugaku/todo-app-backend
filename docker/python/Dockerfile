FROM python:3.13

WORKDIR /todo_app

# apt:Linuxがパッケージのインストールをするとき
# tzdata：datetimeを使う時に記載する
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN pip install poetry

# Poetryの仮想環境は使わずグローバルに（Docker内ではこれがシンプル）
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# アプリケーションのソースコードをコピー
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

