/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdlib.h>
#include <Xm/Form.h>

#include "gui.h"
#include "messages.h"
#include "commands.h"

void GuiComInit(int argc, char **argv)
/* 通信部の起動処理。ソケット情報の獲得などを行なう */
/* 95.1.18 for Extended Argument which are host and port */
{
  char *hostname = (char *)NULL;
  struct hostent *hostinfo;
  struct sockaddr_in server;
  int result;
  int port = 0;
  int debug = 0;
  char **arg;
  int i;

  if (argc > 1) {
    /* 引数あり */
    i = 1;
    while( i < argc ) {
      if ( strcmp(argv[i],HELIC_ARG_DEBUG) == 0 ) 
	/* デバッグ引数 */
	debug = atoi(argv[++i]);
      else if ( strcmp(argv[i],HELIC_ARG_HOST) == 0 ) {
	i++;
	GuiStrCp(hostname, argv[i]);
      }
      else if ( strcmp(argv[i],HELIC_ARG_PORT) == 0 ) {
	port = atoi(argv[++i]);
      }
      else {
	GuiErrorStopPopup("Command arg error\n");
      }
      i++;
    }
  }

  if (port == 0) {
    if ( getenv("HELIC_HOST_PORT") == NULL ) {
      GuiErrorStopPopup("No PORT assigned\n");
    } else {
      port = atoi( getenv("HELIC_HOST_PORT") );
    }  
  }
  if (hostname == (char *)NULL) 
    if ( (hostname = getenv("HELIC_HOST_NAME")) == NULL ) 
      GuiErrorStopPopup("No HOST assigned\n");

  hostinfo = gethostbyname(hostname,strlen(hostname));
  bzero( (char *)&server, sizeof(server));
  server.sin_family = AF_INET;
  server.sin_port = port;
  bcopy(hostinfo->h_addr, 
	(char *)&server.sin_addr, hostinfo->h_length);

#ifdef DEBUG
  printf("h_addr = %u.%u.%u.%u\ndebug = %d\n",
	 (u_char)hostinfo->h_addr[0],
	 (u_char)hostinfo->h_addr[1],
	 (u_char)hostinfo->h_addr[2],
	 (u_char)hostinfo->h_addr[3], debug);
#endif DEBUG


  GuiMacro(ComInit(&server, debug));

}

void GuiEnd()
/* new HelicIIの終了処理。ソケットの閉鎖を行なう */
{
  GuiMacro(ComClose());
  exit(0);
}

Boolean GuiPending()
{
  if(guiPending) {
    guiPending = False;
    return True;
  } else
    return False;
}

void GuiPendingOn()
{
  guiPending = True;
}

int GuiComFileLoad(char *file, int type)
/* 知識ベースファイルのロード処理 */
{
  switch(type) {
  case 0: 
    /* TYPE */
    GuiMacroP(init_form,ComLoadType(PROSECUTOR,file));
    break;
  case 1: 
    /* RULE */
    GuiMacroP(init_form,ComLoadRule(PROSECUTOR,file));
    break;
  case 2:
    /* VIEW */
    GuiMacroP(init_form,ComLoadView(PROSECUTOR,file));
    break; 
  case 3:
    /* QUERY */
    GuiMacroP(init_form,ComLoadQuery(PROSECUTOR,file));
    break;
  case 4:
    /* COMMAND */
    GuiMacroP(init_form,ComLoadCommand(PROSECUTOR,file));
    break;
  }
  loadFlag = ((MessageC *)(ComMessageInfo.message))->arg2;
  return(COM_OK);
}
