Since the same cell may have different NMOS/PMOS widths W, the dimensions corresponding to the specified width W are given as follows:
AKbar1: 10 dimensions
AKbar2: 10 dimensions
antonio: 16 dimensions
AP1: 16 dimensions
ha: 14 dimensions
kong2: 16 dimensions
momeni: 12 dimensions
sabetz: 4 dimensions

Standard PPA
	        area(µm²)	delay(ns)	power(µW)
AKbar1	    4.21	      0.992	        0.483
AKbar2	    5.49	      0.983	        0.673
antonio	    7.69	         1	        1.008
AP1	        9.51	      0.941	        1.137
ha	        6.22	      0.948	        0.797
kong2	    7.69	      0.921	        0.917
momeni	    4.21	      1.031	        0.512
sabetz	    2.56	      0.935	        0.249

IO-definition

Type	Input	        Output   Range of Widths  Step
AKbar1	XNOR2_X1_NMOS1	Delay	   2.7~0.145	  0.045
		XNOR2_X1_NMOS2	Power		
		XNOR2_X1_PMOS1	Area		
		XNOR2_X1_PMOS2			
		NAND2_X1_NMOS1			
		NAND2_X1_PMOS1			
		BUF_X1_NMOS1			
		BUF_X1_NMOS2			
		BUF_X1_PMOS1			
		BUF_X1_PMOS2			
				
AKbar2	XNOR2_X1_NMOS1	Delay	   2.7~0.145	  0.045
		XNOR2_X1_NMOS2	Power		
		XNOR2_X1_PMOS1	Area		
		XNOR2_X1_PMOS2			
		NAND2_X1_NMOS1			
		NAND2_X1_PMOS1			
		AOI22_X1_NMOS1			
		AOI22_X1_PMOS1			
		INV_X1_NMOS1			
		INV_X1_PMOS1			
				
antonio	OR2_X1_NMOS1	Delay	   2.7~0.145	  0.045
		OR2_X1_NMOS2	Power		
		OR2_X1_PMOS1	Area		
		OR2_X1_PMOS2			
		AOI22_X1_NMOS1			
		AOI22_X1_PMOS1			
		INV_X1_NMOS1			
		INV_X1_PMOS1			
		NAND2_X1_NMOS1			
		NAND2_X1_PMOS1			
		XNOR2_X1_NMOS1			
		XNOR2_X1_NMOS2			
		XNOR2_X1_PMOS1			
		XNOR2_X1_PMOS2			
		OAI21_X1_NMOS1			
		OAI21_X1_PMOS1			
				
AP1	    OAI22_X1_NMOS1	Delay	   2.7~0.145	  0.045
		OAI22_X1_PMOS1	Power		
		NAND2_X1_NMOS1	Area		
		NAND2_X1_PMOS1			
		NAND3_X1_NMOS1			
		NAND3_X1_PMOS1			
		XOR2_X1_NMOS1			
		XOR2_X1_NMOS2			
		XOR2_X1_PMOS1			
		XOR2_X1_PMOS2			
		XNOR2_X1_NMOS1			
		XNOR2_X1_NMOS2			
		XNOR2_X1_PMOS1			
		XNOR2_X1_PMOS2			
		OAI21_X1_NMOS1			
		OAI21_X1_PMOS1			
				
ha	    NOR2_X1_NMOS1	Delay	   2.7~0.145	  0.045
		NOR2_X1_PMOS1	Power		
		NAND2_X1_NMOS1	Area		
		NAND2_X1_PMOS1			
		XOR2_X1_NMOS1			
		XOR2_X1_NMOS2			
		XOR2_X1_PMOS1			
		XOR2_X1_PMOS2			
		XNOR2_X1_NMOS1			
		XNOR2_X1_NMOS2			
		XNOR2_X1_PMOS1			
		XNOR2_X1_PMOS2			
		OAI21_X1_NMOS1			
		OAI21_X1_PMOS1			
				
kong2	OAI22_X1_NMOS1	Delay	   2.7~0.145	   0.045
		OAI22_X1_PMOS1	Power		
		INV_X1_NMOS1	Area		
		INV_X1_PMOS1			
		AOI22_X1_NMOS1			
		AOI22_X1_PMOS1			
		NAND2_X1_NMOS1			
		NAND2_X1_PMOS1			
		XOR2_X1_NMOS1			
		XOR2_X1_NMOS2			
		XOR2_X1_PMOS1			
		XOR2_X1_PMOS2			
		NOR3_X1_NMOS1			
		NOR3_X1_PMOS1			
		AOI21_X1_NMOS1			
		AOI21_X1_PMOS1			
				
momeni	OAI22_X1_NMOS1	Delay	   2.7~0.145	   0.045
		OAI22_X1_PMOS1	Power		
		INV_X1_NMOS1	Area		
		INV_X1_PMOS1			
		AND2_X1_NMOS1			
		AND2_X1_NMOS2			
		AND2_X1_PMOS1			
		AND2_X1_PMOS2			
		OR3_X1_NMOS1			
		OR3_X1_NMOS2			
		OR3_X1_PMOS1			
		OR3_X1_PMOS2			
				
sabetz	NAND2_X1_NMOS1	Delay	   2.7~0.145	   0.045
		NAND2_X1_PMOS1	Power		
		OAI21_X1_NMOS1	Area		
		OAI21_X1_PMOS1			
