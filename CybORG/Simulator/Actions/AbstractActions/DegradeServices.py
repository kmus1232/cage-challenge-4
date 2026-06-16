
from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.StopService import StopService
from CybORG.Simulator.State import State


class DegradeServices(Action):
    """ A Red action that attempts to degrade a service used by green in the mission.
    This is achieved by stopping a random service currently running on a host that red has root priviliges on.

    Attributes
    ----------
    hostname : str
        The name of the host the red agent is intefering with.
    session : int
        The source session id.
    agent : str
        The name of the red agent executing the action.

    [한국어]
    Green 에이전트(정상 사용자)가 임무에서 사용하는 서비스의 성능을 저하시키려는
    Red 에이전트(공격 측)의 행동(Action)이다. Red가 root 권한을 가진 호스트에서
    현재 실행 중인 서비스를 멈추는 방식으로 이루어진다.

    속성
    ----
    hostname : str
        Red 에이전트가 간섭하는 대상 호스트 이름.
    session : int
        출발지(source) 세션 ID.
    agent : str
        이 행동을 실행하는 Red 에이전트 이름.
    """
    def __init__(self, hostname: str, session: int, agent: str):
        """
        Parameters
        ----------
        hostname : str
            The name of the host the red agent is intefering with.
        session : int
            The source session id.
        agent : str
            The name of the red agent executing the action.

        [한국어]
        매개변수
        --------
        hostname : str
            Red 에이전트가 간섭하는 대상 호스트 이름.
        session : int
            출발지(source) 세션 ID.
        agent : str
            이 행동을 실행하는 Red 에이전트 이름.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration=2

    def execute(self, state: State) -> Observation:
        """Executes the DegradeServices action.
        Action process:
            1) Check if there are sessions for the agent on this host
                - if not, return unsuccessful obs
            2) Check one of those sessions has root or sudo priviledges.
                - if not, return unsuccessful obs
            3) Check if host has services
            4) Degrade all services on host

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.

        Returns
        -------
        obs: Observation
            An observation indicating the action's success as True/False, and the service stopped, if any.

        [한국어]
        DegradeServices 행동을 실행한다.
        행동 절차:
            1) 이 호스트에 해당 에이전트의 세션이 있는지 확인한다.
                - 없으면 실패(success=False) 관찰값(Observation)을 반환한다.
            2) 그 세션 중 하나가 root 또는 sudo 권한을 가졌는지 확인한다.
                - 없으면 실패 관찰값을 반환한다.
            3) 호스트에 서비스가 있는지 확인한다.
            4) 호스트의 모든 서비스의 성능을 저하시킨다.

        매개변수
        --------
        state: State
            현재 스텝(step)에서의 시뮬레이션 네트워크 상태.

        반환값
        ------
        obs: Observation
            행동의 성공 여부(True/False)와, 있다면 중단된 서비스를 담은 관찰값(Observation).
        """
        # (1) find session on the chosen host
        # (1) 대상 호스트에서 이 에이전트의 세션을 찾는다.
        sessions_on_host = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions_on_host) == 0:
            return Observation(success=False)

        # (2) find if any session are already SYSTEM or root
        # (2) 세션 중 이미 SYSTEM 또는 root 권한을 가진 것이 있는지 찾는다.
        # [설명] has_privileged_access()가 True인 첫 세션의 ID만 취하고, 없으면 None.
        #        권한 있는 세션이 하나도 없으면 행동은 실패한다.
        session = next((s.ident for s in sessions_on_host if s.has_privileged_access()), None)
        if session is None:
            return Observation(success=False)

        # (3) find if host has services
        # (3) 호스트에 활성(active) 서비스가 있는지 찾는다.
        services = [service for s_name, service in state.hosts[self.hostname].services.items() if service.active]

        if len(services) == 0:
            return Observation(success=False)

        # (4) degrade all services
        # (4) 모든 활성 서비스의 성능을 저하시킨다.
        obs = Observation(success=True)

        for service in services:
            # [설명] degrade_service_reliability()는 서비스를 완전히 멈추는 것이 아니라
            #        신뢰도(reliability)를 낮춰 Green의 서비스 이용 성공률을 떨어뜨린다.
            #        각 서비스의 프로세스 상태를 조회해 관찰값(Observation)에 기록한다.
            service.degrade_service_reliability()
            process_state = state.hosts[self.hostname].get_process(service.process).get_state()
            obs.add_process(hostid=self.hostname, **process_state[0])

        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name,
            self.hostname == other.hostname,
            self.agent == other.agent,
            self.session == other.session,
        ))
