
.PHONY: pypi help test

# The stuff below implements an auto help feature
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:   ## Show help for avaiable targets
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


testpypi: README.rst  ## Push project to pypi
	 python3 -m build && twine upload -r testpypi dist/*

pypi: README.rst  ## Push project to pypi
	 python3 -m build && twine upload dist/*

README.rst: README.org  ## Create README.rst from README.org
	pandoc --from=org --to=rst --output=README.rst README.org


check:  ## Check everything wokrs
	pylint oxlab
	pytype oxlab


