.PHONY: README

all: README handlebars

README:
	pandoc --from=markdown --to=rst --output=README README.md

include trapdoor/Makefile.inc

