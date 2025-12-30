import torch.nn as nn
import torch
from sram_sizing.borl_model.actor_critic import ActorCritic
import logging
logger = logging.getLogger("BORL.ppo")

device = torch.device("cpu")


class PPO:
    def __init__(self, state_spec_dim, action_dim, hidden_dim, lr, betas, gamma, K_epochs, eps_clip):
        self.lr = lr
        self.betas = betas
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs

        logger.info(f"Initializing PPO, state_dim: {state_spec_dim}, action_dim: {action_dim}, lr: {lr}")

        self.policy = ActorCritic(state_spec_dim, action_dim, hidden_dim).to(device)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr, betas=betas)

        self.policy_old = ActorCritic(state_spec_dim, action_dim, hidden_dim).to(device)

        self.policy_old.load_state_dict(self.policy.state_dict())

        for name, param in self.policy.named_parameters():
            param.data = param.data.to(device)
        for name, param in self.policy_old.named_parameters():
            param.data = param.data.to(device)

        self.MseLoss = nn.MSELoss()

    def update(self, memory):
        """Update policy network"""
        try:
            if len(memory.rewards) == 0:
                logger.warning("Memory is empty, skipping update")
                return

            rewards = []
            discounted_reward = 0
            for reward, is_terminal in zip(reversed(memory.rewards), reversed(memory.is_terminals)):
                if is_terminal:
                    discounted_reward = 0
                discounted_reward = reward + (self.gamma * discounted_reward)
                rewards.insert(0, discounted_reward)

            rewards = torch.tensor(rewards, dtype=torch.float64).to(device)

            if rewards.dim() == 0:
                rewards = rewards.unsqueeze(0)

            if rewards.size()[0] > 1:
                rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-4)

            logger.debug(f"Rewards shape: {rewards.shape}, mean: {rewards.mean()}, std: {rewards.std()}")

            old_spec_states = torch.stack(memory.states_spec).to(device).detach()
            old_actions = torch.stack(memory.actions).to(device).detach()
            old_logprobs = torch.stack(memory.logprobs).to(device).detach()

            if old_spec_states.dim() > 2:
                old_spec_states = old_spec_states.squeeze(1)
            if old_actions.dim() > 2:
                old_actions = old_actions.squeeze(1)

            logger.debug(f"States shape: {old_spec_states.shape}, actions shape: {old_actions.shape}, logprobs shape: {old_logprobs.shape}")

            for _ in range(self.K_epochs):
                logprobs, state_values, dist_entropy = self.policy.evaluate(old_spec_states, old_actions)

                ratios = torch.exp(logprobs - old_logprobs.detach())

                advantages = rewards - state_values.detach()
                surr1 = ratios * advantages
                surr2 = torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
                loss = -torch.min(surr1, surr2) + 0.5 * self.MseLoss(state_values, rewards) - 0.01 * dist_entropy

                self.optimizer.zero_grad()
                loss.mean().backward()
                self.optimizer.step()

            self.policy_old.load_state_dict(self.policy.state_dict())

            memory.clear_memory()

            logger.debug("PPO update succeeded")

        except Exception as e:
            logger.error(f"PPO update error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            memory.clear_memory()
