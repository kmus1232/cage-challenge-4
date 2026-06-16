# Copyright DST Group. Licensed under the MIT license.
import gym
from gym.utils.seeding import RandomNumberGenerator

from typing import Dict, List, Tuple
from CybORG.Shared import Scenario
from CybORG.Shared import Enums
from CybORG.Shared.AgentInterface import AgentInterface
from CybORG.Shared.Enums import DecoyType, TernaryEnum
from CybORG.Shared.Logger import CybORGLogger
from CybORG.Shared.ObservationSet import ObservationSet
from CybORG.Shared.Results import Results
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Simulator.Actions import BlockTraffic, DiscoverNetworkServices, DiscoverRemoteSystems, ExploitRemoteService, PrivilegeEscalate, Analyse, Remove, Restore, RemoveOtherSessions, Impact
from CybORG.Simulator.Actions.Action import Action, RemoteAction, Sleep, InvalidAction
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import AllowTraffic
from CybORG.Shared.Observation import Observation
from CybORG.Shared.RewardCalculator import RewardCalculator
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator
from CybORG.Simulator.State import State
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator 



class SimulationController(CybORGLogger):
    """The class that controls the Simulation environment.

    Attributes
    ----------
    action : Dict[str, List[Action]]
        dictionary of agent actions for the step
    actions_in_progress : Dict[str, Dict]
        actions in progress during the step
    actions_queues : Dict[str, list]
        queue of actions to be taken during the step
    agents : dict
        unused in CC4, default None
    agent_interfaces : Dict[str, AgentInterface]
        dictionary of agents and their interfaces
    bandwidth_usage : Dict[str, int]
        dictionary of hostnames and their bandwidth usage
    blocked_actions : list
        list of blocked actions
    done: bool
        flag for when the episode is complete
    dropped_actions : list
        list of dropped actions
    end_turn_actions : Dict[str, Action]
        dictionary of default actions each agent completes after all chosen actions taken
    failed_actions : list
        list of failed actions
    hostname_ip_map : Dict[str, IPv4Address]
        map of hostnames to IP addresses
    INFO_DICT : Dict[str, _]
        mapping of individual agent knowledge of the environment
    init_state : Dict[str, _]
        initial state observation data
    max_bandwidth : int
        scenario maximum bandwidth
    message_length : int
        scenario message length
    np_random : RandomNumberGenerator
        seeded numpy random number generator
    observation: Dict[str, ObservationSet]
        observations of all agents
    reward : Dict[str, Dict[str, int]]
        current reward for each team
    routeless_actions : list
        list of routeless actions
    scenario : Scenario
        scenario object that the simulation is based off of
    scenario_generator : ScenarioGenerator
        the scenario generator that created the scenario
    state : State
        the current state of the environment
    step_count : int
        the current step count
    subnet_cidr_map : Dict[SUBNET, IPv4Network]
        map of subnets to their network ip address
    team_reward_calculators : Dict[str, Dict[str, RewardCalculator]]
        mapping of teams to their reward calculators
    team : Dict[str, List[str]]
        mapping of teams to agent names
    team_assignments : Dict[str, List[str]]
        mapping of teams to agent names (duplicate)

    [한국어]
    시뮬레이션 환경을 제어하는 클래스. 한 스텝(step)마다 모든 에이전트의 행동(Action)을
    받아 상태(State)를 갱신하고, 관찰값(Observation)·보상(Reward)·종료 신호를 계산한다.

    주요 속성:
    - action : 이번 스텝에서 각 에이전트가 수행할 행동의 딕셔너리
    - actions_in_progress : 진행 중인 행동(여러 스텝에 걸쳐 수행되는 행동의 남은 틱 관리)
    - actions_queues : 스텝 중 수행할 행동 큐
    - agents : CC4에서는 미사용, 기본값 None
    - agent_interfaces : 에이전트 이름 → AgentInterface 매핑
    - bandwidth_usage : 호스트 이름 → 대역폭 사용량 매핑
    - blocked_actions : 차단된 행동 목록
    - done : 에피소드 종료 여부 플래그
    - dropped_actions : (대역폭 초과 등으로) 폐기된 행동 목록
    - end_turn_actions : 모든 선택 행동 수행 후 각 에이전트가 수행하는 기본 종료 행동
    - failed_actions : 실패한 행동 목록
    - hostname_ip_map : 호스트 이름 → IP 주소 매핑
    - INFO_DICT : 각 에이전트가 환경에 대해 아는 정보의 매핑
    - init_state : 초기 상태 관찰 데이터
    - max_bandwidth : 시나리오의 최대 대역폭
    - message_length : 시나리오의 메시지 길이
    - np_random : 시드가 적용된 numpy 난수 생성기
    - observation : 모든 에이전트의 관찰값
    - reward : 팀별 현재 보상
    - routeless_actions : 경로가 없는 행동 목록
    - scenario : 시뮬레이션의 기반이 되는 시나리오 객체
    - scenario_generator : 시나리오를 생성한 시나리오 생성기(Scenario Generator)
    - state : 환경의 현재 상태
    - step_count : 현재 스텝 카운트
    - subnet_cidr_map : 서브넷 → 네트워크 IP 주소 매핑
    - team_reward_calculators : 팀 → 보상 계산기(RewardCalculator) 매핑
    - team : 팀 → 에이전트 이름 목록 매핑
    - team_assignments : 팀 → 에이전트 이름 목록 매핑 (중복)
    """
    def __init__(self, scenario_generator: ScenarioGenerator, agents, np_random: RandomNumberGenerator):
        """
        Parameters
        ----------
        scenario_generator : ScenarioGenerator
        agents : dict
        np_random: RandomNumberGenerator

        [한국어]
        시나리오 생성기·에이전트 목록·난수 생성기를 받아 시뮬레이션 환경을 초기화한다.
        시나리오를 만들고, 환경/에이전트를 구성하며, 초기 관찰값과 팀별 초기 보상을 계산한다.
        """
        self.state = None
        self.bandwidth_usage = {}
        self.dropped_actions = []
        self.routeless_actions = []
        self.blocked_actions = []
        self.end_turn_actions = {}
        self.hostname_ip_map = None
        self.subnet_cidr_map = None
        self.scenario_generator = scenario_generator
        self.np_random = np_random
        scenario = scenario_generator.create_scenario(np_random)
        self._create_environment(scenario)
        self.max_bandwidth = scenario.max_bandwidth
        self.step_count = 0

        self.agents = agents
        self.agent_interfaces = self._create_agents(scenario, agents)
        self.team_reward_calculators = scenario.get_reward_calculators()
        self.team = scenario.team_agents
        self.team_assignments = scenario.get_team_assignments()
        self.reward = {}
        self.INFO_DICT = {}
        self.action = {}
        self.failed_actions = []
        self.observation: Dict[str, ObservationSet] = {}
        self.actions_in_progress: Dict[str, Dict] = {}
        self.INFO_DICT['True'] = {}
        for host in scenario.hosts:
            self.INFO_DICT['True'][host] = {
                'System info': 'All',
                'Sessions': 'All',
                'Interfaces': 'All',
                'User info': 'All',
                'Processes': ['All']
            }
        self.init_state = self._filter_obs(self.get_true_state(self.INFO_DICT['True'])).data
        for agent in scenario.agents:
            self.INFO_DICT[agent] = scenario.get_agent_info(agent).osint.get('Hosts', {})
            for host in self.INFO_DICT[agent].keys():
                self.INFO_DICT[agent][host]['Sessions'] = agent

        # populate initial observations with OSINT
        # 각 에이전트가 시작 시점에 사전 정보(OSINT)로 갖는 초기 관찰값을 채운다.
        for agent_name, agent in self.agent_interfaces.items():
            obs = self.get_true_state(self.INFO_DICT[agent_name])
            self.observation[agent_name] = self._filter_obs(obs, agent_name)
            agent.set_init_obs(self.observation[agent_name].data, self.init_state)
        self.actions_queues = {agent_name: [] for agent_name in self.agent_interfaces.keys()}
        self.reset_observation()
        self.message_length = self.scenario_generator.MESSAGE_LENGTH
        self.done = self.determine_done()
        # calculate reward for each team
        # 팀별 보상을 계산한다.
        for team_name, team_calcs in self.team_reward_calculators.items():
            self.reward[team_name] = {}
            for reward_name, r_calc in team_calcs.items():
                self.reward[team_name][reward_name] = self.calculate_reward(r_calc)
        self._log_debug(f"Finished init()")

    def reset(self, np_random=None) -> Results:
        """Resets the environment

        Parameters
        ----------
        np_random: RandomNumberGenerator

        Returns
        -------
        : Results
            results object from the reset environment

        [한국어]
        환경을 초기화한다. 시나리오를 다시 생성하고 에이전트·팀·관찰값·보상을 재구성한다.
        EnterpriseScenarioGenerator(CC4 시나리오)일 때만 미션 단계(mission phase)를 0으로
        되돌리고 허용 서브넷을 갱신한다.
        """
        self.reward = {}
        self.action = {}
        self.observation = {}
        self.step_count = 0
        self.actions_in_progress = {}
        if np_random is not None:
            self.np_random = np_random

        scenario = self.scenario_generator.create_scenario(self.np_random)
        self._create_environment(scenario)

        self.agent_interfaces = self._create_agents(scenario, self.agents)
        self.team = scenario.team_agents
        self.team_assignments = scenario.get_team_assignments()
        self.max_bandwidth = scenario.max_bandwidth

        # ## INFO_DICT Changes every env.reset() given the varying network design/nodes
        # ## env.reset()마다 네트워크 설계/노드가 달라지므로 INFO_DICT도 매번 새로 만든다.
        self.INFO_DICT = {}
        self.INFO_DICT['True'] = {}
        for host in scenario.hosts:
            self.INFO_DICT['True'][host] = {'System info': 'All', 'Sessions': 'All', 'Interfaces': 'All', 'User info': 'All',
                                      'Processes': ['All']}
        self.init_state = self._filter_obs(self.get_true_state(self.INFO_DICT['True'])).data
        for agent in scenario.agents:
            self.INFO_DICT[agent] = scenario.get_agent_info(agent).osint.get('Hosts', {})
            for host in self.INFO_DICT[agent].keys():
                self.INFO_DICT[agent][host]['Sessions'] = agent
        self.actions_queues = {agent_name: [] for agent_name in self.agent_interfaces.keys()}
        for agent_name, agent_object in self.agent_interfaces.items():
            self.observation[agent_name] = self._filter_obs(self.get_true_state(self.INFO_DICT[agent_name]), agent_name)
            agent_object.set_init_obs(self.observation[agent_name].data, self.init_state)
        self.reset_observation()
        self.done = self.determine_done()

        # calculate reward for each team
        # 팀별 보상을 계산한다.
        for team_name, team_calcs in self.team_reward_calculators.items():
            self.reward[team_name] = {}
            for reward_name, r_calc in team_calcs.items():
                self.reward[team_name][reward_name] = self.calculate_reward(r_calc)
        # changes to step and mission phase will only effect CC4
        # 스텝·미션 단계 관련 변경은 CC4에만 적용된다.
        if isinstance(self.scenario_generator, EnterpriseScenarioGenerator):
            # update step in state and calc current mission phase to step = 0
            # 상태의 스텝을 갱신하고 미션 단계를 step = 0 기준으로 초기화한다.
            self.state.mission_phase = 0
            # update allowed subnets in all agent interfaces and agent spaces
            # 모든 에이전트 인터페이스와 행동 공간(Action Space)의 허용 서브넷을 갱신한다.
            self._update_agents_allowed_subnets()
    
    def step(self, actions: dict = None, skip_valid_action_check=False):
        """Updates the simulation environment based on the joint actions of all agents

        Parameters
        ----------
        actions : Dict[str, Action]
            name of the agent and the action they perform
        skip_valid_action_check: bool
            if false then action is checked against the agents action space to determine validity of action and .
            if not valid then the action is replaced with an InvalidAction object

        [한국어]
        모든 에이전트의 합동 행동(joint action)을 받아 시뮬레이션 환경을 한 스텝 진행한다.
        흐름: 행동 수집 → 진행 중 행동의 틱 감소·실행 대상 선별 → 우선순위순 실행 →
        세션 재배정 → 종료 행동 실행 → 에이전트 인터페이스/행동 공간 갱신 → 보상 계산.

        skip_valid_action_check가 False면 각 행동을 에이전트의 행동 공간(Action Space)과
        대조해 유효성을 검사하고, 유효하지 않으면 InvalidAction 객체로 교체한다.
        """
        # changes to step and mission phase will only effect CC4
        # 스텝·미션 단계 관련 변경은 CC4에만 적용된다.
        if isinstance(self.scenario_generator, EnterpriseScenarioGenerator):
            # update step in state and calc current mission phase
            # if mission phase has changed (inc.) then return True else return False
            # 상태의 스텝을 갱신하고 현재 미션 단계를 계산한다.
            # 미션 단계가 (증가하여) 바뀌었으면 True, 아니면 False를 반환한다.
            if self.state.check_next_phase_on_update_step(self.step_count):
                # update allowed subnets in all agent interfaces and agent spaces
                # 모든 에이전트 인터페이스와 행동 공간의 허용 서브넷을 갱신한다.
                self._update_agents_allowed_subnets()

        if actions is None:
            actions = {}

        # Adds new actions to the action sets.
        # Any agent that doesn't have an action supplied has a default action added for it.
        # 행동 집합에 새 행동을 추가한다.
        # 행동이 주어지지 않은 에이전트에는 기본 행동을 대신 넣는다.
        for agent_name, agent_object in self.agent_interfaces.items():
            action = actions.get(agent_name, None)
            if action is None:
                last_obs = self.get_last_observation(agent_name)
                action = agent_object.get_action(last_obs)
            if not skip_valid_action_check:
                action = self.replace_action_if_invalid(action, agent_object)
            # Adds a new item to a particular action set. Action sets are indexed by agent_name
            # This function will create any necessary empty dicts/lists as it goes.
            # The remaining_ticks is assumed to start at the duration of the action unless specified otherwise.
            # 행동 집합은 agent_name으로 인덱싱되며, 필요한 빈 dict/list는 진행하며 자동 생성된다.
            # remaining_ticks(남은 틱)는 별도 지정이 없으면 행동의 duration(소요 시간)에서 시작한다고 본다.
            set_item = {"action": action, "remaining_ticks": action.duration}
            if self.actions_in_progress.get(agent_name, None) is None:
                self.actions_in_progress[agent_name] = set_item

        # clear old observations
        # 이전 관찰값을 비운다.
        self.observation = {a: ObservationSet([]) for a in self.agent_interfaces}


        # Iterates through all of the actions in the action sets, decrementing their remaining ticks.
        # Any actions with < 1 remaining ticks are ready to execute and are moved from actions_in_progress to actions_to_execute.
        # [설명] 행동은 여러 스텝에 걸쳐 수행될 수 있다(duration > 1). 매 스텝 remaining_ticks를 1씩
        #        줄이고, 0 미만이 된 행동만 이번 스텝에 실제 실행한다. 아직 진행 중인 행동은 IN_PROGRESS
        #        관찰값을 남기고 Sleep()으로 대체해 이번 스텝에는 효과가 없게 한다.
        actions_to_execute: Dict[str, List[Dict]] = {}
        for agent_name, set_item in self.actions_in_progress.items():
            set_item["remaining_ticks"] -= 1
            actions_to_execute.setdefault(agent_name, [])
            if set_item["remaining_ticks"] < 1:
                self.actions_in_progress[agent_name] = None
                actions_to_execute[agent_name].append(set_item['action'])
            else:
                self.observation[agent_name].append(Observation(TernaryEnum.IN_PROGRESS))
                actions_to_execute[agent_name].append(Sleep())

        self.action = actions_to_execute
        actions_to_execute = self.sort_action_order(actions_to_execute)

        # execute actions in order of priority
        # 우선순위 순서대로 행동을 실행한다.
        for (agent_name, action) in actions_to_execute:
            obs = self.execute_action(action)
            filtered_obs = self._filter_obs(obs, agent_name)
            filtered_obs.data['action'] = action
            self.observation[agent_name].append(filtered_obs)

        # check for sessions that need to be reassigned to a different agent, due to subnet traversal
        # 서브넷을 넘나든 결과 다른 에이전트로 재배정해야 할 세션이 있는지 확인한다.
        self.different_subnet_agent_reassignment()

        # execute additional default end turn actions
        # 각 에이전트의 기본 종료 행동(end turn action)을 추가로 실행한다.
        for agent_name, agent_action in self.end_turn_actions.items():
            if self.agent_interfaces[agent_name].active:
                obs = self.execute_action(agent_action[0](**agent_action[1]))
                filtered_obs = self._filter_obs(obs, agent_name)
                filtered_obs.data['action'] = agent_action[0](**agent_action[1])
                self.observation[agent_name].observations.append(filtered_obs)
                # self._session_check()

        # update agent interfaces and action spaces
        # 에이전트 인터페이스와 행동 공간을 갱신한다.
        for agent_name, observation_sets in self.observation.items():
            for observation in observation_sets.observations:
                session_length = len(self.get_action_space(agent_name)['session'])
                if self.scenario_generator.update_each_step or session_length == 0:
                    self.agent_interfaces[agent_name].update(observation)

        # Increment step counter
        # 스텝 카운터를 증가시킨다.
        self.step_count += 1

        # calculate done signal
        # 종료 신호(done)를 계산한다.
        self.done = self.scenario_generator.determine_done(self)

        # reset previous reward
        # 이전 보상을 초기화한다.
        self.reward = {}

        # calculate reward for each team
        # 팀별 보상을 계산한다(행동 비용 action_cost도 함께 합산).
        for team_name, team_calcs in self.team_reward_calculators.items():
            self.reward[team_name] = {}
            for reward_name, r_calc in team_calcs.items():
                self.reward[team_name][reward_name] = self.calculate_reward(r_calc)
            action_cost = sum(actions.get(agent, Action()).cost for agent in self.team[team_name])
            self.reward[team_name]['action_cost'] = action_cost

        for host in self.state.hosts.values():
            host.update(self.state)
        self.state.update_data_links()

    def set_np_random(self, np_random):
        """Sets the random number generator

        [한국어]
        난수 생성기를 설정한다.
        """
        self.np_random = np_random
        self.state.set_np_random(np_random)

    def execute_action(self, action: Action) -> Observation:
        """Executes the given action

        Parameters
        ----------
        action : Action
            action to execute

        Returns
        -------
        : Observation
            the observation resulting from the performed action

        [한국어]
        주어진 행동(Action)을 실행하고, 그 결과로 생긴 관찰값(Observation)을 반환한다.
        """
        return action.execute(self.state)

    def get_true_state(self, info: dict) -> Observation:
        """Gets the true state

        Parameters
        ----------
        info : dict

        Returns
        -------
        output : Observation
            the observation from the true state

        [한국어]
        실제 상태(true state)를 가져온다. info 딕셔너리로 지정한 범위만큼의
        관찰값(Observation)을 반환한다.
        """
        output = self.state.get_true_state(info)
        return output

    def _create_environment(self, scenario: Scenario):
        self.state = State(scenario, self.np_random)
        self.hostname_ip_map = {h: ip for ip, h in self.state.ip_addresses.items()}
        self.subnet_cidr_map = self.state.subnet_name_to_cidr
        self.end_turn_actions = scenario.get_end_turn_actions()

    def calculate_reward(self, reward_calculator: RewardCalculator) -> float:
        """Calculates the reward using the reward calculator

        Parameters
        ----------
        reward_calculator : RewardCalculator
            An object to calculate the reward

        Returns
        -------
        : float
            The reward value for the associated reward calculator

        [한국어]
        보상 계산기(RewardCalculator)를 사용해 보상값을 계산한다.
        """
        return reward_calculator.calculate_simulation_reward(self)

    def get_active_agents(self) -> list:
        """Gets the currently active agents

        Returns
        -------
        active_agents : list
            list of active agents

        [한국어]
        현재 활성 상태인 에이전트 목록을 반환한다. 활성 부모 세션(parent is None)이 있고
        internal_only가 아닌 에이전트만 포함한다.
        """

        active_agents = []
        for agent_name, sessions in self.state.sessions.items():
            length = len([session.ident for session in sessions.values() if session.active and session.parent is None])
            if length > 0 and not self.agent_interfaces[agent_name].internal_only:
                active_agents.append(agent_name)

        return active_agents

    def is_active(self, agent_name: str) -> bool:
        """Tests if agent has an active server session

        [한국어]
        에이전트가 활성 서버 세션(부모가 없는 active 세션)을 가졌는지 검사한다.
        """
        return len([session.ident for session in self.state.sessions[agent_name].values() if session.active and session.parent is None]) > 0

    def has_active_non_parent_sessions(self, agent_name: str) -> bool:
        """Tests if an agent has active sessions that aren't a parent session

        [한국어]
        에이전트가 부모 세션이 아닌 활성 세션(자식 세션)을 가졌는지 검사한다.
        """
        return len([session.ident for session in self.state.sessions[agent_name].values() if session.active and session.parent is not None]) > 0

    def sort_action_order(self, actions: Dict[str, List[Action]]) -> List[Tuple[str,Action]]:
        """Sorts the actions based on priority and sets the dropped parameter for actions based on bandwidth usage

        Parameters
        ----------
        actions : Dict[str, List[Action]]
            dictionary of actions to sort

        Returns
        -------
        : List[Tuple[str,Action]]
            sorted list of actions

        [한국어]
        행동을 우선순위(priority)로 정렬하고, 대역폭 사용량에 따라 폐기(dropped) 여부를 설정한다.
        원격 행동(RemoteAction)은 통과 경로(route)를 따라 각 호스트에서 대역폭을 소비하며,
        차단(block)되거나 최대 대역폭을 초과하면 그 지점에서 멈추고 차단/폐기로 분류된다.
        """
        # 에이전트별 행동 딕셔너리를 (에이전트, 행동) 튜플 리스트로 펼친 뒤 우선순위로 정렬한다.
        flattened_actions = [(agent_name, agent_action) for agent_name, agent_actions in actions.items() for agent_action in agent_actions]
        actions = sorted(flattened_actions, key=lambda x: x[1].priority)
        actions = self.filter_actions(actions)

        # shuffle action order to randomise which are dropped if bandwidth exceeded
        # [설명] 대역폭 초과 시 어떤 행동을 폐기할지 편향되지 않도록, 우선순위 정렬과 별개로
        #        처리 순서를 무작위로 섞는다(공정성 확보).
        action_index = list(range(len(actions)))
        self.np_random.shuffle(action_index)

        # use bandwidth until exceeded then drop actions
        # 최대 대역폭을 초과하기 전까지는 대역폭을 소비하고, 초과하면 행동을 폐기한다.
        bandwidth_usage = {}
        self.routeless_actions = []
        self.blocked_actions = []
        self.dropped_actions = []

        for i in action_index:
            (agent, action) = actions[i]
            if issubclass(type(action), RemoteAction):
                # 행동이 통과하는 경로(출발지 → 목적지 사이의 호스트 목록)를 구한다.
                route = action.get_used_route(self.state, routing=True)
                action.route_designated = True
                if route is not None:
                    for host in route:
                        # if blocked then action consumes no further bandwidth
                        # if host in self.state.blocks and route[0] in self.state.blocks[host]:
                        # 차단된 경우 이후로는 대역폭을 소비하지 않고 멈춘다.
                        if action.blocking_host(self.state, route[0], host):
                            action.blocked = host
                            self.blocked_actions.append(action)
                            break
                        # otherwise action consumes bandwidth at host
                        # 그렇지 않으면 해당 호스트에서 대역폭을 소비한다.
                        if host in bandwidth_usage:
                            bandwidth_usage[host] += action.bandwidth_usage
                        else:
                            bandwidth_usage[host] = action.bandwidth_usage
                        # and bandwidth from all surrounding hosts
                        # [설명] 무선(wireless) 인터페이스는 전파가 주변으로 퍼지므로, 같은 데이터 링크로
                        #        연결된 주변 호스트의 대역폭도 함께 소비한 것으로 계산한다.
                        for interface in self.state.hosts[host].interfaces:
                            if interface.interface_type == 'wireless':
                                for h in interface.data_links:
                                    if h in bandwidth_usage:
                                        bandwidth_usage[h] += action.bandwidth_usage
                                    else:
                                        bandwidth_usage[h] = action.bandwidth_usage
                        # if the maximum bandwidth is exceeded then the action is droppped and doesn't continue down the route
                        # 최대 대역폭을 초과하면 행동을 폐기하고 더 이상 경로를 따라가지 않는다.
                        if bandwidth_usage[host] > self.max_bandwidth:
                            self.dropped_actions.append(action)
                            action.dropped = True
                            break
                else:
                    # 경로가 없으면(routeless) 행동을 폐기한다.
                    action.dropped = True
                    self.routeless_actions.append(action)
        self.bandwidth_usage = dict(bandwidth_usage)

        # # sort the actions based on priority
        # actions = dict(sorted(actions.items(), key=lambda item: item[1].priority))
        return actions

    def filter_actions(self, actions: List[Tuple[str,Action]]) -> List[Tuple[str,Action]]:
        """ Checks agent and session exist for each action

        Parameters
        ----------
        actions : List[Tuple[str,Action]]
            list of actions to filter

        Returns
        -------
        : List[Tuple[str,Action]]
            list of filtered actions

        [한국어]
        각 행동에 대해 에이전트와 세션이 존재하는지 확인해 걸러낸다.
        세션이 필요 없는 행동(sessionless)이거나, 에이전트가 해당 세션에 접근 권한이 있는
        행동(has_access)만 남긴다.
        """
        # 세션 속성 자체가 없는 행동인지 판별하는 람다.
        sessionless = lambda action: not hasattr(action, 'session')
        # 행동의 세션이 해당 에이전트의 보유 세션 목록에 있는지 판별하는 람다.
        has_access = lambda action: action.session in self.state.sessions.get(action.agent, [])
        filtered_actions: List[Tuple[str,Action]] = []
        for (agent, action) in actions:
            if sessionless(action) or has_access(action):
                filtered_actions.append((agent, action))
        return filtered_actions

    def get_connected_agents(self, agent: str) -> list:
        """Gets a list of agents that are connected the the agent

        [한국어]
        주어진 에이전트와 (라우팅 가능 경로로) 연결된 다른 에이전트 목록을 반환한다.
        에이전트의 부모 세션이 위치한 호스트를 찾고, 그 호스트와 통신 가능한 호스트들에
        부모 세션을 둔 에이전트를 모은다.
        """
        # get agents host
        # 에이전트의 (부모 세션이 위치한) 호스트를 찾는다.
        hostname = None
        for sessions, session_obj in self.state.sessions[agent].items():
            if session_obj.parent == None:
                hostname = session_obj.hostname

        if hostname is None:
            return [agent]

        # get all connected hosts
        # 해당 호스트와 라우팅 가능한 모든 호스트를 구한다.
        connected_hosts = []
        for host in self.state.hosts.keys():
            if RemoteAction.check_routable(self.state, host, hostname):
                connected_hosts.append(host)

        # get agents on connected hosts
        # 연결된 호스트에 부모 세션을 둔 에이전트들을 모은다.
        connected_agents = []
        for other_agent, sessions in self.state.sessions.items():
            if agent == other_agent:
                continue

            for session in sessions.values():
                if session.hostname in connected_hosts and session.parent is None:
                    connected_agents.append(other_agent)
                    break
        return connected_agents

    def get_render_data(self):
        """ Build render data for CC3 - not used for CC4

        [한국어]
        CC3용 렌더링 데이터를 만든다 - CC4에서는 사용하지 않는다(본문 전체 주석 처리됨).
        """
        pass
        # scenario_gen_type = 'Unsupport scenario'
        # if isinstance(self.scenario_generator, DroneSwarmScenarioGenerator):
        #     scenario_gen_type = DroneSwarmScenarioGenerator
        # elif isinstance(self.scenario_generator, FileReaderScenarioGenerator):
        #     scenario_gen_type = FileReaderScenarioGenerator
        # if self.scenario_generator.background_image is None:
        #     raise ValueError(f"Scenario generator {self.scenario_generator.__class__} has not background_image set")
        # background_image = self.scenario_generator.background_image
        # data = {'scenario_gen_type': scenario_gen_type,
        #         'drones': {hostname: {"hostname": hostname,
        #                               "x": host_info.position[0],
        #                               "y": host_info.position[1],
        #                               "os_type": host_info.os_type.name,
        #                               "ip": host_info.interfaces[0].ip_address,
        #                               "processes": host_info.processes,
        #                               "sessions": self.state.sessions} for hostname, host_info in
        #                    self.state.hosts.items()},
        #         'network': {hostname: [h for interface in host_info.interfaces for h in interface.data_links] for
        #                     hostname, host_info in
        #                     self.state.hosts.items()},
        #         'actions': [],
        #         "background": background_image,
        #         "step": self.step_count}

        # # get which hosts are red
        # red_hosts, red_low_hosts, red_action = self.add_red_actions(data, scenario_gen_type)

        # # get which hosts are blue
        # blue_hosts, blue_protected_hosts = self.add_blue_actions(data, red_action, scenario_gen_type)

        # # 'BlueDrone', 'BlueDroneLowProvRed', 'RedDrone', 'BlueDroneProtected'
        # self.update_symbols(data, red_hosts, red_low_hosts, blue_hosts, blue_protected_hosts)

        # # add in rewards
        # self.add_rewards(data)

        # # add number of times taken by Red & number of times retaken by Blue
        # # if self.state.scenario.get_scenario_gen_type() == FileReaderScenarioGenerator:
        # #     data['sessions_count'] = self.get_impact_restore_count()
        # # elif self.state.scenario.get_scenario_gen_type() == DroneSwarmScenarioGenerator:
        # #     data['sessions_count'] = self.state.sessions_count
        # # else:
        # #     data['sessions_count'] = {}

        # return data

    def get_impact_restore_count(self) -> Dict[str, Dict[str, int]]:
        sessions_count = {}
        for hostname, hostinfo in self.state.hosts.items():
            sessions_count[hostname] = {}
            sessions_count[hostname]["impact_count"] = hostinfo.get_impact_count()
            sessions_count[hostname]["restore_count"] = hostinfo.get_restore_count()

        return sessions_count

    def add_rewards(self, data):
        data['rewards'] = {}

        for team in ['Red', 'Blue']:
            rewards = self.reward.get(team, {})

            if len(rewards) == 0:
                data['rewards'][team] = 0
            else:
                try:
                    data['rewards'][team] = sum(rewards.values())
                except:
                    print(rewards)

    def update_symbols(self, data, red_hosts, red_low_hosts, blue_hosts, blue_protected_hosts):
        for hostname, host_info in self.state.hosts.items():
            # if red high priv
            # Red가 높은 권한을 가진 경우
            if hostname in red_hosts:
                data['drones'][hostname]['symbol'] = 'RedDrone'
            # if red low priv
            # Red가 낮은 권한을 가진 경우
            elif hostname in red_low_hosts:
                data['drones'][hostname]['symbol'] = 'BlueDroneLowPrivRed'
            # if blue protected
            # Blue가 보호된(protected) 경우
            elif hostname in blue_protected_hosts:
                data['drones'][hostname]['symbol'] = 'BlueDroneProtected'
            # else blue
            # 그 외 Blue인 경우
            elif hostname in blue_hosts:
                data['drones'][hostname]['symbol'] = 'BlueDrone'
            # else neutral host
            # 그 외 중립 호스트인 경우
            else:
                data['drones'][hostname]['symbol'] = 'NeutralDrone' # routers (라우터)

    def add_blue_actions(self, data, red_action, scenario_gen_type):
        blue_hosts = []
        blue_protected_hosts = []
        blue_action = None
        for agent in self.team['Blue']:
            blue_hosts += [i.hostname for i in self.state.sessions[agent].values()]

            for blue_session in self.state.sessions[agent].values():
                for host_proc in self.state.hosts[blue_session.hostname].processes:
                    if host_proc.decoy_type != DecoyType.NONE:
                        blue_protected_hosts.append(blue_session.hostname)

            if agent in self.action:
                for blue_action in self.action[agent]:

                    if type(blue_action) in (Sleep, InvalidAction):
                        continue

                    blue_from = agent

                    # set action source
                    # 행동의 출발지(source)를 설정한다.
                    if self.state.sessions.get(blue_action.agent) and self.state.sessions[blue_action.agent].get(blue_action.session):
                        blue_source = self.state.sessions[blue_action.agent][blue_action.session].hostname
                    else:
                        continue

                    # set action target
                    # 행동의 목적지(target)를 설정한다.
                    blue_target = None
                    if hasattr(blue_action, 'subnet'):
                        blue_target = \
                        [name for name, cidr in self.state.subnet_name_to_cidr.items() if
                         cidr == red_action.subnet][0] + 'Subnet'
                    # if scenario_gen_type == FileReaderScenarioGenerator:
                    #     if hasattr(blue_action, 'ip_address') and hasattr(red_action, 'ip_address'):
                    #         blue_target = self.state.ip_addresses[red_action.ip_address]
                    #     elif hasattr(blue_action, 'ip_address'):
                    #         blue_target = self.state.ip_addresses[blue_action.ip_address]

                    # if scenario_gen_type == DroneSwarmScenarioGenerator:
                    #     if hasattr(blue_action, 'ip_address'):
                    #         blue_target = self.state.ip_addresses[blue_action.ip_address]

                    #     if type(blue_action) == RemoveOtherSessions:
                    #         blue_target = self.state.sessions[blue_action.agent][0].hostname

                    if hasattr(blue_action, 'hostname'):
                        blue_target = blue_action.hostname

                    # set blue action label
                    # Blue 행동의 라벨(label)을 설정한다.
                    blue_action_type: str = None
                    action_type_map = {}
                    if blue_target is not None:
                        # if scenario_gen_type == FileReaderScenarioGenerator:
                        #     action_type_map = {
                        #         DiscoverNetworkServices: 'port scan',
                        #         DiscoverRemoteSystems: 'network scan',
                        #         Restore: 'restore',
                        #         Remove: 'remove',
                        #         Analyse: 'analyse'
                        #     }
                        # elif scenario_gen_type == DroneSwarmScenarioGenerator:
                        #     action_type_map = {
                        #         RetakeControl: 'restore',
                        #         RemoveOtherSessions: 'remove',
                        #         AllowTraffic: 'allow_traffic',
                        #         BlockTraffic: 'block_traffic'
                        #     }
                        blue_action_type = action_type_map.get(type(blue_action), None)

                        # set actions
                        # 행동(action) 정보를 기록한다.
                        if blue_action_type is not None:
                            data['actions'].append(
                                {"agent": blue_from, "source": blue_source, "destination": blue_target,
                                "type": blue_action_type})
                         
        return blue_hosts,blue_protected_hosts

    def add_red_actions(self, data, scenario_gen_type):
        red_hosts = []
        red_low_hosts = []
        red_action = None
        for agent in self.team['Red']:
            sessions = self.state.sessions[agent].values()
            red_hosts += [s.hostname for s in sessions if s.has_privileged_access()]
            red_low_hosts += [s.hostname for s in sessions]
            # get agent actions
            # 에이전트의 행동들을 가져온다.
            if agent in self.action:
                for red_action in self.action[agent]:

                    if type(red_action) in (Sleep, InvalidAction):
                        continue
                    red_from = agent

                    # fix ActivateTrojan bug for drone swarm scenario
                    # 드론 스웜(drone swarm) 시나리오의 ActivateTrojan 버그를 보정한다.
                    if red_action.name == 'ActivateTrojan':
                        red_source = red_action.hostname
                    else:
                        if self.state.sessions.get(red_action.agent) and self.state.sessions[red_action.agent].get(red_action.session):
                            red_source = self.state.sessions[red_action.agent][red_action.session].hostname
                        else:
                            continue

                    # set red target
                    # Red 행동의 목적지(target)를 설정한다.
                    red_target = None
                    if hasattr(red_action, 'subnet'):
                        red_target = \
                        [name for name, cidr in self.state.subnet_name_to_cidr.items() if
                         cidr == red_action.subnet][0] + '_router'
                    if hasattr(red_action, 'ip_address'):
                        red_target = self.state.ip_addresses[red_action.ip_address]
                    if hasattr(red_action, 'hostname'):
                        red_target = red_action.hostname

                    # set red action label
                    # Red 행동의 라벨(label)을 설정한다.
                    red_action_type: str = None
                    action_type_map = {}
                    if red_target is not None:
                        if scenario_gen_type == EnterpriseScenarioGenerator: # or scenario_gen_type == FileReaderScenarioGenerator):
                            action_type_map = {
                                DiscoverNetworkServices: 'port scan',
                                DiscoverRemoteSystems: 'network scan',
                                ExploitRemoteService: 'exploit',
                                Analyse: 'analyse',
                                PrivilegeEscalate: 'escalate',
                                Impact: 'impact'
                            }
                        # elif scenario_gen_type == DroneSwarmScenarioGenerator:
                        #     action_type_map = {
                        #         ExploitDroneVulnerability: 'exploit',
                        #         FloodBandwidth: 'impact',
                        #         SeizeControl: 'escalate'
                        #     }
                        red_action_type = action_type_map.get(type(red_action), None)

                        if red_action_type is not None:
                            # set actions
                            # 행동(action) 정보를 기록한다.
                            data['actions'].append(
                                {"agent": red_from, "destination": red_target, "source": red_source, "type": red_action_type})

        return red_hosts,red_low_hosts,red_action

    def _update_agents_allowed_subnets(self):
        """This function updates the allowed_subnets of the green agents depending on the current mission phases.

        [한국어]
        현재 미션 단계(mission phase)에 따라 Green 에이전트의 허용 서브넷(allowed_subnets)을
        갱신한다. 미션 단계마다 어떤 서브넷 쌍이 통신 가능한지가 달라지므로, Green 에이전트가
        속한 서브넷과 통신 가능한 서브넷들만 허용 목록에 둔다.
        """
        curr_mp = self.state.mission_phase
        # 현재 미션 단계에서 통신이 허용된 (서브넷, 서브넷) 쌍 목록.
        mphases = self.state.scenario.allowed_subnets_per_mphase[curr_mp]

        for agent_name, agent in self.agent_interfaces.items():
            if "green" in agent_name:
                green_host = self.state.sessions[agent_name][0].hostname
                green_subnet = self.state.hostname_subnet_map[green_host]
                green_mphase = [green_subnet]   # a subnet is always allowed to communicate within itself
                                                # 서브넷은 항상 자기 자신 안에서는 통신이 허용된다.

                # [설명] 허용 쌍 목록을 훑어 Green 서브넷이 한쪽에 등장하면 반대쪽 서브넷을
                #        허용 목록에 추가한다. 즉 현재 단계에서 이 Green이 통신할 수 있는 서브넷을 모은다.
                for idx in range(len(mphases)):
                    (s1, s2) = mphases[idx]
                    if s1 == green_subnet:
                        green_mphase.append(s2)
                    elif s2 == green_subnet:
                        green_mphase.append(s1)

                agent.update_allowed_subnets(green_mphase)

    def reset_observation(self):
        """Populate initial observations with OSINT

        [한국어]
        각 에이전트의 초기 관찰값을 사전 정보(OSINT)로 채운다.
        """
        for agent_name, agent in self.agent_interfaces.items():
            true_state = self.get_true_state(self.INFO_DICT[agent_name])
            initial_obs = self._filter_obs(true_state, agent_name)
            agent.set_init_obs(initial_obs.data, self.init_state)
            self.observation[agent_name] = ObservationSet([initial_obs])

    def _session_check(self):
        for agent in self.state.sessions:
            for host in self.state.hosts.values():
                for session in host.sessions[agent]:
                    assert session in self.state.sessions[agent]

    def send_messages(self, messages: dict = None):
        """Sends messages between agents

        Parameters
        ----------
        messages : dict

        [한국어]
        에이전트 간 메시지를 전달한다. 각 메시지는 보낸 에이전트와 연결된(connected) 에이전트들에게만
        전달되고, 그 결과는 수신 에이전트의 관찰값(Observation)에 추가된다.
        """
        if messages is None:
            messages = {}

        # reset messages
        # 메시지를 초기화한다.
        for agent, agent_interface in self.agent_interfaces.items():
            agent_interface.messages = []

        # send message to other agents
        # 다른 에이전트에게 메시지를 보낸다(메시지 공간 message space에 속하는지 검증 포함).
        for agent, message in sorted(messages.items()):
            assert self.get_message_space(agent).contains(message), f'{agent} attempting to send message {message} that is not in the message space {self.get_message_space(agent)}'
            for other_agent in self.get_connected_agents(agent):
                self.agent_interfaces[other_agent].messages.append(message)

        # add messages to observations
        # 받은 메시지를 관찰값에 추가한다.
        for agent, observation in self.observation.items():
            if len(self.agent_interfaces[agent].messages) > 0:
                observation.append(Observation(msg=self.agent_interfaces[agent].messages))

    def get_message_space(self, agent) -> gym.Space:
        msg_space = gym.spaces.MultiBinary(self.message_length)
        msg_space._np_random = self.np_random
        return msg_space

    def determine_done(self) -> bool:
        """The done signal is always false
        Returns
        -------
        bool
            whether goal was reached or not

        [한국어]
        종료 신호(done)를 계산해 반환한다. 실제 판정은 시나리오 생성기에 위임한다.
        (원문 주석은 "항상 false"라고 하지만 판정은 scenario_generator가 담당한다.)
        """
        return self.scenario_generator.determine_done(self)

    def different_subnet_agent_reassignment(self):
        """ If an agent has a session outside of their subnet, change the agent to the corresponding agent for the subnet. If that agent is not active, activate them.

        Note, a red agent may have multiple red sessions assigned to it from the PhisingEmail action (assigned to the closest connected red agent).
        However, only not all of these will need to be reassigned, therefore, we may need to reindex the original red agents sessions.
        This requires making adjustments to the state.sessions, state.sessions_counts, state.hosts, and the sessions children.

        This is only required for the EnterpriseScenarioGenerator, and will cause the failure of tests that utilise older scenarios if instance not checked.

        [한국어]
        에이전트가 자기 서브넷 밖에 세션을 가지고 있으면, 그 서브넷을 담당하는 에이전트로 세션을
        재배정한다. 담당 에이전트가 비활성이면 활성화한다.

        배경: PhishingEmail 행동으로 Red 에이전트는 (가장 가깝게 연결된 Red에게) 여러 세션을 한꺼번에
        받을 수 있다. 그중 일부만 재배정 대상일 수 있어 원래 Red 에이전트의 세션을 다시 인덱싱해야 한다.
        이를 위해 state.sessions, state.sessions_count, state.hosts, 그리고 세션의 자식 관계를 함께 손본다.

        이 처리는 EnterpriseScenarioGenerator(CC4)에서만 필요하다. isinstance로 막지 않으면 옛 시나리오를
        쓰는 테스트가 실패하므로 반드시 인스턴스 검사를 둔다.
        """

        if isinstance(self.scenario_generator, EnterpriseScenarioGenerator):
            # Red 에이전트별 허용 서브넷 매핑을 만든다.
            red_allowed_subnets_map = { agent_name : agent.allowed_subnets for agent_name, agent in self.agent_interfaces.items() if 'red' in agent_name}
            sessions_to_reassign = []

            # if a session's agent does not match its host's subnet, then add it to the list of 'sessions_to_reassign'
            # [설명] 세션이 위치한 호스트의 서브넷이 해당 에이전트의 허용 서브넷에 없으면,
            #        그 세션은 다른 에이전트로 넘겨야 하므로 재배정 대상 목록에 추가한다.
            for agent_name in red_allowed_subnets_map.keys():
                for session_id in self.state.sessions[agent_name]:
                    session_host_subnet = self.state.hostname_subnet_map[self.state.sessions[agent_name][session_id].hostname].value
                    if session_host_subnet not in red_allowed_subnets_map[agent_name]:
                        reassign = {
                            'orig_agent' : agent_name,
                            'orig_session_id' : session_id,
                            'host_subnet' : session_host_subnet,
                            'host_name' : self.state.sessions[agent_name][session_id].hostname,
                            'host_ip' : str(self.state.hostname_ip_map[self.state.sessions[agent_name][session_id].hostname])
                        }
                        sessions_to_reassign.append(reassign)

            # Find the agent that should own the session
            # 세션의 호스트 서브넷을 허용 서브넷으로 가진 에이전트를 새 소유자로 지정한다.
            for red_owner, allowed_subnets in red_allowed_subnets_map.items():
                for reassign_dict in sessions_to_reassign:
                    if reassign_dict['host_subnet'] in allowed_subnets:
                        reassign_dict['new_agent'] = red_owner

            # For each of the sessions to reassign
            # 재배정 대상 세션마다 처리한다.
            for reassignment in sessions_to_reassign:
                # Reassign sessions (remove old and add new)
                # 세션을 재배정한다(기존 세션 제거 후 새 세션 추가).
                old_session = self.state.sessions[reassignment['orig_agent']].pop(reassignment['orig_session_id'])
                new_session = RedAbstractSession(
                    hostname=old_session.hostname, username=old_session.username,
                    agent=reassignment['new_agent'], parent=None, pid=old_session.pid,
                    session_type=Enums.SessionType.RED_ABSTRACT_SESSION,
                    timeout=old_session.timeout, ident = None,
                    is_escalate_sandbox=old_session.is_escalate_sandbox,
                )
                self.state.add_session(new_session)
                self.state.sessions_count[reassignment['orig_agent']]-=1

                self.state.hosts[new_session.hostname].sessions[reassignment['orig_agent']].remove(reassignment['orig_session_id'])
                reassignment['new_session_id'] = new_session.ident

                # Edit + Add Observation
                # [설명] 기존 에이전트의 관찰값에서 이 세션 항목을 찾아 새 에이전트/세션 ID로 수정하고,
                #        같은 호스트 정보만 추린 사본을 새 에이전트의 관찰값으로 추가한다.
                new_obs = None
                for i, obs in enumerate(self.observation[reassignment['orig_agent']].observations):
                    if reassignment['host_ip'] in obs.data.keys():
                        for obs_sess in obs.data[reassignment['host_ip']]['Sessions']:
                            if obs_sess['agent'] == reassignment['orig_agent'] and obs_sess['session_id'] == reassignment['orig_session_id']:
                                # Edit the current agent's observation
                                # 기존 에이전트의 관찰값을 수정한다.
                                obs_sess['agent'] = reassignment['new_agent']
                                obs_sess['session_id'] = reassignment['new_session_id']
                                obs_sess['Type'] = Enums.SessionType.RED_ABSTRACT_SESSION

                                # Add this as a new observation to the new agent
                                # 이를 새 에이전트의 새 관찰값으로 추가한다.
                                new_obs = obs.copy()
                                remove_keys = [k for k in new_obs.data.keys() if not k == reassignment['host_ip'] and not k == 'action' and not k == 'success']
                                for key in remove_keys:
                                    new_obs.data.pop(key)

                                new_obs.raw = reassignment['orig_agent'] + "'s action created a new session."
                                new_obs.data.pop('action')
                                new_obs.data['success'] = TernaryEnum.UNKNOWN

                                self.observation[reassignment['new_agent']].observations.append(new_obs)
                        break

        # if agent is not active but has sessions then activate
        # [설명] 비활성 에이전트가 세션을 가지게 되면 활성화하고, 활성 에이전트가 세션을 모두 잃으면
        #        비활성화한다. 단, Trojan 계열은 에이전트를 생성할 수 있어야 하므로 비활성화에서 제외한다.
        for agent_name, agent_int in self.agent_interfaces.items():
            if agent_int.active==False and self.is_active(agent_name)==True:
                self.agent_interfaces[agent_name].active=True
            elif agent_int.active==False and self.is_active(agent_name)==False and self.has_active_non_parent_sessions(agent_name):
                self.agent_interfaces[agent_name].active=True
            elif agent_int.active==True and self.is_active(agent_name)==False and self.has_active_non_parent_sessions(agent_name)==False and 'Trojan' not in agent_name:
                # hack to ensure DroneScenario Trojan can still spawn agents
                # DroneScenario의 Trojan이 계속 에이전트를 생성할 수 있게 하려는 임시 처리(hack).
                self.agent_interfaces[agent_name].active=False

    def start(self, steps: int = None, log_file=None, verbose=False):
        """Start the environment and run for a specified number of steps.

        Parameters
        ----------
        steps : int
            the number of steps to run for
        log_file : File, optional
            a file to write results to (default=None)

        Returns
        -------
        bool
            whether goal was reached or not

        [한국어]
        환경을 시작해 지정한 스텝 수만큼 실행한다. steps가 None이면 종료될 때까지 무한히 진행한다.
        log_file이 주어지면 실행 결과(스텝 수, 팀별 보상 등)를 기록한다.
        """
        done = False
        max_steps = 0
        if steps is None:
            while not done:
                if verbose:
                    print(max_steps)
                max_steps += 1
                self.step()
            if verbose:
                print('Red Wins!')  # Junk Test Code (불필요한 테스트용 코드)
        else:
            for step in range(steps):
                max_steps += 1
                self.step()
                if verbose:
                    print(max_steps)
                done = self.done
                if step == 500:
                    print(step)  # Junk Test Code (불필요한 테스트용 코드)
                if done:
                    print(f'Red Wins at step {step}')  # Junk Test Code (불필요한 테스트용 코드)
                    break

            # print(f"{agent_name}'s Reward: {self.reward[agent_name]}")
        if log_file is not None:
            log_file.write(
                f"{max_steps},{self.reward['Red']},{self.reward['Blue']},"
                f"{self.agent_interfaces['Red'].agent.epsilon},"
                f"{self.agent_interfaces['Red'].agent.gamma}\n"
            )
        return done

    def get_agent_state(self, agent_name: str) -> Observation:
        """Gets agent's current state

        Parameters
        ----------
        agent_name : str

        Returns
        -------
        : Observations
            the agent's current state

        [한국어]
        에이전트의 현재 상태를 반환한다. 해당 에이전트의 INFO_DICT 범위만큼의 실제 상태를 가져온다.
        """
        return self.get_true_state(self.INFO_DICT[agent_name])

    def get_last_observation(self, agent: str) -> Observation:
        """Get the last observation for an agent

        Parameters
        ----------
        agent : str
            name of agent to get observation for

        Returns
        -------
        Observation
            agents last observation

        [한국어]
        에이전트의 마지막 관찰값을 반환한다. 관찰값이 없으면 빈 Observation을 반환한다.
        """
        if agent in self.observation:
            return self.observation[agent].get_combined_observation()
        return Observation()

    def get_action_space(self, agent: str) -> dict:
        """Gets the action space for a chosen agent

        Parameters
        ----------
        agent: str
            agent selected

        Returns
        -------
        : dict
            action space of the agent

        [한국어]
        지정한 에이전트의 행동 공간(Action Space)을 반환한다. 목록에 없는 에이전트면 ValueError를 던진다.
        """
        if agent in self.agent_interfaces:
            return self.agent_interfaces[agent].action_space.get_action_space()
        raise ValueError(f'Agent {agent} not in agent list {self.agent_interfaces.keys()}')

    def get_observation_space(self, agent: str) -> dict:
        """Gets the observation space for a chosen agent

        Parameters
        ----------
        agent: str
            agent selected

        Returns
        -------
        : dict
            agent observation space

        [한국어]
        지정한 에이전트의 관찰 공간(observation space)을 반환한다. 목록에 없는 에이전트면 ValueError를 던진다.
        """
        if agent in self.agent_interfaces:
            return self.agent_interfaces[agent].get_observation_space()
        raise ValueError(f'Agent {agent} not in agent list {self.agent_interfaces.values()}')

    def get_last_action(self, agent: str) -> Action:
        """Gets the observation space for a chosen agent

        Parameters
        ----------
        agent: str
            agent selected

        Returns
        -------
        : Action
            agent's last action

        [한국어]
        지정한 에이전트의 마지막 행동(Action)을 반환한다. 없으면 None을 반환한다.
        (원문 요약은 "관찰 공간"이라 적혀 있으나 실제로는 마지막 행동을 반환한다.)
        """
        return self.action[agent] if agent in self.action else None

    def _create_agents(self, scenario: Scenario, agent_classes: dict = None) -> Dict[str, AgentInterface]:
        agents = {}

        for agent_name in scenario.agents:
            agent_info = scenario.get_agent_info(agent_name)
            if agent_classes is not None and agent_name in agent_classes:
                agent_obj = agent_classes[agent_name]
            else:
                agent_obj = agent_info.agent_type
            agent_obj.np_random = self.np_random
            agent_obj.end_episode()
            agents[agent_name] = AgentInterface(
                agent_obj,
                agent_name,
                agent_info.actions,
                allowed_subnets=agent_info.allowed_subnets,
                scenario=scenario,
                active = agent_info.active,
                internal_only = agent_info.internal_only
            )
        return agents

    def _filter_obs(self, obs: Observation, agent_name=None):
        """Filter obs to contain only hosts/subnets in scenario network

        [한국어]
        관찰값(Observation)을 시나리오 네트워크에 속한 호스트/서브넷만 남도록 필터링한다.
        agent_name이 주어지면 그 에이전트의 허용 서브넷으로 범위를 좁힌다.
        """
        if self.scenario_generator.update_each_step:
            if agent_name is not None:
                allowed_subnets = self.agent_interfaces[agent_name].allowed_subnets
                subnets = [self.subnet_cidr_map[subnet] for subnet in allowed_subnets]
            else:
                subnets = list(self.subnet_cidr_map.values())

            obs.filter_addresses(
                ips=self.hostname_ip_map.values(), cidrs=subnets, include_localhost=False
            )
        return obs

    def replace_action_if_invalid(self, action: Action, agent: AgentInterface):
        """Returns action if the parameters in the action are in and true in the action set else return InvalidAction imbued with bug report.

        Parameters
        ----------
        action : Action
            action to test if valid
        agent : AgentInterface
            agent that is performing the action

        Returns
        -------
        action : Action
            Action parameter if valid, otherwise InvalidAction

        [한국어]
        행동의 종류와 파라미터가 에이전트의 행동 공간(Action Space)에 모두 유효하면 그 행동을
        그대로 반환하고, 그렇지 않으면 사유를 담은 InvalidAction으로 교체해 반환한다.
        (대개 아직 발견하지 못한 호스트·IP·포트 등 정보를 쓰려 할 때 유효하지 않게 된다.)
        """
        action_space = agent.action_space.get_action_space()

        if type(action) not in action_space['action']:
            message = f'Action {action} not in action space for agent {agent.agent_name}.'
            return InvalidAction(action=action, error=message)

        if not action_space['action'][type(action)]:
            message = f'Action {action} is not valid for agent {agent.agent_name} at the moment. This usually means it is trying to access a host it has not discovered yet.'
            return InvalidAction(action=action, error=message)

        # next for each parameter in the action
        # 다음으로 행동의 각 파라미터가 행동 공간 안에서 유효한지 확인한다.
        for parameter_name, parameter_value in action.get_params().items():
            if parameter_name not in action_space:
                continue
            
            if isinstance(parameter_value, list):
                for value in parameter_value:
                    if value not in action_space[parameter_name]:
                        message = f'Action {action} has parameter {parameter_name} that contains {value}. However, {value} is not in the action space for agent {agent.agent_name}.'
                        return InvalidAction(action=action, error=message)
            else:
                if parameter_value not in action_space[parameter_name]:
                    message = f'Action {action} has parameter {parameter_name} valued at {parameter_value}. However, {parameter_value} is not in the action space for agent {agent.agent_name}.'
                    return InvalidAction(action=action, error=message)

                if not action_space[parameter_name][parameter_value]:
                    message = f'Action {action} has parameter {parameter_name} valued at the invalid value of {parameter_value}. This usually means an agent is trying to utilise information it has not discovered yet such as an ip_address or port number.'
                    return InvalidAction(action=action, error=message)

        return action

    def get_reward_breakdown(self, agent:str):
        """Returns host scores from reward calculator

        [한국어]
        보상 계산기(RewardCalculator)가 산출한 호스트별 점수를 반환한다.
        """
        return self.agent_interfaces[agent].reward_calculator.host_scores

    def get_reward(self, agent):
        """Returns the team's reward

        [한국어]
        에이전트가 속한 팀의 보상을 반환한다. 어느 팀에도 속하지 않으면 ValueError를 던진다.
        """
        team = [team_name for team_name, agents in self.team_assignments.items() if agent in agents]
        if len(team) > 0:
            return self.reward[team[0]]
        raise ValueError(f"Agent {agent} not in any team {self.team_assignments}")
