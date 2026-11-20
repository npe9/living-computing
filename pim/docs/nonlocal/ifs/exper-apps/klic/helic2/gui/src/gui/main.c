/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>

#define MAIN
#include "gui.h"
#include "messages.h"

void main(int argc, char **argv)
{
  Widget tmp;

  XtSetLanguageProc(NULL, NULL, NULL);
  XtToolkitInitialize();
  application1 = XtCreateApplicationContext();
  display1 = XtOpenDisplay(application1, (String)getenv("DISPLAY"),
			   "helicII", "HelicII", 
			   NULL, 0, 
			   &argc, argv);
  toplevel = XtAppCreateShell("helicII", "HelicII", 
			      applicationShellWidgetClass, display1, NULL, 0);

/* Applicationを使わない場合の初期処理
  toplevel = XtInitialize(argv[0], "HelicII", NULL, (int)NULL, &argc, argv);
*/

  GuiComInit(argc, argv); /* 通信部の初期化 */

  GuiFontCreate();

  GuiCreateInitWindow();
  GuiCreateLoadWindow();
  GuiCreateRoleWindow();

  XtRealizeWidget(toplevel);
  GuiMainLoop();
}

void GuiMainLoop()
{
/*  XtAppMainLoop(application1);*/
/* メインループ */
  while(True) {
    XEvent event;
    if(XtAppPending(application1)) {
      XtAppNextEvent(application1,&event);
      XtDispatchEvent(&event);
    } 
    if (GuiPending()) {
      GuiRunData();
    }
  }
}



