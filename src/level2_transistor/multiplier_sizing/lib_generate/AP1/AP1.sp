* Xyce netlist for AP1 - Template for Liberty Generation
* Approximate 4-2 Compressor (58 transistors)
* Function: 4-input approximate compressor
* CRITICAL: Python script will add actual voltage sources

* MOS Models
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

* Power supplies
VDD VDD 0 DC __VDD_VAL__
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: AP1 (58 transistors)
*************************************************************************

* Flattened instance: _06_ (OAI22_X1)
M__06__M_i_3 VSS d net__06__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__06__M_i_2 net__06__net_0 cin VSS VSS NMOS_VTL W=0.145u L=0.050u
M__06__M_i_0 _03_ a net__06__net_0 VSS NMOS_VTL W=0.145u L=0.050u
M__06__M_i_1 net__06__net_0 b _03_ VSS NMOS_VTL W=0.145u L=0.050u
M__06__M_i_7 net__06__net_2 d VDD VDD PMOS_VTL W=0.145u L=0.050u
M__06__M_i_6 _03_ cin net__06__net_2 VDD PMOS_VTL W=0.145u L=0.050u
M__06__M_i_4 net__06__net_1 a _03_ VDD PMOS_VTL W=0.145u L=0.050u
M__06__M_i_5 VDD b net__06__net_1 VDD PMOS_VTL W=0.145u L=0.050u

* Flattened instance: _07_ (NAND2_X1)
M__07__M_i_1 net__07__net_0 d VSS VSS NMOS_VTL W=0.190u L=0.050u
M__07__M_i_0 _04_ cin net__07__net_0 VSS NMOS_VTL W=0.190u L=0.050u
M__07__M_i_3 _04_ d VDD VDD PMOS_VTL W=0.145u L=0.050u
M__07__M_i_2 VDD cin _04_ VDD PMOS_VTL W=0.145u L=0.050u

* Flattened instance: _08_ (NAND2_X1)
M__08__M_i_1 net__08__net_0 b VSS VSS NMOS_VTL W=0.190u L=0.050u
M__08__M_i_0 _05_ a net__08__net_0 VSS NMOS_VTL W=0.190u L=0.050u
M__08__M_i_3 _05_ b VDD VDD PMOS_VTL W=0.145u L=0.050u
M__08__M_i_2 VDD a _05_ VDD PMOS_VTL W=0.145u L=0.050u

* Flattened instance: _09_ (NAND3_X1)
M__09__M_i_2 net__09__net_1 _05_ VSS VSS NMOS_VTL W=0.775u L=0.050u
M__09__M_i_1 net__09__net_0 _04_ net__09__net_1 VSS NMOS_VTL W=0.775u L=0.050u
M__09__M_i_0 C _03_ net__09__net_0 VSS NMOS_VTL W=0.775u L=0.050u
M__09__M_i_5 C _05_ VDD VDD PMOS_VTL W=0.145u L=0.050u
M__09__M_i_4 VDD _04_ C VDD PMOS_VTL W=0.145u L=0.050u
M__09__M_i_3 C _03_ VDD VDD PMOS_VTL W=0.145u L=0.050u

* Flattened instance: _10_ (XOR2_X1)
M__10__M_i_0 net__10__net_000 a VSS VSS NMOS_VTL W=0.280u L=0.050u
M__10__M_i_7 VSS b net__10__net_000 VSS NMOS_VTL W=0.280u L=0.050u
M__10__M_i_13 _00_ net__10__net_000 VSS VSS NMOS_VTL W=0.235u L=0.050u
M__10__M_i_19 net__10__net_001 a _00_ VSS NMOS_VTL W=0.235u L=0.050u
M__10__M_i_24 VSS b net__10__net_001 VSS NMOS_VTL W=0.145u L=0.050u
M__10__M_i_30 net__10__net_002 a net__10__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M__10__M_i_35 VDD b net__10__net_002 VDD PMOS_VTL W=0.145u L=0.050u
M__10__M_i_41 net__10__net_003 net__10__net_000 VDD VDD PMOS_VTL W=0.235u L=0.050u
M__10__M_i_47 _00_ a net__10__net_003 VDD PMOS_VTL W=0.235u L=0.050u
M__10__M_i_53 net__10__net_003 b _00_ VDD PMOS_VTL W=0.235u L=0.050u

* Flattened instance: _11_ (XOR2_X1)
M__11__M_i_0 net__11__net_000 cin VSS VSS NMOS_VTL W=0.280u L=0.050u
M__11__M_i_7 VSS d net__11__net_000 VSS NMOS_VTL W=0.280u L=0.050u
M__11__M_i_13 _01_ net__11__net_000 VSS VSS NMOS_VTL W=0.235u L=0.050u
M__11__M_i_19 net__11__net_001 cin _01_ VSS NMOS_VTL W=0.235u L=0.050u
M__11__M_i_24 VSS d net__11__net_001 VSS NMOS_VTL W=0.145u L=0.050u
M__11__M_i_30 net__11__net_002 cin net__11__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M__11__M_i_35 VDD d net__11__net_002 VDD PMOS_VTL W=0.315u L=0.050u
M__11__M_i_41 net__11__net_003 net__11__net_000 VDD VDD PMOS_VTL W=0.235u L=0.050u
M__11__M_i_47 _01_ cin net__11__net_003 VDD PMOS_VTL W=0.235u L=0.050u
M__11__M_i_53 net__11__net_003 d _01_ VDD PMOS_VTL W=0.235u L=0.050u


* Flattened instance: _12_ (XNOR2_X1)
M__12__M_i_0 net__12__net_001 _00_ net__12__net_000 VSS NMOS_VTL W=2.305u L=0.050u
M__12__M_i_5 VSS _01_ net__12__net_001 VSS NMOS_VTL W=2.305u L=0.050u
M__12__M_i_11 net__12__net_002 net__12__net_000 VSS VSS NMOS_VTL W=0.370u L=0.050u
M__12__M_i_17 _02_ _00_ net__12__net_002 VSS NMOS_VTL W=0.370u L=0.050u
M__12__M_i_23 net__12__net_002 _01_ _02_ VSS NMOS_VTL W=0.370u L=0.050u
M__12__M_i_29 net__12__net_000 _00_ VDD VDD PMOS_VTL W=0.145u L=0.050u
M__12__M_i_36 VDD _01_ net__12__net_000 VDD PMOS_VTL W=0.145u L=0.050u
M__12__M_i_42 _02_ net__12__net_000 VDD VDD PMOS_VTL W=0.235u L=0.050u
M__12__M_i_48 net__12__net_003 _00_ _02_ VDD PMOS_VTL W=0.235u L=0.050u
M__12__M_i_53 VDD _01_ net__12__net_003 VDD PMOS_VTL W=0.235u L=0.050u

* Flattened instance: _13_ (OAI21_X1)
M__13__M_i_1 S _04_ net__13__net_0 VSS NMOS_VTL W=0.235u L=0.050u
M__13__M_i_0 net__13__net_0 _05_ S VSS NMOS_VTL W=0.235u L=0.050u
M__13__M_i_2 VSS _02_ net__13__net_0 VSS NMOS_VTL W=0.235u L=0.050u
M__13__M_i_4 net__13__net_1 _04_ VDD VDD PMOS_VTL W=2.170u L=0.050u
M__13__M_i_3 S _05_ net__13__net_1 VDD PMOS_VTL W=2.170u L=0.050u
M__13__M_i_5 VDD _02_ S VDD PMOS_VTL W=2.170u L=0.050u

*************************************************************************
* Parasitic capacitances for internal nodes
*************************************************************************
C_NET06_0 net__06__net_0 0 0.5f
C_NET06_1 net__06__net_1 0 0.5f
C_NET06_2 net__06__net_2 0 1f
C_NET07_0 net__07__net_0 0 0.5f
C_NET08_0 net__08__net_0 0 0.5f
C_NET09_0 net__09__net_0 0 0.5f
C_NET09_1 net__09__net_1 0 0.5f
C_NET10_000 net__10__net_000 0 0.5f
C_NET10_001 net__10__net_001 0 0.5f
C_NET10_002 net__10__net_002 0 0.5f
C_NET10_003 net__10__net_003 0 1f
C_NET11_000 net__11__net_000 0 0.5f
C_NET11_001 net__11__net_001 0 0.5f
C_NET11_002 net__11__net_002 0 0.5f
C_NET11_003 net__11__net_003 0 1f
C_NET12_000 net__12__net_000 0 0.5f
C_NET12_001 net__12__net_001 0 0.5f
C_NET12_002 net__12__net_002 0 0.5f
C_NET12_003 net__12__net_003 0 1f
C_NET13_0 net__13__net_0 0 1f
C_NET13_1 net__13__net_1 0 1f
C_INT_00 _00_ 0 0.5f
C_INT_01 _01_ 0 0.5f
C_INT_02 _02_ 0 0.5f
C_INT_03 _03_ 0 0.5f
C_INT_04 _04_ 0 0.5f
C_INT_05 _05_ 0 0.5f

* Initial conditions
.IC V(_00_)=__VDD_50__ V(_01_)=__VDD_50__ V(_02_)=__VDD_50__
.IC V(_03_)=__VDD_50__ V(_04_)=__VDD_50__ V(_05_)=__VDD_50__
.IC V(S)=0 V(C)=0

*************************************************************************
* Test Pattern - WILL BE REPLACED BY PYTHON
* Python script will insert actual voltage sources (Va, Vb, Vcin, Vd)
*************************************************************************

* Input under test
* NOTE: This section will be COMPLETELY REPLACED by Python with actual sources

* Output loads
CLoad_S S 0 __OUTPUT_LOAD__
CLoad_C C 0 __OUTPUT_LOAD__

* Decoupling
C_VDD VDD 0 10p
C_VSS VSS 0 10p

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
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=2ns TO=__TSTOP__
.MEASURE TRAN I_LEAK AVG {-I(VDD)} FROM=__LEAK_START__ TO=__TSTOP__

*************************************************************************
* Output
*************************************************************************
.PRINT TRAN FORMAT=CSV FILE=timing_data.csv V(__INPUT_PIN__) V(__OUTPUT_PIN__) {-I(VDD)}

.END
