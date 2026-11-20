/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#define UTIL
#include <Xm/Form.h>
#include <Xm/Separator.h>
#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/ToggleBG.h>
#include <Xm/PushB.h>
#include <Xm/RowColumn.h>
#include <Xm/MessageB.h>
#include <Xm/MenuShell.h>
#include <Xm/List.h>
#include "gui.h"

Widget waitW;


void GuiXmAttachForm(int top, int left, int right, int bottom)
{
  if (top != -1) {
    GuiSa(XmNtopAttachment, XmATTACH_FORM);
    GuiSa(XmNtopOffset, top);
  }
  if (left != -1) {
    GuiSa(XmNleftAttachment, XmATTACH_FORM);
    GuiSa(XmNleftOffset, left);
  }
  if (right != -1) {
    GuiSa(XmNrightAttachment, XmATTACH_FORM);
    GuiSa(XmNrightOffset, right);
  }
  if (bottom != -1) {
    GuiSa(XmNbottomAttachment, XmATTACH_FORM);
    GuiSa(XmNbottomOffset, bottom);
  }
}

void GuiXmAttachPos(int top, int left, int right, int bottom)
{
  if (top != -1) {
    GuiSa(XmNtopAttachment, XmATTACH_POSITION);
    GuiSa(XmNtopPosition, top);
  }
  if (left != -1) {
    GuiSa(XmNleftAttachment, XmATTACH_POSITION);
    GuiSa(XmNleftPosition, left);
  }
  if (right != -1) {
    GuiSa(XmNrightAttachment, XmATTACH_POSITION);
    GuiSa(XmNrightPosition, right);
  }
  if (bottom != -1) {
    GuiSa(XmNbottomAttachment, XmATTACH_POSITION);
    GuiSa(XmNbottomPosition, bottom);
  }
}

void GuiXmAttachWidget(int topr, Widget topw, int top, 
		    int leftr, Widget leftw, int left,
		    int rightr, Widget rightw, int right, 
		    int bottomr, Widget bottomw, int bottom)
{
  if (topr != (int)NULL) {
    if (topr == GuiREG) 
      GuiSa(XmNtopAttachment, XmATTACH_WIDGET);
    else 
      GuiSa(XmNtopAttachment, XmATTACH_OPPOSITE_WIDGET);
    GuiSa(XmNtopWidget, topw);
    GuiSa(XmNtopOffset, top);
  }
  if (leftr != (int)NULL) {
    if (leftr == GuiREG) 
      GuiSa(XmNleftAttachment, XmATTACH_WIDGET);
    else 
      GuiSa(XmNleftAttachment, XmATTACH_OPPOSITE_WIDGET);
    GuiSa(XmNleftWidget, leftw);
    GuiSa(XmNleftOffset, left);
  }
  if (rightr != (int)NULL) {
    if (rightr == GuiREG) 
      GuiSa(XmNrightAttachment, XmATTACH_WIDGET);
    else 
      GuiSa(XmNrightAttachment, XmATTACH_OPPOSITE_WIDGET);
    GuiSa(XmNrightWidget, rightw);
    GuiSa(XmNrightOffset, right);
  }
  if (bottomr != (int)NULL) {
    if (bottomr == GuiREG) 
      GuiSa(XmNbottomAttachment, XmATTACH_WIDGET);
    else 
      GuiSa(XmNbottomAttachment, XmATTACH_OPPOSITE_WIDGET);
    GuiSa(XmNbottomWidget, bottomw);
    GuiSa(XmNbottomOffset, bottom);
  }
}

Widget GuiXmCreateForm(Widget parent, char *name)
{
  GuiXmW = XmCreateForm(parent, name, GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateSeparatorHorizontal(Widget parent)
{
  GuiSa(XmNorientation, XmHORIZONTAL);
  GuiSa(XmNleftAttachment, XmATTACH_FORM);
  GuiSa(XmNrightAttachment, XmATTACH_FORM);
  GuiXmW = XmCreateSeparator (parent, "separator", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateFrame(Widget parent)
{
  GuiSa(XmNshadowType, XmSHADOW_OUT);
  GuiXmW = XmCreateFrame (parent, "frame", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateLabel(Widget parent, char *label)
{
  XmString mlabel;

  if (label != NULL) {
    GuiSa(XmNlabelType, XmSTRING);
    mlabel = XmStringCreateLtoR (label, XmSTRING_DEFAULT_CHARSET);
    GuiSa(XmNlabelString, mlabel);
    GuiXmW = XmCreateLabel(parent, "label", GuiXArg, GuiXArgNum);
    XmStringFree (mlabel);
  } else
    GuiXmW = XmCreateLabel(parent, "label", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateCheckBox(Widget parent)
{
  GuiXmW = XmCreateSimpleCheckBox(parent, "checkbox", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateRadioBox(Widget parent)
{
  GuiXmW = XmCreateSimpleRadioBox(parent, "radiobox", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateRowColumn(Widget parent)
{
  GuiXmW = XmCreateRowColumn(parent, "radiobox", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateToggleButtonGadget(Widget parent, char *label)
{
  XmString mlabel;

  if (label != NULL) {
    GuiSa(XmNlabelType, XmSTRING);
    mlabel = XmStringCreateLtoR (label, XmSTRING_DEFAULT_CHARSET);
    GuiSa(XmNlabelString, mlabel);
    GuiXmW = XmCreateToggleButtonGadget(parent, "toggle", GuiXArg, GuiXArgNum);
    XmStringFree (mlabel);
  } else
    GuiXmW = XmCreateToggleButtonGadget(parent, "toggle", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateButton(Widget parent, char *label)
{
  XmString mlabel;

  if (label != NULL) {
    GuiSa(XmNlabelType, XmSTRING);
    mlabel = XmStringCreateLtoR (label, XmSTRING_DEFAULT_CHARSET);
    GuiSa(XmNlabelString, mlabel);
    GuiXmW = XmCreatePushButton(parent, "button", GuiXArg, GuiXArgNum);
    XmStringFree (mlabel);
  } else
    GuiXmW = XmCreatePushButton(parent, "button", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

void GuiFontCreate()
{
  XFontStruct *fs;

  fs = XLoadQueryFont(XtDisplay(toplevel),GUI_F_BOLD24_B);
  GuiFontList = XmFontListCreate(fs,GUI_F_BOLD24);
  fs = XLoadQueryFont(XtDisplay(toplevel),GUI_F_BOLD18_B);
  GuiFontList = XmFontListAdd(GuiFontList,fs,GUI_F_BOLD18);
  fs = XLoadQueryFont(XtDisplay(toplevel),GUI_F_ITAL14_B);
  GuiFontList = XmFontListAdd(GuiFontList,fs,GUI_F_ITAL14);
  fs = XLoadQueryFont(XtDisplay(toplevel),GUI_F_ITAL18_B);
  GuiFontList = XmFontListAdd(GuiFontList,fs,GUI_F_ITAL18);
  fs = XLoadQueryFont(XtDisplay(toplevel),GUI_F_ITAL34_B);
  GuiFontList = XmFontListAdd(GuiFontList,fs,GUI_F_ITAL34);
  fs = XLoadQueryFont(XtDisplay(toplevel),GUI_F_MEDI18_B);
  GuiFontList = XmFontListAdd(GuiFontList,fs,GUI_F_MEDI18);
  
}

Widget GuiXmCreateFormDialog(Widget parent, char *name)
{
  GuiSt();
  GuiXmW = XmCreateFormDialog(parent, name, GuiXArg, GuiXArgNum);

  return GuiXmW;
}

void GuiMakeAndSetLabel(char *string, XmStringCharSet charset)
{
  GuiSa(XmNlabelType, XmSTRING);
  GuiSa(XmNfontList, GuiFontList);
  GuiSa(XmNlabelString, XmStringCreateLtoR(string, charset));
  GuiSa(XmNalignment, XmALIGNMENT_BEGINNING);
}
  
Widget GuiXmCreateText(Widget parent)
{
  GuiSa(XmNeditMode, XmMULTI_LINE_EDIT);
  GuiXmW = (Widget)XmCreateScrolledText(parent, "text", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

void GuiXmTextAddString(Widget w, char *string)
{
  int l;
  XmTextPosition pos;

  if (w == (Widget)NULL)
    return;
  if (string[0] == '\0')
    return;
  pos = XmTextGetInsertionPosition(w);
  XmTextInsert(w, pos, string);
}

Widget GuiXmCreateTextField(Widget parent)
{
  GuiXmW = (Widget)XmCreateTextField(parent, "text", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiXmCreateScrolledList(Widget parent, int num, char **list)
{
  XmString *mlist,tmp;
  int i;

  GuiSa(XmNitemCount, num);
  if (num != 0) {
    mlist = (XmString *)XtCalloc(num,sizeof(XmString));
    for(i = 0; i < num; i++) 
      mlist[i] = XmStringCreateLtoR( list[i], XmSTRING_DEFAULT_CHARSET);
    GuiSa(XmNitems, mlist);
  }
/*
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
*/
  GuiXmW = (Widget)XmCreateScrolledList(parent, "list", GuiXArg, GuiXArgNum);
/* ウインドウ終了時に行なう
  for( i = 0; i < num; i++) 
    XmStringFree(mlist[i]);
  XtFree((char *)mlist);
*/

  XtManageChild(GuiXmW);

  return GuiXmW;
}

GuiCallback(GuiAutoExitCallback)
{
  exit(0);
}

void GuiErrorStopPopup(char *message)
{
  XmString quitL,messageL;
  char *s;
  Widget w,tmp;

  GuiSt();
  quitL = XmStringCreateLtoR("Quit",XmSTRING_DEFAULT_CHARSET);
  GuiSa(XmNokLabelString, quitL);
  s = XtMalloc( (strlen("A critical error has been occured.\n")
		 + strlen(message)
		 + 1 /* \0の分 */ ) );
  s = strcpy(s, "A critical error has been occured.\n");
  s = strcat(s, message);

  messageL = XmStringCreateLtoR( s, XmSTRING_DEFAULT_CHARSET);
  GuiSa(XmNmessageString, messageL);
  w = (Widget)XmCreateErrorDialog(toplevel, "error", GuiXArg, GuiXArgNum);
  XtManageChild( w );
  XmStringFree(quitL);
  XmStringFree(messageL);
  XtFree( s );
  XtUnmanageChild(XmMessageBoxGetChild(w, XmDIALOG_HELP_BUTTON));
  XtUnmanageChild(XmMessageBoxGetChild(w, XmDIALOG_CANCEL_BUTTON));
  XtAddCallback(w, XmNokCallback, GuiAutoExitCallback, NULL);

  GuiMainLoop(); /* infinite loop */
}

void GuiErrorPopup(char *message)
{
  XmString quitL,contL,messageL;
  char *s;
  Widget w,tmp;

  GuiSt();
  quitL = XmStringCreateLtoR("Quit",XmSTRING_DEFAULT_CHARSET);
  GuiSa(XmNokLabelString, quitL);
  contL = XmStringCreateLtoR("Continue",XmSTRING_DEFAULT_CHARSET);
  GuiSa(XmNcancelLabelString, contL);
  s = XtMalloc( (strlen("A critical error has been occured.\n")
		 + strlen(message)
		 + 1 /* \0の分 */ ) );
  s = strcpy(s, "A critical error has been occured.\n");
  s = strcat(s, message);

  messageL = XmStringCreateLtoR( s, XmSTRING_DEFAULT_CHARSET);
  GuiSa(XmNmessageString, messageL);
  w = (Widget)XmCreateErrorDialog(toplevel, "error", GuiXArg, GuiXArgNum);
  XtManageChild( w );
  XmStringFree(quitL);
  XmStringFree(contL);
  XmStringFree(messageL);
  XtFree( s );
  XtUnmanageChild(XmMessageBoxGetChild(w, XmDIALOG_HELP_BUTTON));
  XtAddCallback(w, XmNokCallback, GuiAutoExitCallback, NULL);

  GuiMainLoop(); /* infinite loop */
}

void GuiWarningPopup(char *message)
{
  XmString quitL,contL,messageL;
  char s;
  Widget w,tmp;

  GuiSt();
  messageL = XmStringCreateLtoR( message, XmSTRING_DEFAULT_CHARSET);
  GuiSa(XmNmessageString, messageL);
  w = (Widget)XmCreateWarningDialog(toplevel, "error", GuiXArg, GuiXArgNum);
  XtManageChild( w );
  XmStringFree(messageL);
  XtUnmanageChild(XmMessageBoxGetChild(w, XmDIALOG_HELP_BUTTON));
  XtUnmanageChild(XmMessageBoxGetChild(w, XmDIALOG_CANCEL_BUTTON));
}

void GuiXmListAddItem(Widget w, char *string, int position)
{
  XmString tmp;

  if(string[0] != '\0') 
    tmp = XmStringCreateLtoR( string, XmSTRING_DEFAULT_CHARSET);
  else
    tmp = XmStringCreateLtoR( " ", XmSTRING_DEFAULT_CHARSET);
  XmListAddItem(w, tmp, position);
}

void GuiXmListAddItems(Widget w, char **items, int item_num, int position)
{
  int i;

  for(i=0; i<item_num; i++) {
    GuiXmListAddItem(w,items[i],position);
  }
}
  
Widget GuiXmCreateButtonGadget(Widget parent, char *label)
{
  XmString mlabel;

  if (label != NULL) {
    GuiSa(XmNlabelType, XmSTRING);
    mlabel = XmStringCreateLtoR (label, XmSTRING_DEFAULT_CHARSET);
    GuiSa(XmNlabelString, mlabel);
    GuiXmW = (Widget)XmCreatePushButtonGadget(parent, "button", GuiXArg, GuiXArgNum);
    XmStringFree (mlabel);
  } else
    GuiXmW = (Widget)XmCreatePushButtonGadget(parent, "button", GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}

Widget GuiBuildPopupMenu(Widget w, int item_num, char **items, void cb())
{
  Widget menu, tmp;
  int i;

  menu = XmCreatePopupMenu(w, "popup", GuiXArg, GuiXArgNum);
  if (item_num != 0) {
    for(i = 0; i < item_num; i++) {
      GuiSt();
      tmp = GuiXmCreateButtonGadget(menu, items[i]);
      XtAddCallback(tmp, XmNactivateCallback, cb, (XtPointer)i);
    }
  }
}

Widget GuiXmCreateSelectionDialog(Widget w, char *name, 
				  int item_num, char **items)
{
  XmStringTable mlist;
  int i;

  mlist = (XmStringTable)XtCalloc(item_num, sizeof(XmString));
  for(i = 0; i < item_num; i++) {
    mlist[i] = XmStringCreateLtoR (items[i], XmSTRING_DEFAULT_CHARSET);
  }
  GuiSa(XmNlistItems, mlist);
  GuiSa(XmNlistItemCount, item_num);
  GuiXmW = (Widget)XmCreateSelectionDialog(w, name, GuiXArg, GuiXArgNum);
  XtManageChild(GuiXmW);

  return GuiXmW;
}


void GuiShortLoop()
{
  int i;

  for(i = 0; i < 1000; i++) {
    XEvent event;
    if(XtAppPending(application1)) {
      XtAppNextEvent(application1,&event);
      XtDispatchEvent(&event);
    } 
  }
}

void GuiWait(Widget parent)
{
  GuiSt();
  waitW = GuiXmCreateFormDialog(parent, "wait");

  GuiSt();
  GuiXmAttachForm(10,10,10,10);
  GuiMakeAndSetLabel("Please wait",GUI_F_ITAL34);
  GuiXmCreateLabel(waitW, NULL);
  XtManageChild(waitW);

  GuiShortLoop();
}

void GuiWaitClose()
{
  XtDestroyWidget(waitW);

  GuiShortLoop();
}

