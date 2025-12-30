from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF, u_A, u_mA
from sram_compiler.subcircuits.sram_6t_core_for_yield import Sram6TCore, Sram6TCell, Sram6TCoreForYield, Sram6TCellForYield  # type: ignore  # Assuming SRAM_6T_Cell_RC is defined
from sram_compiler.subcircuits.standard_cell import Pbuff  # type: ignore
from sram_compiler.subcircuits.wordline_driver import WordlineDriver  # type: ignore
from sram_compiler.subcircuits.precharge_and_write_driver import Precharge, WriteDriver  # type: ignore
from sram_compiler.subcircuits.mux_and_sa import ColumnMux, ColumnMux_simple, SenseAmp  # type: ignore
from sram_compiler.subcircuits.decoder import DECODER_CASCADE  # type: ignore
from utils import parse_spice_models  # type: ignore
from sram_compiler.testbenches.base_testbench import BaseTestbench  # type: ignore
from math import ceil, log2


class Sram6TCoreTestbench(BaseTestbench):  # SRAM array testbench, inherits from BaseTestbench
    def __init__(self, sram_config, w_rc=False, pi_res=10 @ u_Ohm, pi_cap=0.001 @ u_pF, custom_mc: bool = False, param_sweep: bool = False, sweep_precharge: bool = False, sweep_senseamp: bool = False, sweep_wordlinedriver: bool = False, sweep_columnmux: bool = False, sweep_writedriver: bool = False, sweep_decoder: bool = False, corner="TT", choose_columnmux: bool = True, q_init_val: int = 0, gen_unused_cells: bool = False):
        # Store configuration object reference
        self.sram_config = sram_config  # Contains parameters of all subcircuits
        global_cfg = sram_config.global_config
        cell_cfg = sram_config.sram_6t_cell

        super().__init__(f"SRAM_6T_CORE_{global_cfg.num_rows}x{global_cfg.num_cols}_TB", global_cfg.vdd, global_cfg.pdk_path_TT)
        # transistor size info.
        # self.pd_width = pd_width
        # self.pu_width = pu_width
        # self.pg_width = pg_width
        # self.length = length
        # array size
        self.num_rows = global_cfg.num_rows  # Read rows/cols from global.yaml
        self.num_cols = global_cfg.num_cols
        self.cell_inst_prefix = "X"  # Instance prefix
        self.arr_inst_prefix = "X"
        # add rc?
        self.w_rc = w_rc
        self.pi_res = pi_res
        self.pi_cap = pi_cap
        self.heir_delimiter = ":"
        # User defined MC simulation
        self.choose_columnmux = choose_columnmux
        self.corner = corner  # Select process corner
        self.custom_mc = custom_mc  # Enable Monte Carlo?
        self.param_sweep = param_sweep  # Parameter sweep for cell?
        self.sweep_precharge = sweep_precharge  # Parameter sweep for precharge?
        self.sweep_senseamp = sweep_senseamp  # Parameter sweep for sense amplifier?
        self.sweep_wordlinrdriver = sweep_wordlinedriver  # Parameter sweep for wordline driver?
        self.sweep_columnmux = sweep_columnmux  # Parameter sweep for column mux?
        self.sweep_writedriver = sweep_writedriver  # Parameter sweep for write driver?
        self.sweep_decoder = sweep_decoder  # Parameter sweep for decoder?
        # init internal data q
        self.q_init_val = q_init_val
        self.gen_unused_cells = gen_unused_cells  # Generate unused cells?
        # default mux inputs
        self.mux_in = 1
        # self.set_vdd(5)

    def create_decoder(self, circuit: Circuit):
        decoder_config = self.sram_config.decoder  # Extract decoder parameters from top-level config
        decoder = DECODER_CASCADE(nmos_model_name=decoder_config.nmos_model.value[0], pmos_model_name=decoder_config.pmos_model.value[0], num_rows=self.num_rows, base_nand_pmos_width=decoder_config.pmos_width.value[0], base_nand_nmos_width=decoder_config.nmos_width.value[0], base_inv_pmos_width=decoder_config.pmos_width.value[1], base_inv_nmos_width=decoder_config.nmos_width.value[1], length=decoder_config.length.value, w_rc=self.w_rc, pi_res=self.pi_res, pi_cap=self.pi_cap, sweep_decoder=self.sweep_decoder, pmos_model_choices=self.sram_config.senseamp.pmos_model.choices, nmos_model_choices=self.sram_config.senseamp.nmos_model.choices)  # default `w_rc` is False
        circuit.subcircuit(decoder)  # Add to main circuit
        # Compute address bit width
        n_bits = ceil(log2(self.num_rows)) if self.num_rows > 1 else 1
        # Address nodes
        address_nodes = [f"A{i}" for i in range(n_bits)]

        # # Set address signals (target row address)
        # address_nodes = []
        # for bit in range(n_bits):
        #     bit_val = (target_row >> bit) & 1  # Extract each bit's value
        #     node_name = f'A{bit}'
        #     if bit_val:
        #         circuit.V(f'ADDR_{bit}', node_name, self.gnd_node, self.vdd)
        #     else:
        #         circuit.V(f'ADDR_{bit}', node_name, self.gnd_node, 0 @ u_V)
        #     address_nodes.append(node_name)

        # Add enable signal - always enabled
        # circuit.V('DEC_EN', 'EN', self.gnd_node, self.vdd @ u_V)

        # Wordline nodes
        wl_nodes = [f"DEC_WL{i}" for i in range(self.num_rows)]

        # Instantiate decoder
        circuit.X("DECODER", decoder.NAME, self.power_node, self.gnd_node, *address_nodes, *wl_nodes)  # VDD, VSS  # address signals  # wordline outputs
        # Save decoder outputs for wordline driver
        self.decoder_wl_nodes = wl_nodes

        return circuit

    def create_wl_driver(self, circuit: Circuit, target_row: int):  # Create wordline driver function
        """Create wordline driver for the target/standby row"""
        wl_config = self.sram_config.wordline_driver  # Extract wordline parameters from top-level config
        wldrv = WordlineDriver(
            nmos_model_name=wl_config.nmos_model.value[0],
            pmos_model_name=wl_config.pmos_model.value[0],
            base_nand_pmos_width=wl_config.pmos_width.value[0],
            base_nand_nmos_width=wl_config.nmos_width.value[0],
            base_inv_pmos_width=wl_config.pmos_width.value[1],
            base_inv_nmos_width=wl_config.nmos_width.value[1],
            length=wl_config.length.value,
            num_cols=self.num_cols,
            w_rc=self.w_rc,  # default `w_rc` is False
            # pi_res=self.pi_res, pi_cap=self.pi_cap,
            sweep_wordlinedriver=self.sweep_wordlinrdriver,
            pmos_modle_choices=self.sram_config.senseamp.pmos_model.choices,
            nmos_modle_choices=self.sram_config.senseamp.nmos_model.choices,
        )
        circuit.subcircuit(wldrv)  # Add to main circuit

        # Add WL enable signal (pulse voltage source)
        circuit.PulseVoltageSource(
            "WL_EN",
            "WL_EN",
            self.gnd_node,
            initial_value=0 @ u_V,
            pulsed_value=self.vdd @ u_V,
            delay_time=5 @ u_ns,
            rise_time=self.t_rise,
            fall_time=self.t_fall,
            pulse_width=7e-09,
            period=self.t_period,
        )

        # Wordline control & drivers
        for row in range(self.num_rows):
            # if row == target_row:   # Target row, initially row 0 in MC
            #     # Add pulse source to control WL enable for target row
            #     circuit.PulseVoltageSource(
            #         f'WLE_{row}', f'WLE{row}', self.gnd_node,
            #         initial_value=0 @ u_V, pulsed_value=self.vdd,
            #         delay_time=self.t_pulse,
            #         rise_time=self.t_rise, fall_time=self.t_fall,
            #         pulse_width=self.t_pulse,
            #         period=self.t_period
            #     )
            # Use decoder output as enable signal
            decoder_enable = self.decoder_wl_nodes[row]
            # Instantiate wordline driver
            # Add wordline driver
            circuit.X(
                f"WL_DRV_{row}",
                wldrv.name,
                self.power_node,
                self.gnd_node,
                decoder_enable,  # Enable signal from decoder
                "WL_EN",  # Internal enable (always active)
                f"WL{row}",  # Output to SRAM array
            )
            # else:
            #     # Tie idle wordlines to ground
            #     circuit.V(f'WL{row}_gnd', f'WL{row}', self.gnd_node, 0 @ u_V)
        return circuit

    def create_read_periphery(self, circuit: Circuit, target_col: int):  # Create read periphery circuitry
        """Create read periphery circuitry: precharge + column mux + sense amplifier"""

        prch = Precharge(
            pmos_model_name=self.sram_config.precharge.pmos_model.value,
            base_pmos_width=self.sram_config.precharge.pmos_width.value,
            length=self.sram_config.precharge.length.value,
            w_rc=self.w_rc,  # default `w_rc` is False
            # pi_res=self.pi_res, pi_cap=self.pi_cap,
            num_rows=self.num_rows,
            sweep_precharge=self.sweep_precharge,
            pmos_modle_choices=self.sram_config.precharge.pmos_model.choices,
        )
        circuit.subcircuit(prch)  # Add precharge circuit to main circuit
        self.prch_inst_prefix = f"X{prch.name}"

        # Add precharge circuitry for all columns
        for col in range(self.num_cols):
            circuit.X(f"{prch.name}_{col}", prch.name, self.power_node, "PRE", f"BL{col}", f"BLB{col}")

        # Add precharge control signal (pulse voltage source)
        circuit.PulseVoltageSource(
            "PRE",
            "PRE",
            self.gnd_node,
            initial_value=self.vdd,
            pulsed_value=0 @ u_V,
            delay_time=0 @ u_ns,
            rise_time=self.t_rise,
            fall_time=self.t_fall,
            # pulse_width=self.t_pulse - 2 * self.t_rise, # different
            pulse_width=5e-09,
            period=self.t_period,
            dc_offset=self.vdd,
        )

        if self.choose_columnmux:
            # we temporarily fix this to 2  # fixed to 2-way mux
            self.mux_in = 2

            # Column Mux
            cmux = ColumnMux_simple(
                nmos_model_name=self.sram_config.column_mux.nmos_model.value,
                pmos_model_name=self.sram_config.column_mux.pmos_model.value,
                num_in=self.mux_in,
                base_nmos_width=self.sram_config.column_mux.nmos_width.value,
                base_pmos_width=self.sram_config.column_mux.pmos_width.value,
                length=self.sram_config.column_mux.length.value,
                w_rc=self.w_rc,
                sweep_columnmux=self.sweep_columnmux,
                # pi_res=self.pi_res, pi_cap=self.pi_cap,
                pmos_modle_choices=self.sram_config.senseamp.pmos_model.choices,
                nmos_modle_choices=self.sram_config.senseamp.nmos_model.choices,
            )
            circuit.subcircuit(cmux)  # Add column mux instance to main circuit
            self.cmux_inst_prefix = f"X{cmux.name}"

            # Add Column Mux for all columns
            for col in range(self.num_cols // self.mux_in):  # integer division; determines mux groups
                circuit.X(
                    f"{cmux.name}_{col}",
                    cmux.name,
                    self.power_node,
                    self.gnd_node,  # Power node and GND node
                    f"SA_IN{col}",  # SA inputs are Mux's outputs
                    f"SA_INB{col}",  # SA inputs are Mux's outputs
                    # SELect signal, high valid, #SEL = self.mux_in
                    *[f"SEL{i}" for i in range(self.mux_in)],
                    *[f"SELB{i}" for i in range(self.mux_in)],
                    # Inputs are BLs, #BLs  = self.mux_in
                    *[f"BL{i}" for i in range(col * self.mux_in, (col + 1) * self.mux_in)],
                    # Inputs are BLBs, #BLBs = self.mux_in
                    *[f"BLB{i}" for i in range(col * self.mux_in, (col + 1) * self.mux_in)],
                )
                # Set SEL signals: target column uses pulse source; others tied to ground
            # for i in range(self.mux_in):
            #     if i == target_col % self.mux_in:   # target column's group
            #         # Pulse setting of select signal is the same as WLE
            #         circuit.PulseVoltageSource(
            #             f'SEL_{i}', f'SEL{i}', self.gnd_node,
            #             initial_value=0 @ u_V, pulsed_value=self.vdd @ u_V,
            #             delay_time=self.t_pulse,
            #             rise_time=self.t_rise, fall_time=self.t_fall,
            #             pulse_width=self.t_pulse,
            #             period=self.t_period
            #         )
            #     else:
            #         circuit.V(f'SEL_{i}', f'SEL{i}', self.gnd_node, 0 @ u_V)

            for i in range(self.mux_in):
                if i == target_col % self.mux_in:  # target column's group
                    # Pulse setting of select signal is the same as WLE
                    circuit.PulseVoltageSource(f"SEL_{i}", f"SEL{i}", self.gnd_node, initial_value=0 @ u_V, pulsed_value=self.vdd @ u_V, delay_time=self.t_pulse, rise_time=self.t_rise, fall_time=self.t_fall, pulse_width=self.t_pulse, period=self.t_period)
                    circuit.PulseVoltageSource(f"SELB_{i}", f"SELB{i}", self.gnd_node, initial_value=self.vdd @ u_V, pulsed_value=0 @ u_V, delay_time=self.t_pulse, rise_time=self.t_rise, fall_time=self.t_fall, pulse_width=self.t_pulse, period=self.t_period, dc_offset=self.vdd)
                else:
                    circuit.V(f"SEL_{i}", f"SEL{i}", self.gnd_node, 0 @ u_V)
                    circuit.V(f"SELB_{i}", f"SELB{i}", self.gnd_node, 1.0 @ u_V)

        # Sense Amplifer
        sa = SenseAmp(
            nmos_model_name=self.sram_config.senseamp.nmos_model.value,
            pmos_model_name=self.sram_config.senseamp.pmos_model.value,
            base_nmos_width=self.sram_config.senseamp.nmos_width.value,
            base_pmos_width=self.sram_config.senseamp.pmos_width.value,
            length=self.sram_config.senseamp.length.value,
            w_rc=self.w_rc,  # default `w_rc` is False
            # pi_res=self.pi_res, pi_cap=self.pi_cap,
            sweep_senseamp=self.sweep_senseamp,
            pmos_modle_choices=self.sram_config.senseamp.pmos_model.choices,
            nmos_modle_choices=self.sram_config.senseamp.nmos_model.choices,
        )
        circuit.subcircuit(sa)  # Add sense amplifier instance to main circuit
        self.sa_inst_prefix = f"X{sa.name}"

        if self.choose_columnmux:
            # Add SA circuitry for all columns  # connect SA under each mux group
            for col in range(self.num_cols // self.mux_in):
                circuit.X(
                    f"{sa.name}_{col}",
                    sa.name,
                    self.power_node,
                    self.gnd_node,
                    "SAE",  # SA Enable signal
                    f"SA_IN{col}",
                    f"SA_INB{col}",  # Inputs
                    f"SA_Q{col}",
                    f"SA_QB{col}",  # Outputs
                )

        else:
            # Add SA circuitry for all columns  # connect SA under each mux group
            for col in range(self.num_cols):
                circuit.X(
                    f"{sa.name}_{col}",
                    sa.name,
                    self.power_node,
                    self.gnd_node,
                    "SAE",  # SA Enable signal
                    f"BL{col}",
                    f"BLB{col}",  # Inputs
                    f"SA_Q{col}",
                    f"SA_QB{col}",  # Outputs
                )

        # SA enable signal  # add sense amplifier enable signal
        circuit.PulseVoltageSource(
            "SAE",
            "SAE",
            self.gnd_node,
            initial_value=0 @ u_V,
            pulsed_value=self.vdd @ u_V,
            delay_time=2 * self.t_pulse,  # delayed one t_pulse relative to mux
            rise_time=self.t_rise,
            fall_time=self.t_fall,
            pulse_width=self.t_pulse,
            period=self.t_period,
        )

        return circuit

    def create_write_periphery(self, circuit: Circuit):  # Create write periphery circuitry
        """Create write periphery circuitry, writing `1`s into a row, write driver"""
        write_drv = WriteDriver(
            nmos_model_name=self.sram_config.write_driver.nmos_model.value,
            pmos_model_name=self.sram_config.write_driver.pmos_model.value,
            base_nmos_width=self.sram_config.write_driver.nmos_width.value,
            base_pmos_width=self.sram_config.write_driver.pmos_width.value,
            length=self.sram_config.write_driver.length.value,
            w_rc=self.w_rc,  # default `w_rc` is False
            # pi_res=self.pi_res, pi_cap=self.pi_cap,
            num_rows=self.num_rows,
            sweep_writedriver=self.sweep_writedriver,
            pmos_modle_choices=self.sram_config.senseamp.pmos_model.choices,
            nmos_modle_choices=self.sram_config.senseamp.nmos_model.choices,
        )

        circuit.subcircuit(write_drv)  # Add write driver instance to main circuit
        self.wdrv_inst_name = write_drv.name
        self.wdrv_inst_prefix = f"X{write_drv.name}"

        # Instantiate write drivers for all columns
        for col in range(self.num_cols):
            circuit.X(
                self.wdrv_inst_name + f"_{col}",
                write_drv.name,
                self.power_node,  # Power net
                self.gnd_node,  # Ground net
                "WE",  # Write Enable signal
                f"DIN{col}",  # Data In
                f"BL{col}",  # Connect to column bitline
                f"BLB{col}",  # Connect to column bitline bar
            )

        # Write `1` into all columns    # set all data inputs high (write 1)
        for col in range(self.num_cols):
            circuit.V(f"DIN{col}", f"DIN{col}", self.gnd_node, self.vdd @ u_V)
            # circuit.PulseVoltageSource(
            #     f'DIN{col}', f'DIN{col}', self.gnd_node,
            #     initial_value=0 @ u_V, pulsed_value=self.vdd,
            #     # data setup time
            #     delay_time=0,
            #     rise_time=self.t_rise, fall_time=self.t_fall,
            #     # data hold time = 2*t_delay time
            #     pulse_width=2*self.t_pulse + 2*self.t_delay,
            #     period=self.t_period)

        # WE: Write enable signal   # add write enable signal (pulse source)
        circuit.PulseVoltageSource(
            f"WE",
            f"WE",
            self.gnd_node,
            initial_value=0 @ u_V,
            pulsed_value=self.vdd,
            # data on BL/BLB setup time = t_delay time
            delay_time=0,
            rise_time=self.t_rise,
            fall_time=self.t_fall,
            # data on BL/BLB hold time = t_delay time
            pulse_width=2 * self.t_pulse + self.t_delay,
            period=self.t_period,
        )

        return circuit

    def create_single_cell_for_snm(self, circuit: Circuit, operation: str):
        """
        Create a single 6T SRAM cell for SNM measurement. Create cell-level static timing (SNM) analysis
        How to calculate SNM for 6T SRAM cell in SPICE?
        See: https://www.edaboard.com/threads/sram-snm-simulation-hspice.253224/
        """
        # Add U parameter
        # .param U=0
        circuit.parameter("U", 0)

        if self.custom_mc:
            # Instantiate 6T SRAM cell
            sbckt_6t_cell = Sram6TCellForYield(
                self.sram_config.sram_6t_cell.nmos_model.value[0],
                self.sram_config.sram_6t_cell.pmos_model.value,
                self.sram_config.sram_6t_cell.nmos_model.value[1],
                # This function returns a Dict of MOS models
                parse_spice_models(getattr(self.sram_config.global_config, f"pdk_path_{self.corner}")),
                self.sram_config.sram_6t_cell.nmos_width.value[0],
                self.sram_config.sram_6t_cell.pmos_width.value,
                self.sram_config.sram_6t_cell.nmos_width.value[1],
                self.sram_config.sram_6t_cell.length.value,
                w_rc=self.w_rc,
                pi_res=self.pi_res,
                pi_cap=self.pi_cap,
                disconnect=True,  # NOTE: Key argument to disconnect the internal data nodes!!
                suffix="_0_0",
                custom_mc=self.custom_mc,
                param_sweep=self.param_sweep,
            )
        else:
            # Instantiate 6T SRAM cell
            sbckt_6t_cell = Sram6TCell(self.sram_config.sram_6t_cell.nmos_model.value[0], self.sram_config.sram_6t_cell.pmos_model.value, self.sram_config.sram_6t_cell.nmos_model.value[1], self.sram_config.sram_6t_cell.nmos_width.value[0], self.sram_config.sram_6t_cell.pmos_width.value, self.sram_config.sram_6t_cell.nmos_width.value[1], self.sram_config.sram_6t_cell.length.value, w_rc=self.w_rc, pi_res=self.pi_res, pi_cap=self.pi_cap, disconnect=True, param_sweep=self.param_sweep, pmos_modle_choices=self.sram_config.sram_6t_cell.pmos_model.choices, nmos_modle_choices=self.sram_config.sram_6t_cell.nmos_model.choices)  # NOTE: Key argument to disconnect the internal data nodes!!
        # Add subcircuit definition to this testbench.
        circuit.subcircuit(sbckt_6t_cell)  # Add to main circuit
        circuit.X(sbckt_6t_cell.name, sbckt_6t_cell.name, self.power_node, self.gnd_node, "BL", "BLB", "WL")
        # internal node prefix in the SRAM cell
        self.cell_inst_prefix = "X" + sbckt_6t_cell.name

        if operation == "hold_snm":
            # For hold_snm measurement, keep WL low and add DC sources to Q/QB
            # For hold_snm, keep WL low and add DC sources at Q/QB
            circuit.V(f"WL_gnd", "WL", self.gnd_node, 0 @ u_V)

        elif operation == "read_snm":
            # For read_snm operation, keep WL high and add DC sources to Q/QB
            # For read_snm, keep WL high and add DC sources at Q/QB
            circuit.V(f"WL_vdd", "WL", self.gnd_node, self.vdd)
            circuit.V(f"BL_vdd", "BL", self.gnd_node, self.vdd)
            circuit.V(f"BLB_vdd", "BLB", self.gnd_node, self.vdd)
        elif operation == "write_snm":
            # For write_snm operation, keep WL high and add DC sources to Q/QB
            # For write_snm, keep WL high and add DC sources at Q/QB
            circuit.V(f"WL_vdd", "WL", self.gnd_node, self.vdd @ u_V)
            circuit.V(f"BL_vdd", "BL", self.gnd_node, self.vdd @ u_V)
            circuit.V(f"BLB_vdd", "BLB", self.gnd_node, 0 @ u_V)
        else:
            raise ValueError(f"Invalid operation: {operation}")

        # Add voltage-controlled source to obtain SNM
        # The grammar is insane, but it works, fuckin' PySpice,
        # e.g., EV1 V1 0 VOL='U+sqrt(2)*V(XSRAM_6T_CELL.QBD)
        circuit.VCVS("V1", "V1", "", self.gnd_node, "", **{"raw_spice": f"VOL='U+sqrt(2)*V({self.cell_inst_prefix}{self.heir_delimiter}QBD)'"})
        circuit.VCVS("V2", "V2", "", self.gnd_node, "", **{"raw_spice": f"VOL='-U+sqrt(2)*V({self.cell_inst_prefix}{self.heir_delimiter}QD)'"})
        circuit.VCVS("Q", f"{self.cell_inst_prefix}{self.heir_delimiter}Q", "", self.gnd_node, "", **{"raw_spice": f" VOL='1/sqrt(2)*U+1/sqrt(2)*V(V1)'"})
        circuit.VCVS("QB", f"{self.cell_inst_prefix}{self.heir_delimiter}QB", "", self.gnd_node, "", **{"raw_spice": f" VOL='-1/sqrt(2)*U+1/sqrt(2)*V(V2)'"})
        circuit.VCVS("VD", "VD", "", self.gnd_node, "", **{"raw_spice": f"VOL='ABS(V(V1)-V(V2))'"})
        # print("[DEBUG] Netlists for SRAM_6T_Cell_for_Yield")
        # print(circuit)
        # assert 0
        return circuit

    def data_init(self):  # Initialize data nodes; used in MC_testbench2
        init_dict = {}
        vq = self.vdd @ u_V if self.q_init_val else 0 @ u_V
        vqb = 0 @ u_V if self.q_init_val else self.vdd @ u_V

        # target_row = self.target_row
        # target_col = self.target_col

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # from utils import gen_unused_cells

                if self.gen_unused_cells or row == self.target_row or col == self.target_col:
                    # Data Q name is specified by cell_inst_prefix and cell location (row, col)
                    q_name = self.cell_inst_prefix + f"_{row}_{col}{self.heir_delimiter}Q"
                    qb_name = self.cell_inst_prefix + f"_{row}_{col}{self.heir_delimiter}QB"
                    init_dict[q_name] = vq
                    init_dict[qb_name] = vqb
                    # The target cell always stores '0' by default
                    if row == self.target_row and col == self.target_col:  # Target cell initial: Q=0, QB=1 (store 0)
                        init_dict[q_name] = 0 @ u_V
                        init_dict[qb_name] = self.vdd @ u_V

        # initiate the voltage of inputs of SAs, connecting to column muxes
        # Set sense amplifier inputs all to 1
        if self.choose_columnmux:
            for col in range(self.num_cols // self.mux_in):
                init_dict[f"SA_IN{col}"] = self.vdd @ u_V
                init_dict[f"SA_INB{col}"] = self.vdd @ u_V

        return init_dict

    def create_testbench(self, operation, target_row, target_col):
        """
        Create a testbench for the SRAM array.
        operation: 'read' or 'write'
        target_row: Row index of the target cell
        target_col: Column index of the target cell
        """
        self.target_row = target_row if target_row < self.num_rows else self.num_rows - 1
        self.target_col = target_col if target_col < self.num_cols else self.num_cols - 1

        circuit = Circuit(self.name)
        circuit.include(getattr(self.sram_config.global_config, f"pdk_path_{self.corner}"))

        # Power supply
        circuit.V(self.power_node, self.power_node, self.gnd_node, self.vdd @ u_V)
        circuit.V(self.gnd_node, self.gnd_node, circuit.gnd, 0 @ u_V)

        # if it is a SNM test   # operation contains 'snm'; operation determined in main2.py by mc_testbench.run_mc_simulation inputs
        if "snm" in operation:
            self.create_single_cell_for_snm(circuit, operation)
            # finish the circuit just return
            return circuit

        # Instantiate 6T SRAM array; create SRAM Core depending on MC usage
        if self.custom_mc:
            sbckt_6t_array = Sram6TCoreForYield(
                self.num_rows,
                self.num_cols,
                self.sram_config.sram_6t_cell.nmos_model.value[0],
                self.sram_config.sram_6t_cell.pmos_model.value,
                self.sram_config.sram_6t_cell.nmos_model.value[1],
                # This function returns a Dict of MOS models
                parse_spice_models(getattr(self.sram_config.global_config, f"pdk_path_{self.corner}")),
                self.sram_config.sram_6t_cell.nmos_width.value[0],
                self.sram_config.sram_6t_cell.pmos_width.value,
                self.sram_config.sram_6t_cell.nmos_width.value[1],
                self.sram_config.sram_6t_cell.length.value,
                w_rc=self.w_rc,
                pi_res=self.pi_res,
                pi_cap=self.pi_cap,
                param_sweep=self.param_sweep,
                target_row=self.target_row,
                target_col=self.target_col,
                gen_unused_cells=self.gen_unused_cells,
            )
        else:
            sbckt_6t_array = Sram6TCore(self.num_rows, self.num_cols, self.sram_config.sram_6t_cell.nmos_model.value[0], self.sram_config.sram_6t_cell.pmos_model.value, self.sram_config.sram_6t_cell.nmos_model.value[1], self.sram_config.sram_6t_cell.nmos_width.value[0], self.sram_config.sram_6t_cell.pmos_width.value, self.sram_config.sram_6t_cell.nmos_width.value[1], self.sram_config.sram_6t_cell.length.value, w_rc=self.w_rc, pi_res=self.pi_res, pi_cap=self.pi_cap, param_sweep=self.param_sweep, pmos_modle_choices=self.sram_config.sram_6t_cell.pmos_model.choices, nmos_modle_choices=self.sram_config.sram_6t_cell.nmos_model.choices, target_row=self.target_row, target_col=self.target_col, gen_unused_cells=self.gen_unused_cells)

        # Add subcircuit definition to this testbench.
        circuit.subcircuit(sbckt_6t_array)  # Add to main circuit

        # Instantiate the SRAM array.
        circuit.X(sbckt_6t_array.name, sbckt_6t_array.name, self.power_node, self.gnd_node, *[f"BL{i}" for i in range(self.num_cols)], *[f"BLB{i}" for i in range(self.num_cols)], *[f"WL{i}" for i in range(self.num_rows)])

        # internal node prefix in the SRAM cell
        self.arr_inst_prefix = f"X{sbckt_6t_array.name}"
        self.cell_inst_prefix = self.arr_inst_prefix + self.heir_delimiter + sbckt_6t_array.inst_prefix
        print(f"[DEBUG] self.arr_inst_prefix = {self.arr_inst_prefix}")
        print(f"[DEBUG] self.cell_inst_prefix = {self.cell_inst_prefix} of {self.name}")

        # Create decoder (outputs connect to wordline driver)
        self.create_decoder(circuit)

        # Set target row address
        n_bits = ceil(log2(self.num_rows)) if self.num_rows > 1 else 1
        for bit in range(n_bits):
            bit_val = (target_row >> bit) & 1
            node_name = f"A{bit}"
            if bit_val:
                circuit.PulseVoltageSource(f"ADDR_{bit}", node_name, self.gnd_node, initial_value=0 @ u_V, pulsed_value=self.vdd @ u_V, delay_time=5.0e-9, rise_time=self.t_rise, fall_time=self.t_fall, pulse_width=7.5e-9, period=self.t_period)  # 5ns after precharge begins  # keep active
            else:
                circuit.V(f"ADDR_{bit}", node_name, self.gnd_node, 0 @ u_V)

        # Create wordline driver (use decoder outputs as enable)
        self.create_wl_driver(circuit, target_row)

        # For read transient simulation, add pulse source to the array
        if operation == "read":
            self.create_read_periphery(circuit, target_col)
            # self.create_decoder(circuit, target_row)
            # self.create_wl_driver(circuit, target_row)
        # For write transient simulation, add pulse source to the array
        elif operation == "write":
            self.create_write_periphery(circuit)
            # self.create_decoder(circuit, target_row)
            # self.create_wl_driver(circuit, target_row)

        else:
            raise ValueError(f"Invalid test type {operation}. Use 'read' or 'write'")

        return circuit
