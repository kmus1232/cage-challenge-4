from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared import Results
from CybORG.Simulator.Actions import Sleep, Monitor

class ConstantAgent(BaseAgent):
    """A base agent which will repeatedly do the same action.

    Attributes
    ----------
    action : Action
        the action that the agent will repeatedly do

    [한국어]
    항상 같은 행동(Action)만 반복하는 기본 에이전트.
    학습 없이 고정된 행동을 매 스텝 그대로 반환한다.

    속성
    ----
    action : Action
        에이전트가 매번 반복해서 수행할 행동(Action)
    """
    def __init__(self, action, name=None):
        super().__init__(name)
        self.action = action

    def train(self, results: Results):
        """allows an agent to learn a policy

        [한국어]
        에이전트가 정책(policy)을 학습하도록 하는 메서드.
        ConstantAgent은 고정 행동만 하므로 학습이 없어 아무것도 하지 않는다.
        """
        pass

    def get_action(self, observation, action_space):
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space

        [한국어]
        에이전트의 내부 상태와 주어진 관찰값(Observation)·행동 공간(Action Space)을
        바탕으로 수행할 행동(Action)을 반환한다.
        ConstantAgent은 입력과 무관하게 항상 고정된 self.action을 반환한다.
        """
        return self.action

    def end_episode(self):
        """Allows an agent to update its internal state

        [한국어]
        에피소드 종료 시 에이전트가 내부 상태를 갱신하도록 하는 메서드.
        ConstantAgent은 유지할 내부 상태가 없어 아무것도 하지 않는다.
        """
        pass

    def set_initial_values(self, action_space, observation):
        pass

class SleepAgent(ConstantAgent):
    """A constant agent whose fixed action is Sleep.

    [한국어]
    고정 행동이 Sleep(아무 동작도 하지 않음)인 ConstantAgent.
    """
    def __init__(self, name=None, **kwargs):
        action = Sleep()
        super().__init__(action, name)

class MonitorAgent(ConstantAgent):
    # [설명] 고정 행동이 Monitor(모니터링)인 ConstantAgent.
    # Blue 에이전트(방어 측)가 세션 0에서 항상 Monitor만 수행하도록 한다.
    def __init__(self):
        action = Monitor(agent='Blue', session=0)
        super().__init__(action)

