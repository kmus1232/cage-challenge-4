import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, Sleep, PrivilegeEscalate, DegradeServices, Impact, Monitor, ExploitRemoteService
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork

from CybORG.Shared.Enums import ProcessName
from CybORG.Simulator.Process import Process
from CybORG.Shared.Session import Session

from CybORG.Shared.Session import VelociraptorServer, RedAbstractSession

"""
Testing that the AggressiveServiceDiscovery, StealthServiceDiscovery, and ExploitRemoteService are not successful
when blue blocks traffic (BlockTrafficZone) between the source and target ips.

[한국어]
Blue 에이전트가 출발지·목적지 IP 사이의 트래픽을 차단(BlockTrafficZone)했을 때
Red 에이전트의 AggressiveServiceDiscovery, StealthServiceDiscovery,
ExploitRemoteService 행동(Action)이 성공하지 못함을 검증하는 테스트다.
"""

RED_AGENT_NAME = 'red_agent_0'
BLUE_AGENT_NAME = 'blue_agent_0'

@pytest.fixture()
def cyborg_with_root_shell_on_cns0() -> CybORG:
    """Get red_agent_0 a root shell on 'contractor_network_subnet_server_host_0' 
    
    Observation gained from last PrivilegeEscalate:
        'public_access_zone_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.176.254')}]},
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}]},
        'restricted_zone_b_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.100.254')}]},

    Returns
    -------
    cyborg : CybORG
        a cyborg environment with a root shell on cns0

    [한국어]
    Red 에이전트(red_agent_0)가 'contractor_network_subnet_server_host_0'(cns0)에
    root 셸을 확보한 상태의 CybORG 환경을 만들어 반환하는 pytest fixture다.
    원격 시스템 탐색 -> 네트워크 서비스 탐색 -> 익스플로잇(원격 서비스 공격) ->
    권한 상승 순서로 행동(Action)을 실행해 셸을 얻는다.
    위 Observation 예시는 마지막 PrivilegeEscalate(권한 상승)에서 얻은 관찰값이다.

    Returns(반환값)
    -------
    cyborg : CybORG
        cns0에 root 셸이 확보된 CybORG 환경
    """
    ent_sg = EnterpriseScenarioGenerator(
            blue_agent_class=SleepAgent,
            red_agent_class=SleepAgent,
            green_agent_class=SleepAgent,
            steps=100
        )
    cyborg = CybORG(scenario_generator=ent_sg, seed=100)
    cyborg.reset()
    env = cyborg.environment_controller

    s0_hostname = 'contractor_network_subnet_server_host_0'
    s0_ip_addr = env.state.hostname_ip_map[s0_hostname]
    cn_subnet_ip = env.subnet_cidr_map[env.state.hostname_subnet_map[s0_hostname]]

    action = DiscoverRemoteSystems(subnet=cn_subnet_ip, session=0, agent=RED_AGENT_NAME)
    action.duration = 1
    results = cyborg.step(agent=RED_AGENT_NAME, action=action)
    obs = results.observation
    print(obs['action'], obs['success'])

    action = AggressiveServiceDiscovery(session=0, agent=RED_AGENT_NAME, ip_address=s0_ip_addr)
    action.duration = 1
    results = cyborg.step(agent=RED_AGENT_NAME, action=action)
    obs = results.observation
    print(obs['action'], obs['success'])

    action = ExploitRemoteService(ip_address=s0_ip_addr, session=0, agent=RED_AGENT_NAME)
    action.duration = 1
    results = cyborg.step(agent=RED_AGENT_NAME, action=action)
    obs = results.observation
    print(obs['action'], obs['success'])

    action = PrivilegeEscalate(hostname=s0_hostname, session=0, agent=RED_AGENT_NAME)
    action.duration = 1
    results = cyborg.step(agent=RED_AGENT_NAME, action=action)
    obs = results.observation
    print(obs['action'], obs['success'])

    return cyborg

@pytest.mark.parametrize('target_subnet', [
        'public_access_zone_subnet', 
        'restricted_zone_a_subnet',
        'restricted_zone_b_subnet'])
def test_block_effective_against_AggressiveServiceDiscovery(cyborg_with_root_shell_on_cns0, target_subnet):
    cyborg = cyborg_with_root_shell_on_cns0
    env = cyborg.environment_controller

    blue_action = BlockTrafficZone(session=0, agent=BLUE_AGENT_NAME, from_subnet='contractor_network_subnet', to_subnet=target_subnet)
    results = cyborg.step(agent=BLUE_AGENT_NAME, action=blue_action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert obs['success']

    target_host = target_subnet + '_server_host_0'
    target_ip = env.state.hostname_ip_map[target_host]

    red_action = AggressiveServiceDiscovery(session=0, agent=RED_AGENT_NAME, ip_address=target_ip)
    results = cyborg.step(agent=RED_AGENT_NAME, action=red_action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert not 'InvalidAction' in str(obs['action']), 'AggressiveServiceDiscovery is returning InvalidAction'
    assert obs['success'] == False


@pytest.mark.parametrize('target_subnet', [
        'public_access_zone_subnet', 
        'restricted_zone_a_subnet',
        'restricted_zone_b_subnet'])
def test_block_effective_against_Exploit(cyborg_with_root_shell_on_cns0, target_subnet):
    cyborg = cyborg_with_root_shell_on_cns0
    env = cyborg.environment_controller

    target_host = target_subnet + '_server_host_0'
    target_ip = env.state.hostname_ip_map[target_host]

    red_action = AggressiveServiceDiscovery(session=0, agent=RED_AGENT_NAME, ip_address=target_ip)
    results = cyborg.step(agent=RED_AGENT_NAME, action=red_action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert not 'InvalidAction' in str(obs['action']), 'AggressiveServiceDiscovery is returning InvalidAction'
    assert obs['success'] == True

    blue_action = BlockTrafficZone(session=0, agent=BLUE_AGENT_NAME, from_subnet='contractor_network_subnet', to_subnet=target_subnet)
    results = cyborg.step(agent=BLUE_AGENT_NAME, action=blue_action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert obs['success']

    action = ExploitRemoteService(ip_address=target_ip, session=0, agent=RED_AGENT_NAME)
    action.duration = 1
    results = cyborg.step(agent=RED_AGENT_NAME, action=action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert not 'InvalidAction' in str(obs['action']), 'ExploitRemoteService is returning InvalidAction'
    assert obs['success'] == False
