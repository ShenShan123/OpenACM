from sram_sizing.borl_model.actor_net import ActorPolicyNet
from sram_sizing.borl_model.critic_net import CriticNet
import torch.nn as nn
import torch
from torch.distributions import Categorical
from sram_sizing.borl_model.buffer import Memory
import logging
logger = logging.getLogger("BORL.actor_critic")
device = torch.device("cpu")


class ActorCritic(nn.Module):
    def __init__(self, input_dim, action_dim, hidden_dim=64, memory=Memory()):
        super(ActorCritic, self).__init__()

        logger.info(f"Creating ActorCritic model, input_dim: {input_dim}, action_dim: {action_dim}, hidden_dim: {hidden_dim}")

        # actor
        self.action_layer = ActorPolicyNet(input_dim, action_dim, hidden_dim=64).to(device)

        # critic
        self.value_layer = CriticNet(input_dim, hidden_dim=64).to(device)

        self.memory = memory

    def act(self, state_spec):
        try:
            state_spec = state_spec.to(device)

            logger.debug(f"State shape: {state_spec.shape}")

            action_probs = self.action_layer(state_spec)
            logger.debug(f"Action probabilities shape: {action_probs.shape}")

            if action_probs.dim() == 3:  # [batch, action_dim, input_dim]
                action_probs = action_probs.squeeze(0).permute(1, 0)  # [input_dim, action_dim]

            logger.debug(f"Adjusted action probabilities shape: {action_probs.shape}")

            dist = torch.distributions.Categorical(probs=action_probs)
            sampled = dist.sample()  # [input_dim]

            action = sampled.unsqueeze(0)  # [1, input_dim]
            log_prob = dist.log_prob(sampled)
            log_prob_sum = torch.sum(log_prob, dim=0)

            self.memory.states_spec.append(state_spec)
            self.memory.actions.append(action)
            self.memory.logprobs.append(log_prob_sum)

            logger.debug(f"Sampled action shape: {action.shape}")
            return action.detach()

        except Exception as e:
            logger.error(f"act() error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            return torch.zeros_like(state_spec).to(device)

    def evaluate(self, state_spec, action):
        try:
            state_spec = state_spec.to(device)
            action = action.to(device)

            action_probs = self.action_layer(state_spec)

            probs = action_probs
            if action_probs.dim() == 3:  # [batch, action_dim, input_dim]
                probs = action_probs.permute(0, 2, 1)  # → [batch, input_dim, action_dim]

            dists = Categorical(probs=probs)

            action_logprobs = dists.log_prob(action)
            log_prob_sum = action_logprobs.sum(dim=1)

            dist_entropy = dists.entropy()
            dist_entropy_sum = dist_entropy.sum(dim=1)

            state_value = self.value_layer(state_spec)

            return log_prob_sum, torch.squeeze(state_value), dist_entropy_sum

        except Exception as e:
            logger.error(f"evaluate() error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            return (torch.zeros(state_spec.shape[0]).to(device),
                    torch.zeros(state_spec.shape[0]).to(device),
                    torch.zeros(state_spec.shape[0]).to(device))
