/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*                                            */
/* Header File for Debate-Window & RBR-Window */
/*                                            */

#define START_SOLVE 3 /* index of both START and SOLVE */
#define DRS_NAME "Defeasible Reasoning System"

#ifdef DBTMAIN

/* 役割の名前 */
char *posS[POS_NUM] = { "Prosecutor", "Defendant" };
/* ボタンの名前 */
/* 95.2.20 Add for Depth */
char *topS[TOP_NUM] = { "View", "Unit", "Goal", "Start", "Depth", "Quit"};
char *midS[MID_NUM] = { "Pose", "Notice", "Cancel", "Finish",
			      "Justify", "End" }; 
char *botS[BOT_NUM] = { "Backward", "Forward", "Next", "Previous",
	      "Focus", "Jump", "ClaimList", "Explain", "Form"}; /* 95.1.17 */
/* 95.2.20 Add for Depth */
void (*topC[TOP_NUM])() = { viewCB, unitCB, goalCB, startCB, depthCB, quitCB };
void (*midC[MID_NUM])() = { poseCB, noticeCB, cancelCB, finishCB, justifyCB,
			      endCB };
void (*botC[BOT_NUM])() = { backwardCB, forwardCB, nextCB, previousCB, 
			      focusCB, jumpCB, claimCB, explainCB, formCB };
			      
/* 反論選定ウインドウ */
Widget ctrSlct;
/* 価値観変更ウインドウ */
Widget spSlct, spSlctS, spSlctV;
Widget noticeSlct, noticeSlctS;

/* Temporary Area */
char **recvCTtmp; /* counter listで確保したchar **。終了時に解放 */
int recvCTmax; /* 上記recvCTtmpの要素数 */
char **recvCT2tmp; /* counter listで確保したchar **。終了時に解放 */
int recvCT2max; /* 上記recvCT2tmpの要素数 */
char **recvVCtmp; /* receive justifyで確保したchar **。終了時に解放 */
int recvVCmax; /* 上記recvVCtmpの要素数 */
char **recvVC2tmp; /* receive justifyで確保したchar **。終了時に解放 */
int recvVC2max; /* 上記recvVC2tmpの要素数 */
int recvRSmax; /* receive argument listの要素数 */

/* Browse Mode Flag */

Boolean browseMode = False;

#else

extern char *posS[];
extern char *topS[];
extern char *midS[];
extern char *botS[];
extern void (*topC[])();
extern void (*midC[])();
extern void (*botC[])();
extern Widget ctrSlct;
extern Widget spSlct, spSlctS, spSlctV;
extern Widget noticeSlct, noticeSlctS;
extern Widget expW;
extern char **recvCTtmp;
extern int recvCTmax; 
extern char **recvCT2tmp;
extern int recvCT2max; 
extern char **recvVCtmp;
extern int recvVCmax; 
extern char **recvVC2tmp;
extern int recvVC2max; 
extern int recvRSmax; 

extern Boolean browseMode;

#endif DBTMAIN
