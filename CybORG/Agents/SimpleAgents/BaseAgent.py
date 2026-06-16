from gym.utils import seeding
from CybORG.Shared import Results

class BaseAgent:
    """The base inherited class for any agent used in CybORG.

    This class acts as an abstract class that enforces the implementation of the agent choosing an actions.
    It also provides placeholder functions for use when/if the agent: learns a policy, set initial values, or update its internal state.

    Attributes
    ----------
    name : str
        agent name
    np_random : Tuple[np.random.Generator, Any], optional
        contains a RNG and the seed

    [한국어]
    CybORG에서 사용하는 모든 에이전트가 상속하는 기반(base) 클래스.

    행동(Action) 선택 로직의 구현을 강제하는 추상 클래스 역할을 한다. 또한
    에이전트가 정책(policy)을 학습하거나, 초기값을 설정하거나, 내부 상태를
    갱신할 때 쓰는 자리표시자(placeholder) 함수들을 제공한다.

    속성(Attributes)
    - name : str — 에이전트 이름
    - np_random : Tuple[np.random.Generator, Any], optional — 난수 생성기(RNG)와 시드(seed)를 담는다
    """
    def __init__(self, name: str, np_random=None):
        """Initialises the instance with a given name and rnadom number generator (RNG)

        Parameters
        ----------
        name : str
            agent name
        np_random : Tuple[np.random.Generator, Any], optional
            contains a RNG and the seed, usually omitted

        [한국어]
        주어진 이름과 난수 생성기(RNG)로 인스턴스를 초기화한다.

        매개변수(Parameters)
        - name : str — 에이전트 이름
        - np_random : Tuple[np.random.Generator, Any], optional — RNG와 시드를 담으며 보통 생략한다(생략 시 내부에서 새로 생성)
        """

        self.name = name
        # [설명] np_random이 주어지지 않으면 gym의 seeding으로 RNG와 시드를 새로 만든다.
        if np_random is None:
            np_random, seed = seeding.np_random()
        self.np_random = np_random

    def train(self, results: Results):
        """Allows an agent to learn a policy

        Function is left empty to be overwritten by the class that inherits BaseAgent.
        If the agent is deterministic (e.g. a heuristic agent), then this function will usually be passed.

        Parameters
        ----------
        results : Results
            class object that holds the consequences or 'results' of the agent's action

        Raises
        ------
        NotImplementedError
            The class inheriting BaseAgent has not implemented this function

        [한국어]
        에이전트가 정책(policy)을 학습하게 하는 함수.

        본문은 비워 두어 BaseAgent를 상속한 클래스가 재정의하도록 한다. 에이전트가
        결정론적(deterministic)이면(예: 휴리스틱 에이전트) 보통 이 함수는 그냥 넘긴다(pass).

        매개변수(Parameters)
        - results : Results — 에이전트 행동(Action)의 결과(consequences)를 담는 클래스 객체

        예외(Raises)
        - NotImplementedError — BaseAgent를 상속한 클래스가 이 함수를 구현하지 않음
        """
        raise NotImplementedError

    def get_action(self, observation, action_space):
        """ Gets the agent's action for that step.

        The function gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space. The contents is left empty to be overwritten by the class that inherits BaseAgent.

        Parameters
        ----------
        observation : dict
            the 'data' dictionary contained within the Observation object
        action_space : dict
            a dictionary representation of the Action_Space object

        Raises
        ------
        NotImplementedError
            The class inheriting BaseAgent has not implemented this function

        [한국어]
        해당 스텝(step)에서 수행할 에이전트의 행동(Action)을 가져온다.

        에이전트의 내부 상태와 주어진 관찰값(Observation)·행동 공간(Action Space)을
        근거로 수행할 행동을 산출한다. 본문은 비워 두어 BaseAgent를 상속한 클래스가
        재정의하도록 한다.

        매개변수(Parameters)
        - observation : dict — Observation 객체 안의 'data' 딕셔너리
        - action_space : dict — Action_Space 객체를 딕셔너리로 표현한 것

        예외(Raises)
        - NotImplementedError — BaseAgent를 상속한 클래스가 이 함수를 구현하지 않음
        """
        raise NotImplementedError

    def end_episode(self):
        """Allows an agent to update its internal state.

        Raises:
            NotImplementedError: The class inheriting BaseAgent has not implemented this function

        [한국어]
        에피소드(Episode)가 끝날 때 에이전트가 내부 상태를 갱신하게 하는 함수.

        예외(Raises)
        - NotImplementedError — BaseAgent를 상속한 클래스가 이 함수를 구현하지 않음
        """
        raise NotImplementedError

    def set_initial_values(self, action_space, observation):
        """Allows the agent to set initial values when the AgentInterface object is first defined.

        This function is very rarely used and commonly passed in agent implementation.

        Raises
        ------
        NotImplementedError
            The class inheriting BaseAgent has not implemented this function

        [한국어]
        AgentInterface 객체가 처음 정의될 때 에이전트가 초기값을 설정하게 하는 함수.

        실제로는 거의 쓰이지 않으며, 에이전트 구현에서 보통 그냥 넘긴다(pass).

        예외(Raises)
        - NotImplementedError — BaseAgent를 상속한 클래스가 이 함수를 구현하지 않음
        """
        raise NotImplementedError

    # By default special members (e.g. __special__) and private members (e.g. _private) are not included in docstrings
    # 기본적으로 특수 멤버(예: __special__)와 비공개 멤버(예: _private)는 docstring에 포함되지 않는다.

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"
