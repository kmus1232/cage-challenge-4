# Copyright DST Group. Licensed under the MIT license.

from CybORG.Shared.Enums import PasswordHashType
from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.LocalGroup import LocalGroup


class User(Entity):
    """User entity

    Attributes
    ----------
    username : str
    password : str
    password_hash : str
    bruteforceable : bool
    password_hash_type : str
    groups: List[LocalGroup]
    logged_in : bool
    uid : int
    disabled : bool

    [한국어]
    호스트의 사용자 계정을 나타내는 엔티티.

    속성
    ----
    username : str — 사용자 이름
    password : str — 평문 비밀번호
    password_hash : str — 비밀번호 해시값
    bruteforceable : bool — 브루트포스(무차별 대입)로 비밀번호를 알아낼 수 있는지 여부
    password_hash_type : str — 비밀번호 해시 방식
    groups : List[LocalGroup] — 사용자가 속한 로컬 그룹 목록
    logged_in : bool — 로그인 상태 여부
    uid : int — 사용자 ID
    disabled : bool — 계정 비활성화 여부
    """
    def __init__(self, username: str, uid: int, password: str = None, password_hash: str = None,
                 password_hash_type: str = None, groups: list = None,
                 logged_in: bool = None, bruteforceable: bool = False):
        """Instantiate the User object

        [한국어]
        User 객체를 생성한다.
        """
        super().__init__()
        self.username = username

        self.password = password
        self.password_hash = password_hash
        self.bruteforceable = bruteforceable
        # assert type(bruteforceable) is bool
        # 비밀번호 해시 방식이 지정된 경우에만 문자열을 PasswordHashType 열거형으로 파싱한다.
        if password_hash_type is not None:
            self.password_hash_type = PasswordHashType.parse_string(password_hash_type)
        else:
            self.password_hash_type = None
        self.groups = []
        # 전달된 그룹 딕셔너리들을 LocalGroup 객체로 변환해 그룹 목록에 추가한다.
        if groups is not None:
            for group in groups:
                self.groups.append(LocalGroup(name=group.get('Group Name'), gid=group.get('GID')))
        self.logged_in = logged_in
        self.uid = uid
        self.disabled = False

    def get_state(self):
        """Get the current internal state of the user, as an observation

        [한국어]
        사용자의 현재 내부 상태를 관찰값(Observation) 형태로 반환한다.
        그룹이 있으면 그룹마다 항목을 하나씩 만들고, 없으면 그룹 정보를 뺀 항목 하나만 만든다.
        """
        obs = []

        if len(self.groups) > 0:
            for group in self.groups:
                observation = {"username": self.username, "password": self.password,
                               "password_hash": self.password_hash, "password_hash_type": self.password_hash_type,
                               "logged_in": self.logged_in, "group": group.name, "gid": group.ident}
                obs.append(observation)
        else:
            observation = {"username": self.username, "password": self.password, "password_hash": self.password_hash,
                           "password_hash_type": self.password_hash_type, "logged_in": self.logged_in}
            obs.append(observation)
        return obs

    def add_group(self, group: LocalGroup):
        """Add a group to the user's list of groups.

        Parameters
        ----------
        group : LocalGroup
            group to add

        [한국어]
        사용자의 그룹 목록에 그룹을 하나 추가한다.

        매개변수
        --------
        group : LocalGroup
            추가할 그룹
        """
        if self.groups is None:
            self.groups = [group]
        else:
            self.groups.append(group)

    def disable_user(self):
        """Set user to 'disabled'

        [한국어]
        사용자 계정을 'disabled'(비활성화) 상태로 설정한다.
        """
        self.disabled = True
        return True

    @classmethod
    def load(cls, info: dict):
        # [설명] 시나리오 정의 딕셔너리(info)에서 필드를 뽑아 User 인스턴스를 생성하는 팩토리 메서드.
        return cls(
            username=info.get('username'),
            groups=info.get('Groups'),
            uid=info.get('uid'),
            password=info.get('Password'),
            bruteforceable=info.get('Bruteforceable', False)
        )

    def __str__(self):
        return f'{self.username}'
