from typing import List
from ipaddress import IPv4Address

from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.State import State
from CybORG.Shared import Observation
from CybORG.Simulator.HostEvents import NetworkConnection
from CybORG.Shared.Enums import ProcessName


class GreenAccessService(RemoteAction):
    """A Green Agent action for communicating with a server.

    Attributes
    ----------
    src_ip : IPv4Address
        ip address of source host
    dest_ip : IPv4Address
        ip address of destination host
    dest_port : int
        port number of destination host to be contacted
    allowed_subnets : list[str]
        list of subnets that can be reached according to the mission phase
    fp_detection_rate : float
        the decimal probability that a false positive is created for blue (default=0.01)

    [한국어]
    Green 에이전트(정상 사용자)가 서버와 통신하는 행동(Action)이다.

    속성
    ----------
    src_ip : IPv4Address
        출발 호스트의 IP 주소
    dest_ip : IPv4Address
        목적지 호스트의 IP 주소
    dest_port : int
        접속할 목적지 호스트의 포트 번호
    allowed_subnets : list[str]
        현재 미션 단계(mission phase)에서 도달 가능한 서브넷 목록
    fp_detection_rate : float
        Blue(방어 측)에게 오탐(false positive)이 생성될 확률(소수). 기본값 0.01.
    """
    
    def __init__(self, agent: str, session_id: int, src_ip: IPv4Address, allowed_subnets: List[str], fp_detection_rate: float):
        """Initialisation of green agent access service action.

        Parameters
        ----------
        agent : str
            the name of the agent performing the access service action (source agent)
        session_id : int
            source agent session id (default=0)
        src_ip : IPv4Address
            ip address of source host
        allowed_subnets : list[str]
            list of subnets that can be reached according to the mission phase
        fp_detection_rate : float
            the decimal probability that a false positive is created for blue (default=0.01)

        [한국어]
        Green 에이전트의 access service 행동을 초기화한다.

        매개변수
        ----------
        agent : str
            access service 행동을 수행하는 에이전트(출발 에이전트)의 이름
        session_id : int
            출발 에이전트의 세션 id (기본값 0)
        src_ip : IPv4Address
            출발 호스트의 IP 주소
        allowed_subnets : list[str]
            현재 미션 단계에서 도달 가능한 서브넷 목록
        fp_detection_rate : float
            Blue에게 오탐(false positive)이 생성될 확률(소수). 기본값 0.01.
        """
        super().__init__(agent=agent, session=session_id)
        self.ip_address = src_ip
        self.allowed_subnets = allowed_subnets
        self.dest_ip = ""
        self.dest_port = ""
        self.fp_detection_rate = fp_detection_rate

    def _get_my_used_route(self, state: State) -> List[str]:
        """Finds the route used by the action and returns the hostnames along that route.

        Parameters
        ----------
        state : State
            state of simulation at current step

        Returns
        -------
        List[str]
            list of hostnames that occur along the path from src to dest

        [한국어]
        이 행동이 사용하는 경로(route)를 찾아, 그 경로상의 호스트 이름들을 반환한다.

        매개변수
        ----------
        state : State
            현재 스텝(step)에서의 시뮬레이션 상태
        반환값
        -------
        List[str]
            출발지(src)에서 목적지(dest)까지의 경로상에 나타나는 호스트 이름 목록
        """
        source = state.ip_addresses[self.ip_address]
        target = state.ip_addresses[self.dest_ip]

        return self.get_route(state=state, source=source, target=target)

    def random_reachable_ip(self, state: State) -> IPv4Address:
        """Finds an ip address that the green agent believes to be reachable.

        The green agent has additional knowledge of the subnets that can be access for each mission.
        This should be applied to its access service choice, as it serves no purpose for someone to try to access a service they know they cannot.
        This knowledge is found in the agent's ActionSpace variable named allowed_subnets.

        - If the agent knows that it's in an 'allowed_subnet' subnet, it can try to reach out to any other allowed_subnet (including its own).
        - If the agent knows that its subnet has been intentionally cut off due to mission plans (i.e. not in the 'allowed_subnet' list), it will only try to reach out within its own subnet.

        The green agent will only reach out to host that are not themselves (as this is covered under the GreenLocalWork Action), and hosts which are servers.

        Parameters
        ----------
        state : State
            state of simulation at current step

        Returns
        -------
        : IPv4Address
            ip address of target host

        [한국어]
        Green 에이전트가 도달 가능하다고 믿는 IP 주소를 하나 찾는다.

        Green 에이전트는 미션별로 접근 가능한 서브넷에 대한 사전 지식을 갖는다.
        도달 불가능함을 아는 서비스에 접근을 시도하는 것은 의미가 없으므로,
        이 지식을 access service 대상 선택에 반영한다. 해당 지식은 에이전트의
        ActionSpace 변수 allowed_subnets에 들어 있다.

        - 자신이 allowed_subnet(허용 서브넷) 안에 있음을 안다면, 다른 모든
          allowed_subnet(자기 서브넷 포함)으로 접근을 시도할 수 있다.
        - 미션 계획상 자기 서브넷이 의도적으로 차단되었음을(즉 allowed_subnet
          목록에 없음을) 안다면, 자기 서브넷 안에서만 접근을 시도한다.

        Green 에이전트는 자기 자신이 아닌 호스트(자기 자신은 GreenLocalWork
        행동에서 다룸)이면서 서버인 호스트에만 접근을 시도한다.

        매개변수
        ----------
        state : State
            현재 스텝에서의 시뮬레이션 상태
        반환값
        -------
        : IPv4Address
            대상 호스트의 IP 주소
        """
        reachable_hosts = []
        all_allowed_subnet_cidrs = []
        src_subnet = state.hostname_subnet_map[state.ip_addresses[self.ip_address]]
        if src_subnet in self.allowed_subnets:
            # if the source host is in an allowed subnet, then list all allowed subnets
            # 출발 호스트가 허용 서브넷 안에 있으면, 모든 허용 서브넷을 후보로 나열한다
            for subnet_name in self.allowed_subnets:
                all_allowed_subnet_cidrs.append(state.subnet_name_to_cidr[subnet_name])
        else:
            # if the source host is not in an allowed subnet, then only list that subnet
            # 출발 호스트가 허용 서브넷 밖이면, 자기 서브넷만 후보로 나열한다
            all_allowed_subnet_cidrs.append(state.subnet_name_to_cidr[src_subnet])

        # Only list the host ips of hosts in the list of subnets, that are servers and not the source host
        # 위에서 추린 서브넷에 속하며, 서버이고, 출발 호스트가 아닌 호스트의 IP만 후보에 담는다
        for host_ip in state.ip_addresses:
            if 'server' in state.ip_addresses[host_ip] and not host_ip == self.ip_address:
                for subnet in all_allowed_subnet_cidrs:
                    if host_ip in subnet:
                        reachable_hosts.append(host_ip)

        if len(reachable_hosts) < 0:
            return None
        else:
            return state.np_random.choice(reachable_hosts)

    def available_dest_service(self, state) -> bool:
        """Check if there is an active, reliable service to connect to; prioritising OT services.

        [한국어]
        접속할 수 있는, 활성(active)이며 신뢰 가능한(reliable) 서비스가 있는지 확인한다.
        이때 OT 서비스(OTSERVICE)를 우선한다.
        """
        dest_host_name = state.ip_addresses[self.dest_ip]

        if ProcessName.OTSERVICE in state.hosts[dest_host_name].services.keys():
            service = state.hosts[dest_host_name].services[ProcessName.OTSERVICE]
            if service.active and state.np_random.integers(100) < service.get_service_reliability():
                return True
            else:
                return False
        else:
            available_services = [service for service in state.hosts[dest_host_name].services.values() if session.active]
            if len(available_services) > 0:
                service = state.np_random.choice(available_services)
                if state.np_random.integers(100) < service.get_service_reliability():
                    return True
            return False



    def execute(self, state: State) -> Observation:
        """Have the green agent attempt to access a service from another server host, checking routability.

        Deciding the destination host is done by random_reachable_ip().
        If there are no reachable hosts, then there are no hosts that meet the green agent requirements that are available.
        This should not be possible without red actions having taken place, therefore the action will be unsuccessful.

        The destination host is then checked against the following points:

        1. Check if the host is blocked
            - If so, add a network_connections event to the host and return an unsuccessful observation

        2. At the fp_detection_rate, add an erroneous network_connections event to the host

        If a (unsucessful) observation has not yet been returned, the action has been sussessful and a successful observation is returned.

        Notes
        -----
        function closely mimics SendData action execute()

        Parameters
        ----------
        state : State
            state of simulation at current step

        Returns
        -------
        obs : Observation
            observation with true or false success

        [한국어]
        Green 에이전트가 다른 서버 호스트의 서비스에 접속을 시도하며, 경로 도달
        가능성(routability)을 확인한다.

        목적지 호스트는 random_reachable_ip()로 정한다. 도달 가능한 호스트가
        하나도 없다면, Green 에이전트 요건을 충족하는 가용 호스트가 없다는 뜻이다.
        이는 Red 행동이 일어나지 않은 한 발생할 수 없으므로, 그 경우 행동은
        실패 처리된다.

        이후 목적지 호스트를 다음 기준으로 검사한다.

        1. 호스트가 차단(block)되었는지 확인한다.
            - 차단되었으면 해당 호스트에 network_connections 이벤트를 추가하고
              실패 관찰값(Observation)을 반환한다.

        2. fp_detection_rate 확률로, 호스트에 잘못된(오탐) network_connections
           이벤트를 추가한다.

        위 과정에서 (실패) 관찰값을 반환하지 않았다면 행동은 성공한 것이며,
        성공 관찰값을 반환한다.

        참고
        -----
        이 함수는 SendData 행동의 execute()와 거의 동일하게 동작한다.

        매개변수
        ----------
        state : State
            현재 스텝에서의 시뮬레이션 상태
        반환값
        -------
        obs : Observation
            성공/실패 여부를 담은 관찰값(Observation)
        """

        obs = Observation(False)

        self.dest_ip = self.random_reachable_ip(state)
        if self.dest_ip is None:
            self.log("No reachable hosts.")
            return obs
        
        if not self.available_dest_service:
            return obs

        
        from_host = state.ip_addresses[self.dest_ip]
        from_host_obj = state.hosts[from_host]
        self.dest_port = state.hosts[from_host].get_ephemeral_port()
        from_subnet = state.hostname_subnet_map[from_host].value

        to_host = state.ip_addresses[self.ip_address]
        to_subnet = state.hostname_subnet_map[to_host].value

        # (a) Check for firewall blocks of inbound or outbound connections to and from the to/from subnets
        # (a) to/from 서브넷 사이의 인바운드·아웃바운드 연결이 방화벽에 차단됐는지 검사한다
        # [설명] 양방향 모두 확인한다: to_subnet이 from_subnet을 막았거나, 반대로
        #        from_subnet이 to_subnet을 막았으면 연결 실패로 표시한다
        connection_failure_flag = False
        if to_subnet in state.blocks.keys():
            if from_subnet in state.blocks[to_subnet]:
                connection_failure_flag = True
        if from_subnet in state.blocks.keys():
            if to_subnet in state.blocks[from_subnet]:
                connection_failure_flag = True

        # If they are blocked, then make an event
        # 차단된 경우, network_connections 이벤트를 만든다
        if connection_failure_flag:
            event = NetworkConnection(
                local_address=state.hostname_ip_map[from_host],
                remote_address=state.hostname_ip_map[to_host],
                remote_port=8800)
            from_host_obj.events.network_connections.append(event)
            return obs

        # (b) false positive detection by Blue
        # (b) fp_detection_rate 확률로 Blue 측에 오탐(false positive)을 유발하는 이벤트를 남긴다
        if state.np_random.random() < self.fp_detection_rate:
            
            event = NetworkConnection(
                local_address=self.ip_address,
                remote_address=self.dest_ip,
                remote_port=self.dest_port
            )
            from_host_obj.events.network_connections.append(event)

        obs.set_success(True)
        return obs
    
    def __str__(self):
        return f"{self.__class__.__name__} {self.dest_ip} {self.dest_port}"
