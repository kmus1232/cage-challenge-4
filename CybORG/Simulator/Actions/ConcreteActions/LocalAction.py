from CybORG.Simulator.Actions import Action


class LocalAction(Action):
    """Abstract class for all concrete actions that occur locally on a host.

    Attributes
    ----------
    agent : str
        agent name
    session : int
        session id

    [한국어]
    호스트 위에서 로컬로 수행되는 모든 구체 행동(Action)의 추상 클래스.

    Attributes
    ----------
    agent : str
        에이전트 이름
    session : int
        세션 id
    """
    def __init__(self,session: int,agent: str):
        super().__init__()
        self.agent = agent
        self.session = session

    def check_for_enterprise_sessions(self, state):
        permission = False
        for session_id in state.sessions[self.agent]:
            session = state.sessions[self.agent][session_id]
            if 'Enterprise' in session.hostname:
                permission = True

        return permission
