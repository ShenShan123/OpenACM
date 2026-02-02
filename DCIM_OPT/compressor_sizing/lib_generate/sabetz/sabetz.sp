* Xyce netlist for sabetz - Approximate 4-2 Compressor
* Template for Liberty characterization
* Note: S output is constant (1.2V)

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: sabetz (14 transistors)
*************************************************************************

* Constant assignment: S = 1 (always high)
VS S 0 DC __VDD_VAL__

* Instance _2_ (NAND2_X1): computes a NAND d -> _0_
M__2__M_i_1 net__2__net_0 d VSS VSS NMOS_VTL W=1.270u L=0.050u
M__2__M_i_0 _0_ a net__2__net_0 VSS NMOS_VTL W=1.270u L=0.050u
M__2__M_i_3 _0_ d VDD VDD PMOS_VTL W=0.325u L=0.050u
M__2__M_i_2 VDD a _0_ VDD PMOS_VTL W=0.325u L=0.050u

* Instance _3_ (OAI21_X1): computes (a+d)*!c -> _1_
* Logic: _1_ = !((a OR d) AND c) = (a+d)*!c
M__3__M_i_1 _1_ a net__3__net_0 VSS NMOS_VTL W=1.630u L=0.050u
M__3__M_i_0 net__3__net_0 d _1_ VSS NMOS_VTL W=1.630u L=0.050u
M__3__M_i_2 VSS c net__3__net_0 VSS NMOS_VTL W=1.630u L=0.050u
M__3__M_i_4 net__3__net_1 a VDD VDD PMOS_VTL W=1.090u L=0.050u
M__3__M_i_3 _1_ d net__3__net_1 VDD PMOS_VTL W=1.09u L=0.050u
M__3__M_i_5 VDD c _1_ VDD PMOS_VTL W=1.09u L=0.050u

* Instance _4_ (NAND2_X1): computes cout = _0_ NAND _1_
M__4__M_i_1 net__4__net_0 _1_ VSS VSS NMOS_VTL W=1.270u L=0.050u
M__4__M_i_0 cout _0_ net__4__net_0 VSS NMOS_VTL W=1.270u L=0.050u
M__4__M_i_3 cout _1_ VDD VDD PMOS_VTL W=0.325u L=0.050u
M__4__M_i_2 VDD _0_ cout VDD PMOS_VTL W=0.325u L=0.050u

* Parasitic capacitances
C_NET2_0 net__2__net_0 0 0.5f
C_NET3_0 net__3__net_0 0 0.5f
C_NET3_1 net__3__net_1 0 1f
C_NET4_0 net__4__net_0 0 0.5f
C_INT_0 _0_ 0 0.5f
C_INT_1 _1_ 0 0.5f

* Initial conditions
.IC V(_0_)=__VDD_50__ V(_1_)=__VDD_50__
.IC V(cout)=__VDD_VAL__

*************************************************************************
* Test Pattern - WILL BE REPLACED BY PYTHON
*************************************************************************

* Input under test

* Output loads
CLoad_cout cout 0 __OUTPUT_LOAD__

* Decoupling
C_VDD VDD 0 10p

*************************************************************************
* Analysis
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-4 ABSTOL=1e-9 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=__TEMP_VAL__

.TRAN __TSTEP__ __TSTOP__ 0 __TMAX__

*************************************************************************
* Measurements for Output: __OUTPUT_PIN__
*************************************************************************

.MEASURE TRAN T_IN_50 WHEN V(__INPUT_PIN__)=__VDD_50__ CROSS=1

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

.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=0ns TO=__TSTOP__
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=7ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END