from enum import Enum
from ipaddress import IPv4Network
from typing import Dict, List, Type, Tuple
import inspect

from gym.utils.seeding import RandomNumberGenerator
import numpy as np

from CybORG.Agents import SleepAgent
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Agents.SimpleAgents.EnterpriseGreenAgent import EnterpriseGreenAgent
from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent

from CybORG.Shared import Scenario
from CybORG.Shared.RewardCalculator import EmptyRewardCalculator
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Shared.Enums import Architecture, ProcessName, ProcessType, ProcessVersion
from CybORG.Shared.Scenario import ScenarioAgent
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator
from CybORG.Simulator.Actions.AbstractActions import Monitor, DiscoverRemoteSystems, DiscoverNetworkServices, \
    ExploitRemoteService, PrivilegeEscalate, Impact, DegradeServices, AggressiveServiceDiscovery, \
    StealthServiceDiscovery, DiscoverDeception
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoyHarakaSMPT, DecoyApache, DecoyTomcat, DecoyVsftpd, DeployDecoy
from CybORG.Simulator.Actions.AbstractActions import Analyse, Remove, Restore
from CybORG.Simulator.Actions.Action import Sleep
from CybORG.Simulator.Actions.ConcreteActions import RedSessionCheck, Withdraw
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import AllowTrafficZone, BlockTrafficZone
from CybORG.Simulator.Actions.AbstractActions import Impact, DegradeServices, DiscoverDeception
from CybORG.Simulator.Actions.AbstractActions import DiscoverRemoteSystems, AggressiveServiceDiscovery, StealthServiceDiscovery, PrivilegeEscalate, Monitor
from CybORG.Shared.Session import RedAbstractSession, Session, VelociraptorServer
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Interface import Interface
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Service import Service
from CybORG.Simulator.Subnet import Subnet
from CybORG.Simulator.Actions.GreenActions import GreenAccessService, GreenLocalWork
from CybORG.Simulator.User import User


class SUBNET(str, Enum):
    """A class of class attributes that link subnet enums to the corresponding string subnet name.

    [한국어]
    서브넷 enum과 그에 대응하는 문자열 서브넷 이름을 연결하는 클래스 속성 모음이다.
    str을 상속하므로 각 멤버는 그대로 문자열처럼 쓸 수 있다.
    """
    RESTRICTED_ZONE_A = "restricted_zone_a_subnet"
    OPERATIONAL_ZONE_A = "operational_zone_a_subnet"
    RESTRICTED_ZONE_B = "restricted_zone_b_subnet"
    OPERATIONAL_ZONE_B = "operational_zone_b_subnet"
    CONTRACTOR_NETWORK = "contractor_network_subnet"
    PUBLIC_ACCESS_ZONE = "public_access_zone_subnet"
    ADMIN_NETWORK = "admin_network_subnet"
    OFFICE_NETWORK = "office_network_subnet"
    INTERNET = "internet_subnet"


class EnterpriseScenarioGenerator(ScenarioGenerator):
    """ 
    This class is used to generate scenarios designed for the Cage Challenge 4 (CC4)

    Attributes
    ----------
    background_image : str
        path to a background render image
    used_pids: List[int]
    blue_agent_class : BaseAgent
        class instance that inherits from BaseAgent to be used in scenario for blue agents
    red_agent_class : BaseAgent
        class instance that inherits from BaseAgent to be used in scenario for red agents
    green_agent_class : BaseAgent
        class instance that inherits from BaseAgent to be used in scenario for green agents
    steps : int
        number of steps that make up the episode
    MIN_USER_HOSTS : int
        minimum number of user hosts generated in the dynamic scenario, set at 3
    MAX_USER_HOSTS : int
        maximum number of user hosts generated in the dynamic scenario, set at 10
    MIN_SERVER_HOSTS : int
        minimum number of server hosts generated in the dynamic scenario, set at 1
    MAX_SERVER_HOSTS : int
        maximum number of server hosts generated in the dynamic scenario, set at 6
    MAX_ADDON_SERVICES : int
        maximum number of add-on services generated in the dynamic scenario, set at 10
    MAX_BANDWIDTH : int
        maximum bandwidth of communications, set at 100
    MESSAGE_LENGTH : int
        message length of agent communications, set at 8

    [한국어]
    CAGE Challenge 4(CC4)용 시나리오를 생성하는 시나리오 생성기 클래스다.

    주요 속성:
    - background_image: 배경 렌더 이미지 경로
    - used_pids: 이미 사용한 PID 목록(중복 방지용)
    - blue/red/green_agent_class: 시나리오에 쓸 각 진영 에이전트 클래스(BaseAgent 상속)
    - steps: 에피소드를 구성하는 스텝(step) 수
    - MIN/MAX_USER_HOSTS: 동적 시나리오에서 생성할 사용자 호스트 수의 최소/최대(3/10)
    - MIN/MAX_SERVER_HOSTS: 서버 호스트 수의 최소/최대(1/6)
    - MAX_ADDON_SERVICES: 추가(add-on) 서비스 최대 개수(10)
    - MAX_BANDWIDTH: 통신 최대 대역폭(100)
    - MESSAGE_LENGTH: 에이전트 간 통신 메시지 길이(8)
    """

    MIN_USER_HOSTS = 3
    MAX_USER_HOSTS = 10
    MIN_SERVER_HOSTS = 1
    MAX_SERVER_HOSTS = 6
    MAX_ADDON_SERVICES = 10
    MAX_BANDWIDTH = 100
    MESSAGE_LENGTH = 8

    def __init__(
            self,
            blue_agent_class: Type[BaseAgent] = None,
            red_agent_class: Type[BaseAgent] = None,
            green_agent_class: Type[BaseAgent] = None,
            steps: int = 100
    ):
        """
        Parameters
        ----------
        blue_agent_class : BaseAgent, optional
            The type of agent for blue agents, by default None
        red_agent_class : BaseAgent, optional
            The type of agent for red agents, by default None
        green_agent_class : BaseAgent, optional
            The type of agent for green agents, by default None
        steps : int, optional
            The number of steps, by default 100

        [한국어]
        생성기 초기화. 각 진영(blue/red/green) 에이전트 클래스와 에피소드 스텝 수를
        받는다. 모두 기본값이 있어 인자 없이도 생성 가능하다(steps 기본 100).
        """

        super().__init__()
        self.background_image = "img/blank.png"
        self.used_pids: List[int] = []
        self.blue_agent_class = blue_agent_class
        self.red_agent_class = red_agent_class
        self.green_agent_class = green_agent_class
        self.steps = steps

    def create_scenario(self, np_random: RandomNumberGenerator) -> Scenario:
        """
        This public function initiates the generation of a new Enterprise Scenario.

        This function calls a multitude of private functions to generate:
        
        - subnets
        - hosts
        - agents (red, green, blue)
        - mission phases
        - reward machines

        Finally, the outputs from all the private functions in this class are used to create an instance of the Scenario object - which is returned.

        Parameters
        ----------
        np_random : RandomNumberGenerator
            The RNG that will be used to make "random" decisions when creating scenarios.

        Returns
        -------
        scenario : Scenario
            The new enterprise scenario object

        [한국어]
        새 엔터프라이즈 시나리오 생성을 시작하는 공개 함수다.
        내부의 여러 비공개 함수를 호출해 서브넷, 호스트, 에이전트(red/green/blue),
        미션 단계(mission phase), 보상 머신(Reward Machine)을 만든 뒤, 그 결과를 모아
        Scenario 객체 하나로 조립해 반환한다.

        np_random: 시나리오를 만들 때 "무작위" 결정에 사용할 난수 생성기(RNG)다.
        """
        self.used_pids.clear()
        self.np_random = np_random
        subnets = self._generate_subnets()
        hosts = self._generate_hosts(subnets)
        agents: Dict[str, ScenarioAgent] = {}
        self._generate_blue_agents(subnets, agents)
        self._generate_green_agents(hosts, subnets, agents)
        self._generate_red_agents(subnets, agents)
        team_agents = self._generate_team_agents(agents)
        scenario = Scenario(
            agents=agents,
            team_calcs=None,
            team_agents=team_agents,
            hosts=hosts,
            subnets=subnets,
            mission_phases=self._generate_mission_phases(self.steps),
            allowed_subnets_per_mphase=self._set_allowed_subnets_per_mission_phase(),
            predeployed=False,
            max_bandwidth=self.MAX_BANDWIDTH
        )
        scenario.team_calc = self._generate_team_calcs()

        return scenario

    def _generate_subnets(self) -> Dict[str, Subnet]:
        """
        This function generates the specific subnets required by CC4 for the scenario.

        Returns
        -------
        scenario_subnets : Dict[str, Subnet]
            A dictionary where the keys are the subnet names, and the values are the subnets
            themselves.

        [한국어]
        CC4 시나리오에 필요한 특정 서브넷들을 생성한다.
        반환값은 {서브넷 이름: Subnet 객체} 형태의 딕셔너리다.
        """
        subnet_prefix = 24
        network = IPv4Network("10.0.0.0/16")
        network_subnets = list(network.subnets(new_prefix=subnet_prefix))

        # declare subnet NACLs
        # [설명] NACL(Network Access Control List)은 서브넷 간 트래픽 허용/차단 규칙이다.
        # 각 항목은 {대상 서브넷: {"in": 인바운드, "out": 아웃바운드}} 형태이며,
        # "all"은 전체 허용, "None"은 차단을 뜻한다. 이 규칙이 보안 영역(security zone)
        # 사이의 통신 경계를 정의한다.
        subnet_nacls = {
            SUBNET.RESTRICTED_ZONE_A: {
                SUBNET.OPERATIONAL_ZONE_A: {"in": "None", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
            },
            SUBNET.OPERATIONAL_ZONE_A: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "None"}
            },
            SUBNET.RESTRICTED_ZONE_B: {
                SUBNET.OPERATIONAL_ZONE_B: {"in": "None", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
            },
            SUBNET.OPERATIONAL_ZONE_B: {
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "None"}
            },
            SUBNET.CONTRACTOR_NETWORK: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
            },
            SUBNET.PUBLIC_ACCESS_ZONE: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.ADMIN_NETWORK: {"in": "all", "out": "all"},
                SUBNET.OFFICE_NETWORK: {"in": "all", "out": "all"},
            },
            SUBNET.ADMIN_NETWORK: {
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
                SUBNET.OFFICE_NETWORK: {"in": "all", "out": "all"}
            },
            SUBNET.OFFICE_NETWORK: {
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
                SUBNET.ADMIN_NETWORK: {"in": "all", "out": "all"}
            },
            SUBNET.INTERNET: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.OPERATIONAL_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.OPERATIONAL_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
                SUBNET.ADMIN_NETWORK: {"in": "all", "out": "all"},
                SUBNET.OFFICE_NETWORK: {"in": "all", "out": "all"}
            }
        }
        # Create subnets in a list that can be iterated over
        # 정의한 NACL을 바탕으로 모든 서브넷을 실제 Subnet 객체로 생성한다.
        scenario_subnets = {}
        for subnet_name in SUBNET:
            nacl = subnet_nacls[subnet_name]
            subnet = self._generate_subnet(subnet_name.value, nacl, network_subnets)
            scenario_subnets[subnet_name] = subnet
        return scenario_subnets

    def _generate_subnet(self, subnet_name: str, nacls: Dict[str, Dict[str, str]],
                         ipv4_subnets: List[IPv4Network]) -> Subnet:
        """
        This function generates a new Scenario subnet. It has placeholder values for 'size' and
        'hosts' as we haven't generated the hosts yet.

        Parameters
        ----------
        subnet_name : str
            the label of the subnet
        nacls : Dict[str, Dict[str, str]]
            A dictionary where the keys are the other subnets the subnet being generated interacts
            with, and the values are another dictionary that specifies how information can flow.
        ipv4_subnets : List[IPv4Network]
            A list containing the remaining available IPv4 subnets.

        Returns
        -------
        Subnet
            A new Subnet object

        [한국어]
        새 시나리오 서브넷 하나를 생성한다. 호스트는 아직 만들지 않았으므로
        'size'와 'hosts'는 임시(placeholder) 값으로 둔다.

        - subnet_name: 서브넷 라벨
        - nacls: 이 서브넷이 상호작용하는 다른 서브넷별 정보 흐름 규칙(NACL)
        - ipv4_subnets: 아직 사용하지 않은 IPv4 서브넷 후보 목록
        """
        # [설명] 남은 IPv4 서브넷 후보 중 하나를 무작위로 골라 pop으로 꺼내 쓴다.
        # pop이므로 한 번 배정된 CIDR 대역은 후보 목록에서 제거되어 중복 배정을 막는다.
        selected_subnet_index = self.np_random.choice(len(ipv4_subnets))
        cidr = ipv4_subnets.pop(selected_subnet_index)
        size = len(list(cidr.hosts()))
        return Subnet(subnet_name, size, [], nacls, cidr, [])

    def _set_allowed_subnets_per_mission_phase(self) -> Dict[SUBNET, tuple]:
        """This static function returns the allowed_subnets according to readme for CC4.

        # (0) Pre-planning phase
        # (1) Mission A
        # (2) Mission B

        Returns
        -------
        comms_policy : Array[Array[Tuple(Subnet, Subnet)]]
            A list of pairs of subnets that are allowed to communicate with each other during the policy iteration

        [한국어]
        CC4 README에 정의된, 미션 단계(mission phase)별로 통신이 허용되는 서브넷 쌍을 반환한다.
        단계 구분은 위 영어 주석대로 (0) 사전 계획 단계, (1) 미션 A, (2) 미션 B 이다.
        반환값은 단계별 정책 리스트이며, 각 정책은 (서브넷, 서브넷) 통신 허용 쌍의 목록이다.
        """

        policy_1 = [
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.CONTRACTOR_NETWORK), (SUBNET.ADMIN_NETWORK, SUBNET.CONTRACTOR_NETWORK), (SUBNET.OFFICE_NETWORK, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_A), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_A), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_B), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_B), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_B),
            (SUBNET.RESTRICTED_ZONE_A, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.OPERATIONAL_ZONE_A, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.RESTRICTED_ZONE_B, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.RESTRICTED_ZONE_B, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.OPERATIONAL_ZONE_B, SUBNET.RESTRICTED_ZONE_B)
        ]

        policy_2 = [
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.CONTRACTOR_NETWORK), (SUBNET.ADMIN_NETWORK, SUBNET.CONTRACTOR_NETWORK), (SUBNET.OFFICE_NETWORK, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_A), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_A), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_B), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_B), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_B),
            (SUBNET.RESTRICTED_ZONE_B, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.OPERATIONAL_ZONE_B, SUBNET.RESTRICTED_ZONE_B)
        ]

        policy_3 = [
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.CONTRACTOR_NETWORK), (SUBNET.ADMIN_NETWORK, SUBNET.CONTRACTOR_NETWORK), (SUBNET.OFFICE_NETWORK, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_A), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_A), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_B), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_B), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_B),
            (SUBNET.RESTRICTED_ZONE_A, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.OPERATIONAL_ZONE_A, SUBNET.RESTRICTED_ZONE_A)
        ]

        comms_policy = [policy_1, policy_2, policy_3]

        return comms_policy

    def _generate_hosts(self, subnets: Dict[str, Subnet]) -> Dict[str, Host]:
        """
        This function initiates the creation of all the hosts in the scenario. Since the hosts
        are tried to the subnets, the scenario's subnets are required as a parameter.

        Parameters
        ----------
        subnets : Dict[str, Subnet]
            A dictionary where the keys are the names of the subnets, and the values are the
            subnets themselves.

        Returns
        -------
        Dict[str, Host]
            A dictionary where the keys are the hostname, and the values are the hosts themselves.

        [한국어]
        시나리오의 모든 호스트 생성을 시작한다. 호스트는 서브넷에 묶이므로
        시나리오 서브넷을 인자로 받는다. 반환값은 {호스트 이름: Host 객체} 딕셔너리다.
        """
        host_list = []
        for subnet in subnets.values():
            ip_addresses = list(subnet.cidr.hosts())

            # [설명] 인터넷 서브넷은 라우터/사용자/서버 없이 루트 호스트 1개만 둔다.
            # 따라서 별도로 처리하고 size를 1로 고정한 뒤 다음 서브넷으로 넘어간다.
            if subnet.name == "internet_subnet":
                hostname = "root_internet_host_0"
                subnet.hosts.append(hostname)
                selected_ip_address_index = self.np_random.choice(len(ip_addresses))
                ip_address = ip_addresses.pop(selected_ip_address_index)
                subnet.ip_addresses.append(ip_address)
                host_list.append(self._generate_linux_host(hostname, ip_address, subnet))
                subnet.size = 1
                continue

            # 일반 서브넷은 먼저 라우터 호스트 1개를 만든다.
            hostname = f'{subnet.name}_router'
            subnet.hosts.append(hostname)
            selected_ip_address_index = self.np_random.choice(len(ip_addresses))
            ip_address = ip_addresses.pop(selected_ip_address_index)
            subnet.ip_addresses.append(ip_address)
            host_list.append(self._generate_linux_host(hostname, ip_address, subnet))

            # generate user hosts
            # 사용자 호스트를 MIN~MAX 범위에서 무작위 개수만큼 생성한다(endpoint=True라 양끝 포함).
            num_user_hosts = self.np_random.integers(self.MIN_USER_HOSTS, self.MAX_USER_HOSTS, endpoint=True)
            for i in range(num_user_hosts):
                hostname = f"{subnet.name}_user_host_{i}"
                subnet.hosts.append(hostname)
                selected_ip_address_index = self.np_random.choice(len(ip_addresses))
                ip_address = ip_addresses.pop(selected_ip_address_index)
                subnet.ip_addresses.append(ip_address)
                host_list.append(self._generate_linux_host(hostname, ip_address, subnet))

            # generate servers
            # 서버 호스트도 MIN~MAX 범위에서 무작위 개수만큼 생성한다.
            num_server_hosts = self.np_random.integers(self.MIN_SERVER_HOSTS, self.MAX_SERVER_HOSTS, endpoint=True)
            for i in range(num_server_hosts):
                hostname = f"{subnet.name}_server_host_{i}"
                ip_address = ip_addresses.pop()
                subnet.ip_addresses.append(ip_address)
                host_list.append(self._generate_linux_host(hostname, ip_address, subnet))
                subnet.hosts.append(hostname)

            # 서브넷 크기 = 사용자 호스트 + 서버 호스트 + 라우터 1개.
            subnet.size = num_user_hosts + num_server_hosts + 1

        # Convert list into a dictionary and return it
        # 리스트를 {호스트 이름: Host} 딕셔너리로 변환해 반환한다.
        return {host.hostname: host for host in host_list}

    def _generate_data_links(self, hostname: str, subnet):
        """_summary_

                Parameters
                ----------
                hostname : str
                    The name of the host whose parent is to be defined.
                subnet : _type_
                    The subnet that host belongs to.

                Returns
                -------
                List[str]
                    The parent data link

                [한국어]
                해당 호스트가 연결되는 상위(부모) 데이터 링크 목록을 정의한다.
                - hostname: 부모를 정해줄 호스트 이름
                - subnet: 그 호스트가 속한 서브넷
                인터넷 루트 호스트와 각 라우터는 고정된 토폴로지대로 링크가 정해지고,
                그 외 일반 호스트는 자신이 속한 서브넷의 라우터에 연결된다.
                """
        # [설명] 호스트 종류별로 물리 연결(데이터 링크)을 분기 처리한다.
        # 라우터끼리의 연결 토폴로지가 곧 서브넷 간 네트워크 경로를 형성한다.
        if hostname == "root_internet_host_0":
            data_links = ['restricted_zone_a_subnet_router',
                          'restricted_zone_b_subnet_router',
                          'contractor_network_subnet_router',
                          'public_access_zone_subnet_router']
        elif "_router" in hostname:
            if 'restricted_zone_a' in hostname:
                data_links = ["root_internet_host_0", "operational_zone_a_subnet_router"]
            elif 'restricted_zone_b' in hostname:
                data_links = ["root_internet_host_0", "operational_zone_b_subnet_router"]
            elif 'contractor' in hostname:
                data_links = ["root_internet_host_0"]
            elif 'public_access' in hostname:
                data_links = ["root_internet_host_0",
                              "admin_network_subnet_router",
                              "office_network_subnet_router"]
            elif 'operational_zone_a' in hostname:
                data_links = ["restricted_zone_a_subnet_router"]
            elif 'operational_zone_b' in hostname:
                data_links = ["restricted_zone_b_subnet_router"]
            elif 'admin_network' in hostname:
                data_links = ["public_access_zone_subnet_router"]
            elif 'office_network' in hostname:
                data_links = ["public_access_zone_subnet_router"]
            else:
                raise ValueError(f"Unexpected router {hostname} in subnet {subnet}")
        else:
            data_links = [f"{subnet.name}_router"]
        return data_links

    def _between_subnet_links(self, hostname: str):
        """Additional info about other hosts that red gains when it get root controll of the host.

        Parameters
        ----------
        hostname : str
            the name of the host.

        Returns
        -------
        links : Dict[str, List[str]]
            hosts that have (directional) links to eachother

        [한국어]
        Red 에이전트가 어떤 호스트의 루트 권한을 얻었을 때 추가로 알게 되는,
        다른 호스트들에 대한 정보를 정의한다. 반환값은 서로 (방향성) 링크를 가진
        호스트들의 매핑이다. 목록에 없는 호스트는 None을 반환한다.
        """
        links = {
            "contractor_network_subnet_server_host_0": [
                "restricted_zone_a_subnet_server_host_0",
                "restricted_zone_b_subnet_server_host_0",
                "public_access_zone_subnet_server_host_0",
                ],
            "restricted_zone_a_subnet_server_host_0": [
                "operational_zone_a_subnet_server_host_0",
                "contractor_network_subnet_server_host_0"
            ],
            "operational_zone_a_subnet_server_host_0": [
                "restricted_zone_a_subnet_server_host_0"
            ],
            "restricted_zone_b_subnet_server_host_0": [
                "operational_zone_b_subnet_server_host_0",
                "contractor_network_subnet_server_host_0"
            ],
            "operational_zone_b_subnet_server_host_0": [
                "restricted_zone_b_subnet_server_host_0"
            ],
            "public_access_zone_subnet_server_host_0": [
                "admin_network_subnet_server_host_0",
                "office_network_subnet_server_host_0",
                "contractor_network_subnet_server_host_0"
            ],
            "admin_network_subnet_server_host_0": [
                "public_access_zone_subnet_server_host_0"
            ],
            "office_network_subnet_server_host_0": [
                "public_access_zone_subnet_server_host_0"
            ]
        }
        if not hostname in links:
            return None
        # [설명] 연결된 각 호스트에 대해 IP 주소 인터페이스 정보만 노출하는 형태로 가공한다.
        info = {}
        for host in links[hostname]:
            info[host] = {'Interfaces': 'ip_address'}
        return info

    def _generate_linux_host(self, hostname: str, ip_address: IPv4Network, subnet: Subnet) -> Host:
        """
        Generates a host for the scenario with linux specifications.

        Parameters
        ----------
        hostname : str
            The label to be given to the new host.
        ip_address : IPv4Network
            The IP address to be assigned to the new host.
        subnet : Subnet
            The subnet the new host will belong to.

        Returns
        -------
        Host
            The new (linux) Host.

        [한국어]
        리눅스 사양으로 시나리오용 호스트 하나를 생성한다.
        - hostname: 새 호스트에 부여할 라벨
        - ip_address: 새 호스트에 할당할 IP 주소
        - subnet: 새 호스트가 속할 서브넷
        """
        linux_distro_options = [
            { "OSDistribution": "UBUNTU", "OSVersion": "22.04.2 LTS" },
            { "OSDistribution": "KALI", "OSVersion": "K2019_4" }
        ]
        system_info = { 'OSType': "LINUX", "Architecture": Architecture.x64 }

        OSDistribution = self.np_random.choice(linux_distro_options)
        system_info.update(OSDistribution)
        interfaces = [Interface(
            name='eth0',
            ip_address=ip_address,
            subnet=subnet.cidr,
            interface_type='wired',
            data_links=self._generate_data_links(hostname, subnet),
            swarm=False
        )]
        root_user = User(groups=[{'GID': 0, 'Group Name': 'root'}], uid=0, username='root')
        user_group = {'GID': 1, 'Group Name': 'user'}
        # bruteforceable=True: 이 사용자 계정은 무차별 대입(brute force) 공격 대상이 될 수 있다.
        user = User(groups=[user_group], uid=1000, username='user', bruteforceable=True)

        # [설명] 인터넷 루트 호스트와 라우터는 일반 서비스를 두지 않고 ping에도 응답하지 않는다.
        # 그 외 호스트만 서비스/프로세스를 생성하고 ping에 응답한다.
        if hostname == "root_internet_host_0" or 'router' in hostname:
            services = None
            processes = None
            respond_to_ping = False
        else:
            services = self._generate_linux_host_services(hostname)
            processes = self._generate_linux_host_processes(services)
            respond_to_ping = True

        return Host(
            hostname=hostname,
            host_type="",
            processes=processes,
            system_info=system_info,
            interfaces=interfaces,
            info=self._between_subnet_links(hostname),
            users=[root_user, user],
            services=services,
            respond_to_ping=respond_to_ping,
            np_random=self.np_random,
        )

    def _generate_linux_host_services(self, hostname: str) -> Dict[str, Service]:
        """
        This function generates a dict of random services for a linux host.

        Parameters
        ----------
        hostname : str
            The name of the host to have services generated.

        Returns
        -------
        Dict[str, dict]
            A dictionary where the keys are the service names, and the values are the dictionaries
            containing the services themselves.

        [한국어]
        리눅스 호스트용 서비스 딕셔너리를 무작위로 생성한다.
        SSHD는 필수로 두고, operational 호스트에는 OTSERVICE를 추가하며,
        그 외 추가(add-on) 서비스는 후보 중 일부를 무작위로 골라 붙인다.
        """
        # Set up the mandatory services.
        # 필수 서비스 SSHD를 먼저 설정한다.
        services = { ProcessName.SSHD: Service(process=self._generate_pid()) }
        # operational(운영) 호스트에는 OT 서비스를 추가한다.
        if "operational" in hostname:
            services[ProcessName.OTSERVICE] = Service(process=self._generate_pid())

        # Define what the options are for additional services
        # 추가로 붙일 수 있는 선택 서비스 후보 목록을 정의한다.
        addon_services_options = {
            ProcessName.APACHE2: Service(process=self._generate_pid()),
            ProcessName.MYSQLD: Service(process=self._generate_pid()),
            ProcessName.SMTP: Service(process=self._generate_pid()),
        }
        # Choose a random number of the optional services
        # [설명] 선택 서비스를 무작위 개수만큼 고른다. 후보 수와 MAX_ADDON_SERVICES 중
        # 작은 값을 상한으로 삼고, pop으로 꺼내 같은 서비스가 중복 선택되지 않게 한다.
        max_addon_services = min(len(addon_services_options), self.MAX_ADDON_SERVICES)
        num_addon_services = self.np_random.integers(0, max_addon_services, endpoint=True)
        for _ in range(num_addon_services):
            choice = self.np_random.choice(list(addon_services_options.keys()))
            services[choice] = addon_services_options.pop(choice)
        return services

    def _generate_pid(self) -> int:
        """
        Generates a dummy process ID number that is not already contained within the list of used
        process IDs.

        Returns
        -------
        int
            The new process ID.

        [한국어]
        아직 사용하지 않은 더미 프로세스 ID(PID)를 하나 생성한다.
        used_pids 목록에 없는 값이 나올 때까지 무작위로 뽑아 중복을 피한다.
        """
        while True:
            pid = self.np_random.integers(1000, 10000)  # generate a random 4-digit number  # 무작위 4자리 숫자 생성
            if pid not in self.used_pids:  # check if the generated PID is not in the used_pids list  # 이미 쓴 PID인지 확인
                self.used_pids.append(pid)
                return pid  # if not, return the generated PID  # 사용 가능하면 반환

    def _generate_linux_host_processes(self, services: Dict[str, Service]) -> List[dict]:
        """
        Creates a set of randomised processes for a linux host based on its services.

        Parameters
        ----------
        services : dict
            A dict containing the services that were made for the host.

        Returns
        -------
        List[dict]
            A list containing dicts that represent the processes for the linux host.

        [한국어]
        호스트의 서비스 목록을 바탕으로 리눅스 호스트용 프로세스 집합을 무작위로 만든다.
        각 서비스 종류에 맞는 포트와 프로세스 타입을 매핑해 Process 객체를 생성한다.
        """
        processes = []
        # [설명] prob_vuln_proc_occurs는 취약 프로세스 발생 확률 기준값이다.
        # 1.0이므로 아래 'prob_vuln_proc_occurs < random()' 조건은 사실상 항상 거짓이 되어,
        # 현재 설정에서는 취약 버전/속성 부여 분기가 실행되지 않는다.
        prob_vuln_proc_occurs = 1.0

        local_processes = {
            ProcessName.SSHD: {'port': 22, 'type': ProcessType.SSH},
            ProcessName.APACHE2: {'port': 80, 'type': ProcessType.WEBSERVER},
            ProcessName.MYSQLD: {'port': 3390, 'type': ProcessType.MYSQL},
            ProcessName.SMTP: {'port': 25, 'type': ProcessType.SMTP},
            ProcessName.OTSERVICE: {'port': 1, 'type': ProcessType.UNKNOWN},
            "FTP": {'port': 21, 'type': ProcessType.FEMITTER}
        }

        for key, service in services.items():
            process = Process(
                process_name=key,
                pid=service.process,
                path='/ usr / sbin',
                username="user",
                open_ports=[{
                    "local_address": "0.0.0.0",
                    "local_port": local_processes[key]['port'],
                }],
                process_type=local_processes[key]['type']
            )

            # SMTP 프로세스에는 기본적으로 HARAKA 2.8.9 버전을 부여한다.
            if local_processes[key]['type'] == ProcessType.SMTP:
                process.version = ProcessVersion.HARAKA_2_8_9

            # [설명] 확률적으로 취약한 프로세스를 만드는 분기(웹서버에 rfi 속성, SMTP를 구버전으로).
            # 단, prob_vuln_proc_occurs=1.0이라 이 조건은 현재 거의 항상 거짓이다.
            if prob_vuln_proc_occurs < self.np_random.random():
                if local_processes[key]['type'] == ProcessType.WEBSERVER:
                    process.properties = ['rfi']
                if local_processes[key]['type'] == ProcessType.SMTP:
                    process.version = ProcessVersion.HARAKA_2_7_0

            processes.append(process)
        return processes

    def _generate_blue_agents(self, subnets: Dict[str, Subnet], agents: Dict[str, ScenarioAgent]):
        """
        Populates the agents dict with blue agents. These blue agents are distributed between the
        five security zones.
        Parameters
        ----------
        subnets : Dict[str, Subnet]
            A dict containing the subnets of the scenario.
        agents : Dict[str, ScenarioAgent]
            a dict containing the agents of the scenario.

        [한국어]
        agents 딕셔너리에 Blue 에이전트(방어 측)를 채워 넣는다.
        Blue 에이전트는 다섯 개 보안 영역(security zone)에 나뉘어 배치된다.
        - subnets: 시나리오의 서브넷 딕셔너리
        - agents: 시나리오 에이전트들을 담는 딕셔너리(여기에 추가됨)
        """
        blue_actions = [AllowTrafficZone, BlockTrafficZone, Monitor, Analyse, Restore, Remove, DeployDecoy, Sleep]
        blue_agent_allowed_subnets = [
            [SUBNET.RESTRICTED_ZONE_A.value],
            [SUBNET.OPERATIONAL_ZONE_A.value],
            [SUBNET.RESTRICTED_ZONE_B.value],
            [SUBNET.OPERATIONAL_ZONE_B.value],
            [SUBNET.PUBLIC_ACCESS_ZONE.value, SUBNET.ADMIN_NETWORK.value, SUBNET.OFFICE_NETWORK.value]
        ]
        for allowed_subnets in blue_agent_allowed_subnets:
            i = blue_agent_allowed_subnets.index(allowed_subnets)
            agent_name = f"blue_agent_{i}"
            # Determine which subnet the agent is starting on
            # 이 에이전트가 어느 서브넷에서 시작하는지 정한다.
            starting_subnet = subnets[self.np_random.choice(allowed_subnets)]
            # Set-up session objects for all the hosts in the possible subnets
            # 담당 가능한 서브넷의 모든 호스트에 대해 세션 객체를 만든다.
            sessions: List[Session] = []
            allowed_hosts = []
            for subnet_name in allowed_subnets:
                subnet = subnets[subnet_name]
                allowed_hosts += subnet.hosts
            # Set-up OSINT based on the subnet the starting host is in.
            # 시작 호스트가 속한 서브넷을 기준으로 OSINT(사전 수집 정보)를 구성한다.
            osint = {"Hosts": {}}
            for host in allowed_hosts:
                osint["Hosts"][host] = {
                    'Interfaces': 'All', 'System info': 'All', 'User info': 'All'
                }
            # Make one of the sessions the parent session
            # 세션 중 하나를 부모(parent) 세션으로 지정한다.
            parent_host = self.np_random.choice(allowed_hosts)
            for host in allowed_hosts:
                j = allowed_hosts.index(host)
                session_class = Session
                session_type = 'blue_session'
                # [설명] 부모 호스트의 세션만 VelociraptorServer(상위 관제 세션)로 만들고,
                # 나머지는 일반 blue_session으로 둔 뒤 아래에서 부모 세션에 연결한다.
                if host == parent_host:
                    session_class = VelociraptorServer
                    session_type = "VelociraptorServer"
                session = session_class(
                    name=f"blue_session_{i}_{j}",
                    username="ubuntu",
                    session_type=session_type,
                    hostname=host,
                    pid=None,
                    ident=None,
                    agent=None
                )
                sessions.append(session)
            # 부모 세션을 찾아 자식 수를 기록하고, 나머지 세션의 부모로 연결한다.
            parent_session = next(s for s in sessions if s.hostname == parent_host)
            parent_session.num_children = len(sessions) - 1
            for session in sessions:
                if session.name == parent_session.name: continue
                session.parent = parent_session.name
            # Determine agent type
            # 에이전트 종류(타입)를 결정한다.
            agent_type = None
            if self.blue_agent_class:
                agent_type = self.blue_agent_class(agent_name)
            default_actions = (Monitor, {'session': 0, 'agent': agent_name})
            agents[agent_name] = ScenarioAgent(
                agent_name, "Blue", sessions, blue_actions, osint, allowed_subnets, agent_type, True, default_actions
            )

    def _generate_green_agents(self, hosts: Dict[str, Host], subnets: Dict[str, Subnet], agents: Dict[str, ScenarioAgent]):
        """
        Populates the agents dict with green agents. There is a green agents for every host in the
        scenario.

        Parameters
        ----------
        hosts : Dict[str, Host]
            A dict containing all of the hosts of the scenario.
        subnets : Dict[str, Subnet]
            A dict containing all the subnets of the scenario.
        agents : Dict[str, ScenarioAgent]
            A dict containing all of the agents of the scenario (so far.)

        [한국어]
        agents 딕셔너리에 Green 에이전트(정상 사용자)를 채워 넣는다.
        시나리오의 모든 사용자 호스트마다 Green 에이전트가 하나씩 배치된다.
        - hosts: 시나리오의 모든 호스트 딕셔너리
        - subnets: 시나리오의 모든 서브넷 딕셔너리
        - agents: 지금까지 만든 에이전트 딕셔너리(여기에 추가됨)
        """
        green_actions = [GreenAccessService, GreenLocalWork, Sleep]
        green_agent_count = 0
        for subnet in subnets.values():
            for hostname in subnet.hosts:
                # 사용자 호스트가 아니면(라우터·서버 등) Green 에이전트를 두지 않는다.
                if "user" not in hostname: continue
                # Set-up OSINT based on the subnet the starting host is in.
                # 시작 호스트가 속한 서브넷을 기준으로 OSINT(사전 수집 정보)를 구성한다.
                osint = {"Hosts": {}}
                for host in subnet.hosts:
                    osint["Hosts"][host] = {
                        'Interfaces': 'All', 'System info': 'All', 'User info': 'All'
                    }
                agent_name = f"green_agent_{green_agent_count}"
                green_agent_count += 1
                session = Session(
                    name=f"green_session_{green_agent_count}",
                    username="ubuntu",
                    session_type="green_session",
                    hostname=hostname,
                    pid=None,
                    ident=None,
                    agent=None
                )
                agent_type = None
                default_actions = (Sleep, {})
                # [설명] 지정된 green_agent_class 종류에 따라 생성 방식을 분기한다.
                # EnterpriseGreenAgent는 자기 호스트 IP가 필요하고, SleepAgent는 행동을
                # Sleep만으로 제한하며, 그 외에는 이름만 넘겨 생성한다.
                if self.green_agent_class:
                    if self.green_agent_class == EnterpriseGreenAgent:
                        host_ip = hosts[hostname].interfaces[0].ip_address
                        agent_type = self.green_agent_class(name=agent_name, np_random=self.np_random, own_ip=host_ip)
                    elif self.green_agent_class == SleepAgent:
                        green_actions = [Sleep]
                    else:
                        agent_type = self.green_agent_class(agent_name)
                agents[agent_name] = ScenarioAgent(
                    agent_name, "Green", [session], green_actions, osint, [subnet.name], agent_type, True,
                    default_actions
                )

    def _generate_red_agents(self, subnets: Dict[str, Subnet], agents):
        """
        Populates the agents dict with red agents. These red agents are distributed between the
        five security zones. Only one of them starts as active.

        Parameters
        ----------
        subnets : Dict[str, Subnet]
            A dict containing the subnets of the scenario.
        agents : _type_
            A dict containing all of the agents of the scenario (so far.)

        [한국어]
        agents 딕셔너리에 Red 에이전트(공격 측)를 채워 넣는다.
        Red 에이전트는 다섯 개 보안 영역에 나뉘어 배치되며, 처음에 활성(active) 상태인
        것은 협력업체 네트워크(Contractor network)에서 시작하는 단 하나뿐이다.
        - subnets: 시나리오의 서브넷 딕셔너리
        - agents: 지금까지 만든 에이전트 딕셔너리(여기에 추가됨)
        """

        red_actions = [
            DiscoverRemoteSystems, AggressiveServiceDiscovery, StealthServiceDiscovery,
            ExploitRemoteService, PrivilegeEscalate, DegradeServices, DiscoverDeception,
            Impact, Withdraw, Sleep
        ]
        red_agent_allowed_subnets = [
            [SUBNET.CONTRACTOR_NETWORK.value],
            [SUBNET.RESTRICTED_ZONE_A.value],
            [SUBNET.OPERATIONAL_ZONE_A.value],
            [SUBNET.RESTRICTED_ZONE_B.value],
            [SUBNET.OPERATIONAL_ZONE_B.value],
            [SUBNET.PUBLIC_ACCESS_ZONE.value, SUBNET.ADMIN_NETWORK.value, SUBNET.OFFICE_NETWORK.value]
        ]
        red_agent_types: List[Type[BaseAgent]] = [SleepAgent, ]
        for allowed_subnets in red_agent_allowed_subnets:
            i = red_agent_allowed_subnets.index(allowed_subnets)
            agent_name = f"red_agent_{i}"
            starting_subnet = subnets[self.np_random.choice(allowed_subnets)]
            # 시작 호스트는 라우터를 제외한 호스트 중에서 무작위로 고른다.
            allowed_starting_hosts = [h for h in starting_subnet.hosts if 'router' not in h]
            starting_host = self.np_random.choice(allowed_starting_hosts)
            osint = { "Hosts": {}}
            osint["Hosts"][starting_host] = {'Interfaces': 'All', 'System info': 'All', 'User info': 'All'}

            sess_list = []
            active = False

            # Agent is active if it's the one that is in the contractor network.
            # 협력업체 네트워크(Contractor network)에서 시작하는 에이전트만 활성(active) 상태로 둔다.
            if starting_subnet.name == SUBNET.CONTRACTOR_NETWORK.value:
                sess_list.append(RedAbstractSession(
                    name=f"red_session_{i}",
                    username="ubuntu",
                    session_type="RedAbstractSession",
                    hostname=starting_host,
                    pid=None,
                    ident=None,
                    agent=None
                ))
                active = True

            # Determine agent type
            # 에이전트 종류(타입)를 결정한다.
            # [설명] 사용자가 red_agent_class를 지정하면, 그 클래스 생성자의 인자 목록을
            # inspect로 확인해 'np_random'을 받는지에 따라 호출 방식을 다르게 한다.
            # FiniteStateRedAgent는 추가로 담당 서브넷(agent_subnets)까지 넘긴다.
            agent_type = self.np_random.choice(red_agent_types)(agent_name)
            default_actions = (RedSessionCheck, {'session': 0, 'agent': agent_name})
            if self.red_agent_class:
                parameter_list = inspect.getfullargspec(self.red_agent_class).args
                if 'np_random' in parameter_list:
                    if isinstance(self.red_agent_class, FiniteStateRedAgent) or issubclass(self.red_agent_class, FiniteStateRedAgent):
                        agent_subnets = [subnets[sn].cidr for sn in allowed_subnets]
                        agent_type = self.red_agent_class(agent_name, np_random=self.np_random, agent_subnets=agent_subnets)
                    else:
                        agent_type = self.red_agent_class(agent_name, np_random=self.np_random)
                else:
                    agent_type = self.red_agent_class(agent_name)
            agents[agent_name] = ScenarioAgent(agent_name, "Red", sess_list, red_actions, osint, allowed_subnets,
                                               agent_type, active, default_actions)

    def _generate_team_calcs(self) -> dict:
        """
        Returns
        -------
        team_calcs : Dict[str, Dict[str, BlueRewardMachine]]
            A dictionary of reward calculator instances for each agent type

        [한국어]
        진영(team)별 보상 계산기(reward calculator) 인스턴스를 담은 딕셔너리를 반환한다.
        Blue 진영만 BlueRewardMachine(보상 머신)을 쓰고, Red/Green은 보상이 없는
        EmptyRewardCalculator를 쓴다.
        """
        team_calcs = {
            "Blue": { 'BlueRewardMachine': BlueRewardMachine("Blue") },
            "Red": { 'None': EmptyRewardCalculator("Red") },
            "Green": { 'None': EmptyRewardCalculator("Green") }
        }
        return team_calcs

    def _generate_team_agents(self, agents: Dict[str, ScenarioAgent]) -> Dict[str, List[str]]:
        """
        Creates a dict where the keys are the different teams, and the values are lists of the
        names of agents that belong to those teams.

        Parameters
        ----------
        agents : Dict[str, ScenarioAgent]
            A dict that contains all the agents of the scenario.

        Returns
        -------
        Dict[str, List[str]]
            _description_

        [한국어]
        진영(team)을 키로 하고, 그 진영에 속한 에이전트 이름 목록을 값으로 갖는 딕셔너리를 만든다.
        에이전트 이름에 진영명(소문자)이 들어있는지로 소속을 판별한다.
        예: "blue_agent_0"은 이름에 "blue"가 있으므로 Blue 진영으로 분류된다.
        """
        team_agents = {}
        for team in ["Blue", "Red", "Green"]:
            team_agents[team] = [agent for agent in agents.keys() if team.lower() in agent]
        return team_agents


    def _generate_mission_phases(self, steps) -> Tuple[int, int, int]:
        # [설명] 전체 스텝(steps)을 세 미션 단계(mission phase)로 최대한 균등하게 나눈다.
        # 3으로 나눈 몫(quotient)을 기본으로 하고, 나머지(remainder)만큼 앞 단계부터 1씩 더 배분한다.
        # 예: steps=100 -> (34, 33, 33), steps=101 -> (34, 34, 33).
        quotient, remainder = divmod(steps, 3)
        if remainder == 2:
           return (quotient+1, quotient+1, quotient)
        if remainder == 1:
            return (quotient+1, quotient, quotient)
        return (quotient, quotient, quotient)

    def determine_done(self, env_controller) -> bool:
        """ Determines when the episode ends 
        
        Returns
        -------
        Boolean
            T/F value for if episode is to end

        [한국어]
        에피소드가 끝나는 시점을 판정한다. 현재 스텝 수가 (전체 steps - 1) 이상이면
        에피소드를 종료한다는 의미로 True를 반환한다.
        """
        return env_controller.step_count >= (self.steps-1)
