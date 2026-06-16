from CybORG.Shared.Enums import DecoyType, OperatingSystemType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class SvchostDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as svchost

    [한국어]
    svchost처럼 보이도록 프로세스 정보를 구성하는 Decoy(디코이) 팩토리.
    """
    PORT = 3389
    SERVICE_NAME = "svchost"
    NAME = "Svchost.exe"
    PROCESS_TYPE = "rdp"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_windows = host.os_type == OperatingSystemType.WINDOWS
        return all((has_port,is_windows))

class DecoySvchost(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    사용 가능하고 호환되는 옵션에 따라 지정된 호스트에 가짜 프로세스를 생성하는
    Decoy(디코이) 행동(Action)이다.
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {SvchostDecoyFactory()}
