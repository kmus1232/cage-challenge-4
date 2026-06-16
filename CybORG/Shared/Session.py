## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
from ipaddress import IPv4Address
from typing import Dict, List

from CybORG.Shared.Enums import SessionType, OperatingSystemType
from CybORG.Simulator.Entity import Entity

class Session(Entity):
    """Details of the session created between an agent and a host. 
    
    Attributes
    ----------
    ident : int
        session id
    hostname : str
        name of host with session
    username : str
        username of session on host
    agent : str
        name of agent on host
    timeout : int
    pid : int
        process id linked to the session
    parent : int
        parent session id (if exists)
    session_type : str
        type of session
    active : bool
        is the session active/live
    children : {}
        session id of child sessions
    name : str
        name of session
    is_escalate_sandbox : bool
        is the session a decoy sandbox
    num_children : int
        the number of child sessions
    action_queue : list
        queuing actions of multiple time step duration

    [한국어]
    에이전트와 호스트(Host) 사이에 생성된 세션(Session)의 정보를 담는 클래스.

    주요 속성:
    - ident : 세션 ID
    - hostname : 세션이 열려 있는 호스트 이름
    - username : 해당 호스트에서 세션의 사용자명
    - agent : 호스트에 붙은 에이전트 이름
    - timeout : 타임아웃 값
    - pid : 세션과 연결된 프로세스(Process) ID
    - parent : 부모 세션 ID(존재하는 경우)
    - session_type : 세션 종류
    - active : 세션이 활성(살아 있는) 상태인지 여부
    - children : 자식 세션들의 세션 ID
    - name : 세션 이름
    - is_escalate_sandbox : 세션이 디코이(Decoy) 샌드박스인지 여부
    - num_children : 자식 세션 개수
    - action_queue : 여러 스텝(step)에 걸쳐 수행되는 행동(Action)들의 대기열
    """
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell',
                 active: bool = True, parent=None, name=None,
                 is_escalate_sandbox: bool = False, num_children=None):
        super().__init__()
        self.ident = ident
        self.hostname = hostname
        self.username = username
        self.agent = agent
        self.timeout = timeout
        self.pid = pid
        self.parent = parent
        if isinstance(session_type, str):
            self.session_type = SessionType.parse_string(session_type)
        else:
            self.session_type = session_type
        self.active = active
        self.children = {}
        self.name = name
        self.is_escalate_sandbox = is_escalate_sandbox
        self.action_queue = []
        self.num_children = num_children

    def get_state(self):
        """Returns a dictionary representing the state of the session.

        [한국어]
        세션의 현재 상태를 딕셔너리 형태로 반환한다.
        """
        return {
            "username": self.username,
            "session_id": self.ident,
            "timeout": self.timeout,
            "pid": self.pid,
            "session_type": self.session_type,
            "agent": self.agent
        }

    def set_orphan(self):
        """Make the session an orphan session.

        [한국어]
        세션을 고아(orphan) 세션으로 만든다.
        활성 상태를 끄고(active=False) 부모 세션 연결을 끊는다(parent=None).
        """
        self.active = False
        self.parent = None

    def dead_child(self, child_id: int):
        """Remove a specific child session.

        [한국어]
        지정한 자식 세션을 children 목록에서 제거한다.
        """
        self.children.pop(child_id)

    def append_action(self, action: list):
        # [설명] 여러 스텝에 걸친 행동을 대기열(action_queue)에 추가한다.
        # 대기열 끝에 이미 행동이 있으면 그 잔여 시간을 누적 시작점(backlog_time)으로 삼아,
        # 새 행동은 기존 대기 행동들이 모두 끝난 뒤에 완료되도록 남은 시간을 계산한다.
        backlog_time = self.action_queue[-1][1] if len(self.action_queue) != 0 else 0  # 대기열 마지막 행동의 잔여 시간(없으면 0)
        time_remaining = action.duration + backlog_time  # 새 행동의 완료까지 남은 시간 = 행동 소요 시간 + 기존 누적 시간
        action_tuple = (action, time_remaining)
        self.action_queue.append(action_tuple)

    def has_privileged_access(self) -> bool:
        """Does the session have privileged access, based on the username.

        [한국어]
        사용자명을 기준으로 세션이 권한 있는 접근(privileged access)을 가졌는지 판단한다.
        username이 'root' 또는 'SYSTEM'이면 권한 있는 사용자로 본다.
        """
        return self.username in ('root', "SYSTEM")

    @classmethod
    def load(cls, session_info: dict):
        # [설명] session_info 딕셔너리에서 세션 정보를 읽어 적절한 Session 하위 클래스
        # 인스턴스를 만들어 반환하는 팩토리 메서드.
        # session_type 값에 따라 VelociraptorServer / RedAbstractSession / MSFServerSession
        # 등으로 분기하며, 매핑에 없으면 기본 클래스(cls)를 사용한다.
        username = session_info.get("username")
        session_type = session_info.get("type")
        hostname = session_info.get("hostname")
        parent = session_info.get("parent", None)
        num_children = session_info.get("num_children_sessions", 0)
        name = session_info.get('name', None)
        session_types = {
            'VelociraptorServer': VelociraptorServer,
            SessionType.VELOCIRAPTOR_SERVER: VelociraptorServer,
            'RedAbstractSession': RedAbstractSession,
            SessionType.RED_ABSTRACT_SESSION: RedAbstractSession,
            'MetasploitServer': MSFServerSession,
            SessionType.MSF_SHELL: MSFServerSession
        }
        # session_type에 해당하는 클래스를 찾고, 없으면 기본 클래스(cls)를 사용한다.
        session_class = session_types.get(session_type, cls)
        session = session_class(
            username=username, ident=None, session_type=session_type, hostname=hostname, parent=parent,
            num_children=num_children, name=name, pid=None, agent=None
        )
        # This line is a band-aid fix due to inconsistency in how this class is used. Sometimes
        # the value is expected as an enum, sometimes as a string. Should be addressed in future
        # 이 클래스의 사용 방식이 일관되지 않아 넣은 임시방편(band-aid) 처리이다.
        # 어떤 곳은 enum을, 어떤 곳은 문자열을 기대한다. 추후 정리가 필요하다.
        return session

class RedAbstractSession(Session):
    """A red session that remembers previously seen information that can be used by actions.

    [한국어]
    Red 에이전트(공격 측)용 세션으로, 이전에 관찰한 정보를 기억해 두었다가
    이후 행동(Action)에 활용한다.
    """
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell', active: bool = True, parent=None, name=None, num_children=None, is_escalate_sandbox: bool = False):
        super().__init__(ident, hostname, username, agent, pid, timeout, session_type, active, parent, name, num_children=num_children, is_escalate_sandbox=is_escalate_sandbox)
        self.ports: Dict[IPv4Address, List[int]] = {} # a mapping of ip_addresses to previously seen open ports  # IP 주소 -> 이전에 관찰한 열린 포트 목록 매핑
        self.operating_system = {} # a mapping of hostnames to os types  # 호스트 이름 -> OS 종류 매핑
        self.ot_service = None

    def addport(self, ip_address: IPv4Address, port: int):
        self.ports.setdefault(ip_address, []).append(port)

    def clearports(self, ip_address: IPv4Address):
        self.ports[ip_address] = []

    def addos(self, hostname: str, os: OperatingSystemType):
        self.operating_system[hostname] = os

class GreenAbstractSession(Session):
    # Currently a clone of RedAbstractSession
    # a session that remembers previously seen information that can be used by actions
    # 현재는 RedAbstractSession을 그대로 복제한 클래스이다.
    # Green 에이전트(정상 사용자)용 세션으로, 이전에 관찰한 정보를 기억해 행동에 활용한다.
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell', active: bool = True, parent=None, name=None):
        super().__init__(ident, hostname, username, agent, pid, timeout, session_type, active, parent, name)
        self.ports: Dict[IPv4Address, List[int]] = {} # a mapping of ip_addresses to previously seen open ports  # IP 주소 -> 이전에 관찰한 열린 포트 목록 매핑
        self.operating_system = {} # a mapping of hostnames to os types  # 호스트 이름 -> OS 종류 매핑
        self.ot_service = None

    def addport(self, ip_address: IPv4Address, port: int):
        self.ports.setdefault(ip_address, []).append(port)

    def addos(self, hostname: str, os: OperatingSystemType):
        self.operating_system[hostname] = os

class VelociraptorServer(Session):
    # a session that remembers previously seen information that can be used by actions
    # 이전에 관찰한 정보를 기억해 행동에 활용하는 세션이다.
    # (Velociraptor: Blue 측 방어에서 호스트 데이터를 수집하는 엔드포인트 모니터링 도구)
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell', active: bool = True, parent=None, name=None,
                 artifacts=None, num_children=None):
        super().__init__(ident, hostname, username, agent, pid, timeout, session_type, active, parent, name, num_children=num_children)
        self.artifacts = [] if artifacts is None else artifacts  # a list of artifacts that the velociraptor collects  # velociraptor가 수집하는 아티팩트 목록
        self.sus_pids: Dict[str, List[int]] = {}
        self.sus_files = {}

    def add_sus_pids(self, hostname: str, pid: int):
        self.sus_pids.setdefault(hostname, []).append(pid)

class MSFServerSession(Session):

    def __init__(
        self, ident: str, hostname: str, username: str, agent: str, pid: int,
        timeout: int = 0, session_type: str = SessionType.MSF_SERVER, parent=None, name=None,
        num_children=None
    ):
        super().__init__(
            ident, hostname, username, agent, pid, timeout, session_type, parent=parent,
            name=name, num_children=num_children
        )
        self.routes = {}  # routes have the structure sessionid: subnet  # 라우트 구조: 세션 ID -> 서브넷(Subnet)

    def dead_child(self, child_id: int):
        # [설명] 자식 세션을 제거할 때, 부모 동작에 더해 해당 세션의 라우트(routes)도 함께 정리한다.
        super().dead_child(child_id)
        if child_id in self.routes:
            self.routes.pop(child_id)
