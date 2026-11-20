# Project 3 Makefile
#
# USAGE:
# make run ARGS="<username> <password>"

PYTHON = python3
SCRIPT = main.py
ARGS ?=

.PHONY: run
run:
	$(PYTHON) $(SCRIPT) $(ARGS)
