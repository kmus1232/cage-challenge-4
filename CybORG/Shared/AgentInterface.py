# Copyright DST Group. Licensed under the MIT license.

import sys
from typing import List

from CybORG.Shared import Scenario
from CybORG.Shared.ActionSpace import ActionSpace
from CybORG.Simulator.Actions import Action, Sleep
from CybORG.Shared.Observation import Observation
from CybORG.Shared.Results import Results
from CybORG.Shared.RewardCalculator import RewardCalculator

# [설명] 관찰값(Observation)을 고정 크기 벡터로 인코딩할 때 쓰는 상한값들.
# 호스트·프로세스·연결 등 각 요소의 최대 개수를 정의해 행동/관찰 공간 크기를 제한한다.
MAX_HOSTS = 5            # 호스트 최대 개수
MAX_PROCESSES = 100    # 50  # 프로세스 최대 개수
MAX_CONNECTIONS = 10     # 연결 최대 개수
MAX_VULNERABILITIES = 1  # 취약점 최대 개수
MAX_INTERFACES = 4       # 인터페이스 최대 개수
MAX_FILES = 10           # 파일 최대 개수
# MAX_SESSIONS = 10    # 80
MAX_USERS = 10           # 사용자 최대 개수
MAX_GROUPS = 10          # 그룹 최대 개수
MAX_PATCHES = 10         # 패치 최대 개수


class AgentInterface:
    """The agent interfaces for the BaseAgent instances.

    Attributes
    ----------
    actions : List[Action]
        list of possible actions
    action_space : ActionSpace
        ActionSpace instance
    active : bool
        flag of active (currently performing actions) agent
    agent : BaseAgent
        agent object instance
    agent_name : str
        name of the agent
    allowed_subnets : List[str]
        list of allowed subnets
    file : dict
    group_name : dict
    hostname : dict
    interface_name : dict
    internal_only : bool
        flag for the agent being an internal only agent
    last_action = None
    messages : list
        list of messages
    path : dict
    password : dict
    password_hash : dict
    process_name : dict
    scenario : Scenario
        current scenario instance
    username = dict

    [한국어]
    BaseAgent 인스턴스를 감싸는 에이전트 인터페이스 클래스.
    CybORG 환경과 실제 에이전트 객체 사이의 중간 창구 역할을 하며,
    행동 공간(Action Space) 갱신·행동 선택·에피소드 종료 처리를 담당한다.

    주요 속성:
    - actions : 가능한 행동(Action) 목록
    - action_space : 행동 공간(ActionSpace) 인스턴스
    - active : 에이전트가 활성 상태(현재 행동을 수행 중)인지 나타내는 플래그
    - agent : 실제 에이전트 객체 인스턴스(BaseAgent)
    - agent_name : 에이전트 이름
    - allowed_subnets : 에이전트가 접근 가능한 서브넷 목록
    - internal_only : 내부 전용 에이전트 여부 플래그
    - messages : 메시지 목록
    - scenario : 현재 시나리오(Scenario) 인스턴스
    (hostname/username/group_name/process_name 등 dict 속성은 환경에서 관찰한
     식별자를 정규화·매핑하기 위한 저장소다.)
    """

    def __init__(self,
                 agent_obj,
                 agent_name,
                 actions,
                 allowed_subnets,
                 scenario,
                 active=True,
                 internal_only=False):
        """
        Parameters
        ----------
        agent_obj : BaseAgent
        agent_name : str
        actions : List[Action]
        allowed_subnets : List[str]
        scenario : Scenario
        active : bool
        internal_only : bool

        [한국어]
        에이전트 인터페이스를 초기화한다.
        - agent_obj : 감쌀 실제 에이전트 객체(BaseAgent)
        - agent_name : 에이전트 이름
        - actions : 에이전트가 수행 가능한 행동(Action) 목록
        - allowed_subnets : 에이전트가 접근 가능한 서브넷 목록
        - scenario : 현재 시나리오(Scenario)
        - active : 활성 상태 여부(False면 행동 대신 Sleep 수행)
        - internal_only : 내부 전용 에이전트 여부
        식별자 매핑용 dict들을 비우고, ActionSpace를 생성한 뒤
        에이전트에 초기 행동 공간과 빈 관찰값(Observation)을 설정한다.
        """
        self.hostname = {}
        self.username = {}
        self.group_name = {}
        self.process_name = {}
        self.interface_name = {}
        self.path = {}
        self.password = {}
        self.password_hash = {}
        self.file = {}
        self.actions = actions
        self.last_action = None
        self.allowed_subnets = allowed_subnets
        self.scenario = scenario
        self.active = active
        self.internal_only = internal_only

        self.agent_name = agent_name
        self.action_space = ActionSpace(self.actions, agent_name, allowed_subnets)
        self.agent = agent_obj
        self.agent.set_initial_values(
            action_space=self.action_space.get_action_space(),
            observation=Observation().data
        )
        self.messages = []

    def update(self, obs: dict, known: bool=True):
        """update the action space with the observation

        [한국어]
        관찰값(Observation)을 사용해 행동 공간(Action Space)을 갱신한다.
        obs가 Observation 객체면 내부 data로 변환해 처리한다.
        known은 해당 관찰 정보가 에이전트에게 알려진(확정된) 것인지 표시한다.
        """
        if isinstance(obs, Observation):
            obs = obs.data
        self.action_space.update(obs, known)

    def set_init_obs(self, init_obs, true_obs):
        """set and update the true and initial observations

        [한국어]
        에피소드 시작 시 두 종류의 관찰값을 설정·갱신한다.
        - true_obs : 환경의 실제 상태(known=False로 갱신)
        - init_obs : 에이전트가 시작 시 알게 되는 초기 관찰값(known=True로 갱신)
        """
        if isinstance(init_obs, Observation):
            init_obs = init_obs.data
        if isinstance(true_obs, Observation):
            true_obs = true_obs.data
        self.update(true_obs, False)
        self.update(init_obs, True)


    def get_action(self, observation: Observation, action_space: dict = None):
        """Gets an action from the agent to perform on the environment
        
        Parameters
        ----------
        observation : Observation
            agent observation space
        action_space : dict
            agent action space

        Returns
        -------
        last_action : Action
            last action performed

        [한국어]
        에이전트에게 환경에 수행할 행동(Action)을 요청해 받아온다.
        - observation : 에이전트의 관찰값(Observation)
        - action_space : 에이전트의 행동 공간(Action Space). None이면 현재 공간을 사용한다.
        에이전트가 비활성(active=False)이면 행동 대신 Sleep을 수행한다.
        선택된 행동은 last_action에 저장하고 반환한다.
        """
        if isinstance(observation, Observation):
            observation = observation.data
        if action_space is None:
            action_space = self.action_space.get_action_space()
        if not self.active:
            self.last_action = Sleep()
        else:
            self.last_action = self.agent.get_action(observation, action_space)
        return self.last_action

    def end_episode(self):
        """perform agent end of episode functionality and reset the interface

        [한국어]
        에피소드(Episode) 종료 처리를 수행하고 인터페이스를 초기화한다.
        에이전트의 종료 콜백을 호출한 뒤 reset으로 내부 상태를 비운다.
        """
        self.agent.end_episode()
        self.reset()

    def reset(self):
        """resets the interface with empty dictionaries

        [한국어]
        식별자 매핑용 dict들을 모두 비워 인터페이스를 초기 상태로 되돌린다.
        행동 공간(Action Space)도 reset하고 에이전트의 종료 콜백을 호출한다.
        """
        self.hostname = {}
        self.username = {}
        self.group_name = {}
        self.process_name = {}
        self.interface_name = {}
        self.path = {}
        self.password = {}
        self.password_hash = {}
        self.file = {}
        self.action_space.reset(self.agent_name)
        self.agent.end_episode()

    def create_reward_calculator(self, reward_calculator: str, agent_name: str, scenario: Scenario) -> RewardCalculator:
        """Creates a reward calculator based on the name of the calculator to be used.
        
        Parameters
        ----------
        reward_calculator : str
            name of reward calculator
        agent_name : str
            name of agent
        scenario : Scenario
            current scenario object

        Returns
        -------
        : RewardCalculator
            created reward calculator

        [한국어]
        주어진 이름에 맞는 보상 계산기(RewardCalculator)를 생성한다.
        단, CC4(CAGE Challenge 4)에서는 구현되어 있지 않아 호출 시 예외를 던진다.
        아래 주석은 이전 챌린지에서 쓰던 계산기 선택 로직의 흔적이다.
        """
        raise NotImplementedError("Not implemented for CC4")
        # calc = None
        # if reward_calculator == "Baseline":
        #     calc = BaselineRewardCalculator(agent_name)
        # elif reward_calculator == 'PwnRewardCalculator':
        #     calc = PwnRewardCalculator(agent_name, scenario)
        # elif reward_calculator == 'Disrupt':
        #     calc = DistruptRewardCalculator(agent_name, scenario)
        # elif reward_calculator == 'None' or reward_calculator is None:
        #     calc = EmptyRewardCalculator(agent_name)
        # elif reward_calculator == 'HybridAvailabilityConfidentiality':
        #     calc = HybridAvailabilityConfidentialityRewardCalculator(agent_name, scenario)
        # elif reward_calculator == 'HybridImpactPwn':
        #     calc = HybridImpactPwnRewardCalculator(agent_name, scenario)
        # else:
        #     raise ValueError(f"Invalid calculator selection: {reward_calculator} for agent {agent_name}")
        # return calc

    def get_observation_space(self):
        # returns the maximum observation space for the agent given its action set and the amount of parameters in the environment
        # [설명] 에이전트의 행동 집합과 환경 파라미터 개수로 정해지는 최대 관찰 공간을 반환한다(미구현).
        raise NotImplementedError

    def update_allowed_subnets(self, allowed_subnets):
        """ Updates allowed_subnets for agent

        Attributes
        ----------
        allowed_subnets : (List(str))
            agent's allowed_subnets for mission phase

        [한국어]
        에이전트의 접근 가능 서브넷 목록(allowed_subnets)을 갱신한다.
        - allowed_subnets : 미션 단계(mission phase)에서 에이전트가 접근 가능한 서브넷 목록
        인터페이스 속성과 행동 공간(Action Space)의 값을 함께 갱신한다.
        """
        self.allowed_subnets = allowed_subnets
        self.action_space.allowed_subnets = allowed_subnets