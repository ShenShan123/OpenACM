import yaml
import os
from typing import List, Dict, Union, Any, Optional


class AttrDict:
    """Dictionary class supporting dot-access"""

    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                # If value is a dict, recursively convert to AttrDict
                setattr(self, key, AttrDict(value))
            elif isinstance(value, list):
                # Convert dicts inside lists to AttrDict
                setattr(self, key, [AttrDict(item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)

    def __repr__(self):
        return str(self.__dict__)


class GlobalConfig:
    """Global configuration with dot-access to nested attributes"""

    def __init__(self, config_data: Dict[str, Any]):
        # Basic configuration
        self.vdd = config_data.get("vdd", 1.0)
        self.temperature = config_data.get("temperature", 27)
        self.num_rows = config_data.get("num_rows", 32)
        self.num_cols = config_data.get("num_cols", 1)
        self.monte_carlo_runs = config_data.get("monte_carlo_runs", 1)
        self.timeout = config_data.get("timeout", 120)
        self.choose_columnmux = config_data.get("choose_columnmux", False)
        self.pdk_path_TT = config_data.get("pdk_path_TT", "tran_models/models_TT.spice")
        self.pdk_path_FF = config_data.get("pdk_path_FF", "tran_models/models_FF.spice")
        self.pdk_path_SS = config_data.get("pdk_path_SS", "tran_models/models_SS.spice")
        self.pdk_path_FS = config_data.get("pdk_path_FS", "tran_models/models_FS.spice")
        self.pdk_path_SF = config_data.get("pdk_path_SF", "tran_models/models_SF.spice")
        # Convert nested dicts into dot-accessible objects
        self.evaluator = AttrDict(config_data.get("evaluator", {}))
        self.simulator = AttrDict(config_data.get("simulator", {}))
        self.objectives = AttrDict(config_data.get("objectives", {}))

        # Special handling for performance metrics
        self.metrics = self._process_performance_metrics(config_data.get("performance_metrics", {}))

        # Normalize metric bounds
        self._normalize_metric_bounds()

    def _process_performance_metrics(self, metrics_dict: dict) -> AttrDict:
        """Process performance metrics into a dot-accessible structure"""
        metrics = {}
        for metric_name, metric_data in metrics_dict.items():
            # Create a dot-accessible metric object
            metric_obj = AttrDict(metric_data)

            # Special handling for names attribute
            if hasattr(metric_obj, 'names') and not isinstance(metric_obj.names, list):
                metric_obj.names = [metric_obj.names]

            metrics[metric_name] = metric_obj

        # Return a dot-accessible metrics dict
        return AttrDict(metrics)

    def _normalize_metric_bounds(self):
        """Normalize metric bounds; supports scalars and lists"""
        if not hasattr(self, 'metrics'):
            return

        # Iterate over all metrics
        for metric_name in dir(self.metrics):
            if metric_name.startswith('__'):
                continue

            metric = getattr(self.metrics, metric_name)

            # Handle upper bound
            if hasattr(metric, 'upper'):
                upper = metric.upper
                if isinstance(upper, (int, float)):
                    metric.upper = [upper]
                elif not isinstance(upper, list):
                    metric.upper = [upper]

            # Handle lower bound
            if hasattr(metric, 'lower'):
                lower = metric.lower
                if isinstance(lower, (int, float)):
                    metric.lower = [lower]
                elif not isinstance(lower, list):
                    metric.lower = [lower]

    def __repr__(self):
        """Return string representation of the configuration"""
        return (
            f"GlobalConfig:\n"
            f"  VDD: {self.vdd} V\n"
            f"  Temperature: {self.temperature} °C\n"
            f"  Array: {self.num_rows}×{self.num_cols}\n"
            f"  Monte Carlo runs: {self.monte_carlo_runs}\n"
            f"  Timeout: {self.timeout} s\n"
            f"  PDK TT path: {self.pdk_path_TT}\n"
            f"  PDK FF path: {self.pdk_path_FF}\n"
            f"  PDK SS path: {self.pdk_path_SS}\n"
            f"  PDK FS path: {self.pdk_path_FS}\n"
            f"  PDK SF path: {self.pdk_path_SF}\n"
            f"  Performance metrics: {list(vars(self.metrics).keys() if hasattr(self, 'metrics') else [])}\n"
            f"  Objective formula: {getattr(self.objectives, 'formula', 'undefined')}"
        )

    def get_metric(self, metric_name: str) -> Any:
        """Get configuration for a given performance metric"""
        if hasattr(self, 'metrics') and hasattr(self.metrics, metric_name):
            return getattr(self.metrics, metric_name)
        return None

    def get_metric_names(self) -> List[str]:
        """Get all performance metric names"""
        if hasattr(self, 'metrics'):
            return [name for name in dir(self.metrics) if not name.startswith('__')]
        return []

    def get_objective_formula(self) -> str:
        """Get objective formula"""
        return getattr(self.objectives, 'formula', '')

    def get_constraints(self) -> List[str]:
        """Get constraints"""
        constraints = getattr(self.objectives, 'constraints', [])
        # Convert string constraint to list
        if isinstance(constraints, str):
            return [constraints]
        return constraints
# Global configuration loader function
def load_global_config(file_path: str) -> GlobalConfig:
    """Load global configuration file"""
    try:
        # Try different encodings when opening the file
        for encoding in ['utf-8', 'utf-8-sig', 'gbk']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    config_data = yaml.safe_load(f)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"Unable to decode file {file_path}, tried encodings: utf-8, utf-8-sig, gbk")

        # Create global configuration object
        return GlobalConfig(config_data)

    except Exception as e:
        print(f"Error loading global configuration file {file_path}: {e}")
        raise


# Generic parameter class
class Parameter:
    """Represents a design parameter"""

    def __init__(
            self,
            name: str,
            param_type: str,
            instance_names: Union[str, List[str]],
            description: str,
            value: Any,
            upper: Optional[Union[float, List[float]]] = None,
            lower: Optional[Union[float, List[float]]] = None,
            choices: Optional[List[str]] = None
    ):
        self.name = name
        self.param_type = param_type
        self.instance_names = instance_names
        self.description = description
        self.value = value
        self.upper = upper
        self.lower = lower
        self.choices = choices
        self._validate_types()

    def _validate_types(self):
        """Validate parameter type consistency"""
        # Check value type matches parameter type
        if "scalar" in self.param_type:
            if isinstance(self.value, list):
                raise ValueError(f"Scalar parameter {self.name} cannot have a list value")
        elif "list" in self.param_type:
            if not isinstance(self.value, list):
                raise ValueError(f"List parameter {self.name} requires a list value")

        # Check bound types match
        if self.upper is not None:
            if "continuous" in self.param_type:
                if "scalar" in self.param_type:
                    if not isinstance(self.upper, (float, int)) or not isinstance(self.lower, (float, int)):
                        raise TypeError(f"Continuous scalar parameter {self.name} bounds must be numeric")
                else:
                    if not isinstance(self.upper, list) or not isinstance(self.lower, list):
                        raise TypeError(f"Continuous list parameter {self.name} bounds must be lists")
            else:
                raise ValueError(f"Discrete parameter {self.name} should not have numeric bounds")

        # Check choices for discrete parameters
        if self.choices is not None:
            if "categorical" not in self.param_type and "discrete" not in self.param_type:
                raise ValueError(f"Non-discrete parameter {self.name} should not have choices")

    def __repr__(self):
        return (f"<Parameter {self.name} ({self.param_type}): "
                f"instances={self.instance_names}, value={self.value}>")


# Generic circuit configuration class
class CircuitConfig:
    """Represents the full configuration of a circuit"""

    def __init__(self, config_name: str, parameters: Dict[str, Parameter]):
        self.config_name = config_name
        self.parameters = parameters

    def get_parameter(self, name: str) -> Parameter:
        """Get parameter by name"""
        return self.parameters[name]

    def __getattr__(self, name: str) -> Parameter:
        """Allow attribute-style access to parameters"""
        if name in self.parameters:
            return self.parameters[name]
        raise AttributeError(f"No such parameter in {self.config_name} config: {name}")

    def __repr__(self):
        params = "\n  ".join([f"{k}: {v}" for k, v in self.parameters.items()])
        return f"{self.config_name} config:\n  {params}"


class ConfigLoader:
    """Load and manage multiple circuit configurations"""

    def __init__(self):
        self.configs = {}

    def load_config(self, file_path: str, config_name: str) -> CircuitConfig:
        """Load a single configuration file"""
        try:
            # Try different encodings when opening the file
            for encoding in ['utf-8', 'utf-8-sig', 'gbk']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        config_data = yaml.safe_load(f)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Unable to decode file {file_path}, tried encodings: utf-8, utf-8-sig, gbk")

            # Extract circuit config section
            circuit_config = config_data.get(config_name, {})
            if not circuit_config:
                raise ValueError(f"Configuration {config_name} not found in YAML file")

            # Parse parameters
            parameters = {}
            for param_name, param_data in circuit_config.get("parameters", {}).items():
                param = Parameter(
                    name=param_name,
                    param_type=param_data["type"],
                    instance_names=param_data["names"],
                    description=param_data["description"],
                    value=param_data["value"],
                    upper=param_data.get("upper"),
                    lower=param_data.get("lower"),
                    choices=param_data.get("choices")
                )
                parameters[param_name] = param

            # Create and store configuration object
            config = CircuitConfig(config_name, parameters)
            self.configs[config_name] = config
            return config

        except Exception as e:
            print(f"Error loading configuration file {file_path}: {e}")
            raise

    def get_config(self, config_name: str) -> CircuitConfig:
        """Get a loaded configuration"""
        if config_name in self.configs:
            return self.configs[config_name]
        raise KeyError(f"Configuration not found: {config_name}")

    def load_all_configs(self, config_list: Dict[str, str]):
        """Load multiple configurations in batch"""
        for config_name, file_path in config_list.items():
            try:
                self.load_config(file_path, config_name)
                print(f"✓ Loaded {config_name} configuration successfully")
            except Exception as e:
                print(f"⚠ Failed to load {config_name} configuration: {e}")




# Top-level SRAM_CONFIG class
class SRAM_CONFIG:
    """Top-level class integrating all SRAM-related configurations"""

    def __init__(self):
        self.global_config = None
        self.sram_6t_cell = None
        self.wordline_driver = None
        self.precharge = None
        self.column_mux = None
        self.senseamp = None
        self.write_driver = None
        self.decoder = None

    def load_all_configs(self, global_file: str, circuit_configs: Dict[str, str]):
        """Load all configurations"""

        try:
            self.global_config = load_global_config(global_file)
            print(f"✓ Global configuration loaded: {global_file}")
            loader = ConfigLoader()
            print("\nStarting to load circuit configurations:")
            loader.load_all_configs(circuit_configs)
            self.sram_6t_cell = loader.get_config("SRAM_6T_CELL")
            self.wordline_driver = loader.get_config("WORDLINEDRIVER")
            self.precharge = loader.get_config("PRECHARGE")
            self.column_mux = loader.get_config("COLUMNMUX")
            self.senseamp = loader.get_config("SENSEAMP")
            self.write_driver = loader.get_config("WRITEDRIVER")
            self.decoder = loader.get_config("DECODER")
            print("\nAll configurations loaded!")
            return
        except Exception:
            pass

        current_dir = os.path.dirname(os.path.abspath(__file__))
        tm1 = os.path.join(current_dir, "tran_models")
        tm2 = os.path.join(current_dir, "..", "..", "level2_transistor", "sram_sizing", "tran_models")
        tm_path = tm1 if os.path.exists(os.path.join(tm1, "models_TT.spice")) else tm2

        global_defaults = {
            "vdd": 1.0,
            "temperature": 27,
            "num_rows": 32,
            "num_cols": 1,
            "monte_carlo_runs": 1,
            "timeout": 120,
            "choose_columnmux": False,
            "pdk_path_TT": os.path.join(tm_path, "models_TT.spice"),
            "pdk_path_FF": os.path.join(tm_path, "models_FF.spice"),
            "pdk_path_SS": os.path.join(tm_path, "models_SS.spice"),
            "pdk_path_FS": os.path.join(tm_path, "models_FS.spice"),
            "pdk_path_SF": os.path.join(tm_path, "models_SF.spice"),
            "evaluator": {},
            "simulator": {},
            "objectives": {},
            "performance_metrics": {},
        }
        self.global_config = GlobalConfig(global_defaults)

        nmos_choices = ["NMOS_VTL", "NMOS_VTG", "NMOS_VTH"]
        pmos_choices = ["PMOS_VTL", "PMOS_VTG", "PMOS_VTH"]

        sram6t_params = {
            "pmos_width": Parameter("pmos_width", "continuous scalar", "pu", "", 0.09e-6),
            "nmos_width": Parameter("nmos_width", "continuous list", ["pd", "pg"], "", [2.05e-7, 1.35e-7]),
            "length": Parameter("length", "continuous scalar", "l", "", 50e-9),
            "nmos_model": Parameter("nmos_model", "categorical list", ["pd", "pg"], "", ["NMOS_VTG", "NMOS_VTG"], choices=nmos_choices),
            "pmos_model": Parameter("pmos_model", "categorical scalar", "pu", "", "PMOS_VTG", choices=pmos_choices),
        }
        self.sram_6t_cell = CircuitConfig("SRAM_6T_CELL", sram6t_params)

        wl_params = {
            "pmos_width": Parameter("pmos_width", "continuous list", ["nand", "inv"], "", [0.27e-6, 0.27e-6]),
            "nmos_width": Parameter("nmos_width", "continuous list", ["nand", "inv"], "", [0.18e-6, 0.09e-6]),
            "length": Parameter("length", "continuous scalar", "l", "", 0.05e-6),
            "nmos_model": Parameter("nmos_model", "categorical list", ["nand", "inv"], "", ["NMOS_VTG", "NMOS_VTG"], choices=nmos_choices),
            "pmos_model": Parameter("pmos_model", "categorical list", ["nand", "inv"], "", ["PMOS_VTG", "PMOS_VTG"], choices=pmos_choices),
        }
        self.wordline_driver = CircuitConfig("WORDLINEDRIVER", wl_params)

        pr_params = {
            "pmos_width": Parameter("pmos_width", "continuous scalar", "pu", "", 0.27e-6),
            "length": Parameter("length", "continuous scalar", "l", "", 0.05e-6),
            "pmos_model": Parameter("pmos_model", "categorical scalar", "pu", "", "PMOS_VTG", choices=pmos_choices),
        }
        self.precharge = CircuitConfig("PRECHARGE", pr_params)

        cm_params = {
            "nmos_width": Parameter("nmos_width", "continuous scalar", "pd", "", 0.18e-6),
            "pmos_width": Parameter("pmos_width", "continuous scalar", "pu", "", 0.27e-6),
            "length": Parameter("length", "continuous scalar", "l", "", 0.05e-6),
            "nmos_model": Parameter("nmos_model", "categorical scalar", "n", "", "NMOS_VTG", choices=nmos_choices),
            "pmos_model": Parameter("pmos_model", "categorical scalar", "p", "", "PMOS_VTG", choices=pmos_choices),
        }
        self.column_mux = CircuitConfig("COLUMNMUX", cm_params)

        sa_params = {
            "nmos_width": Parameter("nmos_width", "continuous scalar", "pd", "", 0.18e-6),
            "pmos_width": Parameter("pmos_width", "continuous scalar", "pu", "", 0.27e-6),
            "length": Parameter("length", "continuous scalar", "l", "", 0.05e-6),
            "nmos_model": Parameter("nmos_model", "categorical scalar", "n", "", "NMOS_VTG", choices=nmos_choices),
            "pmos_model": Parameter("pmos_model", "categorical scalar", "p", "", "PMOS_VTG", choices=pmos_choices),
        }
        self.senseamp = CircuitConfig("SENSEAMP", sa_params)

        wd_params = {
            "nmos_width": Parameter("nmos_width", "continuous scalar", "pd", "", 0.18e-6),
            "pmos_width": Parameter("pmos_width", "continuous scalar", "pu", "", 0.27e-6),
            "length": Parameter("length", "continuous scalar", "l", "", 0.05e-6),
            "nmos_model": Parameter("nmos_model", "categorical scalar", "n", "", "NMOS_VTG", choices=nmos_choices),
            "pmos_model": Parameter("pmos_model", "categorical scalar", "p", "", "PMOS_VTG", choices=pmos_choices),
        }
        self.write_driver = CircuitConfig("WRITEDRIVER", wd_params)

        dec_params = {
            "pmos_width": Parameter("pmos_width", "continuous list", ["nand", "inv"], "", [0.27e-6, 0.27e-6]),
            "nmos_width": Parameter("nmos_width", "continuous list", ["nand", "inv"], "", [0.18e-6, 0.09e-6]),
            "length": Parameter("length", "continuous scalar", "l", "", 0.05e-6),
            "nmos_model": Parameter("nmos_model", "categorical list", ["nand", "inv"], "", ["NMOS_VTG", "NMOS_VTG"], choices=nmos_choices),
            "pmos_model": Parameter("pmos_model", "categorical list", ["nand", "inv"], "", ["PMOS_VTG", "PMOS_VTG"], choices=pmos_choices),
        }
        self.decoder = CircuitConfig("DECODER", dec_params)

    # def get_all_configs(self) -> Dict[str, Any]:
    #     """Return a dictionary of all configurations"""
    #     return {
    #         "global": self.global_config,
    #         "sram_6t_cell": self.sram_6t_cell,
    #         "wordline_driver": self.wordline_driver,
    #         "precharge": self.precharge,
    #         "column_mux": self.column_mux,
    #         "sense_amp": self.sense_amp,
    #         "write_driver": self.write_driver
    #     }

    def __repr__(self):
        """Return a concise summary of configuration loading status"""
        configs = [
            f"Global config: {self.global_config is not None}",
            f"SRAM cell: {self.sram_6t_cell is not None}",
            f"Wordline driver: {self.wordline_driver is not None}",
            f"Precharge: {self.precharge is not None}",
            f"Column mux: {self.column_mux is not None}",
            f"Sense amplifier: {self.senseamp is not None}",
            f"Write driver: {self.write_driver is not None}",
            f"Decoder: {self.decoder is not None}"
        ]
        return "SRAM configuration status:\n  " + "\n  ".join(configs)





# Usage example at file end
if __name__ == "__main__":
    # Create SRAM configuration manager
    sram_config = SRAM_CONFIG()

    # Define configuration file paths
    global_file = "yaml/global.yaml"
    circuit_files = {
        "SRAM_6T_CELL": "yaml/sram_6t_cell.yaml",
        "WORDLINEDRIVER": "yaml/wordline_driver.yaml",
        "PRECHARGE": "yaml/precharge.yaml",
        "COLUMNMUX": "yaml/mux.yaml",
        "SENSEAMP": "yaml/sa.yaml",
        "WRITEDRIVER": "yaml/write_driver.yaml",
        "DECODER":"yaml/decoder.yaml"
    }

    # Load all configurations
    sram_config.load_all_configs(global_file, circuit_files)
    # Print configuration status
    print("\nConfiguration status summary:")
    print(sram_config)

    # Access specific configurations
    print("\nAccess SRAM cell parameters:")
    sram_cell = sram_config.sram_6t_cell
    if sram_cell:
        print(f"PMOS width: {sram_cell.pmos_width.value} m")
        print(f"NMOS width: PD={sram_cell.nmos_width.value[0]}m, PG={sram_cell.nmos_width.value[1]}m")
        print(f"Channel length: {sram_cell.length.value} m")

    # Access sense amplifier configuration
    print("\nAccess sense amplifier parameters:")
    sense_amp = sram_config.senseamp
    if sense_amp:
        first_param = list(sense_amp.parameters.values())[0]
        print(f"First parameter: {first_param.name} = {first_param.value}")

    print(sram_config.global_config.evaluator.class_name)
    print(sram_config.global_config.metrics.snm.type)
    print(sram_config.senseamp.length.param_type)
    print(sram_config.precharge.pmos_model.value)
    print(sram_config.decoder.pmos_width.value)
