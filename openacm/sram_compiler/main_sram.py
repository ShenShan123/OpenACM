from sram_compiler.testbenches.sram_6t_core_testbench import Sram6TCoreTestbench  # type: ignore
from sram_compiler.testbenches.sram_6t_core_MC_testbench import Sram6TCoreMcTestbench  # type: ignore
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF, u_A, u_mA
import numpy as np
from utils import estimate_bitcell_area  # type: ignore
from config import SRAM_CONFIG
from datetime import datetime
import os

if __name__ == "__main__":
    os.environ["OMP_NUM_THREADS"] = "8"
    os.environ["XYCE_NUM_THREADS"] = "8"
    # ================== 1. Load all configurations ==================
    sram_config = SRAM_CONFIG()
    _base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    _cfg_dir = os.path.join(_base_dir, "config")
    sram_config.load_all_configs(
        global_file=os.path.join(_cfg_dir, "global.yaml"),
        circuit_configs={
            "SRAM_6T_CELL": os.path.join(_cfg_dir, "sram_6t_cell.yaml"),
            "WORDLINEDRIVER": os.path.join(_cfg_dir, "wordline_driver.yaml"),
            "PRECHARGE": os.path.join(_cfg_dir, "precharge.yaml"),
            "COLUMNMUX": os.path.join(_cfg_dir, "mux.yaml"),
            "SENSEAMP": os.path.join(_cfg_dir, "sa.yaml"),
            "WRITEDRIVER": os.path.join(_cfg_dir, "write_driver.yaml"),
            "DECODER": os.path.join(_cfg_dir, "decoder.yaml"),
        },
    )
    _tm1_dir = os.path.join(os.path.dirname(__file__), "tran_models")
    _tm2_dir = os.path.join(_base_dir, "level2_transistor", "sram_sizing", "tran_models")
    if not os.path.exists(sram_config.global_config.pdk_path_TT):
        sram_config.global_config.pdk_path_TT = os.path.join(_tm1_dir if os.path.exists(os.path.join(_tm1_dir, "models_TT.spice")) else _tm2_dir, "models_TT.spice")
    if not os.path.exists(sram_config.global_config.pdk_path_FF):
        sram_config.global_config.pdk_path_FF = os.path.join(_tm1_dir if os.path.exists(os.path.join(_tm1_dir, "models_FF.spice")) else _tm2_dir, "models_FF.spice")
    if not os.path.exists(sram_config.global_config.pdk_path_SS):
        sram_config.global_config.pdk_path_SS = os.path.join(_tm1_dir if os.path.exists(os.path.join(_tm1_dir, "models_SS.spice")) else _tm2_dir, "models_SS.spice")
    if not os.path.exists(sram_config.global_config.pdk_path_FS):
        sram_config.global_config.pdk_path_FS = os.path.join(_tm1_dir if os.path.exists(os.path.join(_tm1_dir, "models_FS.spice")) else _tm2_dir, "models_FS.spice")
    if not os.path.exists(sram_config.global_config.pdk_path_SF):
        sram_config.global_config.pdk_path_SF = os.path.join(_tm1_dir if os.path.exists(os.path.join(_tm1_dir, "models_SF.spice")) else _tm2_dir, "models_SF.spice")

    # 2. Generate timestamped subdirectory
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    sim_path = os.path.join("sim", f"{time_str}_mc_6t")  # e.g., sim/20250928_153045_mc_6t
    os.makedirs(sim_path, exist_ok=True)

    # FreePDK45 default transistor sizes
    area = estimate_bitcell_area(w_access=sram_config.sram_6t_cell.nmos_width.value[1], w_pd=sram_config.sram_6t_cell.nmos_width.value[0], w_pu=sram_config.sram_6t_cell.pmos_width.value, l_transistor=sram_config.sram_6t_cell.length.value)  # pg
    print(f"Estimated 6T SRAM Cell Area: {area*1e12:.2f} µm²")

    temperature = sram_config.global_config.temperature
    num_rows = sram_config.global_config.num_rows
    num_cols = sram_config.global_config.num_cols
    num_mc = sram_config.global_config.monte_carlo_runs

    print("===== 6T SRAM Array Monte Carlo Simulation Debug Session =====")
    mc_testbench = Sram6TCoreMcTestbench(
        sram_config,
        w_rc=True,  # Whether add RC to nets
        pi_res=100 @ u_Ohm,
        pi_cap=0.001 @ u_pF,
        vth_std=0.05,  # Process parameter variation is a percentage of its value in model lib
        use_mc=False,
        custom_mc=False,  # Use your own process params?
        param_sweep=False,
        sweep_precharge=False,
        sweep_senseamp=False,
        sweep_wordlinedriver=False,
        sweep_columnmux=False,
        sweep_writedriver=False,
        sweep_decoder=False,
        coner="TT",  # or FF or SS or FS or SF
        choose_columnmux=sram_config.global_config.choose_columnmux,
        q_init_val=0,
        sim_path=sim_path,
        gen_unused_cells=True,
    )
    # vars = np.random.rand(num_mc,num_rows*num_cols*18)

    # For using DC analysis, operation can be 'write_snm' 'hold_snm' 'read_snm'
    # read_snm = mc_testbench.run_mc_simulation(
    #     operation='hold_snm', target_row=num_rows-1, target_col=num_cols-1, mc_runs=num_mc,
    #     vars=None, # Input your data table
    # )

    # For using TRAN analysis, operation can be 'write' or 'read'
    r_delay, r_pavg, r_pstc, r_pdyn = mc_testbench.run_mc_simulation(
        operation="read",
        target_row=num_rows - 1,
        target_col=num_cols - 1,
        mc_runs=num_mc,
        temperature=temperature,
        vars=None,  # Input your data table
    )

    print(r_delay, r_pavg, r_pstc, r_pdyn)

    # w_delay, w_pavg, w_pstc, w_pdyn = mc_testbench.run_mc_simulation(
    #     operation="write",
    #     target_row=num_rows - 1,
    #     target_col=num_cols - 1,
    #     mc_runs=num_mc,
    #     temperature=temperature,
    #     vars=None,  # Input your data table
    # )

    print("[DEBUG] Monte Carlo simulation completed")
