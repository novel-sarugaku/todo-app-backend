from dataclasses import dataclass  # テスト用の「ダミーのデータ型」を簡単に作るためのライブラリ
from typing import (
    TYPE_CHECKING,  # 型チェック専用のフラグ。型チェックのときだけTrue、実行時はFalseになる特別なフラグ
)

import pytest  # pytest本体(テスト用ライブラリ)

from fastapi.testclient import TestClient  # FastAPIが用意しているテスト専用のクライアント

import todo_app.api.v1.money_flows as api_money_flows

from todo_app.main import app  # アプリ本体(FastAPIで作ったインスタンス)を読み込み

client = TestClient(app)  # 読み込んだappを渡して、擬似的なHTTPクライアントを作成

# if TYPE_CHECKING: ブロックの中は、実行時には動かないため、副作用や循環を起こさない。
# 型の参照だけ。conftest.pyはpytest専用の自動読み込みファイルで直importはNG
# if TYPE_CHECKING:
#     from tests.api.conftest import (
#         FakeSessionError,
#         FakeSessionOK,
#     )

if TYPE_CHECKING:
    from ..conftest import FakeSessionOK

# ダミーモデルを定義（この型を使ってテスト内でダミーデータを作成する）
@dataclass
class DummyKind:  # 収支の種類（expense/income）を表すクラス
    value: str  # .valueを参照する想定のため、valueという名前の文字列フィールドを持たせている


@dataclass
class DummyFlow:  # 収支データを表すクラス
    id: int
    title: str
    amount: int
    occurred_date: str
    kind: DummyKind


# GETテスト
# この記載でセットアップ/後片付けが効く（conftest.pyより）
@pytest.mark.usefixtures("override_get_db_success")
# monkeypatch：pytestが標準で用意しているテスト用の置き換えツール(フィクスチャ)。今回は関数の差し替えに使用
# pytest.MonkeyPatch：monkeypatchのクラス型
def test_get_money_flows(monkeypatch: pytest.MonkeyPatch) -> None:
    # テスト用の既存データを用意
    existing_data = [
        DummyFlow(
            1,
            "お米",
            4200,
            "2025-04-01T00:00:00",
            DummyKind("expense"),
        ),
        DummyFlow(
            2,
            "給料",
            2000,
            "2025-04-01T00:00:00",
            DummyKind("income"),
        ),
    ]
    # .setattr(対象, "差し替えたい属性名(関数名)", 置き換える値)：対象のモジュール/オブジェクトにある属性(今回は関数)を、別のものに入れ替える
    # lambda ... : ... → 無名関数を作るキーワード
    # lambda _session: items → 引数_sessionを受け取るけど使わず、常にitemsを返す
    monkeypatch.setattr(api_money_flows, "get_money_flows_all", lambda _session: existing_data)

    # 実行
    response = client.get("/api/v1/money_flows/")

    # 検証
    assert response.status_code == 200  # ステータスコードが200(成功)であることを確認
    assert (
        response.json()  # 返ってきたデータの中身が以下と同じであるかを確認。response.json()：JSON → 辞書への変換
        == [
            {
                "id": 1,
                "title": "お米",
                "amount": 4200,
                "occurred_date": "2025-04-01T00:00:00",
                "kind": "expense",
            },
            {
                "id": 2,
                "title": "給料",
                "amount": 2000,
                "occurred_date": "2025-04-01T00:00:00",
                "kind": "income",
            },
        ]
    )


# POSTテスト
# テスト関数の引数にoverride_get_db_commit_okを書くと、フィクスチャでyieldされたFakeSessionが渡ってくる。
# @pytest.mark.usefixtures(...) を使うと戻り値が受け取れない。
@pytest.mark.usefixtures("override_get_db_commit_ok")
def test_create_money_flows(success_session: "FakeSessionOK") -> None:
    # APIに送るJSONデータを用意(辞書型)
    body = {
        "title": "お米",
        "amount": 4200,
        "occurred_date": "2025-04-01T00:00:00",
        "kind": "expense",
    }

    # 実行
    response = client.post("/api/v1/money_flows", json=body)  # json=body：辞書をJSONにしてAPIに送る

    # 検証
    assert response.status_code == 200
    assert success_session.commit_called is True  # commitが呼ばれたことを確認
    assert response.json() == {
        "id": 1,
        "title": "お米",
        "amount": 4200,
        "occurred_date": "2025-04-01T00:00:00",
        "kind": "expense",
    }


# # POSTテスト（コミットに失敗した場合）
# def test_create_money_flows_commit_error(override_get_db_commit_error: "FakeSessionError") -> None:
#     # 失敗用ダミーセッション
#     fake_session = override_get_db_commit_error

#     body = {
#         "title": "お米",
#         "amount": 4200,
#         "occurred_date": "2025-04-01T00:00:00",
#         "kind": "expense",
#     }

#     # 実行
#     client.post("/api/v1/money_flows", json=body)

#     # 検証
#     assert fake_session.commit_called is True
#     assert fake_session.rolled_back is True  # rollbackが呼ばれたことを確認


# # PUTテスト
# def test_update_money_flows(
#     override_get_db_commit_ok: "FakeSessionOK", monkeypatch: pytest.MonkeyPatch
# ) -> None:
#     # テスト用の既存データを用意
#     existing_data = DummyFlow(
#         1,
#         "古いタイトル",
#         1000,
#         "2025-04-01T00:00:00",
#         DummyKind("expense"),
#     )

#     monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: existing_data)

#     # 成功用ダミーセッション
#     fake_session = override_get_db_commit_ok

#     body = {
#         "id": 1,
#         "title": "新しいタイトル",
#         "amount": 2000,
#         "occurred_date": "2025-04-02T00:00:00",
#         "kind": "income",
#     }

#     # 実行
#     response = client.put("/api/v1/money_flows", json=body)

#     # 検証
#     assert response.status_code == 200
#     assert fake_session.commit_called is True
#     assert response.json() == {
#         "id": 1,
#         "title": "新しいタイトル",
#         "amount": 2000,
#         "occurred_date": "2025-04-02T00:00:00",
#         "kind": "income",
#     }


# # PUTテスト（コミットに失敗した場合）
# def test_update_money_flows_commit_error(
#     override_get_db_commit_error: "FakeSessionError", monkeypatch: pytest.MonkeyPatch
# ) -> None:
#     # テスト用の既存データを用意
#     existing_data = DummyFlow(
#         1,
#         "古いタイトル",
#         1000,
#         "2025-04-01T00:00:00",
#         DummyKind("expense"),
#     )

#     monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: existing_data)

#     # 失敗用ダミーセッション
#     fake_session = override_get_db_commit_error

#     body = {
#         "id": 1,
#         "title": "新しいタイトル",
#         "amount": 2000,
#         "occurred_date": "2025-04-02T00:00:00",
#         "kind": "income",
#     }

#     # 実行
#     client.put("/api/v1/money_flows", json=body)

#     # 検証
#     assert fake_session.commit_called is True
#     assert fake_session.rolled_back is True


# # PUTテスト（指定IDが存在しない場合：BusinessException）
# @pytest.mark.usefixtures("override_get_db_success")
# def test_update_money_flows_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
#     monkeypatch.setattr(
#         api_money_flows, "get_money_flow_by_id", lambda _session, id: None
#     )  # 指定したIDが見つからない想定のためNoneを返す

#     body = {
#         "id": 999,  # 存在しないID
#         "title": "存在しないIDのタイトル",
#         "amount": 1,
#         "occurred_date": "2025-04-01T00:00:00",
#         "kind": "expense",
#     }

#     # 実行
#     response = client.put("/api/v1/money_flows", json=body)

#     # 検証
#     assert response.status_code == 422  # 設定した422が返ることを確認
#     assert response.json() == {
#         "detail": "指定したIDが存在しません。"
#     }  # 設定したメッセージが返ることを確認


# # DELETEテスト
# def test_delete_money_flows(
#     override_get_db_commit_ok: "FakeSessionOK", monkeypatch: pytest.MonkeyPatch
# ) -> None:
#     target_data = DummyFlow(
#         1,
#         "削除用タイトル",
#         100,
#         "2025-04-01T00:00:00",
#         DummyKind("expense"),
#     )

#     monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: target_data)

#     # 成功用ダミーセッション
#     fake_session = override_get_db_commit_ok

#     # 実行
#     # TestClientはdelete()はjson=を受け付けない実装なので、request()で代用。.request()は共通の引数を受け付ける（json=, data=, params=, headers= など）。
#     response = client.request("DELETE", "/api/v1/money_flows", json={"id": 1})

#     # 検証
#     # == は「中身が等しいか」、is は「同じ実体か（同じ参照か）」
#     assert response.status_code == 204
#     assert (
#         fake_session.deleted is target_data
#     )  # session.delete()に正しい対象（target_data）が渡されたことを確認
#     assert fake_session.commit_called is True


# # DELETEテスト（コミットに失敗した場合）
# def test_delete_money_flows_commit_error(
#     override_get_db_commit_error: "FakeSessionError", monkeypatch: pytest.MonkeyPatch
# ) -> None:
#     target_data = DummyFlow(
#         1,
#         "削除用タイトル",
#         100,
#         "2025-04-01T00:00:00",
#         kind=DummyKind("expense"),
#     )

#     monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: target_data)

#     # 失敗用ダミーセッション
#     fake_session = override_get_db_commit_error

#     # 実行
#     client.request("DELETE", "/api/v1/money_flows", json={"id": 1})

#     # 検証
#     assert fake_session.deleted is target_data
#     assert fake_session.commit_called is True
#     assert fake_session.rolled_back is True


# # DELETEテスト（指定IDが存在しない場合：BusinessException）
# @pytest.mark.usefixtures("override_get_db_success")
# def test_delete_money_flows_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
#     monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: None)

#     response = client.request("DELETE", "/api/v1/money_flows", json={"id": 999})

#     assert response.status_code == 422
#     assert response.json() == {"detail": "指定したIDが存在しません。"}
