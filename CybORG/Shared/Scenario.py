# Copyright DST Group. Licensed under the MIT license.
import itertools
import pprint
import sys
from typing import List, Dict, Tuple

from CybORG.Agents import BaseAgent, SleepAgent
from CybORG.Shared import CybORGLogger
from CybORG.Shared.Session import Session
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Subnet import Subnet

class ScenarioAgent(CybORGLogger):
    """A dataclass for handling scenario information of an agent

    Is essentially a wrapper around the definition for a single agent
    in the scenario dictionary, and provides a consistent interface to
    agent data without having to remember string keys, etc.

    [한국어]
    시나리오에 정의된 단일 에이전트 정보를 담는 데이터클래스.
    시나리오 딕셔너리에 들어 있는 한 에이전트 정의를 감싸는 래퍼(Wrapper)로,
    문자열 키를 일일이 기억하지 않고도 에이전트 데이터에 일관된 방식으로 접근하게 해 준다.
    """

    def __init__(self,
                 agent_name: str,
                 team: str,
                 starting_sessions: List[Session],
                 actions: list,
                 osint: dict,
                 allowed_subnets: list,
                 agent_type: BaseAgent = None,
                 active: bool = True,
                 default_actions: tuple = None,
                 internal_only: bool = False):
        """
        Parameters
        ----------
        agent_name: str
            Name of the agent
        team : str
            the name of the team the agent is a part of
        starting_sessions: list
            the list of sessions the agent starts with
        actions: list
            the list of actions an agent may perform
        osint: dict
            the information the agent begins a game with
        agent_type: BaseAgent
            the class that selects the default actions of the agent
        active: bool
            determines if the agent starts active or inactive at the start of the game
        default_actions : tuple
            the action_class, action_kwargs for actions being performed at the end of a turn by this agent
        internal_only : bool
            marks if an agent is restricted from using the external cyborg interfaces,
            useful if you want to enforce a default behaviour for that agent

        [한국어]
        매개변수
        ----------
        agent_name: str
            에이전트 이름
        team : str
            에이전트가 속한 팀 이름
        starting_sessions: list
            에이전트가 시작 시 보유하는 세션 목록
        actions: list
            에이전트가 수행할 수 있는 행동(Action) 목록
        osint: dict
            게임 시작 시 에이전트가 미리 알고 있는 정보(사전 첩보)
        agent_type: BaseAgent
            에이전트의 기본 행동을 선택하는 클래스
        active: bool
            게임 시작 시 에이전트가 활성/비활성 상태로 시작할지 결정
        default_actions : tuple
            이 에이전트가 매 턴 끝에 수행하는 행동의 (action_class, action_kwargs) 쌍
        internal_only : bool
            에이전트가 외부 cyborg 인터페이스를 사용하지 못하도록 제한할지 표시.
            특정 에이전트에게 기본 동작을 강제하고 싶을 때 유용하다.
        """
        self.name = agent_name
        self.team = team
        self.starting_sessions: List[Session] = []
        for session in starting_sessions:
            self.starting_sessions.append(session)
        self.actions = actions
        if agent_type is not None:
            self.agent_type = agent_type
        else:
            # agent_type이 지정되지 않으면 아무 행동도 하지 않는 SleepAgent를 기본값으로 사용한다.
            self.agent_type = SleepAgent()
        self.osint = osint
        self.allowed_subnets = allowed_subnets
        self.active = active
        self.default_actions = default_actions
        self.internal_only = internal_only

    @staticmethod
    def get_action_classes(actions):
        """Getter method for action classes contained in `CybORG.Simulator.Actions`

        [한국어]
        `CybORG.Simulator.Actions` 모듈에 정의된 행동(Action) 클래스들을 가져오는 게터.
        문자열로 된 행동 이름 목록을 받아 실제 클래스 객체 목록으로 변환한다.
        """
        action_classes = []
        # 이미 import된 Actions 모듈을 sys.modules에서 직접 참조한다.
        action_module = sys.modules['CybORG.Simulator.Actions']
        for action in actions:
            # [설명] getattr로 모듈에서 행동 이름(문자열)에 해당하는 클래스를 조회해 모은다.
            action_classes.append(getattr(action_module, action))
        return action_classes

    @classmethod
    def load(cls, agent_name: str, agent_info: dict):
        """Class load method

        [한국어]
        시나리오 딕셔너리의 에이전트 정의(agent_info)로부터 ScenarioAgent 인스턴스를 생성하는 클래스 메서드.
        """
        return cls(
            agent_name=agent_name,
            team=agent_info.get('team'),
            actions=cls.get_action_classes(agent_info.get("actions", [])),
            starting_sessions=[Session.load(i) for i in agent_info.get("starting_sessions", [])],
            agent_type=getattr(sys.modules['CybORG.Agents'], agent_info.get("agent_type", SleepAgent))(),
            allowed_subnets=agent_info.get("AllowedSubnets", []),
            osint=agent_info.get("INT", {})
        )

class Scenario(CybORGLogger):
    """A dataclass that contains the initial state information.

    Contains getter and setter functions that are used to inform the creation of environmental objects.

    [한국어]
    시나리오(Scenario)의 초기 상태 정보를 담는 데이터클래스.
    환경(environment) 객체를 생성할 때 참조되는 게터/세터 함수들을 제공한다.

    Attributes
    ----------
    agents : Dict[str, ScenarioAgent]
    allowed_subnets_per_mphase : dict
    hosts : Dict[str, Host]
    max_bandwidth : int
    mission_phases : Tuple[int, int, int]
    operational_firewall : bool
    predeployed : bool
    scenario_gen_type : unknown
    starting_sessions : list
    subnets : Dict[str, Subnet]
    team_agents: dict
    team_calc : dict

    """

    def __init__(
        self,
        agents: Dict[str, ScenarioAgent] = None,
        team_calcs: dict = None,
        team_agents: dict = None,
        hosts: Dict[str, Host] = None,
        subnets: Dict[str, Subnet] = None,
        mission_phases: Tuple[int, int, int] = None,
        allowed_subnets_per_mphase: dict = None,
        predeployed: bool = False,
        max_bandwidth: int = 1000
    ):
        """ 
        Parameters
        ----------
        agents : Dict[str, ScenarioAgent]
        allowed_subnets_per_mphase : dict
        hosts : Dict[str, Host]
        max_bandwidth : int
            maximum bandwidth of agent communications
        mission_phases : Tuple[int, int, int]
        predeployed : bool
            by default False
        subnets : Dict[str, Subnet]
        team_agents: dict
        team_calcs : dict

        [한국어]
        매개변수
        ----------
        agents : Dict[str, ScenarioAgent]
        allowed_subnets_per_mphase : dict
        hosts : Dict[str, Host]
        max_bandwidth : int
            에이전트 간 통신의 최대 대역폭
        mission_phases : Tuple[int, int, int]
        predeployed : bool
            기본값 False
        subnets : Dict[str, Subnet]
        team_agents: dict
        team_calcs : dict
        """
        self.agents = agents if agents is not None else {}
        # 각 에이전트의 시작 세션 목록을 모은다.
        agent_starting_sessions = [agent.starting_sessions for agent in self.agents.values()]
        # [설명] 여러 에이전트의 세션 리스트들을 하나로 이어 붙여 전체 시작 세션 목록을 만든다.
        self.starting_sessions = list(itertools.chain(agent_starting_sessions))

        self.team_calc = self._get_team_calc(team_calcs)

        self.team_agents = team_agents if team_agents is not None else {}
        self.hosts = hosts if hosts is not None else {}
        self.subnets = subnets if subnets is not None else {}
        self.predeployed = predeployed
        self.max_bandwidth = max_bandwidth
        self.operational_firewall = False

        self.mission_phases = mission_phases
        self.allowed_subnets_per_mphase = allowed_subnets_per_mphase

        self.scenario_gen_type = None

    @classmethod
    def load(cls, scenario_dict: dict, np_random):
        """Class load method

        [한국어]
        시나리오 딕셔너리(scenario_dict)로부터 Scenario 인스턴스를 생성하는 클래스 메서드.
        에이전트·호스트·서브넷을 각각 로드한 뒤 하나의 Scenario 객체로 묶는다.
        """
        agents = {}
        for name, info in scenario_dict['Agents'].items():
            agents[name] = ScenarioAgent.load(name, info)
        hosts = {}
        for hostname, host_info in scenario_dict['Hosts'].items():
            hosts[hostname] = Host.load(hostname=hostname, host_info=host_info, np_random=np_random)
        subnets = {}
        for subnet_name, subnet_info in scenario_dict['Subnets'].items():
            subnets[subnet_name] = Subnet.load(name=subnet_name, subnet_info=subnet_info)
        return cls(agents=agents,
                   team_calcs=scenario_dict['team_calcs'],
                   team_agents=scenario_dict['team_agents'],
                   hosts=hosts,
                   subnets=subnets,
                   predeployed=scenario_dict.get("predeployed", False))

    def _get_team_calc(self, team_calcs: dict):
        # [설명] 팀별 보상 계산기(reward calculator) 설정을 실제 계산기 객체로 변환한다.
        # team_calcs는 {에이전트명: [(계산기명, 상대팀), ...]} 형태이며,
        # 각 항목을 _get_reward_calculator로 변환해 중첩 딕셔너리로 재구성한다.
        new_team_calcs = {}
        if team_calcs:
            for agent_name, calc_names in team_calcs.items():
                new_team_calcs[agent_name] = {}
                for name, adversary in calc_names:
                    calc = self._get_reward_calculator(agent_name, name, adversary)
                    new_team_calcs[agent_name][name] = calc
        return new_team_calcs

    def get_scenario_gen_type(self):
        return self.scenario_gen_type

    def set_scenario_gen_type(self, scenario_gen_type):
        self.scenario_gen_type = scenario_gen_type

    def _get_reward_calculator(self, team_name, reward_calculator, adversary):
        # [설명] CC4에서는 보상 계산기 선택 로직이 구현되어 있지 않다(아래 주석은 이전 버전의 분기 코드).
        raise NotImplementedError("Not implemented for CC4")
    #     if reward_calculator == "Baseline":
    #         calc = BaselineRewardCalculator(team_name)
    #     elif reward_calculator == 'Pwn':
    #         calc = PwnRewardCalculator(team_name, self)
    #     elif reward_calculator == 'Disrupt':
    #         calc = DistruptRewardCalculator(team_name, self)
    #     elif reward_calculator == 'None' or reward_calculator is None:
    #         calc = EmptyRewardCalculator(team_name)
    #     elif reward_calculator == 'HybridAvailabilityConfidentiality':
    #         calc = HybridAvailabilityConfidentialityRewardCalculator(team_name, self, adversary)
    #     elif reward_calculator == 'HybridImpactPwn':
    #         calc = HybridImpactPwnRewardCalculator(team_name, self)
    #     else:
    #         raise ValueError(f"Invalid calculator selection: {reward_calculator} for team {team_name}")

    #     return calc

    def get_subnet_size(self, subnetname: str) -> int:
        """gets size of subnet

        [한국어]
        서브넷의 크기(size)를 반환한다.
        """
        return self.subnets[subnetname].size

    def get_subnet_hosts(self, subnetname: str) -> List[str]:
        """gets list of hosts in subnet

        [한국어]
        서브넷에 속한 호스트 목록을 반환한다.
        """
        return self.subnets[subnetname].hosts

    def get_subnet_nacls(self, subnetname: str) -> dict:
        """gets dictionary of subnet info

        [한국어]
        서브넷의 NACL(네트워크 접근 제어 목록) 딕셔너리를 반환한다.
        """
        subnet_info = self.subnets[subnetname]
        return subnet_info.nacls

    def get_host_image_name(self, hostname: str) -> str:
        # 호스트 이름으로 해당 호스트의 이미지 이름을 반환한다.
        return self.hosts[hostname]["image"]

    def get_host(self, hostname: str) -> Host:
        """gets host object from hostname

        [한국어]
        호스트 이름으로 Host 객체를 반환한다.
        """
        return self.hosts[hostname]

    def get_team_info(self, team_name: str) -> dict:
        """gets dictionary of team info for team, including calculators and agents

        [한국어]
        해당 팀의 정보 딕셔너리를 반환한다(보상 계산기 calcs와 소속 에이전트 agents 포함).
        """
        return {'calcs': self.team_calc[team_name], 'agents': self.team_agents[team_name]}

    def get_host_subnet_names(self, hostname: str) -> List[str]:
        """gets list of hosts in same subnet as hostname

        [한국어]
        주어진 호스트와 같은 서브넷에 속한 서브넷 이름 목록을 반환한다.
        """
        return [s for s in self.subnets if hostname in self.get_subnet_hosts(s)]

    def get_agent_info(self, agent_name: str) -> ScenarioAgent:
        """gets ScenarioAgent object by agent name

        [한국어]
        에이전트 이름으로 ScenarioAgent 객체를 반환한다.
        """
        return self.agents[agent_name]

    def get_reward_calculators(self) -> dict:
        """gets dictionary of teams and their reward calculators

        [한국어]
        팀별 보상 계산기(reward calculator) 딕셔너리를 반환한다.
        """
        return {team_name: reward_calculators for team_name, reward_calculators \
                in self.team_calc.items()}

    def get_teams(self) -> list:
        """gets a list of the team names

        [한국어]
        팀 이름 목록을 반환한다.
        """
        return list(self.team_calc.keys())

    def get_end_turn_actions(self) -> dict:
        """Returns the end turn action that is performed by an agent

        [한국어]
        각 에이전트가 턴 종료 시 수행하는 행동(end turn action)들을 반환한다.
        """
        end_turn_actions = {}
        for agent_name, data in self.agents.items():
            if data.default_actions is not None:
                end_turn_actions[agent_name] = data.default_actions
        return end_turn_actions

    def get_team_assignments(self) -> dict:
        """Returns team agents dictionary

        [한국어]
        팀별 소속 에이전트(team agents) 딕셔너리를 반환한다.
        """
        return self.team_agents

    def __str__(self):
        # [버그 수정] 기존 코드는 정의되지 않은 self._scenario를 참조해
        #            str(scenario) 호출 시 AttributeError가 발생했다.
        #            실제 인스턴스 속성(agents/hosts/subnets 등) 전체를 보기 좋게
        #            출력하도록 변경한다. Observation.__str__과 동일한 형식.
        scenario_str = pprint.pformat(vars(self), depth=7)
        return f"{self.__class__.__name__}:\n{scenario_str}"