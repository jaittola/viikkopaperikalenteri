
main:
	./cal-generator.py -s 2024-07-15 -e 2024-07-21 -l fi_FI
	lualatex calendar.tex

clean:
	rm *.pdf *.log *.aux weekdays.tex cal-days.tex

.PHONY: clean main
