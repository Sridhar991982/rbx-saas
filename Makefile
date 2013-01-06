CSS_DIR=public/static/css
JS_DIR=public/static/js

all: style js

style: bs-style bs-resp-style rbx-style

js: rbx-js

rbx-style:
	recess --compile $(CSS_DIR)/rbx.less > $(CSS_DIR)/rbx.css
	recess --compress $(CSS_DIR)/rbx.css > $(CSS_DIR)/rbx.min.css
	rm $(CSS_DIR)/rbx.css

bs-style:
	recess --compile  $(CSS_DIR)/bootstrap.less > $(CSS_DIR)/bootstrap.css
	recess --compress  $(CSS_DIR)/bootstrap.css > $(CSS_DIR)/bootstrap.min.css
	rm $(CSS_DIR)/bootstrap.css

bs-resp-style:
	recess --compile $(CSS_DIR)/responsive.less > $(CSS_DIR)/bootstrap-responsive.css
	recess --compress $(CSS_DIR)/bootstrap-responsive.css > $(CSS_DIR)/bootstrap-responsive.min.css
	rm $(CSS_DIR)/bootstrap-responsive.css

rbx-js:
	uglifyjs $(JS_DIR)/rbx.js -o $(JS_DIR)/rbx.min.js -c

run:
	@PYTHONPATH=./lib:$PYTHONPATH python manage.py runserver

watch:
	watchr -e "watch('$(CSS_DIR)/.*\.less') { system 'make' }"

clean:
	find -name "*.pyc" -exec rm {} \;
