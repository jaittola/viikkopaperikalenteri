
START_DATE=2024-12-23
END_DATE=2026-01-18
LOCALE=fi_FI

main: venv calendar.pdf

a6: venv calendar-a6.pdf

calendar.pdf: calendar.tex cal-days.tex
	lualatex calendar.tex

calendar-a6.pdf: calendar-a6.tex cal-days.tex
	lualatex calendar-a6.tex

cal-days.tex: weekdays.tex.template cal-week-template.tex.template cal-generator.py \
              important-days.schema.json important-days.json
	. ./venv/bin/activate && ./cal-generator.py -s $(START_DATE) -e $(END_DATE) -l $(LOCALE)

signatures: calendar.pdf
	lualatex signatures.tex

venv: requirements.txt
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt

clean:
	rm *.pdf *.log *.aux weekdays.tex cal-days.tex

.PHONY: clean main
