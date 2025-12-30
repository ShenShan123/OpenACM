import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
logger = logging.getLogger("BORL.critic_net")
device = torch.device("cpu")


class CriticNet(nn.Module):
    def __init__(self, input_dim, hidden_dim=64):
        super(CriticNet, self).__init__()

        logger.info(f"Creating CriticNet, input_dim: {input_dim}, hidden_dim: {hidden_dim}")

        self.fc1 = nn.Linear(input_dim, hidden_dim).to(device)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim).to(device)
        self.fc3 = nn.Linear(hidden_dim, 1).to(device)

    def forward(self, x):
        try:
            x = x.to(device)

            logger.debug(f"CriticNet input shape: {x.shape}")

            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = self.fc3(x)

            logger.debug(f"CriticNet output shape: {x.shape}")

            return x

        except Exception as e:
            logger.error(f"CriticNet forward error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            if x.dim() == 2:
                return torch.zeros((x.shape[0], 1)).to(device)
            else:
                return torch.zeros(1).to(device)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    input_dim = 10
    critic = CriticNet(input_dim)
    sample_input = torch.randn(1, input_dim)
    value_estimate = critic(sample_input)

    print("Critic output (value estimate):", value_estimate.item())
