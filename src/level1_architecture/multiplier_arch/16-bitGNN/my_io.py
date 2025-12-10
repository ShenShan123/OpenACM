import numpy as np
import pandas as pd 
import torch
from torch_geometric.data import Data
from gnn_predictor import predict_metrics

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def build_edge_index_from_adj_dict(adj_dict):
        """Build edge_index from an adjacency list (node indices start from 1 and are converted to 0-based)."""
        edges = []
        
        for source, targets in adj_dict.items():
            source_idx = source - 1
            
            for target in targets:
                target_idx = target - 1
                edges.append([source_idx, target_idx])
        
        if not edges:
            return torch.empty((2, 0), dtype=torch.long)
        
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        return edge_index

adj_dict = {
            1: [45, 46],
            2: [46, 47],
            3: [47, 48],
            17: [47, 48],
            4: [48, 49],
            18: [48, 49],
            5: [49, 50],
            19: [49, 50],
            29: [71, 72],
            6: [50, 51],
            20: [50, 51],
            30: [72, 73],
            7: [51, 52],
            21: [51, 52],
            31: [73, 74],
            37: [73, 74],
            8: [52, 53],
            22: [52, 53],
            32: [75, 76],
            38: [75, 76],
            9: [10, 53, 54],
            23: [24, 53, 54],
            33: [34, 75, 76],
            39: [75, 76],
            10: [11, 54, 55],
            24: [25, 54, 55],
            34: [35, 76, 77],
            40: [76, 77],
            11: [12, 55, 56],
            25: [26, 55, 56],
            35: [77, 78, 78],
            12: [13, 56, 57],
            26: [27, 56, 57],
            36: [78, 79],
            13: [14, 57, 58],
            27: [57, 58, 80],
            14: [15, 58, 59],
            28: [58, 59],
            15: [59, 60, 60],
            16: [60, 61],
            41: [87, 88],
            42: [88, 89],
            43: [89, 90],
            44: [90, 91],
            45: [91, 92],
            46: [92, 93],
            47: [93, 94],
            48: [94, 95],
            49: [95, 96],
            50: [96, 97],
            51: [97, 98],
            52: [98, 99],
            53: [54, 99, 100],
            54: [55, 100, 101],
            55: [56, 101, 102],
            56: [57, 102, 103],
            57: [58, 103, 104],
            58: [59, 104, 105],
            59: [60, 105, 106],
            60: [61, 106, 107],
            61: [62, 107, 108],
            62: [63, 108, 109],
            63: [110, 110, 110],
            64: [110, 111],
            65: [89, 90],
            66: [90, 91],
            67: [91, 92],
            68: [92, 93],
            69: [93, 94],
            70: [94, 95],
            71: [95, 96],
            72: [96, 97],
            73: [97, 98],
            74: [98, 99],
            75: [76, 99, 100],
            76: [77, 100, 101],
            77: [78, 101, 102],
            78: [79, 102, 103],
            79: [80, 103, 104],
            80: [81, 104, 105],
            81: [82, 105, 106],
            82: [83, 106, 107],
            83: [84, 107, 108],
            84: [108, 109],
            85: [114, 115],
            86: [115, 116],
            87: [116, 117],
            88: [117, 118],
            89: [118, 119],
            90: [119, 120],
            91: [120, 121],
            92: [121, 122],
            93: [122, 123],
            94: [123, 124],
            95: [124, 125],
            96: [125, 126],
            97: [126, 127],
            98: [127, 128],
            99: [100, 128, 129],
            100: [101, 129, 130],
            101: [102, 130, 131],
            102: [103, 131, 132],
            103: [104, 132, 133],
            104: [105, 133, 134],
            105: [106, 134, 135],
            106: [107, 135, 136],
            107: [108, 136, 137],
            108: [109, 137, 138],
            109: [110, 138, 139],
            110: [111, 139, 140],
            111: [112, 140, 141],
            112: [141, 142],
            113: [114],
            114: [115],
            115: [116],
            116: [117],
            117: [118],
            118: [119],
            119: [120],
            120: [121],
            121: [122],
            122: [123],
            123: [124],
            124: [125],
            125: [126],
            126: [127],
            127: [128],
            128: [129],
            129: [130],
            130: [131],
            131: [132],
            132: [133],
            133: [134],
            134: [135],
            135: [136],
            136: [137],
            137: [138],
            138: [139],
            139: [140],
            140: [141],
            141: [142],
            142: []
        }

edge_index = build_edge_index_from_adj_dict(adj_dict)

def generate_cartesian_indices(n_dims, device):
    return torch.cartesian_prod(*[torch.tensor([0, 1], device=device) for _ in range(n_dims)])

def compute_node_value(indices, *tensors):
    device = indices.device
    result = torch.ones(indices.size(0), device=device)
    for dim, tensor in enumerate(tensors):
        idx = indices[:, dim]
        if tensor.dim() == 2:
            result *= tensor[0, idx]
        elif tensor.dim() == 1:
            result *= tensor[idx]
        else:
            raise ValueError(f"Unsupported tensor shape: {tensor.shape}")
    return result   # shape: (1, N)

def safe_stack(values):

    clamped = [torch.clamp(v, 0.0, 1.0) for v in values]
    return torch.stack(clamped)

def state_to_graph(state, device):
    ap_value = {
    '0': torch.tensor([0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    #0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '1': torch.tensor([0,1,1,1,1,0,0,1,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    #0,1,1,1,1,0,0,1,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '2': torch.tensor([0,1,1,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    #0,1,1,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '3': torch.tensor([1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,0,0,0,-1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    #1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,1,1,1,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #1,0,0,-1,0,0,0,0,0,0,0,0,-1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '4': torch.tensor([0,1,1,1,1,0,0,0,1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,], device=device).float(),
    #0,1,1,1,1,0,0,0,1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '5': torch.tensor([0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,1,-1,0,0,1,-1,0,-2,0,-2,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    #0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,2,0,0,0,1,-1,0,0,1,-1,0,-2,0,-2,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '6': torch.tensor([0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1,0,0,-1,-1,0,0,0,0,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    #0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,1,0,0,0,1,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,-1,-1,0,0,-1,-1,0,0,0,0,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    '7': torch.tensor([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,-1,-1,0,0,1,1,0,-1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float()
    #1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #1,0,0,1,0,-1,-1,0,0,1,1,0,-1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    }

    label_dir = './FEATURE.csv'
    state_vector = torch.stack([ap_value[str(i)] for i in state]).to(device)
    ap_value = state_vector.view(49, 128)
    label_df = pd.read_csv(label_dir, header=None)
    label_value = torch.tensor(label_df.values, device=device).float()
    label_value = label_value.view(142, 32)
    
    ha_value = torch.tensor([0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float()
    fa_value = torch.tensor([0,1,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float()
    e_4_2_value = torch.tensor([0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,0,1,0,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1], device=device).float()
    and_value = torch.tensor([0.75, 0.25], device=device)
    pp_value = torch.tensor([1, 0], device=device)

    idxs_3 = generate_cartesian_indices(3, device)
    idxs_4 = generate_cartesian_indices(4, device)
    idxs_5 = generate_cartesian_indices(5, device)

    
    stage1_8_C_1 = torch.matmul(label_value[0,:], ha_value[32:64])
    stage1_8_C = safe_stack([1-stage1_8_C_1,stage1_8_C_1])

    stage1_9_S_1 = torch.matmul(label_value[1, :], ap_value[0, :32])
    stage1_9_C_1 = torch.matmul(label_value[1, :], ap_value[0, 32:64])
    stage1_9_S = safe_stack([1-stage1_9_S_1,stage1_9_S_1])
    stage1_9_C = safe_stack([1-stage1_9_C_1,stage1_9_C_1])

    stage1_10_1_S_1 = torch.matmul(label_value[2, :], ap_value[1, :32])
    stage1_10_1_C_1 = torch.matmul(label_value[2, :], ap_value[1, 32:64])
    stage1_10_1_S = safe_stack([1-stage1_10_1_S_1,stage1_10_1_S_1])
    stage1_10_1_C = safe_stack([1-stage1_10_1_C_1,stage1_10_1_C_1])

    stage1_11_1_S_1 = torch.matmul(label_value[3, :], ap_value[2, :32])
    stage1_11_1_C_1 = torch.matmul(label_value[3, :], ap_value[2, 32:64])
    stage1_11_1_S = safe_stack([1-stage1_11_1_S_1,stage1_11_1_S_1])
    stage1_11_1_C = safe_stack([1-stage1_11_1_C_1,stage1_11_1_C_1])

    stage1_12_1_S_1 = torch.matmul(label_value[4, :], ap_value[3, :32])
    stage1_12_1_C_1 = torch.matmul(label_value[4, :], ap_value[3, 32:64])
    stage1_12_1_S = safe_stack([1-stage1_12_1_S_1,stage1_12_1_S_1])
    stage1_12_1_C = safe_stack([1-stage1_12_1_C_1,stage1_12_1_C_1])

    stage1_13_1_S_1 = torch.matmul(label_value[5, :], ap_value[4, :32])
    stage1_13_1_C_1 = torch.matmul(label_value[5, :], ap_value[4, 32:64])
    stage1_13_1_S = safe_stack([1-stage1_13_1_S_1,stage1_13_1_S_1])
    stage1_13_1_C = safe_stack([1-stage1_13_1_C_1,stage1_13_1_C_1])

    stage1_14_1_S_1 = torch.matmul(label_value[6, :], ap_value[5, :32])
    stage1_14_1_C_1 = torch.matmul(label_value[6, :], ap_value[5, 32:64])
    stage1_14_1_S = safe_stack([1-stage1_14_1_S_1,stage1_14_1_S_1])
    stage1_14_1_C = safe_stack([1-stage1_14_1_C_1,stage1_14_1_C_1])

    stage1_15_1_S_1 = torch.matmul(label_value[7, :], ap_value[6, :32])
    stage1_15_1_C_1 = torch.matmul(label_value[7, :], ap_value[6, 32:64])
    stage1_15_1_S = safe_stack([1-stage1_15_1_S_1,stage1_15_1_S_1])
    stage1_15_1_C = safe_stack([1-stage1_15_1_C_1,stage1_15_1_C_1])

    stage1_16_1_S_1 = torch.matmul(label_value[8,:], e_4_2_value[:32])
    stage1_16_1_C_1 = torch.matmul(label_value[8,:], e_4_2_value[32:64])
    stage1_16_1_S = safe_stack([1-stage1_16_1_S_1,stage1_16_1_S_1])
    stage1_16_1_C = safe_stack([1-stage1_16_1_C_1,stage1_16_1_C_1])

    stage1_17_1_S_1 = torch.matmul(label_value[9,:], e_4_2_value[:32])
    stage1_17_1_C_1 = torch.matmul(label_value[9,:], e_4_2_value[32:64])
    stage1_17_1_S = safe_stack([1-stage1_17_1_S_1,stage1_17_1_S_1])
    stage1_17_1_C = safe_stack([1-stage1_17_1_C_1,stage1_17_1_C_1])

    stage1_10_2_S_1 = torch.matmul(label_value[16,:], ha_value[:32])
    stage1_10_2_C_1 = torch.matmul(label_value[16,:], ha_value[32:64])
    stage1_10_2_S = safe_stack([1-stage1_10_2_S_1, stage1_10_2_S_1])
    stage1_10_2_C = safe_stack([1-stage1_10_2_C_1, stage1_10_2_C_1])

    stage1_11_2_S_1 = torch.matmul(label_value[17, :], ap_value[7, :32])
    stage1_11_2_C_1 = torch.matmul(label_value[17, :], ap_value[7, 32:64])
    stage1_11_2_S = safe_stack([1-stage1_11_2_S_1,stage1_11_2_S_1])
    stage1_11_2_C = safe_stack([1-stage1_11_2_C_1,stage1_11_2_C_1])

    stage1_12_2_S_1 = torch.matmul(label_value[18, :], ap_value[8, :32])
    stage1_12_2_C_1 = torch.matmul(label_value[18, :], ap_value[8, 32:64])
    stage1_12_2_S = safe_stack([1-stage1_12_2_S_1,stage1_12_2_S_1])
    stage1_12_2_C = safe_stack([1-stage1_12_2_C_1,stage1_12_2_C_1])

    stage1_13_2_S_1 = torch.matmul(label_value[19, :], ap_value[9, :32])
    stage1_13_2_C_1 = torch.matmul(label_value[19, :], ap_value[9, 32:64])
    stage1_13_2_S = safe_stack([1-stage1_13_2_S_1,stage1_13_2_S_1])
    stage1_13_2_C = safe_stack([1-stage1_13_2_C_1,stage1_13_2_C_1])

    stage1_14_2_S_1 = torch.matmul(label_value[20, :], ap_value[10, :32])
    stage1_14_2_C_1 = torch.matmul(label_value[20, :], ap_value[10, 32:64])
    stage1_14_2_S = safe_stack([1-stage1_14_2_S_1,stage1_14_2_S_1])
    stage1_14_2_C = safe_stack([1-stage1_14_2_C_1,stage1_14_2_C_1])

    stage1_15_2_S_1 = torch.matmul(label_value[21, :], ap_value[11, :32])
    stage1_15_2_C_1 = torch.matmul(label_value[21, :], ap_value[11, 32:64])
    stage1_15_2_S = safe_stack([1-stage1_15_2_S_1,stage1_15_2_S_1])
    stage1_15_2_C = safe_stack([1-stage1_15_2_C_1,stage1_15_2_C_1])


    stage1_16_2_S_1 = torch.matmul(label_value[22,:], e_4_2_value[:32])
    stage1_16_2_C_1 = torch.matmul(label_value[22,:], e_4_2_value[32:64])
    stage1_16_2_S = safe_stack([1-stage1_16_2_S_1,stage1_16_2_S_1])
    stage1_16_2_C = safe_stack([1-stage1_16_2_C_1,stage1_16_2_C_1])

    stage1_17_2_S_1 = torch.matmul(label_value[23,:], e_4_2_value[:32])
    stage1_17_2_C_1 = torch.matmul(label_value[23,:], e_4_2_value[32:64])
    stage1_17_2_S = safe_stack([1-stage1_17_2_S_1,stage1_17_2_S_1])
    stage1_17_2_C = safe_stack([1-stage1_17_2_C_1,stage1_17_2_C_1])

    stage1_12_3_S_1 = torch.matmul(label_value[28,:], ha_value[:32])
    stage1_12_3_C_1 = torch.matmul(label_value[28,:], ha_value[32:64])
    stage1_12_3_S = safe_stack([1-stage1_12_3_S_1, stage1_12_3_S_1])
    stage1_12_3_C = safe_stack([1-stage1_12_3_C_1, stage1_12_3_C_1])

    stage1_13_3_S_1 = torch.matmul(label_value[29, :], ap_value[12, :32])
    stage1_13_3_C_1 = torch.matmul(label_value[29, :], ap_value[12, 32:64])
    stage1_13_3_S = safe_stack([1-stage1_13_3_S_1,stage1_13_3_S_1])
    stage1_13_3_C = safe_stack([1-stage1_13_3_C_1,stage1_13_3_C_1])

    stage1_14_3_S_1 = torch.matmul(label_value[30, :], ap_value[13, :32])
    stage1_14_3_C_1 = torch.matmul(label_value[30, :], ap_value[13, 32:64])
    stage1_14_3_S = safe_stack([1-stage1_14_3_S_1,stage1_14_3_S_1])
    stage1_14_3_C = safe_stack([1-stage1_14_3_C_1,stage1_14_3_C_1])

    stage1_15_3_S_1 = torch.matmul(label_value[31, :], ap_value[14, :32])
    stage1_15_3_C_1 = torch.matmul(label_value[31, :], ap_value[14, 32:64])
    stage1_15_3_S = safe_stack([1-stage1_15_3_S_1,stage1_15_3_S_1])
    stage1_15_3_C = safe_stack([1-stage1_15_3_C_1,stage1_15_3_C_1])

    stage1_16_3_S_1 = torch.matmul(label_value[32,:], e_4_2_value[:32])
    stage1_16_3_C_1 = torch.matmul(label_value[32,:], e_4_2_value[32:64])
    stage1_16_3_S = safe_stack([1-stage1_16_3_S_1,stage1_16_3_S_1])
    stage1_16_3_C = safe_stack([1-stage1_16_3_C_1,stage1_16_3_C_1])

    stage1_17_3_S_1 = torch.matmul(label_value[33,:], e_4_2_value[:32])
    stage1_17_3_C_1 = torch.matmul(label_value[33,:], e_4_2_value[32:64])
    stage1_17_3_S = safe_stack([1-stage1_17_3_S_1,stage1_17_3_S_1])
    stage1_17_3_C = safe_stack([1-stage1_17_3_C_1,stage1_17_3_C_1])

    stage1_14_4_S_1 = torch.matmul(label_value[36,:], ha_value[:32])
    stage1_14_4_C_1 = torch.matmul(label_value[36,:], ha_value[32:64])
    stage1_14_4_S = safe_stack([1-stage1_14_4_S_1, stage1_14_4_S_1])
    stage1_14_4_C = safe_stack([1-stage1_14_4_C_1, stage1_14_4_C_1])

    stage1_15_4_S_1 = torch.matmul(label_value[37, :], ap_value[15, :32])
    stage1_15_4_C_1 = torch.matmul(label_value[37, :], ap_value[15, 32:64])
    stage1_15_4_S = safe_stack([1-stage1_15_4_S_1,stage1_15_4_S_1])
    stage1_15_4_C = safe_stack([1-stage1_15_4_C_1,stage1_15_4_C_1])

    stage1_16_4_S_1 = torch.matmul(label_value[38,:], fa_value[:32])
    stage1_16_4_C_1 = torch.matmul(label_value[38,:], fa_value[32:64])
    stage1_16_4_S = safe_stack([1-stage1_16_4_S_1,stage1_16_4_S_1])
    stage1_16_4_C = safe_stack([1-stage1_16_4_C_1,stage1_16_4_C_1])

    stage1_17_4_S_1 = torch.matmul(label_value[39,:], ha_value[:32])
    stage1_17_4_C_1 = torch.matmul(label_value[39,:], ha_value[32:64])
    stage1_17_4_S = safe_stack([1-stage1_17_4_S_1,stage1_17_4_S_1])
    stage1_17_4_C = safe_stack([1-stage1_17_4_C_1,stage1_17_4_C_1])

    

    node46_value = compute_node_value(idxs_4, stage1_9_S, stage1_8_C, and_value, and_value)
    node47_value = compute_node_value(idxs_4, stage1_10_1_S, stage1_9_C, stage1_10_2_S, and_value)
    node48_value = compute_node_value(idxs_4, stage1_11_1_S, stage1_10_1_C,stage1_11_2_S, stage1_10_2_C)
    node49_value = compute_node_value(idxs_4, stage1_12_1_S, stage1_11_1_C,stage1_12_2_S, stage1_11_2_C)
    node50_value = compute_node_value(idxs_4, stage1_13_1_S, stage1_12_1_C,stage1_13_2_S, stage1_12_2_C)
    node51_value = compute_node_value(idxs_4, stage1_14_1_S, stage1_13_1_C,stage1_14_2_S, stage1_13_2_C)
    node52_value = compute_node_value(idxs_4, stage1_14_1_C, stage1_15_1_S,stage1_14_2_C, stage1_15_2_S)
    node53_value = compute_node_value(idxs_5, stage1_15_1_C, stage1_16_1_S,stage1_15_2_C, stage1_16_2_S, pp_value)
 
    stage2_16_1_S_1 = torch.matmul(node53_value, e_4_2_value[:32])
    stage2_16_1_C_1 = torch.matmul(node53_value, e_4_2_value[32:64])
    stage2_16_1_CO_1 = torch.matmul(node53_value, e_4_2_value[64:])
    stage2_16_1_S = safe_stack([1 - stage2_16_1_S_1, stage2_16_1_S_1])
    stage2_16_1_C = safe_stack([1 - stage2_16_1_C_1, stage2_16_1_C_1])
    stage2_16_1_CO = safe_stack([1 - stage2_16_1_CO_1, stage2_16_1_CO_1])
    
    node54_value = compute_node_value(idxs_5, stage1_16_1_C, stage1_17_1_S,stage1_16_2_C, stage1_17_2_S, stage2_16_1_CO)
    
    stage2_17_1_S_1 = torch.matmul(node54_value, e_4_2_value[:32])
    stage2_17_1_C_1 = torch.matmul(node54_value, e_4_2_value[32:64])
    stage2_17_1_S = safe_stack([1 - stage2_17_1_S_1, stage2_17_1_S_1])
    stage2_17_1_C = safe_stack([1 - stage2_17_1_C_1, stage2_17_1_C_1])

    stage2_18_1_S_1 = torch.matmul(label_value[54,:], e_4_2_value[:32])
    stage2_18_1_C_1 = torch.matmul(label_value[54,:], e_4_2_value[32:64])
    stage2_18_1_S = safe_stack([1 - stage2_18_1_S_1, stage2_18_1_S_1])
    stage2_18_1_C = safe_stack([1 - stage2_18_1_C_1, stage2_18_1_C_1])

    stage2_19_1_S_1 = torch.matmul(label_value[55,:], e_4_2_value[:32])
    stage2_19_1_S = safe_stack([1 - stage2_19_1_S_1, stage2_19_1_S_1])

    node72_value = compute_node_value(idxs_4, stage1_13_3_S, stage1_12_3_C, and_value, and_value)
    node73_value = compute_node_value(idxs_4, stage1_14_3_S, stage1_13_3_C, stage1_14_4_S, and_value)
    node74_value = compute_node_value(idxs_4, stage1_14_3_C, stage1_15_3_S, stage1_14_4_C, stage1_15_4_S)
    
    node75_value = compute_node_value(idxs_5, stage1_15_3_C, stage1_16_3_S,stage1_15_4_C, stage1_16_4_S, pp_value)
    
    stage2_16_2_S_1 = torch.matmul(node75_value, e_4_2_value[:32])
    stage2_16_2_C_1 = torch.matmul(node75_value, e_4_2_value[32:64])
    stage2_16_2_CO_1 = torch.matmul(node75_value, e_4_2_value[64:])
    stage2_16_2_S = safe_stack([1 - stage2_16_2_S_1, stage2_16_2_S_1])
    stage2_16_2_C = safe_stack([1 - stage2_16_2_C_1, stage2_16_2_C_1])
    stage2_16_2_CO = safe_stack([1 - stage2_16_2_CO_1, stage2_16_2_CO_1])

    node76_value = compute_node_value(idxs_5, stage1_16_3_C, stage1_17_3_S,stage1_16_4_C, stage1_17_4_S, stage2_16_2_CO)

    stage2_17_2_S_1 = torch.matmul(node76_value, e_4_2_value[:32])
    stage2_17_2_C_1 = torch.matmul(node76_value, e_4_2_value[32:64])
    stage2_17_2_S = safe_stack([1 - stage2_17_2_S_1, stage2_17_2_S_1])
    stage2_17_2_C = safe_stack([1 - stage2_17_2_C_1, stage2_17_2_C_1])

    stage2_18_2_S_1 = torch.matmul(label_value[76, :], e_4_2_value[:32])
    stage2_18_2_C_1 = torch.matmul(label_value[76, :], e_4_2_value[32:64])
    stage2_18_2_S = safe_stack([1 - stage2_18_2_S_1, stage2_18_2_S_1]) 
    stage2_18_2_C = safe_stack([1 - stage2_18_2_C_1, stage2_18_2_C_1]) 

    stage2_19_2_S_1 = torch.matmul(label_value[77,:], e_4_2_value[:32])
    stage2_19_2_S = safe_stack([1 - stage2_19_2_S_1, stage2_19_2_S_1]) 

    stage2_4_1_C_1 = torch.matmul(label_value[40,:], ha_value[32:64])
    stage2_4_1_C = safe_stack([1-stage2_4_1_C_1, stage2_4_1_C_1])

    stage2_5_1_S_1 = torch.matmul(label_value[41, :], ap_value[16, :32])
    stage2_5_1_C_1 = torch.matmul(label_value[41, :], ap_value[16, 32:64])
    stage2_5_1_S = safe_stack([1-stage2_5_1_S_1,stage2_5_1_S_1])
    stage2_5_1_C = safe_stack([1-stage2_5_1_C_1,stage2_5_1_C_1])

    stage2_6_1_S_1 = torch.matmul(label_value[42, :], ap_value[17, :32])
    stage2_6_1_C_1 = torch.matmul(label_value[42, :], ap_value[17, 32:64])
    stage2_6_1_S = safe_stack([1-stage2_6_1_S_1,stage2_6_1_S_1]) 
    stage2_6_1_C = safe_stack([1-stage2_6_1_C_1,stage2_6_1_C_1]) 

    stage2_7_1_S_1 = torch.matmul(label_value[43, :], ap_value[18, :32])
    stage2_7_1_C_1 = torch.matmul(label_value[43, :], ap_value[18, 32:64])
    stage2_7_1_S = safe_stack([1-stage2_7_1_S_1,stage2_7_1_S_1]) 
    stage2_7_1_C = safe_stack([1-stage2_7_1_C_1,stage2_7_1_C_1]) 

    stage2_8_1_S_1 = torch.matmul(label_value[44, :], ap_value[19, :32])
    stage2_8_1_C_1 = torch.matmul(label_value[44, :], ap_value[19, 32:64])
    stage2_8_1_S = safe_stack([1-stage2_8_1_S_1,stage2_8_1_S_1]) 
    stage2_8_1_C = safe_stack([1-stage2_8_1_C_1,stage2_8_1_C_1]) 

    stage2_9_1_S_1 = torch.matmul(node46_value, ap_value[20, :16])
    stage2_9_1_C_1 = torch.matmul(node46_value, ap_value[20, 32:48])
    stage2_9_1_S = safe_stack([1-stage2_9_1_S_1,stage2_9_1_S_1])
    stage2_9_1_C = safe_stack([1-stage2_9_1_C_1,stage2_9_1_C_1])

    stage2_10_1_S_1 = torch.matmul(node47_value, ap_value[21, :16])
    stage2_10_1_C_1 = torch.matmul(node47_value, ap_value[21, 32:48])
    stage2_10_1_S = safe_stack([1-stage2_10_1_S_1,stage2_10_1_S_1])
    stage2_10_1_C = safe_stack([1-stage2_10_1_C_1,stage2_10_1_C_1])

    stage2_11_1_S_1 = torch.matmul(node48_value, ap_value[22, :16])
    stage2_11_1_C_1 = torch.matmul(node48_value, ap_value[22, 32:48])
    stage2_11_1_S = safe_stack([1-stage2_11_1_S_1,stage2_11_1_S_1])
    stage2_11_1_C = safe_stack([1-stage2_11_1_C_1,stage2_11_1_C_1])

    stage2_12_1_S_1 = torch.matmul(node49_value, ap_value[23, :16])
    stage2_12_1_C_1 = torch.matmul(node49_value, ap_value[23, 32:48])
    stage2_12_1_S = safe_stack([1-stage2_12_1_S_1,stage2_12_1_S_1])
    stage2_12_1_C = safe_stack([1-stage2_12_1_C_1,stage2_12_1_C_1])

    stage2_13_1_S_1 = torch.matmul(node50_value, ap_value[24, :16])
    stage2_13_1_C_1 = torch.matmul(node50_value, ap_value[24, 32:48])
    stage2_13_1_S = safe_stack([1-stage2_13_1_S_1,stage2_13_1_S_1])
    stage2_13_1_C = safe_stack([1-stage2_13_1_C_1,stage2_13_1_C_1])

    stage2_14_1_S_1 = torch.matmul(node51_value, ap_value[25, :16])
    stage2_14_1_C_1 = torch.matmul(node51_value, ap_value[25, 32:48])
    stage2_14_1_S = safe_stack([1-stage2_14_1_S_1,stage2_14_1_S_1])
    stage2_14_1_C = safe_stack([1-stage2_14_1_C_1,stage2_14_1_C_1])

    stage2_15_1_S_1 = torch.matmul(node52_value, ap_value[26, :16])
    stage2_15_1_C_1 = torch.matmul(node52_value, ap_value[26, 32:48])
    stage2_15_1_S = safe_stack([1-stage2_15_1_S_1,stage2_15_1_S_1])
    stage2_15_1_C = safe_stack([1-stage2_15_1_C_1,stage2_15_1_C_1])

    stage2_6_2_S_1 = torch.matmul(label_value[64,:], ha_value[:32])
    stage2_6_2_C_1 = torch.matmul(label_value[64,:], ha_value[32:64])
    stage2_6_2_S = safe_stack([1-stage2_6_2_S_1, stage2_6_2_S_1]) 
    stage2_6_2_C = safe_stack([1-stage2_6_2_C_1, stage2_6_2_C_1]) 

    stage2_7_2_S_1 = torch.matmul(label_value[65,:], ap_value[27, :32])
    stage2_7_2_C_1 = torch.matmul(label_value[65,:], ap_value[27, 32:64])
    stage2_7_2_S = safe_stack([1-stage2_7_2_S_1,stage2_7_2_S_1]) 
    stage2_7_2_C = safe_stack([1-stage2_7_2_C_1,stage2_7_2_C_1]) 

    stage2_8_2_S_1 = torch.matmul(label_value[66,:], ap_value[28, :32])
    stage2_8_2_C_1 = torch.matmul(label_value[66,:], ap_value[28, 32:64])
    stage2_8_2_S = safe_stack([1-stage2_8_2_S_1,stage2_8_2_S_1]) 
    stage2_8_2_C = safe_stack([1-stage2_8_2_C_1,stage2_8_2_C_1]) 

    stage2_9_2_S_1 = torch.matmul(label_value[67,:], ap_value[29, :32])
    stage2_9_2_C_1 = torch.matmul(label_value[67,:], ap_value[29, 32:64])
    stage2_9_2_S = safe_stack([1-stage2_9_2_S_1,stage2_9_2_S_1]) 
    stage2_9_2_C = safe_stack([1-stage2_9_2_C_1,stage2_9_2_C_1]) 

    stage2_10_2_S_1 = torch.matmul(label_value[68,:], ap_value[30, :32])
    stage2_10_2_C_1 = torch.matmul(label_value[68,:], ap_value[30, 32:64])
    stage2_10_2_S = safe_stack([1-stage2_10_2_S_1,stage2_10_2_S_1]) 
    stage2_10_2_C = safe_stack([1-stage2_10_2_C_1,stage2_10_2_C_1]) 

    stage2_11_2_S_1 = torch.matmul(label_value[69,:], ap_value[31, :32])
    stage2_11_2_C_1 = torch.matmul(label_value[69,:], ap_value[31, 32:64])
    stage2_11_2_S = safe_stack([1-stage2_11_2_S_1,stage2_11_2_S_1]) 
    stage2_11_2_C = safe_stack([1-stage2_11_2_C_1,stage2_11_2_C_1]) 

    stage2_12_2_S_1 = torch.matmul(label_value[70,:], ap_value[32, :32])
    stage2_12_2_C_1 = torch.matmul(label_value[70,:], ap_value[32, 32:64])
    stage2_12_2_S = safe_stack([1-stage2_12_2_S_1,stage2_12_2_S_1]) 
    stage2_12_2_C = safe_stack([1-stage2_12_2_C_1,stage2_12_2_C_1]) 

    stage2_13_2_S_1 = torch.matmul(node72_value, ap_value[33, :16])
    stage2_13_2_C_1 = torch.matmul(node72_value, ap_value[33, 32:48])
    stage2_13_2_S = safe_stack([1-stage2_13_2_S_1,stage2_13_2_S_1])
    stage2_13_2_C = safe_stack([1-stage2_13_2_C_1,stage2_13_2_C_1])

    stage2_14_2_S_1 = torch.matmul(node73_value, ap_value[34, :16])
    stage2_14_2_C_1 = torch.matmul(node73_value, ap_value[34, 32:48])
    stage2_14_2_S = safe_stack([1-stage2_14_2_S_1,stage2_14_2_S_1])
    stage2_14_2_C = safe_stack([1-stage2_14_2_C_1,stage2_14_2_C_1])
    
    stage2_15_2_S_1 = torch.matmul(node74_value, ap_value[35, :16])
    stage2_15_2_C_1 = torch.matmul(node74_value, ap_value[35, 32:48])
    stage2_15_2_S = safe_stack([1-stage2_15_2_S_1,stage2_15_2_S_1])
    stage2_15_2_C = safe_stack([1-stage2_15_2_C_1,stage2_15_2_C_1])
    
    node88_value = compute_node_value(idxs_4, stage2_5_1_S, and_value, and_value, stage2_4_1_C)
    node89_value = compute_node_value(idxs_4, stage2_6_1_S, and_value, stage2_6_2_S, stage2_5_1_C)
    node90_value = compute_node_value(idxs_4, stage2_7_1_S, stage2_6_1_C, stage2_7_2_S, stage2_6_2_C)
    node91_value = compute_node_value(idxs_4, stage2_8_1_S, stage2_7_1_C, stage2_8_2_S, stage2_7_2_C)
    node92_value = compute_node_value(idxs_4, stage2_9_1_S, stage2_8_1_C, stage2_9_2_S, stage2_8_2_C)
    node93_value = compute_node_value(idxs_4, stage2_10_1_S, stage2_9_1_C, stage2_10_2_S, stage2_9_2_C)
    node94_value = compute_node_value(idxs_4, stage2_11_1_S, stage2_10_1_C, stage2_11_2_S, stage2_10_2_C)
    node95_value = compute_node_value(idxs_4, stage2_12_1_S, stage2_11_1_C, stage2_12_2_S, stage2_11_2_C)
    node96_value = compute_node_value(idxs_4, stage2_13_1_S, stage2_12_1_C, stage2_13_2_S, stage2_12_2_C)
    node97_value = compute_node_value(idxs_4, stage2_14_1_S, stage2_13_1_C, stage2_14_2_S, stage2_13_2_C)
    node98_value = compute_node_value(idxs_4, stage2_15_1_S, stage2_14_1_C, stage2_15_2_S, stage2_14_2_C)
    
    node99_value = compute_node_value(idxs_5, stage2_15_1_C, stage2_16_1_S,stage2_15_2_C, stage2_16_2_S, pp_value)
   
    stage3_16_S_1 = torch.matmul(node99_value, e_4_2_value[:32])
    stage3_16_C_1 = torch.matmul(node99_value, e_4_2_value[32:64])
    stage3_16_CO_1 = torch.matmul(node99_value, e_4_2_value[64:])
    stage3_16_S = safe_stack([1 - stage3_16_S_1, stage3_16_S_1])
    stage3_16_C = safe_stack([1 - stage3_16_C_1, stage3_16_C_1])
    stage3_16_CO = safe_stack([1 - stage3_16_CO_1, stage3_16_CO_1])

    node100_value = compute_node_value(idxs_5, stage2_16_1_C, stage2_17_1_S,stage2_16_2_C, stage2_17_2_S, stage3_16_CO)

    stage3_17_S_1 = torch.matmul(node100_value, e_4_2_value[:32])
    stage3_17_C_1 = torch.matmul(node100_value, e_4_2_value[32:64])
    stage3_17_CO_1 = torch.matmul(node100_value, e_4_2_value[64:])
    stage3_17_S = safe_stack([1 - stage3_17_S_1, stage3_17_S_1])
    stage3_17_C = safe_stack([1 - stage3_17_C_1, stage3_17_C_1])
    stage3_17_CO = safe_stack([1 - stage3_17_CO_1, stage3_17_CO_1])


    node101_value = compute_node_value(idxs_5, stage2_17_1_C, stage2_18_1_S,stage2_17_2_C, stage2_18_2_S, stage3_17_CO)

    stage3_18_S_1 = torch.matmul(node101_value, e_4_2_value[:32])
    stage3_18_C_1 = torch.matmul(node101_value, e_4_2_value[32:64])
    stage3_18_CO_1 = torch.matmul(node101_value, e_4_2_value[64:])
    stage3_18_S = safe_stack([1 - stage3_18_S_1, stage3_18_S_1])
    stage3_18_C = safe_stack([1 - stage3_18_C_1, stage3_18_C_1])
    stage3_18_CO = safe_stack([1 - stage3_18_CO_1, stage3_18_CO_1])

    node102_value = compute_node_value(idxs_5, stage2_18_1_C, stage2_19_1_S,stage2_18_2_C, stage2_19_2_S, stage3_18_CO)

    stage3_2_C_1 = torch.matmul(label_value[84,:], ha_value[32:64])
    stage3_2_C = safe_stack([1-stage3_2_C_1,stage3_2_C_1])

    stage3_3_S_1 = torch.matmul(label_value[85,:], ap_value[36, :32])
    stage3_3_C_1 = torch.matmul(label_value[85,:], ap_value[36, 32:64])
    stage3_3_S = safe_stack([1-stage3_3_S_1,stage3_3_S_1])
    stage3_3_C = safe_stack([1-stage3_3_C_1,stage3_3_C_1])

    stage3_4_S_1 = torch.matmul(label_value[86,:], ap_value[37, :32])
    stage3_4_C_1 = torch.matmul(label_value[86,:], ap_value[37, 32:64])
    stage3_4_S = safe_stack([1-stage3_4_S_1,stage3_4_S_1])
    stage3_4_C = safe_stack([1-stage3_4_C_1,stage3_4_C_1])

    stage3_5_S_1 = torch.matmul(node88_value, ap_value[38, :16])
    stage3_5_C_1 = torch.matmul(node88_value, ap_value[38, 32:48])
    stage3_5_S = safe_stack([1-stage3_5_S_1,stage3_5_S_1])
    stage3_5_C = safe_stack([1-stage3_5_C_1,stage3_5_C_1])

    stage3_6_S_1 = torch.matmul(node89_value, ap_value[39, :16])
    stage3_6_C_1 = torch.matmul(node89_value, ap_value[39, 32:48])
    stage3_6_S = safe_stack([1-stage3_6_S_1,stage3_6_S_1])
    stage3_6_C = safe_stack([1-stage3_6_C_1,stage3_6_C_1])

    stage3_7_S_1 = torch.matmul(node90_value, ap_value[40, :16])
    stage3_7_C_1 = torch.matmul(node90_value, ap_value[40, 32:48])
    stage3_7_S = safe_stack([1-stage3_7_S_1,stage3_7_S_1])
    stage3_7_C = safe_stack([1-stage3_7_C_1,stage3_7_C_1])

    stage3_8_S_1 = torch.matmul(node91_value, ap_value[41, :16])
    stage3_8_C_1 = torch.matmul(node91_value, ap_value[41, 32:48])
    stage3_8_S = safe_stack([1-stage3_8_S_1,stage3_8_S_1])
    stage3_8_C = safe_stack([1-stage3_8_C_1,stage3_8_C_1])

    stage3_9_S_1 = torch.matmul(node92_value, ap_value[42, :16])
    stage3_9_C_1 = torch.matmul(node92_value, ap_value[42, 32:48])
    stage3_9_S = safe_stack([1-stage3_9_S_1,stage3_9_S_1])
    stage3_9_C = safe_stack([1-stage3_9_C_1,stage3_9_C_1])

    stage3_10_S_1 = torch.matmul(node93_value, ap_value[43, :16])
    stage3_10_C_1 = torch.matmul(node93_value, ap_value[43, 32:48])
    stage3_10_S = safe_stack([1-stage3_10_S_1,stage3_10_S_1])
    stage3_10_C = safe_stack([1-stage3_10_C_1,stage3_10_C_1])

    stage3_11_S_1 = torch.matmul(node94_value, ap_value[44, :16])
    stage3_11_C_1 = torch.matmul(node94_value, ap_value[44, 32:48])
    stage3_11_S = safe_stack([1-stage3_11_S_1,stage3_11_S_1])
    stage3_11_C = safe_stack([1-stage3_11_C_1,stage3_11_C_1])

    stage3_12_S_1 = torch.matmul(node95_value, ap_value[45, :16])
    stage3_12_C_1 = torch.matmul(node95_value, ap_value[45, 32:48])
    stage3_12_S = safe_stack([1-stage3_12_S_1,stage3_12_S_1])
    stage3_12_C = safe_stack([1-stage3_12_C_1,stage3_12_C_1])

    stage3_13_S_1 = torch.matmul(node96_value, ap_value[46, :16])
    stage3_13_C_1 = torch.matmul(node96_value, ap_value[46, 32:48])
    stage3_13_S = safe_stack([1-stage3_13_S_1,stage3_13_S_1])
    stage3_13_C = safe_stack([1-stage3_13_C_1,stage3_13_C_1])

    stage3_14_S_1 = torch.matmul(node97_value, ap_value[47, :16])
    stage3_14_C_1 = torch.matmul(node97_value, ap_value[47, 32:48])
    stage3_14_S = safe_stack([1-stage3_14_S_1,stage3_14_S_1])
    stage3_14_C = safe_stack([1-stage3_14_C_1,stage3_14_C_1])

    stage3_15_S_1 = torch.matmul(node98_value, ap_value[48, :16])
    stage3_15_C_1 = torch.matmul(node98_value, ap_value[48, 32:48])
    stage3_15_S = safe_stack([1-stage3_15_S_1,stage3_15_S_1])
    stage3_15_C = safe_stack([1-stage3_15_C_1,stage3_15_C_1])

    stage3_19_S_1 = torch.matmul(label_value[101,:], e_4_2_value[:32])
    stage3_19_C_1 = torch.matmul(label_value[101,:], e_4_2_value[32:64])
    stage3_19_CO_1 = torch.matmul(label_value[101,:], e_4_2_value[64:])
    stage3_19_S = safe_stack([1 - stage3_19_S_1, stage3_19_S_1])
    stage3_19_C = safe_stack([1 - stage3_19_C_1, stage3_19_C_1])
    stage3_19_CO = safe_stack([1 - stage3_19_CO_1, stage3_19_CO_1])

    stage3_20_S_1 = torch.matmul(label_value[102,:], e_4_2_value[:32])
    stage3_20_C_1 = torch.matmul(label_value[102,:], e_4_2_value[32:64])
    stage3_20_CO_1 = torch.matmul(label_value[102,:], e_4_2_value[64:])
    stage3_20_S = safe_stack([1 - stage3_20_S_1, stage3_20_S_1])
    stage3_20_C = safe_stack([1 - stage3_20_C_1, stage3_20_C_1])
    stage3_20_CO = safe_stack([1 - stage3_20_CO_1, stage3_20_CO_1])

    stage3_21_S_1 = torch.matmul(label_value[103, :], e_4_2_value[:32])
    stage3_21_C_1 = torch.matmul(label_value[103, :], e_4_2_value[32:64])
    stage3_21_CO_1 = torch.matmul(label_value[103, :], e_4_2_value[64:])
    stage3_21_S = safe_stack([1 - stage3_21_S_1, stage3_21_S_1])
    stage3_21_C = safe_stack([1 - stage3_21_C_1, stage3_21_C_1])
    stage3_21_CO = safe_stack([1 - stage3_21_CO_1, stage3_21_CO_1])

    stage3_22_S_1 = torch.matmul(label_value[104, :], e_4_2_value[:32])
    stage3_22_C_1 = torch.matmul(label_value[104, :], e_4_2_value[32:64])
    stage3_22_CO_1 = torch.matmul(label_value[104, :], e_4_2_value[64:])
    stage3_22_S = safe_stack([1 - stage3_22_S_1, stage3_22_S_1])
    stage3_22_C = safe_stack([1 - stage3_22_C_1, stage3_22_C_1])
    stage3_22_CO = safe_stack([1 - stage3_22_CO_1, stage3_22_CO_1])

    stage3_23_S_1 = torch.matmul(label_value[105, :], e_4_2_value[:32])
    stage3_23_C_1 = torch.matmul(label_value[105, :], e_4_2_value[32:64])
    stage3_23_CO_1 = torch.matmul(label_value[105, :], e_4_2_value[64:])
    stage3_23_S = safe_stack([1 - stage3_23_S_1, stage3_23_S_1])
    stage3_23_C = safe_stack([1 - stage3_23_C_1, stage3_23_C_1])
    stage3_23_CO = safe_stack([1 - stage3_23_CO_1, stage3_23_CO_1])

    stage3_24_S_1 = torch.matmul(label_value[106, :], e_4_2_value[:32])
    stage3_24_C_1 = torch.matmul(label_value[106, :], e_4_2_value[32:64])
    stage3_24_CO_1 = torch.matmul(label_value[106, :], e_4_2_value[64:])
    stage3_24_S = safe_stack([1 - stage3_24_S_1, stage3_24_S_1])
    stage3_24_C = safe_stack([1 - stage3_24_C_1, stage3_24_C_1])
    stage3_24_CO = safe_stack([1 - stage3_24_CO_1, stage3_24_CO_1])

    stage3_25_S_1 = torch.matmul(label_value[107, :], e_4_2_value[:32])
    stage3_25_C_1 = torch.matmul(label_value[107, :], e_4_2_value[32:64])
    stage3_25_CO_1 = torch.matmul(label_value[107, :], e_4_2_value[64:])
    stage3_25_S = safe_stack([1 - stage3_25_S_1, stage3_25_S_1])
    stage3_25_C = safe_stack([1 - stage3_25_C_1, stage3_25_C_1])
    stage3_25_CO = safe_stack([1 - stage3_25_CO_1, stage3_25_CO_1])

    stage3_26_S_1 = torch.matmul(label_value[108, :], e_4_2_value[:32])
    stage3_26_C_1 = torch.matmul(label_value[108, :], e_4_2_value[32:64])
    stage3_26_CO_1 = torch.matmul(label_value[108, :], e_4_2_value[64:])
    stage3_26_S = safe_stack([1 - stage3_26_S_1, stage3_26_S_1])
    stage3_26_C = safe_stack([1 - stage3_26_C_1, stage3_26_C_1])
    stage3_26_CO = safe_stack([1 - stage3_26_CO_1, stage3_26_CO_1])

    stage3_27_S_1 = torch.matmul(label_value[109, :], e_4_2_value[:32])
    stage3_27_C_1 = torch.matmul(label_value[109, :], e_4_2_value[32:64])
    stage3_27_CO_1 = torch.matmul(label_value[109, :], e_4_2_value[64:])
    stage3_27_S = safe_stack([1 - stage3_27_S_1, stage3_27_S_1])
    stage3_27_C = safe_stack([1 - stage3_27_C_1, stage3_27_C_1])
    stage3_27_CO = safe_stack([1 - stage3_27_CO_1, stage3_27_CO_1])

    stage3_28_S_1 = torch.matmul(label_value[110, :], e_4_2_value[:32])
    stage3_28_C_1 = torch.matmul(label_value[110, :], e_4_2_value[32:64])
    stage3_28_CO_1 = torch.matmul(label_value[110, :], e_4_2_value[64:])
    stage3_28_S = safe_stack([1 - stage3_28_S_1, stage3_28_S_1])
    stage3_28_C = safe_stack([1 - stage3_28_C_1, stage3_28_C_1])
    stage3_28_CO = safe_stack([1 - stage3_28_CO_1, stage3_28_CO_1])

    stage3_29_S_1 = torch.matmul(label_value[111, :], fa_value[:32])
    stage3_29_C_1 = torch.matmul(label_value[111, :], fa_value[32:64])
    stage3_29_S = safe_stack([1 - stage3_29_S_1, stage3_29_S_1])
    stage3_29_C = safe_stack([1 - stage3_29_C_1, stage3_29_C_1])

    stage4_2_C_1 = torch.matmul(label_value[114,:], fa_value[32:64])
    stage4_2_C = safe_stack([1-stage4_2_C_1,stage4_2_C_1])

    node115_value = compute_node_value(idxs_3, stage3_3_S, stage3_2_C,stage4_2_C)
    node115_C_1 = torch.matmul(node115_value, fa_value[32:40])
    node115_C = safe_stack([1 - node115_C_1, node115_C_1])

    node116_value = compute_node_value(idxs_3, stage3_4_S, stage3_3_C, node115_C)
    node116_C_1 = torch.matmul(node116_value, fa_value[32:40])
    node116_C = safe_stack([1 - node116_C_1, node116_C_1])

    node117_value = compute_node_value(idxs_3, stage3_5_S, stage3_4_C, node116_C)
    node117_C_1 = torch.matmul(node117_value, fa_value[32:40])
    node117_C = safe_stack([1 - node117_C_1, node117_C_1])

    node118_value = compute_node_value(idxs_3, stage3_6_S, stage3_5_C, node117_C)
    node118_C_1 = torch.matmul(node118_value, fa_value[32:40])
    node118_C = safe_stack([1 - node118_C_1, node118_C_1])

    node119_value = compute_node_value(idxs_3, stage3_7_S, stage3_6_C, node118_C)
    node119_C_1 = torch.matmul(node119_value, fa_value[32:40])
    node119_C = safe_stack([1 - node119_C_1, node119_C_1])

    node120_value = compute_node_value(idxs_3, stage3_8_S, stage3_7_C, node119_C)
    node120_C_1 = torch.matmul(node120_value, fa_value[32:40])
    node120_C = safe_stack([1 - node120_C_1, node120_C_1])

    node121_value = compute_node_value(idxs_3, stage3_9_S, stage3_8_C, node120_C)
    node121_C_1 = torch.matmul(node121_value, fa_value[32:40])
    node121_C = safe_stack([1 - node121_C_1, node121_C_1])

    node122_value = compute_node_value(idxs_3, stage3_10_S, stage3_9_C, node121_C)
    node122_C_1 = torch.matmul(node122_value, fa_value[32:40])
    node122_C = safe_stack([1 - node122_C_1, node122_C_1])

    node123_value = compute_node_value(idxs_3, stage3_11_S, stage3_10_C, node122_C)
    node123_C_1 = torch.matmul(node123_value, fa_value[32:40])
    node123_C = safe_stack([1 - node123_C_1, node123_C_1])

    node124_value = compute_node_value(idxs_3, stage3_12_S, stage3_11_C, node123_C)
    node124_C_1 = torch.matmul(node124_value, fa_value[32:40])
    node124_C = safe_stack([1 - node124_C_1, node124_C_1])

    node125_value = compute_node_value(idxs_3, stage3_13_S, stage3_12_C, node124_C)
    node125_C_1 = torch.matmul(node125_value, fa_value[32:40])
    node125_C = safe_stack([1 - node125_C_1, node125_C_1])

    node126_value = compute_node_value(idxs_3, stage3_14_S, stage3_13_C, node125_C)
    node126_C_1 = torch.matmul(node126_value, fa_value[32:40])
    node126_C = safe_stack([1 - node126_C_1, node126_C_1])

    node127_value = compute_node_value(idxs_3, stage3_15_S, stage3_14_C, node126_C)
   
    node127_C_1 = torch.matmul(node127_value, fa_value[32:40])
    node127_C = safe_stack([1 - node127_C_1, node127_C_1])

    node128_value = compute_node_value(idxs_3, stage3_16_S, stage3_15_C, node127_C)
    node128_C_1 = torch.matmul(node128_value, fa_value[32:40])
    node128_C = safe_stack([1 - node128_C_1, node128_C_1])

    node129_value = compute_node_value(idxs_3, stage3_17_S, stage3_16_C, node128_C)
    node129_C_1 = torch.matmul(node129_value, fa_value[32:40])
    node129_C = safe_stack([1 - node129_C_1, node129_C_1])

    node130_value = compute_node_value(idxs_3, stage3_18_S, stage3_17_C, node129_C)
    node130_C_1 = torch.matmul(node130_value, fa_value[32:40])
    node130_C = safe_stack([1 - node130_C_1, node130_C_1])

    node131_value = compute_node_value(idxs_3, stage3_19_S, stage3_18_C, node130_C)
    node131_C_1 = torch.matmul(node131_value, fa_value[32:40])
    node131_C = safe_stack([1 - node131_C_1, node131_C_1])

    node132_value = compute_node_value(idxs_3, stage3_20_S, stage3_19_C, node131_C)
    node132_C_1 = torch.matmul(node132_value, fa_value[32:40])
    node132_C = safe_stack([1 - node132_C_1, node132_C_1])

    node133_value = compute_node_value(idxs_3, stage3_21_S, stage3_20_C, node132_C)
    node133_C_1 = torch.matmul(node133_value, fa_value[32:40])
    node133_C = safe_stack([1 - node133_C_1, node133_C_1])

    node134_value = compute_node_value(idxs_3, stage3_22_S, stage3_21_C, node133_C)
    node134_C_1 = torch.matmul(node134_value, fa_value[32:40])
    node134_C = safe_stack([1 - node134_C_1, node134_C_1])

    node135_value = compute_node_value(idxs_3, stage3_23_S, stage3_22_C, node134_C)
    node135_C_1 = torch.matmul(node135_value, fa_value[32:40])
    node135_C = safe_stack([1 - node135_C_1, node135_C_1])

    node136_value = compute_node_value(idxs_3, stage3_24_S, stage3_23_C, node135_C)
    node136_C_1 = torch.matmul(node136_value, fa_value[32:40])
    node136_C = safe_stack([1 - node136_C_1, node136_C_1])

    node137_value = compute_node_value(idxs_3, stage3_25_S, stage3_24_C, node136_C)
    node137_C_1 = torch.matmul(node137_value, fa_value[32:40])
    node137_C = safe_stack([1 - node137_C_1, node137_C_1])

    node138_value = compute_node_value(idxs_3, stage3_26_S, stage3_25_C, node137_C)
    node138_C_1 = torch.matmul(node138_value, fa_value[32:40])
    node138_C = safe_stack([1 - node138_C_1, node138_C_1])

    node139_value = compute_node_value(idxs_3, stage3_27_S, stage3_26_C, node138_C)
    node139_C_1 = torch.matmul(node139_value, fa_value[32:40])
    node139_C = safe_stack([1 - node139_C_1, node139_C_1])

    node140_value = compute_node_value(idxs_3, stage3_28_S, stage3_27_C, node139_C)
    node140_C_1 = torch.matmul(node140_value, fa_value[32:40])
    node140_C = safe_stack([1 - node140_C_1, node140_C_1])

    node141_value = compute_node_value(idxs_3, stage3_29_S, stage3_28_C, node140_C)
    node141_C_1 = torch.matmul(node141_value, fa_value[32:40])
    node141_C = safe_stack([1 - node141_C_1, node141_C_1])

    node142_value = compute_node_value(idxs_3, and_value, stage3_29_C, node141_C)

    node2_value = label_value[1, :] * ap_value[0, 96:]
    node3_value = label_value[2, :] * ap_value[1, 96:]
    node4_value = label_value[3, :] * ap_value[2, 96:]
    node5_value = label_value[4, :] * ap_value[3, 96:]
    node6_value = label_value[5, :] * ap_value[4, 96:]
    node7_value = label_value[6, :] * ap_value[5, 96:]
    node8_value = label_value[7, :] * ap_value[6, 96:]

    node18_value = label_value[17, :] * ap_value[7, 96:]
    node19_value = label_value[18, :] * ap_value[8, 96:]
    node20_value = label_value[19, :] * ap_value[9, 96:]
    node21_value = label_value[20, :] * ap_value[10, 96:]
    node22_value = label_value[21, :] * ap_value[11, 96:]

    node30_value = label_value[29, :] * ap_value[12, 96:]
    node31_value = label_value[30, :] * ap_value[13, 96:]
    node32_value = label_value[31, :] * ap_value[14, 96:]

    node38_value = label_value[37, :] * ap_value[15, 96:]
    
    node42_value = label_value[41, :] * ap_value[16, 96:]
    node43_value = label_value[42, :] * ap_value[17, 96:]
    node44_value = label_value[43, :] * ap_value[18, 96:]
    node45_value = label_value[44, :] * ap_value[19, 96:]
    node46_value = node46_value * ap_value[20, 96:112]
    node47_value = node47_value * ap_value[21, 96:112]
    node48_value = node48_value * ap_value[22, 96:112]
    node49_value = node49_value * ap_value[23, 96:112]
    node50_value = node50_value * ap_value[24, 96:112]
    node51_value = node51_value * ap_value[25, 96:112]
    node52_value = node52_value * ap_value[26, 96:112]

    node46_value = torch.nn.functional.pad(node46_value, (0, 16), mode='constant', value=0)
    node47_value = torch.nn.functional.pad(node47_value, (0, 16), mode='constant', value=0)
    node48_value = torch.nn.functional.pad(node48_value, (0, 16), mode='constant', value=0)
    node49_value = torch.nn.functional.pad(node49_value, (0, 16), mode='constant', value=0)
    node50_value = torch.nn.functional.pad(node50_value, (0, 16), mode='constant', value=0)
    node51_value = torch.nn.functional.pad(node51_value, (0, 16), mode='constant', value=0)
    node52_value = torch.nn.functional.pad(node52_value, (0, 16), mode='constant', value=0)

    node66_value = label_value[65, :] * ap_value[27, 96:]
    node67_value = label_value[66, :] * ap_value[28, 96:]
    node68_value = label_value[67, :] * ap_value[29, 96:]
    node69_value = label_value[68, :] * ap_value[30, 96:]
    node70_value = label_value[69, :] * ap_value[31, 96:]
    node71_value = label_value[70, :] * ap_value[32, 96:]
    node72_value = node72_value * ap_value[33, 96:112]
    node73_value = node73_value * ap_value[34, 96:112]
    node74_value = node74_value * ap_value[35, 96:112]

    node72_value = torch.nn.functional.pad(node72_value, (0, 16), mode='constant', value=0)
    node73_value = torch.nn.functional.pad(node73_value, (0, 16), mode='constant', value=0)
    node74_value = torch.nn.functional.pad(node74_value, (0, 16), mode='constant', value=0)

    node86_value = label_value[85, :] * ap_value[36, 96:]
    node87_value = label_value[86, :] * ap_value[37, 96:]
    node88_value = node88_value * ap_value[38, 96:112]
    node89_value = node89_value * ap_value[39, 96:112]
    node90_value = node90_value * ap_value[40, 96:112]
    node91_value = node91_value * ap_value[41, 96:112]
    node92_value = node92_value * ap_value[42, 96:112]
    node93_value = node93_value * ap_value[43, 96:112]
    node94_value = node94_value * ap_value[44, 96:112]
    node95_value = node95_value * ap_value[45, 96:112]
    node96_value = node96_value * ap_value[46, 96:112]
    node97_value = node97_value * ap_value[47, 96:112]
    node98_value = node98_value * ap_value[48, 96:112]
    
    node88_value = torch.nn.functional.pad(node88_value, (0, 16), mode='constant', value=0)
    node89_value = torch.nn.functional.pad(node89_value, (0, 16), mode='constant', value=0)
    node90_value = torch.nn.functional.pad(node90_value, (0, 16), mode='constant', value=0)
    node91_value = torch.nn.functional.pad(node91_value, (0, 16), mode='constant', value=0)
    node92_value = torch.nn.functional.pad(node92_value, (0, 16), mode='constant', value=0)
    node93_value = torch.nn.functional.pad(node93_value, (0, 16), mode='constant', value=0)
    node94_value = torch.nn.functional.pad(node94_value, (0, 16), mode='constant', value=0)
    node95_value = torch.nn.functional.pad(node95_value, (0, 16), mode='constant', value=0)
    node96_value = torch.nn.functional.pad(node96_value, (0, 16), mode='constant', value=0)
    node97_value = torch.nn.functional.pad(node97_value, (0, 16), mode='constant', value=0)
    node98_value = torch.nn.functional.pad(node98_value, (0, 16), mode='constant', value=0)

    node115_value = torch.nn.functional.pad(node115_value, (0, 24), mode='constant', value=0)
    node116_value = torch.nn.functional.pad(node116_value, (0, 24), mode='constant', value=0)
    node117_value = torch.nn.functional.pad(node117_value, (0, 24), mode='constant', value=0)
    node118_value = torch.nn.functional.pad(node118_value, (0, 24), mode='constant', value=0)
    node119_value = torch.nn.functional.pad(node119_value, (0, 24), mode='constant', value=0)
    node120_value = torch.nn.functional.pad(node120_value, (0, 24), mode='constant', value=0)
    node121_value = torch.nn.functional.pad(node121_value, (0, 24), mode='constant', value=0)
    node122_value = torch.nn.functional.pad(node122_value, (0, 24), mode='constant', value=0)
    node123_value = torch.nn.functional.pad(node123_value, (0, 24), mode='constant', value=0)
    node124_value = torch.nn.functional.pad(node124_value, (0, 24), mode='constant', value=0)
    node125_value = torch.nn.functional.pad(node125_value, (0, 24), mode='constant', value=0)
    node126_value = torch.nn.functional.pad(node126_value, (0, 24), mode='constant', value=0)
    node127_value = torch.nn.functional.pad(node127_value, (0, 24), mode='constant', value=0)
    node128_value = torch.nn.functional.pad(node128_value, (0, 24), mode='constant', value=0)
    node129_value = torch.nn.functional.pad(node129_value, (0, 24), mode='constant', value=0)
    node130_value = torch.nn.functional.pad(node130_value, (0, 24), mode='constant', value=0)
    node131_value = torch.nn.functional.pad(node131_value, (0, 24), mode='constant', value=0)
    node132_value = torch.nn.functional.pad(node132_value, (0, 24), mode='constant', value=0)
    node133_value = torch.nn.functional.pad(node133_value, (0, 24), mode='constant', value=0)
    node134_value = torch.nn.functional.pad(node134_value, (0, 24), mode='constant', value=0)
    node135_value = torch.nn.functional.pad(node135_value, (0, 24), mode='constant', value=0)
    node136_value = torch.nn.functional.pad(node136_value, (0, 24), mode='constant', value=0)
    node137_value = torch.nn.functional.pad(node137_value, (0, 24), mode='constant', value=0)
    node138_value = torch.nn.functional.pad(node138_value, (0, 24), mode='constant', value=0)
    node139_value = torch.nn.functional.pad(node139_value, (0, 24), mode='constant', value=0)
    node140_value = torch.nn.functional.pad(node140_value, (0, 24), mode='constant', value=0)
    node141_value = torch.nn.functional.pad(node141_value, (0, 24), mode='constant', value=0)
    node142_value = torch.nn.functional.pad(node142_value, (0, 24), mode='constant', value=0)

    label_value[1, :] = node2_value
    label_value[2, :] = node3_value
    label_value[3, :] = node4_value
    label_value[4, :] = node5_value
    label_value[5, :] = node6_value
    label_value[6, :] = node7_value
    label_value[7, :] = node8_value

    label_value[17, :] = node18_value
    label_value[18, :] = node19_value
    label_value[19, :] = node20_value
    label_value[20, :] = node21_value
    label_value[21, :] = node22_value

    label_value[29, :] = node30_value
    label_value[30, :] = node31_value
    label_value[31, :] = node32_value
    
    label_value[37, :] = node38_value

    label_value[41, :] = node42_value
    label_value[42, :] = node43_value
    label_value[43, :] = node44_value
    label_value[44, :] = node45_value
    label_value[45, :] = node46_value
    label_value[46, :] = node47_value
    label_value[47, :] = node48_value
    label_value[48, :] = node49_value
    label_value[49, :] = node50_value
    label_value[50, :] = node51_value
    label_value[51, :] = node52_value
    label_value[52, :] = node53_value
    label_value[53, :] = node54_value

    label_value[65, :] = node66_value
    label_value[66, :] = node67_value
    label_value[67, :] = node68_value
    label_value[68, :] = node69_value
    label_value[69, :] = node70_value
    label_value[70, :] = node71_value
    label_value[71, :] = node72_value
    label_value[72, :] = node73_value
    label_value[73, :] = node74_value
    label_value[74, :] = node75_value
    label_value[75, :] = node76_value

    label_value[85, :] = node86_value
    label_value[86, :] = node87_value
    label_value[87, :] = node88_value
    label_value[88, :] = node89_value
    label_value[89, :] = node90_value
    label_value[90, :] = node91_value
    label_value[91, :] = node92_value
    label_value[92, :] = node93_value
    label_value[93, :] = node94_value
    label_value[94, :] = node95_value
    label_value[95, :] = node96_value
    label_value[96, :] = node97_value
    label_value[97, :] = node98_value
    label_value[98, :] = node99_value
    label_value[99, :] = node100_value
    label_value[100, :] = node101_value
    label_value[101, :] = node102_value

    label_value[114, :] = node115_value
    label_value[115, :] = node116_value
    label_value[116, :] = node117_value
    label_value[117, :] = node118_value
    label_value[118, :] = node119_value
    label_value[119, :] = node120_value
    label_value[120, :] = node121_value
    label_value[121, :] = node122_value
    label_value[122, :] = node123_value
    label_value[123, :] = node124_value
    label_value[124, :] = node125_value
    label_value[125, :] = node126_value
    label_value[126, :] = node127_value
    label_value[127, :] = node128_value
    label_value[128, :] = node129_value
    label_value[129, :] = node130_value
    label_value[130, :] = node131_value
    label_value[131, :] = node132_value
    label_value[132, :] = node133_value
    label_value[133, :] = node134_value
    label_value[134, :] = node135_value
    label_value[135, :] = node136_value
    label_value[136, :] = node137_value
    label_value[137, :] = node138_value
    label_value[138, :] = node139_value
    label_value[139, :] = node140_value
    label_value[140, :] = node141_value
    label_value[141, :] = node142_value

    data = Data(x=label_value, edge_index=edge_index, num_nodes=142)

    return data.to(device)

min_max = {
    'MRED': (0.00000533, 0.00375792),
    'NMED': (0.00000012, 0.00002442),
    'Delay': (1.70000000, 1.94000000),
    'Area': (1573.12400000, 1693.35600000),
    'Power': (0.00060700, 0.00088600),
}
    
def normalize(value, key):
    min_val, max_val = min_max[key]
    return (value - min_val) / (max_val - min_val)

def denormalize(value, key):
    min_val, max_val = min_max[key]
    return value * (max_val - min_val) + min_val

# if __name__ == "__main__":
#     state = [5, 4, 5, 1, 6, 3, 0, 7, 7, 1, 4, 2, 1, 4, 3, 1, 0, 5, 5, 2, 7, 5, 0, 1, 4, 1, 2, 5, 6, 3, 4, 7, 6, 5, 5, 6, 3, 1, 2, 2, 3, 0, 6, 2, 0, 4, 2, 5, 0]  # 示例49个位置
#     graph = state_to_graph(state, device)  
#     metrics = predict_metrics(graph) #MRED NMED Delay Area Power
#     print(metrics)

#     metric_names = ['MRED', 'NMED', 'Delay', 'Area', 'Power']
#     denorm_results = {k: denormalize(v, k) for k, v in zip(metric_names, metrics)}

#     print("\nDenormalized metrics:")
#     for k, v in denorm_results.items():
#         print(f"{k}: {v:.8f}")
