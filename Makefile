# Para Windows -> (set ENV_FILE_LOCATION=./.env)

gen_doc:
	pip install eralchemy
	eralchemy -i sqlite:///core/attendance.db -o doc/DER_SQlite.pdf
	pip install pipreqs
	pipreqs ./ --force

install:
	pip install -r requirements.txt
	pip install marshmallow-sqlalchemy
	pip install pytest-coverage pytest-sugar

init_db:
	cd core;\
	python config.py

test:
	export ENV_FILE_LOCATION=./.env;\
	FLASK_ENV=test pytest --cov-report xml --cov=APIs tests/

run:
	export ENV_FILE_LOCATION=./.env;\
	FLASK_APP=core/run.py FLASK_ENV=development python core/run.py