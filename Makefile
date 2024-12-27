
START_DATE=2024-12-23
END_DATE=2026-01-18
LATITUDE=60.187728
LONGITUDE=24.919004
TIMEZONE="Europe/Helsinki"
LOCALE=fi_FI
DATEFORMAT="%d.%m"
# LUNAR_PHASES=lunar-phases-2025.json

ifdef LUNAR_PHASES
MOONDATA=moondata.json
MOONDATA_ARG=-M $(MOONDATA)
WITHMOON=1
else
WITHMOON=0
endif

main: venv suntimes calendar.pdf

a6: venv suntimes calendar-a6.pdf

calendar.pdf: calendar.tex cal-days.tex
	lualatex calendar.tex

calendar-a6.pdf: calendar-a6.tex cal-days.tex
	lualatex "\def\withmoon{$(WITHMOON)} \input calendar-a6.tex"

cal-days.tex: weekdays.tex.template cal-week-template.tex.template cal-generator.py \
              important-days.schema.json important-days.json
	. ./venv/bin/activate && ./cal-generator.py -s $(START_DATE) -e $(END_DATE) -l $(LOCALE)

signatures: calendar.pdf
	lualatex signatures.tex

venv: requirements.txt
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt

ifdef MOONDATA
$(MOONDATA): $(LUNAR_PHASES) lunar-phasedata-conv.py venv
	./lunar-phasedata-conv.py $(LUNAR_PHASES) > $(MOONDATA)
endif

suntimes: daylength.py venv $(MOONDATA)
	./daylength.py -s $(START_DATE) -e $(END_DATE) -l $(LOCALE) -a $(LATITUDE) -o $(LONGITUDE) -z $(TIMEZONE) -f $(DATEFORMAT) $(MOONDATA_ARG) > daylengths.tex

clean:
	rm -f *.pdf *.log *.aux weekdays.tex cal-days.tex daylengths.tex moondata.json

.PHONY: clean main suntimes
