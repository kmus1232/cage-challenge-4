import pytest

from CybORG import CybORG
from CybORG.Shared.Session import Session
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw
from CybORG.Simulator.State import State

def add_sessions(state, agent_name, hostname, user_type, num_sessions=1, min_ident=0):
    """Add num_sessions with a parent session

    [한국어]
    부모 세션 하나를 두고 num_sessions개의 세션을 추가한다.
    """
    for session_int in range(min_ident, num_sessions+min_ident):
        parent = None if session_int == 0 else 0
        state.add_session(Session(
            hostname=hostname, username=user_type, agent=agent_name, parent=parent,
            session_type='shell', ident=session_int, pid=None
        ))

# @pytest.mark.skip
# def test_real_agent():
#     """
#     TBC when non sleep based agents are completed
#         given they can have Withdraw in their action_space
#         and wont require forcing the skip_valid_action_flag==True
#     """
#     pass
# [한국어] (보류 중인 테스트 스텁) SleepAgent가 아닌 실제 에이전트가 완성되면 작성 예정.
#          그 에이전트는 Withdraw를 행동 공간(action space)에 가질 수 있어
#          skip_valid_action_flag==True 강제가 필요 없기 때문이다.

# @pytest.mark.skip
# def test_other_session_creation_actions():
#     """TBC"""
#     pass
# [한국어] (보류 중인 테스트 스텁) 추후 작성 예정(TBC).


@pytest.fixture(scope='module')
def cyborg():
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=124)
    return cyborg


@pytest.mark.parametrize('num_sessions',[1,3,5])
@pytest.mark.parametrize('user_type',['user', 'root', 'SYSTEM'])
@pytest.mark.parametrize('red_agent_str',['red_agent_0', 'red_agent_1'])
def test_Withdraw_num_session(cyborg, num_sessions, user_type, red_agent_str):
    """
    Test that the action Withdraw action will withdraw:
        - a varying number of sessions [1,3,5] from a host
        - irrespective of the user type ['user', 'root', 'SYSTEM'] of that host
        - irrespective of whether they have other sessions or not (deactivating agent if no other sessions) on that host

    [한국어]
    Withdraw(철수) 행동(Action)이 다음 조건에서 세션을 철수시키는지 검증한다.
        - 한 호스트에서 세션 개수가 [1,3,5]로 달라져도
        - 해당 호스트의 사용자 유형 ['user', 'root', 'SYSTEM']과 무관하게
        - 그 호스트에 다른 세션이 있든 없든 무관하게(다른 세션이 없으면 에이전트를 비활성화)
    """
    env = cyborg.environment_controller
    env.reset()

    session_id=0
    agent = env.agent_interfaces[red_agent_str]
    
    # if agent has sessions then
    # 에이전트가 세션을 가지고 있으면
    if env.state.sessions_count[red_agent_str]>0:
        local_hostname = env.state.sessions[red_agent_str][0].hostname
        # randomly select a host from the available hosts the agent can access on the subnet that isn't its own hostname
        # 에이전트가 서브넷에서 접근 가능한 호스트 중 자기 자신이 아닌 호스트를 임의로 하나 고른다
        target_hostname = [host for host in env.state.hosts if env.agent_interfaces[red_agent_str].allowed_subnets[0] in host if host!= local_hostname][0]
    else:
        # randomly select a host from the available hosts the agent can access on the subnet
        # 에이전트가 서브넷에서 접근 가능한 호스트 중 하나를 임의로 고른다
        target_hostname = [host for host in env.state.hosts if env.agent_interfaces[red_agent_str].allowed_subnets[0] in host][0]
        local_hostname = target_hostname
    
    own_ip = env.hostname_ip_map[local_hostname]

    obs = cyborg.get_observation(red_agent_str)
    action_space = cyborg.get_action_space(red_agent_str)

    for i in range(30):
        # check the red_agent_1 starts inactive
        # red_agent_1이 비활성 상태로 시작하는지 확인한다
        if i==0:
            if red_agent_str=='red_agent_0':
                assert env.agent_interfaces[red_agent_str].active==True
                assert env.is_active(red_agent_str)==True
                assert env.state.sessions_count[red_agent_str]>0
            elif red_agent_str=='red_agent_1':
                assert env.agent_interfaces[red_agent_str].active==False
                assert env.is_active(red_agent_str)==False 
                assert env.state.sessions_count[red_agent_str]==0

        action = agent.get_action(obs, action_space)
        # add 1 session for red_agent_0
        # red_agent_0에 세션을 추가한다
        if i==5:
            if red_agent_str=='red_agent_0':
                min_ident=1
                add_sessions(env.state, red_agent_str, target_hostname, user_type=user_type, num_sessions=num_sessions, min_ident=min_ident); 
            elif red_agent_str=='red_agent_1':
                min_ident=0
                add_sessions(env.state, red_agent_str, target_hostname, user_type=user_type, num_sessions=num_sessions, min_ident=min_ident); 
        # withdraw and delete all sessions from red_agent_1
        # Withdraw(철수)로 red_agent_1의 모든 세션을 철수·삭제한다
        if i==15: action = Withdraw(session=session_id, agent=red_agent_str, ip_address=own_ip, hostname=target_hostname)
        # skip action check as Withdaw isn't in the red SleepAgent's valid action space
        # Withdraw가 Red SleepAgent의 유효 행동 공간(action space)에 없으므로 행동 검사를 건너뛴다
        results = cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
        # check that after the action and step method, red_agent_1 is now active given the new session
        # 행동과 step 실행 후, 새 세션이 생겨 red_agent_1이 활성화됐는지 확인한다
        if i==5:
            assert env.agent_interfaces[red_agent_str].active==True
            assert env.is_active(red_agent_str)==True
            assert env.state.sessions_count[red_agent_str]==num_sessions + min_ident
                
        if i==15:
            assert str(cyborg.get_last_action(red_agent_str)[0]) == f"Withdraw {target_hostname}"
            # check that after the Withdraw action, red_agent_0 remains active
            # Withdraw 행동 후에도 red_agent_0이 계속 활성 상태인지 확인한다
            if red_agent_str=='red_agent_0':
                assert env.agent_interfaces[red_agent_str].active==True
                assert env.is_active(red_agent_str)==True
                assert env.state.sessions_count[red_agent_str]>0
            # check that after the Withdraw action, red_agent_1 is no longer active
            # Withdraw 행동 후 red_agent_1이 더 이상 활성 상태가 아닌지 확인한다
            elif red_agent_str=='red_agent_1':
                assert env.agent_interfaces[red_agent_str].active==False 
                assert env.is_active(red_agent_str)==False 
                assert env.state.sessions_count[red_agent_str]==0
                
        obs = results.observation
        action_space = results.action_space



def test_Withdraw_on_only_host(cyborg):
    """
    Test that the action Withdraw action will withdraw from the only session
        it has active rendering itself inactive.

    [한국어]
    Withdraw(철수) 행동(Action)이 유일하게 활성 상태인 세션에서 철수해,
        에이전트 자신을 비활성 상태로 만드는지 검증한다.
    """
    env = cyborg.environment_controller
    env.reset()
    red_agent_str='red_agent_0'
    session_id=0
    agent = env.agent_interfaces[red_agent_str]
    
    # get the host of the only session red_agent_0 has
    # red_agent_0이 가진 유일한 세션의 호스트를 가져온다
    hostname = [int.hostname for int in env.state.sessions[red_agent_str].values() if int.ident==0][0]

    own_ip = env.hostname_ip_map[hostname]
    obs = cyborg.get_observation(red_agent_str)
    action_space = cyborg.get_action_space(red_agent_str)

    for i in range(30):
        # check the red_agent_0 starts active
        # red_agent_0이 활성 상태로 시작하는지 확인한다
        if i==0:
            assert env.agent_interfaces[red_agent_str].active==True
            assert env.is_active(red_agent_str)==True
            assert env.state.sessions_count[red_agent_str]==1

        action = agent.get_action(obs, action_space)
        # withdraw and delete all sessions from red_agent_1
        # Withdraw(철수)로 red_agent_1의 모든 세션을 철수·삭제한다
        if i==10: action = Withdraw(session=session_id, agent=red_agent_str, ip_address=own_ip, hostname=hostname)
        # skip action check as Withdaw isn't in the red SleepAgent's valid action space
        # Withdraw가 Red SleepAgent의 유효 행동 공간(action space)에 없으므로 행동 검사를 건너뛴다
        results = cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
        # check that after the Withdraw action, red_agent_1 is no longer active
        # Withdraw 행동 후 red_agent_1이 더 이상 활성 상태가 아닌지 확인한다
        if i==10:
            assert str(cyborg.get_last_action(red_agent_str)[0]) == f"Withdraw {hostname}"
            assert env.agent_interfaces[red_agent_str].active==False 
            assert env.is_active(red_agent_str)==False 
            assert env.state.sessions_count[red_agent_str]==0

        obs = results.observation
        action_space = results.action_space

    # check that all red agents are now inactive with no sessions
    # 모든 Red 에이전트가 이제 세션 없이 비활성 상태인지 확인한다
    for red_agent_str in env.team_assignments['Red']:
        assert env.agent_interfaces[red_agent_str].active==False 
        assert env.is_active(red_agent_str)==False


def test_scenario_reset(cyborg):
    """Test the initial set up for red agent activation

    [한국어]
    Red 에이전트 활성화에 대한 초기 설정을 검증한다.
    """
    env = cyborg.environment_controller
    env.reset()
    
    assert len(env.state.sessions['red_agent_0'].keys())==1 \
        and env.agent_interfaces['red_agent_0'].active==True \
        and env.is_active('red_agent_0') == True \
        and env.has_active_non_parent_sessions('red_agent_0')==False
    
    assert len(env.state.sessions['red_agent_1'].keys())==0 \
        and env.agent_interfaces['red_agent_1'].active==False \
        and env.is_active('red_agent_1') == False \
        and env.has_active_non_parent_sessions('red_agent_1')==False
    
