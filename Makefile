.PHONY: cleanup compile default dist install isclean pep test vimmodelines

PYTHON = python  # or python3
WHERE = ./exactonline
PYFILES = $(wildcard $(WHERE)/*.py)
DATAFILES = LICENSE.txt README.rst

default: cleanup vimmodelines pep compile test

dist: isclean $(PYFILES) $(DATAFILES)
	# sdist likes a reStructuredText README.txt
	#cp -n README.rst README.txt
	# do the sdist
	$(PYTHON) setup.py sdist
	##python setup.py register # only needed once
	#python setup.py sdist upload
	# clean up
	$(RM) MANIFEST
	#README.txt

install:
	$(PYTHON) setup.py install

isclean:
	# Check that there are no leftover unversioned python files.
	# If there are, you should clean it up.
	# (We check this, because the setup.py will include every .py it finds
	# due to its find_package_module() function.)
	! (git status | sed -e '1,/^# Untracked/d;/^#\t.*\.py$$/!d;s/^#\t/Untracked: /' | grep .)
	# These files should be created AND removed by the *-dist rules.
	test ! -f README.txt

cleanup:
	#$(RM) -r build
	find $(WHERE) -name '*.pyc' | \
	  xargs --no-run-if-empty -d\\n rm
	which pepclean >/dev/null && find $(WHERE) -name '*.py' | \
	  xargs --no-run-if-empty -d\\n pepclean

compile:
	$(PYTHON) -m compileall $(WHERE)

pep:
	@# Use a custom --format so the path is space separated for
	@# easier copy-pasting.
	find $(WHERE) -name '*.py' -print0 | \
          xargs --no-run-if-empty -0 $(PYTHON) -m flake8 \
            --max-line-length=99 --max-complexity=10 \
            --format='%(path)s %(row)d:%(col)d [%(code)s] %(text)s'

test: $(PYFILES)
	# Check RST, somewhat.
	$(PYTHON) setup.py check --restructuredtext --strict
	# Run tests on the rest.
	./test.sh

vimmodelines:
	find $(WHERE) -name '*.py' -size +0 '!' -perm -u=x -print0 | \
	  xargs --no-run-if-empty -0 grep -L '^# v''im:' | \
	  xargs --no-run-if-empty -d\\n \
	    sed -i -e '1i# vim: set ts=8 sw=4 sts=4 et ai tw=79:'
