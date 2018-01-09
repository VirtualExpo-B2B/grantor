#
# Makefile for grantor
#

# installs to $DESTDIR
install:
	install -m 755 -d $(DESTDIR)
	install -m 755 grantor.py $(DESTDIR)/grantor.py
	install -m 644 -t $(DESTDIR)/helpers helpers
	install -m 644 -t $(DESTDIR)/data data

