from typing import Union, Any

from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared import Results


class BaseWrapper:
    """Base class for all CybORG wrappers.

    A wrapper sits between an external agent and the CybORG environment,
    transforming observations and action spaces without changing the
    underlying simulation. Subclasses override observation_change and
    action_space_change to adapt the interface for a particular agent.

    [한국어]
    모든 CybORG 래퍼(Wrapper)의 기반 클래스.
    래퍼는 외부 에이전트와 CybORG 환경 사이에 끼어들어, 시뮬레이션 자체는
    바꾸지 않으면서 관찰값(Observation)과 행동 공간(Action Space)을 변환한다.
    하위 클래스는 observation_change와 action_space_change를 재정의해 특정
    에이전트에 맞게 인터페이스를 가공한다.
    """
    def __init__(self, env: CybORG = None):
        # wrapper allows changes to be made to the interface between external agents via specification of the env
        # [설명] 래퍼는 env를 지정해 외부 에이전트와 환경 사이 인터페이스를 가공할 수 있게 한다.
        self.env = env
        self.agents = env.agents if env is not None else []

    def step(self, agent=None, action=None, messages: dict=None) -> Results:
        """Advance the environment one step, then transform the result.

        [한국어]
        환경을 한 스텝(step) 진행시킨 뒤, 반환된 결과의 관찰값과 행동 공간을
        래퍼가 변환해 돌려준다.
        """
        result = self.env.step(agent, action)
        # [설명] 원본 환경의 결과를 받아, 래퍼 규칙에 따라 관찰값/행동 공간을 가공한다.
        result.observation = self.observation_change(agent, result.observation)
        result.action_space = self.action_space_change(result.action_space)
        return result

    def reset(self, agent=None, seed = None):
        """Reset the environment, then transform the initial result.

        [한국어]
        환경을 초기화(reset)하고, 초기 결과의 행동 공간과 관찰값을 래퍼가
        변환해 돌려준다.
        """
        result = self.env.reset(agent, seed)
        result.action_space = self.action_space_change(result.action_space)
        result.observation = self.observation_change(agent, result.observation)
        return result

    def observation_change(self, agent: str, observation: dict):
        # [설명] 기본 구현은 관찰값을 그대로 반환한다. 하위 클래스가 재정의해 가공한다.
        return observation

    def action_space_change(self, action_space: dict) -> dict:
        # [설명] 기본 구현은 행동 공간을 그대로 반환한다. 하위 클래스가 재정의해 가공한다.
        return action_space

    def get_action_space(self, agent: str) -> dict:
        # 에이전트의 행동 공간을 환경에서 가져와 래퍼 규칙으로 변환해 반환한다.
        return self.action_space_change(self.env.get_action_space(agent))

    def get_observation(self, agent: str):
        # 에이전트의 관찰값을 환경에서 가져와 래퍼 규칙으로 변환해 반환한다.
        return self.observation_change(agent, self.env.get_observation(agent))

    def get_last_action(self, agent: str):
        # 해당 에이전트가 마지막으로 수행한 행동(Action)을 반환한다.
        return self.env.get_last_action(agent=agent)

    def set_seed(self, seed: int):
        # 환경의 난수 시드(seed)를 설정해 재현 가능한 실행을 만든다.
        self.env.set_seed(seed)

    @property
    def active_agents(self) -> list:
        # 현재 활성화된 에이전트 목록을 반환한다.
        return self.env.active_agents

    def get_message_space(self, agent: str):
        # 에이전트 간 통신에 쓰이는 메시지 공간(message space)을 반환한다.
        return self.env.get_message_space(agent)

    def get_attr(self, attribute: str) -> Any:
        """gets a specified attribute from this wrapper if present of requests it from the wrapped environment

                Parameters
                ----------
                attribute : str
                    name of the requested attribute

                Returns
                -------
                Any
                    the requested attribute

                [한국어]
                지정한 속성(attribute)을 가져온다. 래퍼 자신이 그 속성을 가지고
                있으면 자신의 것을 반환하고, 없으면 감싸고 있는 환경에 요청한다.

                Parameters(매개변수)
                - attribute : str — 요청할 속성 이름
                Returns(반환값)
                - Any — 요청한 속성
                """
        # [설명] 먼저 래퍼 자신에게 속성이 있는지 확인하고, 없으면 원본 환경으로 위임한다.
        if hasattr(self, attribute):
            return self.__getattribute__(attribute)
        else:
            return self.env.get_attr(attribute)

    def render(self, mode):
        # 환경을 지정한 모드(mode)로 렌더링한다.
        return self.env.render(mode)

    @property
    def unwrapped(self):
        # [설명] 래퍼를 모두 벗겨낸 원본 환경(CybORG)을 반환한다.
        return self.env.unwrapped
