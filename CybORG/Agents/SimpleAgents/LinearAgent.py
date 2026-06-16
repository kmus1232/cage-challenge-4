import inspect
from typing import Dict, Tuple
from pprint import pprint
from random import randint

from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared.Enums import TernaryEnum
from CybORG.Simulator.Actions import Action, Sleep, InvalidAction


class LinearAgent(BaseAgent):
    """This agent will perform a list of actions, and either repeat them indefinately or Sleep. If no action list is given it will always Sleep.
    
    This agent is intended to help with stress testing and debugging, as it allows the tester to perform a series of specific actions that they have pre-listed.
    As actions sometimes require other action to have been performed successfully to function, this sequential execution makes it possible to test these actions.
    The agent can also be used to test that another type of agent is reacting correctly to a specif series of actions.

    Attributes
    ----------
    action_list : Dict[int : (Action, dict)]
        a list of actions, with parameters, to be executed sequentially.
    circular : bool
        if true, the list of actions will be repeated once the end is reached, otherwise the remaining actions will be Sleep
    step : int
        the agent's internal step counter (not accurate to the State)
    last_action : str
        the name of the previous action that was performed
    print_action_output : bool
        print the action and action success
    print_obs_output : bool
        print the observation from the action
    
    Example
    -------
    An action list could look like the following:

    ```python
    action_list = {
        0: PrivilegeEscalate(
            hostname='contractor_network_subnet_user_host_2', 
            session=0, 
            agent='red_agent_0'),
        1: DiscoverRemoteSystems(
            subnet=IPv4Network('10.0.0.1/24'), 
            session=0, 
            agent='red_agent_0'),
        2: AggressiveServiceDiscovery(
            session=0, 
            agent='red_agent_0', 
            ip_address=IPv4Address('10.0.0.2')
    }
    ```

    [한국어]
    미리 정해 둔 행동(Action) 리스트를 순서대로 실행하고, 끝에 도달하면
    무한 반복하거나 Sleep(아무 동작도 하지 않음)을 수행하는 에이전트다.
    행동 리스트가 주어지지 않으면 항상 Sleep만 한다.

    주 용도는 스트레스 테스트와 디버깅이다. 테스터가 특정 행동들을 미리
    나열해 두고 순서대로 실행할 수 있게 해 준다. 어떤 행동은 다른 행동이
    먼저 성공해야 동작하는데, 이렇게 순차 실행하면 그런 의존 관계가 있는
    행동들도 테스트할 수 있다. 또한 다른 종류의 에이전트가 특정 행동 시퀀스에
    올바르게 반응하는지 검증하는 용도로도 쓸 수 있다.

    속성(Attributes)
    ----------
    action_list : Dict[int : (Action, dict)]
        순차적으로 실행할 행동 리스트(파라미터 포함).
    circular : bool
        true이면 리스트 끝에 도달했을 때 처음부터 다시 반복한다.
        false이면 남은 스텝은 모두 Sleep으로 채운다.
    step : int
        에이전트 내부 스텝 카운터(실제 State와는 일치하지 않는 자체 카운터).
    last_action : str
        직전에 수행한 행동의 이름.
    print_action_output : bool
        수행한 행동과 그 성공 여부를 출력할지 여부.
    print_obs_output : bool
        행동으로 얻은 관찰값(Observation)을 출력할지 여부.
    """

    def __init__(
        self, name: str, action_list: Dict[int, Tuple[Action, dict]] = None,
        circular: bool = True, print_action_output: bool = True, print_obs_output: bool = False):

        super().__init__(name)
        self.action_list = action_list
        self.circular = circular
        self.step = 0

        self.print_action_output = print_action_output
        self.print_obs_output = print_obs_output

    def get_action(self, observation, action_space):
        """Returns the next action from the action list, or Sleep.

        [한국어]
        행동 리스트에서 다음 행동을 반환하며, 해당하는 행동이 없으면 Sleep을 반환한다.
        """
        # 직전 행동이 아직 진행 중이면 새 행동을 내지 않고 Sleep한다.
        if observation['success'] == TernaryEnum.IN_PROGRESS:
            return Sleep()

        # 행동 리스트가 없으면 Sleep만 하는 기본 리스트로 채운다.
        if self.action_list == None:
            self.action_list = {0: Sleep()}

        if self.print_action_output:
            self.last_turn_summary(observation)

        # [설명] 현재 step에 해당하는 행동이 없고 circular(반복) 모드이면,
        # step을 리스트 길이로 나눈 나머지(modulo)를 인덱스로 써서 리스트를
        # 처음부터 다시 순환시킨다. 그 인덱스에도 행동이 없으면 Sleep한다.
        if not self.step in self.action_list.keys() and self.circular:
            n = self.step % len(self.action_list.keys())
            if n in self.action_list.keys():
                action = self.action_list[n]
            else:
                action = Sleep()

        # 현재 step에 해당하는 행동이 있으면 그대로 사용한다.
        elif self.step in self.action_list.keys():
            action = self.action_list[self.step]

        # 그 외(반복 모드가 아니고 해당 step 행동도 없음)에는 Sleep한다.
        else:
            action = Sleep()

        self.step += 1  # 내부 스텝 카운터를 1 증가시킨다.
        return action

    def last_turn_summary(self, observation: dict):
        """Prints action name, parameters, success and sometimes observation

        [한국어]
        직전 턴의 행동 이름·파라미터·성공 여부를 출력하고, 설정에 따라
        관찰값(Observation)도 함께 출력한다.
        """

        action_str = None
        # 관찰값에 'action' 키가 있으면 그 행동을 문자열로 변환하고,
        # 없으면(에피소드 첫 관찰값) "Initial Observation"으로 표기한다.
        if 'action' in observation.keys():
            action_str = str(observation['action'])
        else:
            action_str = "Initial Observation"

        print(f'\n** Turn {self.step} for {self.name} **')
        print("Action: " + action_str)
        print("Action Success: " + str(observation['success']) )

        # 옵션이 켜져 있으면 관찰값(Observation) 전체를 보기 좋게 출력한다.
        if self.print_obs_output:
            print("Observation:")
            pprint(observation)

        # 행동이 InvalidAction(잘못된 행동)이면 그 오류 내용을 출력한다.
        if isinstance(observation.get('action'), InvalidAction):
            pprint(observation['action'].error)

    def train(self, results):
        pass

    def set_initial_values(self, action_space, observation):
        pass

    def end_episode(self):
        pass

