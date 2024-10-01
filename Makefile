help:			##Shows help
	@cat makefile | grep "##." | sed '2d;s/##//;s/://'

DATABASE_DIR = database/
DATABASE_SOURCE = database/database.py

database:		##Use database
	@python3 $(DATABASE_SOURCE)

run:
	@python3 -m main