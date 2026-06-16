import pytest

from CybORG.Simulator.Actions.Action import InvalidAction
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator, SUBNET
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions.AbstractActions import Impact
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG import CybORG
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Simulator.Service import Service

ordered_subnets = [
    [SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.ADMIN_NETWORK, SUBNET.OFFICE_NETWORK], 
    [SUBNET.CONTRACTOR_NETWORK], 
    [SUBNET.RESTRICTED_ZONE_A],
    [SUBNET.OPERATIONAL_ZONE_A],
    [SUBNET.RESTRICTED_ZONE_B],
    [SUBNET.OPERATIONAL_ZONE_B],
]

policy_1 = [
    [1,1,1,0,1,0],
    [1,1,1,0,1,0],
    [1,1,1,1,1,0],
    [0,0,1,1,0,0],
    [1,1,1,0,1,1],
    [0,0,0,0,1,1]
]

policy_2 = [
    [1,1,1,0,1,0],
    [1,1,0,0,1,0],
    [1,0,1,0,0,0],
    [0,0,0,1,0,0],
    [1,1,0,0,1,1],
    [0,0,0,0,1,1]
]

policy_3 = [
    [1,1,1,0,1,0],
    [1,1,1,0,0,0],
    [1,1,1,1,0,0],
    [0,0,1,1,0,0],
    [1,0,0,0,1,0],
    [0,0,0,0,0,1]
]

@pytest.mark.parametrize('mission_phase', [0,1,2])
def test_blocks_not_interfere_with_green(mission_phase):

    # Set up CybORG with EnterpriseScenarioGenerator (cc4)
    # EnterpriseScenarioGenerator(cc4)로 CybORG 환경을 구성한다.
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=EnterpriseGreenAgent, red_agent_class=SleepAgent, steps=300
    )

    cyborg = CybORG(scenario_generator=esg, seed=3)
    env = cyborg.environment_controller
    env.reset()

    # set all greens to have no false detections or phishing email effects
    # 모든 Green 에이전트의 오탐(false detection)과 피싱 이메일 효과를 0으로 만든다.
    for _, agent_interface in cyborg.environment_controller.agent_interfaces.items():
        agent = agent_interface.agent
        if isinstance(agent, EnterpriseGreenAgent):
            agent.fp_detection_rate = 0.0
            agent.phishing_error_rate = 0.0

    # for each entry in the policy table that is a 0 (where blocks should not impact as the greens are not expecting to be allowed communication to), add a block
    # 통신정책표에서 값이 0인 항목마다 트래픽 차단을 추가한다. 0은 Green이 애초에
    # 통신을 허용받지 못한 구간이므로, 차단을 걸어도 Green에 영향이 없어야 한다.
    pol = mission_phase
    for row in range(len(comms_policies[pol])):
        for col in range(len(comms_policies[pol][row])):
            if comms_policies[pol][row][col] == 0:
                r_subnets = ordered_subnets[row]
                c_subnets = ordered_subnets[col]

                for r_sub in r_subnets:
                    for c_sub in c_subnets:
                        blocked_pair = (r_sub.value, c_sub.value)
                        if r_sub.value in cyborg.environment_controller.state.blocks.keys():
                            cyborg.environment_controller.state.blocks[r_sub.value].append(c_sub.value)
                        else:
                            cyborg.environment_controller.state.blocks[r_sub.value] = [c_sub.value]
                        
    
    # start the step count at the correct point for the desired mission phase
    # 원하는 미션 단계(mission phase)에 맞춰 step 카운트를 올바른 지점에서 시작한다.
    if mission_phase == 0:
        cyborg.environment_controller.step_count = 0
    elif mission_phase == 1:
        cyborg.environment_controller.step_count = 100
    else:
        cyborg.environment_controller.step_count = 200

    # Run 100 steps and assert that each have the reward 0 - showing that green has not been impacted by the blocks
    # 100 스텝을 실행하며 매 스텝 보상이 0임을 확인한다. 보상 0은 차단(blocks)이
    # Green에 영향을 주지 않았다는 뜻이다.
    for i in range(100):
        obs, reward, _, _ = cyborg.parallel_step()
        step_reward = reward['blue_agent_0']['BlueRewardMachine']

        if not step_reward == 0:
            for agent, entry in obs.items():
                if entry['success'] == False:
                    print(agent, entry['action'], entry['success'])
        assert step_reward == 0


# 세 가지 미션 단계별 통신정책표를 묶고, 각 정책에 대해 테스트를 직접 실행한다.
comms_policies = [policy_1, policy_2, policy_3]
for pol in range(len(comms_policies)):
    print("Policy", pol)
    test_blocks_not_interfere_with_green(pol)

