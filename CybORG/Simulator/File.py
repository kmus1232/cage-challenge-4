# Copyright DST Group. Licensed under the MIT license.
from datetime import datetime

from CybORG.Shared.Enums import FileType, FileVersion
from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.LocalGroup import LocalGroup
from CybORG.Simulator.User import User
import enum


class File(Entity):
    """A File object present on a host.

    Attributes
    ----------
    create_time : str
    default_permissions : int
    density : int
    file_type : str
    group : str
    group_permissions : int
    last_access_time : str
    last_modified_time : str
    name : str
    path : str
    signed : bool
    user : User
    user_permissions : int
    vendor : str
    version : str

    [한국어]
    호스트(Host)에 존재하는 파일 객체.
    파일의 경로·이름·소유자·권한·종류 등 시뮬레이션에서 다루는 파일 속성을 담는다.

    주요 속성:
    - create_time / last_modified_time / last_access_time : 생성·수정·접근 시각(str)
    - default_permissions / group_permissions / user_permissions : 권한 비트값(int)
    - file_type : 파일 종류, vendor / version : 공급자·버전 정보
    - group : 소속 그룹, user : 소유 사용자(User), name / path : 파일 이름·경로
    - density : 밀도값, signed : 서명 여부(bool)
    """
    def __init__(self, name: str, path: str, user: User, user_permissions: int = None,
                 group: str = None, group_permissions: int = None, default_permissions: int = None,
                 create_time: str = None, last_modified_time: str = None,
                 last_access_time: str = None, file_type: str = None, vendor: str = None, version: str = None,
                 density=0, signed=False):
        super().__init__()
        self.name = name
        self.path = path
        self.user = user
        self.user_permissions = user_permissions
        if self.user_permissions is None and self.user is not None:
            self.group_permissions = 7
        self.group = group
        self.group_permissions = group_permissions
        if self.group_permissions is None and self.group is not None:
            self.group_permissions = 7
        self.default_permissions = default_permissions
        if self.default_permissions is None:
            self.default_permissions = 7
        self.create_time = create_time
        self.last_modified_time = last_modified_time
        # [설명] 문자열로 받은 수정 시각을 "일 월 연 시:분" 형식으로 파싱해 datetime 객체로 변환한다.
        if self.last_modified_time is not None:
            self.last_modified_time = datetime.strptime(self.last_modified_time, "%d %b %Y %H:%M")
        self.last_access_time = last_access_time
        self.file_type = FileType.UNKNOWN
        # [설명] file_type이 문자열로 들어오면 FileType enum 값으로 변환한다. 이미 FileType이면 그대로 사용한다.
        if file_type is not None:
            if type(file_type) is not FileType:
                file_type = FileType.parse_string(file_type)
            self.file_type = file_type
        self.vendor = vendor
        self.version = None
        if version is not None:
            self.version = FileVersion.parse_string(version)

        self.density = density
        self.signed = signed

    def get_state(self):
        """Returns a dictionary that represents the file.

        [한국어]
        파일을 표현하는 딕셔너리를 반환한다. 관찰값(Observation) 등에서 파일 상태를 나타낼 때 쓴다.
        """
        obs = {"path": self.path,
               "name": self.name,
               "vendor": self.vendor,
               "version": self.version,
               "file_type": self.file_type,
               "user_permissions": self.user_permissions,
               "group": self.group,
               "group_permissions": self.group_permissions,
               "default_permissions": self.default_permissions,
               "last_modified_time": self.last_modified_time,
               "user": self.user}
        return obs

    
    def check_executable(self, user: User):
        """Checks if the file is executable by a given user - assumes the user and file are on the same dict.

        [한국어]
        주어진 사용자(User)가 이 파일을 실행할 수 있는지 검사한다. 사용자와 파일이 같은 dict에 있다고 가정한다.
        """
        # [설명] 권한 비트의 최하위 비트(실행 권한)를 % 2로 확인한다. 1이면 실행 가능.
        # default(전체) → group(그룹) → user(소유자) 순으로 하나라도 실행 권한이 있으면 True.
        if self.default_permissions % 2:
            return True
        if self.group in user.groups and self.group_permissions % 2:
            return True
        if self.user == user and self.user_permissions % 2:
            return True
        return False

    def check_readable(self, user: User):
        """Checks readability of file.

        [한국어]
        파일의 읽기 가능 여부를 검사한다.
        """
        # [설명] 권한 비트값이 4 이상이면 읽기 권한(읽기 비트)이 켜진 것으로 본다.
        # default(전체) → group(그룹) → user(소유자) 순으로 검사하고, 사용자명이 'SYSTEM'이면 항상 읽기 가능.
        if self.default_permissions >= 4:
            return True
        if self.group in user.groups and self.group_permissions >= 4:
            return True
        if self.user == user.username and self.user_permissions >= 4:
            return True
        if user.username == 'SYSTEM':
            return True
        return False
