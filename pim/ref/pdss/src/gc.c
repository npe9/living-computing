/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <sys/time.h>
#include <sys/resource.h>
#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "gc.h"

int gc_code;
int gc_counter;
int gc_panic_flag;

#define CD if(gc_code)


/*************************************************************************
*  Collect Garbage & Display Memory Statistics.				 *
*************************************************************************/

gc()
{
    PARENT_RECORD *ma;
    CELL *rma;
    long uspent;
    struct rusage usage_before, usage_after;
    getrusage(RUSAGE_SELF, &usage_before);
    gc_counter++;
    gc_code = CodeGcFlag_ON();
    ResetGcFlag();
    display_memory_statistics(1);
    switch_heap();
CD  switch_code();
CD  gc_code_area();
    ma = grand_mother;
    GcGetParentRecord(grand_mother);
    gc_parent_record(ma, grand_mother);
    rma = result_of_grand_mother;
    GcAlloc1Word(result_of_grand_mother);
    gc_cell(rma, result_of_grand_mother);
    gc_ready_queue();
    gc_io_table();
    gc_timer_table();
    deadlock_check_and_report();
    terminate_shoen_by_gc();
    display_memory_statistics(2);
CheckHeap();
#if GC_SWAP_GOALS_WHEN_PANIC
    if(HeapRest() < heap_size/20){  /** less then 5% **/
	if(gc_panic_flag < 1){
	    if(swap_highest_queue()){
		PrintCons("GC gain is less than 5%. Swap goals in queue.\n");
		gc_panic_flag = 1;
		goto done;
	    }
	}
#endif
#if GC_ABORT_TASK_WHEN_PANIC
	if(HeapRest() < heap_size/100){	 /** less then 1% **/
	    if(gc_panic_flag < 2){
		Error("GC gain is less than 1%. Cannot continue task.\n");
		io_table[1].int_code = 1;
		SetKeyIntFlag();
		gc_panic_flag = 2;
	    }
	    goto done;
	}
#endif
#if GC_SWAP_GOALS_WHEN_PANIC
    }
#endif
    gc_panic_flag = 0;
  done:
    getrusage(RUSAGE_SELF, &usage_after);
    uspent = (usage_after.ru_utime.tv_sec-usage_before.ru_utime.tv_sec)*1000
	   + (usage_after.ru_utime.tv_usec-usage_before.ru_utime.tv_usec)/1000;
    PrintCons1F("GC Time: %d msec\n", uspent);
}


/*************************************************************************
*   Display Memory Statistics.						 *
*************************************************************************/

#if MRBGC_SWITCH && MRBGC_STATISTICS
#if MRBGC_FREE_LIST_TYPE == 0

display_memory_statistics(f)
    int f;
{
    static unsigned f01, f02, f03, f04, f05, f06, f07, f08, f16, f32, f99;
    static unsigned src, g08, g16, g32, prc, cod;
    static unsigned htb, hpb, hua, hub, ttb, tpb, tua, tub;
    static CHAR buf1[128], buf2[128], buf3[128];
    static CHAR buf4[128], buf5[128], buf6[128];
    switch(f){
      case 0:
      case 1:
	htb = f01total+f02total*2+f03total*3+f04total*4+f05total*5+f06total*6+
	      f07total*7+f08total*8+f16total*16+f32total*32+f99total;
	ttb = htb*sizeof(CELL)+
	      srec_total*sizeof(SUSPENSION_RECORD)+
	      grec08_total*sizeof(GOAL_RECORD)+
	      grec16_total*sizeof(GOAL_RECORD16)+
	      grec32_total*sizeof(GOAL_RECORD32)+
	      prec_total*sizeof(PARENT_RECORD);
	hpb = f01peek+f02peek*2+f03peek*3+f04peek*4+f05peek*5+f06peek*6+
	      f07peek*7+f08peek*8+f16peek*16+f32peek*32+f99peek;
	tpb = hpb*sizeof(CELL)+
	      srec_peek*sizeof(SUSPENSION_RECORD)+
	      grec08_peek*sizeof(GOAL_RECORD)+
	      grec16_peek*sizeof(GOAL_RECORD16)+
	      grec32_peek*sizeof(GOAL_RECORD32)+
	      prec_peek*sizeof(PARENT_RECORD);
	hub = f01used+f02used*2+f03used*3+f04used*4+f05used*5+f06used*6+
	      f07used*7+f08used*8+f16used*16+f32used*32+f99used;
	tub = hub*sizeof(CELL)+
	      srec_used*sizeof(SUSPENSION_RECORD)+
	      grec08_used*sizeof(GOAL_RECORD)+
	      grec16_used*sizeof(GOAL_RECORD16)+
	      grec32_used*sizeof(GOAL_RECORD32)+
	      prec_used*sizeof(PARENT_RECORD);
	break;
      case 2:
	hua = f01used+f02used*2+f03used*3+f04used*4+f05used*5+f06used*6+
	      f07used*7+f08used*8+f16used*16+f32used*32+f99used;
	tua = hua*sizeof(CELL)+
	      srec_used*sizeof(SUSPENSION_RECORD)+
	      grec08_used*sizeof(GOAL_RECORD)+
	      grec16_used*sizeof(GOAL_RECORD16)+
	      grec32_used*sizeof(GOAL_RECORD32)+
	      prec_used*sizeof(PARENT_RECORD);
	break;
    }
    if(f == 1){
	f01 = f01used; f02 = f02used; f03 = f03used; f04 = f04used;
	f05 = f05used; f06 = f06used; f07 = f07used; f08 = f08used;
	f16 = f16used; f32 = f32used; f99 = f99used;
	src = srec_used;
	g08 = grec08_used; g16 = grec16_used; g32 = grec32_used;
	prc = prec_used;
	cod = CodeUsed();
    }
/******************************************************************************
	  1W	 2W	3W     4W    5W	   6W	 7W    8W   16W	  32W	  More
TO: 12345678 123456 123456 123456 12345 12345 12345 12345 12345 12345 12345678
      KL1-Data	  Srec	    Gr08     Gr16    Gr32   Prec   HeapTotal	  Code
TO: 1234567890 1234567 123456789 12345678 1234567 123456 12345678901 123456789
	  word	   rec	     rec      rec     rec    rec	byte	  byte
******************************************************************************/
    SelectWindow(CONSOLE);
    switch(f){
      case 0:
	printf("\
===============================================================================\n");
#if MRBGC_STATISTICS == 2
	printf("\
          1W     2W     3W     4W    5W    6W    7W    8W   16W   32W     More\n");
	printf("DRF: %7d\n", mst_deref);
	printf("CLS:         %6d\n", mst_cslst);
	printf(" -F:         %6d\n", mst_cflst);
	printf("CVC: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_csv01, mst_csv02, mst_csv03, mst_csv04, mst_csv05,
	       mst_csv06, mst_csv07, mst_csv08, mst_csv16, mst_csv32);
	printf(" -F: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_cfv01, mst_cfv02, mst_cfv03, mst_cfv04, mst_cfv05,
	       mst_cfv06, mst_cfv07, mst_cfv08, mst_cfv16, mst_cfv32);
	printf("CVL: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_cvl01, mst_cvl02, mst_cvl03, mst_cvl04, mst_cvl05,
	       mst_cvl06, mst_cvl07, mst_cvl08, mst_cvl16, mst_cvl32);
	printf("CBL: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_cbl01, mst_cbl02, mst_cbl03, mst_cbl04, mst_cbl05,
	       mst_cbl06, mst_cbl07, mst_cbl08, mst_cbl16, mst_cbl32);
	printf("RLS:         %6d\n", mst_rslst);
	printf(" -F:         %6d\n", mst_rflst);
	printf("RVC: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       mst_rsv01, mst_rsv02, mst_rsv03, mst_rsv04, mst_rsv05,
	       mst_rsv06, mst_rsv07, mst_rsv08, mst_rsv16, mst_rsv32,
	       mst_rsv99);
	printf(" -F: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       mst_rfv01, mst_rfv02, mst_rfv03, mst_rfv04, mst_rfv05,
	       mst_rfv06, mst_rfv07, mst_rfv08, mst_rfv16, mst_rfv32,
	       mst_rfv99);
	printf("RBL: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       mst_rbl01, mst_rbl02, mst_rbl03, mst_rbl04, mst_rbl05,
	       mst_rbl06, mst_rbl07, mst_rbl08, mst_rbl16, mst_rbl32,
	       mst_rbl99);
	printf("RMG:         %6d\n", mst_merge);
	printf("\
-------------------------------------------------------------------------------\n");
#endif
	printf("\
          1W     2W     3W     4W    5W    6W    7W    8W   16W   32W     More\n");
	printf("TO: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01total, f02total, f03total, f04total, f05total, f06total,
	       f07total, f08total, f16total, f32total, f99total);
	printf("PK: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01peek, f02peek, f03peek, f04peek, f05peek, f06peek,
	       f07peek, f08peek, f16peek, f32peek, f99peek);
	printf("US: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01used, f02used, f03used, f04used, f05used, f06used,
	       f07used, f08used, f16used, f32used, f99used);
	printf("\
-------------------------------------------------------------------------------\n");
	printf("\
      KL1-Data    Srec      Gr08     Gr16    Gr32   Prec   HeapTotal      Code\n");
	printf("TO: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       htb, srec_total, grec08_total, grec16_total, grec32_total,
	       prec_total, ttb, CodeUsed());
	printf("PK: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hpb, srec_peek, grec08_peek, grec16_peek, grec32_peek,
	       prec_peek, tpb, CodeUsed());
	printf("US: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hub, srec_used, grec08_used, grec16_used, grec32_used,
	       prec_used, tub, CodeUsed());
	printf("\
          word     rec       rec      rec     rec    rec        byte      byte\n");
	printf("\
===============================================================================\n");
	break;
      case 1:
	printf("\n\GC-%d\n", gc_counter);
	printf("\
===============================================================================\n");
#if MRBGC_STATISTICS == 2
	printf("\
          1W     2W     3W     4W    5W    6W    7W    8W   16W   32W     More\n");

	printf("DRF: %7d\n", mst_deref);
	printf("CLS:         %6d\n", mst_cslst);
	printf(" -F:         %6d\n", mst_cflst);
	printf("CVC: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_csv01, mst_csv02, mst_csv03, mst_csv04, mst_csv05,
	       mst_csv06, mst_csv07, mst_csv08, mst_csv16, mst_csv32);
	printf(" -F: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_cfv01, mst_cfv02, mst_cfv03, mst_cfv04, mst_cfv05,
	       mst_cfv06, mst_cfv07, mst_cfv08, mst_cfv16, mst_cfv32);
	printf("CVL: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_cvl01, mst_cvl02, mst_cvl03, mst_cvl04, mst_cvl05,
	       mst_cvl06, mst_cvl07, mst_cvl08, mst_cvl16, mst_cvl32);
	printf("CBL: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d\n",
	       mst_cbl01, mst_cbl02, mst_cbl03, mst_cbl04, mst_cbl05,
	       mst_cbl06, mst_cbl07, mst_cbl08, mst_cbl16, mst_cbl32);
	printf("RLS:         %6d\n", mst_rslst);
	printf(" -F:         %6d\n", mst_rflst);
	printf("RVC: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       mst_rsv01, mst_rsv02, mst_rsv03, mst_rsv04, mst_rsv05,
	       mst_rsv06, mst_rsv07, mst_rsv08, mst_rsv16, mst_rsv32,
	       mst_rsv99);
	printf(" -F: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       mst_rfv01, mst_rfv02, mst_rfv03, mst_rfv04, mst_rfv05,
	       mst_rfv06, mst_rfv07, mst_rfv08, mst_rfv16, mst_rfv32,
	       mst_rfv99);
	printf("RBL: %7d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       mst_rbl01, mst_rbl02, mst_rbl03, mst_rbl04, mst_rbl05,
	       mst_rbl06, mst_rbl07, mst_rbl08, mst_rbl16, mst_rbl32,
	       mst_rbl99);
	printf("RMG:         %6d\n", mst_merge);
	printf("\
-------------------------------------------------------------------------------\n");
#endif
	sprintf(buf1, "TO: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01total, f02total, f03total, f04total, f05total, f06total,
	       f07total, f08total, f16total, f32total, f99total);
	sprintf(buf2, "PK: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01peek, f02peek, f03peek, f04peek, f05peek, f06peek,
	       f07peek, f08peek, f16peek, f32peek, f99peek);
	sprintf(buf3, "US: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01used, f02used, f03used, f04used, f05used, f06used,
	       f07used, f08used, f16used, f32used, f99used);
	sprintf(buf4, "TO: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       htb, srec_total, grec08_total, grec16_total, grec32_total,
	       prec_total, ttb, CodeUsed());
	sprintf(buf5, "PK: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hpb, srec_peek, grec08_peek, grec16_peek, grec32_peek,
	       prec_peek, tpb, CodeUsed());
	sprintf(buf6, "US: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hub, srec_used, grec08_used, grec16_used, grec32_used,
	       prec_used, tub, CodeUsed());
	break;
      case 2:
	printf("\
          1W     2W     3W     4W    5W    6W    7W    8W   16W   32W     More\n");
	printf("%s%s%s", buf1, buf2, buf3);
	printf("AF: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01used, f02used, f03used, f04used, f05used, f06used,
	       f07used, f08used, f16used, f32used, f99used);
	printf("GC: %8d %6d %6d %6d %5d %5d %5d %5d %5d %5d %8d\n",
	       f01-f01used, f02-f02used, f03-f03used, f04-f04used,
	       f05-f05used, f06-f06used, f07-f07used, f08-f08used,
	       f16-f16used, f32-f32used, f99-f99used);
	printf("\
-------------------------------------------------------------------------------\n");
	printf("\
      KL1-Data    Srec      Gr08     Gr16    Gr32   Prec   HeapTotal      Code\n");
	printf("%s%s%s", buf4, buf5, buf6);
	printf("AF: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hua, srec_used, grec08_used, grec16_used, grec32_used,
	       prec_used, tua, CodeUsed());
	printf("GC: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hub-hua, src-srec_used, g08-grec08_used, g16-grec16_used,
	       g32-grec32_used, prc-prec_used, tub-tua, cod-CodeUsed());
	printf("\
          word     rec       rec      rec     rec    rec        byte      byte\n");
	printf("\
===============================================================================\n");
	break;
    }
    fflush(stdout);
}

#endif
#if MRBGC_FREE_LIST_TYPE == 1

display_memory_statistics(f)
    int f;
{
    static unsigned f01, f02, f04, f08, f16, f32, f64, f28, f99;
    static unsigned src, g08, g16, g32, prc, cod;
    static unsigned htb, hpb, hua, hub, ttb, tpb, tua, tub;
    static CHAR buf1[128], buf2[128], buf3[128];
    static CHAR buf4[128], buf5[128], buf6[128];
    switch(f){
      case 0:
      case 1:
	htb = f01total+f02total*2+f04total*4+f08total*8+f16total*16+
	      f32total*32+f64total*64+f28total*128+f99total;
	ttb = htb*sizeof(CELL)+
	      srec_total*sizeof(SUSPENSION_RECORD)+
	      grec08_total*sizeof(GOAL_RECORD)+
	      grec16_total*sizeof(GOAL_RECORD16)+
	      grec32_total*sizeof(GOAL_RECORD32)+
	      prec_total*sizeof(PARENT_RECORD);
	hpb = f01peek+f02peek*2+f04peek*4+f08peek*8+f16peek*16+
	      f32peek*32+f64peek*64+f28peek*128+f99peek;
	tpb = hpb*sizeof(CELL)+
	      srec_peek*sizeof(SUSPENSION_RECORD)+
	      grec08_peek*sizeof(GOAL_RECORD)+
	      grec16_peek*sizeof(GOAL_RECORD16)+
	      grec32_peek*sizeof(GOAL_RECORD32)+
	      prec_peek*sizeof(PARENT_RECORD);
	hub = f01used+f02used*2+f04used*4+f08used*8+f16used*16+
	      f32used*32+f64used*64+f28used*128+f99used;
	tub = hub*sizeof(CELL)+
	      srec_used*sizeof(SUSPENSION_RECORD)+
	      grec08_used*sizeof(GOAL_RECORD)+
	      grec16_used*sizeof(GOAL_RECORD16)+
	      grec32_used*sizeof(GOAL_RECORD32)+
	      prec_used*sizeof(PARENT_RECORD);
	break;
      case 2:
	hua = f01used+f02used*2+f04used*4+f08used*8+f16used*16+
	      f32used*32+f64used*64+f28used*128+f99used;
	tua = hua*sizeof(CELL)+
	      srec_used*sizeof(SUSPENSION_RECORD)+
	      grec08_used*sizeof(GOAL_RECORD)+
	      grec16_used*sizeof(GOAL_RECORD16)+
	      grec32_used*sizeof(GOAL_RECORD32)+
	      prec_used*sizeof(PARENT_RECORD);
	break;
    }
    if(f == 1){
	f01 = f01used; f02 = f02used; f04 = f04used; f08 = f08used;
	f16 = f16used; f32 = f32used; f64 = f64used; f28 = f28used;
	f99 = f99used;
	src = srec_used;
	g08 = grec08_used; g16 = grec16_used; g32 = grec32_used;
	prc = prec_used;
	cod = CodeUsed();
    }
/******************************************************************************
	   1W	    2W	     4W	      8W     16W     32W    64W	 128W	  More
TO: 123456789 12345678 12345678 12345678 1234567 1234567 123456 12345 12345678
      KL1-Data	  Srec	    Gr08     Gr16    Gr32   Prec   HeapTotal	  Code
TO: 1234567890 1234567 123456789 12345678 1234567 123456 12345678901 123456789
	  word	   rec	     rec      rec     rec    rec	byte	  byte
******************************************************************************/
    SelectWindow(CONSOLE);
    switch(f){
      case 0:
	printf("\
===============================================================================\n");
#if MRBGC_STATISTICS == 2
	printf("\
           1W       2W       4W       8W     16W     32W    64W  128W     More\n");
	printf("DRF: %8d\n", mst_deref);
	printf("CLS:          %8d\n", mst_cslst);
	printf(" -F:          %8d\n", mst_cflst);
	printf("CVC: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_csv01, mst_csv02, mst_csv04, mst_csv08,
	       mst_csv16, mst_csv32, mst_csv64, mst_csv28);
	printf(" -F: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_cfv01, mst_cfv02, mst_cfv04, mst_cfv08,
	       mst_cfv16, mst_cfv32, mst_cfv64, mst_cfv28);
	printf("CVL: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_cvl01, mst_cvl02, mst_cvl04, mst_cvl08,
	       mst_cvl16, mst_cvl32, mst_cvl64, mst_cvl28);
	printf("CBL: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_cbl01, mst_cbl02, mst_cbl04, mst_cbl08,
	       mst_cbl16, mst_cbl32, mst_cbl64, mst_cbl28);
	printf("RLS:          %8d\n", mst_rslst);
	printf(" -F:          %8d\n", mst_rflst);
	printf("RVC: %8d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       mst_rsv01, mst_rsv02, mst_rsv04, mst_rsv08,
	       mst_rsv16, mst_rsv32, mst_rsv64, mst_rsv28, mst_rsv99);
	printf(" -F: %8d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       mst_rfv01, mst_rfv02, mst_rfv04, mst_rfv08,
	       mst_rfv16, mst_rfv32, mst_rfv64, mst_rfv28, mst_rfv99);
	printf("RBL: %8d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       mst_rbl01, mst_rbl02, mst_rbl04, mst_rbl08,
	       mst_rbl16, mst_rbl32, mst_rbl64, mst_rbl28, mst_rbl99);
	printf("RMG:          %8d\n", mst_merge);
	printf("\
-------------------------------------------------------------------------------\n");
#endif
	printf("\
           1W       2W       4W       8W     16W     32W    64W  128W     More\n");
	printf("TO: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01total, f02total, f04total, f08total, f16total, f32total,
	       f64total, f28total, f99total);
	printf("PK: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01peek, f02peek, f04peek, f08peek, f16peek, f32peek,
	       f64peek, f28peek, f99peek);
	printf("US: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01used, f02used, f04used, f08used, f16used, f32used,
	       f64used, f28used, f99used);
	printf("\
-------------------------------------------------------------------------------\n");
	printf("\
      KL1-Data    Srec      Gr08     Gr16    Gr32   Prec   HeapTotal      Code\n");
	printf("TO: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       htb, srec_total, grec08_total, grec16_total, grec32_total,
	       prec_total, ttb, CodeUsed());
	printf("PK: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hpb, srec_peek, grec08_peek, grec16_peek, grec32_peek,
	       prec_peek, tpb, CodeUsed());
	printf("US: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hub, srec_used, grec08_used, grec16_used, grec32_used,
	       prec_used, tub, CodeUsed());
	printf("\
          word     rec       rec      rec     rec    rec        byte      byte\n");
	printf("\
===============================================================================\n");
	break;
      case 1:
	printf("\n\GC-%d\n", gc_counter);
	printf("\
===============================================================================\n");
#if MRBGC_STATISTICS == 2
	printf("\
           1W       2W       4W       8W     16W     32W    64W  128W     More\n");

	printf("DRF: %8d\n", mst_deref);
	printf("CLS:          %8d\n", mst_cslst);
	printf(" -F:          %8d\n", mst_cflst);
	printf("CVC: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_csv01, mst_csv02, mst_csv04, mst_csv08,
	       mst_csv16, mst_csv32, mst_csv64, mst_csv28);
	printf(" -F: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_cfv01, mst_cfv02, mst_cfv04, mst_cfv08,
	       mst_cfv16, mst_cfv32, mst_cfv64, mst_cfv28);
	printf("CVL: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_cvl01, mst_cvl02, mst_cvl04, mst_cvl08,
	       mst_cvl16, mst_cvl32, mst_cvl64, mst_cvl28);
	printf("CBL: %8d %8d %8d %8d %7d %7d %6d %5d\n",
	       mst_cbl01, mst_cbl02, mst_cbl04, mst_cbl08,
	       mst_cbl16, mst_cbl32, mst_cbl64, mst_cbl28);
	printf("RLS:          %8d\n", mst_rslst);
	printf(" -F:          %8d\n", mst_rflst);
	printf("RVC: %8d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       mst_rsv01, mst_rsv02, mst_rsv04, mst_rsv08,
	       mst_rsv16, mst_rsv32, mst_rsv64, mst_rsv28, mst_rsv99);
	printf(" -F: %8d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       mst_rfv01, mst_rfv02, mst_rfv04, mst_rfv08,
	       mst_rfv16, mst_rfv32, mst_rfv64, mst_rfv28, mst_rfv99);
	printf("RBL: %8d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       mst_rbl01, mst_rbl02, mst_rbl04, mst_rbl08,
	       mst_rbl16, mst_rbl32, mst_rbl64, mst_rbl28, mst_rbl99);
	printf("RMG:          %8d\n", mst_merge);
	printf("\
-------------------------------------------------------------------------------\n");
#endif
	sprintf(buf1, "TO: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01total, f02total, f04total, f08total, f16total, f32total,
	       f64total, f28total, f99total);
	sprintf(buf2, "TO: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01peek, f02peek, f04peek, f08peek, f16peek, f32peek,
	       f64peek, f28peek, f99peek);
	sprintf(buf3, "TO: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01used, f02used, f04used, f08used, f16used, f32used,
	       f64used, f28used, f99used);
	sprintf(buf4, "TO: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       htb, srec_total, grec08_total, grec16_total, grec32_total,
	       prec_total, ttb, CodeUsed());
	sprintf(buf5, "PK: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hpb, srec_peek, grec08_peek, grec16_peek, grec32_peek,
	       prec_peek, tpb, CodeUsed());
	sprintf(buf6, "US: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hub, srec_used, grec08_used, grec16_used, grec32_used,
	       prec_used, tub, CodeUsed());
	break;
      case 2:
	printf("\
           1W       2W       4W       8W     16W     32W    64W  128W     More\n");
	printf("%s%s%s", buf1, buf2, buf3);
	printf("AF: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01used, f02used, f04used, f08used, f16used, f32used,
	       f64used, f28used, f99used);
	printf("GC: %9d %8d %8d %8d %7d %7d %6d %5d %8d\n",
	       f01-f01used, f02-f02used, f04-f04used, f08-f08used,
	       f16-f16used, f32-f32used, f64-f64used, f28-f28used,
	       f99-f99used);
	printf("\
-------------------------------------------------------------------------------\n");
	printf("\
      KL1-Data    Srec      Gr08     Gr16    Gr32   Prec   HeapTotal      Code\n");
	printf("%s%s%s", buf4, buf5, buf6);
	printf("AF: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hua, srec_used, grec08_used, grec16_used, grec32_used,
	       prec_used, tua, CodeUsed());
	printf("GC: %10d %7d %9d %8d %7d %6d %11d %9d\n",
	       hub-hua, src-srec_used, g08-grec08_used, g16-grec16_used,
	       g32-grec32_used, prc-prec_used, tub-tua, cod-CodeUsed());
	printf("\
          word     rec       rec      rec     rec    rec        byte      byte\n");
	printf("\
===============================================================================\n");
	break;
    }
    fflush(stdout);
}

#endif
#else

display_memory_statistics(f)
    int f;
{
    static unsigned ha, hb, sa, sb, ga, gb, pa, pb, ta, tb, ca, cb;
    switch(f){
      case 0:
      case 1:
	hb = HeapUsedKL1();
	sb = SrecUsed();
	gb = GrecUsed();
	pb = PrecUsed();
	tb = HeapUsed()*sizeof(CELL);
	cb = CodeUsed();
	break;
      case 2:
	ha = HeapUsedKL1();
	sa = SrecUsed();
	ga = GrecUsed();
	pa = PrecUsed();
	ta = HeapUsed()*sizeof(CELL);
	ca = CodeUsed();
	break;
    }
/*************************************************************************
   KL1-Data   Srec   Grec  Prec	 HeapTotal     Code
  123456789 123456 123456 12345 1234567890 12345678
       word    rec    rec   rec	      byte     byte
**************************************************************************
GC-1234	 KL1-Data   Srec   Grec	 Prec  HeapTotal     Code
Used :	123456789 123456 123456 12345 1234567890 12345678
	     word    rec    rec	  rec	    byte     byte
*************************************************************************/
    SelectWindow(CONSOLE);
    switch(f){
      case 0:
	printf("   KL1-Data   Srec   Grec  Prec  HeapTotal     Code\n");
	printf("  %9d %6d %6d %5d %10d %8d\n", hb, sb, gb, pb, tb, cb);
	printf("       word    rec    rec   rec       byte     byte\n");
	break;
      case 1:
	printf("\nGC-%-4d  KL1-Data   Srec   Grec  Prec  HeapTotal     Code\n",
	       gc_counter);
	printf("Used :  %9d %6d %6d %5d %10d %8d\n",
	       hb, sb, gb, pb, tb, cb);
	break;
      case 2:
	printf("After:  %9d %6d %6d %5d %10d %8d\n",
	       ha, sa, ga, pa, ta, ca);
	printf("GCed :  %9d %6d %6d %5d %10d %8d\n",
	       hb-ha, sb-sa, gb-ga, pb-pa, tb-ta, cb-ca);
	printf("             word    rec    rec   rec       byte     byte\n");
	break;
    }
    fflush(stdout);
}

#endif


/*************************************************************************
*   Swap Goals in Highest Priority Queue.				 *
*************************************************************************/

#if GC_SWAP_GOALS_WHEN_PANIC
static swap_highest_queue()
{
    register GOAL_RECORD *p, *q, *r;

    p = highest->head;
#if TWO_WAY_READY_GOAL_POOL
    highest->tail = p;
#endif
    q = NULL;
    while(p != NULL){
	r = GoalQueuePt(p);
	SetGoalQueuePt2(p, q);
	q = p;
	p = r;
    }
    if(highest->head != q){
	highest->head = q;
	return(YES);
    }else{
	return(NO);
    }
}
#endif
