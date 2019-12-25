init:
	source lol-env/bin/activate;
	pip install -r requirements.txt;
	jupyter notebook

make server
	source lol-env/bin/activate;
	jupyter notebook;

make install-deps:
	pip install -r requirements.txt;

set_up:
	pip install virtualenv;
	python3 -m venv lol-env;
	source lol-env/bin/activate;
	pip install -r requirements.txt;
	jupyter notebook;