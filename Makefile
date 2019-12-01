all: gmodules uml doxygen

gmodules:
	git submodule update --init --recursive

uml:
	mkdir -p build
	./doctools/py-puml-tools/py2puml/py2puml.py -r src/ --recursive src/__init__.py -c ./doctools/py2puml.ini > build/project.puml
	mv py2puml.log build/py2puml.log
	plantuml docs/main.puml -o ../build/

doxygen:
	doxygen doctools/Doxyfile
	make --directory=./build/latex
