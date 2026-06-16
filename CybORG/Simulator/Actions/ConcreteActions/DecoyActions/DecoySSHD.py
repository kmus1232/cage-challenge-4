from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class SSHDDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an ssh server

    [한국어]
    ssh 서버처럼 보이도록 프로세스 정보를 구성하는 DecoyFactory.
    """
    PORT = 22
    SERVICE_NAME = "sshd"
    NAME = "Sshd.exe"
    PROCESS_TYPE = "sshd"
    PROCESS_PATH = "C:\\Program Files\\OpenSSH\\usr\\sbin"


class DecoySSHD(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    [한국어]
    지정한 호스트에 가짜(미끼) 프로세스를 생성하는 Decoy 액션.
    사용 가능하고 호환되는 옵션에 따라 생성한다.
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {SSHDDecoyFactory()}
