# PDF calendar generator

## Introduction

This repository contains a Python script and LaTeX template files for
generating traditional printable paper calendars.

Each week is laid out on a spread of two pages. The first day of
week in the layout is Monday.

There are two variations of the layout:

 * An A5 layout with hourly time slots
 * A simpler A6 layout without the time slots

[![Sample spread of the A5 calendar](readme-images/sample-spread.png)](readme-images/sample-spread.pdf)

[![Sample spread of the A6 calendar](readme-images/sample-spread-a6.png)](readme-images/sample-spread-a6.pdf)

## Installation and use

### Requirements

1. Install [TeX Live](https://tug.org/texlive/), Python 3, and GNU Make on your computer. Use the appropriate packaging system depending on your operating system.
1. Run `make venv` to set up a [Python venv](https://docs.python.org/3/library/venv.html) for the calendar generator script.

### Creating the calendar

To create a calendar with A5-sized pages,

1. Run `make`
1. If the command succeeds, `calendar.pdf` contains the generated calendar file.

To create a calendar with A6-sized pages,

1. Run `make a6`
1. If the command succeeds, `calendar-a6.pdf` contains the generated calendar file.

To change the language or time range of the calendar, or to otherwise change the output, see [Customisation](#Customisation) below.

### Sunrise and sunset times, and lunar phase data in the A6 calendar

The A6 sized calendar contains pages that list the sunrise and sunset
times for one location. In addition, the pages can optionally show the
lunar phase.

The sunset and sunrise times are generated with a script. To set the
location for the sunset and sunrise times, edit `LATITUDE`,
`LONGITUDE`, `TIMEZONE` and possibly also `DATEFORMAT` in Makefile.

The lunar phase data has to be obtained from an external
source. You can get suitable data from the [Astronomical Applications API of the
Astronomical Applications Department of the U.S. Naval
Observatory](https://aa.usno.navy.mil/data/api).

To include lunar phases in the calendar,

1. Obtain the lunar phase data by running, for example, `curl -vvv 'https://aa.usno.navy.mil/api/moon/phases/year?year=2025' > lunar-phases-2025.json`
1. In `Makefile`, uncomment `LUNAR_PHASES` and point it to the lunar phase data file. For example, `LUNAR_PHASES=lunar-phases-2025.json`.

Finally, generate the A6 calendar.

Note that the calendar template uses the "Arial Unicode MS" font to
render the moon phase symbols. That font exists by default on macOS
but not necessarily on other operating systems. You can change it
in `calendar-a6.tex`, if needed.

### Creating folios (or signatures or gatherings, whichever term you want to use) of the A5 sized calendar for bookbinding

To create a PDF file containing 5-sheet signatures suitable for binding the A5-sized calendar into a book,

1. Run `make signatures`
2. `signatures.pdf` contains now the calendar in a printable signature format.

Note that in typical A4 printer paper the grain runs across the long
end of the sheet. If you fold these sheets in half, the grain
direction is wrong for bookbinding. The other obvious option would be
printing the calendar on A3 paper with four pages per side of sheet
(i.e., quartos) and folding them twice to obtain A5 pages.
Unfortunately, most A3 paper is short grain, which again leaves you
with incorrect grain direction.

Hence, you should either try to find short-grain A4 paper or
long-grain A3 paper to obtain good results for your calendar bound
into a book.

### Creating quartos and other large sheets for printing

If you want to create [quartos](https://en.wikipedia.org/wiki/Quarto)
or other large-format prints of this calendar, one option is
[bookbinder-js](https://momijizukamori.github.io/bookbinder-js).

I have used [these
settings for bookbinder-js](https://momijizukamori.github.io/bookbinder-js/?pageLayout=quarto&customSigLength=0&rotatePage=true&flyleafs=0&sigLength=3&printFile=aggregated&paperSize=A4)
to print the A6 calendar onto A4 paper with four pages on each sheet.

Other options for converting PDFs into signatures include Adobe
Acrobat (you need the commercial version, the free Acrobat Reader
isn't enough) or [https://bookbinder.app/](https://bookbinder.app/).

## The structure of this calendar generator

The calendar generator consists of the following components:

* [cal-generator.py](cal-generator.py): A python script for generating the calendar.
* [calendar.tex](calendar.tex) and [calendar-a6.tex](calendar-a6.tex): The main LaTex files for the calendar, which contain the LaTeX document and functions for laying out the pages. To customise or change the layout, you'll have to edit these files.
* [important-days.json](important-days.json): A JSON file containing holidays and other important days that you want to print into the calendar.
* [important-days.schema.json](important-days.schema.json): A JSON schema file to help with checking the format of important-days.json.
* [requirements.txt](requirements.txt): PIP input file for installing Python libraries.
* [cal-week-template.tex.template](cal-week-template.tex.template) and [weekdays.tex.template](weekdays.tex.template): template files used by cal-generator.py to create the calendar.
* [signatures.tex](signatures.tex): A LaTeX document for creating gatherings (or signatures) suitable for bookbinding.
* [Makefile](Makefile): a makefile containing the commands for generating the calendar.
* [lunar-phasedata-conv.py](lunar-phasedata-conv.py): A Python script for converting the lunar phase data from US Naval Observatory.
* [daylength.py](daylength.py): A Python script for generating the sunrise & sunset & lunar phase table.

## Customisation

This calendar generator can be customised in a limited way.

### Start & end dates

To change the first and last date of the calendar, change
`START_DATE` and `END_DATE` in [Makefile](Makefile).

Note that `START_DATE` must be a Monday and `END_DATE` must be a Sunday.

### Language

[Makefile](Makefile) contains some variables that affect the language
and date formatting.

1. To change the language for week days and month names, change `LOCALE`.
1. To change the date format in the sunrise & sunset table, change `DATEFORMAT`

In their current form, the calendar files and templates contain some
hard-coded texts in Finnish. To create a calendar in another language,
you'll just have to find and change those phrases.

### Important days

The file [important-days.json](important-days.json) contains an array
of holidays and other days of importance that are printed into the
calendar. There is also a JSON schema
([important-days.schema.json](important-days.schema.json)) file used
by the calendar generator to verify the format of
[important-days.json](important-days.json).

The days in [important-days.json](important-days.json) have the following fields:

* `date`: The date in YYYY-MM-DD format.
* `name`: The text to be written into the calendar. The calendar template has three rows of fixed space for this text, so keep the text short.
* `isHoliday`: If `true`, the date is printed in red. All Sundays are printed in red by default.
* `flag`: An identifier for a flag to be printed into the calendar to mark a [flag flying day](https://en.wikipedia.org/wiki/Flag_flying_day). A corresponding image file must be present in the `images` directory with file name `images/flag_[identifier].pdf`.

[important-days.json](important-days.json) contains the Finnish
holidays and flag flying days based on information from
<https://almanakka.helsinki.fi/liputus-ja-juhlapaivat/>,
<https://intermin.fi/suomen-lippu/liputuspaivat> and
[https://www.juhlapyhät.fi](https://www.xn--juhlapyht-22a.fi/).

### Sunrise & Sunset and the lunar phases

To change the location for the sunrise and sunset times, change
`LATITUDE`, `LONGITUDE`, and `TIMEZONE` in [Makefile](Makefile).

The name of the location (by default Helsinki) is embedded in the
heading text in [calendar-a6.tex](calendar-a6.tex).

### Other more extensive customisations

To further modify the calendar (e.g., to start the weeks on Sundays,
or to otherwise modify the layout), you'll have to figure out how the
[calendar generator](./cal-generator.py) and the [calendar
templates](./calendar.tex) work. [calendar.tex](calendar.tex) is
implemented in relatively simple LaTeX, but it is rather long, tedious
and somewhat awkward in places. Changing it will be fiddly.

## License

[![Creative Commons Public Domain
badge](readme-images/cc-publicdomain.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

© 2024. This work is openly licensed via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
