from __future__ import annotations
from typing import Any

import numpy as np

from CybORG.Agents.Wrappers import BlueEnterpriseWrapper
from ray.rllib.env.multi_agent_env import MultiAgentEnv


class EnterpriseMAE(BlueEnterpriseWrapper, MultiAgentEnv):
    """A wrapper designed to support CAGE Challenge 4 (RLlib Compatible).

    Creates a vector output for a neural network by directly pulling
    information out of the state object.

    [한국어]
    CAGE Challenge 4를 지원하기 위한 래퍼(Wrapper)다. RLlib과 호환된다.
    상태(state) 객체에서 직접 정보를 꺼내, 신경망에 넣을 수 있는 벡터
    형태의 출력을 만든다.
    """

    def step(
        self,
        action_dict: dict[str, Any] | None = None,
        messages: dict[str, Any] | None = None,
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        """Take a step in the enviroment using action indices.

        This wrapper supports both the CybORG and original EnterpriseMAE
        parameter conventions. For example:

            actions = { "blue_agent_0": 42 }
            messages = { "blue_agent_0": np.array([1, 0, 0, 0, 0, 0, 0, 0] }

            # CybORG Convention (preferred)
            env.step(action_dict=actions, messages=messages)

            # EnterpriseMAE Convention
            env.step({
                "actions": actions,
                "messages": messages,
            })

        Args:

            action_dict (dict[str, int]): The action index corresponding to each
                agent. These indices will be mapped to CybORG actions using the
                equivalent of `actions(agent)[index]`. The meaning of each action
                can be found using `action_labels(agent)[index]`.

            messages (dict[str, Any]): Optional messages to be passed to each agent.

            **kwargs (dict[str, Any]): Extra keywords are forwarded.

        Returns:
            observation (dict[str, np.ndarray]): Observations for each agent as vectors.

            rewards (dict[str, float]): Rewards for each agent.

            terminated (dict[str, bool]): Flags whether the agent finished normally.

            truncated (dict[str, bool]): Flags whether the agent was stopped by env.

            info (dict[str, dict]): Forwarded from BlueFixedActionWrapper.

        [한국어]
        행동 인덱스(action index)를 사용해 환경에서 한 스텝(step)을 진행한다.

        이 래퍼는 CybORG 방식과 기존 EnterpriseMAE 방식의 두 가지 인자
        전달 규약을 모두 지원한다. 위 영어 예시에서:
          - CybORG 규약(권장): step(action_dict=..., messages=...) 처럼
            인자를 따로 넘긴다.
          - EnterpriseMAE 규약: actions/messages를 하나의 dict로 묶어 넘긴다.

        인자(Args):
          - action_dict: 에이전트별 행동 인덱스. 이 인덱스는
            `actions(agent)[index]`에 해당하는 CybORG 행동(Action)으로
            매핑된다. 각 행동의 의미는 `action_labels(agent)[index]`로
            확인할 수 있다.
          - messages: 각 에이전트에 전달할 선택적 메시지.
          - **kwargs: 추가 키워드 인자는 그대로 전달된다.

        반환값(Returns):
          - observation: 에이전트별 관찰값(Observation)을 벡터로 표현한 것.
          - rewards: 에이전트별 보상(Reward).
          - terminated: 에이전트가 정상적으로 종료됐는지 여부.
          - truncated: 환경에 의해 중단됐는지 여부.
          - info: BlueFixedActionWrapper에서 그대로 전달된 부가 정보.
        """
        obs, rew, terminated, truncated, info = super(BlueEnterpriseWrapper, self).step(
            actions=action_dict, messages=messages
        )
        # [설명] RLlib 멀티에이전트 규약상 "__all__" 키는 전체 에피소드의
        # 종료/중단 여부를 나타낸다. 정상 종료(terminated)는 항상 False로 두고,
        # 에피소드 중단(truncated)은 환경 컨트롤러의 determine_done() 판정에 맡긴다.
        terminated["__all__"] = False
        truncated["__all__"] = self.env.environment_controller.determine_done()
        return obs, rew, terminated, truncated, info
