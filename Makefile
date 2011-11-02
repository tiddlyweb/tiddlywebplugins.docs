.PHONY: clean test all

all:

clean:
	find . -name "*.pyc" -exec rm {} \; || true
	rm -r store || true

test:
	py.test -x test

