/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
**************************************************************************

KLB_PACKED_CODE:
  YES -> All data (char, short, long) is packed compactly,
  NO  -> Long/Short date is aligned 4/2 byte boundary.

KLB_4BYTE_REL_ADDR:
  YES -> Relative address use 4 byte,
  NO  -> Relative address use 2 byte, Module size must be less than 32KB.
*/

#if KLB_PACKED_CODE
#define Z(A,B) A
#else
#define Z(A,B) B
#endif

#if KLB_4BYTE_REL_ADDR
#define ZZ(A,B,C,D) Z(C,D)
#else
#define ZZ(A,B,C,D) Z(A,B)
#endif

#if KLB_4BYTE_REL_ADDR
typedef long RADDR;
typedef unsigned long MSIZE;
#else
typedef short RADDR;
typedef unsigned short MSIZE;
#endif


/*************************************************************************
*    Date Length & Get/Put Macros					 *
*************************************************************************/

#define KLB_OPCODE_LENGTH		1
#define KLB_REG_LENGTH			1
#define KLB_ATOM_LENGTH			2
#define KLB_INTEGER_LENGTH		4
#define KLB_FLOAT_LENGTH		4
#define KLB_ARITY_LENGTH		1
#define KLB_INDEX_LENGTH		1
#define KLB_REPNUM_LENGTH		1
#define KLB_PRED_ARITY_LENGTH		1
#define KLB_PRED_ID_LENGTH		4
#define KLB_CELL_LENGTH			sizeof(CELL)
#define KLB_REL_ADDR_LENGTH		ZZ(2,2,4,4)
#define KLB_MOD_PRED_SIZE_LENGTH	ZZ(2,2,4,4)

#define PutOpCode(x, p)		{ *(p) = (x); CheckCode(p); }
#define PutReg(x, p)		{ *(p) = (x); }
#define PutReg2(x, p)		{ *(p) = (x)-1; }
#define PutAtom(x, p)		{ *(unsigned short *)(p) = (x); }
#define PutInt(x, p)		{ *(long *)(p) = (x); }
#define PutFloat(x, p)		{ *(long *)(p) = (x); }
#define PutArity(x, p)		{ *(p) = (x); }
#define PutIndex(x, p)		{ *(p) = (x); }
#define PutRepnum(x, p)		{ *(p) = (x); }
#define PutPredArity(x, p)	{ *(p) = (x); }
#define PutPredID(x, p)		{ *(unsigned long *)(p) = (x); }
#define PutRelAddr(x, p)	{ *(RADDR *)(p) = (x); }
#define PutModPredSize(x, p)	{ *(MSIZE *)(p) = (x); }
#define PutChar(x, p)		{ *(p) = (x); }
#define PutShort(x, p)		{ *(short *)(p) = (x); }
#define PutLong(x, p)		{ *(long *)(p) = (x); }
#define PutCell(ty, va, mr, p)	{ SetAll(((CELL *)(p)), (ty), (va), (mr)); }

#define GetOpCode(p)	    (*(unsigned char *)(p))
#define GetReg(p)	    (*(unsigned char *)(p))
#define GetReg2(p)	    ((*(unsigned char *)(p))+1)
#define GetAtom(p)	    (*(unsigned short *)(p))
#define GetInt(p)	    (*(long *)(p))
#define GetFloat(p)	    (*(long *)(p))
#define GetArity(p)	    (*(unsigned char *)(p))
#define GetIndex(p)	    (*(unsigned char *)(p))
#define GetRepnum(p)	    (*(unsigned char *)(p))
#define GetPredArity(p)	    (*(unsigned char *)(p))
#define GetPredID(p)	    (*(unsigned long *)(p))
#define GetRelAddr(p)	    (*(RADDR *)(p))
#define GetAddr(p)	    ((p)+(*(RADDR *)(p)))
#define GetModPredSize(p)   (*(MSIZE *)(p))
#define GetChar(p)	    (*(char *)(p))
#define GetShort(p)	    (*(short *)(p))
#define GetLong(p)	    (*(long *)(p))
#define GetUChar(p)	    (*(unsigned char *)(p))
#define GetUShort(p)	    (*(unsigned short *)(p))
#define GetULong(p)	    (*(unsigned long *)(p))
#define GetCell(p)	    (*(struct cell *)(p))
#define GetCellP(p)	    ((struct cell *)(p))

#define GetRi(p)	    (&regs[GetReg(p)])
#define GetGi(p)	    (&(new_grec->args[GetReg(p)]))


/*************************************************************************
*    Module Header							 *
**************************************************************************

	   0/ 0 +----------------+
		|   Module Size	 | 2/4
	   2/ 4 +----------------+
		|   Module Name	 | 2/2
	   4/ 6 +----------------+
		|   Debug Info.	 | 1/1
	   5/ 7 +----------------+
		|  - not used -	 | 5/5
	  10/12 +----------------+
		|Entry Table Size| 2/2
	  12/14 +----------------+
		| Number of Entry| 2/2
	  14/16 +----------------+
		| Raddr to SCNST | 2/4
	  16/20 +----------------+

*/
#define MODULE_SIZE_LENGTH	ZZ( 2, 2, 4, 4)
#define MODULE_HEADER_LENGTH	ZZ(16,16,20,20)

#define MODULE_CODE_SIZE	ZZ( 0, 0, 0, 0)
#define MODULE_NAME		ZZ( 2, 2, 4, 4)
#define MODULE_DEBUG_INFO	ZZ( 4, 4, 6, 6)
#define MODULE_RESERVED_1	ZZ( 5, 5, 7, 7)
#define MODULE_RESERVED_2	ZZ( 6, 6, 8, 8)
#define MODULE_RESERVED_3	ZZ( 8, 8,10,10)
#define MODULE_ENTRY_TABLE_SIZE ZZ(10,10,12,12)
#define MODULE_NUMBER_OF_ENTRY	ZZ(12,12,14,14)
#define MODULE_CONSTANT_OFFSET	ZZ(14,14,16,16)

#define MODULE_DEBUG_ON		1

#define GetModuleSize(mtop)	GetModPredSize((mtop)+MODULE_CODE_SIZE)
#define GetModuleName(mtop)	GetAtom((mtop)+MODULE_NAME)
#define GetModuleDebug(mtop)	GetUChar((mtop)+MODULE_DEBUG_INFO)
#define GetEntryTableSize(mtop) GetUShort((mtop)+MODULE_ENTRY_TABLE_SIZE)
#define GetNumberOfEntry(mtop)	GetUShort((mtop)+MODULE_NUMBER_OF_ENTRY)
#define GetConstantOffset(mtop) GetRelAddr((mtop)+MODULE_CONSTANT_OFFSET)


/*************************************************************************
*    Entry Table							 *
**************************************************************************

			 2		2/4
Hash		+----------------+----------------+
Table:	     #0 |Collision Number| Raddr to CTBL -+--+
		+----------------+----------------+  |
		|		 .		  |  |
		|		 .		  |  |
		+----------------+----------------+  |
	    #15 |		 |		  |  |
		+----------------+----------------+  |
						     |
			 4		2/4	     |
Collision	+----------------+----------------+<-+
Table:		|  Predicate ID	 | Raddr to Pred. |
		+----------------+----------------+
		|		 .		  |
		|		 .		  |
		+----------------+----------------+

*/
#define CNUM_of_ENTRY_TABLE		0
#define OFST_of_ENTRY_TABLE		ZZ(2,2,2,4)
#define TLEN_of_ENTRY_TABLE		ZZ(4,4,6,8)
#define PRED_of_ENTRY_TABLE		0
#define LAB_of_ENTRY_TABLE		4
#define ELEN_of_ENTRY_TABLE		ZZ(6,8,8,8)

#define ENTRY_TABLE_HASH_MASK		0xF
#define ENTRY_TABLE_HASH_FUNC(pid)	((pid^(pid>>16))&ENTRY_TABLE_HASH_MASK)
#define ENTRY_TABLE_HASH_TABLE_SIZE \
				((ENTRY_TABLE_HASH_MASK+1)*TLEN_of_ENTRY_TABLE)


/*************************************************************************
*    Predicate Header							 *
**************************************************************************

	   0/ 0 +----------------+
		| Predicate Size | 2/4
	   2/ 4 +----------------+
		| Raddr to M-Head| 2/4
	   4/ 8 +----------------+
		| Predicate Name | 2/2
	   6/10 +----------------+
		|      Arity	 | 1/1
	   7/11 +----------------+
		|   Debug Info.	 | 1/1
	   8/12 +----------------+
		|  Red. Counter	 | 4/4
	  12/16 +----------------+
		|  Susp. Counter | 4/4
	  16/20 +----------------+

*/
#define PREDICATE_SIZE_LENGTH		ZZ( 2, 2, 4, 4)
#define PREDICATE_HEADER_LENGTH		ZZ(16,16,20,20)
#define PREDICATE_HEADER_LENGTH_1	ZZ( 4, 4, 8, 8)
#define PREDICATE_HEADER_LENGTH_2	ZZ(12,12,12,12)

#define PREDICATE_CODE_SIZE		ZZ( 0, 0, 0, 0)
#define PREDICATE_TO_MODULE_HEADER	ZZ( 2, 2, 4, 4)
#define PREDICATE_NAME			ZZ( 4, 4, 8, 8)
#define PREDICATE_ARITY			ZZ( 6, 6,10,10)
#define PREDICATE_DEBUG_INFO		ZZ( 7, 7,11,11)
#define PREDICATE_RCOUNT		ZZ( 8, 8,12,12)
#define PREDICATE_SCOUNT		ZZ(12,12,16,16)

#define PREDICATE_SPY_ON		1

#define GetPredicateTop(code) \
    ((code)-PREDICATE_HEADER_LENGTH)
#define GetPredicateSize(code) \
    GetModPredSize(GetPredicateTop(code)+PREDICATE_CODE_SIZE)
#define GetPredicateName(code) \
    GetAtom(GetPredicateTop(code)+PREDICATE_NAME)
#define GetPredicateArity(code) \
    GetPredArity(GetPredicateTop(code)+PREDICATE_ARITY)
#define GetPredicateDebug(code) \
    GetUChar(GetPredicateTop(code)+PREDICATE_DEBUG_INFO)
#define GetPredicateReductionCount(code) \
    GetULong(GetPredicateTop(code)+PREDICATE_RCOUNT)
#define GetPredicateSuspensionCount(code) \
    GetULong(GetPredicateTop(code)+PREDICATE_SCOUNT)
#define GetModuleTop(code) \
    GetAddr(GetPredicateTop(code)+PREDICATE_TO_MODULE_HEADER)


/*************************************************************************
*    Adjust PC -- 4byte Boundary					 *
*************************************************************************/

#define AdjustPC(p) (p) = (OBJ *)((((int)(p))+3)&0xFFFFFFFC)

#if KLB_PACKED_CODE
#define AdjustPCunlessPackedCode(p)
#else
#define AdjustPCunlessPackedCode(p) AdjustPC(p)
#endif


/*************************************************************************
*    KL1B Instruction Argument Type					 *
*************************************************************************/

#define NO_ARG			0x00
#define REG			0x01
#define REGS2			0x02
#define REGS3			0x03
#define REGS4			0x04
#define REGS5			0x05
#define REGS6			0x06
#define REGS7			0x07
#define REGS8			0x08

#define REG_ATM			0x0A
#define REG_ATM_LAB		0x0B
#define REG_IT			0x0C
#define REG_IT_LAB		0x0D
#define REG_FLOT		0x0E
#define REG_FLOT_LAB		0x0F
#define REG_ARITY		0x10
#define REG_ARITY_LAB		0x11
#define REG_LAB			0x12
#define REG_LAB6		0x13

#define REG_IDX			0x14
#define REG_IDX_REG		0x15
#define REG_IDX_ATM		0x16
#define REG_IDX_IT		0x17
#define REG_IDX_FLOT		0x18

#define ARG			0x1A
#define ARG_REG			0x1B
#define ARG_ATM			0x1C
#define ARG_IT			0x1D
#define ARG_FLOT		0x1E
#define ARG_LAB			0x1F

#define LAB			0x20
#define PARITY			0x21
#define PARITY_LAB		0x22
#define PARITY_LAB_REG		0x23
#define MOD_PRED_PARITY		0x24

#define REG_REG_ATM		0x28
#define REG_ARITY_ATM		0x29
#define REG_LAB_REG_REG		0x2A
#define REG_REG_REP		0x2B
#define ARG_REG_REP		0x2C
#define REG_IDX_REG_REP		0x2D

#define JUMP_ON			0x30
#define BRANCH_ON_A		0x31
#define BRANCH_ON_I		0x32
#define HASH_ON_A		0x33
#define HASH_ON_I		0x34

#define ASSM_IGNORE		0x3C
#define ASSM_NOT_SUPPORTED	0x3D
#define ASSM_CONTROL		0x3E
#define ASSM_CONSTANT		0x3F


/*************************************************************************
*    KL1B Instruction Argument Offset & Length				 *
*************************************************************************/

/** NO_ARG
P2: [OP]
B2: [OP|  ----	]
P4: [OP]
B4: [OP|  ----	] */
#define LEN_of_NO_ARG			Z(1,4)
#define LEN_of_2B_NO_ARG		Z(1,3)

/** REG
P2: [OP|R1]
B2: [OP|R1| --- ]
P4: [OP|R1]
B4: [OP|R1| --- ] */
#define REG_of_REG			1
#define LEN_of_REG			Z(2,4)
#define LEN_of_2B_REG			Z(2,3)

/** REGS2
P2: [OP|R1|R2]
B2: [OP|R1|R2|--]
P4: [OP|R1|R2]
B4: [OP|R1|R2|--] */
#define RE1_of_REGS2			1
#define RE2_of_REGS2			2
#define LEN_of_REGS2			Z(3,4)
#define LEN_of_2B_REGS2			Z(3,3)

/** REGS3
P2: [OP|R1|R2|R3]
B2: [OP|R1|R2|R3]
P4: [OP|R1|R2|R3]
B4: [OP|R1|R2|R3] */
#define RE1_of_REGS3			1
#define RE2_of_REGS3			2
#define RE3_of_REGS3			3
#define LEN_of_REGS3			4
#define LEN_of_2B_REGS3			Z(4,7)

/** REGS4
P2: [OP|R1|R2|R3| R4]
B2: [OP|R1|R2|R3][R4|  ----  ]
P4: [OP|R1|R2|R3| R4]
B4: [OP|R1|R2|R3][R4|  ----  ] */
#define RE1_of_REGS4			1
#define RE2_of_REGS4			2
#define RE3_of_REGS4			3
#define RE4_of_REGS4			4
#define LEN_of_REGS4			Z(5,8)
#define LEN_of_2B_REGS4			Z(5,7)

/** REGS5
P2: [OP|R1|R2|R3| R4|R5]
B2: [OP|R1|R2|R3][R4|R5| --- ]
P4: [OP|R1|R2|R3| R4|R5]
B4: [OP|R1|R2|R3][R4|R5| --- ] */
#define RE1_of_REGS5			1
#define RE2_of_REGS5			2
#define RE3_of_REGS5			3
#define RE4_of_REGS5			4
#define RE5_of_REGS5			5
#define LEN_of_REGS5			Z(6,8)
#define LEN_of_2B_REGS5			Z(6,7)

/** REGS6
P2: [OP|R1|R2|R3| R4|R5|R6]
B2: [OP|R1|R2|R3][R4|R5|R6|--]
P4: [OP|R1|R2|R3| R4|R5|R6]
B4: [OP|R1|R2|R3][R4|R5|R6|--] */
#define RE1_of_REGS6			1
#define RE2_of_REGS6			2
#define RE3_of_REGS6			3
#define RE4_of_REGS6			4
#define RE5_of_REGS6			5
#define RE6_of_REGS6			6
#define LEN_of_REGS6			Z(7,8)
#define LEN_of_2B_REGS6			Z(7,7)

/** REGS7
P2: [OP|R1|R2|R3| R4|R5|R6|R7]
B2: [OP|R1|R2|R3][R4|R5|R6|R7]
P4: [OP|R1|R2|R3| R4|R5|R6|R7]
B4: [OP|R1|R2|R3][R4|R5|R6|R7] */
#define RE1_of_REGS7			1
#define RE2_of_REGS7			2
#define RE3_of_REGS7			3
#define RE4_of_REGS7			4
#define RE5_of_REGS7			5
#define RE6_of_REGS7			6
#define RE7_of_REGS7			7
#define LEN_of_REGS7			8
#define LEN_of_2B_REGS7			Z(8,11)

/** REGS8
P2: [OP|R1|R2|R3| R4|R5|R6|R7| R8]
B2: [OP|R1|R2|R3][R4|R5|R6|R7][R8|  ----  ]
P4: [OP|R1|R2|R3| R4|R5|R6|R7| R8]
B4: [OP|R1|R2|R3][R4|R5|R6|R7][R8|  ----  ] */
#define RE1_of_REGS8			1
#define RE2_of_REGS8			2
#define RE3_of_REGS8			3
#define RE4_of_REGS8			4
#define RE5_of_REGS8			5
#define RE6_of_REGS8			6
#define RE7_of_REGS8			7
#define RE8_of_REGS8			8
#define LEN_of_REGS8			Z(9,12)
#define LEN_of_2B_REGS8			Z(9,11)

/** REG_ATM
P2: [OP|RG| ATM ]
B2: [OP|RG| ATM ]
P4: [OP|RG| ATM ]
B4: [OP|RG| ATM ] */
#define REG_of_REG_ATM			1
#define ATM_of_REG_ATM			2
#define LEN_of_REG_ATM			4

/** REG_ATM_LAB
P2: [OP|RG| ATM |  LAB ]
B2: [OP|RG| ATM ][ LAB | --- ]
P4: [OP|RG| ATM |     LAB    ]
B4: [OP|RG| ATM ][    LAB    ] */
#define REG_of_REG_ATM_LAB		1
#define ATM_of_REG_ATM_LAB		2
#define LAB_of_REG_ATM_LAB		4
#define LEN_of_REG_ATM_LAB		ZZ(6,8,8,8)

/** REG_IT
P2: [OP|RG|	IT     ]
B2: [OP|RG| --- ][    IT     ]
P4: [OP|RG|	IT     ]
B4: [OP|RG| --- ][    IT     ] */
#define REG_of_REG_IT			1
#define IT_of_REG_IT			Z(2,4)
#define LEN_of_REG_IT			Z(6,8)

/** REG_IT_LAB
P2: [OP|RG| LAB |     IT     ]
B2: [OP|RG| LAB ][    IT     ]
P4: [OP|RG|	IT     |     LAB    ]
B4: [OP|RG| --- ][    IT     ][	   LAB	  ] */
#define REG_of_REG_IT_LAB		1
#define IT_of_REG_IT_LAB		ZZ(4,4,2,4)
#define LAB_of_REG_IT_LAB		ZZ(2,2,6,8)
#define LEN_of_REG_IT_LAB		ZZ(8,8,10,12)

/** REG_FLOT
P2: [OP|RG|    FLOT    ]
B2: [OP|RG| --- ][   FLOT    ]
P4: [OP|RG|    FLOT    ]
B4: [OP|RG| --- ][   FLOT    ] */
#define REG_of_REG_FLOT			1
#define FLOT_of_REG_FLOT		Z(2,4)
#define LEN_of_REG_FLOT			Z(6,8)

/** REG_FLOT_LAB
P2: [OP|RG| LAB |    FLOT    ]
B2: [OP|RG| LAB ][   FLOT    ]
P4: [OP|RG|    FLOT    |     LAB    ]
B4: [OP|RG| --- ][   FLOT    ][	   LAB	  ] */
#define REG_of_REG_FLOT_LAB		1
#define FLOT_of_REG_FLOT_LAB		ZZ(4,4,2,4)
#define LAB_of_REG_FLOT_LAB		ZZ(2,2,6,8)
#define LEN_of_REG_FLOT_LAB		ZZ(8,8,10,12)

/** REG_ARITY
P2: [OP|RG|AR]
B2: [OP|RG|AR|--]
P4: [OP|RG|AR]
B4: [OP|RG|AR|--] */
#define REG_of_REG_ARITY		1
#define ARITY_of_REG_ARITY		2
#define LEN_of_REG_ARITY		ZZ(3,4,3,4)

/** REG_ARITY_LAB
P2: [OP|RG|AR|	LAB ]
B2: [OP|RG|AR|--][ LAB | --- ]
P4: [OP|RG|AR|	   LAB	  ]
B4: [OP|RG|AR|--][    LAB    ] */
#define REG_of_REG_ARITY_LAB		1
#define ARITY_of_REG_ARITY_LAB		2
#define LAB_of_REG_ARITY_LAB		ZZ(3,4,3,4)
#define LEN_of_REG_ARITY_LAB		ZZ(5,8,7,8)

/** REG_LAB
P2: [OP|RG| LAB ]
B2: [OP|RG| LAB ]
P4: [OP|RG|    LAB     ]
B4: [OP|RG| --- ][    LAB    ] */
#define REG_of_REG_LAB			1
#define LAB_of_REG_LAB			ZZ(2,2,2,4)
#define LEN_of_REG_LAB			ZZ(4,4,6,8)

/** REG_LAB6
P2: [OP|RG| LB1 |  LB2 | LB3 |	LB4 | LB5 |  LB6 ]
B2: [OP|RG| LB1 ][ LB2 | LB3 ][ LB4 | LB5 ][ LB6 | --- ]
P4: [OP|RG|    LB1     |    LB2	    |	 .....	 |    LB6     ]
B4: [OP|RG| --- ][    LB1    ][	   LB2	  ][	.....  ][    LB6     ] */
#define REG_of_REG_LAB6			1
#define LB1_of_REG_LAB6			ZZ( 2, 2, 2, 4)
#define LB2_of_REG_LAB6			ZZ( 4, 4, 6, 8)
#define LB3_of_REG_LAB6			ZZ( 6, 6,10,12)
#define LB4_of_REG_LAB6			ZZ( 8, 8,14,16)
#define LB5_of_REG_LAB6			ZZ(10,10,18,20)
#define LB6_of_REG_LAB6			ZZ(12,12,22,24)
#define LEN_of_REG_LAB6			ZZ(14,16,26,28)

/** REG_IDX
P2: [OP|RG|IX]
B2: [OP|RG|IX|--]
P4: [OP|RG|IX]
B4: [OP|RG|IX|--] */
#define REG_of_REG_IDX			1
#define IDX_of_REG_IDX			2
#define LEN_of_REG_IDX			Z(3,4)

/** REG_IDX_REG
P2: [OP|RG|IX|R2]
B2: [OP|RG|IX|R2]
P4: [OP|RG|IX|R2]
B4: [OP|RG|IX|R2] */
#define REG_of_REG_IDX_REG		1
#define IDX_of_REG_IDX_REG		2
#define RE2_of_REG_IDX_REG		3
#define LEN_of_REG_IDX_REG		4

/** REG_IDX_ATM
P2: [OP|RG|IX|	ATM ]
B2: [OP|RG|IX|--][ ATM | --- ]
P4: [OP|RG|IX|	ATM ]
B4: [OP|RG|IX|--][ ATM | --- ] */
#define REG_of_REG_IDX_ATM		1
#define IDX_of_REG_IDX_ATM		2
#define ATM_of_REG_IDX_ATM		Z(3,4)
#define LEN_of_REG_IDX_ATM		Z(5,8)

/** REG_IDX_IT
P2: [OP|RG|IX|	   IT	  ]
B2: [OP|RG|IX|--][     IT     ]
P4: [OP|RG|IX|	   IT	  ]
B4: [OP|RG|IX|--][     IT     ] */
#define REG_of_REG_IDX_IT		1
#define IDX_of_REG_IDX_IT		2
#define IT_of_REG_IDX_IT		Z(3,4)
#define LEN_of_REG_IDX_IT		Z(7,8)

/** REG_IDX_FLOT
P2: [OP|RG|IX|	  FLOT	 ]
B2: [OP|RG|IX|--][    FLOT    ]
P4: [OP|RG|IX|	  FLOT	 ]
B4: [OP|RG|IX|--][    FLOT    ] */
#define REG_of_REG_IDX_FLOT		1
#define IDX_of_REG_IDX_FLOT		2
#define FLOT_of_REG_IDX_FLOT		Z(3,4)
#define LEN_of_REG_IDX_FLOT		Z(7,8)

/** ARG
P2: [OP|AG]
B2: [OP|AG| --- ]
P4: [OP|AG]
B4: [OP|AG| --- ] */
#define ARG_of_ARG			1
#define LEN_of_ARG			Z(2,4)

/** ARG_REG
P2: [OP|AG|RG]
B2: [OP|AG|RG|--]
P4: [OP|AG|RG]
B4: [OP|AG|RG|--] */
#define ARG_of_ARG_REG			1
#define REG_of_ARG_REG			2
#define LEN_of_ARG_REG			Z(3,4)

/** ARG_ATM
P2: [OP|AG| ATM ]
B2: [OP|AG| ATM ]
P4: [OP|AG| ATM ]
B4: [OP|AG| ATM ] */
#define ARG_of_ARG_ATM			1
#define ATM_of_ARG_ATM			2
#define LEN_of_ARG_ATM			4

/** ARG_IT
P2: [OP|AG|	IT     ]
B2: [OP|AG| --- ][    IT     ]
P4: [OP|AG|	IT     ]
B4: [OP|AG| --- ][    IT     ] */
#define ARG_of_ARG_IT			1
#define IT_of_ARG_IT			Z(2,4)
#define LEN_of_ARG_IT			Z(6,8)

/** ARG_FLOT
P2: [OP|AG|    FLOT    ]
B2: [OP|AG| --- ][   FLOT    ]
P4: [OP|AG|    FLOT    ]
B4: [OP|AG| --- ][   FLOT    ] */
#define ARG_of_ARG_FLOT			1
#define FLOT_of_ARG_FLOT		Z(2,4)
#define LEN_of_ARG_FLOT			Z(6,8)

/** ARG_LAB
P2: [OP|AG| LAB ]
B2: [OP|AG| LAB ]
P4: [OP|AG|    LAB     ]
B4: [OP|AG| --- ][    LAB    ] */
#define ARG_of_ARG_LAB			1
#define LAB_of_ARG_LAB			ZZ(2,2,2,4)
#define LEN_of_ARG_LAB			ZZ(4,4,6,8)

/** LAB
P2: [OP| LAB ]
B2: [OP|--| LAB ]
P4: [OP|    LAB	    ]
B4: [OP|  ----	][    LAB    ] */
#define LAB_of_LAB			ZZ(1,2,1,4)
#define LEN_of_LAB			ZZ(3,4,5,8)

/** PARITY
P2: [OP|PA]
B2: [OP|PA| --- ]
P4: [OP|PA]
B4: [OP|PA| --- ] */
#define PARITY_of_PARITY		1
#define LEN_of_PARITY			Z(2,4)

/** PARITY_LAB
P2: [OP|PA| LAB ]
B2: [OP|PA| LAB ]
P4: [OP|PA|    LAB     ]
B4: [OP|PA| --- ][    LAB    ] */
#define PARITY_of_PARITY_LAB		1
#define LAB_of_PARITY_LAB		ZZ(2,2,2,4)
#define LEN_of_PARITY_LAB		ZZ(4,4,6,8)

/** PARITY_LAB_REG
P2: [OP|PA| LAB | RG]
B2: [OP|PA| LAB ][RG|  ----  ]
P4: [OP|PA|RG|	  LAB	  ]
B4: [OP|PA|RG|--][    LAB    ] */
#define PARITY_of_PARITY_LAB_REG	1
#define LAB_of_PARITY_LAB_REG		ZZ(2,2,3,4)
#define REG_of_PARITY_LAB_REG		ZZ(4,4,2,2)
#define LEN_of_PARITY_LAB_REG		ZZ(5,8,7,8)

/** MOD_PRED_ARITY
P2: [OP|PA| MOD |   PRED-ID  ]
B2: [OP|PA| MOD ][  PRED-ID  ]
P4: [OP|PA| MOD |   PRED-ID  ]
B4: [OP|PA| MOD ][  PRED-ID  ] */
#define MOD_of_MOD_PRED_PARITY		2
#define PRED_of_MOD_PRED_PARITY		4
#define PARITY_of_MOD_PRED_PARITY	1
#define LEN_of_MOD_PRED_PARITY		8

/** REG_REG_ATM
P2: [OP|RG| ATM | R2]
B2: [OP|RG| ATM ][R2|  ----  ]
P4: [OP|RG| ATM | R2]
B4: [OP|RG| ATM ][R2|  ----  ] */
#define REG_of_REG_REG_ATM		1
#define ATM_of_REG_REG_ATM		2
#define RE2_of_REG_REG_ATM		4
#define LEN_of_REG_REG_ATM		Z(5,8)

/** REG_ARITY_ATM
P2: [OP|RG| ATM | AR]
B2: [OP|RG| ATM ][AR|  ----  ]
P4: [OP|RG| ATM | AR]
B4: [OP|RG| ATM ][AR|  ----  ] */
#define REG_of_REG_ARITY_ATM		1
#define ATM_of_REG_ARITY_ATM		2
#define ARITY_of_REG_ARITY_ATM		4
#define LEN_of_REG_ARITY_ATM		Z(5,8)

/** REG_LAB_REG_REG
P2: [OP|RG|R2|R3|  LAB ]
B2: [OP|RG|R2|R3][ LAB | --- ]
P4: [OP|RG|R2|R3|     LAB    ]
B4: [OP|RG|R2|R3][    LAB    ] */
#define REG_of_REG_LAB_REG_REG		1
#define LAB_of_REG_LAB_REG_REG		4
#define RE2_of_REG_LAB_REG_REG		2
#define RE3_of_REG_LAB_REG_REG		3
#define LEN_of_REG_LAB_REG_REG		ZZ(6,8,8,8)

/** REG_REG_REP
P2: [OP|RG|R2|RP]
B2: [OP|RG|R2|RP]
P4: [OP|RG|R2|RP]
B4: [OP|RG|R2|RP] */
#define REG_of_REG_REG_REP		1
#define RE2_of_REG_REG_REP		2
#define REP_of_REG_REG_REP		3
#define LEN_of_REG_REG_REP		4

/** ARG_REG_REP
P2: [OP|AG|R2|RP]
B2: [OP|AG|R2|RP]
P4: [OP|AG|R2|RP]
B4: [OP|AG|R2|RP] */
#define ARG_of_ARG_REG_REP		1
#define REG_of_ARG_REG_REP		2
#define REP_of_ARG_REG_REP		3
#define LEN_of_ARG_REG_REP		4

/** REG_IDX_REG_REP
P2: [OP|RG|IX|R2][RP]
B2: [OP|RG|IX|R2][RP|  ----  ]
P4: [OP|RG|IX|R2][RP]
B4: [OP|RG|IX|R2][RP|  ----  ] */
#define REG_of_REG_IDX_REG_REP		1
#define IDX_of_REG_IDX_REG_REP		2
#define RE2_of_REG_IDX_REG_REP		3
#define REP_of_REG_IDX_REG_REP		4
#define LEN_of_REG_IDX_REG_REP		Z(5,8)

/** JUMP_ON
P2: [OP|RG| SIZ |  LAB ]       + [ LAB ]
B2: [OP|RG| SIZ ][ LAB | --- ] + [ LAB ]
P4: [OP|RG| SIZ |     LAB    ] + [    LAB    ]
B4: [OP|RG| SIZ ][    LAB    ] + [    LAB    ] */
#define REG_of_JUMP_ON			1
#define SIZE_of_JUMP_ON			2
#define FAIL_of_JUMP_ON			4
#define TABLE_of_JUMP_ON		ZZ(6,8,8,8)
#define LAB_of_JUMP_ON			0
#define ELEN_of_JUMP_ON			ZZ(2,2,4,4)

/** BRANCH_ON_A
P2: [OP|RG| SIZ |  LAB ]       + [ ATM | LAB ]
B2: [OP|RG| SIZ ][ LAB | --- ] + [ ATM | LAB ]
P4: [OP|RG| SIZ |     LAB    ] + [ ATM |     LAB    ]
B4: [OP|RG| SIZ ][    LAB    ] + [ ATM | --- ][	   LAB	  ] */
#define REG_of_BRANCH_ON_A		1
#define SIZE_of_BRANCH_ON_A		2
#define FAIL_of_BRANCH_ON_A		4
#define TABLE_of_BRANCH_ON_A		ZZ(6,8,8,8)
#define ATM_of_BRANCH_ON_A		0
#define LAB_of_BRANCH_ON_A		ZZ(2,2,2,4)
#define ELEN_of_BRANCH_ON_A		ZZ(4,4,6,8)

/** BRANCH_ON_I
P2: [OP|RG| SIZ |  LAB ]       + [     IT    |	LAB ]
B2: [OP|RG| SIZ ][ LAB | --- ] + [     IT    ][ LAB | --- ]
P4: [OP|RG| SIZ |     LAB    ] + [     IT    ][	   LAB	  ]
B4: [OP|RG| SIZ ][    LAB    ] + [     IT    |	   LAB	  ] */
#define REG_of_BRANCH_ON_I		1
#define SIZE_of_BRANCH_ON_I		2
#define FAIL_of_BRANCH_ON_I		4
#define TABLE_of_BRANCH_ON_I		ZZ(6,8,8,8)
#define IT_of_BRANCH_ON_I		0
#define LAB_of_BRANCH_ON_I		4
#define ELEN_of_BRANCH_ON_I		ZZ(6,8,8,8)

/** HASH_ON_A
P2: [OP|RG| MSK |  LAB ]       + [ CNM | LAB ]
			       + [ ATM | LAB ]
B2: [OP|RG| MSK ][ LAB | --- ] + [ CNM | LAB ]
			       + [ ATM | LAB ]
P4: [OP|RG| MSK |     LAB    ] + [ CNM |     LAB    ]
			       + [ ATM |     LAB    ]
B4: [OP|RG| MSK ][    LAB    ] + [ CNM | --- ][	   LAB	  ]
			       + [ ATM | --- ][	   LAB	  ] */
#define REG_of_HASH_ON_A		1
#define MASK_of_HASH_ON_A		2
#define FAIL_of_HASH_ON_A		4
#define TABLE_of_HASH_ON_A		ZZ(6,8,8,8)
#define CNUM_of_HASH_ON_A		0
#define OFST_of_HASH_ON_A		ZZ(2,2,2,4)
#define TLEN_of_HASH_ON_A		ZZ(4,4,6,8)
#define ATM_of_HASH_ON_A		0
#define LAB_of_HASH_ON_A		ZZ(2,2,2,4)
#define ELEN_of_HASH_ON_A		ZZ(4,4,6,8)

/** HASH_ON_I
P2: [OP|RG| MSK |  LAB ]       + [ CNM | LAB ]
			       + [     IT    |	LAB ]
B2: [OP|RG| MSK ][ LAB | --- ] + [ CNM | LAB ]
			       + [     IT    ][ LAB | --- ]
P4: [OP|RG| MSK |     LAB    ] + [ CNM |     LAB    ]
			       + [     IT    |	   LAB	  ]
B4: [OP|RG| MSK ][    LAB    ] + [ CNM | --- ][	   LAB	  ]
			       + [     IT    ][	   LAB	  ] */
#define REG_of_HASH_ON_I		1
#define MASK_of_HASH_ON_I		2
#define FAIL_of_HASH_ON_I		4
#define TABLE_of_HASH_ON_I		ZZ(6,8,8,8)
#define CNUM_of_HASH_ON_I		0
#define OFST_of_HASH_ON_I		ZZ(2,2,2,4)
#define TLEN_of_HASH_ON_I		ZZ(4,4,6,8)
#define IT_of_HASH_ON_I			0
#define LAB_of_HASH_ON_I		4
#define ELEN_of_HASH_ON_I		ZZ(6,8,8,8)
