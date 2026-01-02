from datetime import datetime, date, time
from zoneinfo import ZoneInfo

def get_today_range_utcToLocal(day: date, tz_name: str = "America/Argentina/Buenos_Aires") -> tuple[datetime, datetime]:
    """
    Devuelve el rango de UTC para una fecha local.
    
    :param day: Fecha local (sin zona horaria)
    :param tz_name: Nombre de la zona horaria (default: Argentina)
    :return: (utc_start, utc_end)
    """
    local_tz = ZoneInfo(tz_name)
    
    local_start = datetime.combine(day, time.min, tzinfo=local_tz)
    local_end = datetime.combine(day, time.max, tzinfo=local_tz)

    utc_start = local_start.astimezone(ZoneInfo("UTC"))
    utc_end = local_end.astimezone(ZoneInfo("UTC"))

    return utc_start, utc_end