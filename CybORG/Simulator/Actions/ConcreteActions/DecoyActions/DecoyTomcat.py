from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class TomcatDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as a tomcat server

    [한국어]
    tomcat 서버처럼 보이도록 프로세스 정보를 구성하는 DecoyFactory.
    """
    PORT = 443
    SERVICE_NAME = "tomcat"
    NAME = "Tomcat.exe"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]


class DecoyTomcat(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    사용 가능하고 호환되는 옵션에 따라 지정된 호스트에 가짜(미끼) 프로세스를
    생성하는 Decoy 행동(Action)이다.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {TomcatDecoyFactory()}
