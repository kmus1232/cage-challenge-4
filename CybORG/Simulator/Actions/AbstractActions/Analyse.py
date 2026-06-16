from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.DensityScout import DensityScout
from CybORG.Simulator.Actions.ConcreteActions.SigCheck import SigCheck


class Analyse(Action):
    """ Checks for malware on a single host.

    Targets a single host and returns any files that have Density >0.9. Based on Density Scout.
    https://cert.at/en/downloads/software/software-densityscout

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        the name of the host action is targetting.

    [한국어]
    단일 호스트에서 멀웨어(악성코드)를 점검하는 Analyse(분석) 행동(Action).
    지정한 호스트 하나를 대상으로, 엔트로피 밀도(Density)가 0.9를 넘는 파일을 반환한다.
    Density Scout 도구를 기반으로 한다.
    https://cert.at/en/downloads/software/software-densityscout

    속성(Attributes)
    - session: int — 세션 id
    - agent: str — 이 행동을 실행하는 에이전트 이름
    - hostname: str — 이 행동이 대상으로 삼는 호스트 이름
    """
    def __init__(self, session: int, agent: str, hostname: str):
        """ Instantiates Analyse action.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        hostname: str
            the name of the host action is targetting.

        [한국어]
        Analyse(분석) 행동(Action) 인스턴스를 생성한다.

        매개변수(Parameters)
        - session: int — 세션 id
        - agent: str — 이 행동을 실행하는 에이전트 이름
        - hostname: str — 이 행동이 대상으로 삼는 호스트 이름
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration = 2

    def execute(self, state) -> Observation:
        """ Executes the Action.
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

        매개변수(Parameters)
        - state: State — 현재 CybORG 상태(State)

        반환값(Returns)
        - obs: Observation — 에이전트에 돌려줄 관찰값(Observation)
        """
        # perform monitor at start of action
        # 행동 시작 시점에 Monitor(모니터링)를 수행한다 (현재 주석 처리되어 비활성).
        #monitor = Monitor(session=self.session, agent=self.agent)
        #obs = monitor.execute(state)

        # 분석에 사용할 도구(artefact) 목록. DensityScout는 파일 엔트로피 밀도를,
        # SigCheck는 서명 검증을 수행한다.
        artefacts = [DensityScout, SigCheck]
        # find relevant session on the chosen host
        # 선택한 호스트(hostname)에서 동작 중인 관련 세션을 찾는다.
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        # [설명] 대상 호스트에 해당 에이전트의 세션이 하나도 없으면 분석을 수행할 수 없으므로
        # 실패(False) 관찰값을 반환한다.
        if len(sessions) < 1:
            self.log('Failed because relevant session could not be found!')
            return Observation(False)
        # [설명] 후보 세션이 여러 개일 수 있어 결정론적 난수(np_random)로 하나를 고른다.
        # 시드가 고정되면 동일 시나리오에서 동일 세션이 선택되어 재현성이 보장된다.
        session = state.np_random.choice(sessions)
        # run the artifacts on the chosen host
        # 선택한 호스트에서 각 분석 도구를 차례로 실행한다.
        obs = Observation(True)
        for artifact in artefacts:
            sub_action = artifact(
                agent=self.agent, session=self.session, target_session=session.ident
            )
            sub_obs = sub_action.execute(state)
            # [설명] 각 도구의 하위 관찰값(sub_obs)을 하나의 관찰값(obs)으로 합친다.
            obs.combine_obs(sub_obs)
        return obs
    
    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
    
