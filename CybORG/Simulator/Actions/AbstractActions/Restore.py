from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.RestoreFromBackup import RestoreFromBackup

class Restore(Action):
    """ Reimages a host, removing all malicious activity.

    Has flat penalty of -1, representing the downtime of the host.


    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        the name of the host targeted by this action.

    [한국어]
    호스트를 재이미징(reimage)하여 모든 악성 활동을 제거하는 Restore(복원) 행동(Action)이다.
    호스트 다운타임을 반영해 항상 -1의 고정 페널티(보상)를 받는다.

    속성(Attributes)
    - session(int): 세션 id
    - agent(str): 이 행동을 실행하는 에이전트 이름 (보통 Blue 에이전트)
    - hostname(str): 이 행동의 대상이 되는 호스트 이름
    """
    def __init__(self, session: int, agent: str, hostname: str):
        """ Instantiates the Restore class.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        hostname: str
            the name of the host targeted by this action.

        [한국어]
        Restore(복원) 행동(Action) 객체를 생성한다.

        매개변수(Parameters)
        - session(int): 세션 id
        - agent(str): 이 행동을 실행하는 에이전트 이름
        - hostname(str): 이 행동의 대상이 되는 호스트 이름
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration = 5  # 행동이 완료되기까지 걸리는 스텝(step) 수

    def execute(self, state) -> Observation:
        """ Executes the action.
        Parameters
        ----------
        state: State
            The current CybORG state.

        Returns
        -------
        obs: Observation
            The observation to be returned to the user.

        [한국어]
        행동(Action)을 실행한다.

        매개변수(Parameters)
        - state(State): 현재 CybORG 상태(state)

        반환(Returns)
        - obs(Observation): 사용자에게 돌려줄 관찰값(Observation)
        """
        # perform monitor at start of action
        # 행동 시작 시 Monitor(모니터링)를 수행 (현재는 주석 처리되어 비활성)
        #monitor = Monitor(session=self.session, agent=self.agent)
        #obs = monitor.execute(state)

        # 에이전트에게 해당 세션 id가 없으면 실패 관찰값을 반환한다
        if self.session not in state.sessions[self.agent]:
            self.log(f"Session '{self.session}' not found for agent '{self.agent}'.")
            return Observation(False)
        # find relevant session on the chosen host
        # 대상 호스트(hostname)에 존재하는 세션들만 골라낸다
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        # 해당 호스트에 세션이 하나도 없으면 실패 관찰값을 반환한다
        if not sessions:
            self.log(f"No sessions could be found on chosen host '{self.hostname}'.")
            return Observation(False)
        # [설명] 후보 세션이 여러 개면 무작위로 하나를 고른다. 재현 가능한 시뮬레이션을
        # 위해 전역 random이 아니라 상태에 묶인 np_random을 사용한다.
        session = state.np_random.choice(sessions)
        # restore host
        # 선택한 세션을 대상으로 백업본에서 호스트를 복원(RestoreFromBackup)한다
        action = RestoreFromBackup(session=self.session, agent=self.agent, target_session=session.ident)
        action.execute(state)
        # remove suspicious files
        # 의심스러운 파일 제거 (재이미징 복원으로 처리됨). 복원이 끝나면 성공 관찰값을 반환한다
        return Observation(True)

    @property
    def cost(self):
        return -1

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
