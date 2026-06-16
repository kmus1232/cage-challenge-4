

from CybORG.Shared import Observation
from .Monitor import Monitor
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.StopProcess import StopProcess
from CybORG.Shared.Session import VelociraptorServer
from CybORG.Simulator.State import State


class Remove(Action):
    """ Removes any Red User session from the target host.
    Represents killing red's shell using 'kill' or 'Taskkill'. Will not remove privileged sessions such as 'root' or 'SYSTEM' shells. That's because we assume (not realistically) that these shells also have a persistance mechanism.

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        the hostname of the host targeted by the action.

    [한국어]
    대상 호스트에서 Red 사용자 세션을 제거하는 Remove(제거) 행동(Action).
    'kill' 또는 'Taskkill'로 Red의 셸을 종료하는 것을 나타낸다.
    단, 'root'나 'SYSTEM' 같은 권한 있는 세션은 제거하지 않는다. 이런 셸은
    (현실적이지는 않지만) 지속성(persistence) 메커니즘도 갖춘 것으로 가정하기 때문이다.

    속성
    ----
    session: int
        세션 id
    agent: str
        이 행동을 실행하는 에이전트 이름
    hostname: str
        이 행동의 대상이 되는 호스트의 호스트명
    """
    def __init__(self, session: int, agent: str, hostname: str):
        """ Instantiates the Remove class.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        hostname: str
            the hostname of the host targeted by the action.

        [한국어]
        Remove 클래스를 생성(인스턴스화)한다.

        매개변수
        --------
        session: int
            세션 id
        agent: str
            이 행동을 실행하는 에이전트 이름
        hostname: str
            이 행동의 대상이 되는 호스트의 호스트명
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration = 3

    def execute(self, state: State) -> Observation:
        """ Executes the action.
        Parameters
        ----------
        state: State
            The current CybORG state.

        Returns
        -------
        obs: Observation
            The observation to be returned to the agent.

        [한국어]
        이 행동(Action)을 실행한다.

        매개변수
        --------
        state: State
            현재 CybORG 상태(State).

        반환값
        ------
        obs: Observation
            에이전트에게 돌려줄 관찰값(Observation).
        """
        # perform monitor at start of action
        # 행동 시작 시 Monitor(모니터링) 수행 (현재는 주석 처리되어 비활성)
        #monitor = Monitor(session=self.session, agent=self.agent)
        #obs = monitor.execute(state)

        # parent_session: 이 행동을 실행하는 Blue 에이전트의 기준 세션(Velociraptor 서버)
        parent_session: VelociraptorServer = state.sessions[self.agent][self.session]
        # find relevant session on the chosen host
        # 선택한 호스트 위에 존재하는 (이 에이전트의) 세션들을 찾는다
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            # 대상 호스트에 세션이 하나도 없으면 실패(False)를 반환한다
            self.log(f"No sessions could be found on chosen host '{self.hostname}'.")
            return Observation(False)
        session = state.np_random.choice(sessions)
        # remove suspicious processes
        # [설명] parent_session.sus_pids는 호스트별로 '의심스러운 프로세스 PID' 목록을 담는다.
        # Monitor/Analyse 단계에서 탐지된 PID들이며, 대상 호스트에 등록된 PID가 있을 때만
        # 각 PID에 대해 StopProcess(프로세스 종료)를 실행해 Red의 프로세스를 제거한다.
        if self.hostname in parent_session.sus_pids:
            for sus_pid in parent_session.sus_pids[self.hostname]:
                action = StopProcess(session=self.session, agent=self.agent, target_session=session.ident, pid=sus_pid)
                action.execute(state)
        # remove suspicious files
        # 의심스러운 파일 제거 (현재 구현 없음 — 성공(True) 반환만 수행)
        return Observation(True)

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
