# Copyright DST Group. Licensed under the MIT license.

from CybORG.Simulator.Actions.Action import Action
from CybORG.Shared.Logger import CybORGLogger


class RewardCalculator(CybORGLogger):
    """Base class for all reward calculators

    Attributes
    ----------
    agent_name : str
    init_state
    init_obs
    previous_state
    previous_obs
    flat : bool
        by default False
    time : int
        by default 0

    [한국어]
    모든 보상(Reward) 계산기의 베이스 클래스다. 각 에이전트별로
    스텝(step)마다 받는 보상을 어떻게 산출할지는 하위 클래스가 구현한다.

    주요 속성:
    - agent_name : 보상을 계산할 대상 에이전트 이름
    - init_state / init_obs : 에피소드 시작 시점의 상태/관찰값(Observation)
    - previous_state / previous_obs : 직전 스텝의 상태/관찰값(Observation)
    - flat : 관찰값을 평탄화(flatten)할지 여부, 기본값 False
    - time : 경과 스텝 수, 기본값 0
    """
    def __init__(self, agent_name: str):
        """
        Parameters
        ----------
        agent_name : str
            agent's name

        [한국어]
        Parameters
        ----------
        agent_name : str
            보상을 계산할 대상 에이전트 이름
        """
        self.agent_name = agent_name
        self.init_state = None
        self.init_obs = None
        self.previous_state = None
        self.previous_obs = None
        self.flat = False

        # Should this actually be a time.datetime?
        # 원문 주석: 이 값이 사실은 time.datetime 타입이어야 하는지에 대한 의문(원작자 메모).
        # 현재는 스텝 카운터(정수)로만 사용한다.
        self.time = 0

    def calculate_simulation_reward(self, env_controller):
        """Calculates the reward from the environment controller

        [한국어]
        환경 컨트롤러(env_controller)로부터 현재 상태·행동(Action)·관찰값(Observation)·
        종료 여부를 꺼내, 실제 보상 계산은 calculate_reward에 위임한다.
        """
        # [설명] 환경의 참(True) 상태를 가져와 필터링한 뒤 .data로 상태 딕셔너리를 추출한다.
        current_state = env_controller._filter_obs(env_controller.get_true_state(env_controller.INFO_DICT['True'])).data
        action = env_controller.action
        agent_observations = env_controller.observation
        done = env_controller.done
        return self.calculate_reward(current_state, action, agent_observations, done, env_controller.state)

    def calculate_reward(self, current_state: dict, action: dict, agent_observations: dict, done: bool, state: object) -> float:
        # [설명] 실제 보상 산출 로직. 베이스 클래스에서는 미구현이며 하위 클래스가 반드시 재정의한다.
        raise NotImplementedError

    def tick(self):
        # 스텝(step)이 한 번 진행될 때마다 경과 시간 카운터를 1 증가시킨다.
        self.time += 1

    def reset(self):
        # 에피소드 리셋: 직전 상태/관찰값을 초기 상태/관찰값으로 되돌리고 시간 카운터를 0으로 초기화한다.
        self.previous_state = self.init_state
        self.previous_obs = self.init_obs
        self.time = 0


class EmptyRewardCalculator(RewardCalculator):
    # [설명] 항상 0을 반환하는 빈(no-op) 보상 계산기. 보상이 필요 없는 에이전트에 쓴다.
    def calculate_reward(self, current_state: dict, action: Action, agent_observations: dict, done: bool, state: object):
        return 0.
