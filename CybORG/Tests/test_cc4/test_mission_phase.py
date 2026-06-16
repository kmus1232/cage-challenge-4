import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent

"""
Testing the implementation of the mission_phases functionality.

Initially, step starts at -1 but allowed_subnets are filled as if mission_phase = 0. 
For each step, step_count increments. 
If this starts a new mission_phase, the mission_phase value and allowed_subnets are updated accordingly.

Mission Phase Process:
    1) steps given as variable for EnterpriseScenarioGenerator (ESG)
        a) mission_phases calculated off this
        b) allowed_subnets is pre-defined in ESG
    2) mission_phases and allowed_subnets moved into Scenario
    3) state is initialised from scenario
        a) mission_phase of current state, held in State
    4) on env reset
        a) step = -1
    5) on env step
        a) step = step + 1
        b) check if this affects mission_phase, if so:
            i) change mission_phase to zero
            ii) update allowed_subnets in agent interfaces and action spaces

    Note: Agents that utilise mission_phases (green), can see the allowed_subnets change in their action_space and act accordingly.


References in code:
    - Attributes:
        - Scenario.mission_phases
        - Scenario.allowed_subnets_per_mphase
        - State.mission_phase
        - EnterpriseScenarioGenerator.mission_phases

    - Functions and Methods Used/Effected:
        - EnterpriseScenarioGenerator
            - init
            - create_scenario
            - _set_allowed_subnets_per_mission_phase
        - Scenario
            - init
        - EnvironmentController
            - step
            - reset
            - _update_agents_allowed_subnets
        - State
            - init
            - check_next_phase_on_update_step 
        - AgentInterface
            - update_allowed_subnets
        - ActionSpace
            - get_action_space


[한국어]
mission_phases(미션 단계) 기능 구현을 검증하는 테스트.

처음에 step은 -1에서 시작하지만, allowed_subnets(허용 서브넷)는 mission_phase = 0인
것처럼 채워진다. 매 스텝마다 step_count가 증가한다. 이 증가가 새로운 mission_phase를
시작시키면 mission_phase 값과 allowed_subnets가 그에 맞게 갱신된다.

미션 단계(Mission Phase) 처리 과정:
    1) EnterpriseScenarioGenerator(ESG)에 steps가 변수로 주어진다.
        a) 이를 기준으로 mission_phases가 계산된다.
        b) allowed_subnets는 ESG에 미리 정의되어 있다.
    2) mission_phases와 allowed_subnets가 Scenario(시나리오)로 옮겨진다.
    3) 시나리오로부터 state(상태)가 초기화된다.
        a) 현재 상태의 mission_phase는 State에 보관된다.
    4) 환경(env) reset 시
        a) step = -1
    5) 환경(env) step 시
        a) step = step + 1
        b) 이것이 mission_phase에 영향을 주는지 확인하고, 그렇다면:
            i) mission_phase를 0으로 변경
            ii) 에이전트 인터페이스와 행동 공간(action space)의 allowed_subnets 갱신

    참고: mission_phases를 활용하는 에이전트(green)는 자신의 action_space에서
    allowed_subnets 변화를 관찰하고 그에 맞게 행동할 수 있다.

코드 내 참조 대상:
    - 속성(Attributes)
    - 사용/영향받는 함수와 메서드(Functions and Methods Used/Effected)
"""

def run_cc4_steps(steps=9, agent_type="green", output="obs"):

    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=steps)
    cyborg = CybORG(scenario_generator=sg)

    env = cyborg.environment_controller
    env.reset()

    for entity_name, entity_val in env.agent_interfaces.items():
        if agent_type in entity_name:
            agent = entity_val.agent
            agent_name = entity_name
            break

    observations = {}
    obs = cyborg.get_observation(agent_name)
    action_space = cyborg.get_action_space(agent_name)

    for i in range(steps):
        
        action = agent.get_action(obs, action_space)
        results = cyborg.step(action=action, agent=agent_name)
        obs = results.observation
        action_space = results.action_space

        mission_phase = env.state.mission_phase
        agent_allowed_subnets = env.agent_interfaces[agent_name].allowed_subnets
        observations[i] = (mission_phase, agent_allowed_subnets)

    if output == "obs":
        return observations
    else:
        return cyborg

@pytest.mark.parametrize("steps, p0_steps, p1_steps, p2_steps", [
    (3, 1, 1, 1),
    (9, 3, 3, 3),
    (10, 4, 3, 3),
    (11, 4, 4, 3),
    (100, 34, 33, 33)
])
def test_steps_distribution(steps, p0_steps, p1_steps, p2_steps):
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=steps)
    cyborg = CybORG(scenario_generator=sg)
    env = cyborg.environment_controller
    env.reset()

    assert env.state.scenario.mission_phases == (p0_steps, p1_steps, p2_steps)

@pytest.mark.parametrize("step, expected_phase, step_size", [
    (0, 0, 1), (1, 1, 1), (2, 2, 1),
    (0, 0, 3), (1, 0, 3), (2, 0, 3),
    (3, 1, 3), (4, 1, 3), (5, 1, 3),
    (6, 2, 3), (7, 2, 3), (8, 2, 3)
])
def test_mission_phase_change_points(step, expected_phase, step_size):
    total_steps = 3 * step_size
    obs_dict = run_cc4_steps(steps=total_steps)
    assert obs_dict[step][0] == expected_phase

# [설명] allowed_subnets 검증에 더 이상 유효하지 않은 테스트라 skip 처리됨 (2024-02-04)
@pytest.mark.skip("No longer a valid test for allowed subnets - 02/04/24")
@pytest.mark.parametrize("phase", [i for i in range(3)])
def test_phase_subnet_matching(phase):
    obs_dict = run_cc4_steps(steps=9)

    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=9)
    expected_allowed_subnets = sg._set_allowed_subnets_per_mission_phase()

    for _, (p, s) in obs_dict.items():
        if p == phase:
            for name, value in expected_allowed_subnets.items():
                if value[phase]:
                    assert name in s
                else:
                    assert name not in s


def test_step_count():
    """test that step count progresses logically

    [한국어]
    step_count가 논리적으로 증가하는지 검증한다.
    """
    sg = EnterpriseScenarioGenerator()
    cyborg = CybORG(scenario_generator=sg)
    assert cyborg.environment_controller.step_count == 0
    cyborg.step()
    assert cyborg.environment_controller.step_count == 1
    cyborg.step()
    assert cyborg.environment_controller.step_count == 2
    cyborg.reset()
    assert cyborg.environment_controller.step_count == 0


def test_zero_step():
    obs_dict = run_cc4_steps()

    try:
        step_zero = obs_dict[0]
    except KeyError as e:
        print(obs_dict[0])
        print(e)
        assert False
    
    assert True

def test_over_max_step():
    steps = 9
    
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=steps)
    cyborg = CybORG(scenario_generator=sg)

    env = cyborg.environment_controller
    env.reset()

    for entity_name, entity_val in env.agent_interfaces.items():
        if 'green' in entity_name:
            agent = entity_val.agent
            agent_name = entity_name
            break

    obs = cyborg.get_observation(agent_name)
    action_space = cyborg.get_action_space(agent_name)

    for i in range(steps):
        action = agent.get_action(obs, action_space)
        results = cyborg.step(action=action, agent=agent_name)
        obs = results.observation
        action_space = results.action_space

    with pytest.raises(ValueError):
        action = agent.get_action(obs, action_space)
        results = cyborg.step(action=action, agent=agent_name)

