/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "ctype.h"

#define shift_left(x, w) \
    (((w) >= -31 && (w) <= 31) ? ((unsigned int)(x) << (w)) : 0)
#define shift_right(x, w) \
    (((w) >= -31 && (w) <= 31) ? ((unsigned int)(x) >> (w)) : 0)

CHAR string_work_buffer[MAX_PRINTABLE_STRING_ATOM_LENGTH];
#define IsStringTooLong(p) \
    ((p)-string_work_buffer >= MAX_PRINTABLE_STRING_ATOM_LENGTH)

static CELL const_int0 = {INT, MRBOFF, 0};


/*************************************************************************
*   Get String Type (Length & Element Size).				 *
*************************************************************************/

int get_string_type(CELL *string, int *length, int *width)
{
    register int leng, type, widt, rest;
    leng = StringLengthof(string);
    type = StringTypeof(string);
    widt = (1<<(type&7))+(type>>(8-(type&7)));
    rest = (type&(0xFF>>(type&7)))>>3;
    *length = leng*(32/widt)-rest;
    *width = widt;
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Create New String.							 *
*************************************************************************/

int new_string(int length, int width, CELL *string)
{
    register CELL *p;
    register int leng, elms, rest;
    register uint32_t desc = 0;	/* MODERN: was int; (width<<31) overflowed */
    if(width < 1 || width > 32) return(STRUTL_BAD_WIDTH);
    elms = 32/width;
    leng = (length+elms-1)/elms;
    if(length < 0 || leng >= heap_size) return(STRUTL_BAD_LENGTH);
    if(HeapRest() <= leng) return(STRUTL_REQUEST_GC);
    rest = leng*elms-length;
    switch(width){
      case 1:
	desc = ((uint32_t)rest<<27)|leng;
	break;
      case 2: case 3:
	desc = ((uint32_t)width<<31)|((uint32_t)rest<<27)|0x01000000|leng;
	break;
      case 4: case 5: case 6: case 7:
	desc = ((uint32_t)width<<30)|((uint32_t)rest<<27)|0x02000000|leng;
	break;
      case 8: case 9: case 10: case 11: case 12: case 13: case 14: case 15:
	desc = ((uint32_t)width<<29)|((uint32_t)rest<<27)|0x03000000|leng;
	break;
      case 16: case 17: case 18: case 19: case 20: case 21: case 22: case 23:
      case 24: case 25: case 26: case 27: case 28: case 29: case 30: case 31:
	desc = ((uint32_t)width<<28)|((uint32_t)rest<<27)|0x04000000|leng;
	break;
      case 32:
	desc = 0x05000000|leng;
	break;
    }
    AllocString(p, leng);
    SetAll(string, STRING, p, MRBOFF);
    SetAll(p, DESC, desc, MRBOFF);
    while(leng--) *++p = const_int0;
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Copy String.							 *
*************************************************************************/

int copy_string(CELL *string, CELL *newstr)
{
    register CELL *p, *q;
    register int leng;
    leng = StringLengthof(string);
    if(HeapRest() <= leng) return(STRUTL_REQUEST_GC);
    p = Objectof(string);
    AllocString(q, leng);
    SetAll(newstr, STRING, q, MRBOFF);
    SetAll(q, DESC, Valueof(p), MRBOFF);
    while(leng--){ q++; p++; *q = *p; }
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Get/Set String Element.						 *
*************************************************************************/

int get_string_element(CELL *string, int position, int *element)
{
    CELL *p;
    register int leng, type, width, mask, elms, rest;
    leng = StringLengthof(string);
    type = StringTypeof(string);
    if((type&0xE7) == 0x03){
	/*** 8 bits string ***/
	rest = (type&0x1F)>>3;
	if(position < 0 || position >= leng*4-rest)
	    return(STRUTL_BAD_POSITION);
	p = Objectof(string)+1+(position/4);
	*element = (Valueof(p)>>((position%4)*8))&0xFF;
    }else{
	width = (1<<(type&7))+(type>>(8-(type&7)));
	mask = ((unsigned int)0xFFFFFFFF)>>(32-width);
	elms = 32/width;
	rest = (type&(0xFF>>(type&7)))>>3;
	if(position < 0 || position >= leng*elms-rest)
	    return(STRUTL_BAD_POSITION);
	p = Objectof(string)+1+(position/elms);
	*element = (Valueof(p)>>((position%elms)*width))&mask;
    }
    return(STRUTL_SUCCESS);
}

int set_string_element(CELL *string, int position, int element)
{
    CELL *p;
    register int leng, type, width, mask, elms, rest;
    register uint32_t ux;		/* MODERN: was int x; shifts overflowed */
    leng = StringLengthof(string);
    type = StringTypeof(string);
    if((type&0xE7) == 0x03){
	/*** 8 bits string ***/
	rest = (type&0x1F)>>3;
	if(position < 0 || position >= leng*4-rest)
	    return(STRUTL_BAD_POSITION);
	p = Objectof(string)+1+(position/4);
	ux = (uint32_t)Valueof(p)&(~(0xFFu<<((position%4)*8)));
	Valueof(p) = pdss_s32(ux|(((uint32_t)element&0xFFu)<<((position%4)*8)));
    }else{
	width = (1<<(type&7))+(type>>(8-(type&7)));
	mask = ((unsigned int)0xFFFFFFFF)>>(32-width);
	elms = 32/width;
	rest = (type&(0xFF>>(type&7)))>>3;
	if(position < 0 || position >= leng*elms-rest)
	    return(STRUTL_BAD_POSITION);
	p = Objectof(string)+1+(position/elms);
	ux = (uint32_t)Valueof(p)&(~((uint32_t)mask<<((position%elms)*width)));
	Valueof(p) = pdss_s32(ux|(((uint32_t)element&(uint32_t)mask)<<((position%elms)*width)));
    }
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Get/Set Sub String.							 *
*************************************************************************/

int get_substring(CELL *string, int position, int length, CELL *substr)
{
    register CELL *p, *q;
    int leng, leng2, width, elms;
    {
	register int type, rest, type2, rest2;
	leng = StringLengthof(string);
	type = StringTypeof(string);
	width = (1<<(type&7))+(type>>(8-(type&7)));
	elms = 32/width;
	rest = (type&(0xFF>>(type&7)))>>3;
	if(position < 0 || position > leng*elms-rest)
	    return(STRUTL_BAD_POSITION);
	if(length < 0 || position+length > leng*elms-rest)
	    return(STRUTL_BAD_LENGTH);
	leng2 = (length+elms-1)/elms;
	if(HeapRest() <= leng2)
	    return(STRUTL_REQUEST_GC);
	rest2 = leng2*elms-length;
	type2 = (type&(~((0xFF>>(type&7))&0xF8)))|(rest2<<3);
	p = Objectof(string)+1+(position/elms);
	AllocString(q, leng2);
	SetAll(substr, STRING, q, MRBOFF);
	SetAll(q, DESC, (type2<<24)|leng2, MRBOFF); q++;
    }
    if(length > 0){
	int w1 = position%elms;
	if(w1 == 0){
	    register int l = --leng2;
	    register unsigned int m;
	    while(l--){ *q = *p; q++; p++; }
	    m = shift_right(0xFFFFFFFF, 32-(length-leng2*elms)*width);
	    SetAll(q, INT, Valueof(p)&m, MRBOFF);
	}else{
	    register unsigned int x, y, m;
	    register int w2, s1, s2;
	    w2 = elms-w1;
	    s1 = w1*width;
	    s2 = w2*width;
	    m = shift_right(0xFFFFFFFF, 32-s1-s2);
	    x = Valueof(p); p++;
	    while(length >= elms){
		y = (x&m)>>s1;
		x = Valueof(p); p++;
		SetAll(q, INT, y|(x<<s2), MRBOFF); q++;
		length -= elms;
	    }
	    if(length > w2){
		y = (x&m)>>s1;
		x = Valueof(p); p++;
		m = shift_right(0xFFFFFFFF, 32-length*width);
		SetAll(q, INT, (y|(x<<s2))&m, MRBOFF); q++;
	    }else if(length > 0){
		m = shift_right(0xFFFFFFFF, 32-length*width);
		SetAll(q, INT, (x>>s1)&m, MRBOFF);
	    }
	}
    }
    return(STRUTL_SUCCESS);
}    

int set_substring(CELL *string, int position, CELL *substr)
{
    register CELL *p, *q;
    int length, leng, leng2, width, elms;
    {
	register int type, rest, type2, rest2;
	leng = StringLengthof(string);
	type = StringTypeof(string);
	width = (1<<(type&7))+(type>>(8-(type&7)));
	elms = 32/width;
	rest = (type&(0xFF>>(type&7)))>>3;
	leng2 = StringLengthof(substr);
	type2 = StringTypeof(substr);
	if(width != (1<<(type2&7))+(type2>>(8-(type2&7))))
	    return(STRUTL_BAD_TYPE);
	rest2 = (type2&(0xFF>>(type2&7)))>>3;
	length = leng2*elms-rest2;
	if(position < 0 || position > leng*elms-rest)
	    return(STRUTL_BAD_POSITION);
	if(position+length > leng*elms-rest)
	    return(STRUTL_BAD_LENGTH);
	p = Objectof(string)+1+(position/elms);
	q = Objectof(substr)+1;
    }
    if(length > 0){
	int w1 = position%elms;
	if(w1 == 0){
	    while(length >= elms){
		*p = *q; p++; q++;
		length -= elms;
	    }
	    if(length > 0){
		register unsigned int x;
		x=(Valueof(p)&((unsigned int)0xFFFFFFFF<<(length*width)))
		 |(Valueof(q)&((unsigned int)0xFFFFFFFF>>(32-(length*width))));
		Valueof(p) = x;
	    }
	}else{
	    register unsigned int x, y, m, n;
	    register int w2, s1, s2;
	    w2 = elms-w1;
	    s1 = w1*width;
	    s2 = w2*width;
	    if(length > w2){
		m = shift_right(0xFFFFFFFF, 32-s1-s2);
		x = Valueof(q); q++;
		n = (unsigned int)0xFFFFFFFF>>(32-s1);
		Valueof(p) = (Valueof(p)&n)|(x<<s1); p++;
		length -= w2;
		while(length >= elms){
		    y = (x&m)>>s2;
		    x = Valueof(q); q++;
		    y |= x<<s1;
		    Valueof(p) = y; p++;
		    length -= elms;
		}
		if(length > w1){
		    y = (x&m)>>s2;
		    x = Valueof(q);
		    y |= x<<s1;
		}else{
		    y = x>>s2;
		}
		n = (unsigned int)0xFFFFFFFF<<(length*width);
		Valueof(p) = (Valueof(p)&n)|(y&(~n));
	    }else{
		x = Valueof(q);
		n = shift_left(0xFFFFFFFF, s1+length*width)
		   |((unsigned int)0xFFFFFFFF>>(32-s1));
		Valueof(p) = (Valueof(p)&n)|((x<<s1)&(~n));
	    }
	}
    }
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Append 2 Strings.							 *
*************************************************************************/

int append_string(CELL *string1, CELL *string2, CELL *newstr)
{
    register CELL *p, *q;
    int length1, length2, leng1, leng2, width, elms;
    {
	int type1, type2, rest1, rest2;
	leng1 = StringLengthof(string1);
	type1 = StringTypeof(string1);
	width = (1<<(type1&7))+(type1>>(8-(type1&7)));
	elms = 32/width;
	rest1 = (type1&(0xFF>>(type1&7)))>>3;
	length1 = leng1*elms-rest1;
	leng2 = StringLengthof(string2);
	if(HeapRest() <= leng1+leng2) return(STRUTL_REQUEST_GC);
	type2 = StringTypeof(string2);
	if(width != (1<<(type2&7))+(type2>>(8-(type2&7))))
	    return(STRUTL_BAD_TYPE);
	rest2 = (type2&(0xFF>>(type2&7)))>>3;
	length2 = leng2*elms-rest2;
	{
	    register int leng, type, rest;
	    leng = (length1+length2+elms-1)/elms;
	    rest = leng*elms-(length1+length2);
	    type = (type1&(~((0xFF>>(type1&7))&0xF8)))|(rest<<3);
	    p = Objectof(string1);
	    AllocString(q, leng);
	    SetAll(newstr, STRING, q, MRBOFF);
	    SetAll(q, DESC, (type<<24)|leng, MRBOFF);
	    while(leng1--){ q++; p++; *q = *p; }
	}
	if(length2 > 0){
	    int w1 = length1%elms;
	    if(w1 == 0){
		p = Objectof(string2);
		while(leng2--){ q++; p++; *q = *p; }
	    }else{
		register unsigned int  x, y, m, n;
		register int  w2, s1, s2;
		w2 = elms-w1;
		s1 = w1*width;
		s2 = w2*width;
		p = Objectof(string2)+1;
		if(length2 > w2){
		    m = shift_right(0xFFFFFFFF, 32-s1-s2);
		    x = Valueof(p); p++;
		    n = (unsigned int)0xFFFFFFFF>>(32-s1);
		    Valueof(q) = (Valueof(q)&n)|(x<<s1); q++;
		    length2 -= w2;
		    while(length2 > elms){
			y = (x&m)>>s2;
			x = Valueof(p); p++;
			y |= x<<s1;
			SetAll(q, INT, y, MRBOFF); q++;
			length2 -= elms;
		    }
		    if(length2 > w1){
			y = (x&m)>>s2;
			x = Valueof(p); p++;
			y |= x<<s1;
		    }else{
			y = x>>s2;
		    }
		    SetAll(q, INT, y, MRBOFF);
		}else{
		    x = Valueof(p);
		    n = (unsigned int)0xFFFFFFFF>>(32-s1);
		    Valueof(q) = (Valueof(q)&n)|(x<<s1);
		}
	    }
	}
    }
    return(STRUTL_SUCCESS);
}    


/*************************************************************************
*   String AND.								 *
*************************************************************************/

int string_and(CELL *string1, CELL *string2, CELL *newstr, CELL *newstr2)
{
    register CELL *p, *q, *r;
    int length;
    p = Objectof(string1);
    q = Objectof(string2);
    if(Valueof(p) != Valueof(q)) return(STRUTL_BAD_TYPE);
    length = Valueof(p)&0xFFFFFF;
    if(Mrbof(string1) == MRBOFF){
	r = p;
    }else{
	if(HeapRest() <= length) return(STRUTL_REQUEST_GC);
	AllocString(r, length);
	*r = *p;
    }
    SetAll(newstr, STRING, r, MRBOFF);
    *newstr2 = *string2;
    while(length-- > 0){
	p++; q++; r++;
	SetAll(r, INT, Valueof(p)&Valueof(q), MRBOFF);
    }
    return(STRUTL_SUCCESS);
}    


/*************************************************************************
*   String OR.								 *
*************************************************************************/

int string_or(CELL *string1, CELL *string2, CELL *newstr, CELL *newstr2)
{
    register CELL *p, *q, *r;
    int length;
    p = Objectof(string1);
    q = Objectof(string2);
    if(Valueof(p) != Valueof(q)) return(STRUTL_BAD_TYPE);
    length = Valueof(p)&0xFFFFFF;
    if(Mrbof(string1) == MRBOFF){
	r = p;
    }else{
	if(HeapRest() <= length) return(STRUTL_REQUEST_GC);
	AllocString(r, length);
	*r = *p;
    }
    SetAll(newstr, STRING, r, MRBOFF);
    *newstr2 = *string2;
    while(length-- > 0){
	p++; q++; r++;
	SetAll(r, INT, Valueof(p)|Valueof(q), MRBOFF);
    }
    return(STRUTL_SUCCESS);
}    


/*************************************************************************
*   String Exclusive_OR.						 *
*************************************************************************/

int string_exclusive_or(CELL *string1, CELL *string2, CELL *newstr, CELL *newstr2)
{
    register CELL *p, *q, *r;
    int length;
    p = Objectof(string1);
    q = Objectof(string2);
    if(Valueof(p) != Valueof(q)) return(STRUTL_BAD_TYPE);
    length = Valueof(p)&0xFFFFFF;
    if(Mrbof(string1) == MRBOFF){
	r = p;
    }else{
	if(HeapRest() <= length) return(STRUTL_REQUEST_GC);
	AllocString(r, length);
	*r = *p;
    }
    SetAll(newstr, STRING, r, MRBOFF);
    *newstr2 = *string2;
    while(length-- > 0){
	p++; q++; r++;
	SetAll(r, INT, Valueof(p)^Valueof(q), MRBOFF);
    }
    return(STRUTL_SUCCESS);
}    


/*************************************************************************
*   String Complement.							 *
*************************************************************************/

int string_complement(CELL *string, CELL *newstr)
{
    register CELL *p, *q;
    int length;
    p = Objectof(string);
    length = Valueof(p)&0xFFFFFF;
    if(Mrbof(string) == MRBOFF){
	q = p;
    }else{
	if(HeapRest() <= length) return(STRUTL_REQUEST_GC);
	AllocString(q, length);
	*q = *p;
    }
    SetAll(newstr, STRING, q, MRBOFF);
    while(length-- > 0){
	p++; q++;
	SetAll(q, INT, ~Valueof(p), MRBOFF);
    }
    return(STRUTL_SUCCESS);
}    


/*************************************************************************
*   Convert Atom <--> String.						 *
*************************************************************************/

int atom_to_string(unsigned int atom, CELL *string)
{
    register CELL *p;
    register CHAR *str;
    register int x, leng, rest, length, desc;
    str = atom_name(atom);
    length = strlen(str);
    leng = (length+3)/4;
    if(HeapRest() <= leng) return(STRUTL_REQUEST_GC);
    rest = leng*4-length;
    desc = (rest<<27)|0x03000000|leng;
    AllocString(p, leng);
    SetAll(string, STRING, p, MRBOFF);
    SetAll(p, DESC, desc, MRBOFF);
    while(leng-- > 1){
	p++;
	x = (*str++);
	x |= (*str++)<<8;
	x |= (*str++)<<16;
	x |= (*str++)<<24;
	SetAll(p, INT, x, MRBOFF);
    }
    if(leng >= 0){
	p++;
	x = (*str++);
	if(rest <= 2){
	    x |= (*str++)<<8;
	    if(rest <= 1){
		x |= (*str++)<<16;
		if(rest <= 0){
		    x |= (*str++)<<24;
		}
	    }
	}
	SetAll(p, INT, x, MRBOFF);
    }
    return(STRUTL_SUCCESS);
}

int string_to_atom(CELL *string, unsigned int *atom)
{
    register CELL *p;
    register CHAR *s;
    register int x, rest, leng, type;
    CHAR *str;
    leng = StringLengthof(string);
    type = StringTypeof(string);
    if((type&0xE7) != 0x03) return(STRUTL_BAD_TYPE);
    rest = (type>>3)&3;
    s = str = string_work_buffer;
    p = Objectof(string)+1;
    while(leng-- > 1){
	if(IsStringTooLong(s+9)) goto string_done;
	x = Valueof(p++);
	*s++ = x;
	*s++ = x>>8;
	*s++ = x>>16;
	*s++ = x>>24;
    }
    if(leng >= 0){
	x = Valueof(p);
	*s++ = x;
	if(rest <= 2){
	    *s++ = x>>8;
	    if(rest <= 1){
		*s++ = x>>16;
		if(rest <= 0){
		    *s++ = x>>24;
		}
	    }
	}
    }
  string_done:
    *s = 0;
    *atom = intern_atom(str);
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Make Print Image String.						 *
*************************************************************************/

int get_print_image(CELL *atomic, int mode, int left, CELL *string, int *sleng, int *tail)
    /* in:	atomic data */
    /* in:	print mode: 0 -> write, 1 -> writeq */
    /* in:	left character of atomic */
    /* out: print image "string" (8bits) */
    /* out: length if "string" */
    /* out: tail character of "string" */
{
    register CELL *p;
    register CHAR *s1, *s2, *str;
    register int x, leng, rest, length, desc;
    int32_t  fw;

    switch(Typeof(atomic)){
      case INT:
	str = string_work_buffer;
	if(IsAlNum(left) || (IsSymbol(left) && Valueof(atomic) < 0)
			 || left == '-' || left == '+'){
	    sprintf(str, " %d", (int)Valueof(atomic));
	}else{
	    sprintf(str, "%d", (int)Valueof(atomic));
	}	
	length = strlen(str);
	*sleng = length;
	*tail = str[length-1];
	break;
      case FLOAT:
	str = string_work_buffer;
	fw = Valueof(atomic);
	if(IsAlNum(left) || (IsSymbol(left) && fw < 0)
			 || left == '-' || left == '+'){
	    sprintf(str, " %s", float_to_string(&fw));
	}else{
	    sprintf(str, "%s", float_to_string(&fw));
	}	
	length = strlen(str);
	*sleng = length;
	*tail = str[length-1];
	break;
      case ATOM:
	s1 = atom_name(Valueof(atomic));
	length = strlen(s1);
	if(mode == 0){
	    if((IsAlNum(left) && IsAlNum(*s1)) ||
	       (IsSymbol(left) && IsSymbol(*s1))){
		str = s2 = string_work_buffer;
		*s2++ = ' ';
		while(*s1 && !IsStringTooLong(s2+1)) *s2++ = *s1++;
		*sleng = ++length;
		*tail = str[length-1];
	    }else{
		str = s1;
		*sleng = length;
		*tail = (length == 0) ? left : str[length-1];
	    }
	}else{
	    str = string_work_buffer;
	    s2 = str+2;
	    if(IsLower(*s1)){
		*s2++ = *s1++;
		while(*s1 && !IsStringTooLong(s2+3)){
		    if(IsAlNum(*s1)){
			*s2++ = *s1++;
		    }else{
			goto quoted;
		    }
		}
		str++;
	    }else if(IsSymbol(*s1)){
		*s2++ = *s1++;
		while(*s1 && !IsStringTooLong(s2+3)){
		    if(IsSymbol(*s1)){
			*s2++ = *s1++;
		    }else{
			goto quoted;
		    }
		}
		str++;
	    }else if(IsSpcial(*s1)){
		if(s1[0] == '[' && s1[1] == ']' && s1[2] == 0){
		    *s2++ = *s1++;
		    *s2++ = *s1++;
		}else if((s1[0]==',' || s1[0]=='|' || s1[0]=='!') && s1[1]==0){
		    *s2++ = *s1++;
		}else{
		    goto quoted;
		}
		str++;
	    }else{
	  quoted:
		str[1] = '\'';
		while(*s1 && !IsStringTooLong(s2+5)){
		    if(*s1 == '\''){
			*s2++ = '\'';
			*s2++ = '\'';
			s1++;
		    }else{
			*s2++ = *s1++;
		    }
		}
		*s2++ = '\'';
	    }
	    if((IsAlNum(left) && IsAlNum(str[1])) ||
	       (IsDigit(left) && str[1]=='\'') ||
	       (IsSymbol(left) && IsSymbol(str[1])) || (left == str[1])){
		 str[0] = ' ';
	    }else{
		str++;
	    }
	    length = s2-str;
	    *sleng = length;
	    *tail = *--s2;
	}
	break;
      case STRING:
	leng = StringLengthof(atomic);
	rest = (StringTypeof(atomic)>>3)&3;
	str = s2 = string_work_buffer;
	if(left == '"') *s2++ = ' ';
	*s2++ = '"';
	atomic = Objectof(atomic)+1;
	while(leng-- > 1){
	    if(IsStringTooLong(s2+17)) goto string_done;
	    x = Valueof(atomic++);
	    if((*s2++ = x) == '"') *s2++ = '"';
	    if((*s2++ = x>>8) == '"') *s2++ = '"';
	    if((*s2++ = x>>16) == '"') *s2++ = '"';
	    if((*s2++ = x>>24) == '"') *s2++ = '"';
	}
	if(leng>=0){
	    x = Valueof(atomic);
	    if((*s2++ = x) == '"') *s2++ = '"';
	    if(rest<3){
		if((*s2++ = x>>8) == '"') *s2++ = '"';
		if(rest<2){
		    if((*s2++ = x>>16) == '"') *s2++ = '"';
		    if(rest<1){
			if((*s2++ = x>>24) == '"') *s2++ = '"';
		    }
		}
	    }
	}
      string_done:
	*s2++ = '"';
	length = s2-str;
	*sleng = length;
	*tail = str[length-1];
	break;
    }
    leng = (length+3)/4;
    if(HeapRest() <= leng) return(STRUTL_REQUEST_GC);
    rest = leng*4-length;
    desc = (rest<<27)|0x03000000|leng;
    AllocString(p, leng);
    SetAll(string, STRING, p, MRBOFF);
    SetAll(p, DESC, desc, MRBOFF);
    while(leng-- > 1){
	p++;
	x = (*str++);
	x |= (*str++)<<8;
	x |= (*str++)<<16;
	x |= (*str++)<<24;
	SetAll(p, INT, x, MRBOFF);
    }
    if(leng >= 0){
	p++;
	x = (*str++);
	if(rest <= 2){
	    x |= (*str++)<<8;
	    if(rest <= 1){
		x |= (*str++)<<16;
		if(rest <= 0){
		    x |= (*str++)<<24;
		}
	    }
	}
	SetAll(p, INT, x, MRBOFF);
    }
    return(STRUTL_SUCCESS);
}


/*************************************************************************
*   Convert KL1-String <--> C-String.					 *
*************************************************************************/

CELL *convert_to_kl1_string(register CHAR *string)
{
    register CELL *kl1str, *v;
    register int len, n, rest, desc;
    len = strlen(string);
    n = (len+3)/4;
    rest = n*4-len;
    desc = (rest<<27)|0x03000000|n;
    AllocString(kl1str, n);
    SetAll(kl1str, DESC, desc, MRBOFF);
    v = kl1str+1;
    while(len-- > 0){
	n = (*string++)&0xFF;
	if(len-- > 0){
	    n |= ((*string++)&0xFF)<<8;
	    if(len-- > 0){
		n |= ((*string++)&0xFF)<<16;
		if(len-- > 0){
		    n |= ((*string++)&0xFF)<<24;
		}
	    }
	}
	SetAll(v, INT, n, MRBOFF);
	v++;
    }
    return(kl1str);
}

CELL *convert_to_kl1_string2(register CHAR *string, register int len)
{
    register CELL *kl1str, *v;
    register int n, rest, desc;
    n = (len+3)/4;
    rest = n*4-len;
    desc = (rest<<27)|0x03000000|n;
    AllocString(kl1str, n);
    SetAll(kl1str, DESC, desc, MRBOFF);
    v = kl1str+1;
    while(len-- > 0){
	n = (*string++)&0xFF;
	if(len-- > 0){
	    n |= ((*string++)&0xFF)<<8;
	    if(len-- > 0){
		n |= ((*string++)&0xFF)<<16;
		if(len-- > 0){
		    n |= ((*string++)&0xFF)<<24;
		}
	    }
	}
	SetAll(v, INT, n, MRBOFF);
	v++;
    }
    return(kl1str);
}

CHAR *convert_to_c_string(CELL *string, CHAR *buffer, int maxlen)
{
    register CELL *p;
    register CHAR *s;
    register int x, rest, leng, type;
    leng = StringLengthof(string);
    type = StringTypeof(string);
    if((type&0xE7) != 0x03) return(NULL);
    rest = (type>>3)&3;
    s = buffer;
    p = Objectof(string)+1;
    while(leng-- > 1 && maxlen>4){
	x = Valueof(p++);
	*s++ = x;
	*s++ = x>>8;
	*s++ = x>>16;
	*s++ = x>>24;
	maxlen -= 4;
    }
    if(leng >= 0 && maxlen-- > 1){
	x = Valueof(p);
	*s++ = x;
	if(rest <= 2 && maxlen-- > 1){
	    *s++ = x>>8;
	    if(rest <= 1 && maxlen-- > 1){
		*s++ = x>>16;
		if(rest <= 0 && maxlen > 1){
		    *s++ = x>>24;
		}
	    }
	}
    }
    *s = 0;
    return(buffer);
}
