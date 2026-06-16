import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import inspect
import time
import os

import torch as T
import numpy as np

from rich import print

from CybORG import CybORG
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.Wrappers import BaseWrapper, BlueFlatWrapper, BlueFixedActionWrapper

import pettingzoo
from pettingzoo import ParallelEnv
from gymnasium.spaces import Space

from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker

from typing import TypeVar, cast

AgentID = TypeVar("AgentID", bound=str)
ObsType = TypeVar("ObsType", bound=T.Tensor)
ActionType = TypeVar("ActionType", bound=int)


class GenericPzShim(ParallelEnv):
    metadata = {
        "render_modes": [],
        "name": "CybORG v4",
        "is_parallelizable": True,
        "has_manual_policy": False,
    }

    def __init__(self, env: BlueFlatWrapper, **kwargs):
        super().__init__()
        self.env = env

    def reset(self, seed: int | None = None, *args, **kwargs):
        return self.env.reset(seed=seed)

    def step(self, *args, **kwargs):
        return self.env.step(*args, **kwargs)

    @property
    def agents(self):
        return self.env.agents

    @property
    def possible_agents(self):
        return self.env.possible_agents

    @property
    def action_spaces(self) -> dict[AgentID, Space]:
        return self.env.action_spaces()

    def action_space(self, agent_name) -> Space:
        return self.env.action_space(agent_name)

    @property
    def observation_spaces(self) -> dict[AgentID, Space]:
        return self.env.observation_spaces()

    def observation_space(self, agent_name) -> Space:
        return self.env.observation_space(agent_name)

    @property
    def action_masks(self) -> dict[AgentID, T.tensor]:
        return {
            a: T.tensor(self.env.action_masks[a], dtype=T.bool) for a in self.env.agents
        }


# Shamelessly stolen from https://pettingzoo.farama.org/tutorials/sb3/connect_four/
# 출처: PettingZoo의 connect_four SB3 튜토리얼 코드를 그대로 가져왔다.
class SB3ActionMaskWrapper(pettingzoo.utils.BaseWrapper):
    """Wrapper to allow PettingZoo environments to be used with SB3 illegal action masking.

    [한국어]
    PettingZoo 환경을 SB3의 비합법 행동 마스킹(illegal action masking)과 함께 쓸 수
    있게 해주는 래퍼(Wrapper)다.
    """

    def reset(self, seed=None, options=None):
        """Gymnasium-like reset function which assigns obs/action spaces to be the same for each agent.

        This is required as SB3 is designed for single-agent RL and doesn't expect obs/action spaces to be functions

        [한국어]
        Gymnasium 스타일의 reset 함수로, 모든 에이전트에 동일한 관찰값/행동 공간을
        할당한다. SB3는 단일 에이전트 강화학습(RL)용으로 설계되어 관찰값/행동
        공간이 함수 형태인 것을 가정하지 않으므로 이 처리가 필요하다.
        """
        super().reset(seed, options)

        # Strip the action mask out from the observation space
        # 관찰값 공간에서 행동 마스크(action mask)를 떼어낸다.
        self.observation_space = super().observation_space(self.agent_selection)
        self.action_space = super().action_space(self.agent_selection)

        # Return initial observation, info (PettingZoo AEC envs do not by default)
        # 초기 관찰값과 info를 반환한다. (PettingZoo AEC 환경은 기본적으로 반환하지 않음)
        return self.observe(self.agent_selection), {}

    def step(self, action):
        """Gymnasium-like step function, returning observation, reward, termination, truncation, info.

        [한국어]
        Gymnasium 스타일의 step 함수로, 관찰값·보상·종료(termination)·중단
        (truncation)·info를 반환한다.
        """
        super().step(action)
        return super().last()

    def action_mask(self):
        """Separate function used in order to access the action mask.

        [한국어]
        행동 마스크(action mask)에 접근하기 위한 별도 함수다.
        """
        return self.infos[self.agent_selection]["action_mask"]


def mask_fn(env):
    return env.action_mask()


# Shamelessly stolen from https://pettingzoo.farama.org/tutorials/sb3/connect_four/
# 출처: PettingZoo의 connect_four SB3 튜토리얼 코드를 그대로 가져왔다.
def train_action_mask(env_fn, steps=250000, seed=0, **env_kwargs):
    """Train a single model to play as each agent in a zero-sum game environment using invalid action masking.

    [한국어]
    비합법 행동 마스킹(invalid action masking)을 사용해, 제로섬 게임 환경에서 각
    에이전트 역할을 모두 수행하는 단일 모델을 학습시킨다.
    """
    env = env_fn.env(**env_kwargs)

    print(f"Starting training on {str(env.metadata['name'])}.")

    # Custom wrapper to convert PettingZoo envs to work with SB3 action masking
    # PettingZoo 환경을 SB3 행동 마스킹과 호환되게 변환하는 커스텀 래퍼(Wrapper)다.
    env = SB3ActionMaskWrapper(env)

    env.reset(seed=seed)  # Must call reset() in order to re-define the spaces
    # 공간을 재정의하려면 reset()을 반드시 호출해야 한다.

    env = ActionMasker(env, mask_fn)  # Wrap to enable masking (SB3 function)
    # 마스킹을 활성화하기 위해 래핑한다. (SB3 함수)
    # MaskablePPO behaves the same as SB3's PPO unless the env is wrapped
    # with ActionMasker. If the wrapper is detected, the masks are automatically
    # retrieved and used when learning. Note that MaskablePPO does not accept
    # a new action_mask_fn kwarg, as it did in an earlier draft.
    # [한국어] 환경이 ActionMasker로 래핑되지 않으면 MaskablePPO는 SB3의 PPO와
    # 동일하게 동작한다. 래퍼가 감지되면 학습 시 마스크를 자동으로 가져와
    # 사용한다. 초기 초안과 달리 MaskablePPO는 action_mask_fn 인자를 받지 않는다.
    logdir = "logs/TrainingSB3_" + time.strftime("%Y%m%d_%H%M%S")
    model = MaskablePPO(
        MaskableActorCriticPolicy, env, verbose=1, tensorboard_log=logdir
    )
    model.set_random_seed(seed)
    model.learn(total_timesteps=steps)

    model.save(f"{env.unwrapped.metadata.get('name')}_{time.strftime('%Y%m%d-%H%M%S')}")
    print("Model has been saved.")
    print(f"Finished training on {str(env.unwrapped.metadata['name'])}.\n")
    env.close()


def load_env(**kwargs):
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        #red_agent_class=SleepAgent, 
        red_agent_class=FiniteStateRedAgent,
        steps=500,
    )
    cyborg = CybORG(scenario_generator=sg)
    cyborg = BlueFlatWrapper(cyborg, **kwargs)
    cyborg = GenericPzShim(cyborg)
    return cyborg


def run_test():
    print("[TEST] Running initial environment.")
    env = load_env()
    print("[TEST] Running petting zoo API test...")
    from pettingzoo.test import parallel_api_test, api_test

    parallel_api_test(env)
    print("[TEST] Environment ok.")


class Wrapped:
    def env(**kwargs):
        env = load_env(**kwargs)
        from pettingzoo.utils import parallel_to_aec as wrapper

        return wrapper(env)


if __name__ == "__main__":
    run_test()
    train_action_mask(Wrapped, pad_spaces=True)
