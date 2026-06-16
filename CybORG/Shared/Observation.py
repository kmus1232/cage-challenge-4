## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

import pprint
from copy import deepcopy
from datetime import datetime
from typing import Union, Optional
from ipaddress import IPv4Network, IPv4Address

import CybORG.Shared.Enums as CyEnums

BROADCAST_ADDRESS = IPv4Address('0.0.0.0')

class Observation:
    """Class that holds the observation data for the environment at a step in the episode

    Attributes
    ----------
    data : Dict[str, _]
        dictionary of agent observation data
    raw : str

    [한국어]
    에피소드의 한 스텝(step)에서 환경의 관찰값(Observation) 데이터를 담는 클래스.
    에이전트가 그 스텝에 무엇을 관찰했는지를 dict 형태로 모아둔다.

    속성
    - data : 에이전트 관찰값을 담는 dict. 호스트별 정보(프로세스/인터페이스/
      파일/사용자/세션 등)와 행동(Action)의 성공 여부("success")가 들어간다.
    - raw : 가공 전 원본(raw) 관찰값을 담는 문자열.
    """

    def __init__(self, success: Union[bool, CyEnums.TernaryEnum] = CyEnums.TernaryEnum.UNKNOWN, msg:str = None):
        """
        Parameters
        ----------
        success : Union[bool, CyEnums.TernaryEnum]
            success of the action in the observation
        msg : str
            the message, if any, communicated by the agents

        [한국어]
        관찰값을 초기화한다.

        매개변수
        - success : 이 관찰값이 대응하는 행동(Action)의 성공 여부.
          bool 또는 TernaryEnum(TRUE/FALSE/UNKNOWN 3값)을 받는다.
        - msg : 에이전트들이 주고받은 메시지(있을 경우).
        """
        # success가 TernaryEnum이 아니면(예: bool) TernaryEnum 값으로 변환한다.
        if not isinstance(success, CyEnums.TernaryEnum):
            success = CyEnums.TernaryEnum.parse_bool(success)
        self.data = {"success": success}

        if msg is not None:
            self.data['message'] = msg
        self.raw = ''

    def get_dict(self):
        """Returns the data of the observation

        [한국어]
        관찰값 dict(data)를 그대로 반환한다.
        """
        return self.data

    def set_success(self, success: Union[bool, CyEnums.TernaryEnum]):
        """Sets the success value of the data dictionary

        Parameters
        ----------
        success : Union[bool, CyEnums.TrinaryEnum]

        [한국어]
        data dict의 "success"(행동 성공 여부) 값을 설정한다.
        bool로 들어오면 TernaryEnum 값으로 변환해 저장한다.
        """
        if isinstance(success, bool):
            success = CyEnums.TernaryEnum.parse_bool(success)
        self.data["success"] = success

    def add_process(self,
                    hostid: str = None,
                    pid: int = None,
                    PID: int = None,
                    parent_pid: int = None,
                    process_name: str = None,
                    program_name: str = None,
                    service_name: str = None,
                    username: str = None,
                    path: str = None,
                    local_port: int = None,
                    remote_port: int = None,
                    local_address: Union[str, IPv4Address] = None,
                    remote_address: Union[str, IPv4Address] = None,
                    app_protocol: str = None,
                    transport_protocol: str = None,
                    status: str = None,
                    Status: str = None,
                    process_type: str = None,
                    process_version: str = None,
                    vulnerability: str = None,
                    properties: Optional[list[str]] = None,
                    **kwargs):
        """Adds a new process to a host in the observation.
        
        Parameters
        ----------
        hostid: str
        pid: int
        parent_pid: int
        process_name: str
        program_name: str
        service_name: str
        username: str
        path: str
        local_port: int
        remote_port: int
        local_address: Union[str, IPv4Address]
        remote_address: Union[str, IPv4Address]
        app_protocol: str
        transport_protocol: str
        status: str
        process_type: str
        process_version: str
        vulnerability: str
        properties: Optional[list[str]]

        [한국어]
        관찰값 안의 특정 호스트에 프로세스(Process) 정보를 추가한다.
        같은 PID의 프로세스가 이미 있으면 기존 항목을 꺼내 갱신(병합)한다.
        포트·주소·프로토콜 등 연결 정보가 함께 들어오면 Connections에 묶어 넣는다.

        매개변수: 호스트 id, PID, 부모 PID, 프로세스/프로그램/서비스 이름,
        사용자명, 경로, 로컬/원격 포트·주소, 애플리케이션/전송 프로토콜, 상태,
        프로세스 종류·버전, 취약점(vulnerability), 속성(properties) 등.
        """
        if hostid is None:
            hostid = str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Processes", [])

        new_process = {}

        # pid가 None이면 대문자 PID 인자 값을 대신 사용한다(둘 다 받는 호환 처리).
        pid = PID if pid is None else pid
        if pid is not None:
            pid = int(pid)
            if pid < 0:
                raise ValueError
            # [설명] 같은 PID의 기존 프로세스가 있으면 그 항목을 꺼내 new_process로
            # 삼고(목록에서 제거), 아래에서 새 정보를 덧붙여 다시 추가한다. 즉
            # 중복 생성 대신 기존 항목을 갱신(병합)하는 방식이다.
            for old_process in self.data[hostid]["Processes"]:
                if old_process.get("PID", None) == pid:
                    new_process = old_process
                    self.data[hostid]["Processes"].remove(old_process)
                    break
            new_process["PID"] = pid

        if parent_pid is not None:
            new_process["PPID"] = int(parent_pid)

        if process_name is not None:
            new_process["process_name"] = process_name
            if isinstance(process_name, str):
                process_name = CyEnums.ProcessName.parse_string(process_name)
            new_process["Known Process"] = process_name

        if program_name is not None:
            if isinstance(program_name, str):
                program_name = CyEnums.FileType.parse_string(program_name)
            new_process["Program Name"] = program_name

        if service_name is not None:
            new_process["service_name"] = service_name

        if username is not None:
            new_process["username"] = username

        if path is not None:
            new_process["Path"] = path
            new_process["Known Path"] = CyEnums.Path.parse_string(path)

        new_connection = {}
        new_process.setdefault("Connections", [])

        if local_port is not None:
            new_connection["local_port"] = int(local_port)

        if remote_port is not None:
            new_connection["remote_port"] = int(remote_port)

        if local_address is not None:
            if isinstance(local_address, str):
                local_address = IPv4Address(local_address)
            new_connection["local_address"] = local_address
            self.add_interface_info(hostid=hostid, ip_address=local_address)

        if remote_address is not None:
            if isinstance(remote_address, str):
                remote_address = IPv4Address(remote_address)
            new_connection["remote_address"] = remote_address

        if transport_protocol is not None:
            if isinstance(transport_protocol, str):
                transport_protocol = CyEnums.TransportProtocol.parse_string(transport_protocol)
            new_connection["Transport Protocol"] = transport_protocol

        if app_protocol is not None:
            if isinstance(app_protocol, str):
                app_protocol = CyEnums.AppProtocol.parse_string(app_protocol)
            new_connection["Application Protocol"] = app_protocol

        status = status or Status
        if status is not None:
            if isinstance(status, str):
                status = CyEnums.ProcessState.parse_string(status)
            new_connection["Status"] = status

        # 연결 정보가 있으면 Connections에 추가하고, 비어 있으면 빈 Connections 키를 제거한다.
        if new_connection:
            new_process["Connections"].append(new_connection)
        elif new_process["Connections"] == []:
            new_process.pop("Connections")

        if process_type is not None:
            if isinstance(process_type, str):
                process_type = CyEnums.ProcessType.parse_string(process_type)
            new_process["process_type"] = process_type

        if process_version is not None:
            if isinstance(process_version, str):
                process_version = CyEnums.ProcessVersion.parse_string(process_version)
            new_process["Process Version"] = process_version

        if properties is not None:
            new_process["Properties"] = properties

        if vulnerability is not None:
            new_process.setdefault("Vulnerability", [])
            if isinstance(vulnerability, str):
                vulnerability = CyEnums.Vulnerability.parse_string(vulnerability)
            new_process["Vulnerability"].append(vulnerability)

        self.data[hostid]["Processes"].append(new_process)

        # [설명] 실제로 채워진 프로세스 정보가 하나도 없어 호스트에 빈 프로세스만
        # 남은 경우, 의미 없는 항목이므로 해당 호스트 자체를 data에서 제거한다.
        if self.data[hostid] == {"Processes": [{}]}:
            self.data.pop(hostid)

    def add_system_info(self,
                        hostid: str = None,
                        hostname: str = None,
                        os_type: str = None,
                        os_distribution: str = None,
                        os_version: str = None,
                        os_kernel: str = None,
                        os_patches: list = None,
                        architecture: str = None,
                        local_time: datetime = None,
                        position: tuple = None,
                        **kwargs):
        """ And new system information to a specific host in the observation.
        
        Parameters
        ----------
        hostid: str
        hostname: str
        os_type: str
        os_distribution: str
        os_version: str
        os_kernel: str
        os_patches: list
        architecture: str
        local_time: datetime
        position: tuple

        [한국어]
        관찰값 안의 특정 호스트에 시스템 정보(System info)를 추가한다.
        호스트명, OS 종류·배포판·버전·커널, OS 패치 목록, 아키텍처,
        로컬 시각, 위치(position) 등을 담는다.
        문자열로 들어온 값은 대응하는 Enum 값으로 변환해 저장한다.
        """
        # hostid가 없으면 현재 data 크기를 문자열로 만들어 임시 id로 쓴다.
        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("System info", {})
        sys_info: dict = self.data[hostid]["System info"]

        hostname = hostname or kwargs.get("Hostname", None)
        if hostname is not None:
            sys_info["Hostname"] = hostname

        os_type = os_type or kwargs.get("OSType", None)
        if os_type is not None:
            if isinstance(os_type, str):
                os_type = CyEnums.OperatingSystemType.parse_string(os_type)
            sys_info["OSType"] = os_type

        os_distribution = os_distribution or kwargs.get("OSDistribution", None)
        if os_distribution is not None:
            if isinstance(os_distribution, str):
                os_distribution = CyEnums.OperatingSystemDistribution.parse_string(os_distribution)
            sys_info["OSDistribution"] = os_distribution

        os_version = os_version or kwargs.get("OSVersion", None)
        if os_version is not None:
            if isinstance(os_version, str):
                os_version = CyEnums.OperatingSystemVersion.parse_string(os_version)
            sys_info["OSVersion"] = os_version

        os_kernel = os_kernel or kwargs.get("OSKernelVersion", None)
        if os_kernel is not None:
            if isinstance(os_kernel, str):
                os_kernel = CyEnums.OperatingSystemKernelVersion.parse_string(os_kernel)
            sys_info["OSKernelVersion"] = os_kernel

        os_patches = os_patches or kwargs.get("os_patches", None)
        if os_patches is not None:
            for patch in os_patches:
                if isinstance(patch, str):
                    patch = CyEnums.OperatingSystemPatch.parse_string(patch)
                sys_info.setdefault("os_patches", []).append(patch)

        architecture = architecture or kwargs.get("Architecture", None)
        if architecture is not None:
            if isinstance(architecture, str):
                architecture = CyEnums.Architecture.parse_string(architecture)
            sys_info["Architecture"] = architecture

        local_time = local_time or kwargs.get("Local Time", None)
        if local_time is not None:
            sys_info["Local Time"] = local_time

        if position is not None:
            sys_info['position'] = position

    def update_file_with_kwargs(self, kwargs):
        # TEMPORARY FOR REFACTORING. DELETE WHEN DONE.
        # [설명] 리팩터링 중 임시 디버깅용. kwargs로 들어온 키들을 keys.txt에
        # 누적 기록해 어떤 키가 쓰이는지 파악하기 위한 코드이며, 작업 완료 시 삭제 예정.
        filename = "./keys.txt"
        if kwargs:
            existing_keys = set()
            try:
                with open(filename, 'r') as file:
                    for line in file:
                        existing_keys.add(line.strip())
            except FileNotFoundError:
                pass
            with open(filename, 'a') as file:
                for key in kwargs:
                    if key not in existing_keys:
                        file.write(key + '\n')

    def add_interface_info(self,
                           hostid: str = None,
                           interface_name: str = None,
                           ip_address: Union[str, IPv4Address] = None,
                           subnet: Union[str, IPv4Network] = None,
                           Subnet = None,
                           blocked_ips: list = None,
                           network_connections: list = None,
                           **kwargs):
        """Add new interface information to a specifc host in the observation.
        
        Parameters
        ----------
        hostid: str
        interface_name: str
        ip_address: Union[str, IPv4Address]
        subnet: Union[str, IPv4Network]
        blocked_ips: list

        [한국어]
        관찰값 안의 특정 호스트에 네트워크 인터페이스(Interface) 정보를 추가한다.
        인터페이스명, IP 주소, 서브넷(Subnet), 차단 IP 목록(blocked_ips),
        네트워크 연결 정보 등을 담는다.
        같은 인터페이스명·IP를 가진 기존 항목이 있으면 꺼내 갱신(병합)한다.
        """
        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Interface", [])

        new_interface = {}

        if interface_name is not None:
            for interface in self.data[hostid]["Interface"]:
                if interface.get("interface_name", None) == interface_name:
                    new_interface = interface
                    self.data[hostid]["Interface"].remove(interface)
            new_interface["interface_name"] = interface_name

        if ip_address is not None:
            if isinstance(ip_address, str):
                ip_address = IPv4Address(ip_address)
            # [설명] 브로드캐스트 주소(0.0.0.0)는 특정 호스트 정보로 의미가 없으므로
            # 인터페이스에 추가하지 않고, 비어 있는 Interface 키는 정리한 뒤 반환한다.
            if ip_address == BROADCAST_ADDRESS:
                if self.data[hostid]["Interface"] == []:
                    self.data[hostid].pop("Interface")
                return
            # [설명] 같은 IP를 가진 기존 인터페이스들을 훑어 병합한다. 정보가 더 많은
            # (키 개수가 큰) 쪽을 기준으로 삼고, 키 개수가 같으면 누락된
            # interface_name·Subnet만 보충한다. 병합한 기존 항목은 목록에서 제거한다.
            for interface in self.data[hostid]["Interface"]:
                if interface.get("ip_address", None) != ip_address:
                    continue
                if len(interface) > len(new_interface):
                    new_interface = interface
                elif len(interface) == len(new_interface):
                    for k in ["interface_name", "Subnet"]:
                        if k in interface and k not in new_interface:
                            new_interface[k] = interface[k]
                self.data[hostid]["Interface"].remove(interface)
            new_interface["ip_address"] = ip_address

        subnet = subnet or Subnet
        if subnet is not None:
            if isinstance(subnet, str):
                subnet = IPv4Network(subnet)
            new_interface["Subnet"] = subnet

        if blocked_ips is not None:
            new_interface["blocked_ips"] = blocked_ips

        if network_connections is not None:
            new_interface['network_connections'] = network_connections

        self.data[hostid]["Interface"].append(new_interface)

        # 실제 채워진 내용 없이 빈 인터페이스만 남으면 Interface 키를 제거한다.
        if self.data[hostid]["Interface"] == [{}]:
            self.data[hostid].pop("Interface")

    def add_file_info(self,
                      hostid: str = None,
                      path: str = None,
                      name: str = None,
                      vendor: str = None,
                      version: str = None,
                      file_type: str = None,
                      user: str = None,
                      user_permissions: int = None,
                      group: str = None,
                      group_permissions: int = None,
                      default_permissions: int = None,
                      last_modified_time: datetime = None,
                      signed: bool = None,
                      density: float = None,
                      **kwargs):
        """Add new file information to a specific host in the observation.
        
        Parameters
        ----------
        hostid: str
        path: str
        name: str
        vendor: str
        version: str
        file_type: str
        user: str
        user_permissions: int
        group: str
        group_permissions: int
        default_permissions: int
        last_modified_time: datetime
        signed: bool
        density: float

        [한국어]
        관찰값 안의 특정 호스트에 파일(File) 정보를 추가한다.
        경로, 파일명, 벤더, 버전, 파일 종류, 소유 사용자·그룹과 각 권한,
        기본 권한, 최종 수정 시각, 서명 여부(signed), 밀도(density) 등을 담는다.
        파일명과 경로가 모두 일치하는 기존 항목이 있으면 꺼내 갱신(병합)한다.
        """

        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Files", [])

        new_file = {}
        path = path or kwargs.get("Path", None)
        if path is not None:
            new_file["Path"] = path
            new_file["Known Path"] = CyEnums.Path.parse_string(path)

        name = name or kwargs.get("File Name", None)
        if name is not None:
            new_file["File Name"] = name
            new_file["Known File"] = CyEnums.FileType.parse_string(name)

        # [설명] 파일명과 경로가 모두 같은 기존 파일이 있으면 그 항목을 꺼내
        # new_file로 삼고(목록에서 제거), 아래에서 새 정보를 덧붙여 갱신한다.
        if name is not None and path is not None:
            for file in self.data[hostid]["Files"]:
                if file.get("File Name", None) == name and file.get("Path", None) == path:
                    self.data[hostid]["Files"].remove(file)
                    new_file = file
                    break

        vendor = vendor or kwargs.get("Vendor", None)
        if vendor is not None:
            new_file["Vendor"] = CyEnums.Vendor.parse_string(vendor)

        version = version or kwargs.get("Version", None)
        if version is not None:
            new_file["Version"] = version

        file_type = file_type or kwargs.get("Type", None)
        if file_type is not None:
            if isinstance(file_type, str):
                file_type = CyEnums.FileType.parse_string(file_type)
            new_file["Type"] = file_type

        user = user or kwargs.get("username", None)
        if user is not None:
            new_file["username"] = user

        user_permissions = user_permissions or kwargs.get("User Permissions", None)
        if user_permissions is not None:
            new_file["User Permissions"] = user_permissions

        group = group or kwargs.get("Group Name", None)
        if group is not None:
            new_file["Group Name"] = group

        group_permissions = group_permissions or kwargs.get("Group Permissions", None)
        if group_permissions is not None:
            new_file["Group Permissions"] = group_permissions

        default_permissions = default_permissions or kwargs.get("Default Permissions", None)
        if default_permissions is not None:
            new_file["Default Permissions"] = default_permissions

        last_modified_time = last_modified_time or kwargs.get("Last Modified Time", None)
        if last_modified_time is not None:
            new_file["Last Modified Time"] = last_modified_time

        signed = signed or kwargs.get('Signed', None)
        if signed is not None:
            new_file['Signed'] = signed

        density = density or kwargs.get('Density', None)
        if density is not None:
            new_file['Density'] = density

        self.data[hostid]["Files"].append(new_file)

    def add_user_info(self,
                      hostid: str = None,
                      group_name: str = None,
                      gid: int = None,
                      username: str = None,
                      uid: int = None,
                      password: str = None,
                      password_hash: str = None,
                      password_hash_type: str = None,
                      logged_in: bool = None,
                      key_path: str = None,
                      Groups: list = None,
                      **kwargs):
        """Add user information to a host in the observation.
        
        Parameters
        ----------
        hostid: str
        group_name: str
        gid: int
        username: str
        uid: int
        password: str
        password_hash: str
        password_hash_type: str
        logged_in: bool
        key_path: str

        [한국어]
        관찰값 안의 특정 호스트에 사용자(User) 정보를 추가한다.
        사용자명·uid, 비밀번호·해시·해시 종류, 로그인 여부, 키 경로와
        소속 그룹(group_name/gid 또는 Groups 목록) 정보를 담는다.
        같은 사용자명·그룹이 있으면 기존 항목을 갱신(병합)한다.
        """
        hostid = hostid or str(len(self.data))

        # only add user to dict if username or uid is known
        # [설명] 사용자명 또는 uid 중 하나라도 있어야 사용자 항목을 만든다.
        # 둘 다 없으면 식별 불가능하므로 추가하지 않는다.
        if username is not None or uid is not None:
            self.data.setdefault(hostid, {})
            self.data[hostid].setdefault("User Info", [])

            new_user = {}

            if username is not None:
                new_user["username"] = username
                for user in self.data[hostid]["User Info"]:
                    if user.get("username", None) == username:
                        new_user = user
                        self.data[hostid]["User Info"].remove(user)

            if uid is not None:
                new_user["uid"] = uid

            password = password or kwargs.get("Password", None)
            if password is not None:
                new_user["Password"] = password

            if password_hash is not None:
                new_user["password_hash"] = password_hash

            if password_hash_type is not None:
                if isinstance(password_hash_type, str):
                    password_hash_type = CyEnums.PasswordHashType.parse_string(password_hash_type)
                new_user["password_hash_type"] = password_hash_type

            if logged_in is not None:
                new_user["logged_in"] = logged_in

            if key_path is not None:
                new_user["key_path"] = key_path

            # [설명] 이 사용자의 기존 그룹 목록에서 같은 그룹명 또는 같은 GID를
            # 가진 그룹이 있으면 꺼내(목록에서 제거) new_group으로 삼아 갱신한다.
            new_group = {}
            new_user.setdefault("Groups", [])
            for groups in new_user["Groups"]:
                group_name_match = group_name is not None and groups.get("Group Name", None) == group_name
                gid_match = gid is not None and groups.get("GID", None) == gid
                if group_name_match or gid_match:
                    new_group = groups
                    new_user["Groups"].remove(groups)
                    break

            # Groups 목록이 통째로 주어지면 그대로 대체하고, 아니면 group_name으로
            # 단일 그룹을 구성한다. 알려진 빌트인 그룹이면 그 정보도 함께 기록한다.
            if Groups is not None:
                new_user["Groups"] = Groups
            elif group_name is not None:
                new_group["Group Name"] = group_name
                builtin_name = CyEnums.BuiltInGroups.parse_string(group_name)
                if builtin_name is not CyEnums.BuiltInGroups.UNKNOWN:
                    new_group["Builtin Group"] = builtin_name
            if gid is not None:
                new_group["GID"] = gid

            if new_group != {}:
                new_user["Groups"].append(new_group)

            if new_user["Groups"] == []:
                new_user.pop("Groups")

            self.data[hostid]["User Info"].append(new_user)

        # [설명] gid와 group_name이 모두 주어지면, 이 호스트의 모든 사용자 그룹 중
        # 둘 중 하나라도 일치하는 그룹을 찾아 GID·그룹명을 동일하게 맞춘다.
        # (gid<->group_name 매핑을 사용자 전반에 걸쳐 일관되게 보정하는 단계)
        if gid is not None and group_name is not None:
            for user in self.data.get(hostid, {}).get("User Info", []):
                for group in user.get("Groups", []):
                    gid_match = group.get("GID", None) == gid
                    group_name_match = group.get("Group Name", None) == group_name
                    if gid_match or group_name_match:
                        group["GID"] = gid
                        group["Group Name"] = group_name
                        builtin_name = CyEnums.BuiltInGroups.parse_string(group_name)
                        if builtin_name is not CyEnums.BuiltInGroups.UNKNOWN:
                            group["Builtin Group"] = builtin_name

    def add_session_info(self,
                         hostid: str = None,
                         username: str = None,
                         session_id: int = None,
                         agent: str = None,
                         timeout: int = None,
                         pid: int = None,
                         session_type: str = None,
                         **kwargs):
        """Add new session information to specific host in observation.

        Parameters
        ----------
        hostid: str
        username: str
        session_id: int
        agent: str
        timeout: int
        pid: int
        session_type: str

        [한국어]
        관찰값 안의 특정 호스트에 세션(Session) 정보를 추가한다.
        사용자명, 세션 id, 소유 에이전트(agent), 타임아웃, PID, 세션 종류를 담는다.
        같은 에이전트·세션 id의 기존 세션이 있으면 갱신하고, 중복 세션은 추가하지 않는다.
        agent는 반드시 지정해야 하며, 없으면 ValueError를 발생시킨다.
        """
        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Sessions", [])

        new_session = {}
        if session_id is not None:
            # [설명] 같은 agent + session_id를 가진 기존 세션을 찾아 그 항목을
            # 갱신 대상으로 삼는다(is_same). 없으면 session_id만 채운 새 dict로 시작한다.
            sessions = self.data[hostid]["Sessions"]
            is_same = lambda s: s.get("agent", None) == agent and s.get("session_id", None) == session_id
            new_session = next((s for s in sessions if is_same(s)), {"session_id": session_id})

        if username is not None:
            new_session["username"] = username

        session_id = kwargs.get("session_id", None) if session_id is None else session_id
        if session_id is not None:
            new_session["session_id"] = session_id

        if timeout is not None:
            new_session["timeout"] = timeout

        pid = kwargs.get("PID", None) if pid is None else pid
        if pid is not None:
            new_session["PID"] = pid
            # 세션에 PID가 있으면 그 PID로 동작하는 프로세스도 함께 관찰값에 추가한다.
            self.add_process(hostid=hostid, pid=pid, username=username)

        session_type = session_type or kwargs.get("Type", None)
        if session_type is not None:
            if isinstance(session_type, str):
                session_type = CyEnums.SessionType.parse_string(session_type)
            new_session["Type"] = session_type

        if agent is None:
            raise ValueError('Agent must be specified when a session is added to an observation')
        new_session["agent"] = agent

        if new_session not in self.data[hostid]["Sessions"]:
            # check we aren't adding duplicate
            # 중복 세션이 아닌 경우에만 목록에 추가한다.
            self.data[hostid]["Sessions"].append(new_session)

    def combine_obs(self, obs):
        """Combines this Observation with another Observation

        Parameters
        ----------
        obs : Observation
            the other observation

        [한국어]
        다른 관찰값(obs)을 이 관찰값에 병합한다.
        호스트별로 세션·프로세스·사용자·파일·인터페이스·시스템 정보를 각
        add_* 메서드로 다시 넣어 합치므로, 중복 병합 규칙이 그대로 적용된다.
        병합 후 자기 자신(self)을 반환한다.
        """
        # obs가 Observation 객체면 내부 data dict를 꺼내 사용한다.
        if not isinstance(obs, dict):
            obs = obs.data
        for key, info in obs.items():
            # "success"·"action"은 호스트 정보가 아니므로 병합 대상에서 건너뛴다.
            if key in ["success", "action"]:
                # self.set_success(info)
                continue
            # 값이 dict가 아니면(호스트 단위 정보가 아니면) 키-값 그대로 저장한다.
            if not isinstance(info, dict):
                self.add_key_value(key, info)
                continue
            for session_info in info.get("Sessions", []):
                self.add_session_info(hostid=key, **session_info)
            # [설명] 프로세스는 연결(Connections)을 가질 수 있다. 연결이 있으면
            # 연결 하나마다 프로세스 정보(**process)와 연결 정보(**conn)를 함께
            # 넘겨 add_process를 호출한다(연결별로 한 번씩). 연결이 없으면 한 번만 호출한다.
            for process in info.get("Processes", []):
                if 'Connections' in process:
                    for conn in process['Connections']:
                        self.add_process(hostid=key, **process, **conn)
                else:
                    self.add_process(hostid=key, **process)
            for user in info.get("User Info", []):
                self.add_user_info(hostid=key, **user)
            for file_info in info.get("Files", []):
                self.add_file_info(hostid=key, **file_info)
            for interface in info.get("Interface", []):
                self.add_interface_info(hostid=key, **interface)
            if "System info" in info:
                self.add_system_info(hostid=key, **info["System info"])
        return self

    def add_raw_obs(self, raw_obs):
        """Replaces the current raw observation with a new raw observation.

        Parameters
        ----------
        raw_obs

        [한국어]
        현재 원본(raw) 관찰값을 새 raw 관찰값으로 교체한다.
        """
        self.raw = raw_obs

    def add_key_value(self, key, val):
        # 임의의 키-값 쌍을 관찰값 dict에 직접 저장한다.
        self.data[key] = val

    def add_action_obs_pair(self, action, obs):
        """Adds an Action-Observation pair to this observation.

        This can be used to send back observations of multiple
        actions, in a single observation.

        Parameters
        ----------
        action : Action
            the action
        obs : Observation
            the observation

        [한국어]
        행동(Action)-관찰값(Observation) 쌍을 이 관찰값에 추가한다.
        여러 행동의 관찰값을 하나의 관찰값으로 묶어 돌려줄 때 사용한다.
        """
        self.data.setdefault("action_obs", []).append((action, obs))

    def has_multiple_obs(self) -> bool:
        """Returns whether Observation contains multiple nested observation

        Returns
        -------
        bool
            True if Observation has nested observations

        [한국어]
        이 관찰값이 중첩된(nested) 관찰값들을 담고 있는지 여부를 반환한다.
        중첩 관찰값이 있으면 True.
        """
        return "action_obs" in self.data

    def get_nested_obs(self):
        """Returns any nested action, observation pairs

        Returns
        -------
        list((Action, Observation))
            any nested observations

        [한국어]
        중첩된 (행동, 관찰값) 쌍들의 목록을 반환한다. 없으면 빈 목록.
        """
        return self.data.get("action_obs", [])

    def get_sessions(self) -> list:
        """Get list of info for each session in observation

        Returns
        -------
        list(dict)
            list of session info

        [한국어]
        관찰값에 담긴 모든 세션 정보를 하나의 목록으로 모아 반환한다.
        호스트 정보에 "Sessions" 키가 없으면 경고를 남기고 건너뛴다.
        """
        sessions = []
        for k, v in self.data.items():
            if not isinstance(v, dict):
                continue
            if "Sessions" not in v:
                self._log_warning(f"Observation is missing 'Sessions': {v}")
                continue
            sessions += v["Sessions"]
        return sessions

    def get_agent_sessions(self, agent: str) -> list:
        """Get list of info for each agent session in observation

        Parameters
        ----------
        agent : str
            the agent to get session info for

        Returns
        -------
        list(dict)
            list of session info

        [한국어]
        지정한 에이전트(agent)가 소유한 세션 정보만 골라 목록으로 반환한다.
        """
        sessions = []
        for session_info in self.get_sessions():
            if session_info.get("agent", False) == agent:
                sessions.append(session_info)
        return sessions

    def filter_addresses(self,
                         ips: Union[list[str], list[IPv4Address]] = None,
                         cidrs: Union[list[str], list[IPv4Network]] = None,
                         include_localhost: bool = True):
        """Filter observation, in place, to include only certain addresses

        This function will remove any observation information for addresses
        not in the list, and will remove all observations of Hosts which have
        had atleast one address observed but where none of the observed
        addresses are in the list.

        Parameters
        ----------
        ips : list[str] or list[IPv4Address], optional
            the ip addresses to keep, if None does not filter IP addresses
            (default=None)
        cidrs : list[str] or list[IPv4Network], optional
            the cidr addresses to keep, if None does not filter Cidr addresses
            (default=None)
        include_localhost : bool, optional
            If True and ips is not None, will include localhost address
            ('127.0.0.1') in IP addresses to keep (default=True)

        [한국어]
        관찰값을 제자리(in place)에서 걸러, 지정한 주소에 해당하는 정보만 남긴다.
        목록에 없는 주소의 관찰 정보는 제거한다. 또한 주소가 하나 이상 관찰됐지만
        그 어느 것도 목록에 없는 호스트는 해당 호스트 관찰 정보 전체를 제거한다.

        매개변수
        - ips : 남길 IP 주소 목록. None이면 IP 기준 필터링을 하지 않는다.
        - cidrs : 남길 CIDR(서브넷) 주소 목록. None이면 CIDR 기준 필터링을 하지 않는다.
        - include_localhost : True이고 ips가 None이 아니면 localhost('127.0.0.1')도
          남길 IP에 포함한다(기본 True).
        """
        # convert lists to set of str for fast lookup and consistent typing
        # 빠른 조회와 일관된 타입을 위해 목록을 set으로 변환한다.
        if ips is None:
            ip_set = set()
        else:
            ip_set = set(ips)
            if include_localhost:
                ip_set.add(IPv4Address('127.0.0.1'))
            ip_set.add(IPv4Address('0.0.0.0'))

        if cidrs is None:
            cidr_set = set()
        else:
            cidr_set = set(cidrs)
            if include_localhost:
                cidr_set.add(IPv4Network('127.0.0.0/8'))

        filter_hosts = []  # 통째로 제거할 호스트 키를 모아둔다.
        for obs_k, obs_v in self.data.items():
            # 값이 중첩 Observation이면 재귀적으로 같은 필터를 적용한다.
            if isinstance(obs_v, Observation):
                obs_v.filter_addresses(ips, cidrs, include_localhost)
            elif not isinstance(obs_v, dict):
                continue

            # [설명] 프로세스의 연결 주소(local/remote)가 남길 IP 집합에 없으면
            # 그 프로세스 인덱스를 제거 대상에 모은다(중복 추가 방지).
            filter_procs = []
            for i, proc in enumerate(obs_v.get("Processes", [])):
                for conn in proc.get("Connections", []):
                    for proc_k in ["local_address", "remote_address"]:
                        if proc_k in conn and conn[proc_k] not in ip_set and i not in filter_procs:
                            filter_procs.append(i)

            # Must remove indices in reverse order, else risk incorrect proc
            # being removed
            # [설명] 리스트에서 인덱스로 삭제할 때는 큰 인덱스부터(역순) 지워야
            # 앞 항목 삭제로 뒤 인덱스가 밀려 엉뚱한 항목이 지워지는 것을 막는다.
            for p_idx in sorted(filter_procs, reverse=True):
                del obs_v["Processes"][p_idx]

            if "Processes" in obs_v and len(obs_v["Processes"]) == 0:
                del obs_v["Processes"]

            # 인터페이스의 IP 또는 Subnet이 남길 집합에 없으면 제거 대상에 모은다.
            filter_interfaces = []
            for i, interface in enumerate(obs_v.get("Interface", [])):
                check_ip = "IP Address" in interface and interface["IP Address"] not in ip_set
                check_subnet = "Subnet" in interface and interface["Subnet"] not in cidr_set and i not in filter_interfaces
                if check_ip or check_subnet:
                    filter_interfaces.append(i)

            # 프로세스와 동일하게 역순으로 삭제한다.
            for i_idx in sorted(filter_interfaces, reverse=True):
                del obs_v["Interface"][i_idx]

            if "Interface" in obs_v and len(obs_v["Interface"]) == 0:
                del obs_v["Interface"]

            # 필터링 결과 호스트에 남은 정보가 하나도 없으면 호스트 자체를 제거 대상으로 표시한다.
            if len(list(obs_v.values())) == 0:
                filter_hosts.append(obs_k)

        # 순회가 끝난 뒤(반복 중 dict 변경 회피) 비어버린 호스트들을 제거한다.
        for host_k in filter_hosts:
            del self.data[host_k]

    @property
    def success(self):
        """Success of the action that the observation 'observes'

        [한국어]
        이 관찰값이 '관찰하는' 행동의 성공 여부(TernaryEnum)를 반환한다.
        """
        return self.data["success"]

    @property
    def action_succeeded(self) -> bool:
        """Check the success of the action that the observation 'observes'

        [한국어]
        이 관찰값이 '관찰하는' 행동이 성공(TRUE)했는지를 bool로 반환한다.
        UNKNOWN/FALSE는 모두 False가 된다.
        """
        return self.data["success"] == CyEnums.TernaryEnum.TRUE

    def copy(self):
        """Creates a copy of the observation.

        Returns
        -------
        obs_copy : Observation
            copy of the current observation

        [한국어]
        이 관찰값의 복사본을 만들어 반환한다.
        중첩 Observation은 재귀적으로 copy()하고, 그 외 값은 deepcopy로 깊은 복사한다.
        """
        obs_copy = Observation()
        for k, v in self.data.items():
            if isinstance(v, Observation):
                obs_copy.data[k] = v.copy()
            else:
                obs_copy.data[k] = deepcopy(v)
        return obs_copy

    def __str__(self):
        obs_str = pprint.pformat(self.data)
        return f"{self.__class__.__name__}:\n{obs_str}"

    def __eq__(self, other):
        # [설명] self의 모든 키-값이 other에 같은 값으로 존재하면 같다고 본다.
        # other에만 있는 추가 키는 검사하지 않으므로 엄밀한 양방향 동치는 아니다.
        if type(other) is not Observation:
            return False
        for k, v in self.data.items():
            if k not in other.data:
                return False
            other_v = other.data[k]
            if other_v != v:
                return False
        return True
