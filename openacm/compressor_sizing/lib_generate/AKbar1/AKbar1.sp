* Xyce netlist for akbar1 - Template for Liberty Generation
* Approximate 4-2 Compressor (24 transistors + buffer)
* Function: S = (a XNOR b) NAND (c XNOR d), cout = d
* CRITICAL: Python script will add actual voltage sources

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: akbar1
*************************************************************************

* Instance _2_ (XNOR2_X1): computes a XNOR b -> _0_
M__2__M_i_0 net__2__net_001 a net__2__net_000 VSS NMOS_VTL W=0.190u L=0.050u
M__2__M_i_5 VSS b net__2__net_001 VSS NMOS_VTL W=0.190u L=0.050u
M__2__M_i_11 net__2__net_002 net__2__net_000 VSS VSS NMOS_VTL W=2.215u L=0.050u
M__2__M_i_17 _0_ a net__2__net_002 VSS NMOS_VTL W=2.215u L=0.050u
M__2__M_i_23 net__2__net_002 b _0_ VSS NMOS_VTL W=2.215u L=0.050u
M__2__M_i_29 net__2__net_000 a VDD VDD PMOS_VTL W=1.945u L=0.050u
M__2__M_i_36 VDD b net__2__net_000 VDD PMOS_VTL W=1.945u L=0.050u
M__2__M_i_42 _0_ net__2__net_000 VDD VDD PMOS_VTL W=0.685u L=0.050u
M__2__M_i_48 net__2__net_003 a _0_ VDD PMOS_VTL W=0.685u L=0.050u
M__2__M_i_53 VDD b net__2__net_003 VDD PMOS_VTL W=0.685u L=0.050u

* Instance _3_ (XNOR2_X1): computes c XNOR d -> _1_
M__3__M_i_0 net__3__net_001 c net__3__net_000 VSS NMOS_VTL W=0.190u L=0.050u
M__3__M_i_5 VSS d net__3__net_001 VSS NMOS_VTL W=0.190u L=0.050u
M__3__M_i_11 net__3__net_002 net__3__net_000 VSS VSS NMOS_VTL W=2.215u L=0.050u
M__3__M_i_17 _1_ c net__3__net_002 VSS NMOS_VTL W=2.215u L=0.050u
M__3__M_i_23 net__3__net_002 d _1_ VSS NMOS_VTL W=2.215u L=0.050u
M__3__M_i_29 net__3__net_000 c VDD VDD PMOS_VTL W=1.945u L=0.050u
M__3__M_i_36 VDD d net__3__net_000 VDD PMOS_VTL W=1.945u L=0.050u
M__3__M_i_42 _1_ net__3__net_000 VDD VDD PMOS_VTL W=0.685u L=0.050u
M__3__M_i_48 net__3__net_003 c _1_ VDD PMOS_VTL W=0.685u L=0.050u
M__3__M_i_53 VDD d net__3__net_003 VDD PMOS_VTL W=0.685u L=0.050u

* Instance _4_ (NAND2_X1): computes S = _0_ NAND _1_
M__4__M_i_1 net__4__net_0 _1_ VSS VSS NMOS_VTL W=2.260u L=0.050u
M__4__M_i_0 S _0_ net__4__net_0 VSS NMOS_VTL W=2.260u L=0.050u
M__4__M_i_3 S _1_ VDD VDD PMOS_VTL W=1.135u L=0.050u
M__4__M_i_2 VDD _0_ S VDD PMOS_VTL W=1.135u L=0.050u

* Instance _5_ (BUF_X1)
*XBUF_CARRY d cout VDD VSS BUF_X1
M__5__M_i_2 VSS d cout_neg VSS NMOS_VTL W=0.235u L=0.050u
M__5__M_i_0 cout cout_neg VSS VSS NMOS_VTL W=1.675u L=0.050u
M__5__M_i_3 VDD d cout_neg VDD PMOS_VTL W=1.315u L=0.050u
M__5__M_i_1 cout cout_neg VDD VDD PMOS_VTL W=0.235u L=0.050u

* Parasitic capacitances
C_NET2_000 net__2__net_000 0 0.5f
C_NET2_001 net__2__net_001 0 0.5f
C_NET2_002 net__2__net_002 0 0.5f
C_NET2_003 net__2__net_003 0 1f
C_NET3_000 net__3__net_000 0 0.5f
C_NET3_001 net__3__net_001 0 0.5f
C_NET3_002 net__3__net_002 0 0.5f
C_NET3_003 net__3__net_003 0 1f
C_NET4_0 net__4__net_0 0 0.5f
C_NET4_COUT_NEG cout_neg 0 0.5f
C_INT_0 _0_ 0 0.5f
C_INT_1 _1_ 0 0.5f

* Initial conditions
.IC V(_0_)=__VDD_50__ V(_1_)=__VDD_50__
.IC V(S)=0 V(cout)=__VDD_VAL__

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
C_VDD VDD 0 20p
C_VSS VSS 0 20p

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
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=0ns TO=__TSTOP__
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=9ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

*************************************************************************
* Output
*************************************************************************
.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END

