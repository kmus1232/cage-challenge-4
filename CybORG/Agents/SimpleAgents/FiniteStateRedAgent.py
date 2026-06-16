from inspect import signature
from typing import Union, List, Dict
from pprint import pprint
from ipaddress import IPv4Address
from numpy import invert

from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Simulator.Actions.AbstractActions import DiscoverRemoteSystems, PrivilegeEscalate, Impact, DegradeServices, AggressiveServiceDiscovery, StealthServiceDiscovery, DiscoverDeception
from CybORG.Simulator.Actions.AbstractActions.ExploitRemoteService import PIDSelectiveExploitActionSelector, ExploitRemoteService
from CybORG.Simulator.Actions.ConcreteActions.RedSessionCheck import RedSessionCheck
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw
from CybORG.Simulator.Actions import Sleep, Action, InvalidAction


class FiniteStateRedAgent(BaseAgent):
    """
    A red agent that performs as a finite state automata, transitioning the hosts it is aware of between different states of knowledge.

    Throughout the episode, the hosts will transition between the 8 different states.
    This will mainly occur via the state transition matrices, depending on action success or failure.
    However, other external factors may affect the state, such as Blue removing a session from a host or the host being outside the agent's area of influence (their assigned subnets).

    [한국어]
    유한 상태 기계(finite state automata)로 동작하는 Red 에이전트(공격 측)다.
    자신이 인지한 호스트들을 서로 다른 "지식 상태(state of knowledge)" 사이에서 전이시킨다.

    에피소드 동안 각 호스트는 8개 상태 사이를 오간다. 전이는 주로 상태 전이 행렬
    (state transition matrix)을 통해, 행동(Action)의 성공/실패 여부에 따라 일어난다.
    다만 Blue 에이전트(방어 측)가 호스트의 세션(Session)을 제거하거나, 호스트가
    에이전트의 영향권(할당된 서브넷) 밖에 있는 등 외부 요인으로도 상태가 바뀔 수 있다.

    [상태 약어 정리] 각 상태는 호스트에 대한 Red의 지식·장악 수준을 나타낸다.
    K=Known(존재만 앎), S=Scanned(서비스까지 탐색), U=User(사용자 권한 장악),
    R=Root(루트 권한 장악), F=Failure(영향권 밖 등으로 행동 불가).
    뒤에 붙는 D는 Decoy-aware(디코이 존재를 인지한 상태)를 뜻한다. 예: KD, SD, UD, RD.
    """

    def __init__(self, name=None, np_random=None, agent_subnets=None):
        """Initialises the FSM red agent.

        Creates the variables to store internal knowledge for the agent.
        Sets the state transitions (basic) and host priorities (none), for the agent.

        Parameters
        ----------
        name : str
            agent name
        np_random : Tuple[np.random.Generator, Any]
            numpy random number generator
        agent_subnets : List[IPv4Subnet]
            list of subnet cidr bounds that this red agent can reach

        [한국어]
        FSM(유한 상태 기계) Red 에이전트를 초기화한다.

        에이전트가 내부 지식을 저장하는 변수들을 생성하고, 상태 전이(기본값)와
        호스트 우선순위(기본은 없음)를 설정한다.

        매개변수
        ----------
        name : str
            에이전트 이름
        np_random : Tuple[np.random.Generator, Any]
            numpy 난수 생성기
        agent_subnets : List[IPv4Subnet]
            이 Red 에이전트가 도달할 수 있는 서브넷 CIDR 범위 목록
        """
        super().__init__(name, np_random)
        self.step = 0  # 현재 스텝(step) 카운터
        self.action_params = None  # 행동(Action) 클래스별 생성자 매개변수 정보
        self.last_action = None  # 직전에 선택한 행동(진행 중 행동 추적에 사용)
        # [설명] host_states: IP를 키로, 해당 호스트의 지식 상태('state')와 hostname을 저장하는 내부 지식 사전.
        self.host_states = {}
        # [설명] host_service_decoy_status: 호스트별로 탐지한 디코이(Decoy) 프로세스의 PID 목록. 익스플로잇 대상에서 제외하는 데 쓴다.
        self.host_service_decoy_status = {}
        self.agent_subnets = agent_subnets  # 이 에이전트가 도달 가능한 서브넷 목록
        self.action_list = self.action_list()  # 상태 전이 행렬 열 순서와 일치하는 행동 목록

        self.print_action_output = False  # True면 매 턴 행동 요약을 터미널에 출력
        self.print_obs_output = False  # True면 관찰값과 host_states까지 출력(디버깅용)
        self.prioritise_servers = False  # True면 서버 호스트를 우선 선택

        self.host_states_priority_list = self.set_host_state_priority_list()
        self.state_transitions_success = self.state_transitions_success()
        self.state_transitions_failure = self.state_transitions_failure()
        self.state_transitions_probability = self.state_transitions_probability()    

    def get_action(self, observation: dict, action_space):
        """The choosing and returning of the action to be used for the current step.
        

        In order to make an appropriate choice, the observations from the previous action must be processed. 
        This is carried out through private functions, in the order listed below:
        
        1. `_host_state_transition(action, success)`
            - The host that was last acted on has its state changed based on the action success.
        2. `_process_new_observations(observation)` 
            - The details of the observation is then processed for newly discovered hosts and decoy discoveries.
        3. `_session_removal_state_change(observation)` 
            - The sessions are then checked to make sure none were lost in the last step, and changing their host states accordingly.

        An textual output is available if the print attributes are set to True (function `last_turn_summary`).


        The next action for the current step is then selected:

        4. If the previous action is still 'in progress' then Sleep is returned, as this action will not be used.
        5. `_choose_host_and_action(action_space, known_hosts)` 
            - A host is chosen; either randomly or based on host state priority.
            - An action on that host is then selected according to the `state_transition_probabilities` matrix.
        6. If the action chosen is `ExploitRemoteService_cc4`, then the selector that takes into account the detected decoys is chosen.
        7. The action is stored for reference and returned.


        Parameters
        ----------
        observation : dict
            The dictionary holding the observations made by the agent from the previous action
        action_space : dict
            The restricted space that the agent knows about and can act on, given by the environment.

        [한국어]
        현재 스텝에서 사용할 행동(Action)을 선택해 반환한다.

        적절한 선택을 하려면 먼저 직전 행동의 관찰값(Observation)을 처리해야 한다.
        아래 순서대로 비공개(private) 함수를 호출해 처리한다.

        1. `_host_state_transition(action, success)`
            - 직전에 행동 대상이 된 호스트의 상태를 행동 성공 여부에 따라 변경한다.
        2. `_process_new_observations(observation)`
            - 관찰값을 분석해 새로 발견한 호스트와 디코이(Decoy)를 반영한다.
        3. `_session_removal_state_change(observation)`
            - 직전 스텝에서 세션(Session)을 잃은 호스트가 없는지 확인하고, 있으면 상태를 바꾼다.

        print 속성이 True면 텍스트 요약을 출력한다(`last_turn_summary` 함수).

        그다음 이번 스텝의 행동을 선택한다.

        4. 직전 행동이 아직 '진행 중'이면 Sleep을 반환한다(이번 스텝에는 새 행동을 쓰지 않음).
        5. `_choose_host_and_action(action_space, known_hosts)`
            - 호스트를 하나 고른다(무작위 또는 호스트 상태 우선순위 기반).
            - 그 호스트에 대한 행동을 `state_transition_probabilities` 행렬에 따라 선택한다.
        6. 선택된 행동이 `ExploitRemoteService_cc4`라면, 탐지한 디코이를 고려하는 선택기를 적용한다.
        7. 행동을 참조용으로 저장한 뒤 반환한다.

        매개변수
        ----------
        observation : dict
            직전 행동에 대해 에이전트가 받은 관찰값을 담은 사전
        action_space : dict
            환경이 제공하는, 에이전트가 알고 행동할 수 있는 제한된 행동 공간(Action Space)
         """
     
        action = None
        success = None

        # 관찰값에서 직전 행동의 성공 여부(success)와 행동(action) 정보를 꺼낸다.
        if 'success' in observation.keys():
            success = observation.pop('success')

        if 'action' in observation.keys():
            action = observation.pop('action')

        # 위 3개 함수로 내부 지식(host_states 등)을 최신 관찰값에 맞게 갱신한다.
        self._host_state_transition(action, success)
        self._process_new_observations(observation)
        self._session_removal_state_change(observation)

        if self.print_action_output:
            self.last_turn_summary(observation, action, success)

        # 직전 행동이 진행 중('IN_PROGRESS')이면 새 행동을 쓰지 않고 Sleep을 반환한다.
        if success.name == 'IN_PROGRESS':
            self.step += 1
            return Sleep()
        else:
            # 상태가 'F'(영향권 밖 등 행동 불가)인 호스트를 제외한 알려진 호스트 목록.
            known_hosts = [h for h in self.host_states.keys() if not self.host_states[h]['state'] == 'F']
            chosen_host, action = self._choose_host_and_action(action_space, known_hosts)

            # [설명] 익스플로잇 행동이고 대상 호스트에서 디코이를 탐지했다면,
            # 해당 디코이 PID를 제외하는 선택기를 붙여 미끼를 건드리지 않도록 한다.
            if isinstance(action, ExploitRemoteService) and chosen_host in list(self.host_service_decoy_status.keys()):
                action.exploit_action_selector = PIDSelectiveExploitActionSelector(excluded_pids=self.host_service_decoy_status[chosen_host])

            self.step += 1
            self.last_action = action  # 참조용으로 이번 행동을 저장
            return action

    def _host_state_transition(self, action: Action, success):
        """State transition depending on the last action and its success.

        [한국어]
        직전 행동과 그 성공 여부에 따라 대상 호스트의 상태를 전이시킨다.
        """
        if not action == None and not success.name == 'IN_PROGRESS':
            action_index = None
            # 행동 객체가 action_list 중 어느 클래스에 해당하는지 찾는다(열 인덱스 결정용).
            action_type = [A for A in self.action_list if isinstance(action, A)]

            if len(action_type) == 1:
                action_index = self.action_list.index(action_type[0])
                action_params = signature(action_type[0]).parameters

                # [설명] 행동의 매개변수 종류(ip_address / hostname / subnet)에 따라
                # 상태를 전이시킬 대상 호스트의 IP 목록(host_ips)을 다르게 구성한다.
                host_ips = []
                if 'ip_address' in action_params:
                    host_ips.append(str(action.ip_address))
                elif 'hostname' in action_params:
                    for ip, host_dict in self.host_states.items():
                        if host_dict['hostname'] == action.hostname:
                            host_ips.append(ip)
                            break
                elif 'subnet' in action_params:
                    # subnet 단위 행동은 그 서브넷에 속한 모든 호스트가 전이 대상이 된다.
                    for ip in self.host_states.keys():
                        if IPv4Address(ip) in action.subnet:
                            host_ips.append(ip)

                for host_ip in host_ips:
                    if host_ip in self.host_states.keys():
                        curr_state = self.host_states[host_ip]['state']
                        next_state = None
                        # 성공이면 성공 전이 행렬, 실패면 실패 전이 행렬에서 다음 상태를 읽는다.
                        if success.value == 1:
                            next_state = self.state_transitions_success[curr_state][action_index]
                        else:
                            next_state = self.state_transitions_failure[curr_state][action_index]

                        # [설명] 다음 상태가 'U'(사용자 권한 장악)라도, 해당 호스트가
                        # 에이전트 영향권(agent_subnets) 밖이면 'F'(행동 불가)로 강등한다.
                        if next_state == 'U':
                            next_state = 'F'
                            for a_subnet in self.agent_subnets:
                                if IPv4Address(host_ip) in a_subnet:
                                    next_state = 'U'

                        if next_state == None:
                            # i.e. if something happens that causes the host to be in a state where they cannot perform that action
                            # (e.g. session removed during action duration, or error), then just use their previous state.
                            # [한국어] 즉, 해당 행동을 수행할 수 없는 상태가 되는 일이 생기면
                            # (예: 행동 진행 중 세션 제거, 또는 오류) 이전 상태를 그대로 유지한다.
                            next_state = curr_state

                        self.host_states[host_ip]['state'] = next_state

    def _session_removal_state_change(self, observation):
        """The changing of state of hosts, where its session has been removed (by Blue).

        [한국어]
        Blue 에이전트(방어 측)에 의해 세션(Session)이 제거된 호스트의 상태를 변경한다.
        """
        # [설명] 먼저 권한을 장악했던(상태에 'U' 또는 'R' 포함) 호스트를 후보로 모은다.
        # 이번 관찰값에 세션이 여전히 보이는 호스트는 후보에서 제외하고,
        # 끝까지 남은 호스트는 세션을 잃은 것으로 보아 상태를 'KD'로 되돌린다.
        removed_hosts = []

        for ip, hs in self.host_states.items():
            if 'U' in hs['state'] or 'R' in hs['state']:
                removed_hosts.append(ip)

        for host, obs in observation.items():
            if host == 'message':
                continue

            # 세션이 관찰된 호스트는 세션이 유지된 것이므로 제거 후보에서 뺀다.
            if 'Sessions' in obs.keys():
                for i, sess in enumerate(obs['Sessions']):
                    host_ip = str(obs['Interface'][0]['ip_address'])
                    if host_ip in removed_hosts:
                        removed_hosts.remove(host_ip)

        # 세션을 잃은 것으로 판정된 호스트의 상태를 'KD'(존재만 알고 디코이 인지)로 변경.
        for ip in removed_hosts:
            self.host_states[ip]['state'] = 'KD'

    def _process_new_observations(self, observation: dict):
        """The finding of new hosts in the past observation, and the discovery of any decoys.

        [한국어]
        직전 관찰값에서 새 호스트를 찾아내고, 디코이(Decoy)가 있으면 발견해 기록한다.
        """
        # Update knowledge of new hosts and decoys
        # 새 호스트와 디코이에 대한 지식을 갱신한다.
        for host_id, host_details in observation.items():
            hostname = None
            ip = None

            if host_id == 'message':
                continue

            # Identify hostname in obs
            # 관찰값에서 hostname을 식별한다.
            if '_' in host_id:
                hostname = host_id
            elif 'System info' in host_details:
                if 'Hostname' in host_details['System info']:
                    hostname = host_details['System info']['Hostname']

            # Identify ip in obs
            # 관찰값에서 IP를 식별한다.
            if '.' in host_id:
                ip = host_id
            elif 'Interface' in host_details:
                ip = str(host_details['Interface'][0]['ip_address'])

            # If hostname already in host_states, identify ip
            # hostname은 이미 알지만 IP를 모를 때, 기존 host_states에서 IP를 찾는다.
            if ip == None and not hostname == None:
                for h_ip, h_details in self.host_states.items():
                    if h_details['hostname'] == hostname:
                        ip = h_ip
                        break

            # set new host starting state
            # 새 호스트의 시작 상태를 설정한다.
            # [설명] 첫 스텝(step 0)에 보이는 호스트는 에이전트가 이미 장악한 것으로 보아 'U'(사용자 권한),
            # 그 이후 새로 발견되는 호스트는 'K'(존재만 앎)로 시작한다.
            host_state = {}
            if self.step == 0:
                host_state['state'] = 'U'
                # agent_subnets가 지정되지 않았다면, 첫 호스트의 인터페이스에서 서브넷을 추론한다.
                if self.agent_subnets == None:
                    for sub_dict in host_details['Interface']:
                        if 'Subnet' in sub_dict.keys():
                            self.agent_subnets = [sub_dict['Subnet']]
                            break
            else:
                host_state['state'] = 'K'

            # if new ip info
            # 처음 보는 IP라면 host_states에 새로 등록한다.
            if not ip in self.host_states.keys():
                self.host_states[ip] = host_state
                self.host_states[ip]['hostname'] = hostname

            # if new hostname info
            # 기존 IP에 hostname이 비어 있었다면 새로 알아낸 hostname을 채운다.
            if not ip == None and not hostname == None:
                if self.host_states[ip]['hostname'] == None:
                    self.host_states[ip]['hostname'] = hostname

            # if new decoy info
            # [설명] 프로세스 속성에 'decoy'가 있으면 디코이로 보고, 그 PID를
            # host_service_decoy_status에 기록한다(이후 익스플로잇 대상에서 제외).
            if 'Processes' in host_details.keys():
                for process in host_details['Processes']:
                    if 'Properties' in process and 'PID' in process:
                        if 'decoy' in process['Properties']:
                            if host_id in self.host_service_decoy_status:
                                self.host_service_decoy_status[host_id].append(process['PID'])
                            else:
                                self.host_service_decoy_status[host_id] = [process['PID']]
                        
    def _choose_host(self, host_options: List[str]):
        """A valid host is selected and returned

        [한국어]
        유효한 호스트를 하나 골라 반환한다.
        """
        # [설명] 우선순위 리스트(host_states_priority_list)가 없으면 모든 호스트를 후보로 둔다.
        # 있으면 먼저 "어떤 상태를 공략할지"를 상태별 우선순위 가중치에 비례한 확률로 뽑고,
        # 그 상태에 해당하는 호스트들만 후보로 좁힌다.
        if self.host_states_priority_list is None:
            state_host_options = host_options
        else:
            base = 100
            available_states = {}

            # 현재 후보 호스트들이 가진 상태와 그 우선순위 가중치를 모은다.
            for h_opt in host_options:
                if not self.host_states[h_opt]['state'] in available_states.keys():
                    available_states[self.host_states[h_opt]['state']] = self.host_states_priority_list[self.host_states[h_opt]['state']]
                if len(available_states) == len(self.host_states_priority_list):
                    break

            # 가중치 합이 양수면 비례 확률로 상태를 뽑고, 0이면 균등하게 뽑는다.
            if sum(available_states.values()) > 0:
                p_multiplier = 1/((sum(available_states.values()) / base))
                probs = [(p/base)*p_multiplier for p in available_states.values()]
                chosen_state = self.np_random.choice(list(available_states.keys()), p=probs)
            else:
                chosen_state = self.np_random.choice(list(available_states.keys()))

            state_host_options = [h for h in host_options if self.host_states[h]['state'] == chosen_state]

        # [설명] 서버 우선 모드면, 후보 중 hostname에 'server'가 포함된 호스트를 75% 확률로 고른다.
        if self.prioritise_servers and len(state_host_options) > 1:
            server_state_host_options = [h for h in state_host_options if self.host_states[h]['hostname'] is not None and 'server' in self.host_states[h]['hostname']]
            if len(server_state_host_options) > 0:
                i = self.np_random.random()
                if i <= 0.75:
                    chosen_host = self.np_random.choice(server_state_host_options)
                else:
                    #pick other host type
                    # 나머지 25% 확률로는 서버가 아닌 호스트를 고른다(서버만 있으면 그대로 서버 선택).
                    if not len(server_state_host_options) == len(state_host_options):
                        non_server_state_host_options = [h for h in state_host_options if not h in server_state_host_options]
                        chosen_host = self.np_random.choice(non_server_state_host_options)
                    else:
                        chosen_host = self.np_random.choice(server_state_host_options)
            else:
                chosen_host = self.np_random.choice(state_host_options)
        else:
            chosen_host = self.np_random.choice(state_host_options)

        return chosen_host
    
    
    def _choose_host_and_action(self, action_space: dict, host_options: List[str]):
        """The selection of a valid host and action to execute this step.

        [한국어]
        이번 스텝에 실행할 유효한 호스트와 행동(Action)을 선택한다.
        """
        chosen_host = self._choose_host(host_options)
        if chosen_host == None:
            return Sleep()

        # [설명] 선택한 호스트의 현재 상태에 대응하는 확률 행렬 행에서,
        # 확률이 None이 아닌(=수행 가능한) 행동들만 {행동: 확률} 형태로 뽑는다.
        host_action_options = {self.action_list[i]: prob for i, prob in enumerate(self.state_transitions_probability[self.host_states[chosen_host]['state']]) if not prob == None}

        invalid_actions = []
        while True:
            # 행동 공간에서 활성(v=True)이고, 유효하지 않다고 판정되지 않았으며,
            # 현재 상태에서 수행 가능한 행동들만 후보로 추린다.
            options = [i for i, v in action_space['action'].items() if v and i not in invalid_actions and i in list(host_action_options.keys())]
            if len(options) > 0:
                probabilities = []
                for opt in options:
                    probabilities.append(host_action_options[opt])
                action_class = self.np_random.choice(options, p=probabilities)
            else:
                # 이 호스트로는 가능한 행동이 없으면, 그 호스트를 빼고 다시 시도한다.
                new_options = host_options[:]
                new_options.pop(chosen_host)
                return self._choose_action(action_space, new_options)
            # select random options
            # 선택한 행동의 매개변수를 채운다(hostname/ip는 대상 호스트 값, 나머지는 무작위).
            action_params = {}
            for param_name in self.action_params[action_class]:
                options = [i for i, v in action_space[param_name].items() if v]
                if param_name == 'hostname':
                    if not self.host_states[chosen_host]['hostname'] == None:
                        action_params[param_name] = self.host_states[chosen_host]['hostname']
                    else:
                        # hostname을 모르면 이 행동은 수행 불가로 표시하고 다시 고른다.
                        invalid_actions.append(action_class)
                        action_params = None
                        break
                elif param_name == 'ip address' or param_name == "ip_address":
                    action_params[param_name] = IPv4Address(chosen_host)
                elif len(options) > 0:
                    action_params[param_name] = self.np_random.choice(options)
                else:
                    # 채울 수 있는 유효한 매개변수 값이 없으면 수행 불가로 표시하고 다시 고른다.
                    invalid_actions.append(action_class)
                    action_params = None
                    break
            if action_params is not None:
                return chosen_host, action_class(**action_params)
    
    def train(self, results):
        pass

    def end_episode(self): 
        pass

    def set_initial_values(self, action_space, observation):
        """The action parameter values in the action space are sanitised for internal use.

        Parameters
        ----------
        action_space : dict
        observation : dict

        [한국어]
        행동 공간(Action Space)에 담긴 행동별 매개변수 정보를 내부에서 쓰기 좋게 정리한다.

        매개변수
        ----------
        action_space : dict
        observation : dict
        """
        if type(action_space) is dict:
            self.action_params = {action_class: signature(action_class).parameters for action_class in action_space['action'].keys()}

    def last_turn_summary(self, observation: dict, action: str, success):
        """Prints action name, parameters, success and sometimes observation and host states.

        If `self.print_action_output` is True, the function will run and the observed action and its success will be outputted to the terminal.

        If `self.print_obs_output` is True, additionally the observation and internal `host_states` dictionaries will be outputted. This should only be True for debugging.

        Parameters
        ----------
        observation : dict
            the observation that the agent just received about its previous action
        action : str
            the previous action that was taken
        success : Union[bool, CyEnums.TrinaryEnum]
            the success of the previous action

        [한국어]
        행동 이름·매개변수·성공 여부를, 경우에 따라 관찰값과 호스트 상태까지 출력한다.

        `self.print_action_output`가 True면 직전 행동과 그 성공 여부를 터미널에 출력한다.
        `self.print_obs_output`가 True면 추가로 관찰값과 내부 `host_states` 사전까지
        출력한다(디버깅 용도로만 True로 둘 것).

        매개변수
        ----------
        observation : dict
            직전 행동에 대해 에이전트가 방금 받은 관찰값
        action : str
            직전에 수행한 행동
        success : Union[bool, CyEnums.TrinaryEnum]
            직전 행동의 성공 여부
        """

        action_str = None
        if not action == None:
            action_str = str(action)
        elif success.name == 'IN_PROGRESS':
            action_str = str(self.last_action)
        else: 
            action_str = "Initial Observation"

        print(f'\n** Turn {self.step} for {self.name} **')
        print(f"Action: {action_str}")
        print("Action Success: " + str(success))

        if self.print_obs_output:
            print("\nObservation:")
            pprint(observation)
            print("Host States:")
            pprint(self.host_states)
        
        if isinstance(observation.get('action'), InvalidAction):
            pprint(observation['action'].error)
    
    def action_list(self):
        """The possible actions that can be performed by the agent, in the order of the columns of the state transition matrices.

        Returns
        -------
        actions : List[Action]
            List of the 9 actions that a red agent can perform in CC4

        [한국어]
        에이전트가 수행 가능한 행동(Action) 목록을, 상태 전이 행렬의 열 순서와 똑같이 나열한다.

        반환값
        -------
        actions : List[Action]
            CC4에서 Red 에이전트가 수행할 수 있는 9개 행동의 목록
        """
        actions = [
            DiscoverRemoteSystems,          #0  원격 시스템 탐색
            AggressiveServiceDiscovery,     #1  적극적 서비스 탐색
            StealthServiceDiscovery,        #2  은밀한 서비스 탐색
            DiscoverDeception,              #3  기만(디코이) 탐지
            ExploitRemoteService,       #4      익스플로잇(원격 서비스 공격)
            PrivilegeEscalate,              #5  권한 상승
            Impact,                         #6  Impact(타격)
            DegradeServices,                #7  서비스 성능 저하
            Withdraw                        #8  Withdraw(철수)
        ]
        return actions

    def state_transitions_success(self):
        """The state transition matrix for a successful action on a host.
        
        There is a row for each of the host states: K, KD, S, SD, U, UD, R, RD.
        Then there is a column for each of the actions, in the order of the `action_list`.

        All column 0 must have transition state as all hosts in subnet are transitioned

        ??? example
            ```
            map = {
                'K'  : ['KD', 'S',  'S',  None, None, None, None, None, None],
                'KD' : ['KD', 'SD', 'SD',  None, None, None, None, None, None],
                'S'  : ['SD', None, None, 'S' , 'U' , None, None, None, None],
                'SD' : ['SD', None, None, 'SD', 'UD', None, None, None, None],
                'U'  : ['UD', None, None, None, None, 'R' , None, None, 'S' ],
                'UD' : ['UD', None, None, None, None, 'RD', None, None, 'SD'],
                'R'  : ['RD', None, None, None, None, None, 'R' , 'R' , 'S' ],
                'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'SD'],
                'F'  : ['F',  None, None, None, None, None, None, None, None],
            }
            ```

        Returns
        -------
        map : Dict[str, List[float]]
        """
        map = {
            'K'  : ['KD', 'S',  'S',  None, None, None, None, None, None],
            'KD' : ['KD', 'SD', 'SD',  None, None, None, None, None, None],
            'S'  : ['SD', None, None, 'S' , 'U' , None, None, None, None],
            'SD' : ['SD', None, None, 'SD', 'UD', None, None, None, None],
            'U'  : ['UD', None, None, None, None, 'R' , None, None, 'S' ],
            'UD' : ['UD', None, None, None, None, 'RD', None, None, 'SD'],
            'R'  : ['RD', None, None, None, None, None, 'R' , 'R' , 'S' ],
            'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'SD'],
            'F'  : ['F',  None, None, None, None, None, None, None, None],
        }
        return map

    def state_transitions_failure(self):
        """The state transition matrix for an unsuccessful action on a host.

        There is a row for each of the host states: K, KD, S, SD, U, UD, R, RD.
        Then there is a column for each of the actions, in the order of the `action_list`.
        
        All column 0 must have transition state as all hosts in subnet are transitioned

        ??? example
            ```
            map = {
                'K'  : ['K' , 'K' , 'K' , None, None, None, None, None, None],
                'KD' : ['KD', 'KD', 'KD', None, None, None, None, None, None],
                'S'  : ['S' , None, None, 'S' , 'S' , None, None, None, None],
                'SD' : ['SD', None, None, 'SD', 'SD', None, None, None, None],
                'U'  : ['U' , None, None, None, None, 'U' , None, None, 'U' ],
                'UD' : ['UD', None, None, None, None, 'UD', None, None, 'UD'],
                'R'  : ['R' , None, None, None, None, None, 'R' , 'R' , 'R' ],
                'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'RD'],
                'F'  : ['F',  None, None, None, None, None, None, None, None],
            }
            ```

        Returns
        -------
        map : Dict[str, List[float]]
        """
        map = {
            'K'  : ['K' , 'K' , 'K' , None, None, None, None, None, None],
            'KD' : ['KD', 'KD', 'KD', None, None, None, None, None, None],
            'S'  : ['S' , None, None, 'S' , 'S' , None, None, None, None],
            'SD' : ['SD', None, None, 'SD', 'SD', None, None, None, None],
            'U'  : ['U' , None, None, None, None, 'U' , None, None, 'U' ],
            'UD' : ['UD', None, None, None, None, 'UD', None, None, 'UD'],
            'R'  : ['R' , None, None, None, None, None, 'R' , 'R' , 'R' ],
            'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'RD'],
            'F'  : ['F',  None, None, None, None, None, None, None, None],
        }
        return map

    def set_host_state_priority_list(self):
        """ Abstract function for child classes to overwrite with a host state priority list.
        
        Each dictionary value must be an integer or float from 0 to 100, with the total sum of values equaling 100.

        ??? example 
            ```
            host_state_priority_list = {
                'K':12.5, 'KD':12.5, 
                'S':12.5, 'SD':12.5, 
                'U':12.5, 'UD':12.5, 
                'R':12.5, 'RD':12.5}
            ```

        Returns
        -------
        host_state_priority_list : None
            when used in variant child classes, a dict would be returned.
        """
        return None

    def state_transitions_probability(self):
        """Returns a state transitions probability matrix.

        There is a row for each of the host states: K, KD, S, SD, U, UD, R, RD.
        Then there is a column for each of the actions, in the order of the `action_list`.

        ??? example
            ```
            map = {
                'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
                'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
                'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
                'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
                'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
                'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
                'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
                'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
            }
            ```

        Returns
        -------
        matrix : Dict[str, List[float]]
        """

        map = {
            'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
            'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
            'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
            'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
            'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
            'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
            'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
            'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
        }
        return map
