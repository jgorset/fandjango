test:
	./manage.py test

release:
	python setup.py sdist register upload
