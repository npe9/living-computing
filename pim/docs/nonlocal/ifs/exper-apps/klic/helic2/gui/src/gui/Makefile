CC                  = gcc
RM                  = rm -f

CDEBUGFLAGS         = -g

DEFINES             = 
BIN_DIR		    = ../../bin
COMC_DIR	    = ../comc
STD_DEFINES         = 
INCLUDES            = -I. -I$(COMC_DIR) -I/usr/openware/include
LOCAL_LIBRARIES     = -L. -L/usr/openware/lib -L$(BIN_DIR) -lMrm -lXm -lXt -lXext -lX11
SYS_LIBS	    =

CFLAGS              = $(INCLUDES) $(STD_DEFINES) $(DEFINES)

SRCS=	main.c\
	initwin.c\
	util.c\
	dbtwin.c\
	viewset.c\
	guicom.c\
	driver.c\
	argmove.c\
	unit.c\
	goal.c\
	drs.c

OBJS=	main.o\
	initwin.o\
	util.o\
	dbtwin.o\
	viewset.o\
	guicom.o\
	driver.o\
	argmove.o\
	unit.o\
	goal.o\
	drs.o

.c.o: gui.h $(COMC_DIR)/commands.h $(COMC_DIR)/messages.h $(COMC_DIR)/comtypes.h
	$(RM) $@
	$(CC) -c $(CFLAGS) $<

all: $(OBJS) $(BIN_DIR)/libcomc.a
	$(RM) $(BIN_DIR)/gui
	$(CC) -o $(BIN_DIR)/gui $(OBJS) $(LOCAL_LIBRARIES) -lcomc $(SYSLIBS) 

main.o: main.c 
initwin.o : initwin.c 
util.o : util.c dbt.h
dbtwin.o : dbtwin.c dbt.h err.h dbtwin.h 
viewset.o : viewset.c dbt.h 
guicom.o : guicom.c 
driver.o : driver.c  dbt.h dbtwin.h err.h
argmove.o : argmove.c dbt.h err.h
unit.o : unit.c 
goal.o : goal.c err.h
drs.o : drs.c  dbt.h dbtwin.h 

clean::
	$(RM) $(BIN_DIR)/gui
	$(RM) $(OBJS)


