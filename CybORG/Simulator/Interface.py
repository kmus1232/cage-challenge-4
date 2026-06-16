# Copyright DST Group. Licensed under the MIT license.
from ipaddress import IPv4Address, IPv4Network

from CybORG.Simulator.Entity import Entity


class Interface(Entity):
    """Interface object for the Hosts.

    Attributes
    ----------
    name : str
    interface_type : str
    ip_address : IPv4Address
    subnet : IPv4Network
    data_links : list
    max_range : float
    blocked_ips : list
    swarm : bool

    [한국어]
    호스트(Host)에 부착되는 인터페이스(Interface) 객체.

    주요 속성:
    - name: 인터페이스 이름
    - interface_type: 인터페이스 종류(기본값 'wired', 즉 유선)
    - ip_address: IPv4 주소
    - subnet: 소속 서브넷(Subnet)
    - data_links: 연결된 데이터 링크 목록
    - max_range: 통신 가능한 최대 범위(무선·드론 환경에서 사용)
    - blocked_ips: 차단된 IP 목록
    - swarm: 군집(swarm) 동작 여부 플래그
     """
    def __init__(self, name: str = None, ip_address: str = None, subnet: str = None, interface_type: str = 'wired', data_links: list = None, max_range: float = 100, swarm=False):
        """Initiates the Interface

        [한국어]
        인터페이스를 초기화한다.
        """
        super().__init__()
        self.name = name
        self.interface_type = interface_type
        self.ip_address = IPv4Address(ip_address)
        # subnet replaced with Subnet object during state initialisation
        # 상태 초기화 단계에서 이 subnet 문자열은 Subnet 객체로 교체된다.
        # [설명] 생성자에는 subnet이 문자열로 들어올 수 있어, 문자열이면 IPv4Network로 변환해 둔다.
        if type(subnet) is str:
            subnet = IPv4Network(subnet)
        self.subnet = subnet
        if data_links is None:
            self.data_links = []
        else:
            self.data_links = data_links
        self.max_range = max_range
        self.blocked_ips = []
        self.swarm = swarm


    def get_state(self):
        """Gets the internal state of the interface.

        Returns
        -------
        Dict[str, _]
            dictionary containing the interface name, IP address, and subnet.

        [한국어]
        인터페이스의 내부 상태를 반환한다.
        반환값은 인터페이스 이름·IP 주소·서브넷을 담은 딕셔너리다.
        """
        return {"interface_name": self.name, "ip_address": self.ip_address, "subnet": self.subnet}
