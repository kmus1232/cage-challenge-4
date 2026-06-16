from CybORG.Shared.Enums import DecoyType, OperatingSystemType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class HarakaDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server

    [한국어]
    apache 서버처럼 보이도록 프로세스 정보를 구성하는 디코이 팩토리.
    (Haraka SMTP 디코이로 위장한다.)
    """
    PORT = 25
    SERVICE_NAME = "haraka"
    NAME = "haraka"
    PROCESS_TYPE = "smtp"
    PROCESS_PATH = "/usr/sbin"
    VERSION = "haraka 2.7.0"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_linux = host.os_type == OperatingSystemType.LINUX
        return all((has_port, is_linux))

class DecoyHarakaSMPT(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    호스트에서 사용 가능하고 호환되는 옵션에 따라, 지정된 호스트에
    가짜(미끼) 프로세스를 생성하는 Decoy(디코이) 행동(Action).
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {HarakaDecoyFactory()}
