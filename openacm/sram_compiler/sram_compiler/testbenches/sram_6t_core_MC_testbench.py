import os
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF, u_A, u_mA

# Only for yield analysis
from utils import parse_mc_measurements, generate_mc_statistics, save_mc_results, process_simulation_data, parse_spice_models, write_spice_models  # type: ignore
from sram_compiler.testbenches.sram_6t_core_testbench import Sram6TCoreTestbench  # type: ignore
import numpy as np
import csv
from PySpice.Spice.Netlist import SubCircuitFactory


class Sram6TCoreMcTestbench(Sram6TCoreTestbench):
    def __init__(self, sram_config, w_rc=False, pi_res=10 @ u_Ohm, pi_cap=0.001 @ u_pF, vth_std=0.05, use_mc=False, custom_mc=False, param_sweep=False, sweep_precharge=False, sweep_senseamp=True, sweep_wordlinedriver=False, sweep_columnmux=False, sweep_writedriver=False, sweep_decoder=False, coner="TT", choose_columnmux=True, q_init_val=0, sim_path="sim", gen_unused_cells=False):
        """
        Initialize Monte Carlo testbench
        Args:
            sram_config: SRAM config object (includes all design parameters)
            w_rc: Whether to add RC networks
            pi_res: PI model resistance
            pi_cap: PI model capacitance
            vth_std: Threshold voltage standard deviation
            use_mc: Enable Monte Carlo randomness
            custom_mc: Use custom MC parameters
            q_init_val: Initial Q value
            sim_path: Path for saving simulation results
            gen_unused_cells: Generate unused cells (False uses equivalent SRAM cell)
        """
        super().__init__(sram_config, w_rc, pi_res, pi_cap, (custom_mc and use_mc), param_sweep, sweep_precharge, sweep_senseamp, sweep_wordlinedriver, sweep_columnmux, sweep_writedriver, sweep_decoder, coner, choose_columnmux, q_init_val, gen_unused_cells)  # Parent class
        self.use_mc = use_mc
        self.choose_columnmux = choose_columnmux
        self.coner = coner
        self.sweep_decoder = sweep_decoder
        self.sweep_writedriver = sweep_writedriver
        self.sweep_columnmux = sweep_columnmux
        self.sweep_wordlinedriver = sweep_wordlinedriver
        self.sweep_senseamp = sweep_senseamp
        self.sweep_precharge = sweep_precharge
        self.param_sweep = param_sweep
        self.sram_config = sram_config
        self.vth_std = vth_std
        num_rows = sram_config.global_config.num_rows
        num_cols = sram_config.global_config.num_cols
        self.name = f"SRAM_6T_CORE_{num_rows}x{num_cols}_MC_TB"  # Set testbench name based on rows/cols
        self.sim_path = sim_path
        os.makedirs(self.sim_path, exist_ok=True)

    def create_mc_model_file(self):
        """Create temporary model file with Monte Carlo variations"""
        # pdk_path = self.sram_config.global_config.pdk_path
        pdk_path = getattr(self.sram_config.global_config, f"pdk_path_{self.corner}")
        model_dict = parse_spice_models(pdk_path)

        for m in model_dict.keys():

            # Get parameters for the model_name
            param_dict = model_dict[m]["parameters"]

            for param in param_dict.keys():
                # substitute the default values with user-defined parameters
                if param in ["vth0", "u0", "voff"]:
                    val = param_dict[param]
                    param_dict[param] = f"{{AGAUSS({val}, {abs(val) * self.vth_std:.5f}, 1)}}"
                    # Add Gaussian random variables for key parameters (vth0, u0, voff)
        # Generate a modified model library
        temp_model_path = os.path.join(self.sim_path, "tmp_mc.spice")

        print(model_dict)

        # Write the model cards back to temporary file
        write_spice_models(model_dict, temp_model_path)

        return temp_model_path

    def create_testbench(self, operation, target_row=0, target_col=0):  # Define subclass create_testbench method
        """Create testbench with Monte Carlo models"""
        circuit = super().create_testbench(operation, target_row, target_col)
        # Call parent class create_testbench
        # Standard MC needs a model lib with variables,
        # otherwise, process parameters are defined by user
        if (not self.custom_mc) and self.use_mc:
            # When custom MC is not used
            # Replace original included model lib with a new path containing random variables
            circuit._includes[0] = self.create_mc_model_file()

        return circuit

    def add_meas_and_print(self, simulator, init_cond, operation):
        # Internal nodes' names of the target cell
        target_node_q = self.cell_inst_prefix + f"_{self.target_row}_{self.target_col}{self.heir_delimiter}Q"
        target_node_qb = self.cell_inst_prefix + f"_{self.target_row}_{self.target_col}{self.heir_delimiter}QB"
        # Get internal node names of the target cell (Q and QB)
        if operation == "hold_snm" or operation == "read_snm" or operation == "write_snm":
            # Initial V(BL) and V(BLB) for the  cell
            init_cond = {}
            init_cond[f"BL"] = self.vdd @ u_V  # Set initial bitline voltage
            init_cond[f"BLB"] = self.vdd @ u_V
            simulator.initial_condition(**init_cond)  # Apply initial conditions
            simulator.measure("DC", "MAXVD", "MAX V(VD)")  # Measure maximum diagonal voltage
            simulator.measure("DC", operation.upper(), f"PARAM='1/sqrt(2)*MAXVD'")  # Compute static noise margin
            # Add print for SNM
            simulator.circuit.raw_spice += f".PRINT DC FORMAT=NOINDEX {{U}} V(V1) V(V2)\n"

        # The read operation
        elif operation == "read":
            # .ic conditions
            for col in range(self.num_cols):
                # Initial V(BL) and V(BLB) for all columns
                init_cond[f"BL{col}"] = 0 @ u_V
                init_cond[f"BLB{col}"] = 0 @ u_V
                # init_cond[f'Q{col}'] = self.vdd @ u_V
                # init_cond[f'QB{col}'] = 0 @ u_V

            simulator.initial_condition(**init_cond)

            # Measurements for precharge delay (TPRCH), defined by the time from PRE assertion to V(BL)=0.9*VDD
            # Measure precharge delay (TPRCH): time from PRE assert to V(BL)=0.9*VDD
            simulator.measure("TRAN", "TPRCH", f"TRIG V(PRE)={self.half_vdd} FALL=1 " + f"TARG V(BL{self.target_col})={float(self.vdd) * 0.9} RISE=1")  # modified for Xyce

            # Measurements for wl driver delay (TWLDRV), defined as the time from the WLE assertion to V(WL)=VDD/2
            # Measure decoder and WL driver delays; defined to V(WL)=VDD/2
            simulator.measure("TRAN", "TDECODER", f"TRIG V(A0)={self.half_vdd} RISE=1 " + f"TARG V(DEC_WL{self.target_row})={self.half_vdd} RISE=1")
            simulator.measure("TRAN", "TWLDRV", f"TRIG V(DEC_WL{self.target_row})={self.half_vdd} RISE=1 " + f"TARG V(WL{self.target_row})={self.half_vdd} RISE=1")

            # Add measurements for read delay (TREAD)
            # which is defined as the time from the WL rise to BL swing to VDD/2
            simulator.measure("TRAN", "TWL", f"WHEN V(WL{self.target_row})={self.half_vdd} RISE=1 ")  # modified for Xyce
            # Define minimum Vswing = 250mV
            vswing = 0.25
            simulator.measure("TRAN", "TBL", f"WHEN V(BL{self.target_col})='V(BLB{self.target_col})-{vswing}' FALL=1")
            simulator.measure("TRAN", "TSWING", f"PARAM='TBL-TWL'")

            # Measurements for SA delay (TSA), defined as the time from the SAE assertion to V(Q)=VDD/2
            # Measure SA delay (TSA): time from SAE assert to V(Q)=VDD/2
            simulator.measure("TRAN", "TSA", f"TRIG V(SAE)={self.half_vdd} RISE=1 " + f"TARG V(SA_Q{self.target_col // self.mux_in})={float(self.vdd) * 0.1} FALL=1")

            # Add measurements for average power, static power and dynamic power
            simulator.measure("TRAN", "PAVG", f"AVG {{V(VDD)*I(VVDD)}} FROM={float(0.0 @ u_ns)} TO={float(14.0 @ u_ns)}")
            # simulator.measure(
            #     'TRAN', 'PDYN',
            #     f'AVG {{V(VDD)*I(VVDD)}} FROM={float(4.0 @ u_ns)} TO={float(6.0 @ u_ns)}'
            # )
            simulator.measure("TRAN", "PSTC", f"AVG {{V(VDD)*I(VVDD)}} FROM={float(6.0 @ u_ns)} TO={float(10.0 @ u_ns)}")

            # Add print for read operation
            simulator.circuit.raw_spice += f".PRINT TRAN FORMAT=NOINDEX V(SAE) V(WL{self.target_row}) " + f"V(BL{self.target_col}) V(BLB{self.target_col}) " + f"V({target_node_q}) V({target_node_qb}) \n"
            if self.choose_columnmux:
                simulator.circuit.raw_spice += f".PRINT TRAN V(SA_IN{self.target_col // self.mux_in}) " + f"V(SA_INB{self.target_col // self.mux_in})\n"
            simulator.circuit.raw_spice += f".PRINT TRAN V(SA_Q{self.target_col // self.mux_in}) " + f"V(SA_QB{self.target_col // self.mux_in})\n"
        # The write operation
        elif operation == "write":
            # .ic conditions
            for col in range(self.num_cols):
                # Initial V(BL) and V(BLB) for all columns
                init_cond[f"BL{col}"] = 0 @ u_V
                init_cond[f"BLB{col}"] = 0 @ u_V

            simulator.initial_condition(**init_cond)
            # Wordline driver delay
            # Measurements for wl driver delay (TWLDRV), defined as the time from the WLE assertion to V(WL)=VDD/2
            simulator.measure("TRAN", "TDECODER", f"TRIG V(A0)={self.half_vdd} RISE=1 " + f"TARG V(DEC_WL{self.target_row})={self.half_vdd} RISE=1")
            simulator.measure("TRAN", "TWLDRV", f"TRIG V(DEC_WL{self.target_row})={self.half_vdd} RISE=1 " + f"TARG V(WL{self.target_row})={self.half_vdd} RISE=1")
            # Write driver delay
            # Measurements for write driver delay (TWDRV), defined as the time from the WE assertion to V(BL)=VDD/2
            simulator.measure("TRAN", "TWDRV", f"TRIG V(WE)={self.half_vdd} RISE=1 " + f"TARG V(BL{self.target_col})={self.half_vdd} RISE=1")
            # Write delay
            # Measurements for write delay (TWRITE_Q/QB),
            # which is defined as the time from the WL rise to data Q rise to 90% VDD.
            simulator.measure("TRAN", "TWRITE_Q", f"TRIG V(WL{self.target_row})={self.half_vdd} RISE=1", f"TARG V({target_node_q})={float(self.vdd) * 0.9:.2f} RISE=1")
            simulator.measure("TRAN", "TWRITE_QB", f"TRIG V(WL{self.target_row})={self.half_vdd} RISE=1", f"TARG V({target_node_qb})={float(self.vdd) * 0.1:.2f} FALL=1")

            # Add measurements for average power, static power and dynamic power
            simulator.measure("TRAN", "PAVG", f"AVG {{V(VDD)*I(VVDD)}} FROM={float(0.0 @ u_ns)} TO={float(14 @ u_ns)}")
            # simulator.measure(
            #     'TRAN', 'PDYN',
            #     f'MIN {{V(VDD)*I(VVDD)}} FROM={float(4.0 @ u_ns)} TO={float(6.0 @ u_ns)}'
            # )
            simulator.measure("TRAN", "PSTC", f"AVG {{V(VDD)*I(VVDD)}} FROM={float(6.0 @ u_ns)} TO={float(10.0 @ u_ns)}")
            # Add print for write operation
            simulator.circuit.raw_spice += f".PRINT TRAN FORMAT=NOINDEX V(WE) V(WL{self.target_row}) V(BL{self.target_col})" + f" V(BLB{self.target_col}) V({target_node_q}) V({target_node_qb})\n"
        else:
            raise ValueError(f"Invalid operation: {operation}")

    def add_xyce_options(self, circuit, mc_runs, operation):
        """Add options for Xyce"""
        pass

    def add_analysis(self, circuit, operation, num_mc):
        """Add .DC / .TRAN analysis: DC sweep / transient analysis"""
        if "snm" in operation:
            u_tmp = self.vdd / np.sqrt(2)
            circuit.raw_spice += f".DC U -{u_tmp:.2f} {u_tmp:.2f} 0.001\n"
        else:
            circuit.raw_spice += f".TRAN {float(self.t_step):.4e} {float(self.t_period):.4e}\n"
            # Timing interval option is set only in .TRAN analysis.
            circuit.raw_spice += f".OPTIONS OUTPUT INITIAL_INTERVAL={float(self.t_step):.4e}\n"

        if self.use_mc:
            # Whether we use custom MC
            if self.custom_mc:
                # Sweep the each row of the `table`
                circuit.raw_spice += f".STEP data=table\n"
            else:
                if self.param_sweep:
                    circuit.raw_spice += f".STEP data=SRAM_6T_CELL\n"
                if self.sweep_precharge:
                    circuit.raw_spice += f".STEP data=PRECHARGE\n"
                if self.sweep_senseamp:
                    circuit.raw_spice += f".STEP data=SENSEAMP\n"
                if self.sweep_wordlinedriver:
                    circuit.raw_spice += f".STEP data=WORDLINEDRIVER\n"
                if self.sweep_columnmux:
                    circuit.raw_spice += f".STEP data=COLUMNMUX\n"
                if self.sweep_writedriver:
                    circuit.raw_spice += f".STEP data=WRITEDRIVER\n"
                if self.sweep_decoder:
                    circuit.raw_spice += f".STEP data=DECODER\n"
                if not self.param_sweep and not self.sweep_precharge and not self.sweep_senseamp and not self.sweep_wordlinedriver and not self.sweep_columnmux and not self.sweep_writedriver and not self.sweep_decoder:
                    # Use build-in sampling method in Xyce
                    circuit.raw_spice += f".SAMPLING useExpr=true\n.options samples numsamples={num_mc}\n"
                    pass

        print(f"[DEBUG] Custom_MC={self.custom_mc}, numsamples={num_mc}")

    def get_table_head(self):
        return self.table_head

    def gen_process_params(self, circuit: SubCircuitFactory, operation: str, num_mc: int, vars: np.array = None):
        """Add process parameters' data table for STEP
            Generate process parameter data table
        Args:
        ---
            circuit (SubCircuitFactory): simulator's circuits
            operation (string): can be `read`, `write`, `hold_snm`, `read_snm`, `write_snm`
            num_mc (int): number of MC runs
            vars (numpy.ndarray): parameters in data table
        """
        # Order of transistors in bitcell can not be changed
        mos_names = ["PGL", "PGR", "PDL", "PUL", "PDR", "PUR"]
        # This version only takes 3 params into consideration
        param_names = ["vth0", "u0", "voff"]
        self.table_head = ".data table\n+ "
        table_content = "\n"
        num_params = 0

        # Define params
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Only 1 cell's params are generated
                if ("snm" in operation) and (row > 0 or col > 0):
                    continue
                # Each transistor has 6 process variables
                for mos in mos_names:
                    for param in param_names:
                        if mos in ["PUL", "PUR"]:
                            # Parameter definitions for PMOS
                            circuit.raw_spice += f".param {param}_{self.sram_config.sram_6t_cell.pmos_model.value}_{mos}_{row:d}_{col:d}=0.0\n"
                            # Data table head
                            self.table_head += f"{param}_{self.sram_config.sram_6t_cell.pmos_model.value}_{mos}_{row:d}_{col:d} "
                        elif mos in ["PGL", "PGR"]:
                            circuit.raw_spice += f".param {param}_{self.sram_config.sram_6t_cell.nmos_model.value[1]}_{mos}_{row:d}_{col:d}=0.0\n"
                            # Data table head
                            self.table_head += f"{param}_{self.sram_config.sram_6t_cell.nmos_model.value[1]}_{mos}_{row:d}_{col:d} "
                        else:
                            # Parameter definitions for NMOS
                            circuit.raw_spice += f".param {param}_{self.sram_config.sram_6t_cell.nmos_model.value[0]}_{mos}_{row:d}_{col:d}=0.0\n"
                            # Data table head
                            self.table_head += f"{param}_{self.sram_config.sram_6t_cell.nmos_model.value[0]}_{mos}_{row:d}_{col:d} "

                        num_params += 1
        # Just for debugging
        if vars is None:
            vars = [0.4106, 0.045, -0.13, 0.4106, 0.045, -0.13, 0.4106, 0.045, -0.13, -0.3842, 0.02, -0.126, 0.4106, 0.045, -0.13, -0.3842, 0.02, -0.126]  # PGL  # PGR  # PDL  # PUL  # PDR  # PUR

            if operation == "read" or operation == "write":
                vars = np.array([vars * self.num_rows * self.num_cols])
                vars = np.repeat(vars, num_mc, axis=0)
            else:
                vars = np.array([vars])
                vars = np.repeat(vars, num_mc, axis=0)

            print(f"[DEBUG] Generated vars.shape={vars.shape}")
        else:
            assert num_mc == vars.shape[0], f"num_mc={num_mc} mismatches {vars.shape[0]} row number in the data table"
            print(f"[DEBUG] Input vars.shape={vars.shape}")

        assert len(vars.shape) == 2
        assert num_params == vars.shape[1], f"num_params={num_params} mismatches {vars.shape[1]} column number in the data table"

        table_content += "\n".join(["+ " + " ".join([f"{x:.4f}" for x in row]) for row in vars])

        # Generate and run Xyce netlist
        table_path = os.path.join(self.sim_path, f"mc_{operation}_{self.num_rows}x{self.num_cols}_table.data")
        with open(table_path, "w") as f:
            f.write(self.table_head + table_content)
        circuit.include(table_path)
        print(f"[DEBUG] Data table has been saved to {table_path}")

    def gen_param_sweep_6T_CELL(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for bitcell width and length
        """
        #   # Add include file
        # include_path = '/home/majh/OpenYield/sim/mc_read_6T_CELL.data'
        # circuit.raw_spice += f'.include "{include_path}"\n'
        # Define parameter names to add
        param_names = ["pmos_width_pu", "nmos_width_pd", "nmos_width_pg", "length"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_6t_cell.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check header for required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])
        # Build data table content
        table_content = f".data SRAM_6T_CELL\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions in netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 4, f"Row {i} has {len(row)} values, expected 4"

        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_6T_CELL.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    def gen_param_sweep_precharge(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for precharge unit width and length
        """
        #   # Add include file
        # include_path = '/home/majh/OpenYield/sim/mc_read_6T_CELL.data'
        # circuit.raw_spice += f'.include "{include_path}"\n'
        # Define parameter names to add
        param_names = ["pmos_width_precharge", "length_precharge"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_precharge.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check if header contains required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])

        # Build data table contents
        table_content = f".data PRECHARGE\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions to netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 2, f"Row {i} has {len(row)} values, expected 2"
        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_PRECHARGE.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    def gen_param_sweep_senseamp(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for sense amplifier width and length
        """
        #   # Add include file
        # include_path = '/home/majh/OpenYield/sim/mc_read_6T_CELL.data'
        # circuit.raw_spice += f'.include "{include_path}"\n'
        # Define parameter names to add
        param_names = ["pmos_width_senseamp", "nmos_width_senseamp", "length_senseamp"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_senseamp.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check if header contains required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])
        # Build data table contents
        table_content = f".data SENSEAMP\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions to netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 3, f"Row {i} has {len(row)} values, expected 3"

        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_SENSEAMP.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    def gen_param_sweep_wordlinedriver(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for wordline driver width and length
        """

        # Define parameter names to add
        param_names = ["pmos_width_wld_nandp", "nmos_width_wld_nandn", "pmos_width_wld_invp", "nmos_width_wld_invn", "length_wld"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_wordlinedriver.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check if header contains required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])
        # Build data table contents
        table_content = f".data WORDLINEDRIVER\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions to netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 5, f"Row {i} has {len(row)} values, expected 5"

        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_WORDLINEDREIVER.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    def gen_param_sweep_columnmux(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for column mux width and length
        """
        #   # Add include file
        # Define parameter names to add
        param_names = ["pmos_width_mux", "nmos_width_mux", "length_mux"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_columnmux.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check if header contains required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])
        # Build data table contents
        table_content = f".data COLUMNMUX\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions to netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 3, f"Row {i} has {len(row)} values, expected 3"

        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_COLUMNMUX.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    def gen_param_sweep_writedriver(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for write driver width and length
        """
        #   # Add include file
        # Define parameter names to add
        param_names = ["pmos_width_wrd", "nmos_width_wrd", "length_wrd"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_writedriver.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check if header contains required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])
        # Build data table contents
        table_content = f".data WRITEDRIVER\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions to netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 3, f"Row {i} has {len(row)} values, expected 3"

        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_WRITEDRIVER.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    def gen_param_sweep_decoder(self, circuit: SubCircuitFactory, operation: str, vars: np.array = None):
        """Add parameter sweep for width and length variations
        Add parameter sweep for decoder width and length
        """
        #   # Add include file
        # Define parameter names to add
        param_names = ["pmos_width_decoder_nandp", "nmos_width_decoder_nandn", "pmos_width_decoder_invp", "nmos_width_decoder_invn", "length_decoder"]
        csv_path = "sram_compiler/param_sweep_data/param_sweep_decoder.csv"
        if csv_path is None:
            raise ValueError("csv_path parameter must be specified")
        vars = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # Check if header contains required columns
            missing = set(param_names) - set(reader.fieldnames or [])
            if missing:
                raise KeyError(f"CSV missing columns: {missing}")
            for row in reader:
                vars.append([float(row[p]) for p in param_names])
        # Build data table contents
        table_content = f".data DECODER\n"
        table_content += "+ " + " ".join(param_names) + "\n"

        # Add parameter definitions to netlist
        for param in param_names:
            circuit.raw_spice += f".param {param}=0.0\n"

        # # Default values for debug mode
        # if vars is None:
        #     # Default parameter values [pmos_width_pu, nmos_width_pd, nmos_width_pg, length]
        #     vars = [[0.27e-6,0.18e-6,0.27e-6,0.09e-6,5.0e-8] ,[0.30e-6,0.20e-6,0.30e-6,0.25e-6,5.0e-8]]

        #     print(f"[DEBUG]  Using default vars with {len(vars)} rows")

        # Validate parameter dimensions
        for i, row in enumerate(vars):
            assert len(row) == 5, f"Row {i} has {len(row)} values, expected 5"

        for row in vars:
            # Format using scientific notation
            formatted_row = [f"{x:.3e}" for x in row]
            table_content += "+ " + " ".join(formatted_row) + "\n"

        # Generate and save parameter table file
        include_path = os.path.join(self.sim_path, f"param_sweep_DECODER.data")
        with open(include_path, "w") as f:
            f.write(table_content)

        # Include parameter table in netlist
        circuit.include(include_path)
        print(f"[DEBUG] Parameter sweep table saved to {include_path}")

    class SimulatorWrapper:
        """Simple wrapper to avoid invoking PySpice's internal simulator"""

        def __init__(self, circuit):
            self.circuit = circuit

        def initial_condition(self, **conditions):
            """Add initial conditions to circuit"""
            for node, value in conditions.items():
                self.circuit.raw_spice += f".IC V({node})={float(value)}\n"

        def measure(self, analysis_type, name, expression):
            """Add measurement statement to circuit"""
            self.circuit.raw_spice += f".MEASURE {analysis_type} {name} {expression}\n"

    def run_mc_simulation(self, operation="read", target_row=0, target_col=0, mc_runs=100, temperature=27, vars=None):
        """Run Xyce Monte Carlo simulation"""
        circuit = self.create_testbench(operation, target_row, target_col)
        simulator = circuit.simulator(temperature=temperature, nominal_temperature=27)  # Passed via **kwargs
        # simulator = self.create_testbench(operation, target_row, target_col).simulator()

        # if self.param_sweep:
        #     mc_runs=num_sweep
        # Add some Xyce related commands
        self.add_analysis(simulator.circuit, operation, mc_runs)

        # Add measurements according to the operation
        self.add_meas_and_print(simulator, self.data_init(), operation)

        # Add process parameters
        if self.use_mc:
            if self.custom_mc:
                self.gen_process_params(simulator.circuit, operation, vars=vars, num_mc=mc_runs)
            else:
                if self.param_sweep:
                    self.gen_param_sweep_6T_CELL(simulator.circuit, operation, vars=vars)
                if self.sweep_precharge:
                    self.gen_param_sweep_precharge(simulator.circuit, operation, vars=vars)
                if self.sweep_senseamp:
                    self.gen_param_sweep_senseamp(simulator.circuit, operation, vars=vars)
                if self.sweep_wordlinedriver:
                    self.gen_param_sweep_wordlinedriver(simulator.circuit, operation, vars=vars)
                if self.sweep_columnmux:
                    self.gen_param_sweep_columnmux(simulator.circuit, operation, vars=vars)
                if self.sweep_writedriver:
                    self.gen_param_sweep_writedriver(simulator.circuit, operation, vars=vars)
                if self.sweep_decoder:
                    self.gen_param_sweep_decoder(simulator.circuit, operation, vars=vars)

        print("[DEBUG] Printing generated netlists...")
        print(simulator)
        init = "_q1" if self.q_init_val > 0 else ""

        # Generate and run Xyce netlist
        tb_path = os.path.join(self.sim_path, f"mc_{operation}_{self.num_rows}x{self.num_cols}_rc{self.w_rc:d}{init}_tb.sp")

        with open(tb_path, "w") as f:
            f.write(str(simulator))
        # assert 0
        # Execute Xyce and parse results
        try:
            # if True:
            import subprocess

            # command: Xyce <netlist>
            print("[DEBUG] Xyce running ...")
            result = subprocess.run(
                # ['hspice', '-i', tb_path, '-o', self.sim_path],
                ["Xyce", tb_path, "-o", tb_path],
                capture_output=True,
                text=True,
                check=False,
            )
            # Print error message
            # print(f"[DEBUG] Xyce error:")
            # print(result.stderr)

            if result.returncode != 0:
                print(f"[ERROR] Simulation failed: {result.stdout}")
                print(f"Xyce error:\n{result.stderr}, please check the log file {tb_path.replace('.sp', '.lis')}.")
                # exit(0)
                raise RuntimeError(f"Xyce error:\n{result.stderr}, please check the log file {tb_path.replace('.sp', '.lis')}.")
            else:
                print("[DEBUG] Simulation run successfully.")

        except Exception as e:
            print(f"[ERROR] Simulation failed: {e}")

        finally:
            # plot waveforms of signals in `.PRINT`
            process_simulation_data(
                prn_path=tb_path + ".prn",
                num_mc=mc_runs,
                output=f"{self.sim_path}/mc_{operation}_{self.num_rows}x{self.num_cols}_waveform.png",
            )

            # Get all `.mtX` or `.msX` files from MC
            mc_df = parse_mc_measurements(
                netlist_prefix=tb_path,
                file_suffix="ms" if "snm" in operation else "mt",
                num_runs=mc_runs,
                # value_threshold=1e-9
            )
            print("[DEBUG] Printing mc_df")
            print(mc_df)
            # assert 0
            # Generate statistics
            stats = generate_mc_statistics(mc_df)
            # Save results
            save_mc_results(mc_df, stats, data_file=tb_path.replace(".sp", ".data.csv"), stats_file=tb_path.replace(".sp", ".stats.csv"))

            # Reture the performance metrics for yield analysis and sizing optimization
            # important: adjust the rate multiplier here; dynamic power is currently spread across 14ns of sim time while actual clock is 200MHz
            if operation == "write":
                PAVG_temp = mc_df["PAVG"].to_numpy()
                PSTC_temp = mc_df["PSTC"].to_numpy()
                PDYN_temp = (PAVG_temp - PSTC_temp) * 14 / 5
                TIME_temp = mc_df["TDECODER"].to_numpy() + mc_df["TWDRV"].to_numpy() + mc_df["TWLDRV"].to_numpy() + mc_df["TWRITE_Q"].to_numpy()
                return TIME_temp, PAVG_temp, PSTC_temp, PDYN_temp
                # return mc_df['TWRITE_Q'].to_numpy(), , mc_df['PSTC'].to_numpy()
            elif operation == "read":
                PAVG_temp = mc_df["PAVG"].to_numpy()
                PSTC_temp = mc_df["PSTC"].to_numpy()
                PDYN_temp = (PAVG_temp - PSTC_temp) * 14 / 5
                TIME_temp = mc_df["TDECODER"].to_numpy() + mc_df["TPRCH"].to_numpy() + mc_df["TWLDRV"].to_numpy() + mc_df["TSWING"].to_numpy()
                return TIME_temp, PAVG_temp, PSTC_temp, PDYN_temp
                # return mc_df['TSWING'].to_numpy(), mc_df['PAVG'].to_numpy(), mc_df['PSTC'].to_numpy()
            elif operation == "hold_snm":
                return mc_df["HOLD_SNM"].to_numpy()
            elif operation == "read_snm":
                return mc_df["READ_SNM"].to_numpy()
            elif operation == "write_snm":
                return mc_df["WRITE_SNM"].to_numpy()
            else:
                raise KeyError(f"Unkonwn operation {operation}")
