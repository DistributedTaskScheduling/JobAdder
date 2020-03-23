all:
	gcc suid-python.c -o suid-python

install:
	cp suid-python /usr/bin
	chown root.root /usr/bin/suid-python
	chmod 755 /usr/bin/suid-python
	chmod u+s /usr/bin/suid-python
