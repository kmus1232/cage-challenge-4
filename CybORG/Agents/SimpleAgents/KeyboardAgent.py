# Copyright DST Group. Licensed under the MIT license.
import inspect
from pprint import pprint
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared.Enums import TernaryEnum

from ipaddress import IPv4Network

SUCCESS_TO_TEXT = {
    TernaryEnum.FALSE.value: 'The action failed!',
    TernaryEnum.TRUE.value: 'Yay! The action was a success!',
    TernaryEnum.UNKNOWN.value: 'Outcome of action is unknown...',
    TernaryEnum.IN_PROGRESS.value: 'Action is still executing...',
}

class KeyboardAgent(BaseAgent):
    """An agent that lets a human pick actions interactively via the keyboard.

    Each step it prints the current observation and the valid commands, then
    prompts the operator to choose a command and its parameters from the
    action space.

    [한국어]
    사람이 키보드로 직접 행동(Action)을 고르도록 하는 에이전트.
    매 스텝(step)마다 현재 관찰값(Observation)과 선택 가능한 명령을 출력한 뒤,
    행동 공간(Action Space)에서 명령과 파라미터를 운영자가 직접 고르게 한다.
    학습된 정책 대신 사람이 개입해 동작을 확인·디버깅할 때 쓴다.
    """

    def __init__(self,agent_name,screen_width=94):
        self.step = 1
        self.agent_name=agent_name
        self.screen_width = screen_width # Sets width of the printed bars
        # 화면에 출력되는 구분선(bar)의 너비를 설정한다.

    def get_action(self, observation, action_space, sessions=None):
        """Print the current state, then prompt the user to pick an action.

        [한국어]
        현재 상태(관찰값·직전 행동 성공 여부)를 출력한 뒤, 사용자에게 명령과
        파라미터를 입력받아 하나의 행동(Action) 객체를 만들어 반환한다.
        """
        print(94*'-')
        print(94*'-')
        print('',f' Turn {self.step}: {self.agent_name.upper()} '.center(self.screen_width, '*'),'',sep='\n')
        print(94*'-')
        print(94*'-')
        self._print_observation(observation)
        self._print_action_success(observation)

        # 선택 가능한 명령 목록을 만들고, 사용자에게 명령을 고르게 한 뒤,
        # 그 명령에 필요한 파라미터를 마저 입력받아 행동(Action)을 완성한다.
        valid_commands = self._get_valid_commands(action_space)
        command = self._choose_from_options('Command',list(valid_commands.keys()))
        action = self._select_parameters(valid_commands[command])

        self.step += 1
        return action

    def _print_observation(self,observation):
        """Pretty-print the current observation for the user to read.

        [한국어]
        현재 관찰값(Observation)을 사람이 읽기 좋게 출력한다.
        dict면 pprint로 보기 좋게, 아니면 그대로 출력한다.
        """
        print('',f' Turn {self.step}: Observation '.center(self.screen_width, '*'),'',sep='\n')
        if type(observation) == dict:
            pprint(observation)
        else:
            print(observation)

    def _print_action_success(self,observation):
        """Print whether the previous action succeeded, based on the observation.

        [한국어]
        관찰값(Observation)에서 직전 행동의 성공 여부를 읽어 사람이 읽을 수 있는
        문구로 출력한다. 관찰값 형태에 따라 dict 키 또는 속성으로 접근한다.
        """
        if type(observation) == dict:
            success = observation['success']
        else:
            success = observation.success

        # 첫 스텝에는 직전 행동이 없으므로 성공 여부를 출력하지 않는다.
        if self.step == 1:
            return

        if success.value in SUCCESS_TO_TEXT:
            print(self.screen_width * '-', SUCCESS_TO_TEXT[success.value], self.screen_width * '*', sep='\n')

    def _get_valid_commands(self,action_space):
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
        선택 가능한 명령과 그 인자 옵션을 담은 딕셔너리를 만든다.

        각 명령(command)의 함수 시그니처에서 인자 이름을 읽어, 'self'와
        'priority'는 건너뛴다. 나머지 인자별로 행동 공간(action_space)에서
        가능한 옵션을 꺼내, "현재 유효한(True인)" 값만 남긴다.

        파라미터
        ---------
        action_space: dict(dict)
            에이전트의 현재 행동 공간(action_space)

        반환값
        -------
        valid_commands : dict
            유효한 명령과 그 인자 옵션을 담은 딕셔너리
        """

        print('',f' Turn {self.step}: Command Selection '.center(self.screen_width, '*'),'',sep='\n')

        valid_commands = {}
        for command in action_space['action'].keys():
            # 명령 함수의 시그니처에서 인자 목록을 추출한다.
            parameter_list = inspect.signature(command).parameters
            parameter_dict = {}
            for parameter in parameter_list:
                # 'self'와 'priority' 인자는 사용자 선택 대상이 아니므로 건너뛴다.
                if parameter == 'self':
                    continue
                if parameter == 'priority':
                    continue

                # 인자 이름이 'subnet'으로 끝나면 서브넷 옵션 테이블을 사용한다.
                if parameter.endswith('subnet'):
                    option_dict = action_space['subnet']
                else:
                    option_dict = action_space[parameter]

                # [설명] option_dict는 {옵션값: 유효여부(bool)} 형태다.
                # filter는 값이 True인 키만 남기므로, 현재 유효한 옵션만 추린다.
                filter_f = lambda key : option_dict[key]
                valid_options = list(filter(filter_f,option_dict.keys()))
                # 유효한 옵션이 하나도 없으면 이 명령은 실행 불가 -> break로
                # for...else의 else를 건너뛰어 valid_commands에 넣지 않는다.
                if not valid_options:
                    break
                parameter_dict[parameter] = valid_options

            else:
                # [설명] for문이 break 없이 끝났을 때만 실행되는 else 블록.
                # 모든 인자에 유효한 옵션이 있어야 명령을 유효 목록에 등록한다.
                parameter_dict['command'] = command
                valid_commands[command.__name__] = parameter_dict

        return valid_commands

    def _choose_from_options(self, name:str, options:list):
        """Prompt the user to pick one item from a list of options.

        [한국어]
        옵션 목록에서 사용자가 하나를 고르게 한다.
        옵션이 없으면 예외를 던지고, 하나뿐이면 자동 선택한다.
        그 외에는 번호 또는 이름(대소문자 무시)으로 입력받아 선택을 확정한다.
        """
        if len(options) == 0:
            raise ValueError(f'Selecting {name} failed because there are no valid options')
        elif len(options) == 1:
            # 선택지가 하나뿐이면 사용자 입력 없이 자동으로 고른다.
            choice = options[0]
            print(f'Automatically choosing {choice} as it is the only option.')
            return choice

        for i in range(len(options)):
            print(i, options[i])

        # 유효한 입력을 받을 때까지 반복한다.
        while True:
            user_input = input(self.screen_width*'-'+f'\nCHOOSE A {name.upper()}: ')
            if user_input.isdigit():
                # 숫자를 입력하면 옵션 목록의 인덱스로 해석한다.
                try:
                    choice = options[int(user_input)]
                    break
                except:
                    print('Choose a number in range.....')
            else:
                # 숫자가 아니면 옵션 이름을 대소문자 구분 없이 비교해 찾는다.
                options_lower = [str(x).lower() for x in options]
                try:
                    index = options_lower.index(user_input.lower())
                    choice = options[index]
                except:
                    print(f'You didn\'t type in a valid {name}...')

        print(f'You chose {choice}.')
        return choice

    def _select_parameters(self, parameter_dict):
        """Ask the user for each parameter, then build the action object.

        [한국어]
        명령에 필요한 각 파라미터를 사용자에게 차례로 물어 고르게 한 뒤,
        선택된 값들로 명령(command)을 호출해 행동(Action) 객체를 만들어 반환한다.
        """
        print('\n')
        print(f' Turn {self.step}: Parameter Selection '.center(self.screen_width, '*'))
        print('\n')

        # [설명] 'command' 키에는 호출할 명령 함수가 들어 있다. pop으로 꺼내면
        # parameter_dict에는 사용자에게 물어볼 인자만 남는다.
        command = parameter_dict.pop('command')

        chosen_parameters = {}
        for parameter in parameter_dict:
            print(f' {parameter.capitalize()} Selection '.center(self.screen_width, '-'))
            choice = self._choose_from_options('Parameter',parameter_dict[parameter])
            chosen_parameters[parameter] = choice

        # 선택된 인자들을 키워드 인자로 넘겨 행동(Action) 객체를 생성한다.
        return command(**chosen_parameters)

    def train(self, results):
        # The user trains with their brain, not an API!
        # 사용자는 API가 아니라 머리로 학습한다 -> 학습 단계에서 할 일이 없다.
        pass

    def set_initial_values(self, action_space, observation):
        pass

    def end_episode(self):
        pass
