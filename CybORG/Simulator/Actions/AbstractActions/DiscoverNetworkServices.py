from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Simulator.Actions import RemoteAction
from CybORG.Simulator.Actions.ConcreteActions.Portscan import Portscan


class DiscoverNetworkServices(RemoteAction):
    """
    A high level Red action that discovers services on a known host as a prerequisite for running an exploit.

    This calls the low level action 'PortScan', then modifies the observation. This must be used on a host in order to then
    successfully run the high level action ExploitRemoteServices.

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the target host.
    detection_rate: float
        The liklihood of blue detecting red's actions.

    [한국어]
    이미 알고 있는 호스트에서 동작 중인 서비스를 탐색하는 상위 수준 Red 행동(Action)이다.
    익스플로잇(원격 서비스 공격)을 실행하기 위한 사전 단계 역할을 한다.

    내부적으로 하위 수준 행동인 PortScan을 호출한 뒤 그 관찰값(Observation)을 가공한다.
    상위 행동인 ExploitRemoteServices를 성공시키려면 먼저 대상 호스트에 이 행동을 써야 한다.

    Attributes(속성)
    - session: int — 출발 세션 ID
    - agent: str — 이 행동을 실행하는 Red 에이전트 이름
    - ip_address: IPv4Address — 대상 호스트의 IP 주소
    - detection_rate: float — Red의 행동을 Blue가 탐지할 확률
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """
        Parameters
        ----------
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the target host.

        [한국어]
        Parameters(매개변수)
        - session: int — 출발 세션 ID
        - agent: str — 이 행동을 실행하는 Red 에이전트 이름
        - ip_address: IPv4Address — 대상 호스트의 IP 주소
        """
        super().__init__(session=session, agent=agent)
        self.ip_address = ip_address
        self.agent = agent
        self.session = session
        self.detection_rate = 1

    def execute(self, state) -> Observation:
        """
        Discovers the services on the target host.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.

        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False, and a list of the target host's detected services.

        [한국어]
        대상 호스트에서 동작 중인 서비스를 탐색한다.

        Parameters(매개변수)
        - state: State — 현재 스텝(step) 시점의 시뮬레이션 네트워크 상태

        Returns(반환값)
        - obs: Observation — 행동 성공 여부(True/False)와 대상 호스트에서
          탐지된 서비스 목록을 담은 관찰값(Observation)
        """

        # find if agent session exists
        # 에이전트의 세션이 존재하는지 확인한다
        session = state.sessions.get(self.agent, {}).get(self.session, None)
        if session is None:
            self.log(f"Session '{self.session}' for agent '{self.agent}' not found.")
            return Observation(success=False)
        src_hostname = session.hostname

        # check if session is of type RedAbstractSession
        # 세션이 RedAbstractSession 타입인지 확인한다
        if not isinstance(session, RedAbstractSession):
            self.log(f"Session type is '{type(session)}' not 'RedAbstractSession'.")
            return Observation(success=False)

        # Check that there is no traffic blocks between subnets
        # 서브넷 간 트래픽 차단이 없는지 확인한다 (차단돼 있으면 탐색 실패)
        if self.blocking_host(state=state, src_hostname=src_hostname, other_hostname=state.ip_addresses[self.ip_address]):
            self.log(f"'{self.ip_address}' not found in session ports.")
            return Observation(success=False)

        # run portscan on the target ip address from the selected session
        # 선택된 세션에서 대상 IP 주소로 포트 스캔(Portscan)을 실행한다
        sub_action = Portscan(session=self.session, agent=self.agent, ip_address=self.ip_address, detection_rate=self.detection_rate)
        obs = sub_action.execute(state)
        # [설명] 포트 스캔 결과에 대상 IP가 있으면, 세션이 기억하던 해당 IP의 포트 목록을
        # 일단 비우고(clearports), 새로 탐지된 프로세스들의 연결 포트를 다시 등록한다(addport).
        # 이렇게 갱신해 둔 포트 정보가 이후 ExploitRemoteServices의 사전 조건이 된다.
        if str(self.ip_address) in obs.data:
            # session = state.sessions[self.agent][self.session]
            #if isinstance(session, RedAbstractSession):
            session.clearports(self.ip_address)
            for proc in obs.data[str(self.ip_address)]["Processes"]:
                for conn in proc['Connections']:
                    session.addport(self.ip_address, conn["local_port"])
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.ip_address}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name,
            self.ip_address == other.ip_address,
            self.agent == other.agent,
            self.session == other.session,
        ))



class StealthServiceDiscovery(DiscoverNetworkServices):
    """
    The same high level red action as DiscoverNetworkServices, except with:

      - higher duration than AggressiveServiceDiscovery, with 3 ticks
      - lower detection rate of 25%

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the target host.
    duration: int
        The number of ticks the action takes to complete.
    detection_rate: float
        The liklihood of blue detecting red's actions.

    [한국어]
    DiscoverNetworkServices와 동일한 상위 수준 Red 행동이되, 다음 점이 다르다.
    - AggressiveServiceDiscovery보다 소요 시간이 길다 (3틱).
    - 탐지 확률이 25%로 낮다. (은밀하게 탐색하는 변형)

    Attributes(속성)
    - session: int — 출발 세션 ID
    - agent: str — 이 행동을 실행하는 Red 에이전트 이름
    - ip_address: IPv4Address — 대상 호스트의 IP 주소
    - duration: int — 행동 완료까지 걸리는 틱(tick) 수
    - detection_rate: float — Red의 행동을 Blue가 탐지할 확률
    """

    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """
        Parameters
        ----------
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the target host.

        [한국어]
        Parameters(매개변수)
        - session: int — 출발 세션 ID
        - agent: str — 이 행동을 실행하는 Red 에이전트 이름
        - ip_address: IPv4Address — 대상 호스트의 IP 주소
        """
        super().__init__(session, agent, ip_address)
        self.duration = 3
        self.detection_rate = 0.25


class AggressiveServiceDiscovery(DiscoverNetworkServices):
    """
    The same high level red action as DiscoverNetworkServices, except with:

     - lower duration than StealthServiceDiscovery, the default of 1 tick
     - higher detection rate of 75%, compared to StealthServiceDiscovery

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the target host.
    detection_rate: float
        The liklihood of blue detecting red's actions.

    [한국어]
    DiscoverNetworkServices와 동일한 상위 수준 Red 행동이되, 다음 점이 다르다.
    - StealthServiceDiscovery보다 소요 시간이 짧다 (기본값 1틱).
    - StealthServiceDiscovery에 비해 탐지 확률이 75%로 높다. (공격적으로 탐색하는 변형)

    Attributes(속성)
    - session: int — 출발 세션 ID
    - agent: str — 이 행동을 실행하는 Red 에이전트 이름
    - ip_address: IPv4Address — 대상 호스트의 IP 주소
    - detection_rate: float — Red의 행동을 Blue가 탐지할 확률
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """
        Parameters
        ----------
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the target host.

        [한국어]
        Parameters(매개변수)
        - session: int — 출발 세션 ID
        - agent: str — 이 행동을 실행하는 Red 에이전트 이름
        - ip_address: IPv4Address — 대상 호스트의 IP 주소
        """
        super().__init__(session, agent, ip_address)
        self.detection_rate = 0.75

