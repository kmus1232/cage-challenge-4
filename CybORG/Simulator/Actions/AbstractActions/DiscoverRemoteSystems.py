from ipaddress import IPv4Network

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.Pingsweep import Pingsweep
from CybORG.Simulator import State


class DiscoverRemoteSystems(Action):
    """
    A high level Red action that discovers active IP addresses of the other hosts in a subnet.
    It calls the low level action 'Pingsweep'.

    Attributes
    ----------
    subnet: IPv4Network
        The ip_address of the target subnet.
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.

    [한국어]
    서브넷 안의 다른 호스트들 중 활성 상태인 IP 주소를 탐색하는 고수준
    Red 액션이다(원격 시스템 탐색). 내부적으로 저수준 액션 'Pingsweep'을
    호출한다.

    속성
    ----
    subnet: IPv4Network
        탐색 대상 서브넷의 IP 주소.
    session: int
        액션을 실행하는 출발지 세션 id.
    agent: str
        이 액션을 실행하는 Red 에이전트의 이름.
    """
    def __init__(self, subnet: IPv4Network, session: int, agent: str):
        """
        Parameters
        ----------
        subnet: IPv4Network
            The ip_address of the target subnet.
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.

        [한국어]
        매개변수
        --------
        subnet: IPv4Network
            탐색 대상 서브넷의 IP 주소.
        session: int
            출발지 세션 id.
        agent: str
            이 액션을 실행하는 Red 에이전트의 이름.
        """
        super().__init__()
        self.subnet = subnet
        self.agent = agent
        self.session = session

    def execute(self, state: State) -> Observation:
        """
        Pingsweeps the target subnet for active IP addresses of the other hosts.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.

        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False, and any detected host IP addresses on the subnet.

        [한국어]
        대상 서브넷에 핑 스윕(Pingsweep)을 수행해 다른 호스트들의 활성 IP
        주소를 찾는다.

        매개변수
        --------
        state: State
            현재 스텝(step)에서의 시뮬레이션 네트워크 상태.

        반환값
        ------
        obs: Observation
            액션 실행 성공 여부(True/False)와, 서브넷에서 탐지된 호스트 IP
            주소들을 담은 관찰값(Observation).
        """
        # run pingsweep on the target subnet from selected session
        # 선택된 세션을 출발지로 삼아 대상 서브넷에 핑 스윕을 실행한다
        sub_action = Pingsweep(session=self.session, agent=self.agent, subnet=self.subnet)
        obs = sub_action.execute(state)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.subnet}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name,
            self.subnet == other.subnet,
            self.agent == other.agent,
            self.session == other.session,
        ))
