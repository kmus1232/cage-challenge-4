import pytest
import pytest_mock
from ipaddress import IPv4Network, IPv4Address

from CybORG import CybORG
from CybORG.Shared.Enums import SessionType
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.Actions.ConcreteActions.PhishingEmail import PhishingEmail
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env


""" Tests for GreenLocalWork Action and associated (sub-action) PhishingEmail Action.

[한국어]
GreenLocalWork 행동(Action)과 그에 딸린 하위 행동(sub-action)인 PhishingEmail
행동에 대한 테스트.
"""

def test_green_local_work_clear_run():
    """ Test GreenLocalWork Action executes, without false-positive detection and phishing email subaction, successfully with no errors.

    [한국어]
    오탐(false-positive) 탐지와 피싱 이메일 하위 행동 없이 GreenLocalWork 행동이
    오류 없이 정상 실행되는지 테스트한다.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    result_obs = action.execute(state)

    assert result_obs.data['success']

def test_zero_rates_none_occur(mocker):
    """ Test when fp_detection_rate and phishing_error_rate are zero, neither run when GreenLocalWork is executed.

    [한국어]
    fp_detection_rate와 phishing_error_rate가 0일 때 GreenLocalWork 실행 시
    둘 다 발생하지 않는지 테스트한다.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    state = cyborg.environment_controller.state
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    host = cyborg.environment_controller.state.hosts[hostname]
    past_process_creation_host_events = host.events.process_creation

    assert not past_process_creation_host_events

    spy = mocker.spy(PhishingEmail, "execute")

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)
    
    assert spy.call_count == 0

    host = cyborg.environment_controller.state.hosts[hostname]
    new_process_creation_host_events = host.events.process_creation

    assert not new_process_creation_host_events

def test_fp_detection_rate_occurs():
    """ Test when fp_detection_rate = 1.00, fp_detection occurs.

    [한국어]
    fp_detection_rate가 1.00일 때 오탐 탐지(fp_detection)가 발생하는지 테스트한다.
    """

    FP_DETECTION_RATE = 1.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    state = cyborg.environment_controller.state
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    host = cyborg.environment_controller.state.hosts[hostname]
    past_process_creation_host_events = host.events.process_creation

    assert not past_process_creation_host_events

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)

    host = cyborg.environment_controller.state.hosts[hostname]
    new_process_creation_host_events = host.events.process_creation

    assert len(new_process_creation_host_events) == 1
    assert new_process_creation_host_events[0]['local_address'] == agent.own_ip


@pytest.mark.skip("Tests blue monitor functionality, doesn't pick up host.events 100% of the time causing failures")
def test_fp_detection_rate():
    """ Test that when fp_detection occurs, the host appears in the appropriate blue observation spaces.

    fp_detection works by adding a host event to the process_creation.
    Before the end of the step when this action happens, the subAction of the blue_agents (Monitor) occurs.
    Monitor.execute() causes the host.event to be removed and the host is then put into the observation space of a blue agent.
    Only blue agents that have a session on that host will be affected.

    [한국어]
    오탐 탐지(fp_detection)가 발생하면 해당 호스트가 알맞은 Blue 에이전트의
    관찰값(Observation) 공간에 나타나는지 테스트한다.

    fp_detection은 process_creation에 호스트 이벤트를 추가하는 방식으로 동작한다.
    이 행동이 일어난 스텝(step)이 끝나기 전에 Blue 에이전트의 하위 행동인
    Monitor(모니터링)가 실행된다.
    Monitor.execute()는 host.event를 제거하고, 그 호스트를 Blue 에이전트의
    관찰값 공간에 넣는다.
    해당 호스트에 세션을 가진 Blue 에이전트만 영향을 받는다.
    """

    FP_DETECTION_RATE = 1.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )

    cyborg.step(action=action, agent=agent.name)

    hostname_via_ip = cyborg.environment_controller.state.ip_addresses[agent.own_ip]
    host = cyborg.environment_controller.state.hosts[hostname_via_ip]

    # Check that the host checked has the agent as a session
    # 확인 대상 호스트가 해당 에이전트를 세션으로 가지고 있는지 확인한다
    assert host.sessions[agent.name] == [0]

    # Find corresponding blue agent(s)
    # 대응하는 Blue 에이전트를 찾는다
    host_blue_agents = []
    for agent_session, sid in host.sessions.items():
        if 'blue' in agent_session and not sid == []:
            host_blue_agents.append(agent_session)

    # If there are no blue agents with sessions on the host, then no blue agents will see the fp_deception
    # 호스트에 세션을 가진 Blue 에이전트가 없으면, 어떤 Blue 에이전트도 fp_deception을 볼 수 없다
    if not host_blue_agents:
        assert True
        return

    # For each blue agent, check if host in observation space
    # 각 Blue 에이전트별로 호스트가 관찰값 공간에 들어 있는지 확인한다
    for blue_agent in host_blue_agents:
        blue_obs = cyborg.environment_controller.observation[blue_agent]
        for blue_ob in blue_obs.observations:
            if hostname_via_ip in blue_ob.data.keys():
                assert True
                return

    assert False


def test_phishing_error_rate_occur(mocker):
    """ This test checks that, when phishing_error_rate = 1.00, phishing action occurs.

    [한국어]
    phishing_error_rate가 1.00일 때 피싱 행동이 발생하는지 확인하는 테스트다.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00
    
    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state

    spy = mocker.spy(PhishingEmail, "execute")
    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)
    assert spy.call_count == 1


def test_phishing_error_rate_session_creation():
    """ This test checks that when the Phishing Action occurs, a red abstract session is created on that host

    Note: currently agent outside subnet is put as new session agent. May need to be changed to dormant red agent in subnet

    [한국어]
    피싱(Phishing) 행동이 발생하면 해당 호스트에 red abstract 세션이
    생성되는지 확인하는 테스트다.

    참고: 현재는 서브넷 밖의 에이전트가 새 세션 에이전트로 지정된다. 추후
    서브넷 안의 휴면(dormant) Red 에이전트로 바꿔야 할 수 있다.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00
    
    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    hostname = cyborg.environment_controller.state.ip_addresses[agent_interface.agent.own_ip]

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    result_obs = action.execute(state)

    list_of_host_sessions = result_obs.data[hostname]['Sessions']

    check_red_session = False
    for session in list_of_host_sessions:
        if 'red_agent' in session['agent'] and session['Type'] == SessionType.RED_ABSTRACT_SESSION:
            check_red_session = True

    assert check_red_session

def test_failure_on_fully_degraded_services():
    """Tests that the action can fail when the services on the host have no reliability (due to being degraded).

    [한국어]
    호스트의 서비스가 (성능 저하로 인해) 신뢰도(reliability)를 전혀 갖지 못할 때
    행동이 실패할 수 있는지 테스트한다.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    hostname = state.ip_addresses[agent_interface.agent.own_ip]

    # change all service percent reliability to 0
    # 모든 서비스의 신뢰도 비율(percent reliability)을 0으로 바꾼다
    for service in state.hosts[hostname].services.values():
        service._percent_reliable = 0

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    result_obs = action.execute(state)
    assert result_obs.data['success'] == False
