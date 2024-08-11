#!/usr/bin/env python3

import datetime
import argparse
import locale
import itertools
import pprint
import string
import pathlib
import json
import jsonschema

parser = argparse.ArgumentParser(
    prog='cal-generator',
    description='Generate a TeX calendar',
    epilog='')
parser.add_argument('-l', '--locale')
parser.add_argument('-s', '--start_date', required=True)
parser.add_argument('-e', '--end_date', required=True)
parser.add_argument('-o', '--output', default='cal-days.tex')
parser.add_argument('-w', '--weekdays_output', default='weekdays.tex')
parser.add_argument('-c', '--important_days_schema', default='important-days.schema.json')
parser.add_argument('-d', '--important_days', default='important-days.json')

args = parser.parse_args()

if args.locale:
    locale.setlocale(locale.LC_TIME, args.locale)

startdate = datetime.date.fromisoformat(args.start_date)   # datetime.date(2024, 7, 15)
enddate = datetime.date.fromisoformat(args.end_date)       # datetime.date(2024, 12, 31)

if startdate.isoweekday() != 1 or enddate.isoweekday() != 7:
    print("Start date should be a monday and end date a sunday")
    exit(1)

def to_caldata(calendardate):
    return { 'date': calendardate,  # year, month, day
             'isodate': calendardate.isoformat(),
             'year': calendardate.year,
             'month': calendardate.month,
             'dayofmonth': calendardate.day,
             'weekday': calendardate.isoweekday(),
             'day_name': calendardate.strftime("%A"),
             'month_name': calendardate.strftime("%B"),
             'weeknum': calendardate.isocalendar()[1] }


def generate_calendar_days(startdate, enddate):
    daycount = (enddate - startdate).days + 1
    dayrange = range(0, daycount)

    calendardates = [ datetime.date.fromordinal(startdate.toordinal() + i) for i in dayrange]

    cal_data_by_week = []
    for wn, days in itertools.groupby(map(to_caldata, calendardates), lambda d: d['weeknum']):
        daylist = list(days)
        cal_data_by_week.append({ 'week': wn,
                                  'month_name': daylist[0]['month_name'],
                                  'year': daylist[0]['year'],
                                  'days': daylist })

    pprint.pprint(cal_data_by_week)

    return cal_data_by_week


def get_template(path):
    template_path = pathlib.Path(path)
    template_contents = template_path.read_text()
    template = string.Template(template_contents)

    return template


def generate_weekdays(cal_data_week):
    weekdays_template = get_template("weekdays.tex.template")
    days = cal_data_week['days']
    daynames = {
        'mon_name': days[0]['day_name'],
        'tue_name': days[1]['day_name'],
        'wed_name': days[2]['day_name'],
        'thu_name': days[3]['day_name'],
        'fri_name': days[4]['day_name'],
        'sat_name': days[5]['day_name'],
        'sun_name': days[6]['day_name'],
    }

    with open(args.weekdays_output, "w") as output:
        output.writelines(weekdays_template.substitute(daynames))


def generate_calendar(cal_data_by_week, important_days):
    week_template = get_template("cal-week-template.tex.template")

    with open(args.output, "w") as cal_output:
        for w in cal_data_by_week:
            days = w['days']

            wd_range = range(0, 7)

            week_important_days = [important_days.get(days[i]['isodate']) for i in wd_range]
            week_events = [week_important_days[i]['name'] if week_important_days[i] is not None else "" for i in wd_range]

            week_flags = [week_important_days[i].get("flag", "") if week_important_days[i] is not None else "" for i in wd_range]

            week_holidays = [str(i + 1) if i == 6 or (week_important_days[i] is not None and week_important_days[i].get('isHoliday')) else "" for i in wd_range]
            week_holidays_str = "".join(week_holidays)

            wd = {
                'month_name': w['month_name'],
                'weeknum': w['week'],
                'year': w['year'],

                'mon_dayofmonth': days[0]['dayofmonth'],
                'tue_dayofmonth': days[1]['dayofmonth'],
                'wed_dayofmonth': days[2]['dayofmonth'],
                'thu_dayofmonth': days[3]['dayofmonth'],
                'fri_dayofmonth': days[4]['dayofmonth'],
                'sat_dayofmonth': days[5]['dayofmonth'],
                'sun_dayofmonth': days[6]['dayofmonth'],

                'mon_event': week_events[0],
                'tue_event': week_events[1],
                'wed_event': week_events[2],
                'thu_event': week_events[3],
                'fri_event': week_events[4],
                'sat_event': week_events[5],
                'sun_event': week_events[6],

                'mon_flag': week_flags[0],
                'tue_flag': week_flags[1],
                'wed_flag': week_flags[2],
                'thu_flag': week_flags[3],
                'fri_flag': week_flags[4],
                'sat_flag': week_flags[5],
                'sun_flag': week_flags[6],

                'holidays': week_holidays_str,
            }

            cal_output.writelines(week_template.substitute(wd))

def read_important_days():
    schema_text = pathlib.Path(args.important_days_schema).read_text()
    schema = json.loads(schema_text)

    important_days_text = pathlib.Path(args.important_days).read_text()
    important_days = json.loads(important_days_text)

    try:
        jsonschema.validate(instance=important_days, schema=schema)
        days = important_days["days"]
        important_days_dict = {days[i]["date"]: days[i] for i in range(len(days))}
        return important_days_dict
    except Exception as error:
        print("Validating important days failed")
        print(error)
        exit(2)


important_days = read_important_days()
cal_data_by_week = generate_calendar_days(startdate, enddate)
generate_weekdays(cal_data_by_week[0])
generate_calendar(cal_data_by_week, important_days)
