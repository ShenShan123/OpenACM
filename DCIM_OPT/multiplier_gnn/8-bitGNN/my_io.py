import os
import numpy as np
import pandas as pd 
import torch
from torch_geometric.data import Data
from gnn_predictor import predict_metrics
device = torch.device('cuda' if torch.cuda.is_available() else 'cuda')  # keep original logic

def load_graph_from_csv(adjacency_matrix_path, node_features_tensor):
    """
    Construct a PyG Data object from an adjacency-matrix CSV and a node-feature tensor.
    
    Args:
        adjacency_matrix_path (str): Path to adjacency matrix CSV file (e.g., 'Graph.csv')
        node_features_tensor (torch.Tensor): Node feature tensor of shape (num_nodes, feature_dim)
        
    Returns:
        torch_geometric.data.Data: PyG graph object
    """
    # Read adjacency matrix from CSV
    adj_matrix = pd.read_csv(adjacency_matrix_path, header=None).values
    
    # (Optional) Convert to sparse matrix format if the matrix is large
    # adj_sparse = csr_matrix(adj_matrix)
    
    # Get edge indices in COO format
    rows, cols = np.nonzero(adj_matrix)
    edge_index = torch.tensor(np.stack([rows, cols], axis=0), dtype=torch.long)
    
    # Create PyG Data object
    data = Data(
        x=node_features_tensor,           # node features
        edge_index=edge_index,           # edge indices
        num_nodes=node_features_tensor.shape[0]
    )
    
    return data

def generate_cartesian_indices(n_dims, device):
    """Generate all 2^n_dims binary combinations as Cartesian product indices."""
    return torch.cartesian_prod(*[torch.tensor([0, 1], device=device) for _ in range(n_dims)])

def compute_node_value(indices, *tensors):
    """
    Given indices (Cartesian product over {0,1}) and a list of 1D/2D tensors,
    compute the product of selected entries across all tensors.
    """
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
    return result.unsqueeze(0)  # shape: (1, N)

def state_to_graph(state, device):
    # Convert state to a 9 × 128 tensor
    ap_value = {
    '0': torch.tensor([0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    # Expanded binary pattern for approximate compressor type 0
    '1': torch.tensor([0,1,1,1,1,0,0,1,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    # Expanded binary pattern for approximate compressor type 1
    '2': torch.tensor([0,1,1,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    # Expanded binary pattern for approximate compressor type 2
    '3': torch.tensor([1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,0,0,0,-1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    # Expanded binary pattern for approximate compressor type 3
    '4': torch.tensor([0,1,1,1,1,0,0,0,1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,], device=device).float(),
    # Expanded binary pattern for approximate compressor type 4
    '5': torch.tensor([0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,1,-1,0,0,1,-1,0,-2,0,-2,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    # Expanded binary pattern for approximate compressor type 5
    '6': torch.tensor([0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1,0,0,-1,-1,0,0,0,0,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float(),
    # Expanded binary pattern for approximate compressor type 6
    '7': torch.tensor([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,-1,-1,0,0,1,1,0,-1,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float()
    # Expanded binary pattern for approximate compressor type 7
    }

    base_dir = os.path.dirname(__file__)
    label_dir = os.path.join(base_dir, 'FEATURE.csv')
    batch = 1

    # Map each state index to its corresponding ap_value vector and reshape
    state_vector = torch.stack([ap_value[str(i)] for i in state]).to(device)
    ap_value = state_vector.view(batch, 9, 128)
    label_df = pd.read_csv(label_dir, header=None)
    label_value = torch.tensor(label_df.values, device=device).float()
    label_value = label_value.view(batch, 38, 32)
    
    # Predefined primitive cell probability vectors
    ha_value = torch.tensor([0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float()
    fa_value = torch.tensor([0,1,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], device=device).float()
    e_4_2_value = torch.tensor([0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,0,1,0,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1], device=device).float()
    and_value = torch.tensor([0.75, 0.25], device=device)
    pp_value = torch.tensor([1, 0], device=device)

    # Node 64 (HA-based)
    node64_S_1 = torch.matmul(label_value[0,0,:], ha_value[:32])
    node64_C_1 = torch.matmul(label_value[0,0,:], ha_value[32:64])
    node64_S = torch.stack([1-node64_S_1, node64_S_1])
    node64_C = torch.stack([1-node64_C_1, node64_C_1])

    # Node 72 (HA-based)
    node72_S_1 = torch.matmul(label_value[0,8,:], ha_value[:32])
    node72_C_1 = torch.matmul(label_value[0,8,:], ha_value[32:64])
    node72_S = torch.stack([1-node72_S_1,node72_S_1])
    node72_C = torch.stack([1-node72_C_1,node72_C_1])

    # Node 75 (HA-based)
    node75_S_1 = torch.matmul(label_value[0,11,:], ha_value[:32])
    node75_C_1 = torch.matmul(label_value[0,11,:], ha_value[32:64])
    node75_S = torch.stack([1-node75_S_1,node75_S_1])
    node75_C = torch.stack([1-node75_C_1,node75_C_1])

    # Node 76 (HA-based)
    node76_S_1 = torch.matmul(label_value[0,12,:], ha_value[:32])
    node76_C_1 = torch.matmul(label_value[0,12,:], ha_value[32:64])
    node76_S = torch.stack([1-node76_S_1,node76_S_1])
    node76_C = torch.stack([1-node76_C_1,node76_C_1])

    # Node 88 (HA-based)
    node88_S_1 = torch.matmul(label_value[0,24,:], ha_value[:32])
    node88_C_1 = torch.matmul(label_value[0,24,:], ha_value[32:64])
    node88_S = torch.stack([1-node88_S_1,node88_S_1])
    node88_C = torch.stack([1-node88_C_1,node88_C_1])

    # Node 68 (exact 4-2)
    node68_S_1 = torch.matmul(label_value[0,4,:], e_4_2_value[:32])
    node68_C_1 = torch.matmul(label_value[0,4,:], e_4_2_value[32:64])
    node68_S = torch.stack([1-node68_S_1,node68_S_1])
    node68_C = torch.stack([1-node68_C_1,node68_C_1])

    # Node 69 (exact 4-2)
    node69_S_1 = torch.matmul(label_value[0,5,:], e_4_2_value[:32])
    node69_C_1 = torch.matmul(label_value[0,5,:], e_4_2_value[32:64])
    node69_S = torch.stack([1-node69_S_1,node69_S_1])
    node69_C = torch.stack([1-node69_C_1,node69_C_1])

    # Node 70 (exact 4-2)
    node70_S_1 = torch.matmul(label_value[0,6,:], e_4_2_value[:32])
    node70_C_1 = torch.matmul(label_value[0,6,:], e_4_2_value[32:64])
    node70_S = torch.stack([1-node70_S_1,node70_S_1])
    node70_C = torch.stack([1-node70_C_1,node70_C_1])

    # Node 84 (exact 4-2)
    node84_S_1 = torch.matmul(label_value[0,20,:], e_4_2_value[:32])
    node84_C_1 = torch.matmul(label_value[0,20,:], e_4_2_value[32:64])
    node84_S = torch.stack([1-node84_S_1,node84_S_1])
    node84_C = torch.stack([1-node84_C_1,node84_C_1])

    # Node 85 (exact 4-2)
    node85_S_1 = torch.matmul(label_value[0,21,:], e_4_2_value[:32])
    node85_C_1 = torch.matmul(label_value[0,21,:], e_4_2_value[32:64])
    node85_S = torch.stack([1-node85_S_1,node85_S_1])
    node85_C = torch.stack([1-node85_C_1,node85_C_1])

    # Node 86 (exact 4-2)
    node86_S_1 = torch.matmul(label_value[0,22,:], e_4_2_value[:32])
    node86_C_1 = torch.matmul(label_value[0,22,:], e_4_2_value[32:64])
    node86_S = torch.stack([1-node86_S_1,node86_S_1])
    node86_C = torch.stack([1-node86_C_1,node86_C_1])

    # Node 71 (FA-based)
    node71_S_1 = torch.matmul(label_value[0,7,:], fa_value[:32])
    node71_C_1 = torch.matmul(label_value[0,7,:], fa_value[32:64])
    node71_S = torch.stack([1-node71_S_1,node71_S_1])
    node71_C = torch.stack([1-node71_C_1,node71_C_1])

    # Node 74 (FA-based)
    node74_S_1 = torch.matmul(label_value[0,10,:], fa_value[:32])
    node74_C_1 = torch.matmul(label_value[0,10,:], fa_value[32:64])
    node74_S = torch.stack([1-node74_S_1,node74_S_1])
    node74_C = torch.stack([1-node74_C_1,node74_C_1])

    # Node 87 (FA-based)
    node87_S_1 = torch.matmul(label_value[0,23,:], fa_value[:32])
    node87_C_1 = torch.matmul(label_value[0,23,:], fa_value[32:64])
    node87_S = torch.stack([1-node87_S_1,node87_S_1])
    node87_C = torch.stack([1-node87_C_1,node87_C_1])

    # Node 89 (FA-based)
    node89_S_1 = torch.matmul(label_value[0,25,:], fa_value[:32])
    node89_C_1 = torch.matmul(label_value[0,25,:], fa_value[32:64])
    node89_S = torch.stack([1-node89_S_1,node89_S_1])
    node89_C = torch.stack([1-node89_C_1,node89_C_1])

    # Approximate compressor nodes with ap_value (batch dimension)
    node65_S_1 = torch.sum(label_value[:, 1, :] * ap_value[:, 0, :32], dim=1)
    node65_C_1 = torch.sum(label_value[:, 1, :] * ap_value[:, 0, 32:64], dim=1)
    node65_S = torch.stack([1-node65_S_1,node65_S_1], dim=1)
    node65_C = torch.stack([1-node65_C_1,node65_C_1], dim=1)

    node66_S_1 = torch.sum(label_value[:, 2, :] * ap_value[:, 1, :32], dim=1)
    node66_C_1 = torch.sum(label_value[:, 2, :] * ap_value[:, 1, 32:64], dim=1)
    node66_S = torch.stack([1-node66_S_1,node66_S_1], dim=1)
    node66_C = torch.stack([1-node66_C_1,node66_C_1], dim=1)

    node67_S_1 = torch.sum(label_value[:, 3, :] * ap_value[:, 2, :32], dim=1)
    node67_C_1 = torch.sum(label_value[:, 3, :] * ap_value[:, 2, 32:64], dim=1)
    node67_S = torch.stack([1-node67_S_1,node67_S_1], dim=1)
    node67_C = torch.stack([1-node67_C_1,node67_C_1], dim=1)

    node73_S_1 = torch.sum(label_value[:, 9, :] * ap_value[:, 3, :32], dim=1)
    node73_C_1 = torch.sum(label_value[:, 9, :] * ap_value[:, 3, 32:64], dim=1)
    node73_S = torch.stack([1-node73_S_1,node73_S_1], dim=1)
    node73_C = torch.stack([1-node73_C_1,node73_C_1], dim=1)

    node77_S_1 = torch.sum(label_value[:, 13, :] * ap_value[:, 4, :32], dim=1)
    node77_C_1 = torch.sum(label_value[:, 13, :] * ap_value[:, 4, 32:64], dim=1)
    node77_S = torch.stack([1-node77_S_1,node77_S_1], dim=1)
    node77_C = torch.stack([1-node77_C_1,node77_C_1], dim=1)

    node78_S_1 = torch.sum(label_value[:, 14, :] * ap_value[:, 5, :32], dim=1)
    node78_C_1 = torch.sum(label_value[:, 14, :] * ap_value[:, 5, 32:64], dim=1)
    node78_S = torch.stack([1-node78_S_1,node78_S_1], dim=1)
    node78_C = torch.stack([1-node78_C_1,node78_C_1], dim=1)

    # ----------- Node value computation (multi-input composition) -----------

    # Example: deduce device from an existing tensor
    device = node65_S.device

    # node79
    idxs_4 = generate_cartesian_indices(4, device)
    node79_value = compute_node_value(idxs_4, node65_S, node64_C, and_value, and_value)

    # node80
    node80_value = compute_node_value(idxs_4, node66_S, node65_C, node72_S, and_value)

    # node81
    node81_value = compute_node_value(idxs_4, node67_S, node73_S, node66_C, node72_C)

    # node82 (5-input combination)
    idxs_5 = generate_cartesian_indices(5, device)
    node82_value = compute_node_value(idxs_5, node68_S, node67_C, node74_S, node73_C, pp_value)

    node82_S_1 = torch.matmul(node82_value, e_4_2_value[:32])
    node82_S = torch.stack([1 - node82_S_1, node82_S_1], dim=1)
    node82_C_1 = torch.matmul(node82_value, e_4_2_value[32:64])
    node82_C = torch.stack([1 - node82_C_1, node82_C_1], dim=1)
    node82_Co_1 = torch.matmul(node82_value, e_4_2_value[64:])
    node82_Co = torch.stack([1 - node82_Co_1, node82_Co_1], dim=1)

    # node83 (5-input combination)
    node83_value = compute_node_value(idxs_5, node69_S, node68_C, node75_S, node74_C, node82_Co)

    node83_S_1 = torch.matmul(node83_value, e_4_2_value[:32])
    node83_S = torch.stack([1 - node83_S_1, node83_S_1], dim=1)
    node83_C_1 = torch.matmul(node83_value, e_4_2_value[32:64])
    node83_C = torch.stack([1 - node83_C_1, node83_C_1], dim=1)

    # node79 S/C (AP-based)
    node79_S_1 = torch.sum(node79_value * ap_value[:, 6, :16], dim=1)
    node79_C_1 = torch.sum(node79_value * ap_value[:, 6, 32:48], dim=1)
    node79_S = torch.stack([1 - node79_S_1, node79_S_1], dim=1)
    node79_C = torch.stack([1 - node79_C_1, node79_C_1], dim=1)

    # node80 S/C (AP-based)
    node80_S_1 = torch.sum(node80_value * ap_value[:, 7, :16], dim=1)
    node80_C_1 = torch.sum(node80_value * ap_value[:, 7, 32:48], dim=1)
    node80_S = torch.stack([1 - node80_S_1, node80_S_1], dim=1)
    node80_C = torch.stack([1 - node80_C_1, node80_C_1], dim=1)

    # node81 S/C (AP-based)
    node81_S_1 = torch.sum(node81_value * ap_value[:, 8, :16], dim=1)
    node81_C_1 = torch.sum(node81_value * ap_value[:, 8, 32:48], dim=1)
    node81_S = torch.stack([1 - node81_S_1, node81_S_1], dim=1)
    node81_C = torch.stack([1 - node81_C_1, node81_C_1], dim=1)

    # Subsequent nodes 90 ~ 101 are all 3-input compositions; reuse idxs_3
    idxs_3 = generate_cartesian_indices(3, device)

    node90_value = compute_node_value(idxs_3, node77_S, node76_C, node89_C)
    node90_C_1 = torch.matmul(node90_value, fa_value[32:40])
    node90_C = torch.stack([1 - node90_C_1, node90_C_1], dim=1)

    node91_value = compute_node_value(idxs_3, node78_S, node77_C, node90_C)
    node91_C_1 = torch.matmul(node91_value, fa_value[32:40])
    node91_C = torch.stack([1 - node91_C_1, node91_C_1], dim=1)

    node92_value = compute_node_value(idxs_3, node79_S, node78_C, node91_C)
    node92_C_1 = torch.matmul(node92_value, fa_value[32:40])
    node92_C = torch.stack([1 - node92_C_1, node92_C_1], dim=1)

    node93_value = compute_node_value(idxs_3, node80_S, node79_C, node92_C)
    node93_C_1 = torch.matmul(node93_value, fa_value[32:40])
    node93_C = torch.stack([1 - node93_C_1, node93_C_1], dim=1)

    node94_value = compute_node_value(idxs_3, node81_S, node80_C, node93_C)
    node94_C_1 = torch.matmul(node94_value, fa_value[32:40])
    node94_C = torch.stack([1 - node94_C_1, node94_C_1], dim=1)

    node95_value = compute_node_value(idxs_3, node82_S, node81_C, node94_C)
    node95_C_1 = torch.matmul(node95_value, fa_value[32:40])
    node95_C = torch.stack([1 - node95_C_1, node95_C_1], dim=1)

    node96_value = compute_node_value(idxs_3, node83_S, node82_C, node95_C)
    node96_C_1 = torch.matmul(node96_value, fa_value[32:40])
    node96_C = torch.stack([1 - node96_C_1, node96_C_1], dim=1)

    node97_value = compute_node_value(idxs_3, node84_S, node83_C, node96_C)
    node97_C_1 = torch.matmul(node97_value, fa_value[32:40])
    node97_C = torch.stack([1 - node97_C_1, node97_C_1], dim=1)

    node98_value = compute_node_value(idxs_3, node85_S, node84_C, node97_C)
    node98_C_1 = torch.matmul(node98_value, fa_value[32:40])
    node98_C = torch.stack([1 - node98_C_1, node98_C_1], dim=1)

    node99_value = compute_node_value(idxs_3, node86_S, node85_C, node98_C)
    node99_C_1 = torch.matmul(node99_value, fa_value[32:40])
    node99_C = torch.stack([1 - node99_C_1, node99_C_1], dim=1)

    node100_value = compute_node_value(idxs_3, node87_S, node86_C, node99_C)
    node100_C_1 = torch.matmul(node100_value, fa_value[32:40])
    node100_C = torch.stack([1 - node100_C_1, node100_C_1], dim=1)

    node101_value = compute_node_value(idxs_3, and_value, node87_C, node100_C)
    node101_C_1 = torch.matmul(node101_value, fa_value[32:40])
    node101_C = torch.stack([1 - node101_C_1, node101_C_1], dim=1)

    # Overwrite label_value entries with AP-tail or composed patterns
    node65_value = label_value[:, 1, :] * ap_value[:, 0, 96:]
    node66_value = label_value[:, 2, :] * ap_value[:, 1, 96:]
    node67_value = label_value[:, 3, :] * ap_value[:, 2, 96:]
    node73_value = label_value[:, 9, :] * ap_value[:, 3, 96:]

    node77_value = label_value[:, 13, :] * ap_value[:, 4, 96:]
    node78_value = label_value[:, 14, :] * ap_value[:, 5, 96:]
    node79_value = node79_value * ap_value[:, 6, 96:112]
    node80_value = node80_value * ap_value[:, 7, 96:112]
    node81_value = node81_value * ap_value[:, 8, 96:112]

    # Pad to 32 entries where necessary
    node79_value = torch.nn.functional.pad(node79_value, (0, 16), mode='constant', value=0)
    node80_value = torch.nn.functional.pad(node80_value, (0, 16), mode='constant', value=0)
    node81_value = torch.nn.functional.pad(node81_value, (0, 16), mode='constant', value=0)
    
    node90_value = torch.nn.functional.pad(node90_value, (0, 24), mode='constant', value=0)
    node91_value = torch.nn.functional.pad(node91_value, (0, 24), mode='constant', value=0)
    node92_value = torch.nn.functional.pad(node92_value, (0, 24), mode='constant', value=0)
    node93_value = torch.nn.functional.pad(node93_value, (0, 24), mode='constant', value=0)
    node94_value = torch.nn.functional.pad(node94_value, (0, 24), mode='constant', value=0)
    node95_value = torch.nn.functional.pad(node95_value, (0, 24), mode='constant', value=0)
    node96_value = torch.nn.functional.pad(node96_value, (0, 24), mode='constant', value=0)
    node97_value = torch.nn.functional.pad(node97_value, (0, 24), mode='constant', value=0)
    node98_value = torch.nn.functional.pad(node98_value, (0, 24), mode='constant', value=0)
    node99_value = torch.nn.functional.pad(node99_value, (0, 24), mode='constant', value=0)
    node100_value = torch.nn.functional.pad(node100_value, (0, 24), mode='constant', value=0)
    node101_value = torch.nn.functional.pad(node101_value, (0, 24), mode='constant', value=0)

    # Update label_value with the final node patterns
    label_value[:,1,:] = node65_value
    label_value[:,2,:] = node66_value
    label_value[:,3,:] = node67_value
    label_value[:,9,:] = node73_value
    label_value[:,13,:] = node77_value
    label_value[:,14,:] = node78_value

    label_value[:,15,:] = node79_value
    label_value[:,16,:] = node80_value
    label_value[:,17,:] = node81_value
    label_value[:,18,:] = node82_value
    label_value[:,19,:] = node83_value

    label_value[:,26,:] = node90_value
    label_value[:,27,:] = node91_value
    label_value[:,28,:] = node92_value
    label_value[:,29,:] = node93_value
    label_value[:,30,:] = node94_value
    label_value[:,31,:] = node95_value
    label_value[:,32,:] = node96_value
    label_value[:,33,:] = node97_value
    label_value[:,34,:] = node98_value
    label_value[:,35,:] = node99_value
    label_value[:,36,:] = node100_value
    label_value[:,37,:] = node101_value

    # Collect all groups into a single tensor
    df_list = []
    for group in label_value:
        if isinstance(group, torch.Tensor):
            # group is already on GPU, directly append
            group_gpu = group
            df_list.append(group_gpu)

    # Concatenate all groups along the row dimension
    df_total = torch.cat(df_list, dim=0)

    # Base node template: fixed AND gate probability for the first two entries
    base_node = torch.zeros(32)  # CPU tensor
    base_node[0] = 0.75
    base_node[1] = 0.25
    fixed_nodes = torch.stack([base_node.clone() for _ in range(64)], dim=0)
    fixed_nodes = fixed_nodes.to(device)

    # Final node features: [fixed primitive nodes; computed label_value nodes]
    node_features = torch.cat([fixed_nodes, df_total], dim=0)

    # Build PyG graph from Graph.csv
    graph = load_graph_from_csv(os.path.join(base_dir, 'Graph.csv'), node_features)
    
    return graph


min_max = {
    'MRED': (0.00086214, 0.15909895),
    'NMED': (0.00009676, 0.00313291),
    'Delay': (1.30000000, 1.34000000),
    'Area': (435.97400000, 480.92800000),
    'Power': (0.00014600, 0.00018400),
}

def normalize(value, key):
    """Normalize a scalar metric to [0,1] using pre-defined min/max."""
    min_val, max_val = min_max[key]
    return (value - min_val) / (max_val - min_val)

def denormalize(value, key):
    """Denormalize a [0,1] metric back to its original range."""
    min_val, max_val = min_max[key]
    return value * (max_val - min_val) + min_val

# if __name__ == "__main__":
#     # Example: 9 compressor positions
#     state = [4, 0, 4, 5, 6, 2, 0, 4, 3]
#     graph = state_to_graph(state, device)
#     metrics = predict_metrics(graph)  # MRED, NMED, Delay, Area, Power
#     print(metrics)

#     metric_names = ['MRED', 'NMED', 'Delay', 'Area', 'Power']
#     denorm_results = {k: denormalize(v, k) for k, v in zip(metric_names, metrics)}

#     print("\nDenormalized metrics:")
#     for k, v in denorm_results.items():
#         print(f"{k}: {v:.6f}")
