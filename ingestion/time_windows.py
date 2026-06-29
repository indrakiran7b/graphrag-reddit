from datetime import datetime, timedelta, timezone


def get_time_windows():

    now = datetime.now(timezone.utc)

    return {

        "Last7Days": {

            "start": now - timedelta(days=7),

            "end": now

        },

        "Last30Days": {

            "start": now - timedelta(days=30),

            "end": now

        },

        "Last180Days": {

            "start": now - timedelta(days=180),

            "end": now

        }

    }