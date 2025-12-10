* Xyce netlist for kong2 - 4:2 Compressor
* Template for Liberty characterization - FIXED VERSION
* Consistent measurement naming: delay_OUTPUT_rise/fall, slew_OUTPUT_rise/fall

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: kong2
*************************************************************************

* Flattened instance: _05_ (OAI22_X1)
M__05__M_i_3 VSS d net__05__net_0 VSS NMOS_VTL W=0.190u L=0.050u
M__05__M_i_2 net__05__net_0 c VSS VSS NMOS_VTL W=0.190u L=0.050u
M__05__M_i_0 _02_ a net__05__net_0 VSS NMOS_VTL W=0.190u L=0.050u
M__05__M_i_1 net__05__net_0 b _02_ VSS NMOS_VTL W=0.190u L=0.050u
M__05__M_i_7 net__05__net_2 d VDD VDD PMOS_VTL W=0.505u L=0.050u
M__05__M_i_6 _02_ c net__05__net_2 VDD PMOS_VTL W=0.505u L=0.050u
M__05__M_i_4 net__05__net_1 a _02_ VDD PMOS_VTL W=0.505u L=0.050u
M__05__M_i_5 VDD b net__05__net_1 VDD PMOS_VTL W=0.505u L=0.050u

* Flattened instance: _06_ (INV_X1)
M__06__M_i_0 _03_ _02_ VSS VSS NMOS_VTL W=0.325u L=0.050u
M__06__M_i_1 _03_ _02_ VDD VDD PMOS_VTL W=0.235u L=0.050u

* Flattened instance: _07_ (AOI22_X1)
M__07__M_i_3 net__07__net_1 d VSS VSS NMOS_VTL W=0.685u L=0.050u
M__07__M_i_2 _04_ c net__07__net_1 VSS NMOS_VTL W=0.685u L=0.050u
M__07__M_i_0 net__07__net_0 a _04_ VSS NMOS_VTL W=0.685u L=0.050u
M__07__M_i_1 VSS b net__07__net_0 VSS NMOS_VTL W=0.685u L=0.050u
M__07__M_i_7 VDD d net__07__net_2 VDD PMOS_VTL W=0.865u L=0.050u
M__07__M_i_6 net__07__net_2 c VDD VDD PMOS_VTL W=0.865u L=0.050u
M__07__M_i_4 _04_ a net__07__net_2 VDD PMOS_VTL W=0.865u L=0.050u
M__07__M_i_5 net__07__net_2 b _04_ VDD PMOS_VTL W=0.865u L=0.050u

* Flattened instance: _08_ (NAND2_X1)
M__08__M_i_1 net__08__net_0 _04_ VSS VSS NMOS_VTL W=1.945u L=0.050u
M__08__M_i_0 cout _02_ net__08__net_0 VSS NMOS_VTL W=1.9455u L=0.050u
M__08__M_i_3 cout _04_ VDD VDD PMOS_VTL W=1.990u L=0.050u
M__08__M_i_2 VDD _02_ cout VDD PMOS_VTL W=1.990u L=0.050u

* Flattened instance: _09_ (XOR2_X1)
M__09__M_i_0 net__09__net_000 a VSS VSS NMOS_VTL W=0.190u L=0.050u
M__09__M_i_7 VSS b net__09__net_000 VSS NMOS_VTL W=0.190u L=0.050u
M__09__M_i_13 _00_ net__09__net_000 VSS VSS NMOS_VTL W=0.145u L=0.050u
M__09__M_i_19 net__09__net_001 a _00_ VSS NMOS_VTL W=0.145u L=0.050u
M__09__M_i_24 VSS b net__09__net_001 VSS NMOS_VTL W=0.145u L=0.050u
M__09__M_i_30 net__09__net_002 a net__09__net_000 VDD PMOS_VTL W=0.190u L=0.050u
M__09__M_i_35 VDD b net__09__net_002 VDD PMOS_VTL W=0.190u L=0.050u
M__09__M_i_41 net__09__net_003 net__09__net_000 VDD VDD PMOS_VTL W=0.145u L=0.050u
M__09__M_i_47 _00_ a net__09__net_003 VDD PMOS_VTL W=0.145u L=0.050u
M__09__M_i_53 net__09__net_003 b _00_ VDD PMOS_VTL W=0.145u L=0.050u

* Flattened instance: _10_ (NOR3_X1)
M__10__M_i_2 _01_ _00_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__10__M_i_1 VSS d _01_ VSS NMOS_VTL W=0.415u L=0.050u
M__10__M_i_0 _01_ c VSS VSS NMOS_VTL W=0.415u L=0.050u
M__10__M_i_5 net__10__net_1 _00_ VDD VDD PMOS_VTL W=0.145u L=0.050u
M__10__M_i_4 net__10__net_0 d net__10__net_1 VDD PMOS_VTL W=0.145u L=0.050u
M__10__M_i_3 _01_ c net__10__net_0 VDD PMOS_VTL W=0.145u L=0.050u

* Flattened instance: _11_ (AOI21_X1)
M__11__M_i_1 net__11__net_0 _03_ VSS VSS NMOS_VTL W=0.280u L=0.050u
M__11__M_i_0 S _04_ net__11__net_0 VSS NMOS_VTL W=0.280u L=0.050u
M__11__M_i_2 VSS _01_ S VSS NMOS_VTL W=0.280u L=0.050u
M__11__M_i_4 S _03_ net__11__net_1 VDD PMOS_VTL W=2.575u L=0.050u
M__11__M_i_3 net__11__net_1 _04_ S VDD PMOS_VTL W=2.575u L=0.050u
M__11__M_i_5 VDD _01_ net__11__net_1 VDD PMOS_VTL W=2.575u L=0.050u

* Parasitic capacitances
C_NET09_000 net__09__net_000 0 0.5f
C_NET09_001 net__09__net_001 0 0.5f
C_NET09_002 net__09__net_002 0 0.5f
C_NET09_003 net__09__net_003 0 1f
C_NET05_0 net__05__net_0 0 0.5f
C_NET05_1 net__05__net_1 0 0.5f
C_NET05_2 net__05__net_2 0 0.5f
C_NET07_0 net__07__net_0 0 0.5f
C_NET07_1 net__07__net_1 0 0.5f
C_NET07_2 net__07__net_2 0 0.5f
C_NET08_0 net__08__net_0 0 0.5f
C_NET10_0 net__10__net_0 0 0.5f
C_NET10_1 net__10__net_1 0 0.5f
C_NET11_0 net__11__net_0 0 0.5f
C_NET11_1 net__11__net_1 0 0.5f
C_INT_00 _00_ 0 0.5f
C_INT_01 _01_ 0 0.5f
C_INT_02 _02_ 0 0.5f
C_INT_03 _03_ 0 0.5f
C_INT_04 _04_ 0 0.5f

* Initial conditions
.IC V(_00_)=__VDD_50__ V(_01_)=__VDD_50__ V(_02_)=__VDD_50__
.IC V(_03_)=__VDD_50__ V(_04_)=__VDD_50__
.IC V(S)=0 V(cout)=__VDD_VAL__

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

.OPTIONS TIMEINT RELTOL=1e-4 ABSTOL=1e-9 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0
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