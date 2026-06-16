import pytest
import pytest_mock
import networkx as nx

from random import choice as rand_choice

from CybORG import CybORG
from CybORG.Simulator.State import State
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env


def test_GreenAccessService():
    """Test that GreenAccessService Action initialises and executes without exceptions, and the observation returned is successful.

    [한국어]
    GreenAccessService 행동(Action)이 예외 없이 초기화·실행되고, 반환된 관찰값(Observation)이 성공인지 검증한다.
    """

    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent

    action = GreenAccessService(agent=agent.name, session_id=0, src_ip = agent.own_ip, allowed_subnets=agent_interface.allowed_subnets, fp_detection_rate = FP_DETECTION_RATE)
    result_obs = action.execute(state)

    assert result_obs.data['success']


def test_execute_no_host_events():
    """Tests that when GreenAccessService.execute() is run, in a situation when no host events should be created, no host events are created.

    Conditions
        - fp_detection_rate is set to 0.00
        - a new environment is utilised (step = 0) with SleepAgents for all blue and red agents.
        - there are no pre-existing host events

    [한국어]
    호스트 이벤트가 생성되지 않아야 하는 상황에서 GreenAccessService.execute()를 실행하면 호스트 이벤트가 생기지 않는지 검증한다.

    조건
        - fp_detection_rate를 0.00으로 설정한다
        - 모든 Blue·Red 에이전트가 SleepAgent인 새 환경(step = 0)을 사용한다
        - 기존 호스트 이벤트가 없다
    """
    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    # Check there are no pre-existing network_connections events
    # 기존 network_connections 이벤트가 없는지 확인한다
    for host in cyborg.environment_controller.state.hosts.values():
        assert not host.events.network_connections

    # initialise and execute the action
    # 행동(Action)을 초기화하고 실행한다
    action = GreenAccessService(agent=agent.name, session_id=0, src_ip=agent.own_ip,
                                allowed_subnets=agent_interface.allowed_subnets, fp_detection_rate=FP_DETECTION_RATE)

    result_obs = action.execute(state)

    # Check for no newly created network_connections events
    # 새로 생성된 network_connections 이벤트가 없는지 확인한다
    for host in cyborg.environment_controller.state.hosts.values():
        assert not host.events.network_connections

    assert True

@pytest.mark.skip("Links are never removed during episode, so test not necessary")
def test_obs_fail_on_no_route():
    """Tests that when a route is not possible, the observation is unsuccessful.

    Conditions:
        - route is forced go between subnets
        - the internet node is removed so a route between subnets is not possible

    [한국어]
    경로(route)가 불가능할 때 관찰값(Observation)이 실패로 나오는지 검증한다.

    조건:
        - 경로가 서브넷 간 통신이 되도록 강제된다
        - 인터넷 노드를 제거해 서브넷 간 경로가 불가능하게 만든다
    """
    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state 
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    # Take out the internet node so that there is no route between subnets
    # 서브넷 간 경로가 없도록 인터넷 노드를 제거한다
    state.link_diagram.remove_node("root_internet_host_0")

    # initialise and execute the action
    # 행동(Action)을 초기화하고 실행한다
    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )

    same_subnet_flag = True
    while same_subnet_flag:
        result_obs = action.execute(state)

        src_subnet = state.hostname_subnet_map[hostname]
        dest_subnet = state.hostname_subnet_map[state.ip_addresses[action.dest_ip]]

        if not src_subnet == dest_subnet:
            interconnected_subnets = [
                [SUBNET.ADMIN_NETWORK, SUBNET.OFFICE_NETWORK, SUBNET.PUBLIC_ACCESS_ZONE], 
                [SUBNET.OPERATIONAL_ZONE_A, SUBNET.RESTRICTED_ZONE_A],
                [SUBNET.OPERATIONAL_ZONE_B, SUBNET.RESTRICTED_ZONE_B],
                [SUBNET.CONTRACTOR_NETWORK]
            ]
            for grouping in interconnected_subnets:
                if src_subnet in grouping and not dest_subnet in grouping:
                    same_subnet_flag = False
                    break

    assert result_obs.data["success"] == False

def set_action_attributes(state:State, action: GreenAccessService, target_hostname: str):
    action.dest_ip = state.hostname_ip_map[target_hostname]
    service = rand_choice(list(state.hosts[target_hostname].services.keys()))
    action.dest_port = state.hosts[target_hostname].services[service].process

@pytest.mark.skip("Green blocking changed to only functions on (source, destination) blocks, not on routing inbetween. New functionality tested in test_BlueRewardMachine.")
@pytest.mark.parametrize('block_type', ['host', 'subnet'])
def test_execute_host_events_blocked(mocker, block_type):
    """Test that, when locations along the route are blocked, the appropriate network_connections events are added.

    [한국어]
    경로상의 위치가 차단(block)되었을 때 적절한 network_connections 이벤트가 추가되는지 검증한다.
    """

    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state 
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    past_network_connections_events = []
    for _, host in cyborg.environment_controller.state.hosts.items():
        network_connections = host.events.network_connections
        if network_connections:
            past_network_connections_events.append(network_connections)

    # Check there are no pre-existing network_connections events
    # 기존 network_connections 이벤트가 없는지 확인한다
    assert not past_network_connections_events

    # initialise and execute the action
    # 행동(Action)을 초기화하고 실행한다
    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )

    # get new target host
    # 새로운 대상 호스트를 가져온다
    has_services = False
    while not has_services:
        target_hostname = rand_choice(list(state.hosts.keys()))
        if len(state.hosts[target_hostname].services) > 0 and (not state.hostname_subnet_map[target_hostname] == state.hostname_subnet_map[hostname]):
            has_services = True
    target_ip = state.hostname_ip_map[target_hostname]

    # get new route
    # 새로운 경로(route)를 가져온다
    new_route = action.get_route(state=state, target=target_hostname, source=hostname, routing=True)

    # mock the random_reachable_ip_and_port function to insert the new target host and port
    # 새 대상 호스트·포트를 끼워 넣도록 random_reachable_ip_and_port 함수를 목(mock) 처리한다
    mocker.patch( __name__ + '.' + GreenAccessService.__name__ + ".random_reachable_ip", return_value=target_ip)
    # mock the get_used_route function to insert the new route
    # 새 경로를 끼워 넣도록 get_used_route 함수를 목(mock) 처리한다
    mocker.patch( __name__ + '.' + GreenAccessService.__name__ + "._get_my_used_route", return_value=new_route)

    # add a block in the route
    # 경로에 차단(block)을 추가한다
    if block_type == 'host':
        state.blocks[new_route[1]] = [new_route[0]]
    elif block_type == 'subnet':
        state.blocks[state.hostname_subnet_map[new_route[-1]]] = state.hostname_subnet_map[new_route[0]]
    else:
        assert False

    # execute the action with the blocked route
    # 차단된 경로로 행동(Action)을 실행한다
    result_obs = action.execute(state)

    # check action success is FALSE
    # 행동 성공 여부가 FALSE인지 확인한다
    assert result_obs.data['success'] == False

    # Check for newly created network_connections events
    # 새로 생성된 network_connections 이벤트를 확인한다
    new_network_connection_events = []
    for hostname, host in cyborg.environment_controller.state.hosts.items():
        list_network_connections_events = host.events.network_connections
        if len(list_network_connections_events) > 0:
            for event in list_network_connections_events:
                new_network_connection_events.append(event)

    assert len(new_network_connection_events) == 1

    local_addr = new_network_connection_events[0].local_address
    remote_addr = new_network_connection_events[0].remote_address

    if block_type == 'host':
        assert (state.hostname_ip_map[new_route[0]] == local_addr and 
                state.hostname_ip_map[new_route[1]] == remote_addr)
    elif block_type == 'subnet':
        assert (state.hostname_subnet_map[new_route[0]] == state.hostname_subnet_map[state.ip_addresses[local_addr]] and 
                state.hostname_subnet_map[new_route[-1]] == state.hostname_subnet_map[state.ip_addresses[remote_addr]])
    else:
        assert False

def test_execute_host_events_fp():
    """Test that when false positive detection happens, a network_connections event is added to the host.

    When fp_detection_rate is at 1, an event will be added to every host along the route (not src), with the local_address being src.

    [한국어]
    오탐(false positive) 탐지가 발생하면 호스트에 network_connections 이벤트가 추가되는지 검증한다.

    fp_detection_rate가 1이면 경로상의 모든 호스트(src 제외)에 이벤트가 추가되며, local_address는 src가 된다.
    """
    FP_DETECTION_RATE = 1.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state 
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    # Check there are no pre-existing network_connections events
    # 기존 network_connections 이벤트가 없는지 확인한다
    for host in cyborg.environment_controller.state.hosts.values():
        assert not host.events.network_connections

    # initialise and execute the action
    # 행동(Action)을 초기화하고 실행한다
    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )

    result_obs = action.execute(state)

    # Check for newly created network_connections events
    # 새로 생성된 network_connections 이벤트를 확인한다
    new_network_connection_events = []
    for host in cyborg.environment_controller.state.hosts.values():
        new_network_connection_events += host.events.network_connections

    # Check dictionary contents
    # 딕셔너리 내용을 확인한다
    dest_ip_flag = False
    for event in new_network_connection_events:
        assert action.ip_address == event.local_address
        if action.dest_ip == event.remote_address:
            dest_ip_flag = True
    assert dest_ip_flag


def test_random_reachable_ip():
    """Test that function random_reachable_ip_and_port outputs correctly for mission phase.

    Checked properties of output:
        1) dest_ip and dest_port are changed once run on initial state (this may not alway be the case throughout the episode).
        2) dest_ip is not the same as src_ip
        3) dest_ip is not in a subnet that is not reachable for that mission phase, unless in that subnet
        4) destination host is a server

    [한국어]
    random_reachable_ip_and_port 함수가 미션 페이즈(mission phase)에 맞게 올바른 출력을 내는지 검증한다.

    검증하는 출력 속성:
        1) 초기 상태에서 실행하면 dest_ip와 dest_port가 변경된다(에피소드 전체에서 항상 그런 것은 아니다).
        2) dest_ip가 src_ip와 같지 않다
        3) dest_ip가 해당 미션 페이즈에서 도달 불가능한 서브넷에 속하지 않는다(그 서브넷 자신은 예외).
        4) 목적지 호스트가 서버다
    """

    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent

    mission_phase = state.mission_phase
    sg_allowed_subnets = cyborg.environment_controller.scenario_generator._set_allowed_subnets_per_mission_phase()[mission_phase]

    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    
    # vars should be empty initally
    # 변수는 초기에 비어 있어야 한다
    assert action.dest_ip == ""
    assert action.dest_port == ""

    action.dest_ip = action.random_reachable_ip(state=state)

    # vars should be changed once function run
    # 함수가 실행되면 변수가 변경되어야 한다
    assert not action.dest_ip == ""

    # ip should not be the same as itself
    # ip가 자기 자신과 같으면 안 된다
    assert action.dest_ip != agent.own_ip

    # ip should not be in a subnet that is not reachable for that mission phase, unless in that subnet
    # ip는 해당 미션 페이즈에서 도달 불가능한 서브넷에 속하면 안 된다(그 서브넷 자신은 예외)
    dest_hostname = state.ip_addresses[action.dest_ip]
    dest_subnet = state.hostname_subnet_map[dest_hostname]
    src_subnet = state.hostname_subnet_map[state.ip_addresses[action.ip_address]]

    all_subnets = list(state.subnet_name_to_cidr.keys())
    all_subnets.remove(src_subnet)

    if dest_subnet != src_subnet:
        for idx in range(len(sg_allowed_subnets)):
            s1, s2 = sg_allowed_subnets[idx]
            if s1 is src_subnet:
                all_subnets.remove(s2)
            elif s2 is src_subnet:
                all_subnets.remove(s1)

        for subnet in all_subnets:
            assert dest_subnet != subnet

    # host should be a server
    # 호스트는 서버여야 한다
    assert 'server' in dest_hostname


def test_get_used_route():
    """Test for getting the used route between the source and destination hosts.

    First and last host in list checked to be source and destination host.
    The route itself in calculated in function from RemoteAction parent class, therefore not tested directly for truth.

    [한국어]
    출발지·목적지 호스트 사이에 사용된 경로(route)를 가져오는지 검증한다.

    리스트의 첫 호스트와 마지막 호스트가 각각 출발지·목적지 호스트인지 확인한다.
    경로 자체는 RemoteAction 부모 클래스의 함수에서 계산되므로 여기서 직접 검증하지 않는다.
    """

    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent

    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    action.dest_ip = action.random_reachable_ip(state=state)
    used_route = action._get_my_used_route(state)
    assert used_route[0] == state.ip_addresses[action.ip_address]
    assert used_route[-1] == state.ip_addresses[action.dest_ip]