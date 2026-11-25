/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

/* Control */
#define KL1B_TRUE					0x001
#define KL1B_FAIL					0x002
#define KL1B_JUMP					0x003
#define KL1B_TRY_ME_ELSE				0x004
#define KL1B_OTHERWISE					0x005
#define KL1B_READ_EAGERLY				0x006
#define KL1B_SUSPEND					0x008
#define KL1B_PROCEED					0x009
#define KL1B_EXECUTE					0x00A
#define KL1B_EXECUTE_EXTERNAL				0x00B
#define KL1B_CREATE_GOAL				0x00C
#define KL1B_ENQUEUE_GOAL				0x00D
#define KL1B_ENQUEUE_GOAL_WITH_PRIORITY			0x00E
#define KL1B_ENQUEUE_GOAL_EXTERNAL			0x00F

/* Wait Bounded Value */
#define KL1B_WAIT					0x010

/* Check Type */
#define KL1B_IS_ATOM					0x011
#define KL1B_IS_INTEGER					0x012
#define KL1B_IS_FLOAT					0x013
#define KL1B_IS_LIST					0x014
#define KL1B_IS_VECTOR					0x015
#define KL1B_IS_STRING					0x016
#define KL1B_SWITCH_ON_TYPE				0x017

/* Check Value, Arity */
#define KL1B_TEST_ATOM					0x018
#define KL1B_TEST_NIL					0x019
#define KL1B_TEST_INTEGER				0x01A
#define KL1B_TEST_FLOAT					0x01B
#define KL1B_TEST_ARITY					0x01C
#define KL1B_JUMP_ON_INTEGER				0x01D
#define KL1B_JUMP_ON_ARITY				0x01E
#define KL1B_BRANCH_ON_ATOM				0x01F
#define KL1B_BRANCH_ON_INTEGER				0x020
#define KL1B_HASH_ON_ATOM				0x021
#define KL1B_HASH_ON_INTEGER				0x022
#define KL1B_TABLE_ENTRY				0x1F8
#define KL1B_BUCKET_ENTRY_I				0x1F9
#define KL1B_BUCKET_ENTRY_A				0x1FA

/* Wait Bounded Value & Check Type (1) */
#define KL1B_ATOM					0x024
#define KL1B_INTEGER					0x025
#define KL1B_FLOAT					0x026
#define KL1B_LIST					0x027
#define KL1B_VECTOR					0x028
#define KL1B_STRING					0x029

/* Wait Bounded Value & Check Type (2) */
#define KL1B_JUMP_ON_NON_ATOM				0x02A
#define KL1B_JUMP_ON_NON_INTEGER			0x02B
#define KL1B_JUMP_ON_NON_FLOAT				0x02C
#define KL1B_JUMP_ON_NON_LIST				0x02D
#define KL1B_JUMP_ON_NON_VECTOR				0x02E
#define KL1B_JUMP_ON_NON_STRING				0x02F

/* Check Type & Check Value, Arity */
#define KL1B_CHECK_ATOM					0x030
#define KL1B_CHECK_NIL					0x031
#define KL1B_CHECK_INTEGER				0x032
#define KL1B_CHECK_FLOAT				0x033
#define KL1B_CHECK_VECTOR				0x034

/* Wait Bounded Value & Check Type & Check Value, Arity */
#define KL1B_WAIT_ATOM					0x035
#define KL1B_WAIT_NIL					0x036
#define KL1B_WAIT_INTEGER				0x037
#define KL1B_WAIT_FLOAT					0x038
#define KL1B_WAIT_VECTOR				0x039

/* Wait Value -- General Unification */
#define KL1B_WAIT_VALUE					0x03A

/* Read Structure Element */
#define KL1B_READ_CAR					0x03C
#define KL1B_READ_CDR					0x03D
#define KL1B_READ_ELEMENT				0x03E

/* Put Value from Register to Register */
#define KL1B_PUT_VALUE					0x040
#define KL1B_PUT_MARKED_VALUE				0x041

/* Set Value from Register to New Goal Argument */
#define KL1B_SET_VALUE					0x042
#define KL1B_SET_MARKED_VALUE				0x043

/* Write Value from Register to Structure Element */
#define KL1B_WRITE_CAR_VALUE				0x044
#define KL1B_WRITE_CDR_VALUE				0x045
#define KL1B_WRITE_ELEMENT_VALUE			0x046
#define KL1B_WRITE_CAR_MARKED_VALUE			0x047
#define KL1B_WRITE_CDR_MARKED_VALUE			0x048
#define KL1B_WRITE_ELEMENT_MARKED_VALUE			0x049

/* Put Constant to Register */
#define KL1B_PUT_ATOM					0x04C
#define KL1B_PUT_NIL					0x04D
#define KL1B_PUT_INTEGER				0x04E
#define KL1B_PUT_FLOAT					0x04F
#define KL1B_PUT_LIST					0x050
#define KL1B_PUT_REUSED_LIST				0x051
#define KL1B_PUT_VECTOR					0x052
#define KL1B_PUT_REUSED_VECTOR				0x053
#define KL1B_PUT_STRUCTURED_CONSTANT			0x054

/* Set Constant to New Goal Argument */
#define KL1B_SET_ATOM					0x05C
#define KL1B_SET_NIL					0x05D
#define KL1B_SET_INTEGER				0x05E
#define KL1B_SET_FLOAT					0x05F

/* Write Constent to Structure Element */
#define KL1B_WRITE_CAR_ATOM				0x060
#define KL1B_WRITE_CDR_ATOM				0x061
#define KL1B_WRITE_ELEMENT_ATOM				0x062
#define KL1B_WRITE_CAR_NIL				0x063
#define KL1B_WRITE_CDR_NIL				0x064
#define KL1B_WRITE_ELEMENT_NIL				0x065
#define KL1B_WRITE_CAR_INTEGER				0x066
#define KL1B_WRITE_CDR_INTEGER				0x067
#define KL1B_WRITE_ELEMENT_INTEGER			0x068
#define KL1B_WRITE_CAR_FLOAT				0x069
#define KL1B_WRITE_CDR_FLOAT				0x06A
#define KL1B_WRITE_ELEMENT_FLOAT			0x06B

/* Put Variable to Register */
#define KL1B_PUT_VOID					0x06C
#define KL1B_PUT_VARIABLE				0x06D
#define KL1B_PUT_MARKED_VARIABLE			0x06E

/* Set Variable to New Goal Record */
#define KL1B_SET_VOID					0x070
#define KL1B_SET_VARIABLE				0x071
#define KL1B_SET_MARKED_VARIABLE			0x072

/* Write Variable to Structure Element */
#define KL1B_WRITE_CAR_VOID				0x074
#define KL1B_WRITE_CDR_VOID				0x075
#define KL1B_WRITE_ELEMENT_VOID				0x076
#define KL1B_WRITE_CAR_VARIABLE				0x077
#define KL1B_WRITE_CDR_VARIABLE				0x078
#define KL1B_WRITE_ELEMENT_VARIABLE			0x079
#define KL1B_WRITE_CAR_MARKED_VARIABLE			0x07A
#define KL1B_WRITE_CDR_MARKED_VARIABLE			0x07B
#define KL1B_WRITE_ELEMENT_MARKED_VARIABLE		0x07C

/* Active Unification */
#define KL1B_GET_ATOM					0x080
#define KL1B_GET_NIL					0x081
#define KL1B_GET_INTEGER				0x082
#define KL1B_GET_FLOAT					0x083
#define KL1B_GET_LIST_VALUE				0x084
#define KL1B_GET_VECTOR_VALUE				0x085
#define KL1B_GET_VALUE					0x086

/* Merged Instructions */
#define KL1B_WAIT_LIST_VAR_VAR				0x08E
#define KL1B_JUMP_ON_NON_LIST_VAR_VAR			0x08F
#define KL1B_PUT_FUNC					0x090
#define KL1B_PUT_REUSED_FUNC				0x091
#define KL1B_PUT_LIST_VAL_VAL				0x092
#define KL1B_PUT_REUSED_LIST_VAL_VAL			0x093
#define KL1B_PUT_LIST_VAL_VAR				0x094
#define KL1B_PUT_REUSED_LIST_VAL_VAR			0x095
#define KL1B_GET_LIST_VAL_VAR				0x096
#define KL1B_GET_REUSED_LIST_VAL_VAR			0x097
#define KL1B_READ_ELEMENTS_INC				0x098
#define KL1B_READ_ELEMENTS_DEC				0x099
#define KL1B_PUT_VALUES_INC				0x09A
#define KL1B_PUT_VALUES_DEC				0x09B
#define KL1B_SET_VALUES_INC				0x09C
#define KL1B_SET_VALUES_DEC				0x09D
#define KL1B_WRITE_ELEMENTS_INC				0x09E
#define KL1B_WRITE_ELEMENTS_DEC				0x09F

/* MRB-GC */
#define KL1B_COLLECT_VALUE				0x0A0
#define KL1B_COLLECT_LIST				0x0A1
#define KL1B_COLLECT_VECTOR				0x0A2

/* Guard Builtin -- Diff */
#define KL1B_G_DIFF					0x0A8

/* Guard Builtin -- Comparison */
#define KL1B_G_EQUAL					0x0AC
#define KL1B_G_NOT_EQUAL				0x0AD
#define KL1B_G_LESS_THAN				0x0AE
#define KL1B_G_NOT_LESS_THAN				0x0AF

/* Guard Builtin -- Calculation */
#define KL1B_G_ADD					0x0B0
#define KL1B_G_SUBTRACT					0x0B1
#define KL1B_G_MULTIPLY					0x0B2
#define KL1B_G_DIVIDE					0x0B3
#define KL1B_G_MODULO					0x0B4
#define KL1B_G_MINUS					0x0B5
#define KL1B_G_INCREMENT				0x0B6
#define KL1B_G_DECREMENT				0x0B7
#define KL1B_G_ABS					0x0B8
#define KL1B_G_MIN					0x0B9
#define KL1B_G_MAX					0x0BA
#define KL1B_G_AND					0x0BB
#define KL1B_G_OR					0x0BC
#define KL1B_G_EXCLUSIVE_OR				0x0BD
#define KL1B_G_COMPLEMENT				0x0BE
#define KL1B_G_SHIFT_LEFT				0x0BF
#define KL1B_G_SHIFT_RIGHT				0x0C0

/* Guard Builtin -- Vector */
#define KL1B_G_VECTOR					0x0C2
#define KL1B_G_VECTOR_ELEMENT				0x0C3
#define KL1B_MARK_ELEMENT				0x0C4

/* Guard Builtin -- String */
#define KL1B_G_STRING					0x0C6
#define KL1B_G_STRING_ELEMENT				0x0C7

/* Body Builtin -- Calculation */
#define KL1B_B_ADD					0x0C8
#define KL1B_B_SUBTRACT					0x0C9
#define KL1B_B_MULTIPLY					0x0CA
#define KL1B_B_DIVIDE					0x0CB
#define KL1B_B_MODULO					0x0CC
#define KL1B_B_MINUS					0x0CD
#define KL1B_B_INCREMENT				0x0CE
#define KL1B_B_DECREMENT				0x0CF
#define KL1B_B_ABS					0x0D0
#define KL1B_B_MIN					0x0D1
#define KL1B_B_MAX					0x0D2
#define KL1B_B_AND					0x0D3
#define KL1B_B_OR					0x0D4
#define KL1B_B_EXCLUSIVE_OR				0x0D5
#define KL1B_B_COMPLEMENT				0x0D6
#define KL1B_B_SHIFT_LEFT				0x0D7
#define KL1B_B_SHIFT_RIGHT				0x0D8

/* Body Builtin -- Vector */
#define KL1B_B_VECTOR					0x0DA
#define KL1B_B_NEW_VECTOR				0x0DB
#define KL1B_B_VECTOR_ELEMENT				0x0DC
#define KL1B_B_SET_VECTOR_ELEMENT			0x0DD
#define KL1B_B_SUBVECTOR				0x0DE /* NOT USED */
#define KL1B_B_SET_SUBVECTOR				0x0DF /* NOT USED */

/* Body Builtin -- String */
#define KL1B_B_STRING					0x0E0
#define KL1B_B_NEW_STRING				0x0E1
#define KL1B_B_STRING_ELEMENT				0x0E2
#define KL1B_B_SET_STRING_ELEMENT			0x0E3
#define KL1B_B_SUBSTRING				0x0E4
#define KL1B_B_SET_SUBSTRING				0x0E5
#define KL1B_B_APPEND_STRING				0x0E6

/* Body Builtin -- Atom */
#define KL1B_B_NEW_ATOM					0x0E8
#define KL1B_B_INTERN_ATOM				0x0E9
#define KL1B_B_ATOM_NAME				0x0EA
#define KL1B_B_ATOM_NUMBER				0x0EB

/* Body Builtin -- Code */
#define KL1B_B_PREDICATE_TO_CODE			0x0EE
#define KL1B_B_CODE_TO_PREDICATE			0x0EF

/* Guard Builtin -- Console */
#define KL1B_DISPLAY_CONSOLE				0x0F0
#define KL1B_PUT_CONSOLE				0x0F1
#define KL1B_READ_CONSOLE				0x0F2

/* Body Builtin -- Special */
#define KL1B_B_CURRENT_NODE				0x0F3
#define KL1B_B_APPLY					0x0F4
#define KL1B_B_RAISE					0x0F5
#define KL1B_B_MERGE					0x0F6
#define KL1B_B_CURRENT_PROCESSOR			0x0F7
#define KL1B_B_CURRENT_PRIORITY				0x0F8
#define KL1B_B_RATE					0x0F9
#define KL1B_B_RLTV					0x0FA
#define KL1B_B_HASH					0x0FB
#define KL1B_B_UNBOUND					0x0FC
#define KL1B_B_GET_PRINT_IMAGE				0x0FD
#define KL1B_B_UNBOUND2					0x0FE

/* Guard Builtin -- Floating Point */
#define KL1B_G_FLOAT_EQUAL				0x100
#define KL1B_G_FLOAT_NOT_EQUAL				0x101
#define KL1B_G_FLOAT_LESS_THAN				0x102
#define KL1B_G_FLOAT_NOT_LESS_THAN			0x103

/* Guard Builtin -- Floating Point */
#define KL1B_G_FLOAT_ADD				0x110
#define KL1B_G_FLOAT_SUBTRACT				0x111
#define KL1B_G_FLOAT_MULTIPLY				0x112
#define KL1B_G_FLOAT_DIVIDE				0x113
#define KL1B_G_FLOAT_MINUS				0x114
#define KL1B_G_FLOAT_ABS				0x115
#define KL1B_G_FLOAT_MIN				0x116
#define KL1B_G_FLOAT_MAX				0x117
#define KL1B_G_FLOAT_FLOOR				0x118
#define KL1B_G_FLOAT_SQRT				0x119
#define KL1B_G_FLOAT_LN					0x11A
#define KL1B_G_FLOAT_LOG				0x11B
#define KL1B_G_FLOAT_EXP				0x11C
#define KL1B_G_FLOAT_POW				0x11D
#define KL1B_G_FLOAT_SIN				0x11E
#define KL1B_G_FLOAT_COS				0x11F
#define KL1B_G_FLOAT_TAN				0x120
#define KL1B_G_FLOAT_ASIN				0x121
#define KL1B_G_FLOAT_ACOS				0x122
#define KL1B_G_FLOAT_ATAN				0x123
#define KL1B_G_FLOAT_ATAN2				0x124
#define KL1B_G_FLOAT_SINH				0x125
#define KL1B_G_FLOAT_COSH				0x126
#define KL1B_G_FLOAT_TANH				0x127

/* Guard Builtin -- Integer <-> Floating Point */
#define KL1B_G_FLOAT_TO_INTEGER				0x12E
#define KL1B_G_INTEGER_TO_FLOAT				0x12F

/* Guard Builtin -- Floating Point */
#define KL1B_B_FLOAT_ADD				0x130
#define KL1B_B_FLOAT_SUBTRACT				0x131
#define KL1B_B_FLOAT_MULTIPLY				0x132
#define KL1B_B_FLOAT_DIVIDE				0x133
#define KL1B_B_FLOAT_MINUS				0x134
#define KL1B_B_FLOAT_ABS				0x135
#define KL1B_B_FLOAT_MIN				0x136
#define KL1B_B_FLOAT_MAX				0x137
#define KL1B_B_FLOAT_FLOOR				0x138
#define KL1B_B_FLOAT_SQRT				0x139
#define KL1B_B_FLOAT_LN					0x13A
#define KL1B_B_FLOAT_LOG				0x13B
#define KL1B_B_FLOAT_EXP				0x13C
#define KL1B_B_FLOAT_POW				0x13D
#define KL1B_B_FLOAT_SIN				0x13E
#define KL1B_B_FLOAT_COS				0x13F
#define KL1B_B_FLOAT_TAN				0x140
#define KL1B_B_FLOAT_ASIN				0x141
#define KL1B_B_FLOAT_ACOS				0x142
#define KL1B_B_FLOAT_ATAN				0x143
#define KL1B_B_FLOAT_ATAN2				0x144
#define KL1B_B_FLOAT_SINH				0x145
#define KL1B_B_FLOAT_COSH				0x146
#define KL1B_B_FLOAT_TANH				0x147

/* Guard Builtin -- Integer <-> Floating Point */
#define KL1B_B_FLOAT_TO_INTEGER				0x14E
#define KL1B_B_INTEGER_TO_FLOAT				0x14F

/* Body Builtin -- Shoen */
#define KL1B_B_CREATE_SHOEN				0x170
#define KL1B_B_START_SHOEN				0x171
#define KL1B_B_STOP_SHOEN				0x172
#define KL1B_B_ABORT_SHOEN				0x173
#define KL1B_B_REMOVE_SHOEN				0x174
#define KL1B_B_SHOEN_STATISTICS				0x175
#define KL1B_B_SHOEN_ADD_RESOURCE			0x176
#define KL1B_B_CONSUME_RESOURCE				0x177

/* Body Builtin -- File, Window */
#define KL1B_B_CREATE_WINDOW				0x180
#define KL1B_B_REMOVE_WINDOW				0x181
#define KL1B_B_SHOW_WINDOW				0x182
#define KL1B_B_HIDE_WINDOW				0x183
#define KL1B_B_CREATE_FILE				0x184
#define KL1B_B_REMOVE_FILE				0x185
#define KL1B_B_OPEN_FILE				0x186
#define KL1B_B_CLOSE_FILE				0x187
#define KL1B_B_WRITE_CHAR				0x188
#define KL1B_B_WRITE_LINE				0x189
#define KL1B_B_WRITE_BUFFER				0x18A
#define KL1B_B_WRITE_TERM				0x18B
#define KL1B_B_READ_CHAR				0x18C
#define KL1B_B_READ_LINE				0x18D
#define KL1B_B_READ_BUFFER				0x18E
#define KL1B_B_READ_TOKEN				0x18F
#define KL1B_B_ABORT_READ_COMMAND			0x190

/* Body Builtin -- Directory */
#define KL1B_B_TEST_DIRECTORY				0x198
#define KL1B_B_DIRECTORY_PATHNAME			0x199
#define KL1B_B_LISTING_FILES				0x19A
#define KL1B_B_DELETE_FILES				0x19B

/* Body Builtin -- Timer */
#define KL1B_B_GET_TIME_COUNT				0x1A0
#define KL1B_B_ON_AT					0x1A1
#define KL1B_B_ON_AFTER					0x1A2

/* Body Builtin -- Code Module */
#define KL1B_B_SAVE_MODULE				0x1B0
#define KL1B_B_LOAD_MODULE				0x1B1
#define KL1B_B_ASSEMBLE_MODULE				0x1B2
#define KL1B_B_REMOVE_MODULE				0x1B3
#define KL1B_B_GET_PUBLIC_PREDICATES			0x1B4
#define KL1B_B_TRACE_MODULE				0x1B5
#define KL1B_B_GET_MODULE_STATUS			0x1B6
#define KL1B_B_SPY_PREDICATE				0x1B7
#define KL1B_B_GET_SPIED_PREDICATES			0x1B8
#define KL1B_B_RESET_PROFILE_INFO			0x1B9
#define KL1B_B_GET_PROFILE_INFO				0x1BA

/* Guard/Body Builtin -- Emulator Control, Debug */
#define KL1B_STATISTICS					0x1C0
#define KL1B_GET_CPU_TIME				0x1C1
#define KL1B_GET_CURRENT_TIME				0x1C2
#define KL1B_G_TAG_AND_VALUE				0x1C4
#define KL1B_G_REGISTER_TAG_AND_VALUE			0x1C5
#define KL1B_G_WORD					0x1C6
#define KL1B_G_SET_TAG_AND_VALUE			0x1C7
#define KL1B_G_HALT					0x1C8
#define KL1B_G_REQUEST_GC				0x1C9
#define KL1B_G_SET_SCHEDULING_SWITCH			0x1CA /* NOT USED */
#define KL1B_G_SET_TRACE_SWITCH				0x1CB
#define KL1B_G_SET_BACKTRACE_SWITCH			0x1CC
#define KL1B_G_DEVICE_DUP_CHECK				0x1CD
#define KL1B_B_GET_ALL_ATOM_NAME			0x1D0
#define KL1B_B_UNIX					0x1D1
#define KL1B_B_DEBUG_MONITOR_STREAM			0x1D2
#define KL1B_B_GET_LIBRARY_DIRECTORY			0x1D3

/* Body Builtin -- String II */
#define KL1B_B_STRING_AND				0x1E0
#define KL1B_B_STRING_OR				0x1E1
#define KL1B_B_STRING_EXCLUSIVE_OR			0x1E2
#define KL1B_B_STRING_COMPLEMENT			0x1E3

#define SPECIAL_FUNCTION_SHIFT				0x0FF /* for 2B OP */

#define KL1B_MODULE					0x1FC
#define KL1B_ENTRY					0x1FD
#define KL1B_MODULE_ENTRY				0x1FE
#define KL1B_PREDICATE					0x1FF

#define KL1B_BEGIN_CONST_SECTION			0x1F0
#define KL1B_DEFINE_ATOM				0x1F1
#define KL1B_DEFINE_INTEGER				0x1F2
#define KL1B_DEFINE_FLOAT				0x1F3
#define KL1B_DEFINE_DESC				0x1F4
#define KL1B_DEFINE_LIST				0x1F5
#define KL1B_DEFINE_VECTOR				0x1F6
#define KL1B_DEFINE_STRING				0x1F7


/************************************************************************/

#define INSTRUCTION_TABLE_SIZE 512

extern struct instr_rec{
    unsigned int opcode;
    int		 type;
    CHAR	 *mnem;
} instruction_table[];
extern unsigned int lookup_mnemonic(unsigned char *key, struct instr_rec **value);	/* instr.c (table.c) */

#define GetInstrType(OP)     instruction_table[OP].type
#define GetInstrMnemonic(OP) instruction_table[OP].mnem
