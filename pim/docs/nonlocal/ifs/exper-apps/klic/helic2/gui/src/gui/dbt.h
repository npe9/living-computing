/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#ifdef DBTMAIN
#define DBTEXTERN
#else
#define DBTEXTERN extern
#endif DBTMAIN

/* ボタンの数の設定 */
#define TOP_NUM 6 /* 上部操作エリアのボタンの数 */ /* 95.2.20 Add for Depth */
#define MID_NUM 6 /* 中部操作エリアのボタンの数 */ 
#define BOT_NUM 9 /* 下部操作エリアのボタンの数 */ /* 95.1.17 Add for Form */

/* ウインドウの大きさ */
#define DBT_CLM 60 /* DBTの論証の幅 70 */ 
#define DBT_LINE 18 /* DBTの論証の行 18 */ 
#define DBT_STAT_ROW 3 /* Status情報の行の数 5 */
#define DBT_HIST_ROW 2 /* History情報の行の数 3 */
#define DBT_WIDTH 350
#define JST_WIDTH 200
#define NTS_WIDTH 200

/* ボタンWidget */
DBTEXTERN Widget topB[POS_NUM][TOP_NUM];
DBTEXTERN Widget midB[POS_NUM][MID_NUM];
DBTEXTERN Widget botB[POS_NUM][BOT_NUM];

DBTEXTERN Widget argSlct;

/* 論証説明ウインドウのテキストの大きさ */
#define EXP_WIDTH 400
#define EXP_HEIGHT 400

/* 論証説明表示ウインドウ */
DBTEXTERN Widget expW;

/* CBの宣言 */
void viewCB();
void unitCB();
void goalCB();
void startCB();
void quitCB();
void argSlctEndCB1();
void argSlctEndCB2();
void slctArgCB();
void poseCB();
void noticeCB();
void cancelCB();
void finishCB();
void justifyCB();
void endCB();
void endCB2();
void argLineCB();
void ctrLineCB();
void ctrCancelCB();
void spDoneCB();
void spCancelCB();
void spLineCB();
void noticeLineCB();
void noticeCancelCB();
void noticeOkCB();
void backwardCB();
void forwardCB();
void previousCB();
void nextCB();
void focusCB();
void jumpDoneCB();
void jumpCB();
void claimCB();
void explainCB();
void formCB();
void depthCB();

/* 論争ウインドウのボタンのセンシティビティ設定のための配列 */
#define SENS_NUM 14
Widget sensBut[POS_NUM][SENS_NUM];

