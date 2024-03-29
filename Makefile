.PHONY: clean test all dist release pypi

all:

clean:
	find . -name "*.pyc" -exec rm {} \; || true
	rm -r store || true
	rm -r dist || true
	rm -r build || true
	rm -r *.egg-info || true

test:
	py.test -x test

dist: test
	python setup.py sdist

release: clean pypi

pypi: test
	python setup.py sdist upload
