from datetime import datetime
from zoneinfo import ZoneInfo

from freezegun import freeze_time

from todo_app.logic.calculate.calculate_datetime import get_now


@freeze_time("2025-04-01 12:00:00")
def test_get_now() -> None:
    result = get_now()
    expected = datetime(
        year=2025,
        month=4,
        day=1,
        hour=21,
        minute=0,
        second=0,
        tzinfo=ZoneInfo('Asia/Tokyo')
    )

    assert result == expected
    assert result.tzinfo == ZoneInfo("Asia/Tokyo")
