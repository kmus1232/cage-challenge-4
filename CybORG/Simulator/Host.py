## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
import hashlib
from typing import Dict, Optional, List

import numpy as np


from CybORG.Shared.Enums import (OperatingSystemPatch, OperatingSystemKernelVersion,
        OperatingSystemVersion, DecoyType,
        OperatingSystemDistribution, OperatingSystemType,
        )

from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.File import File
from CybORG.Simulator.HostEvents import HostEvents
from CybORG.Simulator.Interface import Interface
from CybORG.Simulator.Process import Process
from CybORG.Shared.Session import Session
from CybORG.Simulator.Service import Service

from CybORG.Simulator.User import User


class Host(Entity):
    """This class simulates the internals of a host, including files, processes and interfaces. The methods are used to change the state of the host.

    The Host class contains all the relevant data for a host along with the relevant methods for modifying that data. It is instantiated by the State object when the scenario is loaded and can be found in Simulator/Host.py.

    

    The methods in the Host class are mostly about modifying data. This is where most of the low-level work of CybORG is done as the Action objects call these methods, usually through the State object. An exception to this is the get_ephemeral port method, which generates a random port, which is particularly important when a new session is created. This is usually due to red activity, where an exploit creates a new shell, which needs to listen on a new port.
    
    Attributes
    ----------
    original_services: Dict[str, Dict[str,[bool, int]]
        Services present on the host at the beginning of the scenario. Needed for the Restore action.
    os_type: OperatingSystemType
        Differentiates between Windows and Linux hosts.
    distribution: OperatingSystemDistribution
        Differentiates between Linux Distributions and Windows generations (XP,7,8,10 etc.).
    version: OperatingSystemVersion
        Differentiates between Operating System versions. e.g. Windows XP Service Pack 1, Ubuntu 18.04.
    kernel: OperatingSystemKernelVersion
        Represents the kernel of the operating system.
    patches: List[OperatingSystemPatch]
        A list of patches applied to the operating system.
    hostname: str
        The name of the host.
    architecture: dict
    respond_to_ping: bool
    host_type: str
    users: List[User]
    files: List[File]
    original_files: List[File]
    sessions: Dict[Session]
    original_sessions: Dict[Session]
    default_process_info: List[Process]
    processes: List[Process]
    original_processes: List[Process]
    interfaces: List[Interface]
    ephemeral_ports: List[int]
    services: Dict[str, Dict[str,[bool, int]]

    [한국어]
    호스트의 내부(파일, 프로세스, 인터페이스 등)를 시뮬레이션하는 클래스.
    이 클래스의 메서드들은 호스트의 상태를 바꾸는 데 쓰인다.

    Host는 호스트 1대의 모든 관련 데이터와 그 데이터를 수정하는 메서드를 담는다.
    시나리오가 로드될 때 State 객체가 인스턴스화하며, Simulator/Host.py에 있다.

    Host의 메서드는 대부분 데이터 수정용이다. Action(행동) 객체가 보통 State 객체를
    거쳐 이 메서드들을 호출하므로, CybORG의 저수준 작업 대부분이 여기서 일어난다.
    예외는 get_ephemeral_port로, 임의의 포트를 생성한다. 이는 새 세션이 만들어질 때
    특히 중요하다. 보통 Red(공격 측) 활동으로 익스플로잇이 새 셸을 생성하고, 그
    셸이 새 포트에서 수신 대기해야 할 때 발생한다.

    주요 속성(Attributes):
    - original_services: 시나리오 시작 시점의 서비스 목록. Restore(복원) 행동에 필요하다.
    - os_type: Windows / Linux 호스트 구분.
    - distribution: 리눅스 배포판 또는 윈도우 세대(XP, 7, 8, 10 등) 구분.
    - version: OS 버전 구분. 예) Windows XP SP1, Ubuntu 18.04.
    - kernel: 운영체제 커널 버전.
    - patches: 운영체제에 적용된 패치 목록.
    - hostname: 호스트 이름.
    """

    def __init__(
        self, np_random, system_info: dict, hostname: str = None, users: List[User] = None,
        files: List[File] = None, sessions: Dict[str, List[int]] = None, processes: List[Process] = None, interfaces: List[Interface] = None,
        info: dict = None, services: dict = None, respond_to_ping: bool = True,
        starting_position=np.array([0.0, 0.0]), host_type='host',
        confidentiality_value: str = None, availability_value: str = None
    ):
        """Instantiates the class
        
        Hosts have an large `__init__` function because they contain most of the data inside specified in the image and scenario files. This includes operating system information, interfaces, users, groups, files, processes, sessions and services. Each of these is it's own custom datatype.

        Parameters
        ----------
        np_random : numpy random generator
        system_info : dict
        hostname : str
        users : Dict[str, User]
        files: List[File]
        sessions : Dict[str, Session]
            dictionary of agent names and session objects
        processes : List[Process]
        interfaces : List[Interface]
        info : dict
        services : dict
        respond_to_ping : bool
        starting_position : np.array
        host_type : str

        [한국어]
        클래스를 인스턴스화한다.

        Host는 이미지·시나리오 파일에 명시된 데이터 대부분을 담기 때문에 `__init__`
        함수가 크다. OS 정보, 인터페이스, 사용자, 그룹, 파일, 프로세스, 세션, 서비스가
        포함되며, 각각은 별도의 커스텀 자료형이다.

        주요 매개변수:
        - sessions: 에이전트 이름과 세션 객체의 딕셔너리.
        """
        super().__init__()
        self.original_services: Dict[str, Service] = {}
        self.os_type = OperatingSystemType.parse_string(system_info["OSType"])
        self.distribution = OperatingSystemDistribution.parse_string(system_info["OSDistribution"])
        self.version = OperatingSystemVersion.parse_string(str(system_info["OSVersion"]))
        kernel = None
        if "OSKernelVersion" in system_info:
            kernel = OperatingSystemKernelVersion.parse_string(system_info["OSKernelVersion"])
        self.kernel = kernel
        self.patches = []
        if "Patches" in system_info:
            for patch in system_info["Patches"]:
                self.patches.append(OperatingSystemPatch.parse_string(patch))
        self.hostname = hostname
        self.architecture = system_info["Architecture"]
        self.respond_to_ping = respond_to_ping
        self.host_type = host_type
        self.users = users or []
        self.files = files or []
        self.original_files = []
        self.sessions = sessions or {}
        self.original_sessions = {}
        self.processes = processes or []
        self.default_processes = self.processes.copy()
        self.original_processes = []
        self.interfaces = interfaces or []
        self.ephemeral_ports = []
        self.services: Dict[str, Service] = services or {}
        self.info = info if info is not None else {}
        self.events = HostEvents()
        self.position = starting_position
        self.np_random = np_random
        self.impact_count = 0
        self.restore_count = 0
        self.availability_value = availability_value
        self.confidentiality_value = confidentiality_value

    @classmethod
    def load(cls, hostname: str, host_info: dict, np_random):
        services = host_info.get("Services")
        if services:
            services = {name: Service.load(info) for name, info in services.items()}
        users = host_info.get("User Info")
        if users:
            users = [User.load(info) for info in users]
        processes = host_info.get("Processes")
        if processes:
            processes = [Process.load(info) for info in processes]
        return cls(
            np_random=np_random,
            hostname=hostname,
            processes=processes,
            system_info=host_info.get("System info"),
            users=users,
            info=host_info.get("info", {}),
            services=services,
            confidentiality_value=host_info.get("ConfidentialityValue", None),
            availability_value=host_info.get("AvailabilityValue", None)
        )
    
    def get_impact_count(self):
        """Getter for impact count

        [한국어]
        impact_count(Impact 타격 횟수)를 반환하는 getter.
        """
        return self.impact_count

    def get_restore_count(self):
        """Getter for restore count

        [한국어]
        restore_count(Restore 복원 횟수)를 반환하는 getter.
        """
        return self.restore_count

    def get_state(self):
        """Getter for observation dictionary.

        Return
        ------
        observation : Dict[str, _]

        [한국어]
        관찰값(Observation) 딕셔너리를 반환하는 getter.
        """
        observation = {"os_type": self.os_type, "os_distribution": self.distribution, "os_version": self.version,
                       "os_patches": self.patches, "os_kernel": self.kernel, "hostname": self.hostname,
                       "architecture": self.architecture, "position": self.position}
        return observation

    def get_ephemeral_port(self):
        """Getter for the host's ephemeral port

        Returns
        -------
        port : int
            a random value between 49152 and 60000 based on the environment seed

        [한국어]
        호스트의 임시 포트(ephemeral port)를 반환하는 getter.
        환경 시드(seed)에 따라 49152~60000 사이의 임의값을 반환한다.
        """
        port = self.np_random.integers(49152, 60000)
        if port in self.ephemeral_ports:
            port = self.np_random.integers(49152, 60000)
        self.ephemeral_ports.append(port)
        return port

    def add_session(self, new_session: Session):
        if new_session.pid is None:
            pid = self.create_pid()
            self.processes.append(Process(
                pid=pid, process_name=new_session.session_type, username=new_session.username
            ))
            new_session.pid = pid
        self.sessions.setdefault(new_session.agent, []).append(new_session.ident)
    
    def create_pid(self) -> int:
        pids = [0] + [process.pid for process in self.processes]
        return max(pids) + self.np_random.integers(1, 10)

    def add_user(self, username: str, password: str = None, password_hash_type: str = None):
        """Creates and returns a new user object.

        Returns
        -------
        new_user : User
            new user object

        [한국어]
        새 User 객체를 생성해 반환한다. OS(Linux/Windows)에 따라 uid 할당과
        패스워드 해시 방식이 달라진다. 이미 같은 사용자가 있으면 None을 반환한다.
        """
        if self.os_type == OperatingSystemType.LINUX:
            uid_list = [999]
            for user in self.users:
                uid_list.append(user.uid)
            if username in uid_list:
                return None
            # 리눅스 useradd와 동일하게 기존 uid 최댓값 + 1을 새 uid로 부여한다.
            uid = max(uid_list) + 1  # Algorithm Tested in Linux: useradd
        elif self.os_type == OperatingSystemType.WINDOWS:
            uid_list = []
            for user in self.users:
                uid_list.append(user.username)
            if username in uid_list:
                return None
            uid = None
        else:
            raise NotImplementedError('Only Windows or Linux OS are Implemented')

        if password_hash_type is None:
            if self.os_type == OperatingSystemType.LINUX:
                password_hash_type = 'sha512'
            elif self.os_type == OperatingSystemType.WINDOWS:
                password_hash_type = 'NTLM'

        if password_hash_type == 'sha512':
            password_hash = hashlib.sha512(bytes(password, 'utf-8')).hexdigest()
        elif password_hash_type == 'NTLM':
            password_hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest()
        else:
            raise NotImplementedError('Only sha512 and NTLM hashes have been implemented')

        new_user = User(username=username, uid=uid, password=password, password_hash=password_hash,
                        password_hash_type=password_hash_type, groups=None, logged_in=False)

        self.users.append(new_user)
        return new_user

    def get_user(self, username):
        """Get user object by username

        [한국어]
        username으로 User 객체를 찾아 반환한다.
        """
        return next((user for user in self.users if username == user.username), None)

    def get_interface(self, name=None, cidr=None, ip_address=None, subnet_name=None):
        """Get an interface with a selected name, subnet, or ip_address

        [한국어]
        name, subnet(cidr), ip_address 중 하나로 인터페이스를 찾아 반환한다.
        """
        for interface in self.interfaces:
            name_match = name and interface.name == name
            cidr_match = cidr and interface.subnet == cidr
            ip_address_match = ip_address and interface.ip_address == ip_address
            if name_match or cidr_match or ip_address_match:
                return interface

    def get_process(self, pid):
        """Get process by pid

        [한국어]
        pid로 Process 객체를 찾아 반환한다.
        """
        return next((process for process in self.processes if process.pid == pid), None)

    def get_file(self, name: str, path=None):
        """Get file by filename

        [한국어]
        파일 이름(필요 시 path까지)으로 File 객체를 찾아 반환한다.
        """
        for file in self.files:
            if file.name == name and (not path or file.path == path):
                return file

    def disable_user(self, username):
        user = self.get_user(username)
        if user is not None:
            return user.disable_user()
        return False

    def remove_user_group(self, user, group):
        user = self.get_user(user)
        return user is not None

    def start_service(self, service_name: str):
        """Starts a stopped service, no effect if service already started

        [한국어]
        멈춰 있는 서비스를 시작한다. 이미 시작된 서비스면 아무 효과가 없다.
        """
        if service_name in self.services:
            if self.services[service_name]['process'] not in self.processes:
                self.services[service_name]['active'] = True
                process = self.services[service_name]['process']
                process.pid = self.create_pid()
                self.processes.append(process)
                self.services[service_name]['process'] = process
                return process, self.services[service_name]['session']
            return self.services[service_name]['process'], self.services[service_name]['session']

    # Fix bug - impact count does not increment
    # 버그 수정 - impact_count가 증가하지 않던 문제 대응
    def increment_impact_count(self):
        self.impact_count += 1

    def stop_service(self, service_name: str):
        """Stops a started service, no effect if service already stopped

        [한국어]
        시작된 서비스를 멈춘다. 이미 멈춘 서비스면 아무 효과가 없다.
        """
        if service_name in self.services:
            if self.services[service_name].active:
                self.services[service_name].active = False
                return self.services[service_name].process

    def add_service(self, service_name: str, service: Service) -> Service:
        """
        Adds a service to the host, and starts it

        [한국어]
        호스트에 서비스를 추가하고 시작한다.
        """
        if service_name not in self.services:
            self.services[service_name] = service
        return self.services[service_name]

    def is_using_port(self, port: int) -> bool:
        """
        Convenience method for checking if a host is using a port

        [한국어]
        호스트가 특정 포트를 사용 중인지 확인하는 편의 메서드.
        """
        return any(proc.is_using_port(port) for proc in self.processes)
    
    def create_backup(self):
        """Creates a backup of the host by filling original class attributes with current class details

        [한국어]
        현재 호스트 상태를 original_* 속성에 복사해 백업을 만든다.
        나중에 restore()가 이 백업으로 호스트를 되돌린다.
        """
        self.original_files = []
        if self.files is not None:
            for file in self.files:
                self.original_files.append(File(**file.get_state()[0]))

        self.original_sessions = {}
        if self.sessions is not None:
            for agent_name, sessions in self.sessions.items():
                if agent_name not in self.original_sessions:
                    self.original_sessions[agent_name] = []
                self.original_sessions[agent_name] += sessions

        self.original_processes = []
        if self.processes is not None:
            # [설명] process.get_state()는 열린 포트마다 dict 1개를 돌려준다.
            # 첫 dict(temp)를 프로세스 본체로 삼고 open_ports 리스트를 만든 뒤,
            # 나머지 dict들은 포트 정보만 뽑아 open_ports에 합친다.
            # 즉 여러 포트 항목을 프로세스 1개 dict로 접어 Process를 재구성한다.
            for process in self.processes:
                temp = None
                for p in process.get_state():
                    if temp is None:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p.pop('local_port')
                        if 'remote_port' in p:
                            open_port['remote_port'] = p.pop('remote_port')
                        if 'local_address' in p:
                            open_port['local_address'] = p.pop('local_address')
                        if 'remote_address' in p:
                            open_port['remote_address'] = p.pop('remote_address')
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p.pop('transport_protocol')
                        if len(process.properties) > 0:
                            p['properties'] = process.properties

                        temp = p
                        temp['open_ports'] = []
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                    else:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p['local_port']
                        if 'remote_port' in p:
                            open_port['remote_port'] = p['remote_port']
                        if 'local_address' in p:
                            open_port['local_address'] = p['local_address']
                        if 'remote_address' in p:
                            open_port['remote_address'] = p['remote_address']
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p['transport_protocol']
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                self.original_processes.append(Process(**temp))

        self.ephemeral_ports = []
        self.original_services = self._clone_services(self.services)

    def restore(self):
        """Restores the host by filling current class details from 'original' class attributes

        [한국어]
        create_backup()이 저장해 둔 original_* 속성으로 현재 호스트 상태를 되돌린다.
        Restore(복원) 행동이 이 메서드를 호출하며, 마지막에 restore_count를 1 증가시킨다.
        """
        self.events = HostEvents()
        self.files = []
        if self.original_files is not None:
            for file in self.original_files:
                self.files.append(File(**file.get_state()))

        self.sessions = {}
        if self.original_sessions is not None:
            for agent_name, sessions in self.original_sessions.items():
                if agent_name not in self.sessions:
                    self.sessions[agent_name] = []
                self.sessions[agent_name] += sessions

        self.processes = []
        if self.original_processes is not None:
            # [설명] create_backup()과 동일한 로직으로, 백업된 프로세스의 여러
            # 포트 항목을 프로세스 1개 dict로 접어 Process를 재구성한다.
            for process in self.original_processes:
                temp = None
                for p in process.get_state():
                    if temp is None:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p.pop('local_port')
                        if 'remote_port' in p:
                            open_port['remote_port'] = p.pop('remote_port')
                        if 'local_address' in p:
                            open_port['local_address'] = p.pop('local_address')
                        if 'remote_address' in p:
                            open_port['remote_address'] = p.pop('remote_address')
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p.pop('transport_protocol')
                        if len(process.properties) > 0:
                            p['properties'] = process.properties
                        temp = p
                        temp['open_ports'] = []
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                    else:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p['local_port']
                        if 'remote_port' in p:
                            open_port['remote_port'] = p['remote_port']
                        if 'local_address' in p:
                            open_port['local_address'] = p['local_address']
                        if 'remote_address' in p:
                            open_port['remote_address'] = p['remote_address']
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p['transport_protocol']
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                self.processes.append(Process(**temp))

        self.ephemeral_ports = []
        self.services = self._clone_services(self.original_services)
        self.restore_count += 1

    def get_availability_value(self, default):
        return self.availability_value if self.availability_value is not None else default

    def get_confidentiality_value(self, default):
        return self.confidentiality_value if self.confidentiality_value is not None else default
    
    def update(self, state):
        pass

    def _clone_services(self, services: Dict[str, Service]) -> Dict[str, Service]:
        cloned_services = {}
        for service_name, service_info in services.items():
            cloned_services[service_name] = Service(
                    process=service_info.process, active=service_info.active
                )
        return cloned_services

    def __str__(self):
        return f'{self.hostname}'
