from inspect import signature
from typing import Union

from gymnasium import Space
from gym.vector.utils import spaces

from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent

#agent that does random action
# 무작위 행동(Action)을 수행하는 에이전트
from CybORG.Simulator.Actions import Sleep

#testing
# 테스트용 (특정 행동을 강제로 내보낼 때 쓰는 import)
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone, AllowTrafficZone

class RandomAgent(BaseAgent):
    """Takes a random action or a test action based on the epsilon value

    [한국어]
    epsilon 값에 따라 무작위 행동(Action) 또는 지정된 테스트 행동을 고르는 에이전트.
    epsilon 확률로 무작위 행동을 선택하고, 그 외에는 test_action을 그대로 반환한다.
    """

    def __init__(self, name=None, test_action=None, epsilon=1.0, np_random = None):
        super().__init__(name, np_random)
        self.test_action = test_action
        self.epsilon = epsilon
        self.action_params = None
        self.excluded_actions = []

    def train(self, results):
        pass

    def get_action(self, observation: dict, action_space: Union[Space, dict]):
        # [설명] epsilon 확률로 무작위 행동을 고른다. test_action이 없으면 항상 무작위로 동작한다.
        if (self.np_random.random() < self.epsilon) or (self.test_action is None):
            # select random action
            # 무작위 행동 선택
            if isinstance(action_space, Space):
                return action_space.sample()
            elif type(action_space) is dict:
                # [설명] 행동 공간(Action Space)이 dict인 경우: 사용 가능한 행동 클래스 중 하나를
                #        고른 뒤, 그 행동에 필요한 파라미터를 무작위로 채워 인스턴스를 만든다.
                # excluded_actions(제외 목록)는 복사본으로 두고, 파라미터를 못 채운 행동을 여기 누적해 배제한다.
                invalid_actions = self.excluded_actions[:]
                while True:
                    # 활성화(v=True)되어 있고 제외 대상이 아닌 행동 클래스만 후보로 추린다.
                    options = [i for i, v in action_space['action'].items() if v and i not in invalid_actions]
                    if len(options) > 0:
                        action_class = self.np_random.choice(options)
                    else:
                        # 고를 수 있는 행동이 없으면 아무것도 하지 않는 Sleep 행동을 반환한다.
                        return Sleep()
                    # select random options
                    # 선택한 행동에 필요한 파라미터를 무작위로 채운다.
                    action_params = {}
                    for param_name in self.action_params[action_class]:
                        options = [i for i, v in action_space[param_name].items() if v]
                        if len(options) > 0:
                            action_params[param_name] = self.np_random.choice(options)
                        else:
                            # [설명] 이 행동에 필요한 파라미터 중 선택 가능한 값이 하나도 없으면,
                            #        해당 행동을 배제 목록에 넣고 파라미터 채우기를 중단한 뒤 다시 다른 행동을 고른다.
                            invalid_actions.append(action_class)
                            action_params = None
                            break
                    if action_params is not None:
                        # 모든 파라미터를 채웠으면 행동 인스턴스를 생성해 반환한다.
                        return action_class(**action_params)
            else:
                raise ValueError("Random agent can only handle Space or dict action space")
        else:
            # epsilon 조건에 걸리지 않으면 지정된 테스트 행동을 그대로 반환한다.
            return self.test_action

    def end_episode(self):
        pass

    def set_initial_values(self, action_space, observation):
        if type(action_space) is dict:
            self.action_params = {action_class: signature(action_class).parameters for action_class in action_space['action'].keys()}


class cc4BlueRandomAgent(RandomAgent):
    def __init__(self, name: str = None, np_random = None):
        super().__init__(name=name, np_random=np_random)
        self.excluded_actions = [BlockTrafficZone, AllowTrafficZone]