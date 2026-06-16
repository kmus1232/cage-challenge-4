# Copyright DST Group. Licensed under the MIT license.
from typing import Dict
from CybORG.Simulator.Entity import Entity
from ipaddress import IPv4Network


class Subnet(Entity):
    """ Class that holds the details about a subnet.

    Attributes
    ----------
    name : str
        name of the subnet
    size : int
        number of hosts in the subnet?
    hosts : List[str]
        a list of the hostnames in the subnet?
    nacls : Dict[str, Dict[str, str]]
        ?
    cidr : IPv4Network
        The network object for the subnet
    ip_addresses : list
        ?

    [한국어]
    서브넷의 세부 정보를 담는 클래스.

    속성(Attributes)
    ----------
    name : str
        서브넷 이름
    size : int
        서브넷에 속한 호스트 수(원문에 물음표가 붙어 있어 확정되지 않은 의미)
    hosts : List[str]
        서브넷에 속한 호스트명 목록(원문 미확정)
    nacls : Dict[str, Dict[str, str]]
        NACL(네트워크 접근 제어 목록) 규칙(원문 미기재)
    cidr : IPv4Network
        서브넷을 표현하는 네트워크 객체
    ip_addresses : list
        IP 주소 목록(원문 미기재)
    """
    def __init__(
        self,
        name: str,
        size: int = None,
        hosts: list = None,
        nacls: Dict[str, Dict[str, str]] = None,
        cidr: IPv4Network = None,
        ip_addresses: list = None
    ):
        super().__init__()
        self.name = name
        self.size = size
        self.hosts = hosts if hosts is not None else []
        self.nacls = nacls if nacls is not None else {}
        self.cidr = cidr
        self.ip_addresses = ip_addresses


    @classmethod
    def load(cls, name, subnet_info):
        size = subnet_info.get('Size')
        hosts = subnet_info.get('Hosts')
        nacls = subnet_info.get('NACLs')
        return cls(name=name, size=size,hosts=hosts,nacls=nacls)

    def get_state(self): #TODO  # 미구현(상태 반환 로직 추가 예정)
        pass

    def contains_ip_address(self, ip_address: str) -> bool:
        """Check if the specified ip address is in the subnet.

        Parameters
        ----------
        ip_address: str
            host ip address in string form

        Returns
        -------
        bool
            true if the specified ip address is in the subnet

        [한국어]
        지정한 IP 주소가 이 서브넷에 속하는지 확인한다.

        매개변수(Parameters)
        ----------
        ip_address: str
            문자열 형태의 호스트 IP 주소

        반환값(Returns)
        -------
        bool
            지정한 IP 주소가 서브넷에 속하면 True
        """
        return ip_address in self.cidr

    def __str__(self):
        output = f"ScenarioAgent: name={self.name} _info={self._info} \nsessions=\n"
        for session in self.starting_sessions:
            output += f"{session}"
        return output