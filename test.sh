rm -rf ./src/test/remote/__init__.py
rm -rf ./src/test/ssh/__init__.py
rm -rf ./src/test/worker/__init__.py
rm -rf ./src/test/server/__init__.py
rm -rf ./src/test/proxy/__init__.py
rm -rf ./src/test/serializable/__init__.py
rm -rf ./src/test/user/__init__.py

cd src
PYTHONPATH=$(pwd) python3 -m unittest discover --verbose --start-directory ja_integration --pattern "*.py"
cd ..

touch ./src/test/proxy/__init__.py
touch ./src/test/serializable/__init__.py
touch ./src/test/user/__init__.py
touch ./src/test/server/__init__.py
touch ./src/test/worker/__init__.py
touch ./src/test/ssh/__init__.py
touch ./src/test/remote/__init__.py
