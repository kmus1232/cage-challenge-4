from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class ApacheDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server

    [한국어]
    apache 서버처럼 보이도록 프로세스 정보를 구성하는 Decoy(디코이, 미끼) 팩토리.
    """
    PORT = 80
    SERVICE_NAME = "apache2"
    NAME = "apache2"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]
    PROCESS_PATH="/usr/sbin"


class DecoyApache(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    사용 가능하고 호환되는 옵션에 따라 지정된 호스트에 위장 프로세스를 생성하는
    Decoy(디코이) 행동(Action)이다.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {ApacheDecoyFactory()}
