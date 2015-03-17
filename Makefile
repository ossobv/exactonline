.PHONY: cleanup compile default install pep test vimmodelines

PYFILES = $(wildcard exactonline/*.py)

default: cleanup vimmodelines pep compile test

install:
	python setup.py install

cleanup:
	find . -name '*.pyc' | \
	  xargs --no-run-if-empty -d\\n rm
	which pepclean >/dev/null && find . -name '*.py' | \
	  xargs --no-run-if-empty -d\\n pepclean

compile:
	python -m compileall exactonline

pep:
	@# Use a custom --format so the path is space separated for
	@# easier copy-pasting.
	find . -name '*.py' -print0 | \
          xargs --no-run-if-empty -0 flake8 \
            --max-line-length=99 --max-complexity=16 \
            --format='%(path)s %(row)d:%(col)d [%(code)s] %(text)s'

test: $(PYFILES)
	for py in $^; do echo "$$py TEST"; python "$$py" || exit 1; done

vimmodelines:
	find . -name '*.py' -size +0 '!' -perm -u=x -print0 | \
	  xargs --no-run-if-empty -0 grep -L '^# vim:' | \
	  xargs --no-run-if-empty -d\\n \
	    sed -i -e '1i# vim: set ts=8 sw=4 sts=4 et ai tw=79:'

#
#
#
