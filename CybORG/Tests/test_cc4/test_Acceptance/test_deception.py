from typing import Type
import pytest
import pytest_mock
from CybORG.Shared.Enums import ProcessName
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions.AbstractActions.DegradeServices import DegradeServices
from CybORG.Simulator.Actions.AbstractActions.DiscoverDeception import DiscoverDeception
from CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices import AggressiveServiceDiscovery
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoyAction, DeployDecoy
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
# Decoys below are unavailable in CC4 given they require a windows machine and the scenario is only creating linux machines.
# 아래 Decoy(디코이)들은 windows 머신을 요구하는데 시나리오가 linux 머신만 생성하므로 CC4에서는 사용 불가하다.
#from CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions import DecoyApache_cc4, DecoyHarakaSMPT_cc4, DecoyTomcat_cc4, DecoyVsftpd_cc4
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyApache import ApacheDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.Simulator.State import State
from CybORG.env import CybORG

def test_agents_can_create_decoy_services(cc4_cyborg: CybORG):
    """
    From Deception, paragraph 1:
    Both blue and red agents may employ deception to further their goals. Blue agents can stand up
    decoy services in any host or server. Decoy services resemble normal ones, but cannot replace
    or be instantiated along with existing services (they can use the Discover Network Services
    action to determine which services are already running on a given host).

    [한국어]
    Deception 1번 문단 발췌:
    Blue·Red 에이전트 모두 목표 달성을 위해 기만(deception)을 활용할 수 있다. Blue
    에이전트는 임의의 호스트나 서버에 Decoy(디코이, 미끼) 서비스를 띄울 수 있다.
    Decoy 서비스는 정상 서비스처럼 보이지만, 기존 서비스를 대체하거나 함께 띄울 수는
    없다(어떤 서비스가 이미 호스트에서 돌고 있는지는 Discover Network Services
    (네트워크 서비스 탐색) 행동(Action)으로 확인할 수 있다).
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agents = sim_controller.agent_interfaces.items()
    blue_agent = next(agent for agent_name, agent in agents if 'blue' in agent_name)
    blue_actions = blue_agent.action_space.actions.keys()

    assert DeployDecoy in blue_actions

    # Check that the red and blue agents have the decoy actions available to them.
    # Red·Blue 에이전트가 Decoy(디코이) 행동을 행동 공간(Action Space)에 갖고 있는지 확인한다.
    # decoy_actions = {DecoyApache_cc4, DecoyHarakaSMPT_cc4, DecoyTomcat_cc4, DecoyVsftpd_cc4}
    # for decoy_action in decoy_actions:
    #     assert decoy_action in blue_actions, f"Blue agent is missing decoy action '{decoy_action}' from its action space!"

def test_red_decoys_alert_blue_agents(cc4_cyborg: CybORG):
    """
    From Deception, paragraph 1:
    When a red agent attempts to compromise a decoy service, blue will be alerted and can then see
    any further actions taken by red agents originating from that host.

    [한국어]
    Deception 1번 문단 발췌:
    Red 에이전트가 Decoy(디코이) 서비스를 침해하려 시도하면 Blue 측에 경보가 뜨고,
    이후 해당 호스트에서 출발하는 Red 에이전트의 모든 행동(Action)을 볼 수 있게 된다.
    """
    decoy_type = DeployDecoy
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    required_port = next(iter(decoy_type.CANDIDATE_DECOYS)).PORT
    blue_agents_sessions_hosts = [
        (agent, session, sim_controller.state.hosts[session.hostname])
        for agent, sessions in sim_controller.state.sessions.items()
        if "blue" in agent
        for session in sessions.values()
    ]
    # Filter out options where the host is already using the required port
    # 호스트가 이미 해당 포트를 쓰고 있는 경우는 후보에서 제외한다.
    selected_agent, selected_session, selected_host = next(
        (agent, session, host)
        for agent, session, host in blue_agents_sessions_hosts
        if not host.is_using_port(required_port)
    )
    blue_agent = sim_controller.agent_interfaces[selected_agent]
    action = decoy_type(
        agent=blue_agent.agent_name,
        session=selected_session.ident,
        hostname=selected_host.hostname
    )

    obs = action.execute(sim_controller.state)
    assert obs.success == True, "Decoy was not successfully set-up on host!"

    # Get green agent on that host to spawn a red agent via phishing attack.
    # 해당 호스트의 Green 에이전트를 가져와, 피싱 공격으로 Red 에이전트를 생성하게 한다.
    green_agent_name, green_sessions = next(
        ((agent, sessions) for agent, sessions in selected_host.sessions.items() if "green" in agent and sessions),
        (None, None)
    )
    green_agent = sim_controller.agent_interfaces[green_agent_name]
    action = GreenLocalWork(
        agent=green_agent_name,
        session_id=green_sessions[0],
        ip_address=green_agent.agent.own_ip,
        fp_detection_rate=0.00,
        phishing_error_rate=1.00,
    )
    action.execute(sim_controller.state)

    # Get the new red agent that's on the green host.
    # Green 호스트에 새로 생긴 Red 에이전트를 가져온다.
    red_sessions = []
    for agent, sessions in selected_host.sessions.items():
        if sessions and "red" in agent:
            red_sessions.append((agent, sessions))
    assert red_sessions, "Could not find red session on host!"

    # Now the red agent needs to perform an action against the decoy service.
    # 이제 Red 에이전트가 Decoy(디코이) 서비스를 상대로 행동(Action)을 수행해야 한다.



@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_red_agents_can_discover_deception(cc4_cyborg: CybORG, decoy_fp_rate):
    """
    From Deception, paragraph 1:
    Red agents can use the DiscoverDeception action to determine if they are interacting with decoy
    services.

    [한국어]
    Deception 1번 문단 발췌:
    Red 에이전트는 DiscoverDeception 행동(Action)으로 자신이 Decoy(디코이) 서비스와
    상호작용하고 있는지 판별할 수 있다.
    """
    RED_AGENT='red_agent_0'
    SESSION_ID=0
    env: SimulationController = cc4_cyborg.environment_controller
    
    # get the hostname for the blue_agent session
    # blue_agent 세션에 해당하는 호스트명을 가져온다.
    hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname

    # ensure the Apache service isn't running initially
    # 초기에 Apache 서비스가 돌고 있지 않도록 보장한다.
    while ProcessName.APACHE2 in env.state.hosts[hostname].services.keys():
        env.reset()
        hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname

    # this action is only successful if the service doesnt already exist on the host \
    # which is true for the current seed set in the environment (1)
    # 이 행동(Action)은 호스트에 해당 서비스가 아직 없을 때만 성공하며, 환경에 설정된
    # 현재 시드(1)에서는 그 조건이 참이다.
    action = DeployDecoy(agent=RED_AGENT, session=SESSION_ID, hostname=hostname)
    action.CANDIDATE_DECOYS = [ApacheDecoyFactory()]
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    # Decoy(디코이)가 호스트에 추가됐는지 확인한다.
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='apache2'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    # 대상 호스트를 식별하고, 탐지율(detection_rate) 100%로 Decoy(디코이)를 탐지한다.
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    # ensure the action was a success and that the rfi properties exist from the decoy
    # 행동(Action)이 성공했고 Decoy(디코이)에서 비롯된 rfi 속성이 존재하는지 보장한다.
    assert obs.data['success']==True
    apache_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='apache2']
    assert "decoy" in apache_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    # 탐지된 Decoy(디코이)에서 위음성(false negative)을 점검한다 - detection_rate 100%로 모두
    # 탐지되지만, 그중 어느 것도 'decoy' 속성을 갖지 않아야 한다.
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='apache2']
    if decoy_fp_rate==0:
        assert len(non_decoys)==0
    elif decoy_fp_rate==1:
        assert len(non_decoys)>0

def add_sessions(state: State, agent_name, hostname, user_type, num_sessions=1):
    """Add num_sessions with a parent session

    [한국어]
    부모 세션(Session)을 둔 채로 num_sessions개의 세션을 추가한다.
    """
    for session_int in range(0, num_sessions):
        parent = None if session_int == 0 else 0
        state.add_session(Session(
            hostname=hostname, username=user_type, agent=agent_name, parent=parent,
            session_type='shell', ident=None, pid=None
        ))

@pytest.mark.parametrize('update_phishing_email_rate',[0, 0.01, 0.25, 1])
@pytest.mark.parametrize('num_sessions',[1,3,5])
@pytest.mark.parametrize('user_type',['user', 'root', 'SYSTEM'])
@pytest.mark.parametrize('red_agent_str',['red_agent_0', 'red_agent_1'])
def test_red_agents_can_withdraw(cc4_cyborg: CybORG, num_sessions, user_type, red_agent_str, update_phishing_email_rate):
    """
    From Deception, paragraph 1:
    Red agents can use their Withdraw action to remove their presence.

    [한국어]
    Deception 1번 문단 발췌:
    Red 에이전트는 Withdraw(철수) 행동(Action)으로 자신의 존재(흔적)를 제거할 수 있다.
    """
    env: SimulationController = cc4_cyborg.environment_controller
    
    # test variations of the phising_email_rate to spawn greater numbers of red agents
    # 더 많은 Red 에이전트를 생성하도록 phising_email_rate 값을 여러 가지로 바꿔 테스트한다.
    for agent_name, agent in env.agent_interfaces.items():
        if 'green' in agent_name: agent.agent.phishing_error_rate = update_phishing_email_rate

    session_id=0
    agent = env.agent_interfaces[red_agent_str]
    
    # if agent has sessions then
    # 에이전트가 세션(Session)을 가진 경우
    if env.state.sessions_count[red_agent_str]>0:
        local_hostname = env.state.sessions[red_agent_str][0].hostname
        # randomly select a host from the available hosts the agent can access on the subnet that isn't its own hostname
        # 에이전트가 서브넷에서 접근 가능한 호스트 중, 자기 자신이 아닌 호스트를 임의로 하나 고른다.
        target_hostname = [host for host in env.state.hosts if env.agent_interfaces[red_agent_str].allowed_subnets[0] in host if host!= local_hostname and 'router' not in host][0]
    else:
        # randomly select a host from the available hosts the agent can access on the subnet
        # 에이전트가 서브넷에서 접근 가능한 호스트 중 하나를 임의로 고른다.
        target_hostname = [host for host in env.state.hosts if env.agent_interfaces[red_agent_str].allowed_subnets[0] in host if 'router' not in host][0]
        local_hostname = target_hostname
    
    own_ip = env.hostname_ip_map[local_hostname]

    obs = cc4_cyborg.get_observation(red_agent_str)
    action_space = cc4_cyborg.get_action_space(red_agent_str)
    
    phishing_email_increment_red = 0
    num_withdrawing=0
    original_session_count = 1 if red_agent_str=='red_agent_0' else 0

    for i in range(30):
        # check the red_agent_1 starts inactive
        # red_agent_1이 비활성(inactive) 상태로 시작하는지 확인한다.
        if i==0:
            if red_agent_str=='red_agent_0':
                assert env.agent_interfaces[red_agent_str].active==True
                assert env.is_active(red_agent_str)==True
                assert env.state.sessions_count[red_agent_str]>0
            elif red_agent_str=='red_agent_1':
                assert env.agent_interfaces[red_agent_str].active==False
                assert env.is_active(red_agent_str)==False 
                assert env.state.sessions_count[red_agent_str]== phishing_email_increment_red

        action = agent.get_action(obs, action_space)
        # add 1 session for red_agent_0
        # red_agent_0에 세션(Session)을 추가한다.
        if i==5:
            add_sessions(env.state, red_agent_str, target_hostname, user_type=user_type, num_sessions=num_sessions)
        # withdraw and delete all sessions from red_agent_1
        # red_agent_1을 Withdraw(철수)시키고 그 모든 세션(Session)을 삭제한다.
        if i==15:
            action = Withdraw(
                session=session_id,
                agent=red_agent_str,
                ip_address=own_ip,
                hostname=target_hostname
            )
            num_withdrawing = len([s for s in env.state.sessions[red_agent_str].values() if s.hostname == target_hostname])
        red_agent_active = env.agent_interfaces[red_agent_str].active
        # skip action check as Withdaw isn't in the red SleepAgent's valid action space
        # Withdraw(철수)는 Red SleepAgent의 유효 행동 공간(Action Space)에 없으므로 행동 검사를 건너뛴다.
        results = cc4_cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
        red_allowed_subnets_map = { agent_name : agent.allowed_subnets for agent_name, agent in env.agent_interfaces.items() if 'red' in agent_name}

        for agent_name, agent in env.agent_interfaces.items():
            if 'green' in agent_name:
                if env.get_last_action(agent_name)[0].__str__().split(' ')[0]=='GreenLocalWork':
                    obs_ph = env.get_last_observation(agent_name)
                    hostname = [k for k in obs_ph.data.keys() if k not in ['success', 'action']]
                    if len(hostname)>0:
                        ## if there is a phishing email in a subnet with an initially inactive red agent
                        ## then the session is reassigned to the red agent to activate it
                        ## 처음에 비활성이던 Red 에이전트가 있는 서브넷에 피싱 이메일이 발생하면,
                        ## 그 세션(Session)이 해당 Red 에이전트에 재할당되어 에이전트가 활성화된다.
                        subnet = env.state.hostname_subnet_map[hostname[0]].value
                        for red_agent_name, subnets in red_allowed_subnets_map.items():
                            if subnet in subnets and red_agent_name==red_agent_str:
                                if red_agent_active==False:
                                    phishing_email_increment_red += 1
                        ## if the agent is already active then the appropriate agent is captured in the greens oberservation
                        ## 에이전트가 이미 활성 상태라면, 해당 에이전트는 Green의 관찰값(Observation)에 잡힌다.
                        red_agent = obs_ph.data[hostname[0]]['Sessions'][0]['agent']
                        if red_agent==red_agent_str and red_agent_active and subnet in red_allowed_subnets_map[red_agent_str]:
                            phishing_email_increment_red += 1
        
        # check that after the action and step method, red_agent_1 is now active given the new session
        # 행동(Action)과 step 실행 후, 새 세션(Session) 덕분에 red_agent_1이 활성 상태가 됐는지 확인한다.
        if i==5:
            assert env.agent_interfaces[red_agent_str].active==True
            assert env.is_active(red_agent_str)==True
            assert env.state.sessions_count[red_agent_str]== (num_sessions + phishing_email_increment_red + original_session_count)
        if i==15:
            assert str(cc4_cyborg.get_last_action(red_agent_str)[0]) == f"Withdraw {target_hostname}"
            # check that after the Withdraw action, red_agent_0 remains active
            # Withdraw(철수) 행동(Action) 후에도 red_agent_0이 계속 활성 상태인지 확인한다.
            if red_agent_str=='red_agent_0':
                assert env.agent_interfaces[red_agent_str].active==True 
                assert env.is_active(red_agent_str)==True
                assert env.state.sessions_count[red_agent_str]>0
            # check that after the Withdraw action, red_agent_1 is no longer active
            # Withdraw(철수) 행동(Action) 후 red_agent_1이 더 이상 활성 상태가 아닌지 확인한다.
            elif red_agent_str=='red_agent_1':
                if (phishing_email_increment_red + num_sessions - num_withdrawing) > 0:
                    assert env.agent_interfaces[red_agent_str].active==True 
                    assert env.is_active(red_agent_str)==True
                    assert env.state.sessions_count[red_agent_str]>0
                else:
                    assert env.agent_interfaces[red_agent_str].active==False 
                    assert env.is_active(red_agent_str)==False 
                    assert env.state.sessions_count[red_agent_str] == (phishing_email_increment_red + num_sessions - num_withdrawing)
        obs = results.observation
        action_space = results.action_space


# @pytest.mark.skip('Test unfinished.')
def test_red_agents_can_use_aggressive_service_discovery(cc4_cyborg: CybORG, mocker: pytest_mock.MockerFixture):
    """
    From Deception paragraph 2:
    For their part, red agents can generate extra alerts for blue defenders using the Aggressive
    Service Discovery action on a selected host. This action is faster than the Service Discovery
    action but has a higher probability of generating an alert, so it may also be used simply to
    trade off speed over stealth.

    [한국어]
    Deception 2번 문단 발췌:
    Red 에이전트 측에서는, 선택한 호스트에 Aggressive Service Discovery(공격적 서비스
    탐색) 행동(Action)을 써서 Blue 방어자에게 추가 경보를 일으킬 수 있다. 이 행동은
    일반 Service Discovery(서비스 탐색)보다 빠르지만 경보 발생 확률이 더 높아, 은밀함을
    포기하고 속도를 택하는 트레이드오프 용도로도 쓸 수 있다.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agent  = 'red_agent_0'
    target_ip = cc4_cyborg.get_ip_map()["restricted_zone_a_subnet_user_host_0"]
    session = 0
    action = AggressiveServiceDiscovery(ip_address=target_ip, agent=agent, session=session)
    
    # For the purposes of testing
    # 테스트 목적으로 설정한다.
    action.detection_rate = 1
    assert target_ip not in sim_controller.state.sessions[agent][session].ports
    action.execute(sim_controller.state)
    assert target_ip in sim_controller.state.sessions[agent][session].ports

@pytest.mark.skip('Requirement demonstrated in other tests')
def test_red_agents_can_use_degrade():
    """
    From Deception paragraph 2:
    In addition, red agents with elevated privileges can use the Degrade action to cause green
    agent actions on the target host to fail much more frequently.

    Shown in tests:

    - Tests/test_cc4/test_Red/test_DegradeServices.py
    - Tests/test_cc4/test_Green/test_GreenLocalWork.py::test_failure_on_fully_degraded_services()

    [한국어]
    Deception 2번 문단 발췌:
    또한, 권한이 상승된 Red 에이전트는 Degrade(서비스 성능 저하) 행동(Action)으로 대상
    호스트의 Green 에이전트 행동이 훨씬 더 자주 실패하게 만들 수 있다.

    아래 테스트에서 확인된다:

    - Tests/test_cc4/test_Red/test_DegradeServices.py
    - Tests/test_cc4/test_Green/test_GreenLocalWork.py::test_failure_on_fully_degraded_services()
    """
    pass
    # env: SimulationController = cc4_cyborg.environment_controller

    # red_agent_str = 'red_agent_0'
    # session = env.state.sessions[red_agent_str][0]
    # hostname = env.state.sessions['red_agent_0'][0].hostname
    # agent = env.agent_interfaces[red_agent_str]

    # obs = cc4_cyborg.get_observation(red_agent_str)
    # action_space = cc4_cyborg.get_action_space(red_agent_str)

    # for i in range(30):
    #     # base action for each step - Sleep unless overwritten
    #     action = agent.get_action(obs, action_space)

    #     # on step 1, set the action to be Degrade - this will fail
    #     if i == 1:
    #         action = DegradeServices(hostname=hostname, session=session.ident, agent=red_agent_str)
    #     # add a root shell session on the host that is controlled by the red agent
    #     if i == 5:
    #         session = Session(
    #             hostname=hostname, username=user_type, agent=red_agent_str, parent=session.ident,
    #             session_type='shell', ident=None, pid=None
    #         )
    #         env.state.add_session(session)
    #     # on step 10, set the action to be Degrade - this should pass
    #     if i == 10:
    #         action = DegradeServices(hostname=hostname, session=session.ident, agent=red_agent_str)

    #     # env step and get results
    #     results = cc4_cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
    #     obs = results.observation

    #     # assert statements on results
    #     if i == 1:
    #         action_details = env.get_last_action(red_agent_str)[0].__str__().split(' ')
    #         assert action_details[0] == 'DegradeServices'
    #         assert action_details[1] == hostname
    #         assert obs['success'] != True
    #         assert len([(pro.name) for pro in list(env.state.hosts[hostname].processes) if pro.name == ProcessName.SSHD]) == 1
    #         assert env.state.hosts[hostname].services[ProcessName.SSHD].active is True
    #     if i == 10:
    #         action_details = env.get_last_action(red_agent_str)[0].__str__().split(' ')
    #         assert action_details[0] == 'DegradeServices'
    #         assert action_details[1] == hostname
    #         # the action should fail is the new session is not root/system level
    #         if user_type == 'user':
    #             assert obs['success'] == False
    #             assert env.state.hosts[hostname].services[ProcessName.SSHD].active is True
    #         else:
    #             assert obs['success'] == True
    #             services = env.state.hosts[hostname].services
    #             inactive_services = [name for name, service in services.items() if not service.active]
    #             assert obs[hostname]['Processes'][0]['process_name'] in inactive_services
