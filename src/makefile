test: 
	echo "Hello World"

create_resourse: 
	cd assets/ && pyrcc5 resourse.qrc -o resourse_rc.py

create_ui:
	echo 'Generating interface UI .py file'
	pyuic5 -x ui/interface.ui -o interface.py 
	tac interface.py | sed '1,11d' | tac > interface_temp.py
	mv interface_temp.py interface.py 

run: 
	python3 setup.py

create: 
	pyinstaller app.spec 

clean: 
	echo "Clearing Cache"
	-rm -rf __pycache__ 
