## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
from ipaddress import IPv4Address
from typing import List

from CybORG.Shared.Enums import (ProcessType, ProcessVersion,
        TransportProtocol, DecoyType)
from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.HostEvents import NetworkConnection


class Process(Entity):
    def __init__(self, process_name: str, pid: int, username: str, parent_pid: int = None, program_name: str = None,
                 path: str = None, open_ports: list = None, process_type: str = None, process_version: str = None,
                 decoy_type: DecoyType = DecoyType.NONE, properties: List[str] = None):
        """
        Parameters
        ----------
        process_name: str
            name of process
        pid: int
            id of process
        parent_pid: int
            id of parent of process
        program_name: str
            program the process is running
        username: str
            the user runnning the process
        path: str
            the path of the program the process is running
        open_ports: List[Dict[str, _]]
            listening ports of structure [{Port: int, Address: str, Application Protocol: str}, ...]
        process_type: str
            the type of process
        process_version: str
            the version of the process
        decoy_type: DecoyType
            which red actions are prevented despite appearing vulnerable
        properties: List[str]
            properties of the process to specify configuration details such as RFI presence

        [한국어]
        프로세스(Process) 엔티티를 초기화한다.

        주요 파라미터:
        - process_name: 프로세스 이름
        - pid / parent_pid: 프로세스 ID와 부모 프로세스 ID
        - program_name: 프로세스가 실행 중인 프로그램
        - username: 프로세스를 실행하는 사용자
        - path: 실행 중인 프로그램의 경로
        - open_ports: 리스닝 중인 포트 목록. [{Port, Address, Application Protocol}, ...] 구조
        - process_type / process_version: 프로세스 유형과 버전
        - decoy_type: 취약해 보이지만 실제로는 막아내는 Red 행동(Action)의 종류.
          즉 이 프로세스가 Decoy(디코이, 미끼)로서 어떤 공격을 차단하는지 지정한다.
        - properties: RFI 존재 여부 등 설정 세부사항을 명시하는 프로세스 속성 목록
        """
        super().__init__()
        self.name = process_name
        self.pid = pid
        self.ppid = parent_pid
        self.program = program_name
        self.user = username
        self.path = path
        self.open_ports = open_ports
        self.decoy_type = decoy_type
        # Connections는 [{local_port, local_address, remote_port, Remote Address, Application Protocol}] 구조를 가진다
        self.connections: List[NetworkConnection] = []  # Connections has the structure [{local_port, local_address, remote_port, Remote Address, Application Protocol}]
        self.properties = properties or []
        # [설명] open_ports(딕셔너리 목록)를 NetworkConnection 객체 목록으로 변환한다.
        if open_ports is not None:
            for port_dict in open_ports:
                local_address = port_dict['local_address']
                # [설명] 특수 주소 문자열을 실제 IP로 치환한다: broadcast는 모든 주소(0.0.0.0), local은 루프백(127.0.0.1)
                if local_address == 'broadcast':
                    local_address = '0.0.0.0'
                elif local_address == 'local':
                    local_address = '127.0.0.1'
                transport_protocol = port_dict.get("transport_protocol", TransportProtocol.UNKNOWN)
                # [설명] 문자열로 들어온 전송 프로토콜은 TransportProtocol enum으로 파싱한다
                if not isinstance(transport_protocol, TransportProtocol):
                    transport_protocol = TransportProtocol.parse_string(transport_protocol)
                self.connections.append(NetworkConnection(
                    local_address=IPv4Address(local_address),
                    local_port=port_dict['local_port'],
                    transport_protocol=transport_protocol
                ))
        # [설명] process_type 결정 우선순위: 명시된 process_type을 우선 사용하고,
        # 없으면 process_name 문자열에서 유형을 추론(parse)한다.
        self.process_type = None
        if process_type is not None:
            if isinstance(process_type, str):
                self.process_type = ProcessType.parse_string(process_type)
            else:
                self.process_type = process_type
        elif isinstance(process_name, str):
            self.process_type = ProcessType.parse_string(process_name)

        if process_version is not None:
            self.version = ProcessVersion.parse_string(process_version)
        else:
            self.version = None

    def get_state(self):
        """
        Getter for the state of the process.

        Returns
        -------
        observations : List[dict]

        [한국어]
        프로세스의 상태를 관찰값(Observation) 목록으로 반환하는 게터.
        연결(connection)마다 기본 정보에 연결 상태를 합쳐 하나의 dict로 만들고,
        연결이 하나도 없으면 기본 정보만 담은 dict를 한 개 반환한다.
         """
        observations = []
        base_obs = {
            "pid": self.pid,
            "parent_pid": self.ppid,
            "process_name": self.name,
            "program_name": self.program,
            "path": self.path,
            "process_type": self.process_type,
            "process_version": self.version,
        }
        # [설명] 연결마다 base_obs를 복사해 연결 상태를 합치고 사용자 정보를 덧붙인다
        for connection in self.connections:
            obs = base_obs.copy()
            obs.update(connection.get_state())
            if self.user is not None:
                obs["username"] = self.user
            observations.append(obs)
        # [설명] 연결이 하나도 없으면 기본 정보(base_obs)만 담은 관찰값을 한 개 반환한다
        if not observations:
            obs = base_obs.copy()
            obs['username'] = self.user
            observations.append(obs)
        return observations

    def is_using_port(self, port: int) -> bool:
        # [설명] 연결 중 하나라도 해당 로컬 포트를 쓰고 있으면 True를 반환한다
        return any(conn.local_port == port for conn in self.connections)

    @classmethod
    def load(cls, info: dict):
        # [설명] 시나리오/상태 dict(info)로부터 Process 인스턴스를 생성하는 팩토리 메서드.
        # dict의 키 이름을 생성자 파라미터에 매핑한다.
        return cls(
            pid=info.get('PID'),
            parent_pid=info.get('PPID'),
            username=info.get("username"),
            process_name=info.get('process_name'),
            path=info.get('Path'),
            open_ports=info.get('Connections'),
            properties=info.get('Properties'),
            process_version=info.get('Process Version'),
            process_type=info.get('process_type')
        )
    
    def __str__(self):
        return f'{self.name}: {self.pid} <- {self.ppid}'
