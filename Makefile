all: js

js:
	coffee -b -c -o frontend/js/ frontend/coffee/

watch:
	coffee -b -w -c -o frontend/js/ frontend/coffee/
