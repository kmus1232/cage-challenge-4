import pprint
from random import choice, randint

import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.EnterpriseGreenAgent import EnterpriseGreenAgent
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent

pp = pprint.PrettyPrinter(indent=4)

def create_cyborg_env(param_seed: int = None):
    """ Function that creates a CybORG environment with a specifc green agent.

    A new CybORG environment is created from the EnterpriseScenario of CC4, with green agents as EnterpriseGreenAgents, and the remaining agents (blue and red) as SleepAgents. This environment is created from a random seed.
    Green agents in the scenario are collected and a single green agent interface is chosen at random, to be passed back for further testing.

    Note: This function has not been made as a pytest fixture due to the tests needing to be run from a clean environment.

    Returns:
        cyborg (CybORG): a new cyborg environment
        agent_interface (AgentInterface): an agent interface of a random green agent in the scenario

    [한국어]
    특정 Green 에이전트를 포함한 CybORG 환경을 생성하는 함수.

    CC4의 EnterpriseScenario로 새 CybORG 환경을 만든다. Green 에이전트는
    EnterpriseGreenAgent로, 나머지 에이전트(Blue·Red)는 SleepAgent로 설정한다.
    환경은 랜덤 시드로 생성한다. 시나리오 안의 Green 에이전트들을 모은 뒤,
    그중 하나의 Green 에이전트 인터페이스를 무작위로 골라 후속 테스트용으로 반환한다.

    참고: 테스트는 깨끗한 환경에서 실행되어야 하므로 이 함수는 pytest fixture로
    만들지 않았다.

    반환값:
        cyborg (CybORG): 새 cyborg 환경
        agent_interface (AgentInterface): 시나리오 내 무작위 Green 에이전트의 인터페이스
    """
    if param_seed is None:
        seed = randint(10, 100000)
    else:
        seed = param_seed
    print("environment seed: " + str(seed))

    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=EnterpriseGreenAgent, red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=sg, seed=seed)
    cyborg.environment_controller.reset()

    # [설명] 에이전트 인터페이스 중 이름에 'green'이 포함된 것만 모은다.
    scenario_green_agents = []
    for entity_name, entity_val in cyborg.environment_controller.agent_interfaces.items():
        if 'green' in entity_name:
            scenario_green_agents.append(entity_val)

    # [설명] CybORG 환경의 난수 생성기로 Green 에이전트 하나를 무작위 선택한다.
    np_random = cyborg.np_random
    agent_interface = np_random.choice(scenario_green_agents)

    return cyborg, agent_interface