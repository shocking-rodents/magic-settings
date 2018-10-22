REQUIREMENTS="requirements-dev.txt"
TAG="\n\n\033[0;32m\#\#\# "
END=" \#\#\# \033[0m\n"
APP_NAME=magic_settings


all: test


init: uninstall
	@echo $(TAG)Installing dev requirements$(END)
	pip install --upgrade -r $(REQUIREMENTS)

	@echo $(TAG)Installing package$(END)
	pip install --upgrade --editable .

	@echo

uninstall:
	@echo $(TAG)Uninstalling package$(END)
	- pip uninstall --yes $(APP_NAME) &2>/dev/null

	@echo "Verifying…"
	cd .. && ! python -m $(APP_NAME) --version &2>/dev/null

	@echo "Done"
	@echo

test: init
	@echo $(TAG)Running tests $(APP_NAME) the current Python interpreter with coverage $(END)
	py.test --cov ./$(APP_NAME) --cov ./tests  --verbose ./tests
	@echo


clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf htmlcov
	rm -rf dist
	rm -rf *.egg-info


.PHONY: all test clean