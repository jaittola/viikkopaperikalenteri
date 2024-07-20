#!/usr/bin/env python3

import datetime
import argparse
import locale
import itertools
import pprint
import string
import pathlib

parser = argparse.ArgumentParser(
    prog='cal-generator',
    description='Generate a TeX calendar',
    epilog='')
parser.add_argument('-l', '--locale')
parser.add_argument('-s', '--start_date', required=True)
parser.add_argument('-e', '--end_date', required=True)
parser.add_argument('-o', '--output', default='cal-days.tex')
parser.add_argument('-w', '--weekdays_output', default='weekdays.tex')

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


def generate_calendar(cal_data_by_week):
    week_template = get_template("cal-week-template.tex.template")

    with open(args.output, "w") as cal_output:
        for w in cal_data_by_week:
            days = w['days']
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
                'sun_dayofmonth': days[6]['dayofmonth']
            }

            cal_output.writelines(week_template.substitute(wd))


cal_data_by_week = generate_calendar_days(startdate, enddate)
generate_weekdays(cal_data_by_week[0])
generate_calendar(cal_data_by_week)
