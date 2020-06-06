test:
	DJANGO_SETTINGS_MODULE=tests.project.settings nosetests --nologcapture

release:
	python setup.py sdist register upload
