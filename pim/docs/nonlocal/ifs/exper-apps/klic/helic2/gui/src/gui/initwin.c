/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include <Xm/Label.h>
#include <Xm/Text.h>
#include <stdio.h>
#include "gui.h"
#include "messages.h"

/******* 後でgui.hに入れる分 *******/

/***********************************/

Widget fileLoad;
char *fileSuffix[FILE_TYPE_NUM] = 
{ TYPE_SUFFIX, RULE_SUFFIX, VIEW_SUFFIX, QUERY_SUFFIX, COMMAND_SUFFIX };
Widget fileSlct;
Widget fileList;
Widget roleW;
Widget status, statusR; /* labels in inti-window */
Widget pb[FILE_TYPE_NUM]; /* toggle buttons in load window */
Widget text;
Widget tg[2][2]; /* toggle buttons in role window */
Widget debateB;
Widget drsB;

static int selectedFileType = 0;

void GuiCreateLoadedFileWindow();
void loadListCB();

/******************************************/
/* Window   : new Helic-II Initial Window */
/* Function : Open Load Window            */
/*            Assign roles of game        */
/*            End new Helic-II            */
/******************************************/

CheckIntDebateButSensitive()
/* ロードが完了し、役割設定が終った時にdebateボタンをsensitiveにする */
{
  if ( (loadingStatus == 4) && (roleStatus != 0) ) 
    XtSetSensitive( debateB, True);
  else
    XtSetSensitive( debateB, False);

  if ( loadingStatus == 4) 
    XtSetSensitive( drsB, True);
  else 
    XtSetSensitive( drsB, False);
}

GuiCallback(loadsCB)
/* 初期ウインドウのLoadボタンのCB */
{
  XtManageChild(fileLoad);
}

GuiCallback(roleCB)
/* 初期ウインドウのRoleボタンのCB */
{
  XtManageChild(roleW);
}

GuiCallback(guiQuitCB)
/* 初期ウインドウのQuitボタンのCB */
{
  GuiEnd(); /* ソケットの閉鎖などの処理と終了処理 */
  /** not reached **/
}

GuiCallback(debateCB)
/* 初期ウインドウのDebateボタンのCB */
{
  int i;
  int pos;
  int l;
  char *vc;

/* 初期ウインドウでの設定通知処理 */
  for(i = 0; i < POS_NUM; i++) {
    if ( (ComSetSolver((char)i, (char)roleAssign[i] )) == COM_NG ) {
      GuiErrOn;
    }
  }

/* 論争ウインドウの作成 */
  GuiCreateDebateWindowDrv(); /* 95.1.13 for RBR */

/* 初期ウインドウのインセンシティブ化 */
  XtSetSensitive( init_form, False ); /* 95.1.13 for RBR */

/* 全ての判断基準を求める */
  GuiMacro(ComSendStandpointList((char)PROSECUTOR));
  ComListMax(MessageD,arg2,allStandPoint_num);
  ComListCp(allStandPoint,allStandPoint_num,MessageD,arg2);

/* 全てのView候補を求める */
  GuiMacro(ComSendViewCandidateList((char)PROSECUTOR));
  ComListMax(MessageD,arg2,allViewCList_num);
  ComListCp(allViewCList,allViewCList_num,MessageD,arg2);

/* 現在設定しているユニット名を求める */
  for(pos = 0; pos < POS_NUM; pos++) {
    GuiMacro(ComSendCurrentUnit((char)pos));
    ComListMax(MessageD,arg2,currentUnitList_num[pos]);
    ComListCp(currentUnitList[pos],currentUnitList_num[pos],MessageD,arg2);
  }

/* 現在設定しているゴールおよびゴール候補を求める */ 
  for(pos = 0; pos < POS_NUM; pos++) {
    GuiMacro(ComSendGoalCandidateList((char)pos));
    currentGoal[pos] = (int)GuiCm(MessageE)->arg2;
    if (pos == PROSECUTOR) {
      ComListMax(MessageE,arg3,goalCandidateList_num);
      ComListCp(goalCandidateList,goalCandidateList_num,MessageE,arg3);
    }
    if (currentGoal[pos] != (short)-1) {
      if (pos == PROSECUTOR) {
	/* 論証ウインドウのGoal情報に記入 */
	XmTextSetString(dbtGoal[pos], goalCandidateList[currentGoal[pos]]);
/*
	XmTextSetStringWcs(dbtGoal[pos], 
			   (wchar_t *)goalCandidateList[currentGoal[pos]]);
*/
      }
    }
  }

/* 現在設定されている価値感を求める */
  for(pos = 0; pos < POS_NUM; pos++) {
    GuiMacro(ComSendCurrentView((char)pos));
    ComListMax(MessageD,arg2,currentView_num[pos]);
    ComListCp(currentView[pos],currentView_num[pos],MessageD,arg2);
    if (currentView_num[pos] != 0) {
      /* 論証ウインドウのView情報に記入 */
      l = 0;
      for(i = 0; i < currentView_num[pos]; i++) 
	l += strlen((currentView[pos])[i]) + 3;
      l = l - 3 + 1; /* decrease for " > " and increase for '\0' */
      vc = XtMalloc(l); 
      vc[0] = '\0';
      for(i = 0; i < currentView_num[pos]-1; i++)  {
	vc = strcat(vc,(currentView[pos])[i]);
	vc = strcat(vc," > ");
      }
      vc = strcat(vc,(currentView[pos])[currentView_num[pos]-1]);
      XmTextSetString(dbtView[pos], vc);
    }
  }

/* 論争ウインドウをMapする */
  for( i = 0 ; i < POS_NUM ; i++) {
    XtManageChild(dbtform[i]);
  }
}

GuiCallback(drsCB)
/* 初期ウインドウのDRSボタンのCB */
{
  int i;
  int pos;
  int l;
  char *vc;

/* 初期ウインドウでの設定通知処理 */
  if ( (ComSetSolver((char)DRS, (char)SYSTEM )) == COM_NG ) {
    GuiErrOn;
  }

/* 論争ウインドウの作成 */
  GuiCreateDRSWindow(); /* 95.1.13 for RBR */

/* 初期ウインドウのインセンシティブ化 */
  XtSetSensitive( init_form, False ); /* 95.1.13 for RBR */

/* 全ての判断基準を求める */
  GuiMacro(ComSendStandpointList((char)DRS));
  ComListMax(MessageD,arg2,allStandPoint_num);
  ComListCp(allStandPoint,allStandPoint_num,MessageD,arg2);

/* 全てのView候補を求める */
  GuiMacro(ComSendViewCandidateList((char)DRS));
  ComListMax(MessageD,arg2,allViewCList_num);
  ComListCp(allViewCList,allViewCList_num,MessageD,arg2);

/* 現在設定しているユニット名を求める */
  GuiMacro(ComSendCurrentUnit((char)DRS));
  ComListMax(MessageD,arg2,currentUnitList_num[DRS]);
  ComListCp(currentUnitList[DRS],currentUnitList_num[DRS],MessageD,arg2);


/* 現在設定しているゴールおよびゴール候補を求める */ 
  GuiMacro(ComSendGoalCandidateList((char)DRS));
  currentGoal[DRS] = (int)GuiCm(MessageE)->arg2;
  ComListMax(MessageE,arg3,goalCandidateList_num);
  ComListCp(goalCandidateList,goalCandidateList_num,MessageE,arg3);

  if (currentGoal[DRS] != (short)-1) {
    /* 論証ウインドウのGoal情報に記入 */
    XmTextSetString(dbtGoal[DRS], goalCandidateList[currentGoal[DRS]]);
  }


/* 現在設定されている価値感を求める */
  GuiMacro(ComSendCurrentView((char)DRS));
  ComListMax(MessageD,arg2,currentView_num[DRS]);
  ComListCp(currentView[DRS],currentView_num[DRS],MessageD,arg2);
  if (currentView_num[DRS] != 0) {
    /* 論証ウインドウのView情報に記入 */
    l = 0;
    for(i = 0; i < currentView_num[DRS]; i++) 
      l += strlen((currentView[DRS])[i]) + 3;
    l = l - 3 + 1; /* decrease for " > " and increase for '\0' */
    vc = XtMalloc(l); 
    vc[0] = '\0';
    for(i = 0; i < currentView_num[DRS]-1; i++)  {
      vc = strcat(vc,(currentView[DRS])[i]);
      vc = strcat(vc," > ");
    }
    vc = strcat(vc,(currentView[DRS])[currentView_num[DRS]-1]);
    XmTextSetString(dbtView[DRS], vc);
  }


/* 論争ウインドウをMapする */
  XtManageChild(dbtform[DRS]);
}

#ifdef DEBUG
GuiCallback(debugCB)
{
  XtSetSensitive( debateB, True);
  XtSetSensitive( drsB, True);
}
#endif DEBUG

void GuiCreateInitWindow()
/* 初期ウインドウの作成処理 */
{
  Widget title, loadLabel;
  Widget sep1, sep2;
  Widget act, loadb, roleb, quitb;
  Widget roleLabel;
  Widget formB;
  Dimension dim;
  Widget debugB;

  /* Form Widet */
  GuiSt();
  init_form = GuiXmCreateForm(toplevel, "init_form");

  /* Create new Helic-II label */
  GuiSt();
  GuiXmAttachForm(10, 20, 20, -1); 
  GuiMakeAndSetLabel("new Helic-II",GUI_F_ITAL34);
  title = GuiXmCreateLabel(init_form, NULL);

  /* Separator */
  GuiSt();
  GuiXmAttachWidget(GuiREG, title, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  sep1 = GuiXmCreateSeparatorHorizontal(init_form);

  /* Loading Status Display */

  GuiSt();
  GuiXmAttachForm(-1, 20, 20, -1);
  GuiXmAttachWidget(GuiREG, sep1, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Loading Status",GUI_F_ITAL14);
  loadLabel = GuiXmCreateLabel(init_form, NULL);
  GuiSt();
  GuiXmAttachForm(-1, -1, 20, -1);
  GuiXmAttachWidget(GuiREG, loadLabel, 5,
		    GuiOPP, loadLabel, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel(loadingStatusString[loadingStatus],GUI_F_MEDI18);
  status = GuiXmCreateLabel(init_form, NULL);

  /* Role Assigment Status Display */
  GuiSt();
  GuiXmAttachForm(-1, 20, 20, -1);
  GuiXmAttachWidget(GuiREG, status, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Role Assigment Status",GUI_F_ITAL14);
  roleLabel = GuiXmCreateLabel(init_form, NULL);
  GuiSt();
  GuiXmAttachForm(-1, -1, 20, -1);
  GuiXmAttachWidget(GuiREG, roleLabel, 5,
		    GuiOPP, roleLabel, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel(roleStatusString[roleStatus],GUI_F_MEDI18);
  statusR = GuiXmCreateLabel(init_form, NULL);

  /* Create the action area */
  GuiSt();
  GuiXmAttachWidget(GuiREG, statusR, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  sep2 = GuiXmCreateSeparatorHorizontal(init_form);
  GuiSt();
  GuiXmAttachForm(-1,5,5,5);
  GuiXmAttachWidget(GuiREG, sep2, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  formB = GuiXmCreateForm(init_form, "form");
  GuiSt();
  GuiXmAttachForm(0, 0, -1, 0);
  GuiSa(XmNorientation, XmHORIZONTAL);
  act = GuiXmCreateRowColumn(formB);
  GuiSt();
  loadb = GuiXmCreateButton(act, "Load");
  GuiSt();
  roleb = GuiXmCreateButton(act, "Role");
  GuiSt();
  GuiSa(XmNsensitive, False);
  debateB = GuiXmCreateButton(act, "Debate");
  GuiSt();
  GuiSa(XmNsensitive, False);
  drsB = GuiXmCreateButton(act, "DRS");
#ifdef DEBUG
  GuiSt();
  GuiSa(XmNsensitive, True);
  debugB = GuiXmCreateButton(act, "Debug");
  XtAddCallback(debugB, XmNactivateCallback, (XtCallbackProc)debugCB, NULL);
#endif DEBUG
  GuiSt();
  GuiSa(XmNmarginHeight, &dim);
  GuiSg(act);
  GuiSt();
  GuiXmAttachForm(dim, -1, dim, dim);
  quitb = GuiXmCreateButton(formB, "Quit");
  XtAddCallback(loadb, XmNactivateCallback, (XtCallbackProc)loadsCB, NULL);
  XtAddCallback(roleb, XmNactivateCallback, (XtCallbackProc)roleCB, NULL);
  XtAddCallback(debateB, XmNactivateCallback, (XtCallbackProc)debateCB, NULL);
  XtAddCallback(drsB, XmNactivateCallback, (XtCallbackProc)drsCB, NULL);
  XtAddCallback(quitb, XmNactivateCallback, (XtCallbackProc)guiQuitCB, NULL);
}


/***************************************/
/* Window   : Load Window              */
/* Function : Load Knowledge file      */
/***************************************/

GuiCallback(loadQuitCB)
/* ロードウインドウのQuitボタンのCB */
{
  XtUnmanageChild(fileLoad);
  XtUnmanageChild(fileList);
}

GuiCallback(loadListCB)
/* ロードウインドウのListボタンのCB */
{
  XtManageChild( fileList );
}

GuiCallback(loadFileTypeCB)
/* ロードウインドウのFileTypeトグルボタンのCB */
{
  selectedFileType = (int)client_data;
  XmFileSelectionDoSearch(fileSlct, 
			  XmStringCreateSimple(fileSuffix[selectedFileType]));
}

void LoadTgSet(int id, int flag)
/* ロードウインドウのFileTypeトグルボタンのsensitive操作処理 */
/* IdentifyLoadingStatus()で使用 */
{
  GuiSt();
  GuiSa(XmNsensitive, flag);
  GuiSv(pb[id]);
}

void IdentifyLoadingStatus()
/* Comから戻るLoading Status情報をもとにトグルのsensitiveを切替える */
{
  int newStatus;

  if ( (loadFlag & 0x0001) == 0x0000 ) /* no type */
    newStatus = 0; 
  else if ( (loadFlag & 0x0002) == 0x0000 ) /* no rule */
    newStatus = 1;
  else if ( (loadFlag & 0x0004) == 0x0000 ) /* no view */
    newStatus = 2;
  else if ( (loadFlag & 0x0008) == 0x0000 ) /* no goal */
    newStatus = 3;
  else if ( loadFlag == 0x000f ) /* all file */
    newStatus = 4;
  else
    printf("Illegal loadFlag %x\n",loadFlag);

  if ( newStatus != loadingStatus ) {
    GuiSt();
    GuiSa(XmNlabelString, 
	  XmStringCreateLtoR(loadingStatusString[newStatus],GUI_F_MEDI18));
    GuiSv(status);
    switch( newStatus ) {
    case 0:
      LoadTgSet(0,True);
      LoadTgSet(1,False);
      LoadTgSet(2,False);
      LoadTgSet(3,True); /* 95.2.3 for GOAL */
      LoadTgSet(4,True);
      break;
    case 1:
      LoadTgSet(0,True);
      LoadTgSet(1,True);
      LoadTgSet(2,False);
      LoadTgSet(3,True); /* 95.2.3 for GOAL */
      LoadTgSet(4,True);
      break;
    case 2:
      LoadTgSet(0,True);
      LoadTgSet(1,True);
      LoadTgSet(2,True);
      LoadTgSet(3,True); /* 95.2.3 for GOAL */
      LoadTgSet(4,True);
      break;
    case 3:
      LoadTgSet(0,True);
      LoadTgSet(1,True);
      LoadTgSet(2,True);
      LoadTgSet(3,True);
      LoadTgSet(4,True);
      break;
    case 4:
      LoadTgSet(0,True);
      LoadTgSet(1,True);
      LoadTgSet(2,True);
      LoadTgSet(3,True);
      LoadTgSet(4,True);
      break;
    }
    loadingStatus = newStatus;
  }
}

void loadLoadCB(Widget w, XtPointer client_data, 
		XmFileSelectionBoxCallbackStruct *call_data)
/* ロードウインドウのLoadボタンのCB */
{
  char *tmp;
  char *file;

  if (call_data->length == call_data->dir_length)
    return; /* no file selected */

  XmStringGetLtoR(call_data->value, XmSTRING_DEFAULT_CHARSET, &file);
  if ( COM_OK == GuiComFileLoad(file, selectedFileType) ) {
    IdentifyLoadingStatus();
    GuiXmTextAddString(text, file);
    GuiXmTextAddString(text, "\n");
    CheckIntDebateButSensitive();
  }
}

Widget GuiCreateLoadWindow()
/* ロードウインドウの作成 */
{
  Widget rowc;
  Widget tmp, label1, sep1;
  int i;

  /* Form Widet */
  GuiSt();
  fileLoad = GuiXmCreateFormDialog(toplevel, "Load");

  /* Label */
  GuiSt();
  GuiXmAttachForm(10, 5, 5, -1);
  GuiMakeAndSetLabel("Loading Knowledge",GUI_F_ITAL18);
  label1 = (Widget)GuiXmCreateLabel(fileLoad, NULL);

  /* Separator */
  GuiSt();
  GuiXmAttachWidget(GuiREG, label1, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  sep1 = GuiXmCreateSeparatorHorizontal(fileLoad);

  /* File Selection Box */
  GuiSt();
  GuiSa(XmNokLabelString, XmStringCreateSimple("Load"));
  GuiSa(XmNapplyLabelString, XmStringCreateSimple("Filter"));
  GuiSa(XmNselectionLabelString, XmStringCreateSimple("Loading File"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("List"));
  GuiSa(XmNlistLabelString, XmStringCreateSimple("File"));
  GuiSa(XmNdirListLabelString, XmStringCreateSimple("Directory"));
  GuiSa(XmNfileListLabelString, XmStringCreateSimple("File"));
  GuiSa(XmNfilterLabelString, XmStringCreateSimple("Filter"));
  GuiSa(XmNdirMask, XmStringCreateSimple(TYPE_SUFFIX));
  GuiXmAttachForm(-1,5,5,5);
  fileSlct = (Widget)XmCreateFileSelectionBox(fileLoad, "file_slct_b", 
						 GuiXArg, GuiXArgNum);
  XtManageChild( fileSlct );
  GuiSt();
  GuiSa(XmNlabelString, XmStringCreateSimple("Done"));
  tmp =  (Widget)XmFileSelectionBoxGetChild( fileSlct, XmDIALOG_HELP_BUTTON );
  XtAddCallback(tmp, XmNactivateCallback, loadQuitCB, NULL);
  GuiSv(tmp);
  XtAddCallback(fileSlct, XmNcancelCallback, loadListCB, NULL);
  XtAddCallback(fileSlct, XmNokCallback, (XtCallbackProc)loadLoadCB, NULL);


  /* Type Selection Area */
  GuiSt();
  GuiXmAttachForm(-1,5,5,-1);
  GuiXmAttachWidget(GuiREG, sep1, 10,
		    NULL, NULL, NULL, NULL, NULL, NULL, GuiREG, fileSlct, 10 );
  GuiSa(XmNbuttonSet, 0);
  rowc = GuiXmCreateRadioBox(fileLoad);
  for(i = 0; i < FILE_TYPE_NUM; i++) {
    GuiSt();
    if (i == RULE_FILE || i == VIEW_FILE) /* 95.2.3 */
      GuiSa(XmNsensitive, False);
    if (i == TYPE_FILE)
      GuiSa(XmNset, True);
    GuiMakeAndSetLabel(fileType[i],GUI_F_ITAL14);
    GuiSa(XmNpacking, XmPACK_TIGHT);
    pb[i] = GuiXmCreateToggleButtonGadget(rowc, NULL);
    XtAddCallback(pb[i], XmNarmCallback, loadFileTypeCB, (XtPointer)i);
  }
  GuiCreateLoadedFileWindow(); /* ロード済みファイル一覧ウインドウの作成 */
}

/**********************************/
/* Window   : Loaded File Window  */
/* Function : Display loaded file */
/**********************************/

GuiCallback(loadListDoneCB)
/* ロード済みファイル一覧ウインドウのDoneボタンのCB */
{
  XtUnmanageChild(fileList);
}

void GuiCreateLoadedFileWindow()
/* ロード済みファイル一覧ウインドウの作成 */
{
  Widget label1;
  int i;
  Widget sep, rowc, but;

  /* Form Widet */
  GuiSt();
  fileList = GuiXmCreateFormDialog(toplevel, "Loaded Files");


  /* Label */
  GuiSt();
  GuiXmAttachForm(5, 5, 5, -1);
  GuiMakeAndSetLabel("Loaded Files",GUI_F_ITAL18);
  label1 = GuiXmCreateLabel(fileList, NULL);

  /* Text Widget */
  GuiSt();
  GuiSa(XmNrows, 5);
  GuiSa(XmNcolumns, 30);
  GuiSa(XmNeditable, False);
  GuiXmAttachForm(-1,5,5,-1);
  GuiXmAttachWidget(GuiREG, label1, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);

  text = GuiXmCreateText(fileList);

  /* Label */
  GuiSt();
  GuiXmAttachWidget(GuiREG, text, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  sep = GuiXmCreateSeparatorHorizontal(fileList);

  /* Button */
  GuiSt();
  GuiXmAttachForm(-1, 5, 5, 5);
  GuiSa(XmNorientation, XmHORIZONTAL);
  GuiXmAttachWidget(GuiREG, sep, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  rowc = GuiXmCreateRowColumn(fileList);
  GuiSt();
  but = GuiXmCreateButton(rowc, "Done");
  XtAddCallback(but, XmNactivateCallback, loadListDoneCB, NULL);
}

/*************************************/
/* Window   : Role Assignment Window */
/* Function : Assign role            */
/*************************************/

GuiCallback(roleDoneCB)
/* 役割設定ウインドウのDoneボタンのCB */
{
  int i,j;
  Boolean tmp;

  for(i=0;i<2;i++) 
    for(j=0;j<2;j++) {
      GuiSt();
      GuiSa(XmNset, &tmp);
      GuiSg(tg[i][j]);
      if(tmp == True) {
	roleAssign[i] = j;
	break;
      }
    }

  if (roleAssign[0] != -1 && roleAssign[1] != -1) 
    roleStatus = roleAssign[0]*2 + roleAssign[1] + 1;
  else 
    roleStatus = 0;
  GuiSt();
  GuiSa(XmNlabelString,
	XmStringCreateLtoR(roleStatusString[roleStatus],GUI_F_MEDI18));
  GuiSv(statusR);

  CheckIntDebateButSensitive();
  
  XtUnmanageChild(roleW);
}

void GuiCreateRoleWindow()
/* 役割設定ウインドウの作成 */
{
  Widget label1;
  int i;
  Widget sep1, sep2;
  Widget form[2], label[2], radio[2];
  char *roleS[2] = {"Prosecutor", "Defendant"};
  Widget but, act;

  /* Form Widet */
  GuiSt();
  roleW = GuiXmCreateFormDialog(toplevel, "Role");

  /* Label */
  GuiSt();
  GuiXmAttachForm(10, 5, 5, -1);
  GuiMakeAndSetLabel("Role Assignment",GUI_F_ITAL18);
  label1 = (Widget)GuiXmCreateLabel(roleW, NULL);

  /* Separator */
  GuiSt();
  GuiXmAttachWidget(GuiREG, label1, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  sep1 = GuiXmCreateSeparatorHorizontal(roleW);

  /* Assigment Area */

  for(i = 0; i < 2; i++) {
    GuiSt();
    if ( i == 0 ) {
      GuiXmAttachForm(-1, 5, -1, -1);
      GuiXmAttachWidget(GuiREG, sep1, 10,
			NULL, NULL, NULL,
			NULL, NULL, NULL,
			NULL, NULL, NULL);
    }
    else {
      GuiXmAttachForm(-1, -1, 5, -1);
      GuiXmAttachWidget(GuiREG, sep1, 10,
			GuiREG, form[0], 5,
			NULL, NULL, NULL,
			NULL, NULL, NULL);
    }
    form[i] = GuiXmCreateForm(roleW, "form");
    GuiSt();
    GuiXmAttachForm(0, 0, 0, -1);
    GuiMakeAndSetLabel(roleS[i],GUI_F_ITAL18);
    label[i] = GuiXmCreateLabel(form[i], NULL);
    GuiSt();
    GuiXmAttachForm(-1, 0, 0, 0);
    GuiXmAttachWidget(GuiREG, label[i], 5,
		      NULL, NULL, NULL,
		      NULL, NULL, NULL,
		      NULL, NULL, NULL);
    radio[i] = GuiXmCreateRadioBox(form[i]);
    GuiSt();
    GuiMakeAndSetLabel("System", GUI_F_MEDI18);
    tg[i][0] = GuiXmCreateToggleButtonGadget(radio[i], NULL);
    GuiSt();
    GuiMakeAndSetLabel("User", GUI_F_MEDI18);
    tg[i][1] = GuiXmCreateToggleButtonGadget(radio[i], NULL);
  }

  /* Separator */
  GuiSt();
  GuiXmAttachWidget(GuiREG, form[0], 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  sep2 = GuiXmCreateSeparatorHorizontal(roleW);

  /* Button */
  GuiSt();
  GuiXmAttachForm(-1, 5, 5, 5);
  GuiSa(XmNorientation, XmHORIZONTAL);
  GuiXmAttachWidget(GuiREG, sep2, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  act = GuiXmCreateRowColumn(roleW);
  GuiSt();
  but = GuiXmCreateButton(act, "Done");
  XtAddCallback(but, XmNactivateCallback, roleDoneCB, NULL);
}

