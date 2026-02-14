"""
SRAM Circuit Optimization using NSGA-II
使用NSGA-II算法的SRAM电路多目标优化
优化目标: SNM(最大化), 功耗(最小化), 面积(最小化), 延时(最小化)
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

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from size_optimization.exp_utils import (
    seed_set, create_directories, evaluate_sram, ModifiedSRAMParameterSpace,
    OptimizationLogger, get_default_transistor_features
)
from utils import estimate_bitcell_area

# Import NSGA-II module
# from size_optimization.NSGA_II.evolution import Evolution
sys.path.append(os.path.join(project_root, 'size_optimization', 'NSGA-II'))
from evolution import Evolution

# Define Problem class for NSGA-II
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
        # from size_optimization.NSGA_II.population import Individual
        # from population import Individual
        import sys
        if os.path.join(project_root, 'size_optimization', 'NSGA-II') not in sys.path:
            sys.path.append(os.path.join(project_root, 'size_optimization', 'NSGA-II'))
        
        # 尝试直接从 individual 模块导入，如果失败则尝试从 population 模块导入（虽然 Individual 定义在 individual.py）
        try:
            from individual import Individual
        except ImportError:
            try:
                from population import Individual
            except ImportError:
                # 最后的手段：手动定义一个简单的 Individual 类，如果原来的太复杂无法导入
                class Individual:
                    def __init__(self, features=None):
                        self.features = features
                        self.objectives = []
                        self.dominated_solutions = []
                        self.domination_count = 0
                        self.rank = 0
                        self.crowding_distance = 0
                        
                    def dominates(self, other_individual):
                        and_condition = True
                        or_condition = False
                        for first, second in zip(self.objectives, other_individual.objectives):
                            if first > second:
                                and_condition = False
                            if first < second:
                                or_condition = True
                        return (and_condition and or_condition)
        
        if self._first_individual and self.default_features is not None:
            self._first_individual = False
            features = list(self.default_features)
        else:
            features = []
            for i in range(self.num_of_variables):
                lower, upper = self.variables_range[i]
                if self.variables_type[i] == 'int':
                    features.append(int(np.random.randint(int(lower), int(upper) + 1)))
                else:
                    features.append(float(np.random.uniform(float(lower), float(upper))))
        
        ind = Individual()
        ind.features = features
        return ind
        
    def calculate_objectives(self, individual):
        if self.expand:
            individual.objectives = [f(*individual.features) for f in self.objectives]
        else:
            individual.objectives = [f(individual.features) for f in self.objectives]

def main(config_path="config_sram.yaml", problem=None, max_iter=None, circuit_mode=1):
    """
    Main function for NSGA-II joint optimization
    """
    # log_dir = Path(project_root) / "results" / "nsgaii"
    # log_dir.mkdir(parents=True, exist_ok=True)
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # log_file = log_dir / f"nsgaii_output_{timestamp}.txt"
    
    # original_stdout = sys.stdout
    # log_fileobj = open(log_file, 'w', encoding='utf-8')
    # sys.stdout = Tee(original_stdout, log_fileobj)
    
    print("=" * 70)
    print("SRAM Joint Multi-Objective Optimization using NSGA-II")
    print("8输入: row_idx, col_idx + 6个晶体管参数")
    print("4目标: SNM, Power, Area, Delay")
    print("=" * 70)
    
    # NSGA-II parameters
    num_of_generations = max_iter if max_iter is not None else 800
    num_of_individuals = 1200
    
    gen_unused_cells = (circuit_mode == 1)
    
    # 设置日志文件
    # log_dir = Path(project_root) / "results" / "nsgaii"
    # log_dir.mkdir(parents=True, exist_ok=True)
    experiment_dir = Path(project_root) / "size_optimization" / "experiment" / "NSGA-II"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    
    # 确保基础 sim 目录存在
    create_directories()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    from size_optimization.experiment import ArchitectureConfigurationSpace, ModifiedSRAMParameterSpace
    
    arch_space = ArchitectureConfigurationSpace()
    param_space = ModifiedSRAMParameterSpace(config_path)
    default_vector, nmos_idx, pmos_idx = get_default_transistor_features(param_space)
    row_idx = arch_space.row_choices.index(16) if 16 in arch_space.row_choices else 0
    col_idx = arch_space.column_choices.index(16) if 16 in arch_space.column_choices else 0
    default_features = [
        row_idx,
        col_idx,
        default_vector[0],
        default_vector[1],
        default_vector[2],
        default_vector[3],
        nmos_idx,
        pmos_idx,
    ]
    
    evaluation_counter = {'count': 0}
    iteration_csv_tag = f"NSGAII_{num_of_generations}_{timestamp}"
    experiment_dir = Path(project_root) / "size_optimization" / "experiment" / "NSGA-II"
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
            stage_label="joint/NSGA-II", gen_unused_cells=gen_unused_cells
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
        
        if success and result:
            min_snm = result.get("min_snm", 0.0)
            max_power = result.get("max_power", 0.0)
            max_delay = result.get("max_delay", max(result.get("read_delay", 0.0), result.get("write_delay", 0.0)))
            area = result.get("total_area", result.get("area", 0.0) * num_arrays)
            nsga_objectives = [-min_snm, max_power, area, max_delay]
        else:
            nsga_objectives = [0.0, 1e3, 1e3, 1e3]

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
            
        record["objective_0"] = nsga_objectives[0]
        record["objective_1"] = nsga_objectives[1]
        record["objective_2"] = nsga_objectives[2]
        record["objective_3"] = nsga_objectives[3]
            
        if constraints:
            record["constraint_0"] = constraints[0] if len(constraints) > 0 else 0
            record["constraint_1"] = constraints[1] if len(constraints) > 1 else 0
            
        _append_iteration_csv(record)
        return nsga_objectives, constraints, result, success

    last_eval_params = {'params': None, 'results': None}
    
    def get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        params_key = (int(row_idx), int(col_idx), pu_width_norm, pd_width_norm, pg_width_norm, length_norm, int(nmos_idx), int(pmos_idx))
        if last_eval_params['params'] == params_key:
            return last_eval_params['results']
        
        objectives, constraints, result, success = evaluate_joint(
            row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx
        )
        
        results = objectives
            
        last_eval_params['params'] = params_key
        last_eval_params['results'] = results
        return results

    def f1_snm(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[0]
    
    def f2_power(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[1]
    
    def f3_area(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[2]
    
    def f4_delay(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx):
        return get_objectives_for_params(row_idx, col_idx, pu_width_norm, pd_width_norm, pg_width_norm, length_norm, nmos_idx, pmos_idx)[3]

    variables_range = [
        (0, len(arch_space.row_choices) - 1),
        (0, len(arch_space.column_choices) - 1),
        (0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0),
        (0, 2), (0, 2)
    ]
    variables_type = ['int', 'int', 'float', 'float', 'float', 'float', 'int', 'int']
    
    problem = Problem(
        objectives=[f1_snm, f2_power, f3_area, f4_delay],
        num_of_variables=8,
        variables_range=variables_range,
        variables_type=variables_type,
        expand=True,
        same_range=False,
        default_features=default_features
    )
    
    evolution = Evolution(
        problem=problem,
        num_of_generations=num_of_generations,
        num_of_individuals=num_of_individuals
    )
    
    print(f"\n开始 NSGA-II 优化...")
    pareto_front = evolution.evolve()
    
    # Save results
    output_dir = experiment_dir
    # output_dir = Path(current_dir) / 'experiment' / 'NSGA-II'
    # output_dir.mkdir(parents=True, exist_ok=True)
    
    pareto_solutions = []
    import torch
    
    # pareto_front 是 Individual 对象列表
    for idx, ind in enumerate(pareto_front):
        state = ind.features
        row_idx = int(state[0])
        col_idx = int(state[1])
        rows = arch_space.row_choices[row_idx]
        cols = arch_space.column_choices[col_idx]
        
        x_tensor = torch.tensor([state[2], state[3], state[4], state[5], state[6], state[6], state[7]], dtype=torch.float32)
        params = param_space.convert_params(x_tensor)
        
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
            
    print(f"NSGA-II pareto CSV saved to: {csv_path}")
    
    return {
        'algorithm': 'NSGA-II',
        'is_multiobjective': True,
        'pareto_solutions': pareto_solutions,
        'num_solutions': len(pareto_solutions),
        'iteration': num_of_generations
    }

if __name__ == "__main__":
    import argparse
    SEED = 1
    seed_set(seed=SEED)
    parser = argparse.ArgumentParser(description='NSGA-II多目标优化')
    parser.add_argument('--max_iter', type=int, default=800)
    parser.add_argument('--circuit_mode', type=int, default=1, choices=[1, 2])
    args = parser.parse_args()
    main(max_iter=args.max_iter, circuit_mode=args.circuit_mode)
