from PySpice.Spice.Netlist import SubCircuitFactory, Circuit
from PySpice.Unit import u_Ohm, u_pF
from numpy import power
from .base_subcircuit import BaseSubcircuit


# from utils import model_dict2str
from typing import Dict, Any, Union

# from utils import gen_unused_cells


class Sram6TCell(BaseSubcircuit):  # 继承自BaseSubcircuit
    ###6T SRAM Cell SubCircuitFactory with debug capabilities###
    NAME = "SRAM_6T_CELL"
    # The first and second nodes are always power and ground nodes,VDD and VSS #子电路名称和所有与外部连接的节点
    NODES = ("VDD", "VSS", "BL", "BLB", "WL")

    def __init__(self, pd_nmos_model_name: str, pu_pmos_model_name: str, pg_nmos_model_name: str, pd_width: float, pu_width: float, pg_width: float, length: float, w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF, disconnect=False, param_sweep=False, pmos_modle_choices="PMOS_VTG", nmos_modle_choices="NMOS_VTG"):  # 是否断开内部数据节点连接  # 基本6t单元所需参数：pd/pu/pg各自的模型名，晶体管长宽以及rc相关参数
        # Modify the name of this subcircuit before call parent class.__init__()
        if disconnect:
            self.NAME += "_DISCONNECT"  # 如果断开内部数据节点连接，改下子电路名字

        super().__init__(pd_nmos_model_name, pu_pmos_model_name, pd_width, pu_width, length, w_rc, pi_res, pi_cap)  # 调用父类初始化
        # Transistor Sizes (FreePDK45 uses nanometers)      #存储关键参数
        self.pmos_modle_choices = pmos_modle_choices
        self.nmos_modle_choices = nmos_modle_choices
        self.REQUIRED_COLUMNS = ["pmos_model_pu", "nmos_model_pd"]
        # 读取参数文件中的模型名
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.REQUIRED_COLUMNS2 = ["nmos_model_pg"]
        # 读取参数文件中的模型名
        self.mos_model_index2 = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS2)

        self.pg_width = pg_width
        self.pd_width = pd_width
        self.pu_width = pu_width
        self.pg_nmos_model_name = pg_nmos_model_name
        self.disconnect = disconnect

        if not self.w_rc:  # 不添加rc网络
            bl_node = self.NODES[2]
            blb_node = self.NODES[3]
            wl_node = self.NODES[4]
            q_node = "Q"
            qb_node = "QB"
        else:  # 添加RC网络，调用父类里的add函数，输入
            # Add L-shape RC networks for BL, BLB, and WL   #起始节点名称和段数
            bl_node = self.add_rc_networks_to_node(self.NODES[2], 1)
            blb_node = self.add_rc_networks_to_node(self.NODES[3], 1)
            wl_node = self.add_rc_networks_to_node(self.NODES[4], 1)
            # Add L-shape RC networks for Q and QB
            q_node = self.add_rc_networks_to_node("Q", 1)
            qb_node = self.add_rc_networks_to_node("QB", 1)

        self.add_6T_cell(bl_node, blb_node, wl_node, q_node, qb_node, param_sweep)  # 添加6T cell单元

    def add_6T_cell(self, bl_node, blb_node, wl_node, q_node, qb_node, param_sweep):
        ###Add 6T cell to the SRAM cell, initializaed with `0` at Q###
        # 处理断开模式下的内部节点命名
        if self.disconnect:
            data_q = "QD"
            data_qb = "QBD"
        else:
            data_q = q_node
            data_qb = qb_node
        if not param_sweep:
            # Access transistors    #添加传输门晶体管
            self.M("PGL", bl_node, wl_node, data_q, self.NODES[1], model=self.pg_nmos_model_name, w=self.pg_width, l=self.length)
            self.M("PGR", blb_node, wl_node, data_qb, self.NODES[1], model=self.pg_nmos_model_name, w=self.pg_width, l=self.length)
            print(f"[DEBUG] M1-M2: Access transistors NMOS={self.pg_nmos_model_name} W={self.pg_width} L={self.length})")

            # Cross-coupled inverters   #添加两个交叉耦合反相器
            self.M("PDL", data_q, "QB", self.NODES[1], self.NODES[1], model=self.nmos_pdk_model, w=self.pd_width, l=self.length)
            self.M("PUL", data_q, "QB", self.NODES[0], self.NODES[0], model=self.pmos_pdk_model, w=self.pu_width, l=self.length)
            self.M("PDR", data_qb, "Q", self.NODES[1], self.NODES[1], model=self.nmos_pdk_model, w=self.pd_width, l=self.length)
            self.M("PUR", data_qb, "Q", self.NODES[0], self.NODES[0], model=self.pmos_pdk_model, w=self.pu_width, l=self.length)

            print(f"[DEBUG] M3-M6: Cross-coupled inverters (NMOS={self.nmos_pdk_model} W={self.pd_width} L={self.length}" + f"        PMOS={self.pmos_pdk_model} W={self.pu_width} L={self.length})")
        else:
            self.M("PGL", bl_node, wl_node, data_q, self.NODES[1], model=self.nmos_modle_choices[int(self.mos_model_index2["nmos"])], w="nmos_width_pg", l="length")
            self.M("PGR", blb_node, wl_node, data_qb, self.NODES[1], model=self.nmos_modle_choices[int(self.mos_model_index2["nmos"])], w="nmos_width_pg", l="length")
            print(f"[DEBUG] M1-M2: Access transistors NMOS={self.pg_nmos_model_name} W={self.pg_width} L={'length'})")

            # Cross-coupled inverters   #添加两个交叉耦合反相器
            self.M("PDL", data_q, "QB", self.NODES[1], self.NODES[1], model=self.nmos_modle_choices[int(self.mos_model_index["nmos"])], w="nmos_width_pd", l="length")
            self.M("PUL", data_q, "QB", self.NODES[0], self.NODES[0], model=self.pmos_modle_choices[int(self.mos_model_index["pmos"])], w="pmos_width_pu", l="length")
            self.M("PDR", data_qb, "Q", self.NODES[1], self.NODES[1], model=self.nmos_modle_choices[int(self.mos_model_index["nmos"])], w="nmos_width_pd", l="length")
            self.M("PUR", data_qb, "Q", self.NODES[0], self.NODES[0], model=self.pmos_modle_choices[int(self.mos_model_index["pmos"])], w="pmos_width_pu", l="length")

            print(f"[DEBUG] M3-M6: Cross-coupled inverters (NMOS={self.nmos_pdk_model} W={self.pd_width} L={self.length}" + f"        PMOS={self.pmos_pdk_model} W={self.pu_width} L={self.length})")


class Sram6TCellForYield(Sram6TCell):  # 支持良率分析的6t sram单元
    ###6T SRAM Cell SubCircuitFactory with debug capabilities###
    NAME = "SRAM_6T_CELL"

    def __init__(
        self,
        pd_nmos_model_name: str,
        pu_pmos_model_name: str,
        pg_nmos_model_name: str,
        model_dict: Dict[str, Dict[str, Any]],
        pd_width: float,
        pu_width: float,
        pg_width: float,
        length: float,
        w_rc=False,
        pi_res=100 @ u_Ohm,
        pi_cap=0.001 @ u_pF,
        disconnect=False,
        suffix="",
        custom_mc=False,
        param_sweep=False,
    ):
        # Modify the name of this subcircuit before call parent class.__init__()
        if disconnect:
            assert suffix == "_0_0", "using disconnected cell in an array"

        self.NAME += suffix
        # Suffix of user defined model name
        self.suffix = suffix
        # Whether use local process parameters
        self.custom_mc = custom_mc
        self.param_sweep = param_sweep
        # Model parameters are in this dict.
        self.model_dict = model_dict

        # Call parent class's __init__()
        super().__init__(pd_nmos_model_name, pu_pmos_model_name, pg_nmos_model_name, pd_width, pu_width, pg_width, length, w_rc, pi_res, pi_cap, disconnect, param_sweep)
        self.pg_nmos_model_name = pg_nmos_model_name

    def add_6T_cell(self, bl_node, blb_node, wl_node, q_node, qb_node, param_sweep):  # 重写add函数
        ###Add 6T cell to the SRAM cell###
        if self.disconnect:
            data_q = "QD"
            data_qb = "QBD"
        else:
            data_q = q_node
            data_qb = qb_node
        if not param_sweep:
            # Access transistors    #为每个晶体管创建udf_model模型
            pgl_udf_model = self.pg_nmos_model_name + "_PGL" + self.suffix
            self.M("PGL", bl_node, wl_node, data_q, self.NODES[1], model=pgl_udf_model, w=self.pg_width, l=self.length)
            self.add_usrdefine_mos_model(self.pg_nmos_model_name, pgl_udf_model)

            pgr_udf_model = self.pg_nmos_model_name + "_PGR" + self.suffix
            self.M("PGR", blb_node, wl_node, data_qb, self.NODES[1], model=pgr_udf_model, w=self.pg_width, l=self.length)
            self.add_usrdefine_mos_model(self.pg_nmos_model_name, pgr_udf_model)

            print(f"[DEBUG] M1-M2: Access transistors NMOS={pgl_udf_model} W={self.pg_width} L={self.length})")

            # Cross-coupled inverters
            # Left-side inverter
            pdl_udf_model = self.nmos_pdk_model + "_PDL" + self.suffix
            self.M("PDL", data_q, "QB", self.NODES[1], self.NODES[1], model=pdl_udf_model, w=self.pd_width, l=self.length)
            self.add_usrdefine_mos_model(self.nmos_pdk_model, pdl_udf_model)

            pul_udf_model = self.pmos_pdk_model + "_PUL" + self.suffix
            self.M("PUL", data_q, "QB", self.NODES[0], self.NODES[0], model=pul_udf_model, w=self.pu_width, l=self.length)
            self.add_usrdefine_mos_model(self.pmos_pdk_model, pul_udf_model)

            # Right-side inverter
            pdr_udf_model = self.nmos_pdk_model + "_PDR" + self.suffix
            self.M("PDR", data_qb, "Q", self.NODES[1], self.NODES[1], model=pdr_udf_model, w=self.pd_width, l=self.length)
            self.add_usrdefine_mos_model(self.nmos_pdk_model, pdr_udf_model)

            pur_udf_model = self.pmos_pdk_model + "_PUR" + self.suffix
            self.M("PUR", data_qb, "Q", self.NODES[0], self.NODES[0], model=pur_udf_model, w=self.pu_width, l=self.length)
            self.add_usrdefine_mos_model(self.pmos_pdk_model, pur_udf_model)

            print(f"[DEBUG] M3-M6: Cross-coupled inverters (NMOS={pdr_udf_model} W={self.pd_width} L={self.length}" + f"        PMOS={pur_udf_model} W={self.pu_width} L={self.length})")
        else:
            # Access transistors    #为每个晶体管创建udf_model模型
            pgl_udf_model = self.pg_nmos_model_name + "_PGL" + self.suffix
            self.M("PGL", bl_node, wl_node, data_q, self.NODES[1], model=pgl_udf_model, w="nmos_width_pg", l="length")
            self.add_usrdefine_mos_model(self.pg_nmos_model_name, pgl_udf_model)

            pgr_udf_model = self.pg_nmos_model_name + "_PGR" + self.suffix
            self.M("PGR", blb_node, wl_node, data_qb, self.NODES[1], model=pgr_udf_model, w="nmos_width_pg", l="length")
            self.add_usrdefine_mos_model(self.pg_nmos_model_name, pgr_udf_model)

            print(f"[DEBUG] M1-M2: Access transistors NMOS={pgl_udf_model} W={'nmos_width_pg'} L={'length'})")

            # Cross-coupled inverters
            # Left-side inverter
            pdl_udf_model = self.nmos_pdk_model + "_PDL" + self.suffix
            self.M("PDL", data_q, "QB", self.NODES[1], self.NODES[1], model=pdl_udf_model, w="nmos_width_pd", l="length")
            self.add_usrdefine_mos_model(self.nmos_pdk_model, pdl_udf_model)

            pul_udf_model = self.pmos_pdk_model + "_PUL" + self.suffix
            self.M("PUL", data_q, "QB", self.NODES[0], self.NODES[0], model=pul_udf_model, w="pmos_width_pu", l="length")
            self.add_usrdefine_mos_model(self.pmos_pdk_model, pul_udf_model)

            # Right-side inverter
            pdr_udf_model = self.nmos_pdk_model + "_PDR" + self.suffix
            self.M("PDR", data_qb, "Q", self.NODES[1], self.NODES[1], model=pdr_udf_model, w="nmos_width_pd", l="length")
            self.add_usrdefine_mos_model(self.nmos_pdk_model, pdr_udf_model)

            pur_udf_model = self.pmos_pdk_model + "_PUR" + self.suffix
            self.M("PUR", data_qb, "Q", self.NODES[0], self.NODES[0], model=pur_udf_model, w="pmos_width_pu", l="length")
            self.add_usrdefine_mos_model(self.pmos_pdk_model, pur_udf_model)

            print(f"[DEBUG] M3-M6: Cross-coupled inverters (NMOS={pdr_udf_model} W={'pmos_width_pu'} L={'length'}" + f"        PMOS={pur_udf_model} W={self.pu_width} L={self.length})")

    def add_usrdefine_mos_model(self, pdk_model_name, udf_model_name):  # 添加用户定义的mos模型？？
        model_data = self.model_dict[pdk_model_name]  # 通过pdk_model_name获取模型数据
        mos_type = model_data["type"]  # 提取模型类型
        self.raw_spice += f".model {udf_model_name} {mos_type} "
        params = model_data["parameters"]  # 获取模型所有参数
        for param_name, param_value in params.items():  # 遍历每个参数名和参数值
            # Format parameter value
            if isinstance(param_value, float):
                # Use scientific notation for very small/large numbers
                if abs(param_value) < 1e-3 or abs(param_value) > 1e6:
                    param_str = f"{param_value:.3e}"  # 非常大或非常小的值用科学计数法
                else:
                    param_str = str(param_value)
            else:
                param_str = str(param_value)
            # substitute the default values with user-defined parameters将默认值替换为用户定义的参数
            if param_name in ["vth0", "u0", "voff"]:
                param_str = f"'{param_name}_{udf_model_name}'"
            # Write parameter
            self.raw_spice += f"{param_name}={param_str} "
        self.raw_spice += "\n"
        # print(f"[DEBUG] {self.raw_spice}")
        # assert 0


class Sram6TCore(SubCircuitFactory):  # 构建sram阵列
    ###
    # SRAM Array SubCircuitFactory class.
    # Configurable number of rows and columns.
    ###

    def __init__(self, num_rows: int, num_cols: int, pd_nmos_model_name: str, pu_pmos_model_name: str, pg_nmos_model_name: str, pd_width=0.205e-6, pu_width=0.09e-6, pg_width=0.135e-6, length=50e-9, w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF, param_sweep=False, pmos_modle_choices="PMOS_VTG", nmos_modle_choices="NMOS_VTG", target_row=1, target_col=1, gen_unused_cells=False, q_init_val=0, config=None):  # 添加新参数
        #  disconnect=False, target_row=None, target_col=None):

        # print(f"\033[91m Sram6TCore Init \033[0m")

        self.NAME = f"SRAM_6T_CORE_{num_rows}x{num_cols}"
        # Define nodes
        self.NODES = (  # 动态生成第几列第几行
            "VDD",  # Power supply
            "VSS",  # Ground
            *[f"BL{i}" for i in range(num_cols)],  # Bitlines
            *[f"BLB{i}" for i in range(num_cols)],  # Bitline bars
            *[f"WL{i}" for i in range(num_rows)],  # Wordlines
        )
        super().__init__()
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.pd_nmos_pdk_model = pd_nmos_model_name
        self.pu_pmos_pdk_model = pu_pmos_model_name
        self.pg_pmos_pdk_model = pg_nmos_model_name
        # Transistor Sizes (FreePDK45 uses nanometers)
        self.pg_width = pg_width
        self.pd_width = pd_width
        self.pu_width = pu_width
        self.length = length
        # other config
        self.w_rc = w_rc
        self.pi_res = pi_res
        self.pi_cap = pi_cap
        self.param_sweep = param_sweep
        self.pmos_modle_choices = pmos_modle_choices
        self.nmos_modle_choices = nmos_modle_choices

        self.target_row = target_row
        self.target_col = target_col

        self.q_init_val = q_init_val  # 初始化Q的值

        self.gen_unused_cells = gen_unused_cells

        self.config = config  # 用于配置文件的参数

        # Build the array
        self.build_array(num_rows, num_cols)  # 构建阵列
        # set instance prefix and the name of 6t cell
        self.inst_prefix = "XSRAM_6T_CELL"  # 设置实例的前缀

    def add_equivalent_circuit(self):
        from .sram_cell_parasitics import SRAMCellParasiticTester

        tester = SRAMCellParasiticTester(config=self.config, corner="TT", pd_nmos_model=self.pd_nmos_pdk_model, pu_pmos_model=self.pu_pmos_pdk_model, pg_nmos_model=self.pg_pmos_pdk_model, pd_width=self.pd_width, pu_width=self.pu_width, pg_width=self.pg_width, length=self.length, q_init_val=self.q_init_val)

        vdd_r = tester.get_static_power_r()["R"]
        self.R(f"res_static_power", self.NODES[0], self.NODES[1], vdd_r / ((self.num_cols - 1) * (self.num_rows - 1)) @ u_Ohm)  # 添加静态功耗电阻

        wl_c = tester.get_port_c("WL")
        bl_c = tester.get_port_c("BL")
        blb_c = tester.get_port_c("BLB")

        if self.w_rc:
            for row in range(self.num_rows):
                if row != self.target_row:
                    wl_mid_node = f"WL{row}_rc_mid"
                    self.C(f"cap_WL{row}", wl_mid_node, self.NODES[1], self.pi_cap * (self.num_cols - 1))
                    self.R(f"res_WL{row}", f"WL{row}", wl_mid_node, self.pi_res / (self.num_cols - 1))

                    self.C(f"cap_WL{row}_cell", f"WL{row}", self.NODES[1], wl_c * (self.num_cols - 1))  # 添加WL的等效电容

            for col in range(self.num_cols):
                if col != self.target_col:
                    bl_mid_node = f"BL{col}_rc_mid"
                    blb_mid_node = f"BLB{col}_rc_mid"
                    self.C(f"cap_BL{col}", bl_mid_node, self.NODES[1], self.pi_cap * (self.num_rows - 1))
                    self.C(f"cap_BLB{col}", blb_mid_node, self.NODES[1], self.pi_cap * (self.num_rows - 1))
                    self.R(f"res_BL{col}", f"BL{col}", bl_mid_node, self.pi_res / (self.num_rows - 1))
                    self.R(f"res_BLB{col}", f"BLB{col}", blb_mid_node, self.pi_res / (self.num_rows - 1))

                    self.C(f"cap_BL{col}_cell", f"BL{col}", self.NODES[1], bl_c * (self.num_rows - 1))  # 添加BL的等效电容
                    self.C(f"cap_BLB{col}_cell", f"BLB{col}", self.NODES[1], blb_c * (self.num_rows - 1))  # 添加BLB的等效电容

    def build_array(self, num_rows, num_cols):
        # print(f"\033[91m {self.target_row} {self.target_col} Init \033[0m")
        print(f"[DEBUG] Sram6TCore: Building {num_rows}x{num_cols} SRAM array with target row {self.target_row} and target col {self.target_col}")
        # Generate SRAM cells   #创建单个sram单元子电路
        subckt_6t_cell = Sram6TCell(self.pd_nmos_pdk_model, self.pu_pmos_pdk_model, self.pg_pmos_pdk_model, self.pd_width, self.pu_width, self.pg_width, self.length, w_rc=self.w_rc, pi_res=self.pi_res, pi_cap=self.pi_cap, param_sweep=self.param_sweep, pmos_modle_choices=self.pmos_modle_choices, nmos_modle_choices=self.nmos_modle_choices)

        # define the cell subcircuit    #添加cell单元
        self.subcircuit(subckt_6t_cell)

        # Instantiate SRAM cells    #遍历所有行和列，实例化单元子电路
        for row in range(num_rows):
            for col in range(num_cols):
                if self.gen_unused_cells or row == self.target_row or col == self.target_col:
                    # print(f"\033[91m{'-' * 20} Sram6TCell {row} {col} {'-' * 20}\033[0m")
                    print(f"[DEBUG] generating Sram6TCell {row} {col}")
                    self.X(
                        subckt_6t_cell.name + f"_{row}_{col}",  # 实例的名称
                        subckt_6t_cell.name,  # 引用的子电路类型，即Sram6TCell
                        self.NODES[0],  # Power net             #连接的节点名
                        self.NODES[1],  # Ground net
                        f"BL{col}",  # Connect to column bitline
                        f"BLB{col}",  # Connect to column bitline bar
                        f"WL{row}",  # Connect to row wordline
                    )

        if not self.gen_unused_cells:
            print(f"[DEBUG] generating equivalent circuit for unused cells")
            self.add_equivalent_circuit()  # 添加等效电路


class Sram6TCoreForYield(Sram6TCore):  # 使用良率分析时调用的sram 阵列，继承基础阵列
    ###
    # SRAM Array SubCircuitFactory class.
    # Configurable number of rows and columns.
    ###

    def __init__(self, num_rows: int, num_cols: int, pd_nmos_model_name: str, pu_pmos_model_name: str, pg_nmos_model_name: str, model_dict: Dict[str, Dict[str, Any]], pd_width=0.205e-6, pu_width=0.09e-6, pg_width=0.135e-6, length=50e-9, w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF, param_sweep=False, target_row=1, target_col=1, gen_unused_cells=False, q_init_val=0, config=None):
        # add model_dict for customizing transistor `.model` in each cell
        # set `model_dict` before super().__init__()

        # print(f"\033[91m Sram6TCoreForYield Init \033[0m")

        self.model_dict = model_dict

        super().__init__(num_rows, num_cols, pd_nmos_model_name, pu_pmos_model_name, pg_nmos_model_name, pd_width, pu_width, pg_width, length, w_rc, pi_res, pi_cap, param_sweep, target_row=target_row, target_col=target_col, gen_unused_cells=gen_unused_cells, q_init_val=q_init_val, config=config)
        self.pd_nmos_pdk_model = pd_nmos_model_name
        self.pu_pmos_pdk_model = pu_pmos_model_name
        self.pg_pmos_pdk_model = pg_nmos_model_name
        self.param_sweep = param_sweep

    def build_array(self, num_rows, num_cols):  # 重写阵列构建函数
        # print(f"\033[91m {self.target_row} {self.target_col} Init \033[0m")
        print(f"[DEBUG] Sram6TCore: Building {num_rows}x{num_cols} SRAM array with target row {self.target_row} and target col {self.target_col}")
        # Generate SRAM cells
        for row in range(num_rows):
            for col in range(num_cols):
                if self.gen_unused_cells or row == self.target_row or col == self.target_col:
                    # print red words
                    # print(f"\033[91m{'-' * 20} Sram6TCoreForYield {row} {col} {'-' * 20}\033[0m")
                    print(f"[DEBUG] generating Sram6TCellForYield {row} {col}")
                    # instantiate the bitcell's subcircuit for each bit
                    subckt_6t_cell = Sram6TCellForYield(self.pd_nmos_pdk_model, self.pu_pmos_pdk_model, self.pg_pmos_pdk_model, self.model_dict, self.pd_width, self.pu_width, self.pg_width, self.length, w_rc=self.w_rc, pi_res=self.pi_res, pi_cap=self.pi_cap, suffix=f"_{row}_{col}", param_sweep=self.param_sweep)  # 和SRAM6TCORE调用的不一样

                    # add the cell subcircuit to this circuit
                    self.subcircuit(subckt_6t_cell)

                    # Instantiate SRAM cells
                    self.X(
                        subckt_6t_cell.name,
                        subckt_6t_cell.name,
                        self.NODES[0],  # Power net
                        self.NODES[1],  # Ground net
                        f"BL{col}",  # Connect to column bitline
                        f"BLB{col}",  # Connect to column bitline bar
                        f"WL{row}",  # Connect to row wordline
                    )

        if not self.gen_unused_cells:
            print(f"[DEBUG] generating equivalent circuit for unused cells")
            self.add_equivalent_circuit()  # 添加等效电路


# if __name__ == '__main__':
#     pdk_path = 'model_lib/models.spice'
#     nmos_model_name = 'NMOS_VTG'
#     pmos_model_name = 'PMOS_VTG'
#     pd_width=0.205e-6
#     pu_width=0.09e-6
#     pg_width=0.135e-6
#     length=50e-9

# #     # bc = SRAM_6T_Cell_for_Yield(
# #     #     nmos_model_name, pmos_model_name,
# #     #     pd_width=0.1e-6, pu_width=0.2e-6, pg_width=1.5e-6, length=45e-9,
# #     #     suffix='_0_0', disconnect=True,
# #     # )
# #     # print(bc)

#     array = Sram6TCoreForYield(
#         2, 2,
#         nmos_model_name, pmos_model_name,
#         pd_width=pd_width, pu_width=pu_width, pg_width=pg_width, length=length,
#         w_rc=True, pi_res=100 @ u_Ohm, pi_cap=0.010 @ u_pF
#     )
#     print(array)
