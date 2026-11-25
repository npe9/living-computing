mpimos_opcode_table:
	module		mpimos_opcode_table
	entry		op,2,op_2_0
	module_entry		mpimos_opcode_table
	predicate		op,2
op_2_0:
	try_me_else		op_2_1
	integer		1
	hash_on_integer		1,123,op_2_1
	bucket_entry_i		200,op_2_3
	bucket_entry_i		201,op_2_4
	bucket_entry_i		202,op_2_5
	bucket_entry_i		203,op_2_6
	bucket_entry_i		204,op_2_7
	bucket_entry_i		205,op_2_8
	bucket_entry_i		206,op_2_9
	bucket_entry_i		207,op_2_10
	bucket_entry_i		208,op_2_11
	bucket_entry_i		209,op_2_12
	bucket_entry_i		210,op_2_13
	bucket_entry_i		211,op_2_14
	bucket_entry_i		212,op_2_15
	bucket_entry_i		213,op_2_16
	bucket_entry_i		214,op_2_17
	bucket_entry_i		215,op_2_18
	bucket_entry_i		216,op_2_19
	bucket_entry_i		218,op_2_20
	bucket_entry_i		219,op_2_21
	bucket_entry_i		220,op_2_22
	bucket_entry_i		221,op_2_23
	bucket_entry_i		224,op_2_24
	bucket_entry_i		225,op_2_25
	bucket_entry_i		226,op_2_26
	bucket_entry_i		227,op_2_27
	bucket_entry_i		228,op_2_28
	bucket_entry_i		229,op_2_29
	bucket_entry_i		230,op_2_30
	bucket_entry_i		232,op_2_31
	bucket_entry_i		233,op_2_32
	bucket_entry_i		234,op_2_33
	bucket_entry_i		235,op_2_34
	bucket_entry_i		238,op_2_35
	bucket_entry_i		239,op_2_36
	bucket_entry_i		243,op_2_37
	bucket_entry_i		244,op_2_38
	bucket_entry_i		245,op_2_39
	bucket_entry_i		246,op_2_40
	bucket_entry_i		247,op_2_41
	bucket_entry_i		248,op_2_42
	bucket_entry_i		249,op_2_43
	bucket_entry_i		250,op_2_44
	bucket_entry_i		251,op_2_45
	bucket_entry_i		252,op_2_46
	bucket_entry_i		253,op_2_47
	bucket_entry_i		254,op_2_48
	bucket_entry_i		304,op_2_49
	bucket_entry_i		305,op_2_50
	bucket_entry_i		306,op_2_51
	bucket_entry_i		307,op_2_52
	bucket_entry_i		308,op_2_53
	bucket_entry_i		309,op_2_54
	bucket_entry_i		310,op_2_55
	bucket_entry_i		311,op_2_56
	bucket_entry_i		312,op_2_57
	bucket_entry_i		313,op_2_58
	bucket_entry_i		314,op_2_59
	bucket_entry_i		315,op_2_60
	bucket_entry_i		316,op_2_61
	bucket_entry_i		317,op_2_62
	bucket_entry_i		318,op_2_63
	bucket_entry_i		319,op_2_64
	bucket_entry_i		320,op_2_65
	bucket_entry_i		321,op_2_66
	bucket_entry_i		322,op_2_67
	bucket_entry_i		323,op_2_68
	bucket_entry_i		324,op_2_69
	bucket_entry_i		325,op_2_70
	bucket_entry_i		326,op_2_71
	bucket_entry_i		327,op_2_72
	bucket_entry_i		334,op_2_73
	bucket_entry_i		335,op_2_74
	bucket_entry_i		368,op_2_75
	bucket_entry_i		369,op_2_76
	bucket_entry_i		370,op_2_77
	bucket_entry_i		371,op_2_78
	bucket_entry_i		372,op_2_79
	bucket_entry_i		373,op_2_80
	bucket_entry_i		374,op_2_81
	bucket_entry_i		375,op_2_82
	bucket_entry_i		384,op_2_83
	bucket_entry_i		385,op_2_84
	bucket_entry_i		386,op_2_85
	bucket_entry_i		387,op_2_86
	bucket_entry_i		388,op_2_87
	bucket_entry_i		389,op_2_88
	bucket_entry_i		390,op_2_89
	bucket_entry_i		391,op_2_90
	bucket_entry_i		392,op_2_91
	bucket_entry_i		393,op_2_92
	bucket_entry_i		394,op_2_93
	bucket_entry_i		395,op_2_94
	bucket_entry_i		396,op_2_95
	bucket_entry_i		397,op_2_96
	bucket_entry_i		398,op_2_97
	bucket_entry_i		399,op_2_98
	bucket_entry_i		400,op_2_99
	bucket_entry_i		408,op_2_100
	bucket_entry_i		409,op_2_101
	bucket_entry_i		410,op_2_102
	bucket_entry_i		411,op_2_103
	bucket_entry_i		416,op_2_104
	bucket_entry_i		417,op_2_105
	bucket_entry_i		418,op_2_106
	bucket_entry_i		432,op_2_107
	bucket_entry_i		433,op_2_108
	bucket_entry_i		434,op_2_109
	bucket_entry_i		435,op_2_110
	bucket_entry_i		436,op_2_111
	bucket_entry_i		437,op_2_112
	bucket_entry_i		438,op_2_113
	bucket_entry_i		439,op_2_114
	bucket_entry_i		440,op_2_115
	bucket_entry_i		441,op_2_116
	bucket_entry_i		442,op_2_117
	bucket_entry_i		464,op_2_118
	bucket_entry_i		465,op_2_119
	bucket_entry_i		466,op_2_120
	bucket_entry_i		467,op_2_121
	bucket_entry_i		480,op_2_122
	bucket_entry_i		481,op_2_123
	bucket_entry_i		482,op_2_124
	bucket_entry_i		483,op_2_125
op_2_3:
	get_atom		2,add
	proceed
op_2_4:
	get_atom		2,subtract
	proceed
op_2_5:
	get_atom		2,multiply
	proceed
op_2_6:
	get_atom		2,divide
	proceed
op_2_7:
	get_atom		2,modulo
	proceed
op_2_8:
	get_atom		2,minus
	proceed
op_2_9:
	get_atom		2,increment
	proceed
op_2_10:
	get_atom		2,decrement
	proceed
op_2_11:
	get_atom		2,abs
	proceed
op_2_12:
	get_atom		2,min
	proceed
op_2_13:
	get_atom		2,max
	proceed
op_2_14:
	get_atom		2,and
	proceed
op_2_15:
	get_atom		2,or
	proceed
op_2_16:
	get_atom		2,exclusive_or
	proceed
op_2_17:
	get_atom		2,complement
	proceed
op_2_18:
	get_atom		2,shift_left
	proceed
op_2_19:
	get_atom		2,shift_right
	proceed
op_2_20:
	get_atom		2,vector
	proceed
op_2_21:
	get_atom		2,new_vector
	proceed
op_2_22:
	get_atom		2,vector_element
	proceed
op_2_23:
	get_atom		2,set_vector_element
	proceed
op_2_24:
	get_atom		2,string
	proceed
op_2_25:
	get_atom		2,new_string
	proceed
op_2_26:
	get_atom		2,string_element
	proceed
op_2_27:
	get_atom		2,set_string_element
	proceed
op_2_28:
	get_atom		2,substring
	proceed
op_2_29:
	get_atom		2,set_substring
	proceed
op_2_30:
	get_atom		2,append_string
	proceed
op_2_31:
	get_atom		2,new_atom
	proceed
op_2_32:
	get_atom		2,intern_atom
	proceed
op_2_33:
	get_atom		2,atom_name
	proceed
op_2_34:
	get_atom		2,atom_number
	proceed
op_2_35:
	get_atom		2,predicate_to_code
	proceed
op_2_36:
	get_atom		2,code_to_predicate
	proceed
op_2_37:
	get_atom		2,current_node
	proceed
op_2_38:
	get_atom		2,apply
	proceed
op_2_39:
	get_atom		2,raise
	proceed
op_2_40:
	get_atom		2,merge
	proceed
op_2_41:
	get_atom		2,current_processor
	proceed
op_2_42:
	get_atom		2,current_priority
	proceed
op_2_43:
	get_atom		2,b_rate
	proceed
op_2_44:
	get_atom		2,b_rltv
	proceed
op_2_45:
	get_atom		2,hash
	proceed
op_2_46:
	get_atom		2,unbound
	proceed
op_2_47:
	get_atom		2,get_print_image
	proceed
op_2_48:
	get_atom		2,unbound
	proceed
op_2_49:
	get_atom		2,floating_point_add
	proceed
op_2_50:
	get_atom		2,floating_point_subtract
	proceed
op_2_51:
	get_atom		2,floating_point_multiply
	proceed
op_2_52:
	get_atom		2,floating_point_divide
	proceed
op_2_53:
	get_atom		2,floating_point_minus
	proceed
op_2_54:
	get_atom		2,floating_point_abs
	proceed
op_2_55:
	get_atom		2,floating_point_min
	proceed
op_2_56:
	get_atom		2,floating_point_max
	proceed
op_2_57:
	get_atom		2,floating_point_floor
	proceed
op_2_58:
	get_atom		2,floating_point_sqrt
	proceed
op_2_59:
	get_atom		2,floating_point_ln
	proceed
op_2_60:
	get_atom		2,floating_point_log
	proceed
op_2_61:
	get_atom		2,floating_point_exp
	proceed
op_2_62:
	get_atom		2,floating_point_pow
	proceed
op_2_63:
	get_atom		2,floating_point_sin
	proceed
op_2_64:
	get_atom		2,floating_point_cos
	proceed
op_2_65:
	get_atom		2,floating_point_tan
	proceed
op_2_66:
	get_atom		2,floating_point_asin
	proceed
op_2_67:
	get_atom		2,floating_point_acos
	proceed
op_2_68:
	get_atom		2,floating_point_atan
	proceed
op_2_69:
	get_atom		2,floating_point_atan
	proceed
op_2_70:
	get_atom		2,floating_point_sinh
	proceed
op_2_71:
	get_atom		2,floating_point_cosh
	proceed
op_2_72:
	get_atom		2,floating_point_tanh
	proceed
op_2_73:
	get_atom		2,floating_point_to_integer
	proceed
op_2_74:
	get_atom		2,integer_to_floating_point
	proceed
op_2_75:
	get_atom		2,create_shoen
	proceed
op_2_76:
	get_atom		2,start_shoen
	proceed
op_2_77:
	get_atom		2,stop_shoen
	proceed
op_2_78:
	get_atom		2,abort_shoen
	proceed
op_2_79:
	get_atom		2,remove_shoen
	proceed
op_2_80:
	get_atom		2,shoen_statistics
	proceed
op_2_81:
	get_atom		2,shoen_add_resource
	proceed
op_2_82:
	get_atom		2,consume_resource
	proceed
op_2_83:
	get_atom		2,create_window
	proceed
op_2_84:
	get_atom		2,remove_window
	proceed
op_2_85:
	get_atom		2,show_window
	proceed
op_2_86:
	get_atom		2,hide_window
	proceed
op_2_87:
	get_atom		2,create_file
	proceed
op_2_88:
	get_atom		2,remove_file
	proceed
op_2_89:
	get_atom		2,open_file
	proceed
op_2_90:
	get_atom		2,close_file
	proceed
op_2_91:
	get_atom		2,write_char
	proceed
op_2_92:
	get_atom		2,write_line
	proceed
op_2_93:
	get_atom		2,write_buffer
	proceed
op_2_94:
	get_atom		2,write_term
	proceed
op_2_95:
	get_atom		2,read_char
	proceed
op_2_96:
	get_atom		2,read_line
	proceed
op_2_97:
	get_atom		2,read_buffer
	proceed
op_2_98:
	get_atom		2,read_token
	proceed
op_2_99:
	get_atom		2,abort_read_command
	proceed
op_2_100:
	get_atom		2,test_directory
	proceed
op_2_101:
	get_atom		2,directory_pathname
	proceed
op_2_102:
	get_atom		2,listing_files
	proceed
op_2_103:
	get_atom		2,delete_files
	proceed
op_2_104:
	get_atom		2,get_time_count
	proceed
op_2_105:
	get_atom		2,on_at
	proceed
op_2_106:
	get_atom		2,on_after
	proceed
op_2_107:
	get_atom		2,save_module
	proceed
op_2_108:
	get_atom		2,load_module
	proceed
op_2_109:
	get_atom		2,assemble_module
	proceed
op_2_110:
	get_atom		2,remove_module
	proceed
op_2_111:
	get_atom		2,get_public_predicates
	proceed
op_2_112:
	get_atom		2,trace_module
	proceed
op_2_113:
	get_atom		2,get_module_status
	proceed
op_2_114:
	get_atom		2,spy_predicate
	proceed
op_2_115:
	get_atom		2,get_spied_predicates
	proceed
op_2_116:
	get_atom		2,reset_profile_info
	proceed
op_2_117:
	get_atom		2,get_profile_info
	proceed
op_2_118:
	get_atom		2,get_all_atom_name
	proceed
op_2_119:
	get_atom		2,unix
	proceed
op_2_120:
	get_atom		2,debug_monitor_stream
	proceed
op_2_121:
	get_atom		2,get_library_directory
	proceed
op_2_122:
	get_atom		2,string_and
	proceed
op_2_123:
	get_atom		2,string_or
	proceed
op_2_124:
	get_atom		2,string_exclusive_or
	proceed
op_2_125:
	get_atom		2,string_complement
	proceed
op_2_1:
	otherwise		op_2_0
	collect_value		1
	get_atom		2,'??Unknown??'
	proceed
op_2_128:
	suspend		op_2_0
