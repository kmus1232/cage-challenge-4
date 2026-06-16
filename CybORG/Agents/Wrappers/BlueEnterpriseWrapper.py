from __future__ import annotations
from typing import Any

import numpy as np

from CybORG import CybORG
from CybORG.Agents.Wrappers.BlueFixedActionWrapper import (
    MESSAGE_LENGTH,
    EMPTY_MESSAGE,
    NUM_MESSAGES,
)

from gymnasium.spaces import Space

from CybORG.Agents.Wrappers import BlueFlatWrapper, BlueFixedActionWrapper


class BlueEnterpriseWrapper(BlueFlatWrapper):
    """A wrapper designed to support CAGE Challenge 4.

    Creates a vector output for a neural network by directly pulling
    information out of the state object.

    [한국어]
    CAGE Challenge 4를 지원하기 위한 래퍼(Wrapper).
    상태 객체에서 정보를 직접 뽑아내, 신경망에 넣을 수 있는 벡터 형태의
    관찰값(Observation)으로 변환한다. BlueFlatWrapper를 상속한다.
    """

    def step(
        self,
        actions: dict[str, Any] | None = None,
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

        이 래퍼는 CybORG 방식과 기존 EnterpriseMAE 방식의 두 가지 인자 규약을
        모두 지원한다. (위 예시 참고)

        인자(Args):
            action_dict (dict[str, int]): 각 에이전트에 대응하는 행동 인덱스.
                이 인덱스는 `actions(agent)[index]`에 해당하는 방식으로 CybORG
                행동(Action)에 매핑된다. 각 행동의 의미는
                `action_labels(agent)[index]`로 확인할 수 있다.
            messages (dict[str, Any]): 각 에이전트에 전달할 선택적 메시지.
            **kwargs (dict[str, Any]): 추가 키워드 인자는 그대로 전달된다.

        반환값(Returns):
            observation (dict[str, np.ndarray]): 각 에이전트의 관찰값을 벡터로.
            rewards (dict[str, float]): 각 에이전트의 보상.
            terminated (dict[str, bool]): 에이전트가 정상적으로 종료됐는지 여부.
            truncated (dict[str, bool]): 에이전트가 환경에 의해 중단됐는지 여부.
            info (dict[str, dict]): BlueFixedActionWrapper에서 그대로 전달됨.
        """
        action_dict = actions if actions is not None else {}

        # Use EnterpriseMAE parameter handling
        # EnterpriseMAE 방식 인자 처리
        # [설명] action_dict 안에 "actions" 키가 있으면 EnterpriseMAE 규약으로 본다.
        # 즉 {"actions": ..., "messages": ...} 형태의 묶음 dict이 넘어온 경우다.
        if "actions" in action_dict:
            # Messages keyword is ignored if action_dict specifies messages.
            # action_dict이 messages를 지정하면 messages 키워드 인자는 무시된다.
            messages = action_dict.get("messages", messages)
            return super().step(action_dict["actions"], messages=messages)

        # Use CybORG parameters
        # CybORG 방식 인자 처리 (권장)
        return super().step(action_dict, messages=messages)

    def reset(
        self, agent=None, seed=None, *args, **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Reset the environment and update the observation space.

        Args:
            seed (Optional[int]): Set the environment's seed.

        Returns:
            observation (dict[str, Any]): The observations corresponding to each
                agent, translated into a vector format.

            info (dict[str, dict]): Forwarded from self.env.

        [한국어]
        환경을 리셋(reset)하고 관찰 공간(observation space)을 갱신한다.

        인자(Args):
            seed (Optional[int]): 환경의 난수 시드(seed)를 설정한다.

        반환값(Returns):
            observation (dict[str, Any]): 각 에이전트에 대응하는 관찰값을 벡터
                형식으로 변환한 것.
            info (dict[str, dict]): self.env에서 그대로 전달됨.
        """
        return super().reset(agent=agent, seed=seed)

    @property
    def long_observation_space(self) -> Space:
        """Observation space used for blue_agent_4.
        This is the largest observation space for this environment.

        Deprecated in favour of self.observation_space(agent_name).

        [한국어]
        blue_agent_4가 사용하는 관찰 공간(observation space).
        이 환경에서 가장 큰 관찰 공간이다.

        self.observation_space(agent_name) 사용을 권장하며, 이 속성은
        지원 중단(deprecated) 예정이다.
        """
        return self._long_obs_space

    @property
    def short_observation_space(self) -> Space:
        """Observation space used for agents other than blue_agent_4.

        This is the standard observation space for this environment UNLESS the
        pad_spaces option is explicitly enabled for the wrapper. If pad_spaces
        is enabled, all agents use self.long_observation_spaces() instead.

        Deprecated in favour of self.observation_space(agent_name), which
        returns the appropriate observation for each agent.

        [한국어]
        blue_agent_4를 제외한 에이전트들이 사용하는 관찰 공간(observation space).

        래퍼의 pad_spaces 옵션이 명시적으로 켜져 있지 않은 한, 이것이 이 환경의
        표준 관찰 공간이다. pad_spaces가 켜져 있으면 모든 에이전트가 대신
        self.long_observation_spaces()를 사용한다.

        각 에이전트에 맞는 관찰 공간을 돌려주는 self.observation_space(agent_name)
        사용을 권장하며, 이 속성은 지원 중단(deprecated) 예정이다.
        """
        return self._short_obs_space
