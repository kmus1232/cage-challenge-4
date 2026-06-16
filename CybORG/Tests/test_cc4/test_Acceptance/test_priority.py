from typing import List, Tuple
import random
import pytest

from pytest_mock import MockerFixture
from CybORG.Shared import Observation
from CybORG.Shared.AgentInterface import AgentInterface
from CybORG.Simulator.Actions.AbstractActions import Impact
from CybORG.Shared.Session import RedAbstractSession, Session
from CybORG.Simulator.Actions.GreenActions import GreenLocalWork
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Service import Service
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Shared.Enums import ProcessName
from CybORG.Tests.test_cc4.test_BlueRewardMachine import test_Score_GreenLocalWork
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent

def test_phase_progression(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 8:
    During the course of an episode, the mission shall progress linearly through three different
    phases Phase 1, Phase 2A and Phase 2B.

    [한국어]
    Challenge details 문단 8 기준:
    한 에피소드 진행 동안 미션은 Phase 1, Phase 2A, Phase 2B 세 단계를 순서대로 거쳐야 한다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller

    # CybORG가 Phase 1로 시작하는지 확인한다.
    assert sim_controller.state.mission_phase == 0, "CybORG does not start in Phase 1!"

    for _ in range(100):
        cc4_cyborg.step()
        is_phase_2a = sim_controller.state.mission_phase == 1
        if is_phase_2a:
            break
    assert is_phase_2a, "CybORG does not progress to Phase 2A"

    for _ in range(100):
        cc4_cyborg.step()
        is_phase_2b = sim_controller.state.mission_phase == 2
        if is_phase_2b:
            break
    assert is_phase_2b, "CybORG does not progress to Phase 2B"

# The tests below test the following from Challenge details, paragraph 8:
# During Phase 1 all missions operating in each zone have the same low priority level. During Phase
# 2A only missions operating in zones within Deployed Network A have the same high priority level,
# while all other missions have the same low priority level. During Phase 2B only missions operating
# in Deployed Network B have the same high priority level, while all other missions have the same
# low priority level.
# [한국어] 아래 테스트들은 Challenge details 문단 8을 검증한다.
# Phase 1에서는 각 zone에서 동작하는 모든 미션이 동일한 낮은 우선순위를 가진다. Phase 2A에서는
# 배치 네트워크(deployed network) A 내 zone에서 동작하는 미션만 동일한 높은 우선순위를 가지고,
# 나머지 미션은 모두 동일한 낮은 우선순위를 가진다. Phase 2B에서는 배치 네트워크 B에서 동작하는
# 미션만 동일한 높은 우선순위를 가지고, 나머지는 모두 동일한 낮은 우선순위를 가진다.

# From Green agents, paragraph 2:
# Rewards are tied to these green agent actions. The blue team receives penalties when a green agent
# is unable to work, either because it cannot make a valid connection to service, or its host is
# unavailable (for example if it is currently being restored by a blue agent). Penalties are also
# awarded to blue when a red agent has compromised a host where a green agent is working, or green
# agents access services on compromised hosts. Green agents in mission-critical zones generate
# higher penalties when their mission is active.
# [한국어] Green agents 문단 2 기준:
# 보상은 이 Green 에이전트의 행동(Action)에 연동된다. Green 에이전트가 작업을 수행하지 못할 때
# (서비스에 유효한 연결을 맺지 못하거나, 호스트가 사용 불가일 때 — 예: Blue 에이전트가 해당 호스트를
# 복원(Restore) 중) Blue 팀은 페널티를 받는다. 또한 Red 에이전트가 Green 에이전트가 작업 중인
# 호스트를 침해했거나, Green 에이전트가 침해된 호스트의 서비스에 접근할 때도 Blue에 페널티가 부여된다.
# 미션 핵심(mission-critical) zone의 Green 에이전트는 미션이 활성 상태일 때 더 큰 페널티를 발생시킨다.

# From Rewards, paragraph 1:
# Blue agents start with 0 points and are assigned penalties when green agents are unable to
# perform their work, when they access a compromised service, and when red chooses the Impact
# action. Penalties change during active missions to reflect the changing criticality of hosts on
# current operations. All rewards for are shown in Table 4.
# [한국어] Rewards 문단 1 기준:
# Blue 에이전트는 0점에서 시작하며, Green 에이전트가 작업을 수행하지 못할 때, 침해된 서비스에
# 접근할 때, Red가 Impact(타격) 행동을 선택할 때 페널티가 부여된다. 페널티는 활성 미션 동안
# 현재 작전에서 호스트의 중요도가 변하는 것을 반영해 달라진다. 모든 보상은 Table 4에 나와 있다.

zones = [
    {"public_access_zone_subnet", "admin_network_subnet", "office_network_subnet"},
    {"contractor_network_subnet"},
    {"restricted_zone_a_subnet"},
    {"operational_zone_a_subnet"},
    {"restricted_zone_b_subnet"},
    {"operational_zone_b_subnet"},
    # {"internet_subnet"}
]

@pytest.mark.parametrize('green_subnet', 
    ['admin_network_subnet',
    'contractor_network_subnet',
    'office_network_subnet',
    'operational_zone_a_subnet',
    'operational_zone_b_subnet',
    'public_access_zone_subnet',
    'restricted_zone_a_subnet',
    'restricted_zone_b_subnet'])
@pytest.mark.parametrize('mission_phase', [0,1,2])
def test_priority_local_work_failure(green_subnet, mission_phase):
    """
    Testing the rewards from the GreenLocalWork action for all phases and relevant security zones.

    - Duplicates test from BlueRewardMachine.py

    [한국어]
    모든 phase와 관련 보안 영역(security zone)에 대해 GreenLocalWork 행동(Action)의 보상을 검증한다.

    - BlueRewardMachine.py의 테스트를 그대로 가져온 것이다.
    """
    test_Score_GreenLocalWork(green_subnet, mission_phase)
    

@pytest.mark.parametrize('phase', range(3))
@pytest.mark.parametrize('zone_phase_reward', [
    (zones[0], (-1, -1, -1)),
    (zones[1], (-5, 0, 0)),
    (zones[2], (-3, -1, -3)),
    (zones[3], (-1, 0, -1)),
    (zones[4], (-3, -1, -1)),
    (zones[5], (-1, -1, 0)),
    # (zones[6], (0, 0, 0))
])
def test_access_service_failure(enterprise_cyborg_min_steps: CybORG, zone_phase_reward: tuple, phase: int, mocker: MockerFixture):
    """
    Testing the rewards from the GreenAccessService action for all phases and relevant security
    zones.

    [한국어]
    모든 phase와 관련 보안 영역(security zone)에 대해 GreenAccessService 행동(Action)의 보상을 검증한다.
    """
    zone = zone_phase_reward[0]
    reward = zone_phase_reward[1][phase]
    sim_controller: SimulationController = enterprise_cyborg_min_steps.environment_controller

    # Get cyborg to the required mission phase.
    # CybORG를 요구되는 미션 phase까지 진행시킨다.
    while sim_controller.state.mission_phase != phase:
        enterprise_cyborg_min_steps.step()

    # Get an appropriate agent to perform the action upon.
    # 행동을 수행할 적절한 에이전트를 가져온다.
    session, agent_interface = get_agent(zone, sim_controller)
    ip_address = sim_controller.hostname_ip_map[session.hostname]

    # Create action
    # 행동(Action)을 생성한다.
    action = GreenAccessService(
        agent=agent_interface.agent_name,
        session_id=0,
        src_ip=ip_address,
        fp_detection_rate=0.00,
        allowed_subnets=agent_interface.allowed_subnets
    )

    # Tamper with action to ensure failure
    # 실패를 강제하기 위해 행동을 조작한다.
    mock = mocker.patch.object(action, "execute")
    mock.return_value = Observation(success=False)

    # Execute action and test reward
    # 행동을 실행하고 보상을 검증한다.
    result = enterprise_cyborg_min_steps.step(agent=agent_interface.agent_name, action=action)
    assert mock.called == 1, "Action was not called or mock did not take effect!"
    assert result.observation["success"] == False, "Action didn't fail!"
    print(result.reward)
    print(sim_controller.reward['Blue']['BlueRewardMachine'])
    #assert result.reward == reward, f"Expected a reward of '{reward}', but got '{result.reward}'!"
    assert sim_controller.reward['Blue']['BlueRewardMachine'] == reward, f"Expected a reward of '{reward}', but got '{sim_controller.reward['Blue']['BlueRewardMachine']}'!"


@pytest.mark.parametrize('operational_subnet', ["operational_zone_a_subnet", "operational_zone_b_subnet"])
@pytest.mark.parametrize('phase', range(3))
def test_red_impact_access(operational_subnet, phase):
    """
    Testing the rewards from the Impact action for all phases and relevant security zones. This
    test requires getting a red agent on a host in a particular security zone, which is
    accomplished by a GreenLocalWork with a 100% phishing error chance.

    [한국어]
    모든 phase와 관련 보안 영역(security zone)에 대해 Impact(타격) 행동(Action)의 보상을 검증한다.
    이 테스트는 특정 보안 영역의 호스트에 Red 에이전트를 올려놓아야 하는데, 이는 피싱 오류 확률
    100%인 GreenLocalWork로 달성한다.
    """

    brm = BlueRewardMachine(agent_name='blue_agent')

    ent_sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        red_agent_class=SleepAgent,
        green_agent_class=SleepAgent,
    )
    cyborg = CybORG(scenario_generator=ent_sg)
    cyborg.reset()
    env = cyborg.environment_controller

    red_allowed_subnets = {interface.allowed_subnets[0]: agent for agent, interface in env.agent_interfaces.items() if 'red' in agent}

    env.state.mission_phase = phase
    i = 0
    server_host = operational_subnet + "_server_host_" + str(i)
    while server_host in env.state.hosts.keys():
        assert env.state.hosts[server_host].services[ProcessName.OTSERVICE]
        
        # add red session
        # Red 세션을 추가한다.
        red_agent = red_allowed_subnets[operational_subnet]
        session = RedAbstractSession(
            hostname=server_host, username='root', agent=red_agent, parent=None,
            session_type='RedAbstractSession', ident=None, pid=None
        )
        env.state.add_session(session)
        env.agent_interfaces[red_agent].active = True
        env.agent_interfaces[red_agent].action_space.server_session[0] = True
        env.agent_interfaces[red_agent].action_space.client_session[0] = True
        env.agent_interfaces[red_agent].action_space.hostname[server_host] = True

        # impact host
        # 호스트에 Impact(타격)를 가한다.
        action = Impact(server_host, 0, red_agent)
        action.duration = 1
        actions = {red_agent: action}
        obs, rewards, _, _ = cyborg.parallel_step(actions=actions)
        
        # get results
        # 결과를 가져온다.
        assert obs[red_agent]['action']

        received_reward = rewards['blue_agent_0']['BlueRewardMachine']
        expected_reward = brm.get_phase_rewards(phase)[operational_subnet]['RIA']

        assert expected_reward == received_reward

        # end of while loop
        # while 루프 끝 — 다음 server_host로 넘어간다.
        i += 1
        server_host = operational_subnet + "_server_host_" + str(i)

def get_agent(zone: set, sim_controller: SimulationController) -> Tuple[Session, AgentInterface]:
    """
    This method chooses a random green agent that is found in the security zone provided.

    Parameters
    ----------
    zone : set
        A set of the subnets the agent can come from.
    sim_controller : SimulationController
        The simulation controller that contains the relevant data.

    Returns
    -------
    Tuple[Session, AgentInterface]
        The session and interface for the chosen agent.

    [한국어]
    주어진 보안 영역(security zone) 안에 있는 Green 에이전트 하나를 무작위로 고른다.

    매개변수
    ----------
    zone : set
        에이전트가 속할 수 있는 서브넷들의 집합.
    sim_controller : SimulationController
        관련 데이터를 담고 있는 시뮬레이션 컨트롤러.

    반환값
    -------
    Tuple[Session, AgentInterface]
        선택된 에이전트의 세션과 인터페이스.
    """
    valid_sessions: List[Session] = []
    for agent, sessions in sim_controller.state.sessions.items():
        if "green" in agent:
            for session in sessions.values():
                if any(subnet in session.hostname for subnet in zone):
                    valid_sessions.append(session)
    assert valid_sessions, f"Could not find valid agent within zone {zone}"
    session = random.choice(valid_sessions)
    agent_interface = sim_controller.agent_interfaces[session.agent]
    return session, agent_interface
