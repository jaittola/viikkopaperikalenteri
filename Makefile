
main: venv calendar.pdf

calendar.pdf: calendar.tex cal-days.tex
	lualatex calendar.tex

cal-days.tex: weekdays.tex.template cal-week-template.tex.template cal-generator.py \
              important-days.schema.json important-days.json
	. ./venv/bin/activate && ./cal-generator.py -s 2024-08-05 -e 2026-01-18 -l fi_FI

signatures: calendar.pdf
	lualatex signatures.tex

venv: requirements.txt
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt

clean:
	rm *.pdf *.log *.aux weekdays.tex cal-days.tex

.PHONY: clean main
