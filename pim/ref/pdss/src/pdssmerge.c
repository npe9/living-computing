/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <stdio.h>
#include <ctype.h>
#include <pwd.h>

#define YES 1
#define NO  0
#define MAXLEN 1000

int level;
int scnst = 0;

main(argc, argv)
    int argc; 
    char **argv;
{
    FILE *fi_org, *fi_new, *fi_mod;
    char fn_org[256], fn_mod[256];
    char buffer[1024], module_label[256];
    char *p, *p1, *p2;
    int	 n;

    if(argc != 3){
	fprintf(stderr, "Usage: %s file1 file2\n", argv[0]);
	exit(1);
    }
    expand_path_name(argv[1], fn_org);
    expand_path_name(argv[2], fn_mod);

   /**** PASS #1 ************************************************************/
    fi_mod = fopen(fn_mod, "r");
    if(fi_mod == NULL){
	fprintf(stderr, "Can't read file \"%s\".\n", fn_mod);
	exit(1);
    }
    if(read_line(fi_mod, buffer)){
	if(buffer[0] == '%' && isdigit(buffer[1]) && isdigit(buffer[2]) &&
	   buffer[3] == 0){
	    fprintf(stderr, "File2 \"%s\" is merged file.\n", fn_mod);
	    exit(1);
	}
	do{
	    if(is_predicate_line(buffer, &p1, &p2, &n)){
		enter_procedure(p1, p2, n);
	    }
	    if(is_begin_const_section_line(buffer)){
		break;
	    }
	} while(read_line(fi_mod, buffer));
    }
    fclose(fi_mod);

    /**** PASS #2 ***********************************************************/
    sprintf(buffer, "%s.%d", fn_org, getpid());
    fi_new = fopen(buffer, "w");
    if(fi_new == NULL){
	fprintf(stderr, "Can't open output file.");
	exit(1);
    }
    fi_org = fopen(fn_org, "r");
    if(fi_org == NULL){
	fprintf(stderr, "Can't read file \"%s\".\n", fn_org);
	exit(1);
    }

    /** merge-level & module-top-label **/
    if(!read_line(fi_org, buffer)){
	fprintf(stderr, "Illegal file format \"%s\". -- EOF.\n", fn_org);
	goto exit1;
    }
    if(buffer[0] == '%' && isdigit(buffer[1]) && isdigit(buffer[2]) &&
       buffer[3] == 0){
	level = (buffer[1]-'0')*10 + (buffer[2]-'0') + 1;
	printf("Merge level: %d.\n", level);
	if(!read_line(fi_org, buffer)){
	    fprintf(stderr, "Illegal file format \"%s\". -- EOF.\n", fn_org);
	    goto exit1;
	}
    }else{
	level = 1;
	printf("Merge level: 1.\n");
    }
    if(!is_label_line(buffer, &p1, &p2)){
	fprintf(stderr, "Illegal file format \"%s\".\n%s\n", fn_org, buffer);
	goto exit1;
    }
    fprintf(fi_new, "%%%02d\n", level);
    write_line(fi_new, buffer);
    p = module_label;
    while(p1 <= p2) *p++ = *p1++;
    *p = 0;

    /** module-name-definition **/
    if(!read_line(fi_org, buffer)){
	fprintf(stderr, "Illegal file format \"%s\". -- EOF.\n", fn_org);
	goto exit1;
    }
    if(!is_module_line(buffer, &p1, &p2)){
	fprintf(stderr, "Illegal file format \"%s\".\n%s\n", fn_org, buffer);
	goto exit1;
    }
    write_line(fi_new, buffer);
    printf("Module: %s\n", p1);

    /** entry-definition **/
    printf("Entry :");
    for(;;){
	if(!read_line(fi_org, buffer)){
	    fprintf(stderr, "\nIllegal file format \"%s\". -- EOF.\n", fn_org);
	    goto exit1;
	}
	if(!is_entry_line(buffer, &p1, &p2, &n)) break;
	write_line(fi_new, buffer);
	p2[1] = 0;
	printf(" %s/%d", p1, n);
    }

    /** predicate-definition **/
    printf("\n");
    if(!is_module_entry_line(buffer)){
	fprintf(stderr, "Illegal file format \"%s\".\n%s\n", fn_org, buffer);
	goto exit1;
    }
  body_loop:
    if(!read_line(fi_org, buffer)){
	fprintf(stderr, "\nIllegal file format \"%s\". -- EOF.\n", fn_org);
	goto exit1;
    }
    if(!is_predicate_line(buffer, &p1, &p2, &n)){
	fprintf(stderr, "\nIllegal file format \"%s\".\n%s\n", fn_org, buffer);
	goto exit1;
    }
    if(check_procedure(p1, p2, n)){
	p2[1] = 0;
	printf(" %s/%d-", p1, n);
	while(read_line(fi_org, buffer)){
	    if(is_module_entry_line(buffer)) goto body_loop;
	    if(is_begin_const_section_line(buffer)){
		scnst |= 1;
		goto body_exit;
	    }
	}
    }else{
	fprintf(fi_new, "\tmodule_entry\t\t%s\n", module_label);
	write_line(fi_new, buffer);
	p2[1] = 0;
	printf(" %s/%d", p1, n);
	while(read_line(fi_org, buffer)){
	    if(is_module_entry_line(buffer)) goto body_loop;
	    if(is_begin_const_section_line(buffer)){
		scnst |= 1;
		goto body_exit;
	    }
	    write_line(fi_new, buffer);
	}
    }
  body_exit:;

    /**** PASS #3 ***********************************************************/
    fi_mod = fopen(fn_mod, "r");
    if(fi_mod == NULL){
	fprintf(stderr, "\nCan't read file \"%s\".\n", fn_mod);
	goto exit1;
    }
    do{
	if(!read_line(fi_mod, buffer)){
	    fprintf(stderr, "\nIllegal file format \"%s\". -- EOF.\n", fn_mod);
	    goto exit1;
	}
    } while(!is_module_entry_line(buffer));

  body2_loop:
    if(!read_line(fi_mod, buffer)){
	fprintf(stderr, "\nIllegal file format \"%s\". -- EOF.\n", fn_mod);
	goto exit1;
    }
    if(!is_predicate_line(buffer, &p1, &p2, &n)){
	fprintf(stderr, "\nIllegal file format \"%s\".\n%s\n", fn_mod, buffer);
	goto exit1;
    }
    fprintf(fi_new, "\tmodule_entry\t\t%s\n", module_label);
    write_line(fi_new, buffer);
    p2[1] = 0;
    printf(" %s/%d+", p1, n);
    while(read_line(fi_mod, buffer)){
	if(is_module_entry_line(buffer)) goto body2_loop;
	if(is_begin_const_section_line(buffer)){
	    scnst |= 2;
	    goto body2_exit;
	}
	rename_sc_label(buffer);
	write_line(fi_new, buffer);
    }
  body2_exit:;

    /**** PASS #4 ***********************************************************/
    if(scnst){
	fprintf(fi_new, "\tbegin_const_section\t\t%s\n", module_label);	
	if(scnst&1){
	    while(read_line(fi_org, buffer)){
		write_line(fi_new, buffer);
	    }
	}
	if(scnst&2){
	    while(read_line(fi_mod, buffer)){
		rename_sc_label(buffer);
		write_line(fi_new, buffer);
	    }
	}
    }

    /**** PASS #5 ***********************************************************/
    printf("\n");
    fclose(fi_org);
    fclose(fi_mod);
    fclose(fi_new);
    sprintf(buffer, "%s.Old", fn_org);
    if(rename(fn_org, buffer)){
	fprintf(stderr, "Can't rename file \"%s\" to \"%s\".", fn_org, buffer);
	exit(1);
    }
    sprintf(buffer, "%s.%d", fn_org, getpid());
    if(rename(buffer, fn_org)){
	fprintf(stderr, "Can't rename file \"%s\" to \"%s\".", buffer, fn_org);
	exit(1);
    }
    exit(0);

  exit1:
    sprintf(buffer, "%s.%d", fn_org, getpid());
    unlink(buffer);
    exit(1);
}

/****************************************************************************/
/****************************************************************************/
struct{
    char name[200];
    int	 argn;
} procedure_table[1000];
int  number_of_procedure = 0;

enter_procedure(name, to, argn)
    char *name, *to;
    int	 argn;
{
    register char *p;
    if(number_of_procedure < 1000){
	p = procedure_table[number_of_procedure].name;
	while(name <= to) *p++ = *name++;
	*p = 0;
	procedure_table[number_of_procedure++].argn = argn;
    }
}

check_procedure(name, to, argn)
    char *name, *to;
    int	 argn;
{
    register char *p, *q;
    register int  i;
    for(i=0; i<number_of_procedure; i++){
	p = procedure_table[i].name;
	q = name;
	while(q <= to) if(*p++ != *q++) goto next;
	if(*p == 0 && procedure_table[i].argn == argn) return(YES);
      next:;
    }
    return(NO);
}

/****************************************************************************/
/****************************************************************************/
is_label_line(buffer, from, to)
    register char *buffer;
    char **from, **to;
{
    if(buffer[0] == ' ' && buffer[1] == '\''){
	buffer++;
    }
    if(buffer[0] == '\''){
	*from = buffer++;
      quote_in_atom:
	while(buffer[0] != '\'') buffer++;
	if(buffer[1] == '\''){ buffer+=2; goto quote_in_atom;}
	*to = buffer;
	return(YES);
    }else if(isprint(buffer[0])){
	*from = buffer++;
	while(buffer[0] != ':' && isprint(buffer[0])) buffer++;
	*to = buffer-1;
	return(YES);
    }else{
	return(NO);
    }
}

/****************************************************************************/
is_module_line(buffer, from, to)
    register char *buffer;
    char **from, **to;
{
    while(isspace(*buffer)) buffer++;
    if(!(buffer[0] == 'm' && buffer[1] == 'o' && buffer[2] == 'd' &&
	 buffer[3] == 'u' && buffer[4] == 'l' && buffer[5] == 'e' &&
	 isspace(buffer[6]))){
	return(NO);
    }
    buffer += 7;
    while(isspace(*buffer)) buffer++;
    if(buffer[0] == '\''){
	*from = buffer++;
      quote_in_atom:
	while(buffer[0] != '\'') buffer++;
	if(buffer[1] == '\''){ buffer+=2; goto quote_in_atom;}
	*to = buffer;
	return(YES);
    }else if(isprint(buffer[0])){
	*from = buffer++;
	while(isprint(buffer[0])) buffer++;
	*to = buffer-1;
	return(YES);
    }else{
	return(NO);
    }
}

/****************************************************************************/
is_entry_line(buffer, from, to, argn)
    register char *buffer;
    char **from, **to;
    int	 *argn;
{
    int	 x;

    while(isspace(*buffer)) buffer++;
    if(!(buffer[0] == 'e' && buffer[1] == 'n' && buffer[2] == 't' &&
	 buffer[3] == 'r' && buffer[4] == 'y' && isspace(buffer[5]))){
	return(NO);
    }
    buffer += 6;
    while(isspace(*buffer)) buffer++;
    if(buffer[0] == '\''){
	*from = buffer++;
      quote_in_atom:
	while(buffer[0] != '\'') buffer++;
	if(buffer[1] == '\''){ buffer+=2; goto quote_in_atom;}
	*to = buffer++;
    }else if(isprint(buffer[0])){
	*from = buffer++;
	while(isprint(buffer[0]) && buffer[0] != ',') buffer++;
	*to = buffer-1;
    }else{
	return(NO);
    }
    while(isspace(*buffer)) buffer++;
    if(*buffer++ != ',') return(NO);
    while(isspace(*buffer)) buffer++;
    if(buffer[0] < '0' || buffer[0] > '9') return(NO);
    x = (*buffer++)-'0';
    while(buffer[0] >= '0' && buffer[0] <= '9') x = x*10+(*buffer++)-'0';
    *argn = x;
    return(YES);
}

/****************************************************************************/
is_module_entry_line(buffer)
    register char *buffer;
{
    while(isspace(*buffer)) buffer++;
    return(buffer[0] == 'm' && buffer[1] == 'o' && buffer[2] == 'd' &&
	   buffer[3] == 'u' && buffer[4] == 'l' && buffer[5] == 'e' &&
	   buffer[6] == '_' && buffer[7] == 'e' && buffer[8] == 'n' &&
	   buffer[9] == 't' && buffer[10] == 'r' && buffer[11] == 'y' &&
	   isspace(buffer[12]));
}

/****************************************************************************/
is_predicate_line(buffer, from, to, argn)
    register char *buffer;
    char **from, **to;
    int	 *argn;
{
    int	 x;

    while(isspace(*buffer)) buffer++;
    if(!(buffer[0] == 'p' && buffer[1] == 'r' && buffer[2] == 'e' &&
	 buffer[3] == 'd' && buffer[4] == 'i' && buffer[5] == 'c' &&
	 buffer[6] == 'a' && buffer[7] == 't' & buffer[8] == 'e' &&
	 isspace(buffer[9]))){
	return(NO);
    }
    buffer += 10;
    while(isspace(*buffer)) buffer++;
    if(buffer[0] == '\''){
	*from = buffer++;
      quote_in_atom:
	while(buffer[0] != '\'') buffer++;
	if(buffer[1] == '\''){ buffer+=2; goto quote_in_atom;}
	*to = buffer++;
    }else if(isprint(buffer[0])){
	*from = buffer++;
	while(isprint(buffer[0]) && buffer[0] != ',') buffer++;
	*to = buffer-1;
    }else{
	return(NO);
    }
    while(isspace(*buffer)) buffer++;
    if(*buffer++ != ',') return(NO);
    while(isspace(*buffer)) buffer++;
    if(buffer[0] < '0' || buffer[0] > '9') return(NO);
    x = (*buffer++)-'0';
    while(buffer[0] >= '0' && buffer[0] <= '9') x = x*10+(*buffer++)-'0';
    *argn = x;
    return(YES);
}

/****************************************************************************/
is_begin_const_section_line(buffer)
    register char *buffer;
{
    while(isspace(*buffer)) buffer++;
    return(buffer[0] == 'b' && buffer[1] == 'e' && buffer[2] == 'g' &&
	   buffer[3] == 'i' && buffer[4] == 'n' && buffer[5] == '_' &&
	   buffer[6] == 'c' && buffer[7] == 'o' && buffer[8] == 'n' &&
	   buffer[9] == 's' && buffer[10] == 't' && buffer[11] == '_' &&
	   buffer[12] == 's' && buffer[13] == 'e' && buffer[14] == 'c' &&
	   buffer[15] == 't' && buffer[16] == 'i' && buffer[17] == 'o' &&
	   buffer[18] == 'n' &&
	   isspace(buffer[19]));
}

/****************************************************************************/
/****************************************************************************/
rename_sc_label(buf)
    register char *buf;
{
    while(*buf){
	/** rename label: $SCNST_ --> $SC$NN_ **/
	if(buf[0] == '$' && buf[1] == 'S' && buf[2] == 'C' &&
	   buf[3] == 'N' && buf[4] == 'S' && buf[5] == 'T' && buf[6] == '_'){
	    buf[3] = '$';
	    buf[4] = '0'+level/10;
	    buf[5] = '0'+level%10;
	    buf += 7;
	    continue;
	}
	buf++;
    }
}

/****************************************************************************/
read_line(file, buffer)
    register FILE *file;
    char *buffer;
{
    register int ch, len;
    register char *bp;

    len = 0;
    bp = buffer;
    while(len++ < MAXLEN-1){
	ch = getc(file);
	if(ch == '\n' && bp == buffer) continue;
	if(ch == '\n' || ch == EOF) break;
	*bp++ = ch;
    }
    *bp = 0;
    return(ch != EOF);
}

write_line(file, buffer)
    register FILE *file;
    register char *buffer;
{
    while(*buffer){
	putc(*buffer++, file);
    }
    putc('\n', file);
}

/****************************************************************************/
struct passwd *getpwent();
struct passwd *getpwuid();
struct passwd *getpwnam();
char *getwd();
char *getenv();
char *mktemp();

expand_path_name(name, buffer)
    char  *name, *buffer;
{
    register struct passwd  *pw;
    register char  *p;

    if(*name == '~'){
	name++;
	if(*name == 0 || *name == '/'){
	    if((p = getenv("HOME")) == NULL){
		fprintf(stderr, "Can't get home directory.\n");
		exit(1);
	    }
	    sprintf(buffer, "%s%s", p, name);
	}else{
	    p = name;
	    while(*p && *p != '/') p++;
	    if(*p){
		*p = 0;
		if((pw = getpwnam(name)) == NULL){
		    fprintf(stderr, "Unknown user \"%s\".\n", name);
		    exit(1);
		}
		*p++ = '/';
		sprintf(buffer, "%s/%s", pw->pw_dir, p);
	    }else{
		if((pw = getpwnam(name)) == NULL){
		    fprintf(stderr, "Unknown user \"%s\".\n", name);
		    exit(1);
		}
		sprintf(buffer, "%s", pw->pw_dir);
	    }
	}
    }else{
	sprintf(buffer, "%s", name);
    }
}
