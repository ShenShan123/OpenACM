import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv

# ====================== Device ======================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ====================== Stage Node Index Ranges ======================
# Stage1 nodes: 41~84 → zero-based: 40~83
stage1_nodes = torch.arange(40, 84, device=device)

# Stage2 nodes: 85~112 → zero-based: 84~111
stage2_nodes = torch.arange(84, 112, device=device)

# Stage3 nodes: 113~142 → zero-based: 112~141
stage3_nodes = torch.arange(112, 142, device=device)


# ====================== Model Definition ======================
class SAGE(nn.Module):
    def __init__(self, in_feats, hid1_feats, hid2_feats, out_feats):
        super().__init__()
        self.conv1 = SAGEConv(in_feats, hid1_feats)
        self.conv2 = SAGEConv(hid1_feats, hid2_feats)
        self.conv3 = SAGEConv(hid2_feats, out_feats)

        # 79 selected nodes × 32 dims = 2528
        self.fc1 = nn.Linear(2528, 256)
        self.fc2 = nn.Linear(256, 5)
        self.ln1 = nn.LayerNorm(256)
        self.prelu1 = nn.PReLU()

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        # ----- stage 1 inference -----
        h1 = F.relu(self.conv1(x, edge_index))
        x1 = x.clone()
        x1[stage1_nodes] = h1[stage1_nodes]

        # ----- stage 2 inference -----
        h2 = F.relu(self.conv2(x1, edge_index))
        x2 = x1.clone()
        x2[stage2_nodes] = h2[stage2_nodes]

        # ----- stage 3 inference -----
        h3 = F.relu(self.conv3(x2, edge_index))
        x3 = x2.clone()
        x3[stage3_nodes] = h3[stage3_nodes]

        # Concatenate selected nodes (0-based index ranges)
        node_indices = []
        node_indices.extend(torch.arange(1, 8, device=device))     # 2~8
        node_indices.extend(torch.arange(17, 22, device=device))   # 18~22
        node_indices.extend(torch.arange(29, 32, device=device))   # 30~32
        node_indices.append(torch.tensor([37], device=device))     # 38
        node_indices.extend(torch.arange(41, 52, device=device))   # 42~52
        node_indices.extend(torch.arange(65, 74, device=device))   # 66~74
        node_indices.extend(torch.arange(85, 98, device=device))   # 86~98
        node_indices.extend(torch.arange(112, 142, device=device)) # 113~142

        node_indices_tensor = torch.cat([
            idx.reshape(-1) if idx.dim() > 0 else idx.unsqueeze(0)
            for idx in node_indices
        ])

        # Gather node features
        node_features = x3[node_indices_tensor]
        x_cat = node_features.view(-1)

        # ----- fully connected layers -----
        x_cat = self.fc1(x_cat)
        x_cat = self.ln1(x_cat)
        x_cat = self.prelu1(x_cat)
        x_cat = self.fc2(x_cat)
        x_cat = F.softplus(x_cat)
        return x_cat


# ====================== Model Manager (Singleton) ======================
class ModelManager:
    """Singleton manager: handles model loading and inference."""
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
        weights_path = os.path.join(os.path.dirname(__file__), "best_model_weights_16.pth")
        self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
        self.model.eval()
        self._initialized = True

    def predict(self, graph):
        """Run inference and return 5 performance metrics."""
        graph = graph.to(self.device)
        with torch.no_grad():
            output = self.model(graph)
        return output.tolist()

    def get_model(self):
        """Return the underlying model instance."""
        return self.model


# ====================== Global Model Instance ======================
model_manager = ModelManager()


# ====================== Public Inference API ======================
def predict_metrics(graph):
    """
    Inference API (external call)

    Args:
        graph: PyG Data object

    Returns:
        list: [MRED, NMED, Delay, Area, Power]
    """
    return model_manager.predict(graph)
