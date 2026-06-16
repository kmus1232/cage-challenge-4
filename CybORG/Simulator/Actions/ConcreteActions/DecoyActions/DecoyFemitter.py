from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Shared.Enums import OperatingSystemType
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class FemitterDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server

    [한국어]
    apache 서버처럼 보이도록 프로세스 정보를 구성하는 디코이 팩토리.
    """
    PORT = 21
    SERVICE_NAME = "femitter"
    NAME = "femitter"
    PROCESS_TYPE = 'femitter'
    PROCESS_PATH = "/usr/sbin"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_windows = host.os_type == OperatingSystemType.WINDOWS
        return has_port and is_windows

class DecoyFemitter(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    사용 가능하고 호환되는 옵션에 따라 지정된 호스트에 오인을 유도하는
    프로세스를 생성하는 Decoy(디코이) 행동(Action).
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {FemitterDecoyFactory()}
