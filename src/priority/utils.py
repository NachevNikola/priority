from datetime import timedelta
from typing import Optional

from pydantic import BaseModel


def parse_timedelta(time_str: str) -> Optional[timedelta]:
    class TimedeltaParser(BaseModel):
        timedelta: timedelta

    parser = TimedeltaParser(timedelta=time_str)
    return parser.timedelta
