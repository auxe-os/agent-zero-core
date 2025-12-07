from datetime import datetime, timezone as dt_timezone, timedelta
import pytz  # type: ignore

from python.helpers.print_style import PrintStyle
from python.helpers.dotenv import get_dotenv_value, save_dotenv_value



class Localization:
    """A class for handling timezone conversions between UTC and local time."""

    # singleton
    _instance = None

    @classmethod
    def get(cls, *args, **kwargs):
        """Gets the singleton instance of the Localization class.

        Returns:
            The singleton instance of the Localization class.
        """
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self, timezone: str | None = None):
        """Initializes a Localization instance.

        Args:
            timezone: The timezone to use.
        """
        self.timezone: str = "UTC"
        self._offset_minutes: int = 0
        self._last_timezone_change: datetime | None = None
        # Load persisted values if available
        persisted_tz = str(get_dotenv_value("DEFAULT_USER_TIMEZONE", "UTC"))
        persisted_offset = get_dotenv_value("DEFAULT_USER_UTC_OFFSET_MINUTES", None)
        if timezone is not None:
            # Explicit override
            self.set_timezone(timezone)
        else:
            # Initialize from persisted values
            self.timezone = persisted_tz
            if persisted_offset is not None:
                try:
                    self._offset_minutes = int(str(persisted_offset))
                except Exception:
                    self._offset_minutes = self._compute_offset_minutes(self.timezone)
                    save_dotenv_value("DEFAULT_USER_UTC_OFFSET_MINUTES", str(self._offset_minutes))
            else:
                # Compute from timezone and persist
                self._offset_minutes = self._compute_offset_minutes(self.timezone)
                save_dotenv_value("DEFAULT_USER_UTC_OFFSET_MINUTES", str(self._offset_minutes))

    def get_timezone(self) -> str:
        """Gets the current timezone.

        Returns:
            The current timezone.
        """
        return self.timezone

    def _compute_offset_minutes(self, timezone_name: str) -> int:
        """Computes the UTC offset in minutes for a given timezone."""
        tzinfo = pytz.timezone(timezone_name)
        now_in_tz = datetime.now(tzinfo)
        offset = now_in_tz.utcoffset()
        return int(offset.total_seconds() // 60) if offset else 0

    def get_offset_minutes(self) -> int:
        """Gets the current UTC offset in minutes.

        Returns:
            The current UTC offset in minutes.
        """
        return self._offset_minutes

    def _can_change_timezone(self) -> bool:
        """Checks if the timezone can be changed.

        The timezone can only be changed once per hour.

        Returns:
            True if the timezone can be changed, False otherwise.
        """
        if self._last_timezone_change is None:
            return True

        time_diff = datetime.now() - self._last_timezone_change
        return time_diff >= timedelta(hours=1)

    def set_timezone(self, timezone: str) -> None:
        """Sets the timezone.

        Args:
            timezone: The timezone to set.
        """
        try:
            # Validate timezone and compute its current offset
            _ = pytz.timezone(timezone)
            new_offset = self._compute_offset_minutes(timezone)

            # If offset changes, check rate limit and update
            if new_offset != getattr(self, "_offset_minutes", None):
                if not self._can_change_timezone():
                    return

                prev_tz = getattr(self, "timezone", "None")
                prev_off = getattr(self, "_offset_minutes", None)
                PrintStyle.debug(
                    f"Changing timezone from {prev_tz} (offset {prev_off}) to {timezone} (offset {new_offset})"
                )
                self._offset_minutes = new_offset
                self.timezone = timezone
                # Persist both the human-readable tz and the numeric offset
                save_dotenv_value("DEFAULT_USER_TIMEZONE", timezone)
                save_dotenv_value("DEFAULT_USER_UTC_OFFSET_MINUTES", str(self._offset_minutes))

                # Update rate limit timestamp only when actual change occurs
                self._last_timezone_change = datetime.now()
            else:
                # Offset unchanged: update stored timezone without logging or persisting to avoid churn
                self.timezone = timezone
        except pytz.exceptions.UnknownTimeZoneError:
            PrintStyle.error(f"Unknown timezone: {timezone}, defaulting to UTC")
            self.timezone = "UTC"
            self._offset_minutes = 0
            # save defaults to avoid future errors on startup
            save_dotenv_value("DEFAULT_USER_TIMEZONE", "UTC")
            save_dotenv_value("DEFAULT_USER_UTC_OFFSET_MINUTES", "0")

    def localtime_str_to_utc_dt(self, localtime_str: str | None) -> datetime | None:
        """Converts a local time string to a UTC datetime object.

        Args:
            localtime_str: The local time string to convert.

        Returns:
            A UTC datetime object, or None if the input is invalid.
        """
        if not localtime_str:
            return None

        try:
            # Handle both with and without timezone info
            try:
                # Try parsing with timezone info first
                local_datetime_obj = datetime.fromisoformat(localtime_str)
                if local_datetime_obj.tzinfo is None:
                    # If no timezone info, assume fixed offset
                    local_datetime_obj = local_datetime_obj.replace(
                        tzinfo=dt_timezone(timedelta(minutes=self._offset_minutes))
                    )
            except ValueError:
                # If timezone parsing fails, try without timezone
                base = localtime_str.split('Z')[0].split('+')[0]
                local_datetime_obj = datetime.fromisoformat(base)
                local_datetime_obj = local_datetime_obj.replace(
                    tzinfo=dt_timezone(timedelta(minutes=self._offset_minutes))
                )

            # Convert to UTC
            return local_datetime_obj.astimezone(dt_timezone.utc)
        except Exception as e:
            PrintStyle.error(f"Error converting localtime string to UTC: {e}")
            return None

    def utc_dt_to_localtime_str(self, utc_dt: datetime | None, sep: str = "T", timespec: str = "auto") -> str | None:
        """Converts a UTC datetime object to a local time string.

        Args:
            utc_dt: The UTC datetime object to convert.
            sep: The separator to use between the date and time.
            timespec: The time specification to use.

        Returns:
            A local time string, or None if the input is invalid.
        """
        if utc_dt is None:
            return None

        # At this point, utc_dt is definitely not None
        assert utc_dt is not None

        try:
            # Ensure datetime is timezone aware in UTC
            if utc_dt.tzinfo is None:
                utc_dt = utc_dt.replace(tzinfo=dt_timezone.utc)
            else:
                utc_dt = utc_dt.astimezone(dt_timezone.utc)

            # Convert to local time using fixed offset
            local_tz = dt_timezone(timedelta(minutes=self._offset_minutes))
            local_datetime_obj = utc_dt.astimezone(local_tz)
            return local_datetime_obj.isoformat(sep=sep, timespec=timespec)
        except Exception as e:
            PrintStyle.error(f"Error converting UTC datetime to localtime string: {e}")
            return None

    def serialize_datetime(self, dt: datetime | None) -> str | None:
        """Serializes a datetime object to an ISO format string.

        Args:
            dt: The datetime object to serialize.

        Returns:
            An ISO format string, or None if the input is invalid.
        """
        if dt is None:
            return None

        # At this point, dt is definitely not None
        assert dt is not None

        try:
            # Ensure datetime is timezone aware (if not, assume UTC)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=dt_timezone.utc)

            local_tz = dt_timezone(timedelta(minutes=self._offset_minutes))
            local_dt = dt.astimezone(local_tz)
            return local_dt.isoformat()
        except Exception as e:
            PrintStyle.error(f"Error serializing datetime: {e}")
            return None
