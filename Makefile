
main: calendar.pdf

calendar.pdf: calendar.tex weekdays.tex.template cal-week-template.tex.template cal-generator.py
	./cal-generator.py -s 2024-07-15 -e 2025-01-05 -l fi_FI
	lualatex calendar.tex

signatures: calendar.pdf
	lualatex signatures.tex

clean:
	rm *.pdf *.log *.aux weekdays.tex cal-days.tex

.PHONY: clean main
