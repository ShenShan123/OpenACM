"""
SRAM Circuit Optimization using MOBO (Multi-Objective Bayesian Optimization)
使用MOBO算法的SRAM电路多目标优化
优化目标: SNM(最大化), 功耗(最小化), 延迟(最小化), 面积(最小化)
8维输入: row_idx, col_idx, pu_width, pd_width, pg_width, length, nmos_model_idx, pmos_model_idx
"""

import os
import sys
import time
import numpy as np
import warnings
import csv
from pathlib import Path
from datetime import datetime

warnings.filterwarnings('ignore')

if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

# Tee类：同时输出到终端和文件
class Tee:
    def __init__(self, *files):
        self.files = files
    
    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

# Import path handling
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utilities from exp_utils
from size_optimization.exp_utils import (
    seed_set, create_directories, evaluate_sram, ModifiedSRAMParameterSpace,
    OptimizationLogger, get_default_normalized_vector
)
from utils import estimate_bitcell_area

# Import MOBO module
# 假设 MOBO 代码在 size_optimization/MOBO 下
# from size_optimization.MOBO.bayesian_optimizer import BayesianOptimizer
sys.path.append(os.path.join(project_root, 'size_optimization', 'MOBO'))
from bayesian_optimizer import BayesianOptimizer
# Problem 类通常在算法模块中定义，如果 MOBO 没有自带 Problem 类，我们需要自己定义一个简单的
# 检查发现 MOBO 的 BayesianOptimizer 接受一个 problem 对象，该对象需要有 num_of_variables, objectives, variables_range 等属性
# 我们可以复用 moead.py 中的 Problem 定义，或者在这里定义一个简单的类

class Problem:
    def __init__(self, objectives, num_of_variables, variables_range, variables_type=None, expand=True, same_range=False, default_features=None):
        self.objectives = objectives
        self.num_of_variables = num_of_variables
        self.variables_range = variables_range
        self.variables_type = variables_type
        self.expand = expand
        self.same_range = same_range
        self.default_features = default_features
        self._first_individual = True
        
    def generate_individual(self):
        # 简单模拟 MOEAD 中的 Individual
        class Individual:
            def __init__(self, features):
                self.features = features

        if self._first_individual and self.default_features is not None:
            self._first_individual = False
            features = list(self.default_features)
        else:
            features = [
                np.random.randint(self.variables_range[i][0], self.variables_range[i][1] + 1)
                for i in range(self.num_of_variables)
            ]
        return Individual(features)
        
    @property
    def num_of_objectives(self):
        return len(self.objectives)


def main(config_path="config_sram.yaml", problem=None, max_iter=None, circuit_mode=1):
    """
    Main function for MOBO joint optimization
    MOBO联合优化主函数
    
    Parameters:
        config_path: Path to SRAM configuration file
        problem: Problem object tuple (parameter_space, eval_fn, constraints_fn) from experiment.py (not used directly here)
        max_iter: Maximum number of iterations
        circuit_mode: Circuit simulation mode
                     1 = Real Circuit
                     2 = Equivalent Model
    """
    # 设置日志文件
    # log_dir = Path(project_root) / "results" / "mobo"
    # log_dir.mkdir(parents=True, exist_ok=True)
    experiment_dir = Path(project_root) / "size_optimization" / "experiment" / "MOBO"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    
    # 确保基础 sim 目录存在
    create_directories()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # MOBO特定参数
    n_iterations = max_iter if max_iter is not None else 50
    n_initial = min(20, n_iterations // 2) # 初始采样
    
    # Circuit mode configuration
    gen_unused_cells = (circuit_mode == 1)
    
    print("=" * 70)
    print("SRAM Joint Multi-Objective Optimization using MOBO")
    print("SRAM联合多目标优化 - 使用MOBO算法")
    print("8输入: row_idx, col_idx + 6个晶体管参数")
    print("4目标: SNM, Power, Delay, Area")
    print("=" * 70)
    
    # Import architecture configuration space
    from size_optimization.experiment import ArchitectureConfigurationSpace, ModifiedSRAMParameterSpace
    
    arch_space = ArchitectureConfigurationSpace()
    param_space = ModifiedSRAMParameterSpace(config_path)
    default_vector = get_default_normalized_vector(param_space)
    def _model_index(param_name, fallback=0):
        dim_idx = 0
        for name, info in param_space.param_info.items():
            if info["type"] == "continuous_list":
                dim_idx += info["count"]
            elif info["type"] == "continuous_scalar":
                dim_idx += 1
            elif info["type"] == "categorical_list":
                if name == param_name:
                    choices = info.get("choices", [])
                    if not choices or dim_idx >= len(default_vector):
                        return fallback
                    idx = int(default_vector[dim_idx] * len(choices))
                    return max(0, min(idx, len(choices) - 1))
                dim_idx += info["count"]
        return fallback
    nmos_idx = _model_index("nmos_model", 0)
    pmos_idx = _model_index("pmos_model", 0)
    default_features = [
        0,
        0,
        default_vector[0] if len(default_vector) > 0 else 0.0,
        default_vector[1] if len(default_vector) > 1 else 0.0,
        default_vector[2] if len(default_vector) > 2 else 0.0,
        default_vector[3] if len(default_vector) > 3 else 0.0,
        nmos_idx,
        pmos_idx,
    ]
    
    # 创建评估缓存
    evaluation_cache = {}
    evaluation_counter = {'count': 0}
    iteration_csv_tag = f"MOBO_{n_iterations}_{timestamp}"
    experiment_dir = Path(project_root) / "size_optimization" / "experiment" / "MOBO"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    iteration_csv_path = experiment_dir / f"stage2_iterations_live_joint_{iteration_csv_tag}.csv"
    iteration_csv_fields = [
        "iteration", "fom", "success", "rows", "cols", "num_arrays",
        "pg_width", "pd_width", "pu_width", "length",
        "nmos_model_name", "pmos_model_name",
        "min_snm", "hold_snm", "read_snm", "write_snm",
        "read_delay", "write_delay", "max_delay",
        "read_power", "write_power", "max_power", "total_power",
        "single_array_area", "total_area",
        "objective_0", "objective_1", "objective_2", "objective_3",
        "constraint_0", "constraint_1",
    ]

    def _append_iteration_csv(record):
        if not record.get("success", False):
            return
        write_header = not iteration_csv_path.exists()
        with open(iteration_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=iteration_csv_fields)
            if write_header:
                writer.writeheader()
            writer.writerow({k: record.get(k, "") for k in iteration_csv_fields})
    
    def evaluate_joint(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        # 映射逻辑与 MOEAD 相同
        import torch
        x_norm = torch.tensor([
            pu_width_norm, pd_width_norm, pg_width_norm, length_norm,
            nmos_idx, nmos_idx, pmos_idx
        ], dtype=torch.float32)
        params = param_space.convert_params(x_norm)
        
        pu_width = params['pu_width']
        pd_width = params['pd_width']
        pg_width = params['pg_width']
        length = params['length']
        nmos_model_name = params['nmos_model_name']
        pmos_model_name = params['pmos_model_name']
        
        rows = arch_space.row_choices[int(row_idx)]
        cols = arch_space.column_choices[int(col_idx)]
        array_capacity = rows * cols
        num_arrays = arch_space.total_bits // array_capacity
        
        from size_optimization.experiment import evaluate_sram_with_config
        
        params_dict = {
            'pu_width': pu_width, 'pd_width': pd_width, 'pg_width': pg_width, 'length': length,
            'nmos_model_name': nmos_model_name, 'pmos_model_name': pmos_model_name
        }
        
        objectives, constraints, result, success = evaluate_sram_with_config(
            params_dict, num_rows=rows, num_cols=cols, num_arrays=num_arrays,
            stage_label="joint/MOBO", gen_unused_cells=gen_unused_cells
        )
        
        iteration_num = evaluation_counter["count"]
        evaluation_counter["count"] += 1
        
        fom = -10.0
        if success and result:
            max_delay = max(result.get("read_delay", 0), result.get("write_delay", 0))
            area = result.get("area", 0)
            min_snm = result.get("min_snm", 0)
            max_power = result.get("max_power", 0)
            if min_snm > 0 and max_power > 0 and area > 0 and max_delay > 0:
                fom = np.log10(min_snm / (max_power * np.sqrt(area) * max_delay))
        
        record = {
            "iteration": iteration_num, "fom": fom, "success": success,
            "rows": rows, "cols": cols, "num_arrays": num_arrays,
            "pg_width": params.get("pg_width"), "pd_width": params.get("pd_width"),
            "pu_width": params.get("pu_width"), "length": params.get("length"),
            "nmos_model_name": params.get("nmos_model_name"), "pmos_model_name": params.get("pmos_model_name"),
        }
        
        if success and result:
            total_power = result.get("total_power", result.get("max_power", 0))
            single_area = result.get("area", 0)
            total_area = result.get("total_area", single_area * num_arrays if single_area else 0)
            record.update({
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
                "total_power": total_power,
                "single_array_area": single_area,
                "total_area": total_area,
            })
            
        if objectives:
            # Note: MOBO记录所有目标
            record["objective_0"] = objectives[0] if len(objectives) > 0 else 0
            record["objective_1"] = objectives[1] if len(objectives) > 1 else 0
            record["objective_2"] = objectives[2] if len(objectives) > 2 else 0
            record["objective_3"] = objectives[3] if len(objectives) > 3 else 0
            
        if constraints:
            record["constraint_0"] = constraints[0] if len(constraints) > 0 else 0
            record["constraint_1"] = constraints[1] if len(constraints) > 1 else 0
            
        _append_iteration_csv(record)
        return objectives, constraints, result, success

    # 缓存机制
    last_eval_params = {'params': None, 'results': None}
    
    def get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        params_key = (int(row_idx), int(col_idx), pu_width_norm, pd_width_norm, pg_width_norm, length_norm, int(nmos_idx), int(pmos_idx))
        if last_eval_params['params'] == params_key:
            return last_eval_params['results']
        
        objectives, constraints, result, success = evaluate_joint(
            row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx
        )
        
        if success and result:
            min_snm = result.get('min_snm', 0.0)
            max_power = result.get('max_power', 1e-3)
            max_delay = result.get('max_delay', max(result.get("read_delay", 0), result.get("write_delay", 0)))
            rows = arch_space.row_choices[int(row_idx)]
            cols = arch_space.column_choices[int(col_idx)]
            num_arrays = arch_space.total_bits // (rows * cols)
            total_area = result.get('total_area', result.get('area', 0) * num_arrays)
            obj1 = -min_snm
            obj2 = max_power
            obj3 = max_delay
            obj4 = total_area
            results = [obj1, obj2, obj3, obj4]
        else:
            results = [0.0, 1e3, 1e3, 1e3]
            
        last_eval_params['params'] = params_key
        last_eval_params['results'] = results
        return results

    # 定义目标函数给 MOBO 调用
    def f1_snm(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[0]

    def f2_power(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[1]

    def f3_delay(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[2]

    def f4_area(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[3]

    variables_range = [
        (0, len(arch_space.row_choices) - 1),
        (0, len(arch_space.column_choices) - 1),
        (0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0),
        (0, 2), (0, 2)
    ]
    variables_type = ['int', 'int', 'float', 'float', 'float', 'float', 'int', 'int']
    
    # Create Problem with 4 objectives for MOBO
    problem = Problem(
        objectives=[f1_snm, f2_power, f3_delay, f4_area],
        num_of_variables=8,
        variables_range=variables_range,
        variables_type=variables_type,
        expand=True,
        same_range=False,
        default_features=default_features
    )
    
    # Initialize MOBO
    mobo = BayesianOptimizer(
        problem=problem,
        n_initial=n_initial,
        n_iterations=n_iterations - n_initial if n_iterations > n_initial else 0,
        n_candidates_per_iter=1000, # 稍微降低以加速
        mc_samples=50
    )
    
    print(f"\n开始 MOBO 优化...")
    pareto_individuals = mobo.optimize()
    
    # Save results
    output_dir = experiment_dir
    # output_dir = Path(current_dir) / 'experiment' / 'MOBO'
    # output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 Pareto CSV
    pareto_solutions = []
    import torch
    
    # pareto_individuals 是 Individual 对象列表
    for idx, ind in enumerate(pareto_individuals):
        state = ind.features
        # 解码
        row_idx = int(state[0])
        col_idx = int(state[1])
        rows = arch_space.row_choices[row_idx]
        cols = arch_space.column_choices[col_idx]
        
        x_tensor = torch.tensor([state[2], state[3], state[4], state[5], state[6], state[6], state[7]], dtype=torch.float32)
        params = param_space.convert_params(x_tensor)
        
        # 重新评估以获取完整结果（应该会命中缓存）
        # 注意：这里我们直接用 evaluate_joint 拿完整结果，而不是 get_objectives_for_params
        _, _, result, _ = evaluate_joint(
            state[0], state[1], state[2], state[3], state[4], state[5], state[6], state[7]
        )
        
        min_snm = result.get('min_snm', 0) if result else 0
        max_power = result.get('max_power', 0) if result else 0
        area = result.get('total_area', result.get('area', 0) * (arch_space.total_bits // (rows * cols))) if result else 0
        max_delay = result.get('max_delay', 0) if result else 0
        
        pareto_solutions.append({
            'solution_id': idx + 1,
            'rows': rows,
            'cols': cols,
            'num_arrays': arch_space.total_bits // (rows * cols),
            'pg_width': params.get("pg_width"),
            'pd_width': params.get("pd_width"),
            'pu_width': params.get("pu_width"),
            'length': params.get("length"),
            'nmos_model_name': params.get("nmos_model_name"),
            'pmos_model_name': params.get("pmos_model_name"),
            'min_snm': min_snm,
            'max_power': max_power,
            'area': area,
            'max_delay': max_delay
        })
        
    csv_path = output_dir / f"pareto_solutions_{timestamp}.csv"
    fieldnames = [
        "solution_id", "rows", "cols", "num_arrays",
        "pg_width", "pd_width", "pu_width", "length",
        "nmos_model_name", "pmos_model_name",
        "min_snm", "max_power", "area", "max_delay",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in pareto_solutions:
            writer.writerow(rec)
            
    print(f"MOBO pareto CSV saved to: {csv_path}")
    
    return {
        'algorithm': 'MOBO',
        'is_multiobjective': True,
        'pareto_solutions': pareto_solutions,
        'num_solutions': len(pareto_solutions),
        'iteration': n_iterations
    }

if __name__ == "__main__":
    import argparse
    SEED = 1
    seed_set(seed=SEED)
    parser = argparse.ArgumentParser(description='MOBO多目标优化')
    parser.add_argument('--max_iter', type=int, default=50)
    parser.add_argument('--circuit_mode', type=int, default=1, choices=[1, 2])
    args = parser.parse_args()
    main(max_iter=args.max_iter, circuit_mode=args.circuit_mode)
