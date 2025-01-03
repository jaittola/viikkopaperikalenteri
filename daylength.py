#!/usr/bin/env python3

# Based on https://en.wikipedia.org/wiki/Sunrise_equation

import logging
from datetime import datetime, timedelta, timezone, tzinfo, date
from zoneinfo import ZoneInfo
from math import acos, asin, ceil, cos, degrees, fmod, radians, sin, sqrt, modf
from time import time
import argparse
import locale
import pathlib
import json

log = logging.getLogger()


def _ts2human(ts: int | float, debugtz: tzinfo | None) -> str:
    return str(datetime.fromtimestamp(ts, debugtz))


def j2ts(j: float | int) -> float:
    return (j - 2440587.5) * 86400


def ts2j(ts: float | int) -> float:
    return ts / 86400.0 + 2440587.5


def _j2human(j: float | int, debugtz: tzinfo | None) -> str:
    ts = j2ts(j)
    return f'{ts} = {_ts2human(ts, debugtz)}'


def _deg2human(deg: float | int) -> str:
    x = int(deg * 3600.0)
    num = f'∠{deg:.3f}°'
    rad = f'∠{radians(deg):.3f}rad'
    human = f'∠{x // 3600}°{x // 60 % 60}′{x % 60}″'
    return f'{rad} = {human} = {num}'


def _tohms(hours: float | int) -> str:
    (h_fraction, hours_full) = modf(hours)
    minutes = h_fraction * 60.0
    (m_fraction, minutes_full) = modf(minutes)
    s_rounded = round(m_fraction * 60.0)
    return f'{int(hours_full)}:{minutes_full:02.0f}:{s_rounded:02d}'


def calc(
        current_timestamp: float,
        f: float,
        l_w: float,
        elevation: float = 0.0,
        *,
        debugtz: tzinfo | None = None,
) -> tuple[float, float, None] | tuple[None, None, bool]:
    log.debug(f'Latitude               f       = {_deg2human(f)}')
    log.debug(f'Longitude              l_w     = {_deg2human(l_w)}')
    log.debug(
        f'Now                    ts      = {_ts2human(current_timestamp, debugtz)}')

    J_date = ts2j(current_timestamp)
    log.debug(f'Julian date            j_date  = {J_date:.3f} days')

    # Julian day
    # TODO: ceil ?
    n = ceil(J_date - (2451545.0 + 0.0009) + 69.184 / 86400.0)
    log.debug(f'Julian day             n       = {n:.3f} days')

    # Mean solar time
    J_ = n + 0.0009 - l_w / 360.0
    log.debug(f'Mean solar time        J_      = {J_:.9f} days')

    # Solar mean anomaly
    # M_degrees = 357.5291 + 0.98560028 * J_  # Same, but looks ugly
    M_degrees = fmod(357.5291 + 0.98560028 * J_, 360)
    M_radians = radians(M_degrees)
    log.debug(f'Solar mean anomaly     M       = {_deg2human(M_degrees)}')

    # Equation of the center
    C_degrees = 1.9148 * sin(M_radians) + 0.02 * \
        sin(2 * M_radians) + 0.0003 * sin(3 * M_radians)
    # The difference for final program result is few milliseconds
    # https://www.astrouw.edu.pl/~jskowron/pracownia/praca/sunspot_answerbook_expl/expl-4.html
    # e = 0.01671
    # C_degrees = \
    #     degrees(2 * e - (1 / 4) * e ** 3 + (5 / 96) * e ** 5) * sin(M_radians) \
    #     + degrees(5 / 4 * e ** 2 - (11 / 24) * e ** 4 + (17 / 192) * e ** 6) * sin(2 * M_radians) \
    #     + degrees(13 / 12 * e ** 3 - (43 / 64) * e ** 5) * sin(3 * M_radians) \
    #     + degrees((103 / 96) * e ** 4 - (451 / 480) * e ** 6) * sin(4 * M_radians) \
    #     + degrees((1097 / 960) * e ** 5) * sin(5 * M_radians) \
    #     + degrees((1223 / 960) * e ** 6) * sin(6 * M_radians)

    log.debug(f'Equation of the center C       = {_deg2human(C_degrees)}')

    # Ecliptic longitude
    # L_degrees = M_degrees + C_degrees + 180.0 + 102.9372  # Same, but looks ugly
    L_degrees = fmod(M_degrees + C_degrees + 180.0 + 102.9372, 360)
    log.debug(f'Ecliptic longitude     L       = {_deg2human(L_degrees)}')

    Lambda_radians = radians(L_degrees)

    # Solar transit (julian date)
    J_transit = 2451545.0 + J_ + 0.0053 * \
        sin(M_radians) - 0.0069 * sin(2 * Lambda_radians)
    log.debug(
        f'Solar transit time     J_trans = {_j2human(J_transit, debugtz)}')

    # Declination of the Sun
    sin_d = sin(Lambda_radians) * sin(radians(23.4397))
    # cos_d = sqrt(1-sin_d**2) # exactly the same precision, but 1.5 times slower
    cos_d = cos(asin(sin_d))

    # Hour angle
    some_cos = (sin(radians(-0.833 - 2.076 * sqrt(elevation) / 60.0)
                    ) - sin(radians(f)) * sin_d) / (cos(radians(f)) * cos_d)
    try:
        w0_radians = acos(some_cos)
    except ValueError:
        return None, None, some_cos > 0.0
    w0_degrees = degrees(w0_radians)  # 0...180

    log.debug(f'Hour angle             w0      = {_deg2human(w0_degrees)}')

    j_rise = J_transit - w0_degrees / 360
    j_set = J_transit + w0_degrees / 360
    daylen = w0_degrees / (180 / 24)

    log.debug(f'Sunrise                j_rise  = {_j2human(j_rise, debugtz)}')
    log.debug(f'Sunset                 j_set   = {_j2human(j_set, debugtz)}')
    log.debug(
        f'Day length                       {w0_degrees / (180 / 24):.3f} hours')

    return {"rise": j2ts(j_rise), "set": j2ts(j_set), "daylen": daylen}


def get_moondata(filename) -> dict:
    moondata = pathlib.Path(filename).read_text()
    return json.loads(moondata)


def get_moonphase(ts: datetime, moondata: dict | None) -> str:
    if moondata == None:
        return ""

    d = ts.date().isoformat()
    md_day = moondata.get(d)

    if md_day:
        sym = md_day.get("c", "")
        return f'& \\moonsym{{{sym}}}' if sym else "& "
    else:
        return "& "


def main():
    logging.basicConfig(level=logging.DEBUG)
    latitude = 60.187728
    longitude = 24.919004
    elevation = 0
    print(calc(time(), latitude, longitude, elevation,
          debugtz=ZoneInfo("Europe/Helsinki")))


def main2():
    parser = argparse.ArgumentParser(prog='daylength',
                                     description='Generate sunrise and sunset times',
                                     epilog='')
    parser.add_argument('-l', '--locale')
    parser.add_argument('-s', '--start_date', required=True)
    parser.add_argument('-e', '--end_date', required=True)
    parser.add_argument('-a', '--latitude', default=60.187728, type=float)
    parser.add_argument('-o', '--longitude', default=24.919004, type=float)
    parser.add_argument('-g', '--elevation', default=0, type=float)
    parser.add_argument('-z', '--timezone', default='Europe/Helsinki')
    parser.add_argument('-m', '--oldmain', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--dateformat', default='%x')
    parser.add_argument('-M', '--moondata')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.locale:
        locale.setlocale(locale.LC_TIME, args.locale)

    # datetime.date(2024, 7, 15)
    startdate = date.fromisoformat(args.start_date)
    # datetime.date(2024, 12, 31)
    enddate = date.fromisoformat(args.end_date)

    daycount = (enddate - startdate).days + 1
    dayrange = range(0, daycount)

    tz = ZoneInfo(args.timezone)

    dates = [date.fromordinal(startdate.toordinal() + i) for i in dayrange]

    moondata = None
    if args.moondata:
        moondata = get_moondata(args.moondata)

    log.debug(f'Dates = {dates}')

    if args.oldmain:
        main()
    else:
        for d in dates:
            ts = datetime(year=d.year,
                          month=d.month,
                          day=d.day,
                          hour=12,
                          tzinfo=tz)
            times = calc(ts.timestamp(), args.latitude,
                         args.longitude, args.elevation, debugtz=tz)
            rise = datetime.fromtimestamp(times["rise"])
            setting = datetime.fromtimestamp(times["set"])
            extraspace = "[0.2cm]" if ts.weekday() == 6 else ""
            moonphase = get_moonphase(ts, moondata)

            print(
                f'{ts.strftime("%a")} & {ts.strftime(args.dateformat)} & {rise.strftime("%R")} & {setting.strftime("%R")} & {_tohms(times["daylen"])} {moonphase}\\\\{extraspace}')


if __name__ == '__main__':
    main2()
