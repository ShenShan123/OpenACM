import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
logger = logging.getLogger("BORL.actor_net")
device = torch.device("cpu")


class ActorPolicyNet(nn.Module):
    def __init__(self, input_dim, action_dim=3, hidden_dim=64):
        super(ActorPolicyNet, self).__init__()

        logger.info(f"Creating ActorPolicyNet, input_dim: {input_dim}, action_dim: {action_dim}, hidden_dim: {hidden_dim}")

        self.action_dim = action_dim
        self.input_dim = input_dim

        self.fc1 = nn.Linear(input_dim, hidden_dim).to(device)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim).to(device)
        self.fc3 = nn.Linear(hidden_dim, action_dim * input_dim).to(device)

    def forward(self, x):
        try:
            x = x.to(device)

            logger.debug(f"ActorPolicyNet input shape: {x.shape}")

            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = self.fc3(x)

            logger.debug(f"FC3 output shape: {x.shape}")

            batch_size = x.shape[0]
            expected_shape = (batch_size, self.action_dim, self.input_dim)
            logger.debug(f"Expected reshape shape: {expected_shape}")

            if x.numel() != torch.prod(torch.tensor(expected_shape)):
                logger.warning(f"Cannot reshape to expected shape {expected_shape}, actual shape {x.shape}")
                actual_input_dim = x.numel() // (batch_size * self.action_dim)
                logger.warning(f"Inferred input_dim: {actual_input_dim}")
                x = x.view(batch_size, self.action_dim, actual_input_dim)
            else:
                x = x.view(batch_size, self.action_dim, self.input_dim)

            logger.debug(f"Reshaped output shape: {x.shape}")

            x = F.softmax(x, dim=1)

            return x

        except Exception as e:
            logger.error(f"ActorPolicyNet forward error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            return torch.zeros((x.shape[0], self.action_dim, self.input_dim)).to(device)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    input_dim = 10
    model = ActorPolicyNet(input_dim)
    sample_input = torch.randn(1, input_dim)
    output = model(sample_input)

    print("Output shape:", output.shape)
