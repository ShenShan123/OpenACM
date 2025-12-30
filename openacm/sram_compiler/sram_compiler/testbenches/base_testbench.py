import os
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF


# from utils import plot_results, measure_delay
# from utils import parse_mt0, analyze_mt0


class BaseTestbench:  # Base testbench class
    def __init__(self, tb_name, vdd, pdk_path):
        self.name = tb_name
        self.pdk_path = pdk_path

        if os.path.exists(pdk_path):  # Verify PDK file exists
            print(f"[DEBUG] Transistor model file found: {pdk_path}")
        else:
            raise FileNotFoundError(f"Transistor model file not found: {pdk_path}")

        # self.nmos_model_name = nmos_model_name
        # self.pmos_model_name = pmos_model_name
        # The power / ground node
        self.power_node = "VDD"
        self.gnd_node = "VSS"
        # Supply voltage
        self.vdd = vdd
        self.half_vdd = float(self.vdd) * 0.5
        ## need to be changed in create_testbench
        self.data_node_prefix = "X"

        # Define timing parameters for pulse sources
        self.t_rise = 0.1 @ u_ns  # Rise time
        self.t_fall = 0.1 @ u_ns  # Fall time
        self.t_pulse = 6 @ u_ns  # Pulse width
        self.t_period = 20 @ u_ns  # Period
        self.t_delay = 1 @ u_ns  # shift for write signal
        self.t_step = self.t_rise * 0.1

    def set_vdd(self, value):  # Allow modifying supply voltage; also update half VDD
        self.vdd = value
        self.half_vdd = float(self.vdd) / 2

    # Allow dynamic modification of all key timing parameters
    def set_timing_parameters(self, t_rise, t_fall, t_pulse, t_period, t_delay):
        self.t_rise = t_rise
        self.t_fall = t_fall
        self.t_pulse = t_pulse
        self.t_period = t_period
        self.t_delay = t_delay

    def create_read_periphery(self, circuit):  # Must be implemented by subclass
        """Create read periphery circuitry"""
        raise NotImplementedError("create_read_periphery method not implemented")

    def create_write_periphery(self, circuit):  # Must be implemented by subclass
        """Create write periphery circuitry"""
        raise NotImplementedError("create_write_periphery method not implemented")

    def create_testbench(self):
        """
        Override this method to create a testbench for the circuit array.
        Create a testbench for the circuit array.
        """
        circuit = Circuit(self.name)
        circuit.include(self.pdk_path)

        # Power supply: add VDD and ground
        circuit.V(self.power_node, self.power_node, self.gnd_node, self.vdd @ u_V)
        circuit.V(self.gnd_node, self.gnd_node, circuit.gnd, 0 @ u_V)

        return circuit

    def run_simulation(self):  # Run SPICE simulation
        """
        Override this method to run a specific test.
        Run specified test and return results
        """
        circuit = self.create_testbench()  # Create circuit testbench
        simulator = circuit.simulator()

        # Initialize all internal data nodes (Q and QB) in all cells to 0V
        initial_conditions = {}
        simulator.initial_condition(**initial_conditions)

        # Run transient simulation with 0.01 ns step; end at t_period
        analysis = simulator.transient(step_time=0.01 @ u_ns, end_time=self.t_period)

        return {
            "success": True,
            "analysis": analysis,
        }
