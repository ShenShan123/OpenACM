import numpy as np

# from scipy.optimize import curve_fit
# from scipy import integrate
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_V, u_A, u_Ohm, u_F, u_H
from sympy import Q, im
from urllib3 import Retry
from sram_compiler.subcircuits.sram_6t_core_for_yield import Sram6TCell
from config import GlobalConfig
import yaml
import matplotlib.pyplot as plt

image_base_path = "equivalent_modeling/images/"


def last_proportion_mean(arr, p=1 / 6):
    n = max(1, int(len(arr) * p))
    return np.mean(arr[-n:])


class SRAMCellParasiticTester:
    def __init__(self, config=None, corner="TT", pd_nmos_model="NMOS_VTH", pu_pmos_model="PMOS_VTG", pg_nmos_model="NMOS_VTH", pd_width=1.8e-7, pu_width=1.2e-7, pg_width=0.7e-7, length=74.0e-9, q_init_val=0):
        # Store parameters
        self.corner = corner
        self.pd_nmos_model = pd_nmos_model
        self.pu_pmos_model = pu_pmos_model
        self.pg_nmos_model = pg_nmos_model
        self.pd_width = pd_width
        self.pu_width = pu_width
        self.pg_width = pg_width
        self.length = length
        self.q_init_val = q_init_val

        # Load or use provided configuration
        if config is None:
            try:
                with open("config.yaml", "r") as f:
                    config_data = yaml.safe_load(f)
                self.config = GlobalConfig(config_data)
            except FileNotFoundError:
                # Use default config
                self.config = GlobalConfig({})
        else:
            self.config = config

        # 瞬态仿真参数
        self.step_time = 1e-14
        self.end_time = 10000 * self.step_time
        self.rise_time = self.step_time * 500
        self.hold_time = 5000 * self.step_time

        # Initialize circuit
        self._init_circuit()

    def _init_circuit(self):
        self.circuit = Circuit("SRAM_Cell_Test")
        pdk_path = getattr(self.config, f"pdk_path_{self.corner}")
        self.circuit.include(pdk_path)

        # Create SRAM cell instance
        sram_cell = Sram6TCell(pd_nmos_model_name=self.pd_nmos_model, pu_pmos_model_name=self.pu_pmos_model, pg_nmos_model_name=self.pg_nmos_model, pd_width=self.pd_width, pu_width=self.pu_width, pg_width=self.pg_width, length=self.length)

        # Add the subcircuit to the circuit
        self.circuit.subcircuit(sram_cell)

        # Instantiate the cell
        self.circuit.X("SRAM1", "SRAM_6T_CELL", "VDD", "VSS", "BL", "BLB", "WL")

        # Power supplies
        self.circuit.V("VDD", "VDD", self.circuit.gnd, self.config.vdd @ u_V)
        self.circuit.V("VSS", "VSS", self.circuit.gnd, 0 @ u_V)

    def _get_pwl_waveform(self, voltage_val):
        # Generate PWL string: 0 -> rise -> hold -> fall -> 0
        t0 = 0
        t1 = self.rise_time
        t2 = self.hold_time
        t3 = self.hold_time + self.rise_time
        t4 = self.end_time

        # Ensure voltage_val is a string or float
        v = str(voltage_val).replace(" ", "")

        pwl = f"PWL({t0} 0 {t1} {v} {t2} {v} {t3} 0 {t4} 0)"
        return pwl

    def _setup_port_source(self, port_name, voltage_val):
        # Remove existing sources on ports
        for p in ["BL", "BLB", "WL"]:
            if f"V{p}" in self.circuit._elements:
                self.circuit._elements.pop(f"V{p}", None)

        # Add new source for the target port
        pwl = self._get_pwl_waveform(voltage_val)
        self.circuit.V(port_name, port_name, self.circuit.gnd, pwl)

        # set other ports
        if port_name in ["BL", "BLB"]:
            self.circuit.V("WL", "WL", self.circuit.gnd, 0 @ u_V)

    def get_current(self, source_name, analysis):
        # Try to find current in branches
        # PySpice branch names are usually lowercase
        branch_name = source_name.lower()
        if branch_name in analysis.branches:
            return -analysis.branches[branch_name].as_ndarray()

        # Fallback: xyce use nodes
        if source_name in analysis.nodes.keys():
            return -analysis.nodes[source_name].as_ndarray()

        print(f"[WARNING] Could not find current for {source_name}. Available branches: {list(analysis.branches.keys())}")
        return np.zeros(len(analysis.time))

    def run_sram_transient(self, port_name, voltage_val):
        print(f"[DEBUG] Running SRAM transient simulation for {port_name} at {voltage_val}")
        self._setup_port_source(port_name, voltage_val)

        simulator = self.circuit.simulator(temperature=self.config.temperature, nominal_temperature=self.config.temperature, simulator="xyce-parallel")

        # Initial conditions
        vq = self.config.vdd @ u_V if self.q_init_val else 0 @ u_V
        vqb = 0 @ u_V if self.q_init_val else self.config.vdd @ u_V
        simulator.initial_condition(**{f"XSRAM1:Q": vq, f"XSRAM1:QB": vqb})

        print(f"[DEBUG] Netlist:")
        print(str(simulator))

        analysis = simulator.transient(step_time=self.step_time, end_time=self.end_time)

        time = analysis.time.as_ndarray()
        voltage = analysis[port_name].as_ndarray()
        current = self.get_current(f"V{port_name}", analysis)
        avg_current = last_proportion_mean(current)

        return {"time": time, "voltage": voltage, "current": current, "avg_current": avg_current}

    def get_equivalent_circuit(self, port_name, voltage_val, params):
        circuit = Circuit(f"{port_name}_Equiv")
        # circuit.include(self.config.pdk_path_TT)

        pwl = self._get_pwl_waveform(voltage_val)
        circuit.V(port_name, port_name, circuit.gnd, pwl)

        c0 = params.get("c0", 1e-16)
        circuit.C("C0", port_name, circuit.gnd, c0)

        # if port_name == "WL":
        #     # 提取参数（带默认值）
        #     r1 = params.get("r1", 6e7)  # 控制支路（延时网络）电阻
        #     c1 = params.get("c1", 1e-20)  # 控制支路（延时网络）电容
        #     r2 = params.get("r2", 20000)  # 被控支路电阻
        #     c2 = params.get("c2", 7e-17)  # 被控支路电容

        #     # 支路1：控制支路（WL 延时网络） - R1-C1
        #     circuit.R("R1", port_name, "WL_CONTROL_NODE", r1)
        #     circuit.C("C1", "WL_CONTROL_NODE", circuit.gnd, c1)

        #     # 支路2：被控支路 - 非线性电阻模型
        #     # 使用控制支路电压控制非线性电阻的行为
        #     circuit.raw_spice += f"BR2 WL WL_CONTROLLED_NODE I = {{v(WL,WL_CONTROLLED_NODE) / (1/(2e-4*EXP((v(WL_CONTROL_NODE)-0.7)*25)) + {r2})}}\n"
        #     circuit.C("C2", "WL_CONTROLLED_NODE", circuit.gnd, c2)

        #     # 初始条件设置 - 被控支路初始电压
        #     circuit.raw_spice += ".ic V(WL_CONTROLLED_NODE)=0.5\n"

        # if port_name == "WL":
        #     c0 = params.get("c0", 1e-16)
        #     circuit.C("C0", port_name, circuit.gnd, c0)

        # else:
        #     r0 = params.get("r0", 1e3)
        #     circuit.R("R0", port_name, circuit.gnd, r0)

        # if port_name == "WL":
        #     c0 = params.get("c0", 1e-16)
        #     # c1 = params.get("c1", 1e-16)

        #     circuit.C("C0", port_name, circuit.gnd, c0)
        #     # Non-linear resistor model
        #     # circuit.raw_spice += f"BR1 {port_name} {port_name}_MID I = {{ 1e-4*(EXP((v({port_name})-0.6)*10))*(v({port_name},{port_name}_MID)) }}\n"
        #     # circuit.C("C1", f"{port_name}_MID", circuit.gnd, c1)
        # else:
        #     # Simple RC for other ports if needed
        #     r = params.get("r", 1e3)
        #     c = params.get("c", 1e-15)
        #     circuit.R("R1", port_name, circuit.gnd, r)
        #     circuit.C("C1", port_name, circuit.gnd, c)

        return circuit

    def run_equivalent_transient(self, port_name, voltage_val, params):
        print(f"[DEBUG] Running Equivalent Circuit transient simulation for {port_name}")
        circuit = self.get_equivalent_circuit(port_name, voltage_val, params)
        simulator = circuit.simulator(temperature=self.config.temperature, nominal_temperature=self.config.temperature, simulator="xyce-parallel")

        print(f"[DEBUG] Netlist:")
        print(str(simulator))

        analysis = simulator.transient(step_time=self.step_time, end_time=self.end_time)

        time = analysis.time.as_ndarray()
        voltage = analysis[port_name].as_ndarray()
        current = self.get_current(f"V{port_name}", analysis)
        avg_current = last_proportion_mean(current)

        result = {"time": time, "voltage": voltage, "current": current, "avg_current": avg_current}

        # if f"{port_name}_MID" in analysis.nodes:
        #     result["voltage_mid"] = analysis[f"{port_name}_MID"].as_ndarray()

        return result

    def compare_and_plot(self, port_name, ratios, equiv_params):
        results = []

        for ratio in ratios:
            voltage_val = self.config.vdd * ratio @ u_V

            # Run SRAM simulation
            sram_res = self.run_sram_transient(port_name, voltage_val)

            # Run Equivalent simulation
            equiv_res = self.run_equivalent_transient(port_name, voltage_val, equiv_params)

            results.append({"ratio": ratio, "voltage_val": voltage_val, "sram": sram_res, "equiv": equiv_res})

        self._plot_comparison(port_name, results)

    def _plot_comparison(self, port_name, results):
        def align_yaxis(ax1, ax2):
            y1_min, y1_max = ax1.get_ylim()
            y2_min, y2_max = ax2.get_ylim()
            ratio_max = y1_max / y2_max if y2_max != 0 else 1
            ratio_min = y1_min / y2_min if y2_min != 0 else 1
            max_ratio = min(abs(ratio_max), abs(ratio_min))
            ax2.set_ylim(y1_min / max_ratio, y1_max / max_ratio)

        n = len(results)
        fig, axes = plt.subplots(n, 1, figsize=(8 / 1.5, 3 * n / 1.2))
        if n == 1:
            axes = [axes]

        for i, res in enumerate(results):
            ax1 = axes[i]
            ratio = res["ratio"]
            sram = res["sram"]
            equiv = res["equiv"]

            # Plot Currents
            color = "tab:blue"
            ax1.set_ylabel("Current (uA)", color=color)
            ax1.plot(sram["time"] * 1e9, sram["current"] * 1e6, color=color, linestyle="-", label="SRAM Current")
            ax1.plot(equiv["time"] * 1e9, equiv["current"] * 1e6, color=color, linestyle="--", label="Equiv Current", alpha=0.7, linewidth=2)
            ax1.tick_params(axis="y", labelcolor=color)
            ax1.grid(True, alpha=0.6)

            # Plot Voltages
            ax2 = ax1.twinx()
            color = "tab:red"
            ax2.set_ylabel("Voltage (V)", color=color)
            ax2.plot(sram["time"] * 1e9, sram["voltage"], color=color, linestyle="-", label="Voltage")
            if "voltage_mid" in equiv:
                ax2.plot(equiv["time"] * 1e9, equiv["voltage_mid"], color="tab:orange", linestyle="-.", label="Equiv Mid Voltage")
            ax2.tick_params(axis="y", labelcolor=color)

            voltage_val = res["voltage_val"]
            ax1.set_title(f"{port_name} = {voltage_val}")

            # Legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

            align_yaxis(ax1, ax2)

        axes[-1].set_xlabel("Time (ns)")
        plt.tight_layout()
        # plt.show(block=False)
        plt.savefig(image_base_path + port_name + "_equiv_comparison.svg")
        plt.close()

    def get_port_c(self, port_name):
        voltage_val = self.config.vdd * 0.4 @ u_V
        sram_res = self.run_sram_transient(port_name, voltage_val)

        # 积分前半部分的电压
        end_index = sum(sram_res["time"] < self.hold_time)
        integrator = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
        charge = integrator(sram_res["current"][:end_index], sram_res["time"][:end_index])
        c_value = charge / (voltage_val)

        # exit(0)
        return c_value

    def get_static_power_r(self):
        print(f"[DEBUG] Running SRAM transient simulation for static power estimation")
        for p in ["BL", "BLB", "WL"]:
            if f"V{p}" in self.circuit._elements:
                self.circuit._elements.pop(f"V{p}", None)
        # self.circuit.V("BL", "BL", self.circuit.gnd, 0 @ u_V)
        # self.circuit.V("BLB", "BLB", self.circuit.gnd, 0 @ u_V)
        # self.circuit.V("WL", "WL", self.circuit.gnd, 0 @ u_V)

        simulator = self.circuit.simulator(temperature=self.config.temperature, nominal_temperature=self.config.temperature, simulator="xyce-parallel")

        # Initial conditions
        vq = self.config.vdd @ u_V if self.q_init_val else 0 @ u_V
        vqb = 0 @ u_V if self.q_init_val else self.config.vdd @ u_V
        simulator.initial_condition(**{f"XSRAM1:Q": vq, f"XSRAM1:QB": vqb})

        print(f"[DEBUG] Netlist:")
        print(str(simulator))

        analysis = simulator.transient(step_time=self.step_time, end_time=self.end_time)

        time = analysis.time.as_ndarray()
        voltage = analysis["VDD"].as_ndarray()
        current = self.get_current(f"VVDD", analysis)
        avg_current = last_proportion_mean(current)

        return {"R": (self.config.vdd / avg_current), "time": time, "voltage": voltage, "current": current, "avg_current": avg_current}


if __name__ == "__main__":
    # Load config
    try:
        with open("config.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        config = GlobalConfig(config_data)
    except FileNotFoundError:
        config = GlobalConfig({})

    tester = SRAMCellParasiticTester(config=config, corner="TT", q_init_val=0)

    result = tester.get_static_power_r()
    print(f"Static Power R: {result['R'] @ u_Ohm}")

    plt.plot(result["time"] * 1e9, result["current"] * 1e9)
    plt.xlabel("Time (ns)")
    plt.ylabel("Current (nA)")
    plt.title("Static Power Current Estimation")
    # plt.show(block=False)
    plt.savefig(image_base_path + "static_power_current.svg")
    plt.close()

    # exit(0)

    # Define ratios to test
    # ratios = [0.2, 0.5, 0.8, 1.0]
    ratios = [1.0]

    for port in ["BL", "BLB", "WL"]:
        # for port in ["BL"]:
        # for port in ["WL"]:
        c0 = tester.get_port_c(port)
        equiv_params = {"c0": c0 @ u_F}
        tester.compare_and_plot(port, ratios, equiv_params)

    plt.show()
