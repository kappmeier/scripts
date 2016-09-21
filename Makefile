SRC_DIR=.

all: clean sloc test flakes lint

sloc:
	sloccount --duplicates --wide --details $(SRC_DIR) | fgrep -v -e .git -e sloccount.sc -e .xml > sloccount.sc || :

test:
	cd $(SRC_DIR) && nosetests --verbose --with-xunit --xunit-file=xunit.xml --with-coverage --xcoverage-file=coverage.xml || :

flakes:
	find $(SRC_DIR) -name *.py|egrep -v '^./tests/'|xargs pyflakes > pyflakes.out || :

lint:
	find $(SRC_DIR) -name *.py|egrep -v '^./tests/' | xargs pylint3 --output-format=parseable --reports=y > pylint.out || :


clean:
	rm -f sloccount.sc
	rm -f coverage.xml
	rm -f xunit.xml
	rm -f pyflakes.out
	rm -f pylint.out
