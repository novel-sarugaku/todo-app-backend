from collections.abc import Iterator  # iterator：順番に取り出せるもの
from types import SimpleNamespace  # mockを作成するために使用

import pytest  # pytest本体(テスト用ライブラリ)

from fastapi.testclient import TestClient  # FastAPIが用意しているテスト専用のクライアント

import todo_app.api.v1.money_flows as api_money_flows

from todo_app.main import app  # アプリ本体(FastAPIで作ったインスタンス)を読み込み
from todo_app.models.db.base import get_db
from todo_app.models.db.money_flows import MoneyFlows

client = TestClient(app)  # 読み込んだappを渡して、擬似的なHTTPクライアントを作成


# GETテスト
# monkeypatch：pytestが標準で用意しているテスト用の置き換えツール(フィクスチャ)。今回は関数の差し替えに使用
# pytest.MonkeyPatch：monkeypatchのクラス型
def test_get_money_flows(monkeypatch: pytest.MonkeyPatch) -> None:
    # 本当のDBの代わりにダミーを返す関数
    # Iterator[object]：この関数はイテレータ(順番に値を返せるもの)を返すことを示す
    # テストではDBセッションの代わりに、ダミーを渡したいだけなので(sessionを実質使っていない)、中身のないダミーobject()を返す
    def _fake_db() -> Iterator[object]:
        yield object()

    # 本番のget_db(DB接続を返す関数)をテスト用の_fake_db(ダミーを返す関数)に置き換える
    app.dependency_overrides[get_db] = _fake_db

    # テスト用の既存データを用意
    existingData = [
        # SimpleNamespace：d.idのようにドットでアクセスできるオブジェクトを簡単に作るためのもの
        # 本物のDBのオブジェクトも.idや.kind.valueのようにドットでアクセスするため、それと同じ形にするためにSimpleNamespaceを使用する
        SimpleNamespace(
            id=1,
            title="お米",
            amount=4200,
            occurred_date="2025-04-01T00:00:00",
            kind=SimpleNamespace(
                value="expense"
            ),  # kindはEnum風に.valueが要るため、SimpleNamespaceで二重にネスト
        ),
        SimpleNamespace(
            id=2,
            title="給料",
            amount=2000,
            occurred_date="2025-04-01T00:00:00",
            kind=SimpleNamespace(value="income"),
        ),
    ]

    # tryブロック：テスト本体（実行＆検証）
    try:
        # .setattr(対象, "差し替えたい属性名(関数名)", 置き換える値)：対象のモジュール/オブジェクトにある属性(今回は関数)を、別のものに入れ替える
        # lambda ... : ... → 無名関数を作るキーワード
        # lambda _session: items → 引数_sessionを受け取るけど使わず、常にitemsを返す
        monkeypatch.setattr(api_money_flows, "get_money_flows_all", lambda _session: existingData)

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
    # finallyブロック：必ず実行される後片付け。途中で失敗しても、必ず最後にクリーンアップが走る
    finally:
        app.dependency_overrides.pop(
            get_db, None
        )  # 他のテストに影響しないように戻す。dict.pop(key, default)：そのキーを削除して元の値を返す関数。今回はget_dbの差し替えを解除。Noneは、もしキーが無かった場合でもエラーにしないための保険


# POSTテスト
def test_create_money_flows(monkeypatch: pytest.MonkeyPatch) -> None:
    # FakeSession → 本物のDBセッションっぽく振る舞う偽のクラス
    class FakeSession:
        # 追加されたレコードへIDを付けるフリ
        def add(
            self, instance: MoneyFlows
        ) -> None:  # 本来DBに保存するときに呼ぶsession.add(...)の代役
            instance.id = (
                1  # 追加されたインスタンスにIDを設定(今回はID=1)する(本来はDBが自動で設定する)
            )

        def commit(self) -> None:
            self.commit_called = True

        def rollback(self) -> None:  # テストでは何もしない空実装
            pass

    fake_session = FakeSession()

    # FakeSessionを返す関数
    # エンドポイント内でsession.add(...)やsession.commit()を実際に呼ぶため、そのメソッドを持つ偽物＝FakeSessionを渡す必要がある
    def _fake_db() -> Iterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db] = _fake_db

    try:
        # APIに送るJSONデータを用意(辞書型)
        body = {
            "title": "お米",
            "amount": 4200,
            "occurred_date": "2025-04-01T00:00:00",
            "kind": "expense",
        }
        # 実行
        response = client.post(
            "/api/v1/money_flows", json=body
        )  # json=body：辞書をJSONにしてAPIに送る

        # 検証
        assert response.status_code == 200
        assert fake_session.commit_called is True  # commitが呼ばれたことを確認
        assert response.json() == {
            "id": 1,
            "title": "お米",
            "amount": 4200,
            "occurred_date": "2025-04-01T00:00:00",
            "kind": "expense",
        }

    finally:
        app.dependency_overrides.pop(get_db, None)


# POSTテスト（コミットに失敗した場合）
def test_create_money_flows_commit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSession:
        def __init__(
            self,
        ) -> None:  # __init__：コンストラクタ(オブジェクトを作るときに最初の設定をする場所)
            self.commit_called = False  # commitが呼ばれたかどうかのフラグ → 呼ばれていない
            self.rolled_back = False  # rollbackが呼ばれたかどうかのフラグ → 呼ばれていない

        def add(self, instance: MoneyFlows) -> None:
            instance.id = 1

        def commit(self) -> None:
            self.commit_called = True  # commitが呼ばれたことを記録
            raise Exception(
                "コミットに失敗しました"
            )  # わざと例外を発生させる。これによりrollbackが呼ばれるようになる

        def rollback(self) -> None:
            self.rolled_back = True  # rollbackが呼ばれたことを記録

    fake_session = FakeSession()

    def _fake_db() -> Iterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db] = _fake_db

    try:
        body = {
            "title": "お米",
            "amount": 4200,
            "occurred_date": "2025-04-01T00:00:00",
            "kind": "expense",
        }
        # 実行
        client.post("/api/v1/money_flows", json=body)

        # 検証
        assert fake_session.commit_called is True
        assert fake_session.rolled_back is True  # rollbackが呼ばれたことを確認

    finally:
        app.dependency_overrides.pop(get_db, None)


# PUTテスト
def test_update_money_flows(monkeypatch: pytest.MonkeyPatch) -> None:
    # テスト用の既存データを用意
    existingData = SimpleNamespace(
        id=1,
        title="古いタイトル",
        amount=1000,
        occurred_date="2025-04-01T00:00:00",
        kind=SimpleNamespace(value="expense"),
    )

    monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: existingData)

    class FakeSession:
        def commit(self) -> None:
            self.commit_called = True

        def rollback(self) -> None:
            pass

    fake_session = FakeSession()

    def _fake_db() -> Iterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db] = _fake_db

    try:
        body = {
            "id": 1,
            "title": "新しいタイトル",
            "amount": 2000,
            "occurred_date": "2025-04-02T00:00:00",
            "kind": "income",
        }
        # 実行
        response = client.put("/api/v1/money_flows", json=body)

        # 検証
        assert response.status_code == 200
        assert fake_session.commit_called is True
        assert response.json() == {
            "id": 1,
            "title": "新しいタイトル",
            "amount": 2000,
            "occurred_date": "2025-04-02T00:00:00",
            "kind": "income",
        }

    finally:
        app.dependency_overrides.pop(get_db, None)


# PUTテスト（コミットに失敗した場合）
def test_update_money_flows_commit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # テスト用の既存データを用意
    existingData = SimpleNamespace(
        id=1,
        title="古いタイトル",
        amount=1000,
        occurred_date="2025-04-01T00:00:00",
        kind=SimpleNamespace(value="expense"),
    )

    monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: existingData)

    class FakeSession:
        def __init__(
            self,
        ) -> None:
            self.commit_called = False
            self.rolled_back = False

        def commit(self) -> None:
            self.commit_called = True
            raise Exception("コミットに失敗しました")

        def rollback(self) -> None:
            self.rolled_back = True

    fake_session = FakeSession()

    def _fake_db() -> Iterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db] = _fake_db

    try:
        body = {
            "id": 1,
            "title": "新しいタイトル",
            "amount": 2000,
            "occurred_date": "2025-04-02T00:00:00",
            "kind": "income",
        }
        # 実行
        client.put("/api/v1/money_flows", json=body)

        # 検証
        assert fake_session.commit_called is True
        assert fake_session.rolled_back is True

    finally:
        app.dependency_overrides.pop(get_db, None)


# PUTテスト（指定IDが存在しない場合：BusinessException）
def test_update_money_flows_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        api_money_flows, "get_money_flow_by_id", lambda _session, id: None
    )  # 指定したIDが見つからない想定のためNoneを返す

    def _fake_db() -> Iterator[object]:
        yield object()

    app.dependency_overrides[get_db] = _fake_db

    try:
        body = {
            "id": 999,  # 存在しないID
            "title": "存在しないIDのタイトル",
            "amount": 1,
            "occurred_date": "2025-04-01T00:00:00",
            "kind": "expense",
        }
        # 実行
        response = client.put("/api/v1/money_flows", json=body)

        # 検証
        assert response.status_code == 422  # 設定した422が返ることを確認
        assert response.json() == {
            "detail": "指定したIDが存在しません。"
        }  # 設定したメッセージが返ることを確認
    finally:
        app.dependency_overrides.pop(get_db, None)


# DELETEテスト
def test_delete_money_flows(monkeypatch: pytest.MonkeyPatch) -> None:
    targetData = SimpleNamespace(
        id=1,
        title="削除用タイトル",
        amount=100,
        occurred_date="2025-04-01T00:00:00",
        kind=SimpleNamespace(value="expense"),
    )

    monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: targetData)

    class FakeSession:
        def __init__(
            self,
        ) -> None:
            self.deleted = None  # 削除対象の入れ物 → 最初は何も入っていない状態のためNone
            self.commit_called = False

        def delete(
            self, obj: object
        ) -> None:  # 削除命令のフリをするメソッド。session.delete(obj)の代役
            self.deleted = obj  # 削除されたオブジェクトを記録

        def commit(self) -> None:
            self.commit_called = True

        def rollback(self) -> None:
            pass

    fake_session = FakeSession()

    def _fake_db() -> Iterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db] = _fake_db

    try:
        # 実行
        # TestClientはdelete()はjson=を受け付けない実装なので、request()で代用。.request()は共通の引数を受け付ける（json=, data=, params=, headers= など）。
        response = client.request("DELETE", "/api/v1/money_flows", json={"id": 1})

        # 検証
        # == は「中身が等しいか」、is は「同じ実体か（同じ参照か）」
        assert response.status_code == 204
        assert (
            fake_session.deleted is targetData
        )  # session.delete()に正しい対象（targetData）が渡されたことを確認
        assert fake_session.commit_called is True

    finally:
        app.dependency_overrides.pop(get_db, None)


# DELETEテスト（コミットに失敗した場合）
def test_delete_money_flows_commit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    targetData = SimpleNamespace(
        id=1,
        title="削除用タイトル",
        amount=100,
        occurred_date="2025-04-01T00:00:00",
        kind=SimpleNamespace(value="expense"),
    )

    monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: targetData)

    class FakeSession:
        def __init__(
            self,
        ) -> None:
            self.deleted = None
            self.commit_called = False
            self.rolled_back = False

        def delete(self, obj: object) -> None:
            self.deleted = obj

        def commit(self) -> None:
            self.commit_called = True
            raise Exception("コミットに失敗しました")

        def rollback(self) -> None:
            self.rolled_back = True

    fake_session = FakeSession()

    def _fake_db() -> Iterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db] = _fake_db

    try:
        # 実行
        client.request("DELETE", "/api/v1/money_flows", json={"id": 1})

        # 検証
        assert fake_session.deleted is targetData
        assert fake_session.commit_called is True
        assert fake_session.rolled_back is True

    finally:
        app.dependency_overrides.pop(get_db, None)


# DELETEテスト（指定IDが存在しない場合：BusinessException）
def test_delete_money_flows_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_money_flows, "get_money_flow_by_id", lambda _session, id: None)

    def _fake_db() -> Iterator[object]:
        yield object()

    app.dependency_overrides[get_db] = _fake_db

    try:
        response = client.request("DELETE", "/api/v1/money_flows", json={"id": 999})

        assert response.status_code == 422
        assert response.json() == {"detail": "指定したIDが存在しません。"}
    finally:
        app.dependency_overrides.pop(get_db, None)
