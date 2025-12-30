from PySpice.Spice.Netlist import SubCircuitFactory, SubCircuit, Circuit
from PySpice.Unit import u_Ohm, u_pF
from pathlib import Path

class BaseSubcircuit(SubCircuit):
    ###6T SRAM Cell SubCircuitFactory with debug capabilities###
    NAME = 'BASE_SUBCKT'
    # The first and second nodes are always power and ground nodes,VDD and VSS
    NODES = ('VDD', 'VSS')
    
    def __init__(self, # Receive transistor and RC parameters
                 nmos_model_name, pmos_model_name,
                 base_nmos_width, base_pmos_width, length,
                 w_rc, pi_res, pi_cap,param_file="sram_compiler/param_sweep_data/param_sweep_model_name.txt"
                 ):
        super().__init__(self.NAME, *self.NODES)
        
        self.nmos_pdk_model = nmos_model_name # Store transistor model name
        self.pmos_pdk_model = pmos_model_name
        print(f"\n[DEBUG] Creating {self.name} with models: "
              f"NMOS={self.nmos_pdk_model}, PMOS={self.pmos_pdk_model}")

        # Transistor Sizes (FreePDK45 uses nanometers)
        self.base_nmos_width = base_nmos_width # Store transistor parameters
        self.base_pmos_width = base_pmos_width
        self.length = length

        # use RC?
        self.w_rc = w_rc # Store RC parasitic parameters
        self.pi_res = pi_res
        self.pi_cap = pi_cap
        # Normalize parameter file path to an absolute path based on sram_compiler root
        self.param_file = self._normalize_param_file_path(param_file)

    def _normalize_param_file_path(self, param_file):
        """
        Normalize the parameter file path to an absolute path:
        - If absolute, return directly
        - If starts with "sram_compiler", resolve relative to the sram_compiler directory
        - Otherwise, look for the relative path under sram_compiler
        - If not found, fallback to project root + original relative path
        """
        pf = Path(param_file)
        sram_compiler_dir = Path(__file__).resolve().parents[1]  # .../sram_compiler

        if pf.is_absolute():
            return str(pf)

        # Remove sram_compiler prefix to avoid duplicate concatenation
        parts = pf.parts
        if len(parts) > 0 and parts[0] == "sram_compiler":
            rel = Path(*parts[1:])
        else:
            rel = pf

        candidate = sram_compiler_dir / rel
        if candidate.exists():
            return str(candidate)

        # Fallback: project root + original relative path (for different working dirs)
        repo_root = sram_compiler_dir.parent
        fallback = repo_root / pf
        return str(fallback)
    def add_rc_networks_to_node(self, in_node, num_segs=1, end_name=None): # Add RC networks to a node
        ###Add RC networks to the SRAM cell###
        start_node = in_node # Start node for each segment
        end_node = start_node # End node for each segment

        for i in range(num_segs):
            if num_segs-1 == i: # Last segment
                if end_name:    # Use provided end node name if available
                    end_node = end_name
                else:           # Otherwise, append '_end' to the start node
                    end_node = in_node + '_end' 
            else:
                end_node = start_node + f'_seg{i}' # Intermediate node name

            self.R(f'R_{in_node}_{i}',  start_node, end_node, self.pi_res)
            self.C(f'Cg_{in_node}_{i}', end_node, self.gnd, self.pi_cap)
            start_node = end_node   # Update start node for next segment
            # Example output: RR_BL_0 BL BL_end 100Ohm  CCg_BL_0 BL_end 0 0.001pF
        
        return end_node

    def read_mos_model_from_param_file(self,names):
        """
        Read MOS model names from parameter sweep file.
        """
        try:
            with open(self.param_file, 'r') as f:
                lines = f.readlines()
                # Assume first line is header, second line is data
                if len(lines) >= 2:
                    header = lines[0].strip().split()
                    values = lines[1].strip().split()
                    models = {}
                    for key in names:
                        if key not in header:
                            raise ValueError(f"Missing required column: {key}")
                        index = header.index(key)
                        models[key.split('_')[0]] = values[index]  # Keep pmos/nmos as keys
                    return models
        except FileNotFoundError:
            raise FileNotFoundError(f"Parameter file '{self.param_file}' not found.")
        except Exception as e:
            raise ValueError(f"Error parsing parameter file: {e}")
        raise ValueError("Could not find 'pmos_model_precharge' in parameter file.")
