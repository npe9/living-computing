/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

extern unsigned short ctype_table[256];

#define	 BLANK	     0x0100
#define	 DIGIT	     0x0200
#define	 UPPER_CASE  0x0400
#define	 LOWER_CASE  0x0800
#define	 SYMBOL	     0x1000
#define	 SPECIAL     0x2000

#define	 IsBlank(chr)  (ctype_table[(chr)&0xFF]&BLANK)
#define	 IsDigit(chr)  (ctype_table[(chr)&0xFF]&DIGIT)
#define	 IsAlpha(chr)  (ctype_table[(chr)&0xFF]&(UPPER_CASE+LOWER_CASE))
#define	 IsUpper(chr)  (ctype_table[(chr)&0xFF]&UPPER_CASE)
#define	 IsLower(chr)  (ctype_table[(chr)&0xFF]&LOWER_CASE)
#define	 IsAlNum(chr)  (ctype_table[(chr)&0xFF]&(UPPER_CASE+LOWER_CASE+DIGIT))
#define	 IsSymbol(chr)	(ctype_table[(chr)&0xFF]&SYMBOL)
#define	 IsSpcial(chr)	(ctype_table[(chr)&0xFF]&SPECIAL)
#define	 GetCharType(chr)  (ctype_table[(chr)&0xFF]&0xFF00)
#define	 GetDigitValue(chr)  (ctype_table[(chr)&0xFF]&0xFF)
/** If GetDigitValue(chr) macro return 0xFF, chr is not digit charactor. **/
