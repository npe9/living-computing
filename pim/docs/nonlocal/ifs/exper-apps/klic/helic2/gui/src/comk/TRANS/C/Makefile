CC  		= 	gcc
OBJECTS1        =       nc.o vect.o y_tab.o lex_yy.o  #English
OBJECTS2        =       nc.o vect.o y_tab.o lex_yyE.o #Use euc.h
OBJECTS3        =       nc.o vect.o y_tab.o lex_yyF.o #flex
OBJECTS4        =       nc.o vect.o y_tab.o lex_yyW.o #Use wcha

TARGET 		= 	gtransrg

all     	: 	
		  	if [ $(Flex) = exist ];\
			then \
			  $(MAKE) $(OBJECTS3); \
 			  $(CC) -g -o ../../../../bin/$(TARGET) $(OBJECTS3) -lfl; \
			else \
				$(MAKE) LANGCHECK;\
			fi

LANGCHECK       :
			if [ $(LANG) = japanese ];\
			then \
			  $(MAKE) $(OBJECTS2); \
		  	  $(CC) -g -o ../../../../bin/$(TARGET) $(OBJECTS2) -ly -ll; \
			else \
			  $(MAKE) $(OBJECTS1); \
		  	  $(CC) -g -o ../../../../bin/$(TARGET) $(OBJECTS1) -ly -ll; \
			fi

clean		:
			/bin/rm  -f *.o


nc.o : nc.c
	$(CC) -c -g nc.c
vect.o : vect.c
	$(CC) -c -g vect.c
y_tab.o : y_tab.c
	$(CC) -c -g y_tab.c
lex_yy.o : lex_yy.c
	$(CC) -c -g lex_yy.c
lex_yyE.o : lex_yyE.c
	$(CC) -c -g lex_yyE.c
lex_yyF.o : lex_yyF.c
	$(CC) -c -g lex_yyF.c
lex_yyW.o : lex_yyW.c
	$(CC) -c -g lex_yyW.c





