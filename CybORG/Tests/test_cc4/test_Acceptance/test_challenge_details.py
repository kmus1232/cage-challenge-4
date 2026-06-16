from collections import defaultdict
from typing import List
import pytest
from pytest_mock import MockerFixture
from CybORG.Simulator.Actions import Sleep
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork

def test_has_four_subnetworks(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 1:
    The network for this challenge is split into four smaller networks as can be seen in Figure 1.
    Two of these are deployed networks, one is the Headquarters (HQ) network and another is the
    Contractor network. These networks connect together via the internet.

    [한국어]
    챌린지 상세 1문단: 본 챌린지의 네트워크는 네 개의 작은 네트워크로 나뉜다.
    이 중 둘은 배치 네트워크(deployed network), 하나는 본부(HQ) 네트워크,
    나머지 하나는 협력업체 네트워크(Contractor network)다. 이들은 인터넷으로 연결된다.
    이 테스트는 서브넷이 정확히 4개인지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    internet_node = sim_controller.state.hosts['root_internet_host_0']
    internet_connections = internet_node.interfaces[0].data_links
    assert len(internet_connections) == 4, f"Network is split into {len(internet_connections)} subnetworks, not 4!"

def test_has_correct_security_zones(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 2:
    Each deployed network consists of two security zones: a restricted zone and an operational
    zone. The Headquarters network consists of three security zones: a Public Access Zone, an Admin
    Zone and an Office Network. The Contractor network only contains a single UAV control zone.

    [한국어]
    챌린지 상세 2문단: 각 배치 네트워크는 두 개의 보안 영역(security zone)으로 구성된다
    — restricted zone과 operational zone. 본부(HQ) 네트워크는 세 개의 보안 영역
    (Public Access Zone, Admin Zone, Office Network)으로 구성된다. 협력업체 네트워크
    (Contractor network)는 단일 UAV 제어 영역만 포함한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    subnets = sim_controller.subnet_cidr_map

    assert subnets["restricted_zone_a_subnet"] is not None
    assert subnets["operational_zone_a_subnet"] is not None
    assert len([s for s in subnets.keys() if "zone_a" in s]) == 2

    assert subnets["restricted_zone_b_subnet"] is not None
    assert subnets["operational_zone_b_subnet"] is not None
    assert len([s for s in subnets.keys() if "zone_b" in s]) == 2

    assert subnets["public_access_zone_subnet"] is not None
    assert subnets["admin_network_subnet"] is not None
    assert subnets["office_network_subnet"] is not None

    assert subnets["contractor_network_subnet"] is not None
    assert len([s for s in subnets.keys() if "contractor" in s]) == 1

def test_host_counts_are_random(cc4_cyborg_list: List[CybORG]):
    """
    From Challenge details, paragraph 3:
    In order to encourage the development of robust agents, the number of hosts in each security
    zone

    [한국어]
    챌린지 상세 3문단: 견고한 에이전트 개발을 유도하기 위해, 각 보안 영역의 호스트 수는
    (그리고 그 서비스는) 무작위로 정해진다. 이 테스트는 인스턴스마다 전체 호스트 수가
    달라지는지(즉 무작위인지) 확인한다.
    """
    host_counts_set = {len(cyborg.environment_controller.state.hosts) for cyborg in cc4_cyborg_list}
    assert len(host_counts_set) > 1, "All instances have same number of hosts"

def test_host_services_are_random(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    and their services will be randomised.

    [한국어]
    챌린지 상세 3문단(이어서): 호스트의 서비스도 무작위로 정해진다. 이 테스트는
    모든 호스트가 동일한 서비스 집합을 갖지 않는지(무작위인지) 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    hosts = sim_controller.state.hosts.values()
    host_services = {frozenset(host.services.keys()) for host in hosts}
    assert len(host_services) > 1, "All hosts have identical services"

def test_zones_have_correct_number_of_servers(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    Each zone will have between 1-6 servers.

    [한국어]
    챌린지 상세 3문단: 각 영역은 1~6대의 서버를 갖는다. 이 테스트는 영역별 서버 수가
    범위(1 이상 7 미만) 안에 있는지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    server_counts = defaultdict(int)
    servers = [host for host in sim_controller.state.hosts.values() if "server" in host.hostname]
    for server in servers:
        subnet = sim_controller.state.hostname_subnet_map[server.hostname]
        server_counts[subnet] += 1
    for count in server_counts.values():
        assert 0 < count < 7, f"{subnet} has an invalid number of server hosts, {count}!"

def test_zones_have_correct_number_of_user_hosts(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    Each zone will have between 3-10 user hosts.

    [한국어]
    챌린지 상세 3문단: 각 영역은 3~10대의 사용자 호스트를 갖는다. 이 테스트는 영역별
    사용자 호스트 수가 범위(2 초과 11 미만) 안에 있는지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    user_host_counts = defaultdict(int)
    user_hosts = [host for host in sim_controller.state.hosts.values() if "user" in host.hostname]
    for user_host in user_hosts:
        subnet = sim_controller.state.hostname_subnet_map[user_host.hostname]
        user_host_counts[subnet] += 1
    for subnet, count in user_host_counts.items():
        assert 2 < count < 11, f"{subnet} has an invalid number of user hosts, {count}!"

def test_hosts_have_correct_number_of_services(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    Each host will have a minimum of 1 service with a maximum of 10.

    [한국어]
    챌린지 상세 3문단: 각 호스트는 최소 1개에서 최대 10개의 서비스를 갖는다. 이 테스트는
    인터넷 호스트와 라우터를 제외한 모든 호스트의 서비스 수가 범위(1 이상 11 미만) 안에
    있는지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    hosts_with_no_services = ['root_internet_host_0']
    for host in sim_controller.state.hosts.values():
        if not host.hostname in hosts_with_no_services and 'router' not in host.hostname:
            assert 0 < len(host.services) < 11

def test_defenders_are_on_correct_networks(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 4:
    The network will have 5 network defenders. Each deployed network will have two, one for each
    security zone. The Headquarters will have a single defensive agent for all zones, while the
    Contractor network will be undefended.

    [한국어]
    챌린지 상세 4문단: 네트워크에는 5명의 방어자(Blue 에이전트)가 있다. 각 배치 네트워크는
    보안 영역마다 하나씩 둘을 갖고, 본부(HQ)는 모든 영역을 담당하는 단일 방어 에이전트를
    가지며, 협력업체 네트워크(Contractor network)는 방어되지 않는다. 이 테스트는 Blue
    에이전트가 정확히 5명이고 각자 담당 서브넷이 올바른지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agents = sim_controller.agent_interfaces.values()
    defenders = [agent for agent in agents if "blue" in agent.agent_name]
    assert len(defenders) == 5
    allowed_subnets = [
        ["restricted_zone_a_subnet"],
        ["operational_zone_a_subnet"],
        ["restricted_zone_b_subnet"],
        ["operational_zone_b_subnet"],
        ["public_access_zone_subnet", "admin_network_subnet", "office_network_subnet"]
    ]
    for subnets in allowed_subnets:
        assert len([d for d in defenders if d.allowed_subnets == subnets]) == 1

def test_red_team_starts_in_contractor_network(cc4_cyborg_list: List[CybORG]):
    """
    From Challenge details, paragraph 5:
    Red team begins the operation with access to a random machine in the contractor network.

    [한국어]
    챌린지 상세 5문단: Red 팀(공격 측)은 협력업체 네트워크(contractor network)의 무작위
    머신에 대한 접근 권한을 가지고 작전을 시작한다. 이 테스트는 활성 Red 에이전트가 하나뿐이고,
    시작 호스트가 인스턴스마다 무작위이며 협력업체 네트워크에 속하는지 확인한다.
    """
    all_hosts = []
    for cyborg in cc4_cyborg_list:
        sim_controller: SimulationController = cyborg.environment_controller
        agents = sim_controller.agent_interfaces.values()
        attackers = [agent for agent in agents if "red" in agent.agent_name and agent.active]
        assert len(attackers) == 1
        all_hosts.append(sim_controller.state.sessions[attackers[0].agent_name][0].hostname)

    assert len(set(all_hosts)) > 1
    assert 'contractor_network' in all_hosts[0]

def test_red_agents_can_spawn(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    Every turn there is also a small chance that a red agent will spawn in the HQ network.

    [한국어]
    챌린지 상세 5문단: 매 턴마다 본부(HQ) 네트워크에 Red 에이전트가 생성될 작은 확률이 있다.
    이 테스트는 100스텝 안에 HQ 서브넷에서 새 Red 에이전트가 활성화되는지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller

    # Assert that there's only one active red agent to begin with.
    # 처음에는 활성 Red 에이전트가 하나뿐임을 확인한다.
    agents = sim_controller.agent_interfaces.values()
    red_agents = [agent for agent in agents if "red" in agent.agent_name and agent.active]
    assert len(red_agents) == 1

    # Assert that a new red agent will activate in the HQ subnet within 100 steps.
    # 100스텝 안에 HQ 서브넷에서 새 Red 에이전트가 활성화됨을 확인한다.
    hq_network_subnets = [
        'public_access_zone_subnet', 'admin_network_subnet', 'office_network_subnet'
    ]
    passed = False
    for _ in range(100):
        cc4_cyborg.step()
        agents = sim_controller.agent_interfaces.values()
        red_agents = [agent for agent in agents if "red" in agent.agent_name and agent.active]
        if len(red_agents) > 1:
            passed = any(
                agent for agent in red_agents if agent.allowed_subnets == hq_network_subnets
            )
            if passed: break
    assert passed, "No additional red agents spawned after 100 steps!"

def test_red_can_enter_network_via_compromised_service(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    Otherwise, red can only enter the deployed networks when a green user accesses a compromised
    service.

    [한국어]
    챌린지 상세 5문단: 그 외에는 Green 사용자(정상 사용자)가 침해된 서비스에 접근할 때에만
    Red가 배치 네트워크(deployed network)에 진입할 수 있다. 이 테스트는 Green 사용자의
    로컬 작업(GreenLocalWork)으로 인해 호스트에 Red 세션이 생기는지 확인한다.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00 # forces PhishingEmail action  # PhishingEmail 행동을 강제로 발생시킴

    preexisting_red_on_host = True
    while preexisting_red_on_host:
        cyborg, agent_interface = create_cyborg_env()
        state = cyborg.environment_controller.state
        green_hostname = state.ip_addresses[agent_interface.agent.own_ip]

        before_agent_sessions_on_host = [agent for agent, arr_sessions in state.hosts[green_hostname].sessions.items() if len(arr_sessions) > 0]
        preexisting_red_on_host = False
        for agent_name in before_agent_sessions_on_host:
            if 'red' in agent_name:
                preexisting_red_on_host = True

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)

    after_agent_sessions_on_host = [agent for agent, arr_sessions in state.hosts[green_hostname].sessions.items() if len(arr_sessions) > 0]

    red_on_host = False
    for agent_name in after_agent_sessions_on_host:
        if 'red' in agent_name:
            red_on_host = True
    assert red_on_host


def test_only_one_red_agent_per_zone(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    There is a maximum of one red agent in each zone.

    [한국어]
    챌린지 상세 5문단: 각 영역(zone)에는 Red 에이전트가 최대 한 명까지만 존재한다.
    이 테스트는 영역별 Red 에이전트 수가 1인지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    zone_red_agent_counts = defaultdict(int)
    agents = sim_controller.agent_interfaces.values()
    attackers = [agent for agent in agents if "red" in agent.agent_name]
    for attacker in attackers:
        for zone in attacker.allowed_subnets:
            zone_red_agent_counts[zone] += 1
    for zone, count in zone_red_agent_counts.items():
        assert count == 1, f"{zone} has more than one ({count}) red agent!"

def test_red_agents_can_be_on_multiple_hosts(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    Red agents can maintain a presence on multiple hosts.

    [한국어]
    챌린지 상세 5문단: Red 에이전트는 여러 호스트에 동시에 존재(거점 유지)할 수 있다.
    이 테스트는 100스텝 안에 한 Red 에이전트가 둘 이상의 호스트에 세션을 갖는 경우가
    나타나는지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    for _ in range(100):
        cc4_cyborg.step()
        sessions = defaultdict(set)
        for agent, session_dict in sim_controller.state.sessions.items():
            if "red" not in agent:
                continue
            for session in session_dict.values():
                sessions[agent].add(session.hostname)
        passed = any(len(hosts) > 1 for hosts in sessions.values())
        if passed:
            break
    assert passed, "Did not see any instances of a red agent being on multiple hosts after 100 steps!"

def test_red_can_respawn_in_contractor_network(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    While Blue team may succeed in removing all traces of red team from a network, red will always
    respawn in the Contractor Network.

    [한국어]
    챌린지 상세 5문단: Blue 팀(방어 측)이 네트워크에서 Red 팀의 흔적을 모두 제거하더라도,
    Red는 항상 협력업체 네트워크(Contractor Network)에서 다시 생성된다. 이 테스트는 모든
    Red 에이전트를 비활성화한 뒤 100스텝 안에 협력업체 서브넷에서 Red가 재활성화되는지
    확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller

    # Set all red agents to inactive.
    # 모든 Red 에이전트를 비활성 상태로 설정한다.
    agents = sim_controller.agent_interfaces.values()
    for agent in agents:
        if "red" in agent.agent_name:
            agent.active = False
    assert not [agent for agent in agents if "red" in agent.agent_name and agent.active]

    # Assert that a red agent will re-activate in the contractor subnet within 100 steps
    # 100스텝 안에 협력업체 서브넷에서 Red 에이전트가 재활성화됨을 확인한다.
    passed = False
    for _ in range(100):
        cc4_cyborg.step()
        agents = sim_controller.agent_interfaces.values()
        red_agent = next(agent for agent in agents if "red" in agent.agent_name and agent.active)
        if red_agent:
            passed = red_agent.allowed_subnets == ['contractor_network_subnet']
            break
    assert passed

def test_red_agents_select_random_strategies(cc4_cyborg_list: List[CybORG]):
    """
    From Challenge details, paragraph 6:
    The red agents will each use a randomly selected strategy.

    [한국어]
    챌린지 상세 6문단: Red 에이전트는 각자 무작위로 선택된 전략을 사용한다. 이 테스트는
    여러 인스턴스의 Red 행동 시퀀스가 서로 달라지는지(무작위 전략인지) 확인한다.
    """
    action_lists = defaultdict(list)
    for cyborg in cc4_cyborg_list:
        sim_controller: SimulationController = cyborg.environment_controller
        agents = sim_controller.agent_interfaces.values()
        red_agent = next(agent for agent in agents if "red" in agent.agent_name and agent.active)
        index = cc4_cyborg_list.index(cyborg)
        for _ in range(10):
            cyborg.step()
            action_lists[index].append(type(red_agent.last_action))
    unique_action_lists = set(map(tuple, action_lists.values()))

    # will fail as the red agent is sleep agent
    # Red 에이전트가 SleepAgent이면 행동이 고정되므로, 이 경우엔 시퀀스가 하나뿐임을 검증한다.
    if red_agent.agent.__str__()=='SleepAgent':
        assert len(unique_action_lists)== 1
    else:
        assert len(unique_action_lists) > 1

def test_action_durations(cc4_cyborg: CybORG, mocker: MockerFixture):
    """
    From Challenge details, paragraph 7:
    Agent actions now have a specified time duration, which varies depending on the action chosen.
    Agents must wait until their action is completed before they are prompted to launch another
    action. Once an agent has chosen it cannot be cancelled.

    [한국어]
    챌린지 상세 7문단: 이제 에이전트의 행동(Action)에는 지정된 소요 시간이 있으며, 선택한
    행동에 따라 달라진다. 에이전트는 행동이 완료될 때까지 기다려야 다음 행동을 지시받을 수
    있고, 한번 선택한 행동은 취소할 수 없다. 이 테스트는 소요 시간이 2인 행동이 한 스텝
    후에는 실행되지 않고 두 번째 스텝에서 실행되는지 확인한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agents = sim_controller.agent_interfaces.values()
    blue_agent = next(agent for agent in agents if "blue" in agent.agent_name)

    # Create an action with a duration > 1
    # 소요 시간이 1보다 큰 행동을 만든다.
    action = Sleep()
    action.duration = 2
    assert action.duration == 2

    # Assert we're starting with zero calls
    # 아직 한 번도 호출되지 않은 상태에서 시작함을 확인한다.
    spy = mocker.spy(action, "execute")
    assert spy.call_count == 0

    # Since the action has a duration of 2, we would not expect it to execute after one step.
    # 행동의 소요 시간이 2이므로, 한 스텝 후에는 아직 실행되지 않아야 한다.
    cc4_cyborg.step(agent=blue_agent.agent_name, action=action, skip_valid_action_check=True)
    assert spy.call_count == 0

    # Assert the action *is* executed after a second step.
    # 두 번째 스텝 후에는 행동이 실행됨을 확인한다.
    cc4_cyborg.step(skip_valid_action_check=True)
    assert spy.call_count == 1
