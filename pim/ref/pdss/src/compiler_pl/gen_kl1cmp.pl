%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

go_comp_pdss :- compile([top2, read, write2, norm3, comp2, 
	             mrb4, reg, index2, pdss_blt, aux2,
                     pdss_sys, macro2, convert, code_opt2, libdir]).

go_consult_pdss :- [top2, read, write2, norm3, comp2, 
	       mrb4, reg, index2, pdss_blt, aux2,
               pdss_sys, macro2, convert, code_opt2, libdir].
