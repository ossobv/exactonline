.PHONY: default install cleanup compile test
PYFILES = $(wildcard exactonline/*.py)

default: cleanup compile test

install:
	python setup.py install

cleanup:
	find . -name '*.pyc' | \
	  xargs --no-run-if-empty -d\\n rm
	which pepclean >/dev/null && find . -name '*.py' | \
	  xargs --no-run-if-empty -d\\n pepclean

compile:
	python -m compileall exactonline

test: $(PYFILES)
	for py in $^; do echo "$$py TEST"; python "$$py"; done

