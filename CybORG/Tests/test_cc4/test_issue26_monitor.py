import pytest
from pprint import pprint
from random import choice as rand_choice

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent
from CybORG.Shared.Session import Session, VelociraptorServer
from CybORG.Simulator.HostEvents import NetworkConnection
from CybORG.Simulator.Actions import Monitor, Sleep


def test_NetworkConnection_detection():
    """Test: Hosts with both Velociraptor and non-Velociraptor session types should have their NetworkConnection events detected by the Monitor action.

    [한국어]
    Velociraptor 세션과 비-Velociraptor 세션을 모두 가진 호스트에서, NetworkConnection
    이벤트가 Monitor(모니터링) 행동에 의해 탐지되는지 검증한다.
    """
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=300
    )

    cyborg = CybORG(scenario_generator=esg)
    env = cyborg.environment_controller
    env.reset()

    for agent, sessions in cyborg.environment_controller.state.sessions.items():
        if 'blue' in agent:

            # Check that session 0 in the agent's dict of sessions is a Velocirator session
            # 에이전트의 세션 딕셔너리에서 세션 0이 Velociraptor 세션인지 확인한다
            assert isinstance(sessions[0], VelociraptorServer)
            velo_hostname = sessions[0].hostname
            velo_host = env.state.hosts[velo_hostname]

            # Check that session 1 in the agent's dict of sessions is NOT a Velocirator session
            # 에이전트의 세션 딕셔너리에서 세션 1이 Velociraptor 세션이 아닌지 확인한다
            assert not isinstance(sessions[1], VelociraptorServer)
            non_velo_hostname = sessions[1].hostname
            non_velo_host = env.state.hosts[non_velo_hostname]

            # Create an arbitrary test event
            # 임의의 테스트용 이벤트를 생성한다
            test_event = NetworkConnection(
                local_address=env.state.hostname_ip_map[velo_hostname],
                remote_port=velo_host.get_ephemeral_port(),
                remote_address=rand_choice(list(env.state.ip_addresses.keys()))
            )

            # Add the test session to the velociraptor session host
            # 테스트 이벤트를 Velociraptor 세션 호스트에 추가한다
            velo_host.events.network_connections.append(test_event)
            assert len(velo_host.events.network_connections) == 1

            # Run the Monitor action and test that it is detected
            # Monitor(모니터링) 행동을 실행하고 이벤트가 탐지되는지 검증한다
            monitor_action = Monitor(session=0, agent=agent)
            monitor_obs = monitor_action.execute(state=env.state).data
            assert monitor_obs.pop("success") == True
            assert len(monitor_obs.keys()) == 1

            # Clear the events
            # 이벤트를 비운다
            velo_host.events.network_connections.clear()

            # Add the test session to the non-velociraptor session host
            # 테스트 이벤트를 비-Velociraptor 세션 호스트에 추가한다
            non_velo_host.events.network_connections.append(test_event)
            assert len(non_velo_host.events.network_connections) == 1

            # Run the Monitor action and test that it is detected
            # Monitor(모니터링) 행동을 실행하고 이벤트가 탐지되는지 검증한다
            monitor_action = Monitor(session=0, agent=agent)
            monitor_obs = monitor_action.execute(state=env.state).data
            assert monitor_obs.pop("success") == True
            assert len(monitor_obs.keys()) == 1

def test_ProcessCreation_detection():
    """Test: Hosts with both Velociraptor and non-Velociraptor session types should have their ProcessCreation events detected by the Monitor action.

    [한국어]
    Velociraptor 세션과 비-Velociraptor 세션을 모두 가진 호스트에서, ProcessCreation
    이벤트가 Monitor(모니터링) 행동에 의해 탐지되는지 검증한다.
    """

    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=300
    )

    cyborg = CybORG(scenario_generator=esg)
    env = cyborg.environment_controller
    env.reset()

    for agent, sessions in cyborg.environment_controller.state.sessions.items():
        if 'blue' in agent:

            # Check that session 0 in the agent's dict of sessions is a Velocirator session
            # 에이전트의 세션 딕셔너리에서 세션 0이 Velociraptor 세션인지 확인한다
            assert isinstance(sessions[0], VelociraptorServer)
            velo_hostname = sessions[0].hostname
            velo_host = env.state.hosts[velo_hostname]

            # Check that session 1 in the agent's dict of sessions is NOT a Velocirator session
            # 에이전트의 세션 딕셔너리에서 세션 1이 Velociraptor 세션이 아닌지 확인한다
            assert not isinstance(sessions[1], VelociraptorServer)
            non_velo_hostname = sessions[1].hostname
            non_velo_host = env.state.hosts[non_velo_hostname]

            # Create an arbitrary test event
            # 임의의 테스트용 이벤트를 생성한다
            test_event = {
                'local_address': env.state.hostname_ip_map[velo_hostname],
                'local_port': velo_host.get_ephemeral_port()
            }

            # Add the test session to the velociraptor session host
            # 테스트 이벤트를 Velociraptor 세션 호스트에 추가한다
            velo_host.events.process_creation.append(test_event)
            assert len(velo_host.events.process_creation) == 1

            # Run the Monitor action and test that it is detected
            # Monitor(모니터링) 행동을 실행하고 이벤트가 탐지되는지 검증한다
            monitor_action = Monitor(session=0, agent=agent)
            monitor_obs = monitor_action.execute(state=env.state).data
            assert monitor_obs.pop("success") == True
            assert len(monitor_obs.keys()) == 1

            # Clear the events
            # 이벤트를 비운다
            velo_host.events.process_creation.clear()

            # Add the test session to the non-velociraptor session host
            # 테스트 이벤트를 비-Velociraptor 세션 호스트에 추가한다
            non_velo_host.events.process_creation.append(test_event)
            assert len(non_velo_host.events.process_creation) == 1

            # Run the Monitor action and test that it is detected
            # Monitor(모니터링) 행동을 실행하고 이벤트가 탐지되는지 검증한다
            monitor_action = Monitor(session=0, agent=agent)
            monitor_obs = monitor_action.execute(state=env.state).data
            assert monitor_obs.pop("success") == True
            assert len(monitor_obs.keys()) == 1


def test_NetworkConnection_Persistence():
    """Test: a host event should not persist after a step

    [한국어]
    호스트 이벤트가 한 스텝(step) 이후에는 남아 있지 않아야 함을 검증한다.
    """
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=300
    )

    cyborg = CybORG(scenario_generator=esg)
    env = cyborg.environment_controller
    env.reset()

    for agent, sessions in cyborg.environment_controller.state.sessions.items():
        if 'blue' in agent:
            for sess_idx, session in sessions.items():

                # if sess_idx == 0:     # before fix, test will succeed with this added
                #     continue
                # [설명] 수정 전에는 위 두 줄(세션 0 건너뛰기)을 추가해야 테스트가 통과했다

                hostname = session.hostname
                host = env.state.hosts[session.hostname]

                # Create an arbitrary test event
                # 임의의 테스트용 이벤트를 생성한다
                test_event = NetworkConnection(
                    local_address=env.state.hostname_ip_map[hostname],
                    remote_port=host.get_ephemeral_port(),
                    remote_address=rand_choice(list(env.state.ip_addresses.keys()))
                )

                # Add the test session to the velociraptor session host
                # 테스트 이벤트를 호스트에 추가한다
                host.events.network_connections.append(test_event)
                assert len(host.events.network_connections) == 1

                # Run a cyborg step - Monitor is a blue default action so will run
                # cyborg 스텝(step)을 한 번 실행한다 - Monitor는 Blue의 기본 행동이라 자동 실행된다
                obs = cyborg.step(agent=agent, action=Sleep())
                assert len(obs.observation.keys()) == 3     # i.e. ['action', 'success', '<host>']  # 즉 키가 3개

                assert len(host.events.network_connections) == 0    # i.e. the step has caused the event to be removed  # 즉 스텝 실행이 이벤트를 제거했다

                obs = cyborg.step(agent=agent, action=Sleep())
                assert len(obs.observation.keys()) == 2     # i.e. ['action', 'success'] - the event is not persistent  # 즉 이벤트가 사라져 키가 2개


def test_ProcessCreation_Persistence():
    """Test: a host event should not persist after a step

    [한국어]
    호스트 이벤트가 한 스텝(step) 이후에는 남아 있지 않아야 함을 검증한다.
    """
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=300
    )

    cyborg = CybORG(scenario_generator=esg)
    env = cyborg.environment_controller
    env.reset()

    for agent, sessions in cyborg.environment_controller.state.sessions.items():
        if 'blue' in agent:
            for sess_idx, session in sessions.items():

                # if sess_idx == 0:     # before fix, test will succeed with this added
                #     continue
                # [설명] 수정 전에는 위 두 줄(세션 0 건너뛰기)을 추가해야 테스트가 통과했다

                hostname = session.hostname
                host = env.state.hosts[session.hostname]

                # Create an arbitrary test event
                # 임의의 테스트용 이벤트를 생성한다
                test_event = {
                    'local_address': env.state.hostname_ip_map[hostname], 
                    'local_port': host.get_ephemeral_port()
                }

                # Add the test session to the velociraptor session host
                # 테스트 이벤트를 호스트에 추가한다
                host.events.process_creation.append(test_event)
                assert len(host.events.process_creation) == 1

                # Run a cyborg step - Monitor is a blue default action so will run
                # cyborg 스텝(step)을 한 번 실행한다 - Monitor는 Blue의 기본 행동이라 자동 실행된다
                obs = cyborg.step(agent=agent, action=Sleep())
                assert len(obs.observation.keys()) == 3     # i.e. ['action', 'success', '<host>']  # 즉 키가 3개

                assert len(host.events.process_creation) == 0    # i.e. the step has caused the event to be removed  # 즉 스텝 실행이 이벤트를 제거했다

                obs = cyborg.step(agent=agent, action=Sleep())
                assert len(obs.observation.keys()) == 2     # i.e. ['action', 'success'] - the event is not persistent  # 즉 이벤트가 사라져 키가 2개
