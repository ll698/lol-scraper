DIR = $(shell pwd)

env:
	source lol-env/bin/activate;
server:
	jupyter notebook --notebook-dir="$(DIR)/notebooks";

install-deps:
	pip install -r requirements.txt;

init:
	make env;
	make install-deps;
	make server;

set_up:
	pip install virtualenv;
	python3 -m venv lol-env;
	make init;