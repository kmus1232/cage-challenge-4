import pytest

from CybORG import CybORG
from CybORG.Shared.Enums import ProcessName
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.AbstractActions.DiscoverDeception import DiscoverDeception
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoyHarakaSMPT, DecoyApache, DecoyTomcat, DecoyVsftpd
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoySmss, DecoyFemitter, DecoySSHD, DecoySvchost

RED_AGENT='red_agent_0'
SESSION_ID=0

# @pytest.mark.skip
# def test_real_agent():
#     """
#     TBC when non sleep based agents are completed
#         given they can have Withdraw in their action_space
#         and wont require forcing the skip_valid_action_flag==True
#
#     [한국어]
#     SleepAgent가 아닌 실제 에이전트가 완성되면 작성 예정(TBC).
#     실제 에이전트는 action_space에 Withdraw(철수)를 가질 수 있고,
#     skip_valid_action_flag==True를 강제할 필요가 없기 때문이다.
#     """
#     pass

@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_DecoyApache(decoy_fp_rate):
    """
    Test we can discover an Apache2 decoy

    [한국어]
    Apache2 Decoy(디코이, 미끼)를 탐지할 수 있는지 검증한다.
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    red_agent_str='red_agent_0'
    
    # get the hostname for the blue_agent session
    # 해당 세션이 올라가 있는 호스트명을 가져온다
    hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host
    # 이 행동(Action)은 해당 서비스가 호스트에 아직 없을 때만 성공한다
    while ProcessName.APACHE2 in env.state.hosts[hostname].services.keys():
        env.reset()
        hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname

    action = DecoyApache(agent=red_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    # Decoy(디코이)가 호스트에 추가되었는지 확인한다
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='apache2'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    # 대상 호스트를 지정하고, 탐지율(detection_rate) 100%로 Decoy(디코이)를 탐지한다
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    # ensure the action was a success and that the rfi properties exist from the decoy
    assert obs.data['success']==True
    apache_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='apache2']
    assert "decoy" in apache_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    # 탐지된 Decoy(디코이)의 false negative(거짓 음성) 점검 - detection_rate 100%라 전부 탐지되지만, 'decoy' 속성을 갖지 않는다
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='apache2']
    if decoy_fp_rate==0:
        assert len(non_decoys)==0
    elif decoy_fp_rate==1:
        assert len(non_decoys)>0


@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_HarakaSMPT(decoy_fp_rate):
    """
    Test we can discover an HarakaSMPT decoy

    [한국어]
    HarakaSMPT Decoy(디코이, 미끼)를 탐지할 수 있는지 검증한다.
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    
    blue_agent_str='blue_agent_0'
    
    # get the hostname for the blue_agent session
    # 해당 세션이 올라가 있는 호스트명을 가져온다
    hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host
    # 이 행동(Action)은 해당 서비스가 호스트에 아직 없을 때만 성공한다
    while ProcessName.SMTP in env.state.hosts[hostname].services.keys():
        env.reset()
        hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    action = DecoyHarakaSMPT(agent=blue_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    # Decoy(디코이)가 호스트에 추가되었는지 확인한다
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='haraka'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    # 대상 호스트를 지정하고, 탐지율(detection_rate) 100%로 Decoy(디코이)를 탐지한다
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    
    # ensure the action was a success
    # 행동(Action)이 성공했는지 확인한다
    assert obs.data['success']==True
    haraka_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='haraka']
    assert "decoy" in haraka_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    # 탐지된 Decoy(디코이)의 false negative(거짓 음성) 점검 - detection_rate 100%라 전부 탐지되지만, 'decoy' 속성을 갖지 않는다
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='haraka']
    non_decoy_list = ["decoy"  in process['Properties'] for process in non_decoys]
    if decoy_fp_rate==0:
        assert len(non_decoy_list)==0
    elif decoy_fp_rate==1:
        assert len(non_decoy_list)>0


@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_DecoyTomcat(decoy_fp_rate):
    """
    Test we can discover an Tomcat decoy

    [한국어]
    Tomcat Decoy(디코이, 미끼)를 탐지할 수 있는지 검증한다.
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    blue_agent_str='blue_agent_0'

    # get the hostname for the blue_agent session
    # 해당 세션이 올라가 있는 호스트명을 가져온다
    hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host \
    # which is true for the current seed set in the environment (1)
    # 이 행동(Action)은 해당 서비스가 호스트에 아직 없을 때만 성공하며, \
    # 환경에 설정된 현재 seed(1)에서는 그 조건이 충족된다
    action = DecoyTomcat(agent=blue_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    # Decoy(디코이)가 호스트에 추가되었는지 확인한다
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='Tomcat.exe'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    # 대상 호스트를 지정하고, 탐지율(detection_rate) 100%로 Decoy(디코이)를 탐지한다
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    
    # ensure the action was a success
    # 행동(Action)이 성공했는지 확인한다
    assert obs.data['success']==True
    tomcat_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='Tomcat.exe']
    assert "decoy" in tomcat_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    # 탐지된 Decoy(디코이)의 false negative(거짓 음성) 점검 - detection_rate 100%라 전부 탐지되지만, 'decoy' 속성을 갖지 않는다
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='Tomcat.exe']
    non_decoy_list = ["decoy" in process['Properties'] for process in non_decoys]
    if decoy_fp_rate==0:
        assert len(non_decoy_list)==0
    elif decoy_fp_rate==1:
        assert len(non_decoy_list)>0


@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_DecoyVsftpd(decoy_fp_rate):
    """
    Test we can discover an Vsftpd decoy

    [한국어]
    Vsftpd Decoy(디코이, 미끼)를 탐지할 수 있는지 검증한다.
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    blue_agent_str='blue_agent_0'

    # get the hostname for the blue_agent session
    # 해당 세션이 올라가 있는 호스트명을 가져온다
    hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host \
    # which is true for the current seed set in the environment (1)
    # 이 행동(Action)은 해당 서비스가 호스트에 아직 없을 때만 성공하며, \
    # 환경에 설정된 현재 seed(1)에서는 그 조건이 충족된다
    action = DecoyVsftpd(agent=blue_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    # Decoy(디코이)가 호스트에 추가되었는지 확인한다
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='vsftpd'
    print(decoy_list)
    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    # 대상 호스트를 지정하고, 탐지율(detection_rate) 100%로 Decoy(디코이)를 탐지한다
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    # ensure the action was a success
    # 행동(Action)이 성공했는지 확인한다
    assert obs.data['success']==True
    vsftpd_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='vsftpd']
    assert "decoy" in vsftpd_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    # 탐지된 Decoy(디코이)의 false negative(거짓 음성) 점검 - detection_rate 100%라 전부 탐지되지만, 'decoy' 속성을 갖지 않는다
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='vsftpd']
    non_decoy_list = ["decoy" in process['Properties'] for process in non_decoys]
    if decoy_fp_rate==0:
        assert len(non_decoy_list)==0
    elif decoy_fp_rate==1:
        assert len(non_decoy_list)>0
