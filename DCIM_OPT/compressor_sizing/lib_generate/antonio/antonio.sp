* Xyce netlist for antonio - Template for Liberty Generation
* Exact 4-2 Compressor (48 transistors)
* Function: S + 2*cout = a + b + c + d (Exact arithmetic)
* CRITICAL: Python script will add actual voltage sources
* FIXED: Output C renamed to cout (Xyce case-insensitive fix)

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: antonio (48 transistors)
*************************************************************************

* Instance _0_ (OR2_X1): w1 = a OR b
M__0__M_i_2 net__1__ZN_neg a VSS VSS NMOS_VTL W=0.145u L=0.050u
M__0__M_i_3 VSS b net__1__ZN_neg VSS NMOS_VTL W=0.145u L=0.050u
M__0__M_i_0 w1 net__1__ZN_neg VSS VSS NMOS_VTL W=0.145u L=0.050u
M__0__M_i_4 net__1__net_0 a net__1__ZN_neg VDD PMOS_VTL W=0.145u L=0.050u
M__0__M_i_5 VDD b net__1__net_0 VDD PMOS_VTL W=0.145u L=0.050u
M__0__M_i_1 w1 net__1__ZN_neg VDD VDD PMOS_VTL W=0.145u L=0.050u

* Instance _1_ (AOI21_X1): _0_ = NOT((a OR b) AND c)
M__1__M_i_1 net__2__net_0 a VSS VSS NMOS_VTL W=0.145u L=0.050u
M__1__M_i_0 _0_ b net__2__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__1__M_i_2 VSS c _0_ VSS NMOS_VTL W=0.145u L=0.050u
M__1__M_i_4 _0_ a net__2__net_1 VDD PMOS_VTL W=0.235u L=0.050u
M__1__M_i_3 net__2__net_1 b _0_ VDD PMOS_VTL W=0.235u L=0.050u
M__1__M_i_5 VDD c net__2__net_1 VDD PMOS_VTL W=0.235u L=0.050u

* Instance _2_ (INV_X1): w2 = NOT(_0_)
M__2__M_i_0 w2 _0_ VSS VSS NMOS_VTL W=0.145u L=0.050u
M__2__M_i_1 w2 _0_ VDD VDD PMOS_VTL W=0.145u L=0.050u

* ============================================
* Full Adder: (w1, w2, d) -> (S, cout)
* ============================================

* Instance _3_ (NAND2_X1): Full_adder__0_ = w1 NAND d
M_FA__3__M_i_1 net_FA__3__net_0 d VSS VSS NMOS_VTL W=0.145u L=0.050u
M_FA__3__M_i_0 Full_adder__0_ w1 net_FA__3__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__3__M_i_3 Full_adder__0_ d VDD VDD PMOS_VTL W=0.460u L=0.050u
M_FA__3__M_i_2 VDD w1 Full_adder__0_ VDD PMOS_VTL W=0.460u L=0.050u

* Instance _4_ (XNOR2_X1): Full_adder__1_ = w1 XNOR d
M_FA__4__M_i_0 net_FA__4__net_001 w1 net_FA__4__net_000 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_5 VSS d net_FA__4__net_001 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_11 net_FA__4__net_002 net_FA__4__net_000 VSS VSS NMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_17 Full_adder__1_ w1 net_FA__4__net_002 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_23 net_FA__4__net_002 d Full_adder__1_ VSS NMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_29 net_FA__4__net_000 w1 VDD VDD PMOS_VTL W=0.460u L=0.050u
M_FA__4__M_i_36 VDD d net_FA__4__net_000 VDD PMOS_VTL W=0.460u L=0.050u
M_FA__4__M_i_42 Full_adder__1_ net_FA__4__net_000 VDD VDD PMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_48 net_FA__4__net_003 w1 Full_adder__1_ VDD PMOS_VTL W=0.145u L=0.050u
M_FA__4__M_i_53 VDD d net_FA__4__net_003 VDD PMOS_VTL W=0.145u L=0.050u

* Instance _5_ (OAI21_X1): Full_adder__2_ = NOT((w1 OR d) AND w2)
M_FA__5__M_i_1 Full_adder__2_ w1 net_FA__5__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__5__M_i_0 net_FA__5__net_0 d Full_adder__2_ VSS NMOS_VTL W=0.145u L=0.050u
M_FA__5__M_i_2 VSS w2 net_FA__5__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__5__M_i_4 net_FA__5__net_1 w1 VDD VDD PMOS_VTL W=0.145u L=0.050u
M_FA__5__M_i_3 Full_adder__2_ d net_FA__5__net_1 VDD PMOS_VTL W=0.145u L=0.050u
M_FA__5__M_i_5 VDD w2 Full_adder__2_ VDD PMOS_VTL W=0.145u L=0.050u

* Instance _6_ (NAND2_X1): cout = Full_adder__0_ NAND Full_adder__2_
M_FA__6__M_i_1 net_FA__6__net_0 Full_adder__2_ VSS VSS NMOS_VTL W=0.145u L=0.050u
M_FA__6__M_i_0 cout Full_adder__0_ net_FA__6__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__6__M_i_3 cout Full_adder__2_ VDD VDD PMOS_VTL W=0.145u L=0.050u
M_FA__6__M_i_2 VDD Full_adder__0_ cout VDD PMOS_VTL W=0.145u L=0.050u

* Instance _7_ (XNOR2_X1): S = w2 XNOR Full_adder__1_
M_FA__7__M_i_0 net_FA__7__net_001 w2 net_FA__7__net_000 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_5 VSS Full_adder__1_ net_FA__7__net_001 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_11 net_FA__7__net_002 net_FA__7__net_000 VSS VSS NMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_17 S w2 net_FA__7__net_002 VSS NMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_23 net_FA__7__net_002 Full_adder__1_ S VSS NMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_29 net_FA__7__net_000 w2 VDD VDD PMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_36 VDD Full_adder__1_ net_FA__7__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M_FA__7__M_i_42 S net_FA__7__net_000 VDD VDD PMOS_VTL W=2.215u L=0.050u
M_FA__7__M_i_48 net_FA__7__net_003 w2 S VDD PMOS_VTL W=2.215u L=0.050u
M_FA__7__M_i_53 VDD Full_adder__1_ net_FA__7__net_003 VDD PMOS_VTL W=2.215u L=0.050u

* Parasitic capacitances
C_1_ZN net__1__ZN_neg 0 1f
C_1_0 net__1__net_0 0 1f
C_2_0 net__2__net_0 0 1f
C_2_1 net__2__net_1 0 1f
C_FA_3 net_FA__3__net_0 0 1f
C_FA_4_000 net_FA__4__net_000 0 1f
C_FA_4_001 net_FA__4__net_001 0 1f
C_FA_4_002 net_FA__4__net_002 0 1f
C_FA_4_003 net_FA__4__net_003 0 2f
C_FA_5_0 net_FA__5__net_0 0 1f
C_FA_5_1 net_FA__5__net_1 0 1f
C_FA_6_0 net_FA__6__net_0 0 1f
C_FA_7_000 net_FA__7__net_000 0 1f
C_FA_7_001 net_FA__7__net_001 0 1f
C_FA_7_002 net_FA__7__net_002 0 1f
C_FA_7_003 net_FA__7__net_003 0 2f
C_0 _0_ 0 1f
C_W1 w1 0 1f
C_W2 w2 0 1f
C_FA0 Full_adder__0_ 0 1f
C_FA1 Full_adder__1_ 0 1f
C_FA2 Full_adder__2_ 0 1f

* Initial conditions
.IC V(_0_)=__VDD_VAL__ V(w1)=0 V(w2)=0
.IC V(Full_adder__0_)=__VDD_VAL__ V(Full_adder__1_)=0 V(Full_adder__2_)=__VDD_VAL__
.IC V(S)=0 V(cout)=0

*************************************************************************
* Test Pattern - WILL BE REPLACED BY PYTHON
* Python script will insert actual voltage sources (Va, Vb, Vc, Vd)
*************************************************************************

* Input under test
* NOTE: This section will be COMPLETELY REPLACED by Python with actual sources

* Output loads
CLoad_S S 0 __OUTPUT_LOAD__
CLoad_cout cout 0 __OUTPUT_LOAD__

* Decoupling
C_VDD VDD 0 10p
C_VSS VSS 0 10p

*************************************************************************
* Analysis
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-5 ABSTOL=1e-9 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS NONLIN-TRAN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=__TEMP_VAL__

* Transient analysis
.TRAN __TSTEP__ __TSTOP__ 0 __TMAX__

*************************************************************************
* Measurements for Output: __OUTPUT_PIN__
*************************************************************************

* Reference timing - input 50% crossing
.MEASURE TRAN T_IN_50 WHEN V(__INPUT_PIN__)=__VDD_50__ CROSS=1

* === Output Timing Measurements ===
.MEASURE TRAN T___OUTPUT_PIN___50_R WHEN V(__OUTPUT_PIN__)=__VDD_50__ RISE=1
.MEASURE TRAN T___OUTPUT_PIN___50_F WHEN V(__OUTPUT_PIN__)=__VDD_50__ FALL=1
.MEASURE TRAN DELAY___OUTPUT_PIN___RISE PARAM='T___OUTPUT_PIN___50_R-T_IN_50' GOAL=0
.MEASURE TRAN DELAY___OUTPUT_PIN___FALL PARAM='T___OUTPUT_PIN___50_F-T_IN_50' GOAL=0

.MEASURE TRAN T___OUTPUT_PIN___10_R WHEN V(__OUTPUT_PIN__)=__VDD_10__ RISE=1
.MEASURE TRAN T___OUTPUT_PIN___90_R WHEN V(__OUTPUT_PIN__)=__VDD_90__ RISE=1
.MEASURE TRAN SLEW___OUTPUT_PIN___RISE PARAM='T___OUTPUT_PIN___90_R-T___OUTPUT_PIN___10_R' 

.MEASURE TRAN T___OUTPUT_PIN___90_F WHEN V(__OUTPUT_PIN__)=__VDD_90__ FALL=1
.MEASURE TRAN T___OUTPUT_PIN___10_F WHEN V(__OUTPUT_PIN__)=__VDD_10__ FALL=1
.MEASURE TRAN SLEW___OUTPUT_PIN___FALL PARAM='T___OUTPUT_PIN___10_F-T___OUTPUT_PIN___90_F' 

* === Power Measurements ===
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=5ns TO=__TSTOP__
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=8ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

*************************************************************************
* Output
*************************************************************************
.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END

