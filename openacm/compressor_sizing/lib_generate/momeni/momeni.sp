* Xyce netlist for momeni - Approximate 4-2 Compressor
* Template for Liberty characterization
* Consistent measurement naming: delay_OUTPUT_rise/fall, slew_OUTPUT_rise/fall

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: momeni (30 transistors)
*************************************************************************

* Instance _3_ (OAI22_X1): computes _1_ = !((a & b) | (c & d))
M__3__M_i_3 VSS d net__3__net_0 VSS NMOS_VTL W=1.550u L=0.050u
M__3__M_i_2 net__3__net_0 c VSS VSS NMOS_VTL W=1.550u L=0.050u
M__3__M_i_0 _1_ a net__3__net_0 VSS NMOS_VTL W=1.550u L=0.050u
M__3__M_i_1 net__3__net_0 b _1_ VSS NMOS_VTL W=1.550u L=0.050u
M__3__M_i_7 net__3__net_2 d VDD VDD PMOS_VTL W=0.505u L=0.050u
M__3__M_i_6 _1_ c net__3__net_2 VDD PMOS_VTL W=0.505u L=0.050u
M__3__M_i_4 net__3__net_1 a _1_ VDD PMOS_VTL W=0.5050u L=0.050u
M__3__M_i_5 VDD b net__3__net_1 VDD PMOS_VTL W=0.505u L=0.050u

* Instance _4_ (INV_X1): computes cout = !_1_
M__4__M_i_0 cout _1_ VSS VSS NMOS_VTL W=2.305u L=0.050u
M__4__M_i_1 cout _1_ VDD VDD PMOS_VTL W=0.820u L=0.050u

* Instance _5_ (AND2_X1): computes _2_ = c & d
M__5__M_i_2 net__5__net_0 c net__5__ZN_neg VSS NMOS_VTL W=0.145u L=0.050u
M__5__M_i_3 VSS d net__5__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__5__M_i_0 _2_ net__5__ZN_neg VSS VSS NMOS_VTL W=0.1455u L=0.050u
M__5__M_i_4 net__5__ZN_neg c VDD VDD PMOS_VTL W=0.145u L=0.050u
M__5__M_i_5 VDD d net__5__ZN_neg VDD PMOS_VTL W=0.145u L=0.050u
M__5__M_i_1 _2_ net__5__ZN_neg VDD VDD PMOS_VTL W=0.145u L=0.050u

* Instance _6_ (AND2_X1): computes _0_ = a & b
M__6__M_i_2 net__6__net_0 a net__6__ZN_neg VSS NMOS_VTL W=0.145u L=0.050u
M__6__M_i_3 VSS b net__6__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__6__M_i_0 _0_ net__6__ZN_neg VSS VSS NMOS_VTL W=0.145u L=0.0500u
M__6__M_i_4 net__6__ZN_neg a VDD VDD PMOS_VTL W=0.145u L=0.050u
M__6__M_i_5 VDD b net__6__ZN_neg VDD PMOS_VTL W=0.145u L=0.050u
M__6__M_i_1 _0_ net__6__ZN_neg VDD VDD PMOS_VTL W=0.145u L=0.050u

* Instance _7_ (OR3_X1): computes S = _1_ | _2_ | _0_
M__7__M_i_2 VSS _1_ net__7__ZN_neg VSS NMOS_VTL W=0.145u L=0.050u
M__7__M_i_3 net__7__ZN_neg _2_ VSS VSS NMOS_VTL W=0.145u L=0.050u
M__7__M_i_4 VSS _0_ net__7__ZN_neg VSS NMOS_VTL W=0.145u L=0.050u
M__7__M_i_0 S net__7__ZN_neg VSS VSS NMOS_VTL W=0.145u L=0.050u
M__7__M_i_5 net__7__net_0 _1_ net__7__ZN_neg VDD PMOS_VTL W=0.145u L=0.050u
M__7__M_i_6 net__7__net_1 _2_ net__7__net_0 VDD PMOS_VTL W=0.145u L=0.050u
M__7__M_i_7 VDD _0_ net__7__net_1 VDD PMOS_VTL W=0.145u L=0.050u
M__7__M_i_1 S net__7__ZN_neg VDD VDD PMOS_VTL W=0.145u L=0.050u

*************************************************************************
* Parasitic capacitances
*************************************************************************
C_NET3_0 net__3__net_0 0 0.5f
C_NET3_1 net__3__net_1 0 0.5f
C_NET3_2 net__3__net_2 0 0.5f
C_NET5_ZN_neg net__5__ZN_neg 0 0.5f
C_NET5_0 net__5__net_0 0 0.5f
C_NET6_ZN_neg net__6__ZN_neg 0 0.5f
C_NET6_0 net__6__net_0 0 0.5f
C_NET7_0 net__7__net_0 0 1f
C_NET7_1 net__7__net_1 0 1f
C_NET7_ZN_neg net__7__ZN_neg 0 1f
C_INT_0 _0_ 0 0.5f
C_INT_1 _1_ 0 0.5f
C_INT_2 _2_ 0 0.5f

* Initial conditions
.IC V(_0_)=__VDD_50__ V(_1_)=__VDD_50__ V(_2_)=__VDD_50__
.IC V(S)=0 V(cout)=__COUT_INIT__

*************************************************************************
* Test Pattern - WILL BE REPLACED BY PYTHON
*************************************************************************

* Input under test

* Output loads
CLoad_S S 0 __OUTPUT_LOAD__
CLoad_cout cout 0 __OUTPUT_LOAD__

* Decoupling
C_VDD VDD 0 10p

*************************************************************************
* Analysis
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-3 ABSTOL=1e-6 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=50 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=__TEMP_VAL__

.TRAN __TSTEP__ __TSTOP__ 0 __TMAX__

*************************************************************************
* Measurements for Output: __OUTPUT_PIN__
* FIXED: Consistent naming convention
*************************************************************************

.MEASURE TRAN T_IN_50 WHEN V(__INPUT_PIN__)=__VDD_50__ CROSS=1

* Delay measurements (50% point)
.MEASURE TRAN T___OUTPUT_PIN___50_R WHEN V(__OUTPUT_PIN__)=__VDD_50__ RISE=1
.MEASURE TRAN T___OUTPUT_PIN___50_F WHEN V(__OUTPUT_PIN__)=__VDD_50__ FALL=1
.MEASURE TRAN DELAY___OUTPUT_PIN___RISE PARAM='T___OUTPUT_PIN___50_R-T_IN_50' GOAL=0
.MEASURE TRAN DELAY___OUTPUT_PIN___FALL PARAM='T___OUTPUT_PIN___50_F-T_IN_50' GOAL=0

* Slew measurements (10%-90% for rise, 90%-10% for fall)
.MEASURE TRAN T___OUTPUT_PIN___10_R WHEN V(__OUTPUT_PIN__)=__VDD_10__ RISE=1
.MEASURE TRAN T___OUTPUT_PIN___90_R WHEN V(__OUTPUT_PIN__)=__VDD_90__ RISE=1
.MEASURE TRAN SLEW___OUTPUT_PIN___RISE PARAM='T___OUTPUT_PIN___90_R-T___OUTPUT_PIN___10_R' GOAL=0

.MEASURE TRAN T___OUTPUT_PIN___90_F WHEN V(__OUTPUT_PIN__)=__VDD_90__ FALL=1
.MEASURE TRAN T___OUTPUT_PIN___10_F WHEN V(__OUTPUT_PIN__)=__VDD_10__ FALL=1 
.MEASURE TRAN SLEW___OUTPUT_PIN___FALL PARAM='T___OUTPUT_PIN___10_F-T___OUTPUT_PIN___90_F' GOAL=0

* Power measurements
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=0ns TO=__TSTOP__
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=2ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END