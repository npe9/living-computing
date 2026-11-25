/******************************************************************************
     jLaTeX 用 日本語対応 索引作成 コマンド --- jmakeindex    (5/26,1989)
*******************************************************************************

                    jLaTeXによる索引の作成: jmakeindex
                   ====================================

  jLaTeXのドキュメントで索引を作る為に、jmakeindex というコマンドを作りました。
これは、英語版の makeindex コマンドの仕様を参考にしました。makeindex コマンド
は ICOT には無いようなので、使い方のドキュメント( .../macros/makeindex.tex )
だけを参考にしました、その為、コンパチになっていない部分もあります。


1. jLaTeX のソース・ファイル
----------------------------

  索引を作る為には、makeidx というスタイルファイルを利用します。従って、jLaTeX
ソースの documentstyle を次のように宣言します。

        \documentstyle[makeidx]{jarticle}
                       ^^^^^^^
また、documentstyle の宣言と \begin{document} の間に、

        \makeindex

という宣言をする必要があります。

  以上で、索引を作る為の準備ができたので、索引に入れるべき各キーワードの所に、
\index コマンドを挿入します。この形式は、以下のようにします。

        \index{alphabet}
        \index{index!subindex}              ... `!' で区切る事により3レベル
        \index{index!subindex!subsubindex}      まで指定できる。
	\index{$\alpha$}                    ... 記号の場合。
        \index{alpha@$\alpha$}              ... alpha の所に、αと表示する。
        \index{かんじ@漢字}                 ... 漢字の場合は読みが必要。
        \index{かんじ@漢字!かんじ@漢字}
        \index{インデックス}                ... 仮名の場合。
        \index{index|(}                     ... 3-5 のような形式でページ数を
        \index{index|)}                         表示する場合。

  最後に、索引を作る所に、以下のコマンドを挿入します。

        \printindex


2. jLaTeX の実行手順
--------------------

foo.tex がソースファイルの場合には、次のような手順を実行する。

(1)  jlatex foo [return] を1回以上実行する。
     複数回行うのは、目次などにより、ページ数がずれた場合。

(2)  jlameindex foo [return] を行う。
     これにより、foo.idx から、foo.ind を作成する。
     索引の項目はここでソートされる。
     ここで、-d のオプションを付けると見出しとページの間が ..... で区切られる。

(3)  jlatex foo [return] を1回以上実行する。
     複数回行うのは、索引を作った事により、目次の変更が必要な場合。

(4)  印刷する。

******************************************************************************/

#include <stdio.h>
#include <ctype.h>

#define YES 1
#define NO  0
#define ESC 27
#define BUFLEN 1024

struct entry_rec{
    struct entry_rec *next;
    short *style;
    short *page;
    short body[2];
};

#define AllocEntry(n)\
  (struct entry_rec *)malloc(sizeof(struct entry_rec)+((n)-2)*sizeof(short))

struct index_rec{
    struct index_rec *prev;
    struct index_rec *next;
    struct index_rec *entries;
    struct index_rec *subindex;
    int class;
    short *key;
    short *string;
    short body[2];
} *root;

#define AllocIndex(n)\
  (struct index_rec *)malloc(sizeof(struct index_rec)+((n)-2)*sizeof(short))

int to_kanji = 0;
int to_alpha = 0;

char *separator = ", ";

main(argc, argv)
    int argc; 
    char **argv;
{
    char *name;
    if(argc == 3 && argv[1][0] == '-' && argv[1][1] == 'd'){
	separator = " \\dotfill\\ ";
	name = argv[2];
    }else if(argc != 2){
	printf("Usage: %s [ -d ] file.idx\n", argv[0]);
	exit(-1);
    }else{
	name = argv[1];
    }
    if(strcmp(&name[strlen(name)-4], ".sav") == 0){
	name[strlen(name)-4] = '\0';
    }
    read_idx(name);
    write_ind(name);
    exit(0);
}


/*****************************************************************************
  .idx ファイルの読み込み と \indexentry の各引数のフィールドの切り分け。
*****************************************************************************/

short line[BUFLEN];
int line_no = 0;

read_idx(name)
    char *name;
{
    FILE *fp;
    short buf[BUFLEN*2];
    short *p, *q, *r;
    short *key, *str;
    short *style, *page;
    struct index_rec *index1, *index2, *index3;
    struct entry_rec *entry;
    sprintf(buf, "%s.idx", name);
    if((fp = fopen(buf, "r")) == NULL){
	printf("Cannot oprn file: %s\n", buf);
	exit(-1);
    }
    while(read_line(fp)){
	if(line[ 0] != '\\' ||
	   line[ 1] != 'i'  ||
	   line[ 2] != 'n'  ||
	   line[ 3] != 'd'  ||
	   line[ 4] != 'e'  ||
	   line[ 5] != 'x'  ||
	   line[ 6] != 'e'  ||
	   line[ 7] != 'n'  ||
	   line[ 8] != 't'  ||
	   line[ 9] != 'r'  ||
	   line[10] != 'y'  ||
	   line[11] != '{'){
	    read_error("No \\indexentry in line %d.\n");
	}
	p = line+12;
	q = buf;
	key = r = q; cut_out(&p, &q, 00000); *q++ = 0;
	if(*p == '@'){
	    p++;
	    str = q; cut_out(&p, &q, 01000); *q++ = 0;
	    index1 = AllocIndex((q-r)+(str-r));
	    index1->class = class(key[0]);
	    index1->key = &(index1->body[0]);
	    conv(key, &(index1->body[0]));
	    index1->string = &(index1->body[(str-r)*2]);
	    copy(str, &(index1->body[(str-r)*2]));
	}else{
	    index1 = AllocIndex((q-r)*3);
	    index1->class = class(key[0]);
	    index1->key = &(index1->body[0]);
	    conv(key, &(index1->body[0]));
	    index1->string = &(index1->body[(q-r)*2]);
	    copy(key, &(index1->body[(q-r)*2]));
	}
	if(*p == '!'){
	    p++;
	    key = r = q; cut_out(&p, &q, 00000); *q++ = 0;
	    if(*p == '@'){
		p++;
		str = q; cut_out(&p, &q, 01000); *q++ = 0;
		index2 = AllocIndex((q-r)+(str-r));
		index2->key = &(index2->body[0]);
		conv(key, &(index2->body[0]));
		index2->string = &(index2->body[(str-r)*2]);
		copy(str, &(index2->body[(str-r)*2]));
	    }else{
		index2 = AllocIndex((q-r)*3);
		index2->key = &(index2->body[0]);
		conv(key, &(index2->body[0]));
		index2->string = &(index2->body[(q-r)*2]);
		copy(key, &(index2->body[(q-r)*2]));
	    }
	    if(*p == '!'){
		p++;
		key = r = q; cut_out(&p, &q, 00100); *q++ = 0;
		if(*p == '@'){
		    p++;
		    str = q; cut_out(&p, &q, 01100); *q++ = 0;
		    index3 = AllocIndex((q-r)+(str-r));
		    index3->key = &(index3->body[0]);
		    conv(key, &(index3->body[0]));
		    index3->string = &(index3->body[(str-r)*2]);
		    copy(str, &(index3->body[(str-r)*2]));
		}else{
		    index3 = AllocIndex((q-r)*3);
		    index3->key = &(index3->body[0]);
		    conv(key, &(index3->body[0]));
		    index3->string = &(index3->body[(q-r)*2]);
		    copy(key, &(index3->body[(q-r)*2]));
		}
	    }else{
		index3 = NULL;
	    }
	}else{
	    index2 = index3 = NULL;
	}
	r = q;
	if(*p == '|'){
	    p++;
	    style = q; cut_out(&p, &q, 01110); *q++ = 0;
	}else{
	    style = NULL;
	}
	if(p[0] != '}' || p[1] != '{'){
	    read_error("Unknown sequence in line %d.\n");
	}
	p += 2;
	page = q; cut_out(&p, &q, 01110); *q++ = 0;
	if(p[0] != '}' || p[1] != 0){
	    read_error("Unknown sequence in line %d.\n");
	}
	entry = AllocEntry(q-r);
	if(style){
	    entry->style = &(entry->body[style-r]);
	    copy(style, &(entry->body[style-r]));
	}else{
	    entry->style = NULL;
	}
	entry->page = &(entry->body[page-r]);
	copy(page, &(entry->body[page-r]));
	enter_index(index1, index2, index3, entry);
    }
    fclose(fp);
}

cut_out(from, to, s)
    short **from, **to;
    int s;
{
    short *p, *q;
    p = *from; q = *to;
    for(;;){
	switch(*p){
	  case '\\':
	    if(p[1] == 'v' &&
	       p[2] == 'e' &&
	       p[3] == 'r' &&
	       p[4] == 'b' &&
	       ispunct(p[5])){
		int c = p[5];
		*q++ = *p++; *q++ = *p++; *q++ = *p++;
		*q++ = *p++; *q++ = *p++; *q++ = *p++;
		while(*p != c){
		    if(*p == 0){
			read_error("Illegal \\verb format in line %d.\n");
		    }
		    *q++ = *p++;
		}
		*q++ = *p++;
	    }else if(isalnum(p[1]) || p[1] == '@'){
		*q++ = *p++;
		*q++ = *p++;
		while(isalnum(*p) || *p == '@'){
		    *q++ = *p++;
		}
	    }else{
		*q++ = *p++;
		if(*p == 0){
		    read_error("Illegal format in line %d.\n");
		}
		*q++ = *p++;
	    }
	    continue;
	  case '"':
	    *q++ = *p++;
	    if(*p == 0){
		read_error("Illegal format in line %d.\n");
	    }
	    *q++ = *p++;
	    continue;
	  case '{':
	    *q++ = *p++;
	    cut_out(&p, &q, 011110);
	    if(*p != '}'){
		read_error("Mismatch { } in line %d.\n");
	    }
	    *q++ = *p++;
	    continue;
	  case '@':
	    if(s&01000) goto next; else goto done;
	  case '!':
	    if(s&00100) goto next; else goto done;
	  case '|':
	    if(s&00010) goto next; else goto done;
	  case '}':
	    if(s&00001) goto next;
	  done:
	    if((s&010000) == 0 && *from == p) goto error;
	    *from = p; *to = q;
	    return;
	  case 0:
	  error:
	    read_error("Illegal format in line %d.\n");
	  default:
	  next:
	    *q++ = *p++;
	    continue;
	}
    }
}

read_line(fp)
    FILE *fp;
{
    register int c, cc;
    register short *p, *q;
    line_no++;
    p = line; q = p+BUFLEN;
    while(p<q){
	c = getc(fp);
	if(c >= ' ' && c <= '~'){
	    /** ALPHA **/
	    *p++ = c;
	    continue;
	}
	if(c >= 0xA1 && c <= 0xFE){
	    /** EUC **/
	    cc = getc(fp);
	    if(cc >= 0xA1 && cc <= 0xFE){
		*p++ = ((c<<8)|cc)&0x7F7F;
		continue;
	    }else{
		*p = 0;
		read_error("Illegal EUC code in line %d.\n");
	    }
	}
	if(c == '\n'){
	    *p = 0;
	    return(YES);
	}
	if(c == EOF){
	    if(p > line){
		*p = 0;
		read_error("Unexpected EOF in %d.\n");
	    }
	    return(NO);
	}
	if(c == ESC && getc(fp) == '$'){
	    c = getc(fp);
	    if(c == '@' || c == 'B'){
		/** JIS-KANJI **/
		to_kanji = c;
		for(;;){
		    if(p >= q) goto too_long;
		    c = getc(fp); cc = getc(fp);
		    if(c >= 0x21 && c <= 0x7E && cc >= 0x21 && cc <= 0x7E){
			*p++ = ((c<<8)|cc)&0x7F7F;
			continue;
		    }
		    if(c == ESC && cc == '('){
			c = getc(fp);
			if(c == 'J' || c == 'H' || c == 'B'){
			    to_alpha = c;
			    break;
			}
		    }
		    *p = 0;
		    read_error("Illegal KANJI code in line %d.\n");
		}
		continue;
	    }
	}
	*p = 0;
	read_error("Illegal control code in line %d.\n");
    }
  too_long:
    *p = 0;
    read_error("Line %d is too long.\n");
}

read_error(msgs)
    char *msgs;
{
    printf(msgs, line_no);
    putstr(line, stdout);
    putchar('\n');
    exit(-1);
}

copy(p, q)
    register short *p, *q;
{
    while(*p) *q++ = *p++;
    *q = 0;
}


/*****************************************************************************
  読み込まれたエントリを辞書順に並べ換え、記憶する。
*****************************************************************************/

enter_index(index1, index2, index3, entry)
    struct index_rec *index1, *index2, *index3;
    struct entry_rec *entry;
{
    struct index_rec **p;
    p = &root;
    while(*p){
	switch(compare(index1->key, (*p)->key)){
	  case -1:
	  prev:
	    p = &((*p)->prev);
	    continue;
	  case 0:
	    switch(compare(index1->string, (*p)->string)){
	      case -1:
		goto prev;
	      case 0:
		if(index2){
		    enter_index2(&((*p)->subindex), index2, index3, entry);
		}else{
		    enter_index4(&((*p)->entries), entry);
		}
		free(index1);
		return;
	      case 1:
		goto next;
	    }
	  case 1:
	  next:
	    p = &((*p)->next);
	    continue;
	}
    }
    *p = index1;
    index1->prev = NULL;
    index1->next = NULL;
    index1->subindex = NULL;
    index1->entries = NULL;
    if(index2){
	enter_index2(&((*p)->subindex), index2, index3, entry);
    }else{
	enter_index4(&((*p)->entries), entry);
    }
}

enter_index2(p, index2, index3, entry)
    struct index_rec **p, *index2, *index3;
    struct entry_rec *entry;
{
    while(*p){
	switch(compare(index2->key, (*p)->key)){
	  case -1:
	  prev:
	    p = &((*p)->prev);
	    continue;
	  case 0:
	    switch(compare(index2->string, (*p)->string)){
	      case -1:
		goto prev;
	      case 0:
		if(index3){
		    enter_index3(&((*p)->subindex), index3, entry);
		}else{
		    enter_index4(&((*p)->entries), entry);
		}
		free(index2);
		return;
	      case 1:
		goto next;
	    }
	  case 1:
	  next:
	    p = &((*p)->next);
	    continue;
	}
    }
    *p = index2;
    index2->prev = NULL;
    index2->next = NULL;
    index2->subindex = NULL;
    index2->entries = NULL;
    if(index3){
	enter_index3(&((*p)->subindex), index3, entry);
    }else{
	enter_index4(&((*p)->entries), entry);
    }
}

enter_index3(p, index3, entry)
    struct index_rec **p, *index3;
    struct entry_rec *entry;
{
    while(*p){
	switch(compare(index3->key, (*p)->key)){
	  case -1:
	  prev:
	    p = &((*p)->prev);
	    continue;
	  case 0:
	    switch(compare(index3->string, (*p)->string)){
	      case -1:
		goto prev;
	      case 0:
		enter_index4(&((*p)->entries), entry);
		free(index3);
		return;
	      case 1:
		goto next;
	    }
	  case 1:
	  next:
	    p = &((*p)->next);
	    continue;
	}
    }
    *p = index3;
    index3->prev = NULL;
    index3->next = NULL;
    index3->subindex = NULL;
    index3->entries = NULL;
    enter_index4(&((*p)->entries), entry);
}

enter_index4(p, entry)
    struct entry_rec **p, *entry;
{
    while(*p) p = &((*p)->next);
    *p = entry;
    entry->next = NULL;
}

compare(p, q)
    register short *p, *q;
{
    while(*p == *q){
	if(*p == 0) return(0);
	p++; q++;
    }
    return(*p < *q ? -1 : 1);
}


/*****************************************************************************
  索引の各エントリを LaTeX のソールファイル .ind として出力する。
*****************************************************************************/

write_ind(name)
    char *name;
{
    FILE *fp;
    char fname[1024];
    sprintf(fname, "%s.ind", name);
    if((fp = fopen(fname, "w")) == NULL){
	printf("Cannot create file: %s\n", fname);
	exit(-1);
    }
    fprintf(fp, "\\begin{theindex}\n");
    write_index(root, fp, 0);
    fprintf(fp, "\\end{theindex}\n");
    fclose(fp);
}

write_index(p, fp, last)
    struct index_rec *p;
    FILE *fp;
    int last;
{
    if(p->prev) last = write_index(p->prev, fp, last);
    if(last != p->class){
	short x[2];
	x[0] = p->class; x[1] = 0;
	if(last){ fprintf(fp, "\\indexspace\n\n"); printf("\n"); }
	printf("*** "); putstr(x, stdout); printf(" ***\n");
	last = p->class;
    }
    fprintf(fp, "\\item "); putstr(p->string, fp);
    putstr(p->string, stdout);
    if(p->entries) write_pages(p->entries, fp);
    fprintf(fp, "\n"); printf("\n");
    if(p->subindex) write_index2(p->subindex, fp);
    if(p->next) last = write_index(p->next, fp, last);
    return(last);
}

write_index2(p, fp)
    struct index_rec *p;
    FILE *fp;
{
    if(p->prev) write_index2(p->prev, fp);
    fprintf(fp, "\\subitem "); putstr(p->string, fp);
    printf("  "); putstr(p->string, stdout);
    if(p->entries) write_pages(p->entries, fp);
    fprintf(fp, "\n"); printf("\n");
    if(p->subindex) write_index3(p->subindex, fp);
    if(p->next) write_index2(p->next, fp);
}

write_index3(p, fp)
    struct index_rec *p;
    FILE *fp;
{
    if(p->prev) write_index3(p->prev, fp);
    fprintf(fp, "\\subsubitem "); putstr(p->string, fp);
    printf("    "); putstr(p->string, stdout);
    if(p->entries) write_pages(p->entries, fp);
    fprintf(fp, "\n"); printf("\n");
    if(p->next) write_index3(p->next, fp);
}

write_pages(p, fp)
    struct entry_rec *p;
    FILE *fp;
{
    int fromto = 0;
    short *last = NULL;
    fprintf(fp, "%s", separator);
    while(p){
	switch(check_style(p->style)){
	  case 0:	/** No specified **/
	    if(fromto) goto error;
	    if(last){
		if(compare(p->page, last)){
		    putstr(last, fp); fprintf(fp, ",");
		    last = p->page;
		}
	    }else{
		last = p->page;
	    }
	    break;
	  case 1:	/** ( **/
	    if(fromto) goto error;
	    if(last){
		if(compare(p->page, last)){
		    putstr(last, fp); fprintf(fp, ",");
		    last = p->page;
		}
	    }else{
		last = p->page;
	    }
	    fromto = 1;
	    break;
	  case 2:	/** (command **/
	    if(fromto) goto error;
	    if(last){
		putstr(last, fp); fprintf(fp, ",");
	    }
	    fprintf(fp, "\\"); putstr(&(p->style[1]), fp); fprintf(fp, "{");
	    last = p->page;
	    fromto = 2;
	    break;
	  case 3:	/** ) **/
	    if(!fromto) goto error;
	    if(fromto == 1){
		if(compare(p->page, last)){
		    putstr(last, fp); fprintf(fp, "-");
		    last = p->page;
		}
	    }else{
		putstr(last, fp);
		if(compare(p->page, last)){
		    fprintf(fp, "-"); putstr(p->page, fp);
		}
		fprintf(fp, "}");
		last = NULL;
	    }
	    fromto = 0;
	    break;
	  case 4:	/** command **/
	    if(fromto) goto error;
	    if(last){
		putstr(last, fp); fprintf(fp, ",");
	    }
	    fprintf(fp, "\\"); putstr(p->style, fp);
	    fprintf(fp, "{"); putstr(p->page, fp); fprintf(fp, "}");
	    last = NULL;
	    break;
	  default:
	    printf("Illegal page number style.\n");
	    exit(-1);
	  error:
	    printf("Illegal ( ) sequence.\n");
	    exit(-1);
	}
	p = p->next;
    }
    if(last) putstr(last, fp);
}

check_style(p)
    short *p;
{
    if(p == NULL) return(0);
    if(*p == '('){
	p++;
	if(*p == 0) return(1);
	while(*p){
	    if(*p < 0x100 && !isalnum(*p)) return(-1);
	    p++;
	}
	return(2);
    }
    if(*p == ')'){
	p++;
	if(*p == 0) return(3);
	return(-1);
    }
    if(*p == 0) return(1);
    while(*p && *p != '{'){
	if(*p < 0x100 && !isalnum(*p)) return(-1);
	p++;
    }
    return(4);
}

putstr(p, fp)
    register short *p;
    FILE *fp;
{
    if(*p < 0){
	static short a[] = {'S','y','m','b','o','l',0};
	static short k[] = {0x352D,0x3966,0};	/* 記号 */
	p = (*p == -1) ? a : k;
    }
    if(to_kanji){
	int f = NO;
	while(*p){
	    if(*p < 0x100){
		if(f){
		    putc(ESC, fp);
		    putc('(', fp);
		    putc(to_alpha, fp);
		    f = NO;
		}
		putc(*p, fp);
	    }else{
		if(!f){
		    putc(ESC, fp);
		    putc('$', fp);
		    putc(to_kanji, fp);
		    f = YES;
		}
		putc((*p>>8)&0x7F, fp);
		putc((*p)&0x7F, fp);
	    }
	    p++;
	}
	if(f){
	    putc(ESC, fp);
	    putc('(', fp);
	    putc(to_alpha, fp);
	}
    }else{
	while(*p){
	    if(*p < 0x100){
		putc(*p, fp);
	    }else{
		putc((*p>>8)|0x80, fp);
		putc((*p)|0x80, fp);
	    }
	    p++;
	}
    }
}


/*****************************************************************************
  文字の辞書順番号と種類分け。
*****************************************************************************/

unsigned char korder[86] = {
    1,  0,       5,  4,       9,  8,      13, 12,      17, 16,         /* あ */
       20, 22,      24, 26,      28, 30,      32, 34,      36, 38,     /* か */
       40, 42,      44, 46,      48, 50,      52, 54,      56, 58,     /* さ */
       60, 62,      64, 66,  69, 68, 70,      72, 74,      76, 78,     /* た */
       80,          84,          88,          92,          96,         /* な */
      100,102,103, 104,106,107, 108,110,111, 112,114,115, 116,118,119, /* は */
      120,         124,         128,         132,         136,         /* ま */
  141,140,                  149,148,                  157,156,         /* や */
      160,         164,         168,         172,         176,         /* ら */
  181,180,         184,                      192,         196,         /* わ */
      200,                       10,          21,          33};        /* ん */

unsigned char cyo_on[86] = {
    0,  0,       4,  4,       8,  8,      12, 12,      16, 16,         /* あ */
        0,  0,       4,  4,       8,  8,      12, 12,      16, 16,     /* か */
        0,  0,       4,  4,       8,  8,      12, 12,      16, 16,     /* さ */
        0,  0,       4,  4,   8,  8,  8,      12, 12,      16, 16,     /* た */
        0,           4,           8,          12,          16,         /* な */
        0,  0,  0,   4,  4,  4,   8,  8,  8,  12, 12, 12,  16, 16, 16, /* は */
        0,           4,           8,          12,          16,         /* ま */
    0,  0,                    8,  8,                   16, 16,         /* や */
        0,           4,           8,          12,          16,         /* ら */
    0,  0,           4,                       12,          16,         /* わ */
        0,                        8,           0,          12};        /* ん */

conv(from, to)
    short *from, *to;
{
    register short *p, *q;
    p = from; q = to;
    while(*p){
	if(*p < 0x100){
	    if(*p >= 'A' && *p <= 'Z'){
		*q++ = (*p-'A')+0x7F00;
	    }else if(*p >= 'a' && *p <= 'z'){
		*q++ = (*p-'a')+0x7F00;
	    }else if(*p >= '0' && *p <= '9'){
		*q++ = (*p-'0')+0x7F20;
	    }else if(*p == '-' && p > from){
		p++; continue;
/**	    }else if(*p == '\\'){
		p++; continue; **/
	    }else{
		*q++ = *p+0x7F80;
	    }
	}else if(*p >= 0x2421 && *p <= 0x2473){  /* ひらがな */
	    *q++ = (korder[*p-0x2421]>>2)+0x80;
	}else if(*p >= 0x2521 && *p <= 0x2576){  /* カタカナ */
	    *q++ = (korder[*p-0x2521]>>2)+0x80;
	}else if(*p == 0x213C && p > from){  /* ー */
	    p--;
	    if(*p >= 0x2421 && *p <= 0x2473){  /* ひらがな */
		*q++ = (cyo_on[*p-0x2421]>>2)+0x80;
	    }else if(*p >= 0x2521 && *p <= 0x2576){  /* カタカナ */
		*q++ = (cyo_on[*p-0x2521]>>2)+0x80;
	    }else{
		*q++ = *(p+1);
	    }
	    p++;
	}else if(*p == 0x2126 && p > from){  /* ・(中黒) */
	    p++; continue;
	}else{
	    *q++ = *p;
	}
	p++;
    }
    p = from;
    while(*p){
	if(*p < 0x100){
	    if(*p >= 'A' && *p <= 'Z'){
		*q++ = 1;
	    }else if(*p >= 'a' && *p <= 'z'){
		*q++ = 2;
	    }else if(*p >= '0' && *p <= '9'){
		*q++ = 1;
	    }else if(*p == '-' && p > from){
		p++; continue;
/**	    }else if(*p == '\\'){
		p++; continue; **/
	    }else{
		*q++ = 1;
	    }
	}else if(*p >= 0x2421 && *p <= 0x2473){  /* ひらがな */
	    *q++ = (korder[*p-0x2421]&3)*2+1;
	}else if(*p >= 0x2521 && *p <= 0x2576){  /* カタカナ */
	    *q++ = (korder[*p-0x2521]&3)*2+2;
	}else if(*p == 0x213C && p > from){  /* ー */
	    p--;
	    if(*p >= 0x2421 && *p <= 0x2473){  /* ひらがな */
		*q++ = 1;
	    }else if(*p >= 0x2521 && *p <= 0x2576){  /* カタカナ */
		*q++ = 1;
	    }else{
		*q++ = 1;
	    }
	    p++;
	}else if(*p == 0x2126 && p > from){  /* ・(中黒) */
	    p++; continue;
	}else{
	    *q++ = 1;
	}
	p++;
    }
    *q = 0;
}

class(c)
    short c;
{
    if(c < 0x100){
	if(c >= 'A' && c <= 'Z'){
	    return(c);
	}else if(c >= 'a' && c <= 'z'){
	    return(toupper(c));
	}else if(c >= '0' && c <= '9'){
	    return(c);
	}else{
	    return(-1);
	}
    }else if(c >= 0x2421 && c <= 0x2473){  /* ひらがな */
	while(korder[c-0x2421]&3) c--;
	return(c);
    }else if(c >= 0x2521 && c <= 0x2573){  /* カタカナ-1 */
	while(korder[c-0x2521]&3) c--;
	return(c-0x100);
    }else if(c >= 0x2574 && c <= 0x2576){  /* カタカナ-2 */
	return(c);
    }else{
	return(-2);
    }
}
