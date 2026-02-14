from sram_compiler.testbenches.sram_6t_core_testbench import Sram6TCoreTestbench  # type: ignore
from sram_compiler.testbenches.sram_6t_core_MC_testbench import Sram6TCoreMcTestbench  # type: ignore
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF, u_A, u_mA
import numpy as np
from utils import estimate_bitcell_area  # type: ignore
from config import SRAM_CONFIG
from datetime import datetime
import os

if __name__ == "__main__":
    # ================== 1. 加载所有配置 ==================
    sram_config = SRAM_CONFIG()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sram_config.load_all_configs(global_file=os.path.join(script_dir, "sram_compiler/config_yaml/global.yaml"), circuit_configs={"SRAM_6T_CELL": os.path.join(script_dir, "sram_compiler/config_yaml/sram_6t_cell.yaml"), "WORDLINEDRIVER": os.path.join(script_dir, "sram_compiler/config_yaml/wordline_driver.yaml"), "PRECHARGE": os.path.join(script_dir, "sram_compiler/config_yaml/precharge.yaml"), "COLUMNMUX": os.path.join(script_dir, "sram_compiler/config_yaml/mux.yaml"), "SENSEAMP": os.path.join(script_dir, "sram_compiler/config_yaml/sa.yaml"), "WRITEDRIVER": os.path.join(script_dir, "sram_compiler/config_yaml/write_driver.yaml"), "DECODER": os.path.join(script_dir, "sram_compiler/config_yaml/decoder.yaml")})

    # 2. 生成时间戳子目录
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    sim_path = os.path.join(script_dir, "sim", f"{time_str}_mc_6t")
    os.makedirs(sim_path, exist_ok=True)

    # FreePDK45 default transistor sizes
    nmos_vals = sram_config.sram_6t_cell.nmos_width.value
    if isinstance(nmos_vals, (list, tuple)):
        pd_width = float(nmos_vals[0])
        pg_width = float(nmos_vals[1])
    else:
        pd_width = float(nmos_vals)
        pg_width = float(nmos_vals)

    pmos_val = sram_config.sram_6t_cell.pmos_width.value
    if isinstance(pmos_val, (list, tuple)):
        pu_width = float(pmos_val[0])
    else:
        pu_width = float(pmos_val)

    length_val = float(sram_config.sram_6t_cell.length.value)
    area = estimate_bitcell_area(w_access=pg_width, w_pd=pd_width, w_pu=pu_width, l_transistor=length_val)
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
        use_mc=True,
        custom_mc=False,  # Use your own process params?
        param_sweep=False,
        sweep_precharge=False,
        sweep_senseamp=False,
        sweep_wordlinedriver=False,
        sweep_columnmux=False,
        sweep_writedriver=False,
        sweep_decoder=False,
        coner="TT",  # or FF or SS or FS or SF
        choose_columnmux=False,
        q_init_val=0,
        sim_path=sim_path,
        gen_unused_cells=True,
    )
    # vars = np.random.rand(num_mc,num_rows*num_cols*18)

    # For using DC analysis, operation can be 'write_snm' 'hold_snm' 'read_snm'
    hold_snm = mc_testbench.run_mc_simulation(
        operation="hold_snm",
        target_row=num_rows - 1,
        target_col=num_cols - 1,
        mc_runs=num_mc,
        vars=None,  # Input your data table
    )

    read_snm = mc_testbench.run_mc_simulation(
        operation="read_snm",
        target_row=num_rows - 1,
        target_col=num_cols - 1,
        mc_runs=num_mc,
        vars=None,  # Input your data table
    )

    write_snm = mc_testbench.run_mc_simulation(
        operation="write_snm",
        target_row=num_rows - 1,
        target_col=num_cols - 1,
        mc_runs=num_mc,
        vars=None,  # Input your data table
    )

    # For using TRAN analysis, operation can be 'write' or 'read'
    # r_delay, r_pavg, r_pstc, r_pdyn = mc_testbench.run_mc_simulation(
    #     operation="read",
    #     target_row=num_rows - 1,
    #     target_col=num_cols - 1,
    #     mc_runs=num_mc,
    #     temperature=temperature,
    #     vars=None,  # Input your data table
    # )

    # print(r_delay, r_pavg, r_pstc, r_pdyn)

    # w_delay, w_pavg, w_pstc, w_pdyn = mc_testbench.run_mc_simulation(
    #     operation="write",
    #     target_row=num_rows - 1,
    #     target_col=num_cols - 1,
    #     mc_runs=num_mc,
    #     temperature=temperature,
    #     vars=None,  # Input your data table
    # )

    print("[DEBUG] Monte Carlo simulation completed")
