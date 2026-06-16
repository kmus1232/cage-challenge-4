from CybORG.Shared.Enums import DecoyType, OperatingSystemType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class VsftpdDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server

    [한국어]
    apache 서버처럼 보이도록 프로세스 정보를 구성한다.
    """
    PORT = 80
    SERVICE_NAME = "vsftpd"
    NAME = "vsftpd"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]
    PROCESS_PATH = "/usr/sbin"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = not host.is_using_port(21)
        is_linux = host.os_type == OperatingSystemType.LINUX
        return has_port and is_linux

class DecoyVsftpd(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    사용 가능하고 호환되는 옵션에 따라, 지정된 호스트에 (공격자를) 오도하는
    Decoy(디코이, 미끼) 프로세스를 생성한다.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {VsftpdDecoyFactory()}
