from gymnasium.envs.registration import register
from .cr3bp_env import CR3BPEnv

register(
    id='CR3BP-v0',
    entry_point='cr3bp_env:CR3BPEnv',
    max_episode_steps=1000,
)
