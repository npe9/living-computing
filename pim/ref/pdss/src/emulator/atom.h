/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#define	 NIL			 0
#define	 ATOM_DDD_SYSTEM	 1
#define	 ATOM_SUCCEEDED		 2
#define	 ATOM_ABORTED		 3
#define	 ATOM_REDUCTION_LIMIT	 4
#define	 ATOM_EXCEPTION		 5
#define	 ATOM_RAISED		 6
#define	 ATOM_DEADLOCK		 7
#define	 ATOM_MERGE		 8

#define	 ATOM_COMMA		 9  /* ',' */
#define	 ATOM_COLON		10  /* ':' */
#define	 ATOM_VLINE		11  /* '|' */
#define	 ATOM_EXCLAMATION	12  /* '!' */
#define	 ATOM_PAREN_L		13  /* '(' */
#define	 ATOM_PAREN_R		14  /* ')' */
#define	 ATOM_BRANKET_L		15  /* '[' */
#define	 ATOM_BRANKET_R		16  /* ']' */
#define	 ATOM_BRACE_L		17  /* '{' */
#define	 ATOM_BRACE_R		18  /* '}' */
#define	 ATOM_PLUS		19  /* '+' */
#define	 ATOM_MINUS		20  /* '-' */

#define	 ATOM_ATOM		21  /* atom */
#define	 ATOM_INTEGER		22  /* integer */
#define	 ATOM_FLOAT		23  /* float */
#define	 ATOM_STRING		24  /* string */
#define	 ATOM_OPEN		25  /* open */
#define	 ATOM_SIGN		26  /* sign */
#define	 ATOM_END		27  /* end */
#define	 ATOM_ILLEGAL		28  /* illegal */
#define	 ATOM_D_VAR		29  /* '$VAR'  */
#define	 ATOM_D_SHOEN		30  /* '$SHOEN'	 */
#define	 ATOM_D_NUE		31  /* '$NUE'  */


/** KL1 Constant **/
extern CELL const_nil;
extern CELL const_atom_succeeded;
extern CELL const_atom_aborted;
extern CELL const_atom_reduction_limit;
extern CELL const_atom_raised;
extern CELL const_atom_exception;
extern CELL const_atom_deadlock;
extern CELL const_atom_merge;
extern CELL const_atom_colon;
extern CELL const_atom_atom;
extern CELL const_atom_integer;
extern CELL const_atom_float;
extern CELL const_atom_string;
extern CELL const_atom_open;
extern CELL const_atom_sign;
extern CELL const_atom_end;
extern CELL const_atom_illegal;
extern CELL const_atom_d_var;
extern CELL const_atom_d_shoen;
