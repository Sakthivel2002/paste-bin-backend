import os
import time
import random
import string
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone  


def generate_id(length=7):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))



def get_now(request=None):
    """
    Deterministic time support for automated testing.
    """
    if os.getenv("TEST_MODE") == "1" and request:
        header_time = request.headers.get("x-test-now-ms")
        if header_time:
            # Use Python's datetime.timezone.utc
            return datetime.fromtimestamp(int(header_time) / 1000, tz=dt_timezone.utc)
    return timezone.now()
