"""
Joint SRAM Optimization Program
SRAM联合优化程序

This program performs joint optimization of architecture configuration and transistor parameters
for 32KB (262144-bit) SRAM arrays.
该程序对32KB（262144 位）SRAM阵列进行架构与晶体管参数的联合优化。

Supported algorithms: SA, PSO, SMAC, CBO, RoSE_Opt, MOEAD, MOBO, NSGA-II
支持算法：SA, PSO, SMAC, CBO, RoSE_Opt, MOEAD, MOBO, NSGA-II
"""

import os
import sys
import time
import numpy as np
import torch
import random
import warnings
import json
import csv
import shutil
from pathlib import Path
import traceback
from datetime import datetime
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

ROW_CHOICES = [16, 32, 64, 128, 256, 512]
COLUMN_CHOICES = [16, 32, 64, 128, 256, 512]
TOTAL_BITS = 262144

# Import path handling
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

# Import utilities
from size_optimization.exp_utils import seed_set, create_directories, ModifiedSRAMParameterSpace, get_params_from_yaml
from utils import estimate_total_area, estimate_bitcell_area

# Import SRAM simulation modules
# 导入SRAM仿真模块
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF, u_A, u_mA
from sram_compiler.testbenches.sram_6t_core_MC_testbench import Sram6TCoreMcTestbench
from config import SRAM_CONFIG


class ArchitectureConfigurationSpace:
    """
    Architecture configuration space for 32KB (262144-bit) SRAM
    32KB（262144 位）SRAM的架构配置空间
    """

    def __init__(self):
        self.total_bits = TOTAL_BITS
        self.row_choices = ROW_CHOICES
        self.column_choices = COLUMN_CHOICES
        self.max_rows = max(self.row_choices)
        self.max_cols = max(self.column_choices)
        self.min_rows = min(self.row_choices)
        self.min_cols = min(self.column_choices)
        self.valid_configs = self._generate_valid_configurations()

    def _generate_valid_configurations(self) -> List[Dict]:
        """
        Generate all valid architecture configurations
        生成所有有效的架构配置
        行列最小值不能小于2
        """
        valid_configs = []

        for rows in self.row_choices:
            for cols in self.column_choices:
                array_capacity = rows * cols

                # Check if total capacity can be achieved with integer number of arrays
                # 检查是否可以用整数个阵列实现总容量
                if self.total_bits % array_capacity == 0:
                    num_arrays = self.total_bits // array_capacity

                    config = {"rows": rows, "cols": cols, "num_arrays": num_arrays, "array_capacity": array_capacity, "total_capacity": self.total_bits}
                    valid_configs.append(config)

        print(f"Generated {len(valid_configs)} valid configurations (rows in {self.row_choices}, cols in {self.column_choices})")
        print(f"生成了 {len(valid_configs)} 个有效配置 (行={self.row_choices}, 列={self.column_choices})")

        return valid_configs

    def get_configuration(self, index: int) -> Dict:
        """
        Get configuration by index
        根据索引获取配置
        """
        if 0 <= index < len(self.valid_configs):
            return self.valid_configs[index]
        else:
            raise IndexError(f"Configuration index {index} out of range [0, {len(self.valid_configs)-1}]")

    def get_num_configurations(self) -> int:
        """
        Get total number of valid configurations
        获取有效配置的总数
        """
        return len(self.valid_configs)


class JointParameterSpace:
    def __init__(self, arch_space: ArchitectureConfigurationSpace, base_space: ModifiedSRAMParameterSpace):
        self.arch_space = arch_space
        self.base_space = base_space
        self.row_choices = arch_space.row_choices
        self.column_choices = arch_space.column_choices
        prefix = torch.tensor([[0.0, 0.0], [1.0, 1.0]], dtype=torch.float32)
        self.bounds = torch.cat([prefix, base_space.bounds], dim=1)

    def convert_params(self, x):
        if isinstance(x, torch.Tensor):
            if x.dim() > 1:
                x = x.flatten()
        else:
            x = torch.tensor(x, dtype=torch.float32)
        row_idx = int(float(x[0]) * len(self.row_choices))
        col_idx = int(float(x[1]) * len(self.column_choices))
        row_idx = max(0, min(row_idx, len(self.row_choices) - 1))
        col_idx = max(0, min(col_idx, len(self.column_choices) - 1))
        rows = self.row_choices[row_idx]
        cols = self.column_choices[col_idx]
        params = self.base_space.convert_params(x[2:])
        params["rows"] = rows
        params["cols"] = cols
        return params

    def print_params(self, params):
        return self.base_space.print_params(params)


def evaluate_sram_with_config(params, num_rows, num_cols, num_arrays, output_cols=16, timeout=120, *, stage_label="stage_eval", iteration_index=None, temperature=None, corner="TT"):
    """
    Execute SRAM evaluation with given parameters and specific row-column configuration
    使用给定参数和特定行列配置执行SRAM评估

    This function is copied from demo_joint_optimization.py to make two_stage_optimization.py
    independent of demo_joint_optimization.py
    此函数从demo_joint_optimization.py复制而来，使two_stage_optimization.py不依赖demo_joint_optimization.py
    """
    # 获取项目根目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir

    # 依据标签确定仿真输出目录
    sim_subdir = str(stage_label) if stage_label else "joint"
    if sim_subdir.startswith("joint"):
        stage_parts = str(stage_label).split("/", 1)
        if len(stage_parts) > 1 and stage_parts[1]:
            sim_subdir = str(Path(sim_subdir) / stage_parts[1])
        sim_subdir = str(Path(sim_subdir) / f"r{num_rows}_c{num_cols}_a{num_arrays}")
    # 输出到绝对路径 /OpenYield/size_optimization/sim/<stage>
    sim_dir_path = Path(project_root) / "size_optimization" / "sim" / sim_subdir
    sim_dir_path.mkdir(parents=True, exist_ok=True)

    sram_config = SRAM_CONFIG()
    sram_config.load_all_configs(global_file=os.path.join(project_root, "sram_compiler/config_yaml/global.yaml"), circuit_configs={"SRAM_6T_CELL": os.path.join(project_root, "sram_compiler/config_yaml/sram_6t_cell.yaml"), "WORDLINEDRIVER": os.path.join(project_root, "sram_compiler/config_yaml/wordline_driver.yaml"), "PRECHARGE": os.path.join(project_root, "sram_compiler/config_yaml/precharge.yaml"), "COLUMNMUX": os.path.join(project_root, "sram_compiler/config_yaml/mux.yaml"), "SENSEAMP": os.path.join(project_root, "sram_compiler/config_yaml/sa.yaml"), "WRITEDRIVER": os.path.join(project_root, "sram_compiler/config_yaml/write_driver.yaml"), "DECODER": os.path.join(project_root, "sram_compiler/config_yaml/decoder.yaml")})

    try:
        print(f"Starting SRAM evaluation with {num_rows}x{num_cols} and {output_cols} output config")
        print(f"开始使用{num_rows}x{num_cols},{output_cols}配置进行SRAM评估")

        def _write_and_load_params_csv():
            """将当前参数写入CSV并读取最新一行返回。"""
            # 将参数追踪CSV写入阶段化目录（与网表输出一致）
            sim_dir = sim_dir_path
            sim_dir.mkdir(parents=True, exist_ok=True)

            headers = [
                "timestamp",
                "stage",
                "iteration",
                "rows",
                "cols",
                "pu_width",
                "pd_width",
                "pg_width",
                "length",
                "pmos_model_name",
                "nmos_model_name",
            ]
            timestamp = datetime.now().isoformat(timespec="seconds")
            row = [
                timestamp,
                stage_label,
                "" if iteration_index is None else iteration_index,
                num_rows,
                num_cols,
                params.get("pu_width", 0.0),
                params.get("pd_width", 0.0),
                params.get("pg_width", 0.0),
                params.get("length", 0.0),
                params.get("pmos_model_name", ""),
                params.get("nmos_model_name", ""),
            ]

            history_path = sim_dir / "transistor_params_history.csv"
            write_header = not history_path.exists()
            with open(history_path, "a", newline="", encoding="utf-8") as f_hist:
                writer = csv.writer(f_hist)
                if write_header:
                    writer.writerow(headers)
                writer.writerow(row)

            latest_path = sim_dir / "transistor_params_latest.csv"
            with open(latest_path, "w", newline="", encoding="utf-8") as f_latest:
                writer = csv.writer(f_latest)
                writer.writerow(headers)
                writer.writerow(row)

            with open(latest_path, "r", newline="", encoding="utf-8") as f_latest:
                reader = csv.DictReader(f_latest)
                latest_row = next(reader)

            def _to_float(value):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return value

            return {
                "pu_width": _to_float(latest_row["pu_width"]),
                "pd_width": _to_float(latest_row["pd_width"]),
                "pg_width": _to_float(latest_row["pg_width"]),
                "length": _to_float(latest_row["length"]),
                "pmos_model_name": latest_row["pmos_model_name"],
                "nmos_model_name": latest_row["nmos_model_name"],
            }

        latest_params = _write_and_load_params_csv()
        params.update({k: v for k, v in latest_params.items() if v != ""})

        # CRITICAL: Update the SRAM configuration with the specified row/column counts
        # 关键：使用指定的行列数更新SRAM配置
        sram_config.global_config.num_rows = num_rows
        sram_config.global_config.num_cols = num_cols
        sram_config.global_config.output_cols = output_cols
        if temperature is None:
            temperature = getattr(sram_config.global_config, "temperature", 27)

        # CRITICAL: Update transistor parameters in sram_config before creating testbench
        # 关键：在创建testbench之前更新sram_config中的晶体管参数
        sram_config.sram_6t_cell.pmos_width.value = float(params["pu_width"])
        sram_config.sram_6t_cell.nmos_width.value[0] = float(params["pd_width"])
        sram_config.sram_6t_cell.nmos_width.value[1] = float(params["pg_width"])
        sram_config.sram_6t_cell.length.value = float(params["length"])

        if params.get("pmos_model_name"):
            pmos_model = params["pmos_model_name"]
            if pmos_model in sram_config.sram_6t_cell.pmos_model.choices:
                sram_config.sram_6t_cell.pmos_model.value = pmos_model
            else:
                print(f"Warning: Invalid PMOS model name '{pmos_model}', using default")
                print(f"警告：无效的PMOS模型名称 '{pmos_model}'，使用默认值")

        if params.get("nmos_model_name"):
            nmos_model = params["nmos_model_name"]
            if nmos_model in sram_config.sram_6t_cell.nmos_model.choices:
                sram_config.sram_6t_cell.nmos_model.value[0] = nmos_model
                sram_config.sram_6t_cell.nmos_model.value[1] = nmos_model
            else:
                print(f"Warning: Invalid NMOS model name '{nmos_model}', using default")
                print(f"警告：无效的NMOS模型名称 '{nmos_model}'，使用默认值")

        print(f"Updated SRAM config with parameters: pu={float(params['pu_width'])*1e9:.2f}nm, " f"pd={float(params['pd_width'])*1e9:.2f}nm, pg={float(params['pg_width'])*1e9:.2f}nm, " f"length={float(params['length'])*1e9:.2f}nm")
        print(f"已更新SRAM配置参数: pu={float(params['pu_width'])*1e9:.2f}nm, " f"pd={float(params['pd_width'])*1e9:.2f}nm, pg={float(params['pg_width'])*1e9:.2f}nm, " f"length={float(params['length'])*1e9:.2f}nm")

        start_time = time.time()

        # Set simulation parameters
        # 设置仿真参数
        vdd = 1.0
        pdk_path = os.path.join(project_root, "tran_models/models_TT.spice")
        num_mc = 1

        if not hasattr(evaluate_sram_with_config, "_default_bitcell_area"):
            default_params = get_params_from_yaml()
            evaluate_sram_with_config._default_bitcell_area = estimate_bitcell_area(
                w_access=default_params["pg_width"],
                w_pd=default_params["pd_width"],
                w_pu=default_params["pu_width"],
                l_transistor=default_params["length"],
            )
        base_array_area = estimate_total_area(num_rows, num_cols, num_arrays)
        current_bitcell_area = estimate_bitcell_area(
            w_access=params.get("pg_width", 0.0),
            w_pd=params.get("pd_width", 0.0),
            w_pu=params.get("pu_width", 0.0),
            l_transistor=params.get("length", 0.0),
        )
        default_bitcell_area = getattr(evaluate_sram_with_config, "_default_bitcell_area", 0.0)
        scale_factor = current_bitcell_area / default_bitcell_area if default_bitcell_area > 0 else 1.0
        area = base_array_area * scale_factor

        mc_testbench = Sram6TCoreMcTestbench(
            sram_config,
            w_rc=True,
            pi_res=100 @ u_Ohm,
            pi_cap=0.001 @ u_pF,
            vth_std=0.05,
            use_mc=False,
            custom_mc=False,
            param_sweep=False,
            sweep_precharge=False,
            sweep_senseamp=False,
            sweep_wordlinedriver=False,
            sweep_columnmux=False,
            sweep_writedriver=False,
            sweep_decoder=False,
            coner=corner,
            choose_columnmux=output_cols < num_cols,
            q_init_val=0,
            sim_path=str(sim_dir_path),
            gen_unused_cells=True,
        )

        

        try:
            # Run simulation directly
            # 直接运行仿真
            hold_snm = mc_testbench.run_mc_simulation(
                operation="hold_snm",
                target_row=num_rows - 1,
                target_col=num_cols - 1,
                mc_runs=num_mc,
                temperature=temperature,
                vars=None,
            )

            read_snm = mc_testbench.run_mc_simulation(
                operation="read_snm",
                target_row=num_rows - 1,
                target_col=num_cols - 1,
                mc_runs=num_mc,
                temperature=temperature,
                vars=None,
            )

            write_snm = mc_testbench.run_mc_simulation(
                operation="write_snm",
                target_row=num_rows - 1,
                target_col=num_cols - 1,
                mc_runs=num_mc,
                temperature=temperature,
                vars=None,
            )

            w_delay, w_pavg, w_pstc, w_pdyn = mc_testbench.run_mc_simulation(
                operation="write",
                target_row=num_rows - 1,
                target_col=num_cols - 1,
                mc_runs=num_mc,
                temperature=temperature,
                vars=None,
            )

            r_delay, r_pavg, r_pstc, r_pdyn = mc_testbench.run_mc_simulation(
                operation="read",
                target_row=num_rows - 1,
                target_col=num_cols - 1,
                mc_runs=num_mc,
                temperature=temperature,
                vars=None,
            )

            

            # Process simulation results
            # 处理仿真结果
            def get_float_value(sim_result):
                return float(sim_result[0]) if isinstance(sim_result, np.ndarray) else float(sim_result)

            hold_snm_val = get_float_value(hold_snm)
            read_snm_val = get_float_value(read_snm)
            write_snm_val = get_float_value(write_snm)
            min_snm = min(hold_snm_val, read_snm_val, write_snm_val)

            # print(w_delay, r_delay)

            # 加上片选信号的延迟
            w_delay += 4.167213500e-11 * np.log2(num_arrays)
            r_delay += 4.167213500e-11 * np.log2(num_arrays)

            # print(w_delay, r_delay)

            # 加上mux的延迟
            mux_delay = 1.8e-10
            r_delay += np.log2(num_arrays) * mux_delay

            # print(w_delay, r_delay)

            # exit(0)

            read_power = get_float_value(r_pstc) * num_arrays + get_float_value(r_pdyn)
            write_power = get_float_value(w_pstc) * num_arrays + get_float_value(w_pdyn)

            # 加上mux的功耗
            mux_power = 0.1e-6
            read_power -= (num_arrays - 1) * np.log2(num_arrays) * mux_power

            if num_cols < output_cols:
                # 需要多个回合
                w_delay *= output_cols // num_cols
                r_delay *= output_cols // num_cols

                read_power += get_float_value(r_pdyn) * (output_cols // num_cols)
                write_power += get_float_value(r_pdyn) * (output_cols // num_cols)

            # Take absolute value of power
            # 取功耗的绝对值
            read_power = abs(read_power)
            write_power = abs(write_power)
            max_power = max(read_power, write_power)

            read_delay = float(r_delay[0]) if isinstance(r_delay, np.ndarray) else float(r_delay)
            write_delay = float(w_delay[0]) if isinstance(w_delay, np.ndarray) else float(w_delay)

            # If any delay equals -1, treat this evaluation as invalid and discard the solution
            # 如果任一延迟为 -1，则视为无效评估并舍弃该解
            if (read_delay == -1) or (write_delay == -1):
                print("Invalid delay detected (read/write = -1). Discarding this solution.")
                print("检测到无效延迟（读/写为 -1）。舍弃该解。")
                objectives = [0.01, -1e-3, -1e-10]  # Penalty objective function
                constraints = [1.0, 1.0]  # Constraint violation
                return objectives, constraints, None, False

            read_delay_feasible = True
            write_delay_feasible = True

            # Calculate FoM (Figure of Merit)
            # 计算FoM（品质因数）
            # FoM = log10(min_snm / (max_power * max_delay))
            max_delay = max(read_delay, write_delay)
            if min_snm > 0 and max_power > 0 and max_delay > 0:
                fom = np.log10(min_snm / (max_power * max_delay))
            else:
                fom = -10.0  # Penalty value for invalid cases

            # Construct objectives (for multi-objective optimization)
            # 构建目标函数（用于多目标优化）
            objectives = [min_snm, -max_power, -max_delay]

            # Construct detailed results
            # 构建详细结果
            result = {"hold_snm": hold_snm_val, "read_snm": read_snm_val, "write_snm": write_snm_val, "min_snm": min_snm, "read_power": read_power, "write_power": write_power, "max_power": max_power, "read_delay": read_delay, "write_delay": write_delay, "max_delay": max_delay, "area": area, "fom": fom, "read_delay_feasible": read_delay_feasible, "write_delay_feasible": write_delay_feasible}

            # 补充阵列规模信息，供外部保存
            result.update(
                {
                    "num_rows": num_rows,
                    "num_cols": num_cols,
                    "capacity": num_rows * num_cols,
                    "aspect_ratio": (num_rows / num_cols) if num_cols else None,
                }
            )

            end_time = time.time()
            print(f"Simulation completed successfully! Time taken: {end_time - start_time:.2f} seconds")
            print(f"仿真成功完成！用时: {end_time - start_time:.2f} 秒")

            constraints = [0, 0]  # Constraint violation

            return objectives, constraints, result, True

        

        except Exception as e:
            print(f"Error occurred during simulation: {str(e)}")
            print(f"仿真过程中发生错误: {str(e)}")
            traceback.print_exc()
            objectives = [0.01, -1e-3, -1e-10]  # Penalty objective function
            constraints = [1.0, 1.0]  # Constraint violation
            return objectives, constraints, None, False

    except Exception as e:
        print(f"Error in testbench setup: {str(e)}")
        print(f"测试平台设置错误: {str(e)}")
        traceback.print_exc()
        objectives = [0.01, -1e-3, -1e-10]  # Penalty objective function
        constraints = [1.0, 1.0]  # Constraint violation
        return objectives, constraints, None, False


class SAOptimizer:
    """
    Simulated Annealing Optimizer
    模拟退火优化器
    """

    def __init__(self, evaluation_function, bounds=None, maximize=True):
        """
        Initialize SA optimizer
        初始化SA优化器

        Args:
            evaluation_function: Function to evaluate solutions
            bounds: Parameter bounds (for continuous optimization)
            maximize: Whether to maximize (True) or minimize (False) the objective
        """
        self.evaluation_function = evaluation_function
        self.bounds = bounds
        self.maximize = maximize
        self.best_solution = None
        self.best_value = float("-inf") if maximize else float("inf")
        self.history = []

    def _accept_probability(self, old_value, new_value, temperature):
        """
        Calculate acceptance probability for SA
        计算SA的接受概率
        """
        if self.maximize:
            if new_value > old_value:
                return 1.0
            else:
                return np.exp((new_value - old_value) / temperature)
        else:
            if new_value < old_value:
                return 1.0
            else:
                return np.exp((old_value - new_value) / temperature)

    def optimize_continuous(self, initial_solution, max_iter=100, T_max=1000, T_min=1e-7):
        """
        Optimize continuous solution space
        优化连续解空间
        """
        print(f"Starting SA optimization for continuous space")
        print(f"开始连续空间的SA优化")

        # Initialize
        current_solution = np.array(initial_solution)
        current_value, current_result = self.evaluation_function(current_solution)

        # Track best solution
        self.best_solution = current_solution.copy()
        self.best_value = current_value
        self.best_result = current_result

        # Temperature schedule
        T = T_max
        alpha = (T_min / T_max) ** (1.0 / max_iter)

        print(f"Initial value: {current_value:.6f}")
        print(f"初始值: {current_value:.6f}")

        for iteration in range(max_iter):
            # Generate neighbor solution
            neighbor_solution = current_solution + np.random.normal(0, 0.1, size=current_solution.shape)

            # Apply bounds if specified
            if self.bounds is not None:
                neighbor_solution = np.clip(neighbor_solution, self.bounds[0], self.bounds[1])

            neighbor_value, neighbor_result = self.evaluation_function(neighbor_solution)

            # Accept or reject
            accept_prob = self._accept_probability(current_value, neighbor_value, T)
            random_val = random.random()
            accepted = random_val < accept_prob

            if accepted:
                current_solution = neighbor_solution.copy()
                current_value = neighbor_value
                current_result = neighbor_result

                # Update best solution
                if (self.maximize and current_value > self.best_value) or (not self.maximize and current_value < self.best_value):
                    self.best_solution = current_solution.copy()
                    self.best_value = current_value
                    self.best_result = current_result
                    print(f"Iteration {iteration}: New best value: {self.best_value:.6f}")
                    print(f"迭代 {iteration}: 新的最佳值: {self.best_value:.6f}")

            # Record history
            self.history.append({"iteration": iteration, "current_value": current_value, "best_value": self.best_value, "temperature": T, "accepted": accepted})

            # Cool down
            T *= alpha

            if iteration % 10 == 0:
                print(f"Iteration {iteration}: T={T:.2e}, current_value={current_value:.6f}, best_value={self.best_value:.6f}")
                print(f"迭代 {iteration}: T={T:.2e}, 当前值={current_value:.6f}, 最佳值={self.best_value:.6f}")

        return self.best_solution, self.best_value, self.best_result


class JointOptimizer:
    """
    Joint SRAM optimization
    SRAM联合优化
    """

    def __init__(self, seed=42):
        """
        Initialize joint optimizer
        初始化联合优化器
        """
        # Set random seed
        seed_set(seed)
        self.seed = seed

        # Create directories
        create_directories()

        # Initialize architecture configuration space
        self.arch_space = ArchitectureConfigurationSpace()

        # Initialize transistor parameter space
        self.param_space = ModifiedSRAMParameterSpace()

        # Results storage
        self.joint_results = {}

        # Iteration history storage
        # 迭代历史存储
        self.joint_iteration_history = []
        self.joint_csv_tag = None

        print("Joint optimizer initialized")
        print("联合优化器已初始化")

    def _append_iteration_csv(self, stage: str, record: Dict[str, Any], label: str = None):
        algorithm_dir = getattr(self, "current_algorithm", None) or "unknown"
        base_dir = Path(project_root) / "size_optimization" / "experiment" / algorithm_dir
        base_dir.mkdir(parents=True, exist_ok=True)
        if label == "joint" and self.joint_csv_tag:
            filename = f"{stage}_iterations_live_joint_{self.joint_csv_tag}.csv"
        else:
            filename = f"{stage}_iterations_live.csv" if not label else f"{stage}_iterations_live_{label}.csv"
        path = base_dir / filename

        joint_fields = [
            "iteration",
            "fom",
            "success",
            "rows",
            "cols",
            "num_arrays",
            "pg_width",
            "pd_width",
            "pu_width",
            "length",
            "nmos_model_name",
            "pmos_model_name",
            "min_snm",
            "hold_snm",
            "read_snm",
            "write_snm",
            "read_delay",
            "write_delay",
            "max_delay",
            "read_power",
            "write_power",
            "objective_0",
            "objective_1",
            "objective_2",
            "constraint_0",
            "constraint_1",
        ]

        fields = joint_fields
        write_header = not path.exists()
        if not record.get("success", False):
            return
        key_fields = ["pg_width", "pd_width", "pu_width", "length", "nmos_model_name", "pmos_model_name", "fom", "max_delay"]
        last = None
        if path.exists():
            try:
                with open(path, "r", newline="", encoding="utf-8") as fr:
                    reader = csv.DictReader(fr)
                    for r in reader:
                        last = r
            except Exception:
                last = None
        dedupe = False
        if last is not None:
            try:
                dedupe = all(str(record.get(k, "")) == str(last.get(k, "")) for k in key_fields if k in fields)
            except Exception:
                dedupe = False
        if dedupe:
            return
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if write_header:
                writer.writeheader()
            row = {k: record.get(k, "") for k in fields}
            writer.writerow(row)

    def _calculate_timeout(self, rows, cols, base_timeout=120):
        """
        Calculate dynamic timeout based on configuration size
        根据配置大小计算动态超时时间

        Args:
            rows: Number of rows
            cols: Number of columns
            base_timeout: Base timeout in seconds (default 120)

        Returns:
            Calculated timeout in seconds
        """
        # Calculate array size
        # 计算阵列大小
        array_size = rows * cols

        # Timeout scales with array size
        # For small arrays (< 1000 bits): use base timeout
        # For medium arrays (1000-10000 bits): scale by 1.5x
        # For large arrays (> 10000 bits): scale by 2.0x or more
        # 超时时间随阵列大小缩放
        # 小阵列 (< 1000 bits): 使用基础超时
        # 中等阵列 (1000-10000 bits): 缩放1.5倍
        # 大阵列 (> 10000 bits): 缩放2.0倍或更多

        if array_size < 1000:
            timeout = base_timeout
        elif array_size < 10000:
            # Linear scaling: 1.0 to 1.5x
            # 线性缩放：1.0到1.5倍
            scale = 1.0 + 0.5 * (array_size - 1000) / 9000
            timeout = int(base_timeout * scale)
        else:
            # For very large arrays, use more aggressive scaling
            # 对于非常大的阵列，使用更激进的缩放
            # Scale factor: 1.5 + (size - 10000) / 20000, capped at 3.0x
            # 缩放因子：1.5 + (大小 - 10000) / 20000，上限为3.0倍
            scale = min(1.5 + (array_size - 10000) / 20000, 3.0)
            timeout = int(base_timeout * scale)

        # Ensure minimum timeout
        # 确保最小超时时间
        timeout = max(timeout, base_timeout)

        return timeout

    def _decode_joint_vector(self, x):
        x = np.array(x, dtype=float)
        if x.size < 2:
            return None
        row_count = len(self.arch_space.row_choices)
        col_count = len(self.arch_space.column_choices)
        row_idx = int(x[0] * row_count)
        col_idx = int(x[1] * col_count)
        row_idx = max(0, min(row_idx, row_count - 1))
        col_idx = max(0, min(col_idx, col_count - 1))
        rows = self.arch_space.row_choices[row_idx]
        cols = self.arch_space.column_choices[col_idx]
        array_capacity = rows * cols
        if self.arch_space.total_bits % array_capacity != 0:
            return None
        num_arrays = self.arch_space.total_bits // array_capacity
        params_tensor = torch.tensor(x[2:], dtype=torch.float32)
        params = self.param_space.convert_params(params_tensor)
        return rows, cols, num_arrays, params, array_capacity, row_idx, col_idx

    def run_joint_optimization(self, max_iter=200, algorithm="SA"):
        print("=" * 60)
        print("JOINT SRAM OPTIMIZATION")
        print("架构与晶体管尺寸联合优化")
        print("=" * 60)

        self.current_algorithm = algorithm
        seed_offsets = {"SA": 1, "PSO": 2, "SMAC": 3, "CBO": 4, "RoSE_Opt": 5, "MOEAD": 6}
        seed_set(self.seed + seed_offsets.get(algorithm, 0))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.joint_csv_tag = f"{algorithm}_{max_iter}_{timestamp}"
        self.joint_iteration_history = []
        iteration_counter = {"count": 0}
        joint_param_space = JointParameterSpace(self.arch_space, self.param_space)

        def _evaluate_joint(x):
            decoded = None
            params = None
            if isinstance(x, dict):
                params = dict(x)
                rows = params.get("rows", self.arch_space.row_choices[0])
                cols = params.get("cols", self.arch_space.column_choices[0])
                array_capacity = rows * cols
                if self.arch_space.total_bits % array_capacity == 0:
                    num_arrays = self.arch_space.total_bits // array_capacity
                    decoded = (rows, cols, num_arrays, params, array_capacity, None, None)
            else:
                decoded = self._decode_joint_vector(x)
            iteration_num = iteration_counter["count"]
            iteration_counter["count"] += 1
            if decoded is None:
                record = {"iteration": iteration_num, "fom": -1e9, "success": False}
                self.joint_iteration_history.append(record)
                self._append_iteration_csv("joint", record, label="joint")
                return -1e9, None, None, None, False, None, params

            rows, cols, num_arrays, params, array_capacity, row_idx, col_idx = decoded
            timeout = self._calculate_timeout(rows, cols)
            objectives, constraints, result, success = evaluate_sram_with_config(
                params,
                rows,
                cols,
                num_arrays,
                timeout=timeout,
                stage_label=f"joint/{algorithm}",
                iteration_index=iteration_num,
            )
            fom = -1e9
            if success and result:
                max_power = result["max_power"]
                max_delay = max(result["read_delay"], result["write_delay"])
                area = result.get("area", 0)
                if result["min_snm"] > 0 and max_power > 0 and area > 0 and max_delay > 0:
                    fom = np.log10(result["min_snm"] / (max_power * np.sqrt(area) * max_delay))
                else:
                    fom = -10.0
                result["total_area"] = area
                result["fom"] = fom
                result["merit"] = fom
                result["num_rows"] = rows
                result["num_cols"] = cols
                result["num_arrays"] = num_arrays

            record = {
                "iteration": iteration_num,
                "fom": fom if fom is not None else -1e9,
                "success": success,
                "rows": rows,
                "cols": cols,
                "num_arrays": num_arrays,
                "pg_width": params.get("pg_width", 0),
                "pd_width": params.get("pd_width", 0),
                "pu_width": params.get("pu_width", 0),
                "length": params.get("length", 0),
                "nmos_model_name": params.get("nmos_model_name", ""),
                "pmos_model_name": params.get("pmos_model_name", ""),
            }
            if success and result:
                record.update(
                    {
                        "min_snm": result.get("min_snm", 0),
                        "hold_snm": result.get("hold_snm", 0),
                        "read_snm": result.get("read_snm", 0),
                        "write_snm": result.get("write_snm", 0),
                        "read_delay": result.get("read_delay", 0),
                        "write_delay": result.get("write_delay", 0),
                        "max_delay": max(result.get("read_delay", 0), result.get("write_delay", 0)),
                        "read_power": result.get("read_power", 0),
                        "write_power": result.get("write_power", 0),
                        "max_power": result.get("max_power", 0),
                        "total_area": result.get("total_area", 0),
                    }
                )
            if objectives:
                record["objective_0"] = objectives[0] if len(objectives) > 0 else 0
                record["objective_1"] = objectives[1] if len(objectives) > 1 else 0
                record["objective_2"] = objectives[2] if len(objectives) > 2 else 0
            if constraints:
                record["constraint_0"] = constraints[0] if len(constraints) > 0 else 0
                record["constraint_1"] = constraints[1] if len(constraints) > 1 else 0

            self.joint_iteration_history.append(record)
            self._append_iteration_csv("joint", record, label="joint")

            config = {"rows": rows, "cols": cols, "num_arrays": num_arrays, "array_capacity": array_capacity}
            return fom, objectives, constraints, result, success, config, params

        def joint_eval_fn(x):
            fom, objectives, constraints, result, success, config, params = _evaluate_joint(x)
            return fom, {"config": config, "params": params, "result": result, "success": success}

        def joint_eval_backend(x):
            fom, objectives, constraints, result, success, config, params = _evaluate_joint(x)
            if objectives is None:
                objectives = [fom, 0.0, 0.0]
            if constraints is None:
                constraints = [1.0, 1.0]
            if success and result:
                if "merit" not in result:
                    result["merit"] = fom
                if "fom" not in result:
                    result["fom"] = fom
            return objectives, constraints, result, success

        if algorithm == "SA":
            param_dim = int(self.param_space.bounds.shape[1])
            total_dim = param_dim + 2
            bounds = (np.zeros(total_dim), np.ones(total_dim))
            initial_solution = np.random.rand(total_dim)
            if total_dim >= 2:
                initial_solution[0] = 0.0
                initial_solution[1] = 0.0

            sa_optimizer = SAOptimizer(evaluation_function=joint_eval_fn, bounds=bounds, maximize=True)
            best_solution, best_fom, best_result = sa_optimizer.optimize_continuous(initial_solution, max_iter=max_iter)

            best_config = None
            best_params = None
            decoded_best = self._decode_joint_vector(best_solution)
            if decoded_best is not None:
                rows, cols, num_arrays, params, array_capacity, row_idx, col_idx = decoded_best
                best_config = {"rows": rows, "cols": cols, "num_arrays": num_arrays, "array_capacity": array_capacity}
                best_params = params

            self.joint_results = {
                "best_config": best_config,
                "best_params": best_params,
                "best_fom": best_fom,
                "best_result": best_result,
                "history": sa_optimizer.history,
                "algorithm": algorithm,
            }
            return self.joint_results

        problem = (joint_param_space, joint_eval_backend, None)
        ret = None
        if algorithm == "PSO":
            from size_optimization import demo_pso

            ret = demo_pso.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        elif algorithm == "SMAC":
            from size_optimization import demo_smac

            ret = demo_smac.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        elif algorithm == "CBO":
            from size_optimization import demo_cbo

            ret = demo_cbo.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        elif algorithm == "RoSE_Opt":
            from size_optimization import demo_roseopt

            ret = demo_roseopt.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        elif algorithm == "MOEAD":
            from size_optimization import demo_moead

            ret = demo_moead.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        elif algorithm == "MOBO":
            from size_optimization import demo_mobo

            ret = demo_mobo.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        elif algorithm == "NSGA-II":
            from size_optimization import demo_nsgaii

            ret = demo_nsgaii.main("config_sram.yaml", problem=problem, max_iter=max_iter)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        best_params = ret.get("params") if isinstance(ret, dict) else None
        best_result = ret.get("result") if isinstance(ret, dict) else None
        best_fom = ret.get("merit") if isinstance(ret, dict) else None
        best_config = None
        if isinstance(best_params, dict) and ("rows" in best_params) and ("cols" in best_params):
            rows = best_params["rows"]
            cols = best_params["cols"]
            array_capacity = rows * cols
            if self.arch_space.total_bits % array_capacity == 0:
                num_arrays = self.arch_space.total_bits // array_capacity
                best_config = {"rows": rows, "cols": cols, "num_arrays": num_arrays, "array_capacity": array_capacity}

        self.joint_results = {
            "best_config": best_config,
            "best_params": best_params,
            "best_fom": best_fom,
            "best_result": best_result,
            "algorithm": algorithm,
        }
        return self.joint_results


def main():
    """
    Main function to run joint optimization
    运行联合优化的主函数
    """
    print("\n" + "=" * 60)
    print("Joint SRAM Optimization")
    print("联合SRAM优化")
    print("=" * 60)

    print("Using real 6T cell + peripheral circuits.")

    max_iter_input = input("Enter the maximum number of iterations for joint optimization (default=40): ").strip()
    try:
        max_iter = int(max_iter_input) if max_iter_input else 40
    except ValueError:
        max_iter = 40
        print("Invalid input. Default to 40.")

    print(f"Maximum number of iterations for joint optimization: {max_iter}")

    algorithm_raw = input("Select algorithm for joint optimization (1=SA, 2=PSO, 3=SMAC, 4=CBO, 5=RoSE_Opt, 6=MOEAD, 7=MOBO, 8=NSGA-II, default=1): ").strip()
    algorithm_norm = algorithm_raw.replace("-", "_").strip()
    algorithm_map = {"1": "SA", "2": "PSO", "3": "SMAC", "4": "CBO", "5": "RoSE_Opt", "6": "MOEAD", "7": "MOBO", "8": "NSGA-II"}
    if not algorithm_norm:
        algorithm = "SA"
    elif algorithm_norm in algorithm_map:
        algorithm = algorithm_map[algorithm_norm]
    else:
        upper = algorithm_norm.upper()
        if upper in {"SA", "PSO", "SMAC", "CBO"}:
            algorithm = upper
        elif upper in {"ROSE_OPT", "ROSEOPT"}:
            algorithm = "RoSE_Opt"
        elif upper in {"MOEAD"}:
            algorithm = "MOEAD"
        elif upper in {"MOBO"}:
            algorithm = "MOBO"
        elif upper in {"NSGA_II", "NSGAII", "NSGA-II"}:
            algorithm = "NSGA-II"
        else:
            algorithm = "SA"
            print("Invalid algorithm input. Default to SA.")

    print(f"Joint optimization algorithm: {algorithm}")

    optimizer = JointOptimizer(seed=42)

    results = optimizer.run_joint_optimization(max_iter=max_iter, algorithm=algorithm)

    return results


if __name__ == "__main__":
    main()
