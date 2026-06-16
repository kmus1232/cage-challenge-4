from __future__ import annotations
from CybORG import CybORG
from CybORG.Agents import BaseAgent

from ray.rllib.env.multi_agent_env import MultiAgentEnv
from CybORG.Agents.Wrappers.EnterpriseMAE import EnterpriseMAE

# Import your custom agents here.
# 여기에 직접 만든 에이전트를 import 한다.
from dummy_agent import DummyAgent

class Submission:

    # Submission name
    # 제출물 이름
    NAME: str = "SUBMISSION NAME"

    # Name of your team
    # 팀 이름
    TEAM: str = "TEAM NAME"

    # What is the name of the technique used? (e.g. Masked PPO)
    # 사용한 기법의 이름 (예: Masked PPO)
    TECHNIQUE: str = "TECHNIQUE NAME"

    # Use this function to define your agents.
    # 이 부분에서 에이전트를 정의한다. (Blue 에이전트 5개를 DummyAgent로 지정)
    AGENTS: dict[str, BaseAgent] = {
        f"blue_agent_{agent}": DummyAgent() for agent in range(5)
    }

    # Use this function to wrap CybORG with your custom wrapper(s).
    # 이 함수에서 CybORG 환경을 직접 만든 래퍼(Wrapper)로 감싼다.
    def wrap(env: CybORG) -> MultiAgentEnv:
        return EnterpriseMAE(env)
