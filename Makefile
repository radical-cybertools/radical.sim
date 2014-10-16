
.PHONY: clean

clean:
	-rm -rf VERSION.git build/ temp/ MANIFEST dist/ src/*.egg-info src/radical/sim/VERSION src/radical/sim/VERSION.git pylint.out *.egg
	find . -name \*.pyc -exec rm -f {} \;
	find . -name \*.egg-info -exec rm -rf {} \;
