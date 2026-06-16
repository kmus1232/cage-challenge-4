import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
from CybORG.Simulator.Actions import *


@pytest.fixture()
def cyborg():
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=FiniteStateRedAgent,
        steps=1000
    )

    cyborg = CybORG(scenario_generator=sg)
    cyborg.reset()

    return cyborg

@pytest.mark.skip("Test failing - under investigation")
def test_degrade_deception_interaction(cyborg: CybORG):
    '''
    Here we wait until red gets onto an appropriate host. Then we create haraka decoy process,
    kill it with degrade services, then bring it back up with another decoy action. This can create
    a contradiction between the service pid and process pid

    [한국어]
    Red가 적절한 호스트에 침투할 때까지 기다린다. 그 다음 haraka 디코이(Decoy) 프로세스를 만들고,
    Degrade Services(서비스 성능 저하)로 그 프로세스를 죽인 뒤, 또 다른 디코이 행동으로 되살린다.
    이 과정에서 서비스의 pid와 프로세스의 pid가 서로 어긋나는 모순이 발생할 수 있다.
    '''
    cyborg.reset(seed=85)
    state = cyborg.environment_controller.state
    red_agent = 'red_agent_1'
    for i in range(100):
        cyborg.step()
        if red_agent in cyborg.active_agents:
            break
    else:
        raise ValueError(f'{red_agent} not active')

    red_session_id = 0
    hostname = state.sessions[red_agent][red_session_id].hostname
    host = state.hosts[hostname]
    agents = [a for a,s in host.sessions.items() if s]
    blue_agent = next((a for a in agents if 'blue' in a), None)

    red_action = DegradeServices(hostname=hostname, session=0, agent=red_agent)
    red_action.duration = 1
    blue_action = DecoyHarakaSMPT_cc4(hostname=hostname, session=0, agent=blue_agent)
    blue_action.duration = 1

    '''
    If you have no empty steps below, then the test crashes due to Finite Red State agent.
    If you only have one, then the Decoy actions gets lucky and recreates the right pid.

    [한국어]
    아래에 빈 스텝(step)이 하나도 없으면 FiniteStateRedAgent 때문에 테스트가 크래시한다.
    빈 스텝이 하나뿐이면 디코이(Decoy) 행동이 운 좋게 올바른 pid를 다시 만들어 버린다.
    '''
    cyborg.step()
    cyborg.step()
    cyborg.step(action=blue_action, agent=blue_agent)
    services = host.services
    assert 'haraka' in services

    for i in range(10):
        cyborg.step(action=red_action, agent=red_agent)
        if not services['haraka'].active:
            break
    else:
        raise ValueError('Degrade Services failed to stop haraka service')

    cyborg.step(action=blue_action, agent=blue_agent)

    processes = {p.name:p.pid for p in host.processes}
    assert processes['haraka'] == services['haraka'].process
