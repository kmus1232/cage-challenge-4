# Copyright DST Group. Licensed under the MIT license.

from inspect import signature

from CybORG.Shared import CybORGLogger
from CybORG.Shared.Enums import SessionType

MAX_SUBNETS = 10
MAX_ADDRESSES = 10
MAX_SESSIONS = 8
MAX_USERNAMES = 10
MAX_PASSWORDS = 10
MAX_PROCESSES = 50
MAX_PORTS = 50
MAX_GROUPS = 15
MAX_FILES = 20
MAX_PATHS = 20
SESSION_TYPES = (
    SessionType.MSF_SERVER, SessionType.VELOCIRAPTOR_SERVER, SessionType.RED_ABSTRACT_SESSION,
    SessionType.GREY_SESSION, SessionType.BLUE_DRONE_SESSION, SessionType.RED_DRONE_SESSION
)


class ActionSpace(CybORGLogger):
    """Action Space of the agent

    Attributes
    ----------
    actions : Dict[Action, bool]
        mapping of agent actions to their validity in the environment
    action_params : Dict[Action, _]
        mapping of actions to params
    allowed_subnets : List[str]
        list of allowed subnets for that action
    subnet : Dict[IPv4Network, bool]
        mapping of subnet networks to the validity of their use in the action
    ip_address : Dict[IPv4Address, bool]
        mapping of IP addresses to the validity of their use in the action
    server_session : dict
    client_session : Dict[int, bool]
        mapping of client session number to validity
    username : Dict[str, bool]
        mapping of username and validity
    password : dict
    process : Dict[int, bool]
        mapping of process number to validity
    port : dict
    hostname : Dict[str, bool]
        mapping of hostname to validity
    agent : Dict[str, bool]
        mapping of agent name to validity

    [한국어]
    에이전트의 행동 공간(Action Space)을 표현하는 클래스.
    에이전트가 선택할 수 있는 행동(Action)과, 그 행동의 인자로 쓸 수 있는
    서브넷·IP·세션·사용자명·프로세스 등 후보값들을 모아 관리한다.
    각 후보값은 `{값: bool}` 형태로 보관하며, bool 값은 그 값이 현재
    행동 공간에서 유효(사용 가능)한지를 나타낸다.

    주요 속성:
    - actions: 에이전트가 취할 수 있는 행동 → 유효성
    - action_params: 각 행동 → 그 행동이 요구하는 인자 목록
    - allowed_subnets: 이 에이전트가 접근 가능한 서브넷 목록
    - subnet / ip_address: 서브넷·IP 주소 → 행동 인자로 쓸 수 있는지
    - server_session / client_session: 서버·클라이언트 세션 번호 → 유효성
    - username / password: 사용자명·비밀번호 → 유효성
    - process / port: 프로세스 번호·포트 → 유효성
    - hostname: 호스트명 → 유효성
    - agent: 에이전트 이름 → 유효성
    """

    def __init__(self, actions, agent, allowed_subnets):
        """Loads the inital information the agent knows about.

        Parameters
        ----------
        actions : List[Action]
            list of actions that the agent can take
        agent : str
            agent name
        allowed_subnets : dict
            subnets the agent is allowed to access

        [한국어]
        에이전트가 처음 알고 있는 초기 정보를 적재한다.

        인자:
        - actions: 에이전트가 취할 수 있는 행동(Action) 목록
        - agent: 에이전트 이름
        - allowed_subnets: 에이전트가 접근 가능한 서브넷
        """
        self.actions = {i: True for i in actions}
        self.action_params = {}
        # [설명] 각 행동(Action)을 자세히 들여다보고, 그 행동이 어떤 인자를
        # 받는지(signature의 parameters)를 미리 추출해 둔다. 이후 행동 공간
        # 크기 계산 시 인자별 후보 개수를 곱하는 데 쓰인다.
        for action in self.actions:
            self.action_params[action] = signature(action).parameters
        self.allowed_subnets = allowed_subnets
        self.subnet = {}
        self.ip_address = {}
        self.server_session = {}
        self.client_session = {i: False for i in range(MAX_SESSIONS)}
        self.username = {}
        self.password = {}
        self.process = {}
        self.port = {}
        self.hostname = {}
        self.agent = {agent: True}

    def get_name(self, action: int) -> str:
        pass

    def get_max_action_space(self):
        """Gets all the max integer values for class attributes.

        Returns
        -------
        max_action : Dict[str, int]
            a dictionary of class attributes and maximum integers

        [한국어]
        각 클래스 속성이 가질 수 있는 최대 정수값을 모아 반환한다.
        (서브넷·IP·세션 등 후보값의 상한선을 담은 딕셔너리)
        """
        max_action = {
            'action': len(self.actions),
            'subnet': MAX_SUBNETS,
            'ip_address': MAX_ADDRESSES,
            'session': MAX_SESSIONS,
            'username': MAX_USERNAMES,
            'password': MAX_PASSWORDS,
            'process': MAX_PROCESSES,
            'port': MAX_PORTS,
            'target_session': MAX_SESSIONS}
        return max_action

    def get_action_space(self):
        """Gets all class attributes.

        Returns
        -------
        max_action : Dict[str, dict]
            a dictionary of class attributes names and values

        [한국어]
        클래스가 보유한 모든 속성을 모아 반환한다.
        get_max_action_space가 후보값의 최대 "개수"만 돌려주는 것과 달리,
        이 메서드는 실제 속성 값(서브넷·IP·세션 등의 후보 딕셔너리)을 통째로 담아 준다.
        """
        max_action = {
            'action': self.actions,
            'allowed_subnets': self.allowed_subnets,
            'subnet': self.subnet,
            'ip_address': self.ip_address,
            'session': self.server_session,
            'username': self.username,
            'password': self.password,
            'process': self.process,
            'port': self.port,
            'target_session': self.client_session,
            'agent': self.agent,
            'hostname': self.hostname
        }
        return max_action

    def reset(self, agent):
        """Resets all class attributes to state after `__init__`.

        Parameters
        ----------
        agent : str
            agent name

        [한국어]
        모든 클래스 속성을 `__init__` 직후 상태로 되돌린다.
        에피소드(Episode)를 다시 시작할 때 그동안 관찰로 쌓인 후보값들을 비우고
        초기 상태로 리셋하는 용도다.

        인자:
        - agent: 에이전트 이름
        """
        self.subnet = {}
        self.ip_address = {}
        self.server_session = {}
        self.client_session = {i: False for i in range(MAX_SESSIONS)}
        self.username = {}
        self.password = {}
        self.process = {}
        self.port = {}
        self.agent = {agent: True}

    def get_max_actions(self, action):
        # [설명] 특정 행동(Action) 하나가 만들어 낼 수 있는 구체적 인스턴스의
        # 최대 개수를 구한다. 행동이 받는 각 인자(예: subnet, ip_address)마다
        # 현재 후보값 개수를 곱해 나가는 방식이다. 예를 들어 인자가 subnet,
        # ip_address 둘이고 후보가 각각 3개, 4개면 3 * 4 = 12개가 된다.
        params = self.action_params[action]
        size = 1
        # [설명] 인자 이름 → 그 인자의 후보값을 담은 딕셔너리. 아래 루프에서
        # 인자 이름을 키로 후보 개수(len)를 찾아 곱하는 데 쓴다.
        len_dict = {
            "session": self.server_session,
            "target_session": self.client_session,
            "subnet": self.subnet,
            "ip_address": self.ip_address,
            "username": self.username,
            "password": self.password,
            "process":self.process,
            "port": self.port,
            "agent": self.agent
        }
        for param in params.keys():
            if param not in len_dict:
                raise NotImplementedError(
                    f"Param '{param}' in action '{action.__name__}' has no"
                    " code to parse its size for action space"
                )
            size *= len(len_dict[param])
        return size

    def update(self, observation: dict, known: bool = True):
        """Updates the ActionSpace class attributes depending on the observation parameter and whether the attribute info is known.
        
        Parameters
        ----------
        observation : dict
            the current observation to update the action space with.
        known : bool

        [한국어]
        관찰값(Observation)을 바탕으로 ActionSpace의 속성들을 갱신한다.
        관찰에서 새로 드러난 호스트명·서브넷·IP·프로세스·포트·사용자명·세션 등을
        행동 인자의 후보값으로 등록한다.

        인자:
        - observation: 행동 공간을 갱신할 현재 관찰값
        - known: 등록할 후보값의 유효성 플래그. 후보 딕셔너리에 이 값으로 기록되며,
          관찰로 알게 된 정보면 True, 아니면 False를 넣는다.
        """
        if observation is None:
            return

        # [설명] 관찰값은 {호스트별 키: 호스트 정보 dict} 구조다. 각 호스트 정보를
        # 훑어 인자 후보(서브넷·IP·프로세스·포트·사용자명·세션)를 추출한다.
        for key, info in observation.items():
            # 메타 키(success/Valid/action)이거나 dict가 아니면 건너뛴다.
            # (호스트 정보 dict만 파싱 대상이다.)
            if (key in ("success", 'Valid', 'action')) or (not isinstance(info, dict)):
                continue
            # 시스템 정보의 호스트명을 후보로 등록
            if "System info" in info and "Hostname" in info["System info"]:
                self.hostname[info["System info"]["Hostname"]] = known
            # 인터페이스 목록에서 서브넷·IP 주소를 후보로 등록
            for interface in info.get("Interface", []):
                if "Subnet" in interface:
                    self.subnet[interface["Subnet"]] = known
                if "ip_address" in interface:
                    self.ip_address[interface["ip_address"]] = known

            # 프로세스 목록에서 PID를 후보로 등록하고,
            # 각 프로세스의 연결(Connection)에서 로컬·원격 포트를 후보로 등록
            for process in info.get("Processes", []):
                if "PID" in process:
                    self.process[process["PID"]] = known
                for connection in process.get("Connections", []):
                    if "local_port" in connection:
                        self.port[connection["local_port"]] = known
                    if "remote_port" in connection:
                        self.port[connection["remote_port"]] = known

            # 사용자 정보에서 사용자명·비밀번호를 후보로 등록
            for user in info.get("User Info", []):
                if "username" in user:
                    self.username[user["username"]] = known
                if "Password" in user:
                    self.password[user["Password"]] = known

            # [설명] 세션은 이 에이전트(self.agent에 등록된 이름)의 것만 처리한다.
            # 세션 타입이 SESSION_TYPES(서버형 세션 집합)에 속하면 server_session에도
            # 등록하고, 모든 세션은 공통으로 client_session(target_session 후보)에 등록한다.
            for session in info.get("Sessions", []):
                if "session_id" in session and session['agent'] in self.agent:
                    if "Type" in session and (session["Type"] in SESSION_TYPES):
                        self.server_session[session["session_id"]] = known
                    self.client_session[session["session_id"]] = known
