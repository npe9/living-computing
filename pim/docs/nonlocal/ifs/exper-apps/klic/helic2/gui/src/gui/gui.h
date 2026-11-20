/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/**************/
/* マクロ定義 */
/**************/

#ifdef MAIN
#define EXTERN
#else
#define EXTERN extern
#endif MAIN

/* 無限ループを避けるための最大数 */
#define INFINITE 10000

/* GuiXmAttachWidgetの接触方式の指定 */
#define GuiREG 1 /* GuiXmAttachWidgetでXmATTACH_WIDGETを指定する場合 */
#define GuiOPP 2 /* GuiXmAttachWidgetでXmATTACH_OPPOSITE_WIDGETを指定する場合*/

/* GuiXmユーティリティのリソース設定のためのマクロ */
#define GuiSa(n, d) \
    ((void)( (GuiXArg[GuiXArgNum]).name = \
	    (n), (GuiXArg[GuiXArgNum]).value = (XtArgVal)(d), GuiXArgNum++ ))
#define GuiSt() (GuiXArgNum = 0)
#define GuiSv(w) XtSetValues(w,GuiXArg,GuiXArgNum)
#define GuiSg(w) XtGetValues(w,GuiXArg,GuiXArgNum)

/* callbackルーチン定義のためのマクロ */
#define GuiCallback(fname) \
  void fname(Widget w, XtPointer client_data, XtPointer call_data)

/* エラーポップアップウインドウ表示のためのマクロ */
#define GuiErrSp \
  GuiErrorStopPopup( ComErrorMessage )
#define GuiErrCt \
  GuiErrorPopup( ComErrorMessage )
#define GuiWarn \
  GuiWarningPopup( ComErrorMessage )
#define GuiErrOn \
  switch( (int)ComErrorType ) {\
    case 0: GuiErrSp;return;\
    case 1: GuiErrCt;return;\
    case 2: GuiWarn;return;}

/* エラーポップアップウインドウ表示のためのマクロ （有引数）*/
#define GuiErrSpA(x) \
  GuiErrorStopPopup( x )
#define GuiErrCtA(x) \
  GuiErrorPopup( x )
#define GuiWarnA(x) \
  GuiWarningPopup( x )

/* エラー処理のためのマクロ */
#define GuiMacro(x) \
  if( (x == COM_NG) ) \
   switch( (int)ComErrorType ) {\
    case 0: GuiErrSp;return;\
    case 1: GuiErrCt;return;\
    case 2: GuiWarn;return;}


#define GuiMacroP(w,x) \
  GuiWait(w); \
  if( (x == COM_NG) ) {\
   GuiWaitClose();\
   switch( (int)ComErrorType ) {\
    case 0: GuiErrSp;return;\
    case 1: GuiErrCt;return;\
    case 2: GuiWarn;return;}}\
  GuiWaitClose();

/* 通信部のデータにアクセスするためのマクロ */
#define GuiCm(c) ((c *)(ComMessageInfo.message))
#define GuiCt ComMessageInfo.type

/* Stringをコピーするためのマクロ */
#define GuiStrCp(x,y) x=strcpy(XtMalloc(strlen(y)+1),y)

/* COMSTRINGをコピーするためのマクロ */
#define ComStringCp(x,t,r) \
  {\
    x = XtMalloc((strlen(GuiCm(t)->r)+1));\
    strcpy(x,GuiCm(t)->r);\
  }

/* COMLISTの最大数を求めるマクロ */
#define ComListMax(t,r,m) \
 {\
    int n = 0;\
    while(GuiCm(t)->r[n] != (char *)NULL)\
      n++;\
    m = n;\
  }

/* COMLISTをコピーするためのマクロ */
#define ComListCp(x,m,t,r) \
{\
  int i;\
  x = (char **)XtCalloc(m,sizeof(char *));\
  for(i = 0; i < m; i++) {\
    (x)[i] = XtMalloc((strlen((GuiCm(t)->r)[i])+1));\
    strcpy((x)[i],(GuiCm(t)->r)[i]);\
  }\
}

/* フォント設定のための識別子 */
#define GUI_F_BOLD24 "bold24"
#define GUI_F_BOLD24_B "-adobe-helvetica-bold-r-normal-*-24-*-*-*-*-*-*-*"
#define GUI_F_BOLD18 "bold18"
#define GUI_F_BOLD18_B "-adobe-helvetica-bold-r-normal-*-18-*-*-*-*-*-*-*"
#define GUI_F_ITAL14 "ital14"
#define GUI_F_ITAL14_B "-adobe-times-medium-i-normal-*-14-*-*-*-*-*-*-*"
#define GUI_F_ITAL18 "ital18"
#define GUI_F_ITAL18_B "-adobe-times-medium-i-normal-*-18-*-*-*-*-*-*-*"
#define GUI_F_ITAL34 "ital34"
#define GUI_F_ITAL34_B "-adobe-times-medium-i-normal-*-34-*-*-*-*-*-*-*"
#define GUI_F_MEDI18 "medi18"
#define GUI_F_MEDI18_B "-adobe-times-medium-r-normal-*-18-*-*-*-*-*-*-*"

/* 知識ベースファイルの接尾子の定義 */
#define TYPE_SUFFIX "*.t"
#define RULE_SUFFIX "*.r"
#define VIEW_SUFFIX "*.v"
#define QUERY_SUFFIX "*.g*"
#define COMMAND_SUFFIX "*.c"

/* 知識ベースファイルの種類の定義 */
#define FILE_TYPE_NUM 5
#define TYPE_FILE 0
#define RULE_FILE 1
#define VIEW_FILE 2
#define QUERRY_FILE 3
#define COMMAND_FILE 4

/* 論争の役割・当事者の定義 */
#define POS_NUM 2  /* 論争の当事者の数 */
#define PROSECUTOR 0
#define DEFENDANT 1
#define DRS 0 /* DRSを検察単体で動く論争として扱う */
#define SYSTEM 0
#define USER 1

/* 95.2.25 Add for showing current level */
/* 先読みの段数のデフォルト値 */
#define P_AHEAD 1  /* 検察(DNR) */
#define D_AHEAD 1  /* 被告 */

/* 通信部からの帰り値 */
#define COM_OK 0
#define COM_NG -1

/* 引数の修飾子 */
#define HELIC_ARG_DEBUG "-netdebug" /* 通信部へデバッグを指定する引数の文字 */
#define HELIC_ARG_HOST "-host" /* サーバーのホスト名 */
#define HELIC_ARG_PORT "-port" /* サーバーのポート番号 */

/******************/
/* 外部定数の定義 */
/******************/

/* GUIにて処理すべきデータがあるかどうかのフラグ
   Xのメインループにて参照する。 */
#ifdef MAIN
Boolean guiPending = False;
#else
extern Boolean guiPending;
#endif MAIN

/* ロードウインドウのtoggleの名前の定義 */
#ifdef MAIN
char *fileType[FILE_TYPE_NUM] = 
               { "Type", "Rule", "View", "Goal", "Command" }; /* 95.2.3 */
char loadFlag;
#else
extern char *fileType[];
extern char loadFlag;
#endif MAIN

/* ロード状況を示す変数 */
#ifdef MAIN
char loadFlag = 0x00;
/* (Goal)(View)(Rule)(Type) */
#else
extern char loadFlag;
#endif MAIN

/* 初期ウインドウにおけるロード状況の表示文字列 */
#ifdef MAIN
char *loadingStatusString[5] = 
{ "Type file hasn't been loaded yet.",
    "Rule file hasn't been loaded yet.",
    "View file hasn't been loaded yet.",
    "Query file hasn't been loaded yet.",
    "We can run a debate."};
int loadingStatus = 0;
#else
extern char *loadingStatusString[];
extern int loadingStatus;
#endif MAIN

/* 初期ウインドウにおける役割設定状況の表示文字列と役割設定状況変数 */
#ifdef MAIN
char *roleStatusString[5] = 
{ "Nothing Assigned\n",
    "Prosecutor is roled by System\nDefendant is roled by System.",
    "Prosecutor is roled by System\nDefendant is roled by User.",
    "Prosecutor is roled by User\nDefendant is roled by System.",
    "Prosecutor is roled by User\nDefendant is roled by User."};
int roleStatus = 0;
#else
extern char *roleStatusString[];
extern int roleStatus;
#endif MAIN

/* 役割設定のフラグ */
#ifdef MAIN
int roleAssign[2] = { -1, -1 };
/* roleAssign[PROSECUTOR] == USER という使い方 */
#else
extern int roleAssign[];
#endif MAIN

/******************/
/* 外部変数の定義 */
/******************/

/* 基本枠の定義 */
EXTERN XtAppContext application1;
EXTERN Display *display1;
EXTERN Widget toplevel;

Widget init_form;

/* 論争ウインドウ */
Widget dbtform[POS_NUM];
Widget dbtHis[POS_NUM], dbtView[POS_NUM], dbtGoal[POS_NUM];
Widget dbtStat[POS_NUM], dbtIss[POS_NUM], dbtArg[POS_NUM];

/* Font Listの定義 */

XmFontList GuiFontList;

/* XArgの定義 */

#define MAX_XARG 50
EXTERN Arg GuiXArg[MAX_XARG];
EXTERN int GuiXArgNum;
EXTERN Widget GuiXmW;

/**************/
/* 関数の定義 */
/**************/

EXTERN void GuiMainLoop();

/* UTIL関数の定義 */

#ifndef UTIL
extern void GuiXmAttachForm();
extern void GuiXmAttachPos();
extern void GuiXmAttachWidget();
extern Widget GuiXmCreateForm();
extern Widget GuiXmCreateSeparatorHorizontal();
extern Widget GuiXmCreateFrame();
extern Widget GuiXmCreateLabel();
extern Widget GuiXmCreateCheckBox();
extern Widget GuiXmCreateRadioBox();
extern Widget GuiXmCreateRowColumn();
extern Widget GuiXmCreateToggleButtonGadget();
extern Widget GuiXmCreateButton();
extern void GuiFontCreate();
extern Widget GuiXmCreateFormDialog();
extern void GuiMakeAndSetLabel();
extern Widget GuiXmCreateText();
extern void GuiXmTextAddString();
extern Widget GuiXmCreateTextField();
extern Widget GuiXmCreateScrolledList();
extern void GuiErrorStopPopup();
extern void GuiErrorPopup();
extern void GuiWarningPopup();
extern void GuiXmListAddItem();
extern Widget GuiXmCreateButtonGadget();
extern Widget GuiBuildPopupMenu();
extern Widget GuiXmCreateSelectionDialog();
extern void GuiShortLoop();
extern void GuiWait();
extern void GuiWaitClose();
#endif UTIL

/****************/
/* データベース */
/****************/

#define DB_INIT -1 /* データベースの初期値 */

#ifdef MAIN
/* 全ての判断基準 */
char **allStandPoint; /* 全ての判断基準の名前のリスト */
int allStandPoint_num = DB_INIT; /* 全ての判断基準の数 */

/* 全てのView候補 */
char **allViewCList; /* 全ての判断基準の名前のリスト */
int allViewCList_num = DB_INIT; /* 全ての判断基準の数 */

/* 現在設定しているユニット名 */
char **currentUnitList[POS_NUM];
int currentUnitList_num[POS_NUM] = { DB_INIT, DB_INIT };

/* 現在設定しているゴール */ 
short currentGoal[POS_NUM] = { DB_INIT, DB_INIT };

/* 全てのゴール候補 */
char **goalCandidateList;
int goalCandidateList_num = DB_INIT;

/* 現在設定されている価値感 */
char **currentView[POS_NUM];
int currentView_num[POS_NUM] = { DB_INIT, DB_INIT };

/* 表示論証、表示論証の親論証、フォーカス論証 */
char *displayedArgId[POS_NUM] = {(char *)NULL, (char *)NULL};
char *parentArgId[POS_NUM] = {(char *)NULL, (char *)NULL};
char *focusArgId[POS_NUM] = {(char *)NULL, (char *)NULL};

/* 95.2.25 Add for showing current level */
/* 現在設定されている先読みの段数 */
int d_ahead[2] = {P_AHEAD, D_AHEAD};  /* 検察(DNR) + 被告 */

#else
extern char **allStandPoint;
extern int allStandPoint_num;
extern char **allViewCList;
extern int allViewCList_num;
extern char **currentUnitList[];
extern int currentUnitList_num[];
extern short currentGoal[];
extern char **goalCandidateList;
extern int goalCandidateList_num;
extern char **currentView[];
extern int currentView_num[];
extern char *displayedArgId[]; 
extern char *parentArgId[];
extern char *focusArgId[];
extern int d_ahead[];
#endif MAIN
