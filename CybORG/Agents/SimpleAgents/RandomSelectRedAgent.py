import inspect
from pprint import pprint
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw

from ipaddress import IPv4Network

class RandomSelectRedAgent(BaseAgent):
    """ Red Agent that random selects an action (with parameters) to execute.

    Attributes
    ----------
    step : int
        number of steps the agent has taken in the environment
    last_action : str or Action
        the previous action that was executed
    print_output : bool
        option as to if action info is printed to the terminal
    disable_withdraw : bool
        when true, the Withdraw action is removed from the list of possible actions, so that the agent will no longer perform Withdraw.

    Other Parameters
    ----------------
    name : str
        name of the agent
    np_random : numpy.random._generator.Generator
        numpy random generator initialised on creation of scenario. This allows for the seed to be consistent with the CybORG() seed parameter

    [한국어]
    행동(매개변수 포함)을 무작위로 골라 실행하는 Red 에이전트(공격 측).

    속성(Attributes)
    - step : int — 에이전트가 환경에서 수행한 스텝(step) 수
    - last_action : str 또는 Action — 직전에 실행한 행동(Action)
    - print_output : bool — 행동 정보를 터미널에 출력할지 여부
    - disable_withdraw : bool — True이면 가능한 행동 목록에서 Withdraw(철수)를
      제거해, 에이전트가 더 이상 Withdraw를 수행하지 않는다.

    그 외 매개변수(Other Parameters)
    - name : str — 에이전트 이름
    - np_random : numpy.random._generator.Generator — 시나리오(Scenario) 생성
      시점에 초기화되는 numpy 난수 생성기. 이를 통해 시드(seed)를 CybORG()의
      seed 매개변수와 일관되게 유지한다.
    """

    def __init__(self, name: str, np_random):
        super().__init__(name, np_random=np_random)
        self.step = 0
        self.last_action = "Initial Observation"
        self.print_output = False
        self.disable_withdraw = False

    def get_action(self, observation, action_space):
        """Chooses a valid action randomly from the action space, along with corresponding parameters - picked randomly when given options.
        
        Parameters
        ----------
        observation : dict
            agent observation from last action
        action_space : dict
            agent action space

        Raises
        ------
        ValueError
            There are no valid actions for the agent to take. Sleep should always be a valid action, so will only occur in error.

        [한국어]
        행동 공간(Action Space)에서 유효한 행동(Action) 하나를 무작위로 고르고,
        선택지가 있는 매개변수도 무작위로 정한다.

        매개변수(Parameters)
        - observation : dict — 직전 행동에 대한 에이전트 관찰값(Observation)
        - action_space : dict — 에이전트 행동 공간(Action Space)

        예외(Raises)
        - ValueError — 에이전트가 취할 수 있는 유효한 행동이 없을 때 발생한다.
          Sleep은 항상 유효한 행동이어야 하므로, 정상적으로는 발생하지 않고
          오류 상황에서만 발생한다.
        """
        if self.print_output:
            self.last_turn_summary(observation)
        
        action = None
        # 행동 공간에서 유효한 명령(command)과 그 인자 선택지를 모은다.
        valid_commands = self._get_valid_commands(action_space)
        list_commands = list(valid_commands.keys())

        if self.disable_withdraw:
            # disable_withdraw가 True이면 후보에서 Withdraw(철수)를 빼 둔다.
            list_commands.remove('Withdraw')

        # [설명] 유효한 행동을 찾을 때까지 반복한다. 무작위로 고른 명령의 어떤
        # 매개변수에 선택지가 하나도 없으면 그 명령은 버리고 다시 고른다.
        valid_action = False
        while not valid_action:
            if len(list_commands) == 0:
                # 후보 명령이 모두 소진되면 유효한 행동이 없는 것이다.
                raise ValueError("No valid commands")
            else:
                valid_action = True
                # 남은 후보 중 하나를 무작위로 골라 목록에서 꺼낸다(pop).
                command_opt_num = self.np_random.integers(0, len(list_commands))
                command_opt = list_commands.pop(command_opt_num)
                param_dict = valid_commands[command_opt]
                # 'command' 키에는 실제 행동 클래스가 들어 있다. 분리해 둔다.
                command = param_dict.pop('command')

                # 각 매개변수마다 유효한 선택지 중 하나를 골라 채운다.
                chosen_params = {}
                for param_name, param_opts in param_dict.items():
                    if len(param_opts) == 0:
                        # [설명] 선택지가 비어 있으면 이 명령은 실행 불가하므로
                        # valid_action을 False로 되돌려 바깥 while에서 다시 고른다.
                        valid_action = False
                        break
                    elif len(param_opts) == 1:
                        # 선택지가 하나뿐이면 그대로 사용한다.
                        chosen_params[param_name] = param_opts[0]
                    else:
                        # 선택지가 여럿이면 무작위로 하나 고른다.
                        param_opt_num = self.np_random.integers(0, len(param_opts))
                        param_choice = param_opts[param_opt_num]
                        chosen_params[param_name] = param_choice

                # 고른 매개변수로 행동(Action) 객체를 생성한다.
                action = command(**chosen_params)

        self.last_action = action
        # print_output가 켜져 있고 선택된 행동이 Withdraw(철수)면 안내를 출력한다.
        if self.print_output and isinstance(self.last_action, Withdraw):
            print(f"\n*** {self.name} attempts to withdraw ***\n")

        self.step += 1  # 스텝(step) 카운터 증가
        return action

    def last_turn_summary(self, observation: dict):
        """Prints action name, parameters and success

        [한국어]
        직전 행동(Action)의 이름·매개변수·성공 여부를 출력한다.
        """

        print(f'** Turn {self.step} for {self.name} **')
        print("Action: " + str(self.last_action))
        print("Action Success: " + str(observation['success']) )
        print()

    def _get_valid_commands(self, action_space: dict):
        """ Get a dictionary of valid commands with valid argument options.

        For each possible action, get the corresponding argument name. Ignore aguments 'self' and 'priority'. Get argument options per command from action_space and filter by validity.

        Parameter
        ---------
        action_space: dict(dict)
            Agent's current action_space

        Returns
        -------
        valid_commands : dict
            Dictionary of valid commands with argument options

        [한국어]
        유효한 명령(command)과 그 유효한 인자 선택지를 담은 딕셔너리를 만든다.

        가능한 행동(Action)마다 인자 이름을 가져오되 'self'와 'priority' 인자는
        무시한다. 그 다음 action_space에서 명령별 인자 선택지를 가져와 유효한
        것만 걸러낸다.

        매개변수(Parameter)
        - action_space : dict(dict) — 에이전트의 현재 행동 공간(Action Space)

        반환값(Returns)
        - valid_commands : dict — 인자 선택지가 포함된 유효한 명령 딕셔너리
        """
        
        valid_commands = {}
        for command in action_space['action'].keys():
            # 명령(행동 클래스)의 생성자 인자 이름 목록을 얻는다.
            parameter_list = inspect.getfullargspec(command).args
            parameter_dict = {}
            for parameter in parameter_list:
                # 'self'와 'priority' 인자는 선택 대상에서 제외한다.
                if parameter == 'self':
                    continue
                if parameter == 'priority':
                    continue

                # [설명] action_space[parameter]는 {선택지: 유효여부(bool)} 형태다.
                # 값이 True인 키만 남겨 유효한 선택지 목록을 만든다.
                option_dict = action_space[parameter]
                filter_f = lambda key : option_dict[key]
                valid_options = list(filter(filter_f,option_dict.keys()))
                if not valid_options:
                    # 유효한 선택지가 없는 인자가 하나라도 있으면 이 명령은 버린다.
                    break
                parameter_dict[parameter] = valid_options

            else:
                # [설명] for-else: break 없이 모든 인자가 유효했을 때만 실행된다.
                # 명령 자체를 'command' 키로 함께 저장해 둔다.
                parameter_dict['command'] = command
                valid_commands[command.__name__] = parameter_dict

        return valid_commands

    def train(self, results):
        # 무작위 에이전트라 학습하지 않는다(no-op).
        pass

    def set_initial_values(self, action_space, observation):
        # 초기값 설정이 필요 없다(no-op).
        pass

    def end_episode(self):
        # 에피소드(Episode) 종료 시 처리할 상태가 없다(no-op).
        pass
