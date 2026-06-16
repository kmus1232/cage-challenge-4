import pytest
from CybORG.Simulator.Actions.ConcreteActions.PhishingEmail import PhishingEmail
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG

def test_green_agents_on_every_host(cc4_cyborg: CybORG):
    """
    From Green agents, paragraph 1:
    Users are represented by green agents, which are present on every host.

    [한국어]
    Green 에이전트 문서 1문단:
    사용자는 Green 에이전트(정상 사용자)로 표현되며, 모든 호스트에 존재한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    hosts = set()
    sessions = sim_controller.state.sessions
    user_hosts = [host for host in sim_controller.state.hosts if "user" in host]
    green_session_sets = [value for key, value in sessions.items() if "green" in key]
    for green_session_set in green_session_sets:
        for green_session in green_session_set.values():
            hosts.add(green_session.hostname)
    assert len(hosts) == len(user_hosts)

def test_green_agents_do_local_work(cc4_cyborg: CybORG):
    """
    From Green agents, paragraph 1:
    Green agents randomly do local work or attempt to reach out to external services, either in
    their local or a remote zone. The service and zone a green agent chooses will be determined
    randomly, but are restricted to valid connections for the current mission phase as governed by
    the communication policy tables below.

    [한국어]
    Green 에이전트 문서 1문단:
    Green 에이전트는 로컬 작업을 하거나, 로컬/원격 보안 영역(security zone)의 외부 서비스에
    접속을 시도하는 것을 무작위로 수행한다. 어떤 서비스와 영역을 고를지는 무작위로 정해지되,
    아래 통신정책표(communication policy tables)가 규정하는 현재 미션 단계의 유효한 연결로만
    제한된다.
    """
    actions = set()
    for _ in range(10):
        cc4_cyborg.step()
        agents = cc4_cyborg.environment_controller.agent_interfaces
        for agent in agents.values():
            if "green" in agent.agent_name:
                actions.add(type(agent.last_action))
    for action in [GreenAccessService, GreenLocalWork]:
        assert action in actions, f"Green agents don't seem to have {action} available to them!"

def test_false_alerts(cc4_cyborg: CybORG):
    """
    From Green agents, paragraph 3:
    Green agents occasionally generate false alerts while going about their work by exhibiting
    behavior similar to a red agent, such as transferring data between hosts.

    [한국어]
    Green 에이전트 문서 3문단:
    Green 에이전트는 작업을 하는 도중, 호스트 간 데이터 전송처럼 Red 에이전트(공격 측)와 비슷한
    행동을 보여 가끔 거짓 경보(false alert)를 발생시킨다.
    """
    FP_DETECTION_RATE = 1.00
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    
    # get green agent
    # Green 에이전트를 가져온다
    agents = sim_controller.agent_interfaces.items()
    agent_interface = next((agent for agent_name, agent in agents if 'green' in agent_name), None)

    # Check there are no pre-existing network_connections events
    # 기존에 network_connections 이벤트가 없는지 확인한다
    for host in sim_controller.state.hosts.values():
        assert not host.events.network_connections

    # initialise and execute the action
    # 행동(Action)을 생성하고 실행한다
    action = GreenAccessService(
        agent=agent_interface.agent.name,
        session_id=0,
        src_ip=agent_interface.agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    action.execute(sim_controller.state)

    # Check for newly created network_connections events
    # 새로 생성된 network_connections 이벤트를 확인한다
    new_network_connection_events = []
    for host in sim_controller.state.hosts.values():
        new_network_connection_events += host.events.network_connections

    # Check dictionary contents
    # 딕셔너리 내용을 확인한다
    dest_ip_flag = False
    for event in new_network_connection_events:
        assert action.ip_address == event.local_address
        if action.dest_ip == event.remote_address:
            dest_ip_flag = True
    assert dest_ip_flag

def test_phishing_attacks(cc4_cyborg: CybORG, mocker):
    """
    From Green agents, paragraph 3:
    They also sometimes introduce red agents into the network via succumbing to phishing attacks,
    installing unapproved software, and general poor security hygiene.

    [한국어]
    Green 에이전트 문서 3문단:
    또한 Green 에이전트는 피싱 공격에 당하거나, 미승인 소프트웨어를 설치하거나, 전반적으로
    보안 위생이 나쁜 탓에 때때로 Red 에이전트(공격 측)를 네트워크에 끌어들이기도 한다.
    """
    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    spy = mocker.spy(PhishingEmail, "execute")
    
    # get green agent
    # Green 에이전트를 가져온다
    agents = sim_controller.agent_interfaces.items()
    agent_interface = next((agent for agent_name, agent in agents if 'green' in agent_name), None)

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE
    )
    action.execute(sim_controller.state)
    assert spy.call_count == 1
