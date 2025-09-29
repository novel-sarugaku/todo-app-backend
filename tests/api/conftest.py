# ★pytestは conftest.py を自動で読み込むため、テストファイルから明示的にimportする必要はない。
# ★ディレクトリ階層にある conftest.py が、その配下の全テストに適用される（tests/api/conftest.py なら tests/api/ 配下に有効）。

from collections.abc import Iterator  # iterator：順番に取り出せるもの

import pytest  # pytest本体(テスト用ライブラリ)

from todo_app.main import app  # アプリ本体(FastAPIで作ったインスタンス)を読み込み
from todo_app.models.db.base import get_db
from todo_app.models.db.money_flows import MoneyFlows


# 【コミット成功パターン（GET/POST/PUT/DELETEテストで使用）】
# そのテストで必要なメソッドが入っていれば十分なため、使わないメソッド（add()delete()など）があっても、問題はない。
class FakeSessionOK:  # FakeSession → 本物のDBセッションっぽく振る舞う偽のクラス
    def __init__(
        self,
    ) -> None:
        self.deleted = None  # 削除対象の入れ物 → 最初は何も入っていない状態のためNone
        self.commit_called = False

    # 追加されたレコードへIDを付けるフリをするメソッド
    # 本来DBに保存するときに呼ぶsession.add(...)の代役
    def add(self, instance: MoneyFlows) -> None:
        instance.id = (
            1  # 追加されたインスタンスにIDを設定(今回はID=1)する(本来はDBが自動で設定する)
        )

    # 削除命令のフリをするメソッド
    # session.delete(obj)の代役
    def delete(self, obj: object) -> None:
        self.deleted = obj  # 削除されたオブジェクトを記録

    def commit(self) -> None:
        self.commit_called = True

    def rollback(self) -> None:  # テストでは何もしない空実装
        pass


# ダミーセッションを返すフィクスチャ
@pytest.fixture
def success_session() -> FakeSessionOK:
    return FakeSessionOK()


# FastAPIのget_dbをsuccess_sessionに差し替えるフィクスチャ
@pytest.fixture
def override_get_db_success(success_session: FakeSessionOK) -> Iterator[FakeSessionOK]:
    # FakeSessionを返す関数
    # エンドポイント内でsession.add(...)やsession.commit()を実際に呼ぶため、そのメソッドを持つ偽物＝FakeSessionを渡す必要がある。
    def _fake_db() -> Iterator[FakeSessionOK]:
        yield success_session

    app.dependency_overrides[get_db] = _fake_db

    yield success_session

    app.dependency_overrides.pop(get_db, None)


# 【コミット失敗パターン（POST/PUT/DELETEテストで使用）】
class FakeSessionError:
    def __init__(
        self,
    ) -> None:  # __init__：コンストラクタ(オブジェクトを作るときに最初の設定をする場所)
        self.deleted = None
        self.commit_called = False  # commitが呼ばれたかどうかのフラグ → 呼ばれていない
        self.rolled_back = False  # rollbackが呼ばれたかどうかのフラグ → 呼ばれていない

    def add(self, instance: MoneyFlows) -> None:
        instance.id = 1

    def delete(self, obj: object) -> None:
        self.deleted = obj

    def commit(self) -> None:
        self.commit_called = True  # commitが呼ばれたことを記録
        raise Exception(
            "コミットに失敗しました"
        )  # わざと例外を発生させる。これによりrollbackが呼ばれるようになる

    def rollback(self) -> None:
        self.rolled_back = True  # rollbackが呼ばれたことを記録


# ダミーセッションを返すフィクスチャ
@pytest.fixture
def error_session() -> FakeSessionError:
    return FakeSessionError()


# FastAPIのget_dbをerror_sessionに差し替えるフィクスチャ
@pytest.fixture
def override_get_db_error(error_session: FakeSessionError) -> Iterator[FakeSessionError]:
    def _fake_db() -> Iterator[FakeSessionError]:
        yield error_session

    app.dependency_overrides[get_db] = _fake_db

    yield error_session

    app.dependency_overrides.pop(get_db, None)
