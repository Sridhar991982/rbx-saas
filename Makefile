CSS_DIR=rbx/static/css

all: style

style: bs-style bs-resp-style rbx-style

rbx-style:
	recess --compile $(CSS_DIR)/rbx.less > $(CSS_DIR)/rbx.css
	recess --compress $(CSS_DIR)/rbx.css > $(CSS_DIR)/rbx.min.css

bs-style:
	recess --compile  $(CSS_DIR)/bootstrap.less > $(CSS_DIR)/bootstrap.css
	recess --compress  $(CSS_DIR)/bootstrap.css > $(CSS_DIR)/bootstrap.min.css

bs-resp-style:
	recess --compile $(CSS_DIR)/responsive.less > $(CSS_DIR)/bootstrap-responsive.css
	recess --compress $(CSS_DIR)/bootstrap-responsive.css > $(CSS_DIR)/bootstrap-responsive.min.css

run:
	@python manage.py runserver

watch:
	watchr -e "watch('$(CSS_DIR)/.*\.less') { system 'make' }"

clean:
	find -name "*.pyc" -exec rm {} \;
