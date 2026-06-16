from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.StopService import StopService
from CybORG.Simulator.State import State
from CybORG.Simulator.Host import Host
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Shared.Enums import ProcessName

class Impact(Action):
    """ Impact (stop service) any OT service on the host, if red has a privileged shell on the host.

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        the name of the agent executing the action
    hostname: str
        the name of the host the action is executed on

    [한국어]
    Impact(타격) 행동(Action). Red 에이전트가 해당 호스트에서 권한 있는 셸을
    가지고 있을 때, 그 호스트의 OT 서비스를 중단(stop service)시킨다.

    속성:
    - session: 행동을 시작한 소스 세션의 id
    - agent: 행동을 실행하는 에이전트 이름
    - hostname: 행동 대상 호스트 이름
    """
    def __init__(self, hostname: str, session: int, agent: str):
        """
        Parameters
        ----------
        session: int
            session id
        agent: str
            name of agent carrying out the action
        hostname: str
            name of the host the action is being carried out on

        [한국어]
        매개변수:
        - session: 세션 id
        - agent: 행동을 수행하는 에이전트 이름
        - hostname: 행동을 수행할 대상 호스트 이름
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration=2

    def execute(self, state: State) -> Observation:
        """ Execution of the Impact action that stops any OT service on the host, if red has a privileged shell on the host.

        Process:

        1. find session on the chosen host
        2. find if any session are already SYSTEM or root
        3. find if host has an OT service
        4. impact/stop OT service

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.

        Returns
        -------
        obs: Observation
            successful/unsuccessful observation

        [한국어]
        Impact 행동의 실제 실행부. Red 에이전트가 대상 호스트에서 권한 있는 셸을
        가지고 있을 때만 그 호스트의 OT 서비스를 중단시킨다.

        처리 절차:
        1. 대상 호스트에 있는 세션을 찾는다.
        2. 그중 이미 SYSTEM 또는 root 권한을 가진 세션이 있는지 확인한다.
        3. 호스트에 OT 서비스가 있는지 확인한다.
        4. OT 서비스를 타격(중단)한다.

        매개변수:
        - state: 현재 스텝(step) 시점의 시뮬레이션 네트워크 상태(State)

        반환값:
        - obs: 성공/실패를 담은 관찰값(Observation)
        """

        # (1) find session on the chosen host
        # (1) 대상 호스트에 있는 이 에이전트의 세션들을 찾는다. 하나도 없으면 실패.
        sessions_on_host = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions_on_host) == 0:
            return Observation(success=False)

        # (2) find if any session are already SYSTEM or root
        # (2) 그중 권한 있는(SYSTEM/root) 세션의 id를 하나 고른다. 없으면 실패.
        session = next((s.ident for s in sessions_on_host if s.has_privileged_access()), None)
        if session is None:
            return Observation(success=False)

        # (3) find if host has an OT service
        # (3) 호스트에서 활성 상태(active)인 OT 서비스를 찾는다. 없으면 실패.
        ot_services = [service for s_name, service in state.hosts[self.hostname].services.items() if s_name == ProcessName.OTSERVICE and service.active]

        if len(ot_services) == 0:
            return Observation(success=False)

        # (4) impact/stop OT service
        # (4) OT 서비스를 타격(중단)한다.
        # [설명] StopService 실행 전에 OT 서비스 프로세스의 현재 상태(sp_state)를
        #        미리 저장해 둔다. 중단에 성공하면 이 상태를 관찰값에 되돌려 담아
        #        (add_process) Blue 에이전트가 어떤 프로세스가 영향받았는지 알 수 있게 한다.
        ot_process = [(process.pid, process.name, process) for process in state.hosts[self.hostname].processes if process.name == ProcessName.OTSERVICE]
        service_process = state.hosts[self.hostname].get_process(ot_services[0].process)
        sp_state = service_process.get_state()

        # 실제 중단은 StopService 하위 행동(sub-action)에 위임한다.
        sub_action = StopService(
            agent=self.agent, session=self.session, service=ProcessName.OTSERVICE, target_session=session
        )
        obs = sub_action.execute(state)

        # 중단에 성공하면 미리 저장한 프로세스 상태를 관찰값에 담고,
        # 해당 호스트의 누적 impact 횟수를 1 증가시킨다.
        if obs.success:
            obs.add_process(self.hostname, **sp_state[0])
            state.hosts[self.hostname].increment_impact_count()
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
