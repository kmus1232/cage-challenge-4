from ipaddress import IPv4Address
import random
from typing import List, Tuple
import pytest
from CybORG.Agents.Wrappers.BlueEnterpriseWrapper import BlueEnterpriseWrapper
from CybORG.Shared.AgentInterface import AgentInterface
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Simulator.Actions.ConcreteActions.ExploitActions import SSHBruteForce
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG

@pytest.mark.skip('Test unfinished.')
def test_phases_have_communication_policy():
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Each mission phase has an associated communication policy governing how zones are intended to
    connect to one another.

    [한국어]
    네트워크 연결·통신 정책 문서 1문단 기준:
    각 미션 단계(mission phase)에는 보안 영역(zone)들이 서로 어떻게 연결되어야 하는지를
    규정하는 통신 정책이 연결되어 있다.
    """

@pytest.mark.skip('Test unfinished.')
def test_policies_implemented_automatically():
    """
    From Network Connectivity and Communication policy, paragraph 1:
    When the mission phase changes the intended policy is implemented automatically, overwriting
    the current configuration if necessary.

    [한국어]
    네트워크 연결·통신 정책 문서 1문단 기준:
    미션 단계가 바뀌면 의도된 정책이 자동으로 적용되며, 필요하면 현재 설정을 덮어쓴다.
    """

@pytest.mark.skip('Test unfinished.')
def test_only_associated_connections_are_changed():
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Only connections associated with the given mission are changed (for example, when mission 2A is
    activated, only connections with Restricted Zone A and Operational Zone A are affected).

    [한국어]
    네트워크 연결·통신 정책 문서 1문단 기준:
    해당 미션과 연관된 연결만 변경된다 (예: 미션 2A가 활성화되면 Restricted Zone A와
    Operational Zone A에 관련된 연결만 영향을 받는다).
    """


def test_intended_and_firewall_state_communicated_to_blue_agents(cc4_blue_wrapper: BlueEnterpriseWrapper):
    """
    From Network Connectivity and Communication policy, paragraph 1:
    The intended policy and actual firewall state is also communicated to blue agents in their
    observation vector.

    [한국어]
    네트워크 연결·통신 정책 문서 1문단 기준:
    의도된 정책과 실제 방화벽 상태는 Blue 에이전트의 관찰값(observation) 벡터에도 전달된다.
    """
    NUM_SUBNETS = len(SUBNET)
    CURRENT_MISSION_INDEX = 0
    START_INDEX = CURRENT_MISSION_INDEX + 1
    BLOCKED_SUBNETS_SLICE = slice(START_INDEX,START_INDEX + NUM_SUBNETS)
    COMMS_POLICY_SLICE = slice(BLOCKED_SUBNETS_SLICE.stop, BLOCKED_SUBNETS_SLICE.stop + NUM_SUBNETS)
    
    results, _ = cc4_blue_wrapper.reset()
    for agent, value in results.items():
        comms_block = value[COMMS_POLICY_SLICE]
        assert comms_block is not None, f"agent '{agent}' does not have a comms block!"

def test_blue_agents_can_open_and_close_firewalls(cc4_cyborg: CybORG):
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Blue agents can open and close firewalls between their zone and other networks, for example to
    prevent infections from red agents, but may incur penalties if their changes prevent green
    agents from accomplishing their own goals. Firewalls are present in each zone, so connections
    must be open in both zones for a green agent to communicate between them.

    [한국어]
    네트워크 연결·통신 정책 문서 1문단 기준:
    Blue 에이전트는 자신의 영역(zone)과 다른 네트워크 사이의 방화벽을 열고 닫을 수 있다.
    예를 들어 Red 에이전트의 감염을 막기 위해 사용하지만, 그 변경이 Green 에이전트의 목표
    달성을 방해하면 페널티를 받을 수 있다. 방화벽은 각 영역마다 존재하므로, Green 에이전트가
    두 영역 사이에서 통신하려면 양쪽 영역 모두에서 연결이 열려 있어야 한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    from_subnet = "contractor_network_subnet"
    to_subnet = 'operational_zone_b_subnet'
    red_agent_interface, red_session = get_agent(sim_controller, from_subnet, "red")
    red_agent = red_agent_interface.agent_name
    blue_agent_interface, blue_session = get_agent(sim_controller, to_subnet, "blue")
    blue_agent = blue_agent_interface.agent_name

    # Attempt SSHBruteForce from User0 to Enterprise0.
    # User0에서 Enterprise0로 SSHBruteForce(SSH 무차별 대입 공격)를 시도한다.
    # Not blocked -> should succeed.
    # 차단되지 않은 상태 -> 성공해야 한다.
    ip_address = IPv4Address(sim_controller.hostname_ip_map[blue_session.hostname])
    actions = { red_agent: SSHBruteForce(session=0, agent=red_agent, ip_address=ip_address) }
    obs, rew, done, info = cc4_cyborg.parallel_step(actions, skip_valid_action_check=True)
    assert obs[red_agent]['success'] == True

    # Block User Zone -> Enterprise Zone traffic
    # User Zone -> Enterprise Zone 트래픽을 차단한다.
    # This is a simultaneous block action and exploit action ->
    # Block and Exploit will both return success == True
    # 차단 행동(Block)과 익스플로잇 행동이 동시에 일어나므로,
    # Block과 Exploit 둘 다 success == True를 반환한다.
    ip_address = IPv4Address(sim_controller.hostname_ip_map[blue_session.hostname])
    actions = {
        red_agent: SSHBruteForce(session=0, agent=red_agent, ip_address=ip_address),
        blue_agent: BlockTrafficZone(
            session=0, agent=blue_agent, from_subnet=from_subnet, to_subnet=to_subnet
        )
    }
    obs, rew, done, info = cc4_cyborg.parallel_step(actions, skip_valid_action_check = True)
    assert obs[red_agent]['success'] == True
    assert obs[blue_agent]['success'] == True

    # Attempt SSHBruteForce from User0 to Enterprise0.
    # User0에서 Enterprise0로 SSHBruteForce를 시도한다.
    # Blocked -> should fail.
    # 차단된 상태 -> 실패해야 한다.
    action = SSHBruteForce(session=0, agent=red_agent, ip_address=ip_address)
    obs, rew, done, info = cc4_cyborg.parallel_step({red_agent: action}, skip_valid_action_check = True)
    assert obs[red_agent]['success'] == False

@pytest.mark.skip('Blue wrapper test')
def test_8_bit_messages(cc4_blue_wrapper: BlueEnterpriseWrapper):
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Some blue agents may communicate with each other regardless of firewall policy via 8-bit
    messages.

    [한국어]
    네트워크 연결·통신 정책 문서 1문단 기준:
    일부 Blue 에이전트는 방화벽 정책과 무관하게 8비트 메시지를 통해 서로 통신할 수 있다.
    """

@pytest.mark.skip('Test unfinished.')
def test_defender_inter_agent_communication(cc4_blue_wrapper: BlueEnterpriseWrapper):
    """
    From Network Connectivity and Communication policy, paragraph 2:
    Some defending agents have the capability to communicate 8-bit messages with each other.
    Specifically, the Headquarters agent can communicate with everybody, agents in Restricted zones
    can communicate with their corresponding operational zone, but the two agents in the
    operational zone cannot communicate with anybody. Figure 2 shows how information can flow only
    into Operational Zone A, but never out. See Table 1 for the complete (initial) network
    communication security policy for the mission pre-planning phase.

    [한국어]
    네트워크 연결·통신 정책 문서 2문단 기준:
    일부 방어 에이전트는 서로 8비트 메시지를 주고받을 수 있다. 구체적으로, 본부(HQ)
    에이전트는 모두와 통신할 수 있고, Restricted 영역의 에이전트는 자신에 대응하는
    operational 영역과 통신할 수 있지만, operational 영역의 두 에이전트는 누구와도 통신할 수
    없다. Figure 2는 정보가 Operational Zone A로 들어갈 수만 있고 절대 나올 수 없음을
    보여준다. 미션 사전 계획 단계의 완전한 (초기) 네트워크 통신 보안 정책은 Table 1을 참고한다.
    """

def get_agent(sim_controller: SimulationController, subnet: str, team: str) -> Tuple[AgentInterface, Session]:
    """
    This method chooses a random agent of a given team that is found in the subnet provided.

    [한국어]
    주어진 서브넷(subnet) 안에 있는 특정 팀(team)의 에이전트 하나를 무작위로 고른다.
    """
    valid_sessions: List[Session] = []
    for agent, sessions in sim_controller.state.sessions.items():
        if team in agent:
            for session in sessions.values():
                if subnet in session.hostname:
                    valid_sessions.append(session)
    assert valid_sessions, f"Could not find valid agent within subnet {subnet}"
    session = random.choice(valid_sessions)
    agent_interface = sim_controller.agent_interfaces[session.agent]
    return agent_interface, session
