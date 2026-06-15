---
hide:
  - toc
---

# Welcome to the CC4 Reference Documentation (CC4 레퍼런스 문서에 오신 것을 환영합니다)

> CC4(CAGE Challenge 4) 레퍼런스 문서에 오신 것을 환영합니다.

## Environment (환경)

<div class="grid cards" markdown>

-   :material-wall:{ .lg .middle } __Scenario Creation__

    ---

    In order to spin up the CC4 CybORG environment, a number of creation classes are needed. These classes hold details about the different entity and agent objects that will be needed in the simulation.

    > CC4 CybORG(Cyber Operations Research Gym) 환경을 구동하려면 여러 생성용 클래스가 필요합니다. 이 클래스들은 시뮬레이션에 쓰일 다양한 엔티티(entity, 개체)와 에이전트 객체에 관한 세부 정보를 담고 있습니다.
    
    The class [EnterpriseScenarioGenerator](environment/scenario_creation/enterprise_scenario_generator.md) is specific to CC4 and holds all the details regarding how to create this challenge.

    > [EnterpriseScenarioGenerator](environment/scenario_creation/enterprise_scenario_generator.md) 클래스는 CC4 전용이며, 이 챌린지를 어떻게 생성하는지에 관한 모든 세부 정보를 담고 있습니다.


-   :material-door-open:{ .lg .middle } __Internal Objects__

    ---

    Once the simulation is up and running, there are a number of internal class objects that hold the majority of the simulation data and control the series of events that happen on each 'step' of the simulated episode.

    > 시뮬레이션이 구동되고 나면, 시뮬레이션 데이터의 대부분을 보관하고 시뮬레이션 에피소드(episode)의 매 '스텝(step)'마다 일어나는 일련의 이벤트를 제어하는 여러 내부 클래스 객체가 존재합니다.


-   :material-star-circle:{ .lg .middle } __Rewards__

    ---

    For the Blue agents to learn, they are given negative rewards according to what has taken place in the environment. For CC4, the [BlueRewardMachine](environment/outputs_and_rewards/blue_reward_machine.md) is in charge of calculating these rewards. 

    > Blue 에이전트(방어 측)가 학습할 수 있도록, 환경에서 일어난 일에 따라 음(-)의 보상이 주어집니다. CC4에서는 [BlueRewardMachine](environment/outputs_and_rewards/blue_reward_machine.md)(보상 머신)이 이 보상을 계산하는 역할을 담당합니다.

    For more information about the specific rewards given, look through the CC4 [Challenge Details](../README.md#rewards).

    > 구체적으로 어떤 보상이 주어지는지에 대한 자세한 내용은 CC4 [Challenge Details](../README.md#rewards)(챌린지 상세) 문서를 참고하세요.

-   :material-texture-box:{ .lg .middle } __Entities__

    ---

    Within the environment, there are lots of smaller classes that are used to give the scenario more depth. 

    > 환경 안에는 시나리오(scenario)에 더 풍부한 깊이를 더해주는 작은 클래스들이 많이 존재합니다.
    
    These classes all inherit from the parent class [Entity](hosts_and_networking/entity.md).

    > 이 클래스들은 모두 부모 클래스인 [Entity](hosts_and_networking/entity.md)(엔티티)를 상속합니다.

</div>

## Outputs and Wrappers (출력과 래퍼)

<div class="grid cards" markdown>

-   :material-export:{ .lg .middle } __Environmental Outputs__

    ---

    After each step is taken, the CybORG environment outputs information about that step; including the observation space. This is used to train the blue agents.

    > 매 스텝(step)이 수행될 때마다 CybORG 환경은 해당 스텝에 관한 정보를 출력하며, 여기에는 관찰 공간(observation space)도 포함됩니다. 이 정보는 Blue 에이전트(방어 측)를 학습시키는 데 사용됩니다.

-   :material-gift-outline:{ .lg .middle } __Wrappers__

    ---

    To facilitate the usage of the outputted data, wrappers can be used to augment the data. These can be written as an interface between CybORG and a machine learning library, or as an aid to make the environmental output more comprehendable to people. 

    > 출력된 데이터를 더 쉽게 활용할 수 있도록, 래퍼(Wrapper)를 사용해 데이터를 가공할 수 있습니다. 래퍼는 CybORG와 머신러닝 라이브러리 사이의 인터페이스로 작성할 수도 있고, 환경 출력을 사람이 더 이해하기 쉽게 만들어주는 보조 도구로 작성할 수도 있습니다.
    
    While a few wrappers have been provided here, there are no restrictions around participants creating their own with development of additional wrappers being actively encouraged.

    > 여기에 몇 가지 래퍼가 기본 제공되지만, 참가자가 직접 래퍼를 만드는 데에는 아무런 제약이 없으며, 오히려 추가 래퍼 개발이 적극 권장됩니다.

</div>

## Agents and Actions (에이전트와 행동)

<div class="grid cards" markdown>

-   :material-account-wrench-outline:{ .lg .middle } __Base Classes__

    ---

    These classes are parents of all the agents and actions in this simulation.

    > 이 클래스들은 이 시뮬레이션에 등장하는 모든 에이전트와 행동(Action)의 부모 클래스입니다.


-   :material-incognito:{ .lg .middle } __Red Agents__

    ---

    Red agents are the attackers that are trying to take complete control of the network.
    They have 10 possible actions and there are a few different red agents available, with [FiniteRedAgent](agents/FiniteStateRedAgent.md) being the primary agent.

    > Red 에이전트(공격 측)는 네트워크를 완전히 장악하려는 공격자입니다. 이들은 10가지 행동(Action)을 사용할 수 있으며, 몇 가지 서로 다른 Red 에이전트가 제공됩니다. 그중 [FiniteRedAgent](agents/FiniteStateRedAgent.md)가 주력 에이전트입니다.

    This implementation is quite complex, therefore a [red overview](agents/red_overview.md) has been provided for more information.

    > 이 구현은 상당히 복잡하기 때문에, 더 자세한 정보를 담은 [red overview](agents/red_overview.md)(Red 에이전트 개요)를 함께 제공합니다.


-   :material-laptop-account:{ .lg .middle } __Green Agents__

    ---

    Green agents are the common users of the network, who are just trying to get work done while the invisible red and blue wars rage on. Blue agents need to avoid any impacts to the green agents' work, otherwise they will receive negative rewards.

    > Green 에이전트(정상 사용자)는 네트워크의 일반 사용자로, 보이지 않는 Red와 Blue의 전쟁이 벌어지는 와중에도 그저 자기 일을 하려는 존재입니다. Blue 에이전트(방어 측)는 Green 에이전트의 업무에 영향을 주지 않아야 하며, 그렇지 않으면 음(-)의 보상을 받게 됩니다.

    CC4 uses [EnterpriseGreenAgents](agents/green_agents.md), who do one of three things: work locally, access a remote service, or sleep (hopefully not on the clock!).

    > CC4는 [EnterpriseGreenAgents](agents/green_agents.md)를 사용하며, 이들은 세 가지 중 하나의 행동을 합니다: 로컬에서 작업하기, 원격 서비스에 접속하기, 또는 잠자기(부디 근무 중에는 아니길 바랍니다!).

-   :material-shield-account:{ .lg .middle } __Blue Agents__

    ---

    Blue agents are the defender of the network, and the agents that competitors are trying to build. They have 8 actions (including Sleep) that they can use to identify and take back control of the network from Red.

    > Blue 에이전트(방어 측)는 네트워크의 방어자이자, 참가자들이 직접 만들고자 하는 에이전트입니다. 이들은 (Sleep을 포함해) 8가지 행동(Action)을 사용할 수 있으며, 이를 통해 Red(공격 측)로부터 네트워크의 통제권을 식별하고 되찾아옵니다.

</div>