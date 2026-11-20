#
#      File Name  : Makefile
#      Function   : make comc library
#$     History    :
#$     1994/11/18 : library install directory
#$     1994/10/31 : crank in
#
#

CC = gcc

COMCLIBDIR = ../../bin

DEBUGFLAG = -DNETDEBUG

CFLAGS = -O
#CFLAGS = -g $(DEBUGFLAG)

SRCS =	comerrs.c rbuf.c sbuf.c rcom.c scom.c socacc.c\
	client.c server.c comdebug.c smes.c mesfree.c

OBJS =	comerrs.o rbuf.o sbuf.o rcom.o scom.o socacc.o\
	client.o server.o comdebug.o smes.o mesfree.o

.c.o:
	$(CC) $(CFLAGS) -c $<

COMCLIB = libcomc.a

all : $(COMCLIB)

$(COMCLIB) : $(OBJS)
	ar rcvl $(COMCLIBDIR)/$@ $?
	ranlib $(COMCLIBDIR)/$@

clean:
	rm -f core $(OBJS) $(COMCLIB)
