# Copyright DST Group. Licensed under the MIT license.
import queue
from threading import Thread, Event
import warnings
from typing import Any, Tuple, Union

import gym
import numpy as np
import pygame
from gym.utils import seeding

from CybORG.Simulator.SimulationController import SimulationController
from CybORG.Shared import Observation, Results, CybORGLogger
from CybORG.Shared.Enums import DecoyType
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator
from CybORG.Simulator.Actions import DiscoverNetworkServices, DiscoverRemoteSystems, ExploitRemoteService, \
    InvalidAction, \
    Sleep, PrivilegeEscalate, Impact, Remove, Restore, RemoveOtherSessions
from CybORG.Simulator.Actions.ConcreteActions.ActivateTrojan import ActivateTrojan
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTraffic, AllowTraffic
from CybORG.Simulator.Actions.ConcreteActions.ExploitActions.ExploitAction import ExploitAction
# from CybORG.Simulator.Scenarios import DroneSwarmScenarioGenerator, FileReaderScenarioGenerator
from CybORG.Tests.utils import CustomGenerator
# from CybORG.render.pygame_user_interface import SimulationGUI
# from CybORG.render.renderer import Renderer


class CybORG(CybORGLogger):
    """The main interface for the Cyber Operations Research Gym.

    The primary purpose of this class is to provide a unified interface for the CybORG simulation and emulation
    environments. The user chooses which of these modes to run when instantiating the class and CybORG initialises
    the appropriate environment controller.

    This class also provides the external facing API for reinforcement learning agents, before passing these commands
    to the environment controller. The API is intended to closely resemble that of OpenAI Gym, but is also inspired by PettingZoo for MultiAgent aspects.

    Attributes
    ----------
    scenario_generator: ScenarioGenerator
        ScenarioGenerator object that creates scenarios.
    environment: str
        The environment to use. CybORG currently only supports 'sim' (default='sim').
    env_config: dict
        Configuration keyword arguments for environment controller
        (See relevant Controller class for details), (default=None).
    agents: dict
        Defines the agent that selects the default action to be performed if the external agent does not pick an action
        If None agents will be loaded from description in scenario file (default=None).

    [한국어]
    CybORG(Cyber Operations Research Gym)의 메인 인터페이스 클래스다.
    이 클래스의 핵심 역할은 CybORG의 시뮬레이션/에뮬레이션 환경에 대한 단일
    창구를 제공하는 것이다. 사용자는 클래스를 생성할 때 어떤 모드로 실행할지
    고르고, CybORG는 그에 맞는 환경 컨트롤러를 초기화한다.

    또한 이 클래스는 강화학습 에이전트를 위한 외부 공개 API를 제공하며, 받은
    명령을 환경 컨트롤러로 전달한다. API는 OpenAI Gym과 거의 유사하게
    설계되었고, 다중 에이전트(Multi-Agent) 부분은 PettingZoo에서 영감을 받았다.

    Attributes(속성)
    - scenario_generator: 시나리오를 생성하는 ScenarioGenerator 객체.
    - environment: 사용할 환경. CybORG는 현재 'sim'만 지원한다(기본값 'sim').
    - env_config: 환경 컨트롤러에 넘기는 설정 키워드 인자(기본값 None).
    - agents: 외부 에이전트가 행동(Action)을 고르지 않을 때 기본 행동을 선택할
      에이전트를 정의한다. None이면 시나리오 파일의 기술(description)에서 로드한다.
    """
    supported_envs = ['sim']

    def __init__(self,
                 scenario_generator: ScenarioGenerator,
                 agents: dict = None,
                 seed: Union[int, CustomGenerator] = None):
        """Instantiates the CybORG class.

        Parameters
        ----------
        scenario_generator: ScenarioGenerator
            ScenarioGenerator object that creates scenarios.
        agents: dict, optional
            Defines the agent that selects the default action to be performed if the external agent does not pick an action
            If None agents will be loaded from description in scenario file (default=None).
        seed : Union[int, CustomGenerator]
            optional seed for random number generator

        [한국어]
        CybORG 클래스를 생성(인스턴스화)한다.

        Parameters(매개변수)
        - scenario_generator: 시나리오를 생성하는 ScenarioGenerator 객체.
        - agents: 외부 에이전트가 행동을 고르지 않을 때 기본 행동을 선택할
          에이전트를 정의한다. None이면 시나리오 파일에서 로드한다(기본값 None).
        - seed: 난수 생성기에 쓸 선택적 시드.
        """
        # [설명] scenario_generator는 반드시 ScenarioGenerator의 하위 클래스여야 한다.
        assert issubclass(type(scenario_generator),
                          ScenarioGenerator), f'Scenario generator object of type {type(scenario_generator)} must be a subclass of ScenarioGenerator'
        self.scenario_generator = scenario_generator
        self._log_info(f"Using scenario generator {str(scenario_generator)}")
        # [설명] seed가 None이거나 정수면 난수 생성기(np_random)를 새로 만들고,
        # 이미 CustomGenerator 객체로 넘어왔으면 그것을 그대로 사용한다.
        if seed is None or isinstance(seed, int):
            self.np_random, seed = seeding.np_random(seed)
        else:
            self.np_random = seed
        self.environment_controller = SimulationController(self.scenario_generator, agents, self.np_random)

        # # CC4: GUI not implemented for CC4, disable by default
        # self._disable_gui = True

        # self.renderer: Renderer = None
        # self.gui: Thread = None
        # self.gui_actions_queue: queue.Queue = None

        # # used to signal termination to the threads
        # self.stop_event: Event = None if self._disable_gui else Event()

    # def _gui(f):
    #     def _impl(self, *args, **kwargs):
    #         if not self._disable_gui:
    #             f(self, *args, **kwargs)
    #     return _impl

    def parallel_step(self, actions: dict = None, messages: dict = None, skip_valid_action_check: bool = False) -> Tuple[dict, dict, dict, dict]:
        """Performs a step in CybORG accepting multiple external agent inputs.
            
            Used by multiagent scenarios such as CAGE Challenge 3 and CAGE Challenge 4. Actions conceptually occur simultaneously, but in reality occur sequentially according to priority order.

                Parameters
                ----------
                actions: dict
                    the actions to perform
                skip_valid_action_check: bool
                    a flag to diable the valid action check
                Returns
                -------
                tuple
                    the result of agent performing the action

                [한국어]
                여러 외부 에이전트의 입력을 받아 CybORG에서 한 스텝(step)을 진행한다.

                CAGE Challenge 3, CAGE Challenge 4 같은 다중 에이전트 시나리오에서
                사용한다. 행동(Action)들은 개념적으로 동시에 일어나지만, 실제로는
                우선순위(priority order)에 따라 순차적으로 처리된다.

                Parameters(매개변수)
                - actions: 수행할 행동들.
                - skip_valid_action_check: 유효 행동 검사를 끄는 플래그.

                Returns(반환값)
                - tuple: 에이전트가 행동을 수행한 결과.
                """
        if actions is not None and len(actions) > 0:
            agents = list(actions.keys())
        else:
            agents = []
        # [설명] 넘어온 actions가 컨트롤러 내부의 action 객체와 동일한 참조이면,
        # 시뮬레이션 내부에서 변형되어 이전 스텝의 행동이 섞일 수 있으므로 경고한다.
        if actions is self.environment_controller.action:
            warnings.warn("Reuse of the actions input. This variable is altered inside the simulation "
                          "and may contain actions from previous steps")
        self.environment_controller.step(actions, skip_valid_action_check)
        self.environment_controller.send_messages(messages)
        # [설명] 입력으로 받은 에이전트와 현재 활성(active) 에이전트를 합집합으로 모은다.
        agents = set(agents + self.active_agents)
        return {agent: self.get_observation(agent) for agent in agents}, \
               {agent: self.environment_controller.get_reward(agent) for agent in agents}, \
               {agent: self.environment_controller.done for agent in agents}, {}

    def step(self, agent: str = None, action=None, messages: dict = None,
         skip_valid_action_check: bool = False) -> Results:
        """Performs a step in CybORG for the given agent.
        Enables compatibility with older versions of CybORG including CAGE Challenge 1 and CAGE Challenge 2

        Parameters
        ----------
        agent: str, optional
            the agent to perform step for (default=None)
        action: Action
            the action to perform
        skip_valid_action_check: bool
            a flag to diable the valid action check
        Returns
        -------
        Results
            the result of agent performing the action

        [한국어]
        지정한 에이전트에 대해 CybORG에서 한 스텝(step)을 진행한다.
        CAGE Challenge 1, CAGE Challenge 2를 포함한 구버전 CybORG와의 호환성을
        보장한다.

        Parameters(매개변수)
        - agent: 스텝을 수행할 에이전트(기본값 None).
        - action: 수행할 행동(Action).
        - skip_valid_action_check: 유효 행동 검사를 끄는 플래그.

        Returns(반환값)
        - Results: 에이전트가 행동을 수행한 결과.
        """
        # [설명] action이나 agent 중 하나라도 없으면 빈 행동 딕셔너리로 처리한다.
        if action is None or agent is None:
            action = {}
        else:
            action = {agent: action}
        self.environment_controller.step(action, skip_valid_action_check)
        self.environment_controller.send_messages(messages)
        if agent is None:
            result = Results(observation=Observation().data)
        else:
            # [설명] 해당 에이전트의 보상(reward)을 모두 더해 소수점 첫째 자리로 반올림한다.
            reward = round(sum(self.environment_controller.get_reward(agent).values()), 1)
            action_space = self.environment_controller.agent_interfaces[agent].action_space.get_action_space()
            result = Results(
                observation=self.get_observation(agent),
                done=self.environment_controller.done,
                reward=reward,
                action_space=action_space,
                action=self.environment_controller.action[agent]
            )
        return result

    def start(self, steps: int, log_file=None, verbose=False) -> bool:
        """Start CybORG and run for a specified number of steps.

        Parameters
        ----------
        steps: int
            the number of steps to run for
        log_file: File, optional
            a file to write results to (default=None)

        Returns
        -------
        bool
            whether goal was reached or not

        [한국어]
        CybORG를 시작해 지정한 스텝(step) 수만큼 실행한다.

        Parameters(매개변수)
        - steps: 실행할 스텝 수.
        - log_file: 결과를 기록할 파일(기본값 None).

        Returns(반환값)
        - bool: 목표(goal) 도달 여부.
        """
        return self.environment_controller.start(steps, log_file, verbose)

    def get_true_state(self, info: dict) -> dict:
        """Create's a dictionary containing the requested information from the state.

        Intended to be used for debugging and evaluation purposes. Agents should not have visibility of the unfiltered state.
        Info dictionary should have hostnames as keys. Each host is passed a dictionary whose keys define the subcomponents to pull out and whose values specify which attributes. For example:
            {'HostnameA': {'Interfaces':'ip_address','Services':'Femitter'},
             'HostnameB': {'Interfaces':'All', 'Files': 'All', 'Sessions':'All'},
             'HostnameC': {'User info': 'All', 'System info': 'All'}
             }

        Parameters
        ----------
        info: dict


        Returns
        -------
        Results
            The information requested.

        [한국어]
        상태(state)에서 요청한 정보만 뽑아 딕셔너리로 만들어 반환한다.

        디버깅·평가용이다. 에이전트는 필터링되지 않은 원본 상태를 볼 수 없어야 한다.
        info 딕셔너리는 호스트명(hostname)을 키로 갖는다. 각 호스트에는 뽑아낼
        하위 구성요소(키)와 그중 어떤 속성(값)을 가져올지 지정하는 딕셔너리를
        넘긴다. 예시는 영어 docstring의 예시 블록을 참고한다.

        Parameters(매개변수)
        - info: 위 형식의 요청 딕셔너리.

        Returns(반환값)
        - Results: 요청한 정보.
        """
        return self.environment_controller.get_true_state(info).data

    def get_agent_state(self, agent_name) -> dict:
        """Get the initial observation of the specified agent.

        Parameters
        ----------
        agent_name : str
            The agent to get the initial observation for.
            Set as 'True' to get the true-state.

        Returns
        -------
        : dict
            The initial observation of the specified agent.

        [한국어]
        지정한 에이전트의 초기 관찰값(Observation)을 가져온다.

        Parameters(매개변수)
        - agent_name: 초기 관찰값을 가져올 에이전트. 'True'로 두면 참 상태
          (true-state)를 가져온다.

        Returns(반환값)
        - dict: 지정한 에이전트의 초기 관찰값.
        """
        return self.environment_controller.get_agent_state(agent_name).data

    def reset(self, agent: str = None, seed: int = None) -> Results:
        """Resets CybORG and gets initial observation and action-space for the specified agent.

        Note
        ----
        This method is a critical part of the OpenAI Gym API.

        Parameters
        ----------
        agent: str, optional
            The agent to get the initial observation for.
            If None will return the initial true-state (default=None).

        Returns
        -------
        Results
            The initial observation and actions of an agent.

        [한국어]
        CybORG를 리셋하고 지정한 에이전트의 초기 관찰값(Observation)과
        행동 공간(Action Space)을 가져온다.

        참고: 이 메서드는 OpenAI Gym API의 핵심 구성요소다.

        Parameters(매개변수)
        - agent: 초기 관찰값을 가져올 에이전트. None이면 초기 참 상태
          (true-state)를 반환한다(기본값 None).

        Returns(반환값)
        - Results: 에이전트의 초기 관찰값과 행동.
        """
        if seed is not None:
            self.np_random, seed = seeding.np_random(seed)
        self.environment_controller.reset(np_random=self.np_random)
        if agent is None:
            return Results(observation=self.environment_controller.init_state)
        obs = self.environment_controller.observation[agent].get_combined_observation().data
        action_space = self.environment_controller.agent_interfaces[agent].action_space.get_action_space()
        return Results(observation=obs, action_space=action_space)

    def get_observation(self, agent: str) -> dict:
        """Get the last observation for an agent.

        Parameters
        ----------
        agent: str
            Name of the agent to get observation for.

        Returns
        -------
        Observation
            The agent's last observation.

        [한국어]
        에이전트의 가장 최근 관찰값(Observation)을 가져온다.

        Parameters(매개변수)
        - agent: 관찰값을 가져올 에이전트 이름.

        Returns(반환값)
        - Observation: 해당 에이전트의 최근 관찰값.
        """
        return self.environment_controller.get_last_observation(agent).data  # Temp for stability  # 안정성을 위한 임시 처리

        # observation = self.environment_controller.get_last_observation(agent) # Required for time
        # for name, obs in observation.items():
        #    observation[name] = obs.data

        # return observation

    def get_action_space(self, agent: str):
        """Returns the most recent action space for the specified agent.

        Action spaces may change dynamically as the scenario progresses.

        Parameters
        ----------
        agent: str
            Name of the agent to get action space for.

        Returns
        -------
        dict
            The action space of the specified agent.

        [한국어]
        지정한 에이전트의 가장 최근 행동 공간(Action Space)을 반환한다.

        행동 공간은 시나리오가 진행되면서 동적으로 바뀔 수 있다.

        Parameters(매개변수)
        - agent: 행동 공간을 가져올 에이전트 이름.

        Returns(반환값)
        - dict: 지정한 에이전트의 행동 공간.
        """
        return self.environment_controller.get_action_space(agent)

    def get_observation_space(self, agent: str):
        """Returns the most recent observation for the specified agent.

        Parameters
        ----------
        agent: str
            Name of the agent to get observation space for.

        Returns
        -------
        dict
            The observation of the specified agent.

        [한국어]
        지정한 에이전트의 가장 최근 관찰값(Observation)을 반환한다.

        Parameters(매개변수)
        - agent: 관찰 공간(observation space)을 가져올 에이전트 이름.

        Returns(반환값)
        - dict: 지정한 에이전트의 관찰값.
        """
        return self.environment_controller.get_observation_space(agent)

    def get_last_action(self, agent: str):
        """Returns the last executed action for the specified agent.

        Parameters
        ----------
        agent: str
            Name of the agent to get last action for.

        Returns
        -------
        Action
            The last action of the specified agent.

        [한국어]
        지정한 에이전트가 마지막으로 실행한 행동(Action)을 반환한다.

        Parameters(매개변수)
        - agent: 마지막 행동을 가져올 에이전트 이름.

        Returns(반환값)
        - Action: 지정한 에이전트의 마지막 행동.
        """
        return self.environment_controller.get_last_action(agent)

    def set_seed(self, seed: int):
        """Creates an np_random object to seed all internal CybORG randomisations.

        Parameters
        ----------
        seed: int
            The seed to pass to the np_random object

        [한국어]
        CybORG 내부의 모든 무작위화에 시드를 주기 위한 np_random 객체를 만든다.

        Parameters(매개변수)
        - seed: np_random 객체에 넘길 시드.
        """
        self.np_random, seed = seeding.np_random(seed)
        self.environment_controller.set_np_random(self.np_random)

    def get_ip_map(self):
        """Returns a mapping of hostnames to ip addresses for the current scenario.

        Returns
        -------
        ip_map
            The ip_map indexed by hostname.

        [한국어]
        현재 시나리오에서 호스트명(hostname)을 IP 주소로 매핑한 결과를 반환한다.

        Returns(반환값)
        - ip_map: 호스트명을 키로 갖는 IP 매핑.
        """
        return self.environment_controller.hostname_ip_map

    def get_cidr_map(self):
        '''Returns a mapping of hostnames to subnet cidrs for the current scenario.

        Returns
        -------
        cidr_map
            The ip_map indexed by hostname.

        [한국어]
        현재 시나리오에서 호스트명(hostname)을 서브넷 CIDR로 매핑한 결과를 반환한다.

        Returns(반환값)
        - cidr_map: 호스트명을 키로 갖는 매핑.
        '''
        return self.environment_controller.subnet_cidr_map

    def get_rewards(self):
        """Returns the rewards for each agent at the last executed step.

        Returns
        -------
        rewards: dict
            The rewards indexed by team name.

        [한국어]
        가장 최근에 실행한 스텝(step)에서 각 에이전트의 보상(Reward)을 반환한다.

        Returns(반환값)
        - rewards: 팀(team) 이름을 키로 갖는 보상.
        """
        return self.environment_controller.reward

    def get_reward_breakdown(self, agent: str):
        '''Returns a dictionary mapping hosts to the rewards they contribute to the overall total.

        Parameters
        ----------
        agent: str
            The agent to see the reward breakdown for.
            
        Returns
        -------
        rewards: dict
            The rewards indexed by hostname.

        [한국어]
        각 호스트가 전체 보상(Reward) 합계에 기여하는 보상을 호스트별로 매핑해
        반환한다.

        Parameters(매개변수)
        - agent: 보상 내역(reward breakdown)을 확인할 에이전트.

        Returns(반환값)
        - rewards: 호스트명(hostname)을 키로 갖는 보상.
        '''
        return self.environment_controller.get_reward_breakdown(agent)

    def get_attr(self, attribute: str) -> Any:
        """Returns the specified attribute if present.

        Intended to give wrappers access to the base CybORG class.

        Parameters
        ----------
        attribute: str
            Name of the requested attribute.

        Returns
        -------
        Any
            The requested attribute.

        [한국어]
        지정한 속성(attribute)이 있으면 반환한다.

        래퍼(Wrapper)가 기반 CybORG 클래스에 접근할 수 있도록 하기 위한 용도다.

        Parameters(매개변수)
        - attribute: 요청한 속성 이름.

        Returns(반환값)
        - Any: 요청한 속성.
        """
        if hasattr(self, attribute):
            return self.__getattribute__(attribute)
        return None

    @property
    def agents(self) -> list:
        """Returns all external-facing agents.
        
        Returns
        -------
        Agents: List[str]
            List of names of all external-facing agents.

        [한국어]
        외부에 공개된(external-facing) 모든 에이전트를 반환한다.

        Returns(반환값)
        - Agents: 외부 공개 에이전트 이름 목록.
        """
        # [설명] internal_only(내부 전용)가 아닌 에이전트만 골라 외부 공개 목록으로 만든다.
        return [agent_name for agent_name, agent_info in self.environment_controller.agent_interfaces.items() if not agent_info.internal_only]

    @property
    def active_agents(self) -> list:
        '''Returns all active agents.

        An active agent must have an active shell.

        Returns
        -------
        agents: List[str]
            List of names of all active agents.

        [한국어]
        모든 활성(active) 에이전트를 반환한다.

        활성 에이전트는 활성 셸(active shell)을 가지고 있어야 한다.

        Returns(반환값)
        - agents: 활성 에이전트 이름 목록.
        '''
        return self.environment_controller.get_active_agents()

    def get_agent_ids(self):
        '''Returns the ids for the agents.
        Returns
        -------
        agent_ids: List[str]
            List of agent ids.

        [한국어]
        에이전트들의 id 목록을 반환한다.

        Returns(반환값)
        - agent_ids: 에이전트 id 목록.
        '''
        return list(self.environment_controller.agent_interfaces.keys())

    def close(self, **kwargs):
        '''Shuts down CybORG.

        Designed for the emulator.

        Parameters
        ----------
        **kwargs
            Keyword Arguments to pass to the environment_controller.

        [한국어]
        CybORG를 종료한다.

        에뮬레이터(emulator)용으로 설계되었다.

        Parameters(매개변수)
        - **kwargs: environment_controller로 넘길 키워드 인자.
        '''
        if not self._disable_gui:
            self.gui_actions_queue.put('shutdown')

    @property
    def unwrapped(self):
        '''Returns CybORG without any wrappers.
        Returns
        -------
        cyborg: CybORG
            The CybORG main class.

        [한국어]
        래퍼(Wrapper)가 하나도 적용되지 않은 CybORG를 반환한다.

        Returns(반환값)
        - cyborg: CybORG 메인 클래스.
        '''
        return self

    def get_message_space(self, agent: str) -> gym.Space:
        '''Returns an OpenAI Gym Space that contains possible values for messages.

        Parameters
        ----------
        agent: str
            The agent whose message space is being returned.

        Returns
        -------
        message_space: gym.Space
            The message space being returned.

        [한국어]
        메시지가 가질 수 있는 값들을 담은 OpenAI Gym Space를 반환한다.

        Parameters(매개변수)
        - agent: 메시지 공간(message space)을 반환할 대상 에이전트.

        Returns(반환값)
        - message_space: 반환되는 메시지 공간.
        '''
        return self.environment_controller.get_message_space(agent)

    # --- GUI functions removed in CC4 trim as not supported ---
    # [설명] 아래 GUI 관련 함수들은 CC4에서 지원하지 않아 빈 함수로 남겨 두었다.

    def get_renderer(self):
        pass

    def gui_thread(self):
        pass

    def stop_gui(self):
        pass

    def render(self, mode='human'):
        pass

    def add_red_actions(self, data):
        pass

    def add_blue_actions(self, data, red_action):
        pass

    def get_render_data(self):
        pass

    def add_rewards(self, data):
        pass

    def update_symbols(self, data, red_hosts, red_low_hosts, blue_hosts, blue_protected_hosts):
        pass