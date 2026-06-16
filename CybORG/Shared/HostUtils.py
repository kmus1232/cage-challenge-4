# Copyright DST Group. Licensed under the MIT license.
import datetime
from ipaddress import IPv4Address, IPv4Network

import CybORG.Shared.Enums as CyEnums


class NetworkInterface:
    """A class for storing network interface information

    [한국어]
    호스트의 네트워크 인터페이스 정보(인터페이스 이름, IP 주소, 서브넷 등)를
    저장하는 클래스다.
    """

    def __init__(self,
                 hostid: str = None,
                 interface_name: str = None,
                 ip_address: IPv4Address = None,
                 subnet: IPv4Network = None):
        self.hostid = hostid
        self.interface_name = interface_name
        self.ip_address = IPv4Address(ip_address)
        self.subnet = IPv4Network(subnet)

    def get_info(self) -> dict:
        """Return network interface as dict.

        Keys of dict match arguments of Observation.add_interface_info()

        [한국어]
        네트워크 인터페이스 정보를 dict로 반환한다.
        dict의 키는 Observation.add_interface_info()의 인자와 일치한다.
        """
        return {
            "hostid": self.hostid,
            "interface_name": self.interface_name,
            "ip_address": self.ip_address,
            "subnet": self.subnet
        }

    def __str__(self):
        output = [f"{self.__class__.__name__}:"]
        for k, v in self.get_info().items():
            if v is None:
                continue
            output.append(f"{k}={v}")
        return f" ".join(output)


class File:
    """A dataclass for storing information about a single file

    [한국어]
    단일 파일의 정보(이름, 경로, 소유자/그룹 권한, 파일 타입, 버전 등)를
    저장하는 데이터 클래스다.
    """

    def __init__(self,
                 name: str,
                 path: str,
                 file_type: str = None,
                 vendor: str = None,
                 version: str = None,
                 user: str = None,
                 user_permissions: int = None,
                 group: str = None,
                 group_permissions: int = None,
                 default_permissions: int = None,
                 last_modified_time: datetime.datetime = None):
        self.name = name
        self.path = path
        self.user = user
        self.group = group
        self.vendor = vendor

        self.user_permissions = user_permissions
        if self.user_permissions is None and self.user is not None:
            self.group_permissions = 7

        self.group_permissions = group_permissions
        if self.group_permissions is None and self.group is not None:
            self.group_permissions = 7

        self.default_permissions = default_permissions
        if self.default_permissions is None:
            self.default_permissions = 7

        self.last_modified_time = last_modified_time
        if self.last_modified_time is not None:
            self.last_modified_time = datetime.strptime(
                self.last_modified_time, "%d %b %Y %H:%M"
            )

        self.file_type = file_type
        if file_type is None:
            self.file_type = CyEnums.FileType.UNKNOWN
        elif not isinstance(file_type, CyEnums.FileType):
            self.file_type = CyEnums.FileType.parse_string(file_type)

        self.version = version
        if version is not None and not isinstance(CyEnums.FileVersion):
            self.version = CyEnums.FileVersion.parse_string(version)

    def get_info(self) -> dict:
        """Return network interface as dict.

        Keys of dict match arguments of Observation.add_file_info()

        [한국어]
        파일 정보를 dict로 반환한다.
        dict의 키는 Observation.add_file_info()의 인자와 일치한다.
        """
        return {
            "path": self.path,
            "name": self.name,
            "vendor": self.vendor,
            "version": self.version,
            "file_type": self.file_type,
            "user": self.user,
            "user_permissions": self.user_permissions,
            "group": self.group,
            "group_permissions": self.group_permissions,
            "default_permissions": self.default_permissions,
            "last_modified_time": self.last_modified_time
        }

    def __str__(self):
        output = [f"{self.__class__.__name__}:"]
        for k, v in self.get_info().items():
            if v is None:
                continue
            output.append(f"{k}={v}")
        return f" ".join(output)


class Credentials:
    """A class for storing a set of credentials

    [한국어]
    하나의 자격 증명 묶음(사용자명, 비밀번호, 키 경로, 해시 등)을 저장하는
    클래스다.
    """

    def __init__(self,
                 username: str,
                 password: str = None,
                 key_path: str = None,
                 password_hash: str = None,
                 password_hash_type: str = None,
                 groups: list = None):
        self.username = username
        self.password = password
        self.key_path = key_path
        self.password_hash = password_hash
        self.password_hash_type = password_hash_type
        self.groups = [] if groups is None else groups

    def get_info(self) -> dict:
        """Return credentials as dict

        Keys of dict match arguments of Observation.add_user_info()

        [한국어]
        자격 증명 정보를 dict로 반환한다.
        dict의 키는 Observation.add_user_info()의 인자와 일치한다.
        """
        return {
            "username": self.username,
            "password": self.password,
            "password_hash": self.password_hash,
            "password_hash_type": self.password_hash_type,
            "key_path": self.key_path
        }

    def __str__(self):
        output = [f"{self.__class__.__name__}:"]
        for k, v in self.get_info().items():
            if v is None:
                continue
            output.append(f"{k}={v}")
        return f" ".join(output)


class OperatingSystemInfo:
    """A class for storing information about the OS of a VM

    [한국어]
    VM의 운영체제 정보(OS 타입, 배포판, 버전, 커널, 아키텍처, 패치)를 저장하는
    클래스다.
    """

    def __init__(self,
                 os_type: CyEnums.OperatingSystemType = None,
                 dist: CyEnums.OperatingSystemDistribution = None,
                 version: CyEnums.OperatingSystemVersion = None,
                 kernel: CyEnums.OperatingSystemKernelVersion = None,
                 architecture: CyEnums.Architecture = None,
                 patch: CyEnums.OperatingSystemPatch = None):
        self.os_type = os_type
        self.dist = dist
        self.version = version
        self.kernel = kernel
        self.architecture = architecture
        self.patch = patch

    def get_info(self) -> dict:
        """Return OS info as dict

        Keys of dict match arguments of Observation.add_system_info()

        [한국어]
        OS 정보를 dict로 반환한다.
        dict의 키는 Observation.add_system_info()의 인자와 일치한다.
        """
        return {
            "os_type": self.os_type,
            "os_distribution": self.dist,
            "os_verson": self.version,
            "os_kernel": self.kernel,
            "os_patches": self.patch,
            "architecture": self.architecture
        }

    def __str__(self):
        output = [f"{self.__class__.__name__}:"]
        for k, v in self.get_info().items():
            if v is None:
                continue
            output.append(f"{k}={v}")
        return f" ".join(output)


class Image:
    """An class for storing VM Image information

    [한국어]
    VM 이미지 정보(이름, 서비스 목록, OS 정보, 자격 증명, root 사용자, 파일 등)를
    저장하는 클래스다.
    """

    def __init__(self,
                 name: str,
                 services: list = None,
                 os_info: OperatingSystemInfo = None,
                 credentials: dict = None,
                 root_user: str = None,
                 key_access: bool = False,
                 files: dict = None,
                 aux_info: dict = None):
        """
        Parameters
        ----------
        name : str
            The name of the image. This is used to distinguish between images
            with the same OS type, distribution and version in a human
            readable format. e.g. between standard ubuntu 14.04 and the
            Metasploitable 3 ubuntu 14.04
        services : list, optional
            Service objects defining services running on machine (default=None)
        os_info : str, optional
            image os information (i.e. type, distribution, version)
            (default=None)
        credentials : dict, optional
            map of user to credentials for the VM image (default=None)
        root_user : str, optional
            the root user for the image. This is the user whose credentials are
            used when configuring any instances using this image (default=None)
        key_access : bool, optional
            whether SSH access to instance is restricted to key only
            (default=False)
        files : dict, optional
            any known/specified files that are on the image (default=None)
        aux_info: dict, optional
            any extra Image specific information (e.g. MSF or Host monitoring
            info0 (Default=None)

        [한국어]
        파라미터 설명:
        - name : 이미지 이름. 같은 OS 타입/배포판/버전을 가진 이미지를 사람이
          읽기 쉽게 구분하기 위한 이름이다(예: 표준 ubuntu 14.04 vs
          Metasploitable 3 ubuntu 14.04).
        - services : 머신에서 실행 중인 서비스를 정의하는 Service 객체 목록.
        - os_info : 이미지의 OS 정보(타입, 배포판, 버전).
        - credentials : VM 이미지의 사용자별 자격 증명 매핑.
        - root_user : 이미지의 root 사용자. 이 이미지로 인스턴스를 구성할 때
          사용하는 자격 증명의 주인이 되는 사용자다.
        - key_access : 인스턴스 SSH 접근을 키로만 제한하는지 여부.
        - files : 이미지에 존재하는 것으로 알려진/지정된 파일들.
        - aux_info : 이미지에 특화된 추가 정보(예: MSF나 호스트 모니터링 정보).
        """
        self.name = name
        self.services = services
        self.os_info = OperatingSystemInfo if os_info is None else os_info
        self.credentials = {} if credentials is None else credentials
        self.root_user = root_user
        self.key_access = key_access
        self.files = {} if files is None else files
        self.aux_info = {} if aux_info is None else aux_info
        assert root_user is None or root_user in credentials, \
            f"Root user of Image must have matching entry in credentials"

    def get_root_user_creds(self) -> Credentials:
        """Get the credentials of the root user of Image.

        Returns
        -------
        Credentials
            Root user credentials

        Raises
        ------
        AttributeError
            If no valid credentials can be found

        Notes
        -----
        If root_user attribute of image is not defined, this will return the
        first user in the image credentials dict

        [한국어]
        이미지의 root 사용자 자격 증명을 반환한다.
        - 반환값: root 사용자의 Credentials.
        - 예외: 유효한 자격 증명을 찾지 못하면 AttributeError를 던진다.
        - 참고: root_user 속성이 정의돼 있지 않으면, 자격 증명 dict의 첫 번째
          사용자를 반환한다.
        """
        if self.root_user is not None:
            return self.credentials[self.root_user]
        # [설명] root_user가 지정되지 않은 경우, 자격 증명을 순회하며 키 접근만
        # 허용(key_access)이 아니거나 키 경로(key_path)가 있는 첫 사용자를 root로 본다.
        for username, creds in self.credentials.items():
            if not self.key_access or creds.key_path is not None:
                return creds
        raise AttributeError("No valid root user credentials found for {self}")

    def __str__(self):
        creds = [f"{u}: {c}" for u, c in self.credentials.items()]
        creds_str = "[" + ", ".join(creds) + "]"
        output = [f"{self.__class__.__name__}:",
                  f"Name={self.name}"
                  f"Services={self.services}"
                  f"OS Info={str(self.os_info)}"
                  f"Credentials={creds_str}",
                  f"Root User={self.root_user}"
                  f"Key Access={self.key_access}",
                  f"Files={self.files}",
                  f"Aux Info={self.aux_info}"]
        return "  ".join(output)

    def __eq__(self, other):
        if not isinstance(other, Image):
            return False
        return (other.name == self.name
                and other.services == self.services
                and other.os_info == self.os_info
                and other.credentials == self.credentials
                and other.files == self.files
                and other.aux_info == self.aux_info)
