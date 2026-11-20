/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#define STRINGSIZE 2052
#define STSIZE 1024
#define HSTSIZE 1024
#define VECTORSIZE 2048

typedef struct val1{
  int number ;
  char name1[16];
  char name2[128];
  char name3[16];
  struct val1 *next;
}val;

typedef struct {
  val *top;
  val *bottom;
}cont_val;

typedef struct ht1{
  int hnumber ;
  char *hname1;
  char *hname2;
  char *hname3;
  struct ht1 *hnext;
}ht;

typedef struct {
  ht *htop;
  ht *hbottom;
}cont_ht;

typedef struct st1{
  char *sname1;
  char *sname2;
  struct st1 *snext;
}st;

typedef struct {
  st *stop;
  st *sbottom;
}cont_st;


typedef struct cen1{
  char *cname1;
  char *cname2;
  char *cname3;
  struct cen1 *cnext;
}cen;

typedef struct {
  cen *ctop;
  cen *cbottom;
}cont_cen;

cont_val vtable;
cont_ht htable;
cont_st stable;
cont_cen ctable;






