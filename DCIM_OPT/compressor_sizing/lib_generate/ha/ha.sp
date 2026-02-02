* Xyce netlist for ha - Approximate 4-2 Compressor
* Template for Liberty characterization

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: ha (38 transistors)
*************************************************************************

* Instance _04_ (NOR2_X1): computes _1_ = c NOR d
M__04__M_i_1 _1_ d VSS VSS NMOS_VTL W=1.135u L=0.050u
M__04__M_i_0 VSS c _1_ VSS NMOS_VTL W=1.135u L=0.050u
M__04__M_i_3 net__4__net_0 d VDD VDD PMOS_VTL W=0.190u L=0.050u
M__04__M_i_2 _1_ c net__4__net_0 VDD PMOS_VTL W=0.190u L=0.050u

* Instance _05_ (NAND2_X1): computes _2_ = a NAND b
M__05__M_i_1 net__5__net_0 b VSS VSS NMOS_VTL W=0.145u L=0.050u
M__05__M_i_0 _2_ a net__5__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__05__M_i_3 _2_ b VDD VDD PMOS_VTL W=1.810u L=0.050u
M__05__M_i_2 VDD a _2_ VDD PMOS_VTL W=1.810u L=0.050u

* Instance _06_ (NOR2_X1): computes _3_ = a NOR b
M__06__M_i_1 _3_ b VSS VSS NMOS_VTL W=1.135u L=0.050u
M__06__M_i_0 VSS a _3_ VSS NMOS_VTL W=1.135u L=0.050u
M__06__M_i_3 net__6__net_0 b VDD VDD PMOS_VTL W=0.190u L=0.050u
M__06__M_i_2 _3_ a net__6__net_0 VDD PMOS_VTL W=0.190u L=0.050u

* Instance _07_ (XOR2_X1): computes _0_ = a XOR b
M__07__M_i_0 net__7__net_000 a VSS VSS NMOS_VTL W=1.090u L=0.050u
M__07__M_i_7 VSS b net__7__net_000 VSS NMOS_VTL W=1.090u L=0.050u
M__07__M_i_13 _0_ net__7__net_000 VSS VSS NMOS_VTL W=0.145u L=0.050u
M__07__M_i_19 net__7__net_001 a _0_ VSS NMOS_VTL W=0.145u L=0.050u
M__07__M_i_24 VSS b net__7__net_001 VSS NMOS_VTL W=0.145u L=0.050u
M__07__M_i_30 net__7__net_002 a net__7__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M__07__M_i_35 VDD b net__7__net_002 VDD PMOS_VTL W=0.145u L=0.050u
M__07__M_i_41 net__7__net_003 net__7__net_000 VDD VDD PMOS_VTL W=0.235u L=0.050u
M__07__M_i_47 _0_ a net__7__net_003 VDD PMOS_VTL W=0.235u L=0.050u
M__07__M_i_53 net__7__net_003 b _0_ VDD PMOS_VTL W=0.235u L=0.050u

* Instance _08_ (XNOR2_X1): computes S = _1_ XNOR _0_
M__08__M_i_0 net__8__net_001 _1_ net__8__net_000 VSS NMOS_VTL W=0.235u L=0.050u
M__08__M_i_5 VSS _0_ net__8__net_001 VSS NMOS_VTL W=0.235u L=0.050u
M__08__M_i_11 net__8__net_002 net__8__net_000 VSS VSS NMOS_VTL W=0.325u L=0.050u
M__08__M_i_17 S _1_ net__8__net_002 VSS NMOS_VTL W=0.325u L=0.050u
M__08__M_i_23 net__8__net_002 _0_ S VSS NMOS_VTL W=00.325u L=0.050u
M__08__M_i_29 net__8__net_000 _1_ VDD VDD PMOS_VTL W=0.370u L=0.050u
M__08__M_i_36 VDD _0_ net__8__net_000 VDD PMOS_VTL W=0.370u L=0.050u
M__08__M_i_42 S net__8__net_000 VDD VDD PMOS_VTL W=0.235u L=0.050u
M__08__M_i_48 net__8__net_003 _1_ S VDD PMOS_VTL W=0.235u L=0.050u
M__08__M_i_53 VDD _0_ net__8__net_003 VDD PMOS_VTL W=0.235u L=0.050u

* Instance _09_ (OAI21_X1): computes cout = NOT((_1_ AND _3_) OR _2_)
M__09__M_i_1 cout _1_ net__9__net_0 VSS NMOS_VTL W=0.370u L=0.050u
M__09__M_i_0 net__9__net_0 _3_ cout VSS NMOS_VTL W=0.370u L=0.050u
M__09__M_i_2 VSS _2_ net__9__net_0 VSS NMOS_VTL W=0.370u L=0.050u
M__09__M_i_4 net__9__net_1 _1_ VDD VDD PMOS_VTL W=0.280u L=0.050u
M__09__M_i_3 cout _3_ net__9__net_1 VDD PMOS_VTL W=0.280u L=0.050u
M__09__M_i_5 VDD _2_ cout VDD PMOS_VTL W=0.280u L=0.050u

* Parasitic capacitances
C_NET4_0 net__4__net_0 0 0.5f
C_NET5_0 net__5__net_0 0 0.5f
C_NET6_0 net__6__net_0 0 0.5f
C_NET7_000 net__7__net_000 0 0.5f
C_NET7_001 net__7__net_001 0 0.5f
C_NET7_002 net__7__net_002 0 1f
C_NET7_003 net__7__net_003 0 1f
C_NET8_000 net__8__net_000 0 0.5f
C_NET8_001 net__8__net_001 0 0.5f
C_NET8_002 net__8__net_002 0 0.5f
C_NET8_003 net__8__net_003 0 2f
C_NET9_0 net__9__net_0 0 0.5f
C_NET9_1 net__9__net_1 0 1f
C_INT_0 _0_ 0 0.5f
C_INT_1 _1_ 0 0.5f
C_INT_2 _2_ 0 0.5f
C_INT_3 _3_ 0 0.5f

* Initial conditions
.IC V(_0_)=__VDD_50__ V(_1_)=__VDD_50__ V(_2_)=__VDD_50__
.IC V(_3_)=__VDD_50__ V(S)=0 V(cout)=__VDD_VAL__

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
C_VDD VDD 0 25p

*************************************************************************
* Analysis
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-4 ABSTOL=1e-9 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0
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
.MEASURE TRAN SLEW___OUTPUT_PIN___RISE PARAM='T___OUTPUT_PIN___90_R-T___OUTPUT_PIN___10_R' GOAL=0

.MEASURE TRAN T___OUTPUT_PIN___90_F WHEN V(__OUTPUT_PIN__)=__VDD_90__ FALL=1
.MEASURE TRAN T___OUTPUT_PIN___10_F WHEN V(__OUTPUT_PIN__)=__VDD_10__ FALL=1
.MEASURE TRAN SLEW___OUTPUT_PIN___FALL PARAM='T___OUTPUT_PIN___10_F-T___OUTPUT_PIN___90_F' GOAL=0

* === Power Measurements ===
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=0ns TO=__TSTOP__
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=7ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

*************************************************************************
* Output
*************************************************************************
.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END