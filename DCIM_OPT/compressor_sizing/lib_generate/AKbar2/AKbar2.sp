* Xyce netlist for akbar2 - Template for Liberty Generation
* Approximate 4-2 Compressor (34 transistors)
* Function: S = (c XNOR d) NAND (a XNOR b), cout = (a AND b) OR (c AND d)
* CRITICAL: Python script will add actual voltage sources

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: akbar2 (34 transistors)
*************************************************************************

* instance : _3_ (XNOR2_X1): computes c XNOR d -> _1_
M__3__M_i_0 net__3__net_001 c net__3__net_000 VSS NMOS_VTL W=0.235u L=0.050u
M__3__M_i_5 VSS d net__3__net_001 VSS NMOS_VTL W=0.235u L=0.050u
M__3__M_i_11 net__3__net_002 net__3__net_000 VSS VSS NMOS_VTL W=0.325u L=0.050u
M__3__M_i_17 _1_ c net__3__net_002 VSS NMOS_VTL W=0.325u L=0.050u
M__3__M_i_23 net__3__net_002 d _1_ VSS NMOS_VTL W=0.325u L=0.050u
M__3__M_i_29 net__3__net_000 c VDD VDD PMOS_VTL W=0.145u L=0.050u
M__3__M_i_36 VDD d net__3__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M__3__M_i_42 _1_ net__3__net_000 VDD VDD PMOS_VTL W=0.145u L=0.050u
M__3__M_i_48 net__3__net_003 c _1_ VDD PMOS_VTL W=0.145u L=0.050u
M__3__M_i_53 VDD d net__3__net_003 VDD PMOS_VTL W=0.145u L=0.050u

* Instance _4_ (XNOR2_X1): computes a XNOR b -> _2_
M__4__M_i_0 net__4__net_001 a net__4__net_000 VSS NMOS_VTL W=0.235u L=0.050u
M__4__M_i_5 VSS b net__4__net_001 VSS NMOS_VTL W=0.235u L=0.050u
M__4__M_i_11 net__4__net_002 net__4__net_000 VSS VSS NMOS_VTL W=0.325u L=0.050u
M__4__M_i_17 _2_ a net__4__net_002 VSS NMOS_VTL W=0.325u L=0.050u
M__4__M_i_23 net__4__net_002 b _2_ VSS NMOS_VTL W=0.325u L=0.050u
M__4__M_i_29 net__4__net_000 a VDD VDD PMOS_VTL W=0.145u L=0.050u
M__4__M_i_36 VDD b net__4__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M__4__M_i_42 _2_ net__4__net_000 VDD VDD PMOS_VTL W=0.145u L=0.050u
M__4__M_i_48 net__4__net_003 a _2_ VDD PMOS_VTL W=0.145u L=0.050u
M__4__M_i_53 VDD b net__4__net_003 VDD PMOS_VTL W=0.145u L=0.050u

* Instance _5_ (NAND2_X1): computes S = _1_ NAND _2_
M__5__M_i_1 net__5__net_0 _2_ VSS VSS NMOS_VTL W=0.235u L=0.050u
M__5__M_i_0 S _1_ net__5__net_0 VSS NMOS_VTL W=0.235u L=0.050u
M__5__M_i_3 S _2_ VDD VDD PMOS_VTL W=1.495u L=0.050u
M__5__M_i_2 VDD _1_ S VDD PMOS_VTL W=1.495u L=0.050u

* Instance _6_ (AOI22_X1): computes _0_ = NOT((a AND b) OR (c AND d))
M__6__M_i_3 net__6__net_1 d VSS VSS NMOS_VTL W=0.145u L=0.050u
M__6__M_i_2 _0_ c net__6__net_1 VSS NMOS_VTL W=0.145u L=0.050u
M__6__M_i_0 net__6__net_0 a _0_ VSS NMOS_VTL W=0.145u L=0.050u
M__6__M_i_1 VSS b net__6__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__6__M_i_7 VDD d net__6__net_2 VDD PMOS_VTL W=0.145u L=0.050u
M__6__M_i_6 net__6__net_2 c VDD VDD PMOS_VTL W=0.145u L=0.050u
M__6__M_i_4 _0_ a net__6__net_2 VDD PMOS_VTL W=0.145u L=0.050u
M__6__M_i_5 net__6__net_2 b _0_ VDD PMOS_VTL W=0.145u L=0.050u

* Instance _7_ (INV_X1): computes cout = NOT(_0_)
M__7__M_i_0 cout _0_ VSS VSS NMOS_VTL W=0.145u L=0.050u
M__7__M_i_1 cout _0_ VDD VDD PMOS_VTL W=0.145u L=0.050u

* Parasitic capacitances
C_NET3_000 net__3__net_000 0 0.5f
C_NET3_001 net__3__net_001 0 0.5f
C_NET3_002 net__3__net_002 0 0.5f
C_NET3_003 net__3__net_003 0 1f
C_NET4_000 net__4__net_000 0 0.5f
C_NET4_001 net__4__net_001 0 0.5f
C_NET4_002 net__4__net_002 0 0.5f
C_NET4_003 net__4__net_003 0 1f
C_NET5_0 net__5__net_0 0 0.5f
C_NET6_0 net__6__net_0 0 0.5f
C_NET6_1 net__6__net_1 0 0.5f
C_NET6_2 net__6__net_2 0 1f
C_INT_0 _0_ 0 0.5f
C_INT_1 _1_ 0 0.5f
C_INT_2 _2_ 0 0.5f

* Initial conditions
.IC V(_0_)=__VDD_VAL__ V(_1_)=__VDD_50__ V(_2_)=__VDD_50__
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
C_VDD VDD 0 25p
C_VSS VSS 0 25p

*************************************************************************
* Analysis
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-3 ABSTOL=1e-6 METHOD=TRAP MINBREAK=1e-14
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS NONLIN-TRAN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=__TEMP_VAL__ GMIN=1e-15

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
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=2ns TO=__TSTOP__
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=5ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

*************************************************************************
* Output
*************************************************************************
.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END