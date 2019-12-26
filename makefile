DIR = $(shell pwd)
include key
export $(shell sed 's/=.*//' key)

init:
	pip install virtualenv;
	python -m venv lol-env;
	( \
		source lol-env/bin/activate; \
		pip install -r lolcrawler/requirements.txt --no-cache-dir; \
    	pip install lolcrawler/; \
    	pip install ipykernel; \
    	python -m ipykernel install --user --name=lol-env; \
    	jupyter notebook --notebook-dir="$(DIR)/notebooks"; \
    )
