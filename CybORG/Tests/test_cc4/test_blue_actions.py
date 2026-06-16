import pytest

from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Actions import (
    Sleep, DiscoverRemoteSystems, AggressiveServiceDiscovery, StealthServiceDiscovery, PrivilegeEscalate, DegradeServices, Impact, ExploitRemoteService, DiscoverDeception,
    Monitor, Analyse, Restore, Remove, DeployDecoy
)

from .test_blocking_red import cyborg_with_root_shell_on_cns0

red_agent_name = ['red_agent_0', 'red_agent_1']
blue_agent_name = 'blue_agent_0'

target_subnet = 'restricted_zone_a_subnet'
target_host = target_subnet + '_server_host_0'

def test_Monitor(cyborg_with_root_shell_on_cns0):
    """Tests that Monitor (run as a default action for blue agents) detects service discovery attempts when detection_rate = 1.

    [한국어]
    Monitor(Blue 에이전트의 기본 행동(Action)으로 실행됨)가 detection_rate = 1일 때
    서비스 탐색 시도를 탐지하는지 검증한다.
    """

    # Get a cyborg environment with a root shell on contractor_network_subnet_server_0
    # [한국어] contractor_network_subnet_server_0에 root 셸을 가진 CybORG 환경을 가져온다
    cyborg = cyborg_with_root_shell_on_cns0
    env = cyborg.environment_controller
    target_ip = env.state.hostname_ip_map[target_host]

    # Discover a service on restricted_zone_a_subnet_server_host_0
    # [한국어] restricted_zone_a_subnet_server_host_0에서 서비스를 탐색한다
    red_action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
    red_action.detection_rate = 1
    actions = {red_agent_name[0]: red_action}
    observation, _, _, _ = cyborg.parallel_step(actions=actions)
    
    assert target_host in observation[blue_agent_name].keys()

def blue_analyse_host(cyborg:CybORG, blue_agent:str, target_host:str):
    action = Analyse(session=0, agent=blue_agent, hostname=target_host)
    action.duration = 1
    result = cyborg.step(agent=blue_agent, action=action)
    obs = result.observation
    print(obs['action'], obs['success'])
    assert 'Analyse' in str(obs['action'])
    assert obs['success'] == True

    return obs

def test_Analyse(cyborg_with_root_shell_on_cns0):
    """Tests the functionality of the Analyse blue action.

    Checks the analysis observation results after:

    - AggressiveServiceDiscovery (shows nothing)
    - ExploitRemoteService (shows a single cmd.sh file)
    - PrivilegeEscalate (shows a two files: cmd.sh, escalate.sh)

    [한국어]
    Blue의 Analyse(분석) 행동(Action)이 제대로 동작하는지 검증한다.
    다음 각 단계 이후의 분석 관찰값(Observation) 결과를 확인한다.

    - AggressiveServiceDiscovery 이후 (아무것도 보이지 않음)
    - ExploitRemoteService 이후 (cmd.sh 파일 1개가 보임)
    - PrivilegeEscalate 이후 (cmd.sh, escalate.sh 파일 2개가 보임)
     """

    # Get a cyborg environment with a root shell on contractor_network_subnet_server_0
    # [한국어] contractor_network_subnet_server_0에 root 셸을 가진 CybORG 환경을 가져온다
    cyborg = cyborg_with_root_shell_on_cns0
    env = cyborg.environment_controller
    target_ip = env.state.hostname_ip_map[target_host]

    # Discover a service on restricted_zone_a_subnet_server_host_0
    # [한국어] restricted_zone_a_subnet_server_host_0에서 서비스를 탐색한다
    red_action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
    results = cyborg.step(agent=red_agent_name[0], action=red_action)
    obs = results.observation
    assert 'AggressiveServiceDiscovery' in str(obs['action'])
    print(obs['action'], obs['success'])
    assert obs['success'] == True
    
    # Analyse what has happened on that host
    # [한국어] 해당 호스트에서 무슨 일이 일어났는지 분석한다
    obs_visibility = blue_analyse_host(cyborg, blue_agent_name, target_host)
    # Analysis should show nothing ... so far
    # [한국어] 아직까지는 분석에서 아무것도 보이지 않아야 한다
    obs_visibility.pop('action')
    obs_visibility.pop('success')
    assert obs_visibility == {}

    # Red exploits restricted_zone_a_subnet_server_host_0 to gain a user shell
    # [한국어] Red가 restricted_zone_a_subnet_server_host_0을 익스플로잇해 user 셸을 획득한다
    action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
    action.duration = 1
    results = cyborg.step(agent=red_agent_name[0], action=action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert 'Exploit' in str(obs['action'])
    assert obs['success'] == True

    # Analyse what has happened on that host
    # [한국어] 해당 호스트에서 무슨 일이 일어났는지 분석한다
    obs_visibility = blue_analyse_host(cyborg, blue_agent_name, target_host)
    print(obs_visibility)
    # Analysis should show one file
    # [한국어] 분석에서 파일 1개가 보여야 한다
    obs_visibility.pop('action')
    obs_visibility.pop('success')
    assert len(obs_visibility[target_host]['Files']) == 1

    # Red privilege escalates restricted_zone_a_subnet_server_host_0 to gain a user shell
    # [한국어] Red가 restricted_zone_a_subnet_server_host_0에서 권한 상승을 수행한다
    red_action = PrivilegeEscalate(hostname=target_host, session=0, agent=red_agent_name[1])
    red_action.duration = 1
    results = cyborg.step(agent=red_agent_name[1], action=red_action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert 'PrivilegeEscalate' in str(obs['action'])
    assert obs['success'] == True

    # Analyse what has happened on that host
    # [한국어] 해당 호스트에서 무슨 일이 일어났는지 분석한다
    obs_visibility = blue_analyse_host(cyborg, blue_agent_name, target_host)
    print(obs_visibility)
    # Analysis should show two file
    # [한국어] 분석에서 파일 2개가 보여야 한다
    obs_visibility.pop('action')
    obs_visibility.pop('success')
    assert len(obs_visibility[target_host]['Files']) == 2

def get_shell_on_rzas0(cyborg:CybORG, shell_type:str = 'root'):
    # shell_type = user or root
    # [한국어] shell_type은 user 또는 root다. Red가 대상 호스트에 원하는 종류의
    #          셸(user/root)을 확보한 상태의 CybORG 환경을 만들어 반환하는 헬퍼다.

    env = cyborg.environment_controller
    target_ip = env.state.hostname_ip_map[target_host]

    # Discover a service on restricted_zone_a_subnet_server_host_0
    # [한국어] restricted_zone_a_subnet_server_host_0에서 서비스를 탐색한다
    red_action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
    results = cyborg.step(agent=red_agent_name[0], action=red_action)
    obs = results.observation
    assert 'AggressiveServiceDiscovery' in str(obs['action'])
    print(obs['action'], obs['success'])
    assert obs['success'] == True

    # Red exploits restricted_zone_a_subnet_server_host_0 to gain a user shell
    # [한국어] Red가 restricted_zone_a_subnet_server_host_0을 익스플로잇해 user 셸을 획득한다
    action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
    action.duration = 1
    results = cyborg.step(agent=red_agent_name[0], action=action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert 'Exploit' in str(obs['action'])
    assert obs['success'] == True

    if shell_type == 'user':
        return cyborg

    # Red privilege escalates restricted_zone_a_subnet_server_host_0 to gain a user shell
    # [한국어] Red가 restricted_zone_a_subnet_server_host_0에서 권한 상승을 수행한다
    red_action = PrivilegeEscalate(hostname=target_host, session=0, agent=red_agent_name[1])
    red_action.duration = 1
    results = cyborg.step(agent=red_agent_name[1], action=red_action)
    obs = results.observation
    print(obs['action'], obs['success'])
    assert 'PrivilegeEscalate' in str(obs['action'])
    assert obs['success'] == True

    return cyborg

def test_Restore(cyborg_with_root_shell_on_cns0):

    cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0)
    env = cyborg.environment_controller

    blue_action = Restore(session=0, agent=blue_agent_name, hostname=target_host)
    blue_action.duration = 1
    obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})

    assert obs['blue_agent_0']['success'] == True
    assert red_agent_name[1] not in obs.keys()
    assert red_agent_name[1] not in cyborg.active_agents

def test_Remove(cyborg_with_root_shell_on_cns0):
    cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0, shell_type='user')
    env = cyborg.environment_controller

    host_r_sess = [r_agent for r_agent, sess in env.state.hosts[target_host].sessions.items() if 'red' in r_agent and len(sess)>0]
    assert not host_r_sess == []

    blue_action = Remove(session=0, agent=blue_agent_name, hostname=target_host)
    blue_action.duration = 1
    obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})

    assert obs['blue_agent_0']['success'] == True

    host_r_sess = [r_agent for r_agent, sess in env.state.hosts[target_host].sessions.items() if 'red' in r_agent and len(sess)>0]
    assert host_r_sess == []

def test_Remove_fails_on_root_shell(cyborg_with_root_shell_on_cns0):
    cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0, shell_type='root')
    env = cyborg.environment_controller

    host_r_sess = [r_agent for r_agent, sess in env.state.hosts[target_host].sessions.items() if 'red' in r_agent and len(sess)>0]
    assert not host_r_sess == []

    blue_action = Remove(session=0, agent=blue_agent_name, hostname=target_host)
    blue_action.duration = 1
    obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})

    assert obs['blue_agent_0']['success'] == True

    host_r_sess = [r_agent for r_agent, sess in env.state.hosts[target_host].sessions.items() if 'red' in r_agent and len(sess)>0]
    assert not host_r_sess == []

def test_DeployDecoy(cyborg_with_root_shell_on_cns0):

    cyborg = cyborg_with_root_shell_on_cns0
    target_ip = cyborg.environment_controller.state.hostname_ip_map[target_host]

    num_of_services_on_target = len(cyborg.environment_controller.state.hosts[target_host].services)

    action = DeployDecoy(session=0, agent=blue_agent_name, hostname=target_host)
    action.duration = 1
    result = cyborg.step(agent=blue_agent_name, action=action)

    assert result.observation['success']
    assert target_host in result.observation.keys()

    assert len(cyborg.environment_controller.state.hosts[target_host].services) == (num_of_services_on_target + 1)

    action = DiscoverDeception(session=0, agent=red_agent_name[0], ip_address=target_ip)
    action.duration = 1
    result = cyborg.step(agent=red_agent_name[0], action=action)
    pprint(result.observation)
    assert result.observation['action']
    assert 'decoy' in result.observation[target_host]['Processes'][0]['Properties']


def test_DeployDecoy_red_usage(cyborg_with_root_shell_on_cns0):
    """Readme : `When a red agent attempts to compromise a decoy service, blue will be alerted and red’s exploit will automatically fail`

    [한국어]
    README 기준: Red 에이전트가 Decoy(디코이, 미끼) 서비스를 침해하려 시도하면
    Blue에게 경보가 전달되고 Red의 익스플로잇은 자동으로 실패한다.
    """

    cyborg = cyborg_with_root_shell_on_cns0
    shell_ip = cyborg.environment_controller.state.hostname_ip_map['contractor_network_subnet_server_host_3']
    target_ip = cyborg.environment_controller.state.hostname_ip_map[target_host]

    cyborg.environment_controller.state.hosts[target_host].processes = []
    cyborg.environment_controller.state.hosts[target_host].services = {}

    action = DeployDecoy(session=0, agent=blue_agent_name, hostname=target_host)
    action.duration = 1
    obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: action})
    assert obs[blue_agent_name]['success']
    assert len(cyborg.environment_controller.state.hosts[target_host].processes) == 1

    red_action = StealthServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
    red_action.duration = 1
    red_action.detection_rate = 0
    obs, _, _, _ = cyborg.parallel_step(actions={red_agent_name[0]: red_action})
    assert obs[red_agent_name[0]]['success']

    assert obs[blue_agent_name][target_host]['Processes'][0]['Connections'][0]['local_address'] == target_ip
    assert obs[blue_agent_name][target_host]['Processes'][0]['Connections'][0]['remote_address'] == shell_ip

    action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
    action.duration = 1
    obs, _, _, _ = cyborg.parallel_step(actions={red_agent_name[0]: action})

    assert obs[red_agent_name[0]]['success'] == False
    assert obs[blue_agent_name][target_host]['Processes'][0]['Connections'][0]['local_address'] == target_ip
    assert obs[blue_agent_name][target_host]['Processes'][0]['Connections'][0]['remote_address'] == shell_ip