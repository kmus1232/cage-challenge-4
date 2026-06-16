import pytest

from random import randint
from .conftest import create_sleep_cyborg, create_cc4_complex_cyborg

from CybORG import CybORG
from CybORG.Shared.Session import VelociraptorServer

# issue-174 fixes problem
# issue-174 수정으로 해결된 문제를 검증한다.
def test_action_space_server():
    # test 100 random seeds
    # 랜덤 시드 100개로 테스트한다.
    for i in range(100):
        seed = randint(1000, 9999)
        print(seed)

        cyborg = create_sleep_cyborg(seed=seed)

        # for each blue agent
        # 각 Blue 에이전트마다 반복한다.
        for j in range(5):
            agent = 'blue_agent_' + str(j)

            agent_state_velo_sessions = [sess_id for sess_id, sess in cyborg.environment_controller.state.sessions[agent].items() if isinstance(sess, VelociraptorServer)]
            agent_server_sessions = [sess for sess, val in cyborg.environment_controller.agent_interfaces[agent].action_space.server_session.items() if val == True]
            
            assert agent_state_velo_sessions == [0]
            assert agent_state_velo_sessions == agent_server_sessions

def test_action_space_client_size():
    # test 100 random seeds
    # 랜덤 시드 100개로 테스트한다.
    for i in range(100):
        seed = randint(1000, 9999)
        print(seed)

        cyborg = create_sleep_cyborg(seed=seed)

        # for each blue agent
        # 각 Blue 에이전트마다 반복한다.
        for j in range(5):
            agent = 'blue_agent_' + str(j)

            agent_state_sessions = [sess_id for sess_id in cyborg.environment_controller.state.sessions[agent].keys()]
            agent_client_sessions = [sess for sess, val in cyborg.environment_controller.agent_interfaces[agent].action_space.client_session.items() if val == True]

            assert agent_state_sessions == agent_client_sessions


@pytest.mark.parametrize('seed', [100, 200, 300, 400, 500])
def test_action_space_and_state_sessions_equal_thru_steps(seed):
    loop = 1000
    cyborg = create_cc4_complex_cyborg(seed=seed, steps=loop)

    for i in range(loop):
        cyborg.step()
        # for each blue agent
        # 각 Blue 에이전트마다 반복한다.
        for j in range(5):
            agent = 'blue_agent_' + str(j)

            agent_state_sessions = [sess_id for sess_id in cyborg.environment_controller.state.sessions[agent].keys()]
            agent_client_sessions = [sess for sess, val in cyborg.environment_controller.agent_interfaces[agent].action_space.client_session.items() if val == True]
            
            assert agent_state_sessions == agent_client_sessions