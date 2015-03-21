first: all

all:

test:
	python3 -m unittest discover -v tests/ 'test_*.py'

pep8:
	find . -name '*.py' -exec pep8 -r {} \;
