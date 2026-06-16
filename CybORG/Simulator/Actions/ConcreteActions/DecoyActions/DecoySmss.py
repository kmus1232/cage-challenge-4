from CybORG.Shared.Enums import DecoyType, OperatingSystemType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class SMSSDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as smss

    [한국어]
    smss 프로세스인 것처럼 보이도록 프로세스 정보를 구성한다.
    """
    PORT = 139
    SERVICE_NAME = "smss"
    NAME = "Smss.exe"
    PROCESS_TYPE = "smb"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_windows = host.os_type == OperatingSystemType.WINDOWS
        return all((has_port, is_windows))

class DecoySmss(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    사용 가능하고 호환되는 옵션에 따라 지정된 호스트에 기만용 프로세스를 생성한다.
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {SMSSDecoyFactory()}
