

test: 
	echo "Hello World"

create_resourse: 
	cd assets/ && pyrcc5 resourse.qrc -o resource_rc.py

create_ui:
	echo 'Generating interface UI .py file'
	pyuic5 -x interface.ui -o interface.py 

run: 
	python3 app.py

clean: 
	echo "Clearing Cache"
	-rm -rf __pycache__ 