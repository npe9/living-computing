CC = klic

KLICDIR		= 	../../

DBDIR           =       $(KLICDIR)/DB

OBJECTS = dataCheck.o convert.o comGUIRec.o commandTake.o comkGui.o comkGuiDBT.o comksend.o comkreceive.o nh.o dnh.o

all             :       $(OBJECTS)

dnh.o	:	dnh.kl1
	klic -x$(DBDIR) -c dnh.kl1
nh.o 	:	nh.kl1
	klic -x$(DBDIR) -c nh.kl1
convert.o : convert.kl1
	klic -x$(DBDIR) -c convert.kl1
dataCheck.o : dataCheck.kl1
	klic -x$(DBDIR) -c dataCheck.kl1
commandTake.o : commandTake.kl1
	klic -x$(DBDIR) -c commandTake.kl1
comGUIRec.o : comGUIRec.kl1
	klic -x$(DBDIR) -c comGUIRec.kl1
comkGui.o : comkGui.kl1
	klic -x$(DBDIR) -c comkGui.kl1
comkGuiDBT.o : comkGuiDBT.kl1
	klic -x$(DBDIR) -c comkGuiDBT.kl1
comksend.o : comksend.kl1
	klic -x$(DBDIR) -c comksend.kl1
comkreceive.o : comkreceive.kl1
	klic -x$(DBDIR) -c comkreceive.kl1



clean :
	rm -f core *.c *.o *.ext *.h *.db




