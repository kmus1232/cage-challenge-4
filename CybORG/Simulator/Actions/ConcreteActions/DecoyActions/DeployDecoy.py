from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyApache import ApacheDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyTomcat import TomcatDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyHarakaSMPT import HarakaDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyVsftpd import VsftpdDecoyFactory

class DeployDecoy(DecoyAction):
    """
    Creates a misleading process on the designated host depending on available and compatible options.
    
    The candidate decoys in this action is specifically for CC4.

    Attributes
    ----------
    session: int
        The id of the session executing the action.
    agent: str
        The agent executing the action.
    hostname: str
        The hostname of the host targeted by the action.
    duration: int
        Time steps to take the action.

    [한국어]
    지정한 호스트에 사용 가능하고 호환되는 옵션에 따라 가짜(misleading) 프로세스를
    생성하는 행동(Action)이다. 즉 Decoy(디코이, 미끼) 프로세스를 심는다.

    이 행동의 후보 디코이(CANDIDATE_DECOYS)는 CC4(CAGE Challenge 4) 전용이다.

    Attributes(속성)
    ----------
    session: int
        행동을 실행하는 세션의 id.
    agent: str
        행동을 실행하는 에이전트.
    hostname: str
        행동의 대상이 되는 호스트의 hostname.
    duration: int
        행동을 수행하는 데 걸리는 스텝(step) 수.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = [ApacheDecoyFactory(), TomcatDecoyFactory(), HarakaDecoyFactory(), VsftpdDecoyFactory()]

    def __init__(self, *, session: int, agent: str, hostname: str):
        super().__init__(session=session, agent=agent, hostname=hostname)
        self.duration = 2