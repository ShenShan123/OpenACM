import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv

# ====================== Device ======================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ====================== Stage Node Sets ======================
stage1_nodes = torch.tensor([64,65,66,67,68,69,70,71,72,73,74,75], dtype=torch.long, device=device)
stage2_nodes = torch.tensor([76,77,78,79,80,81,82,83,84,85,86,87], dtype=torch.long, device=device)
stage3_nodes = torch.tensor([88,89,90,91,92,93,94,95,96,97,98,99,100,101], dtype=torch.long, device=device)

# ====================== Model Definition ======================
class SAGE(nn.Module):
    def __init__(self, in_feats, hid1_feats, hid2_feats, out_feats):
        super().__init__()
        self.conv1 = SAGEConv(in_feats, hid1_feats)
        self.conv2 = SAGEConv(hid1_feats, hid2_feats)
        self.conv3 = SAGEConv(hid2_feats, out_feats)
        
        # 736 = (selected nodes × 32)
        self.fc1 = nn.Linear(736, 256)
        self.fc2 = nn.Linear(256, 5)
        self.ln1 = nn.LayerNorm(256)
        self.prelu1 = nn.PReLU()

    def forward(self, data, stage1_nodes, stage2_nodes, stage3_nodes):
        x, edge_index = data.x, data.edge_index

        # ---- Stage 1 ----
        h1 = F.relu(self.conv1(x, edge_index))
        x1 = x.clone()
        x1[stage1_nodes] = h1[stage1_nodes]

        # ---- Stage 2 ----
        h2 = F.relu(self.conv2(x1, edge_index))
        x2 = x1.clone()
        x2[stage2_nodes] = h2[stage2_nodes]

        # ---- Stage 3 ----
        h3 = F.relu(self.conv3(x2, edge_index))
        x3 = x2.clone()
        x3[stage3_nodes] = h3[stage3_nodes]

        # Concatenate selected node features
        node_indices_specific = torch.tensor([65, 66, 67, 73, 77, 78, 79, 80, 81, 82, 83], device=device)
        node_features_specific = x3[node_indices_specific]

        # Range 90–101 (inclusive of start, exclusive of end)
        node_indices_90_102 = torch.arange(90, 102, device=device)
        node_features_90_102 = x3[node_indices_90_102]

        x_cat = torch.cat([node_features_specific, node_features_90_102], dim=0).view(-1)
        x_cat = self.fc1(x_cat)
        x_cat = self.ln1(x_cat)
        x_cat = self.prelu1(x_cat)
        x_cat = self.fc2(x_cat)
        x_cat = F.softplus(x_cat)

        return x_cat


# ====================== Model Manager (Singleton) ======================
class ModelManager:
    """
    Singleton manager for loading and running the GNN model.
    Ensures the model is loaded only once and reused for all inference calls.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.device = device
        self.model = SAGE(in_feats=32, hid1_feats=32, hid2_feats=32, out_feats=32).to(self.device)
        self.model.load_state_dict(torch.load('best_model_weights_8.pth', map_location=self.device))
        self.model.eval()
        self._initialized = True
    
    def predict(self, graph):
        """
        Perform inference and return GNN-predicted metrics.

        Args:
            graph: PyG Data object

        Returns:
            list: predicted [MRED, NMED, Delay, Area, Power]
        """
        graph = graph.to(self.device)
        with torch.no_grad():
            output = self.model(graph, stage1_nodes, stage2_nodes, stage3_nodes)
        return output.tolist()
    
    def get_model(self):
        """Return the underlying model instance for advanced access."""
        return self.model


# ====================== Global Model Manager Instance ======================
model_manager = ModelManager()

# ====================== Inference API ======================
def predict_metrics(graph):
    """
    Wrapper function for external inference calls.

    Args:
        graph: PyG Data object

    Returns:
        list: [MRED, NMED, Delay, Area, Power]
    """
    return model_manager.predict(graph)
