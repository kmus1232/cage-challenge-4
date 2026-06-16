# Copyright DST Group. Licensed under the MIT license.
from ipaddress import IPv4Address, IPv4Network
from typing import Optional

from networkx import shortest_path, NetworkXNoPath, NodeNotFound
from networkx.classes.function import nodes, induced_subgraph

from CybORG.Shared import Observation, CybORGLogger
from CybORG.Simulator.Host import Host
from CybORG.Simulator.State import State

lo_subnet = IPv4Network('127.0.0.0/8')
lo = IPv4Address('127.0.0.1')
DEFAULT_PRIORITY = 99
DEFAULT_DURATION = 1

class Action(CybORGLogger):

    def __init__(self):
        self.name = self.__class__.__name__
        self.priority = DEFAULT_PRIORITY
        self.duration = DEFAULT_DURATION
        self.logs: list[str] = []

    def execute(self, state: State) -> Observation:
        raise NotImplementedError(f'Action {type(self)} not implemented')

    def check_c2(self, state: State, session: int) -> bool:
        return True

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return self.__str__()

    def get_params(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key)}

    def log(self, log: str):
        self.logs.append(f'{type(self)}: {log}')

    @property
    def cost(self):
        return 0


class Sleep(Action):
    def execute(self, state):
        return Observation()

class InvalidAction(Action):

    def __init__(self, action: Action = None, error: str =None):
        super().__init__()
        self.action = action
        self.error = error

    def execute(self, state):
        return Observation(success=False)

    @property
    def cost(self):
        return -0.1

class RemoteAction(Action):
    """Abstract class for all actions that happen on a remote host.

    Attributes
    ----------
    agent : str
    session : int
    dropped : bool
    blocked : bool
    bandwidth_usage : int
    route
    route_designated : bool

    [한국어]
    원격 호스트에서 일어나는 모든 행동(Action)의 추상 클래스.

    속성
    ----------
    agent : str         이 행동을 수행하는 에이전트 이름
    session : int       사용하는 세션 ID
    dropped : bool      패킷이 도중에 드롭됐는지 여부
    blocked : bool      트래픽이 차단됐는지 여부
    bandwidth_usage : int  사용한 대역폭
    route               목적지까지의 경로(호스트 이름 리스트)
    route_designated : bool  경로가 이미 확정됐는지 여부
    """
    def __init__(self, session: int, agent: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.dropped = False
        self.blocked = False
        self.bandwidth_usage = 0
        self.route = None
        self.route_designated = False

    @staticmethod
    def remove_blocking_nodes(state:State, src_hostname: str):
        network = state.link_diagram
        all_nodes = nodes(network)
        non_blocking_nodes = []
        for other_hostname in all_nodes:
            if not RemoteAction.blocking_host(state, src_hostname, other_hostname):
                non_blocking_nodes.append(other_hostname)
        
        return induced_subgraph(state.link_diagram, non_blocking_nodes)

    @staticmethod  
    def get_route(state: State, target: str, source: str, routing: bool = False) -> list:
        """finds the route from one ip_address to another and returns the hostname list along that route

        [한국어]
        한 IP 주소에서 다른 IP 주소까지의 경로를 찾아, 그 경로를 따라가는 호스트 이름 리스트를 반환한다.
        routing이 True이면 차단(block) 노드를 제외한 네트워크에서 경로를 다시 계산하고,
        그래도 경로가 없으면 차단을 무시한 기본 경로(default_path)를 그대로 돌려준다.
        """
        try:
            path = shortest_path(state.link_diagram, source=source, target=target)
        except NetworkXNoPath:
            path = None
        if routing:
            # [설명] 차단 노드를 제거하기 전의 경로를 기본값으로 보관해 둔다.
            #        차단 노드를 뺀 네트워크에서 경로를 못 찾으면 이 기본 경로로 폴백한다.
            default_path = path
            # 차단(blocking) 호스트를 제외한 부분 네트워크를 만든다.
            network = RemoteAction.remove_blocking_nodes(state, source)
            try:
                path = shortest_path(network, source=source, target=target)
            except NetworkXNoPath:
                return default_path
            except NodeNotFound:
                return default_path
        return path

    def get_used_route(self, state: State, refresh = True, routing = False) -> list:
        """finds the route used by the action and returns the hostnames along that route

        [한국어]
        이 행동이 실제로 사용하는 경로를 찾아, 경로를 따라가는 호스트 이름들을 반환한다.
        refresh가 True이거나 경로가 아직 확정되지 않았으면 경로를 새로 계산한다.
        """
        if refresh or not self.route_designated:
            target = state.ip_addresses[self.ip_address]
            source = state.sessions[self.agent][self.session].hostname
            self.route = self.get_route(state, target, source, routing)
        return self.route

    @staticmethod
    def blocking_host(state: State, src_hostname: str, other_hostname: str):
        """Returns if the src_hostname is blocked by an ip_address of CIDR filter by other_hostname

        [한국어]
        other_hostname이 설정한 IP 또는 CIDR 차단 필터에 의해 src_hostname이 막혀 있는지 반환한다.
        IP 단위 차단(ip_blocked)과 서브넷 단위 차단(subnet_blocked) 중 하나라도 걸리면 차단으로 본다.
        """
        src_host_subnet = state.hostname_subnet_map[src_hostname]
        other_host_subnet = state.hostname_subnet_map[other_hostname]

        ip_blocked = other_hostname in state.blocks and src_hostname in state.blocks[other_hostname]
        subnet_blocked = other_host_subnet in state.blocks and src_host_subnet in state.blocks[other_host_subnet]

        return (subnet_blocked or ip_blocked)

    @staticmethod
    def check_routable(state: State, target: str, source: str) -> bool:
        """
        Checks if data can be send from one address to another

        [한국어]
        한 주소에서 다른 주소로 데이터를 보낼 수 있는지 확인한다.
        source가 속한 연결 요소(connected component) 안에 target이 함께 있으면 도달 가능하다고 본다.
        """
        for connected_components in state.connected_components:
            if source in connected_components:
                return target in connected_components

    def _get_originating_ip(self, state: State, from_host: Host, target_ip_address) -> Optional[IPv4Address]:
        """
        finds the ip address capable of sending data to the target address

            Parameters
            ----------
            state : State
                the current state of the simulation
            from_host : Host
                the host that is attempting to send data to the target IP address
            target_ip_address : IPv4Address
                the target IP address to which a route is being looked for
            Returns
            -------
            IPv4Address
                the IP address from which data can be sent to the target address else returns None if no route exists

            [한국어]
            목적지 주소로 데이터를 보낼 수 있는 출발 IP 주소를 찾는다.

            매개변수
            ----------
            state : State
                현재 시뮬레이션 상태
            from_host : Host
                목적지 IP로 데이터를 보내려는 호스트
            target_ip_address : IPv4Address
                경로를 찾으려는 목적지 IP 주소
            반환값
            -------
            IPv4Address
                목적지로 데이터를 보낼 수 있는 출발 IP 주소. 경로가 없으면 None을 반환한다.
        """
        if from_host is None:
            return None

        originating_ip_address = None
        if target_ip_address == lo:
            return target_ip_address
        # hacky fix to enable operational firewall in scenario1b and scenario2
        # [설명] scenario1b·scenario2의 운영(Operational) 방화벽을 동작시키기 위한 임시 보정 로직이다.
        if state.operational_firewall:
            # Red 에이전트가 Operational 서브넷을 노릴 때만 방화벽을 적용한다.
            if 'red' in self.agent.lower() and target_ip_address in state.subnet_name_to_cidr['Operational']:
                # Enterprise 세션이 있으면 방화벽을 우회(bypass)할 수 있다.
                bypass_operational_firewall = self.check_for_enterprise_sessions(state)
                if not bypass_operational_firewall:
                    return None
        route = self.get_route(state, state.ip_addresses[target_ip_address], from_host.hostname)
        if route is None:
            return None
        # 경로 길이가 1이면 출발지와 목적지가 같은 호스트이므로 목적지 IP를 그대로 쓴다.
        if len(route) == 1:
            return target_ip_address
        # [설명] 경로의 다음 홉(route[1])과 연결된 인터페이스를 찾아, 그 인터페이스의 IP를 출발 IP로 쓴다.
        for i in from_host.interfaces:
            if route[1] in i.data_links:
                return i.ip_address
        return originating_ip_address

    def check_for_enterprise_sessions(self, state):
        """temporary hacky fix for scenario1b and scenario2 oeprational firewall

        [한국어]
        scenario1b·scenario2의 운영(Operational) 방화벽 처리를 위한 임시 보정 메서드.
        에이전트가 가진 세션 중 호스트 이름에 'Enterprise'가 들어간 세션이 하나라도 있으면
        방화벽 우회 권한이 있다고 보고 True를 반환한다.
        """
        permission = False
        for session_id in state.sessions[self.agent]:
            session = state.sessions[self.agent][session_id]
            if 'Enterprise' in session.hostname:
                permission = True

        return permission
