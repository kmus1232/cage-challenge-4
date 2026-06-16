# Agents (에이전트)
There are a number of agent types available in CC4, with competitors getting to create even more!
In this tutorial, you will be introduced to some of them.

> CC4에는 여러 종류의 에이전트가 준비되어 있으며, 참가자들이 직접 더 많은 에이전트를 만들 수도 있습니다!
> 이 튜토리얼에서는 그중 일부를 소개합니다.

## Green Agent (Green 에이전트)
### EnterpriseGreenAgent
CC4 only has one type of green agent, the EnterpriseGreenAgent, which is present on every host in the network. 
It represents a normal computer user and the majority of the rewards are derived from how the action or inaction of blue affects green, when red agents are also present.

> CC4의 Green 에이전트(정상 사용자)는 `EnterpriseGreenAgent` 한 종류뿐이며, 네트워크의 모든 호스트(Host)에 존재합니다.
> 이 에이전트는 평범한 컴퓨터 사용자를 나타내며, 보상(Reward)의 대부분은 Red 에이전트(공격 측)가 함께 있을 때 Blue 에이전트(방어 측)의 행동 또는 무행동이 Green에 어떤 영향을 주는지에서 비롯됩니다.

The following example runs through all the actions that are taken by the green agents in the first step, and groups together according to action.

> 아래 예제는 첫 번째 스텝(step)에서 Green 에이전트들이 취한 모든 행동(Action)을 살펴보고, 행동별로 묶어 보여줍니다.

```python title="" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent

# Initialise the environment
steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Perform one generic step of the episode
cyborg.step()

# Get the dictionary of actions performed during that step
action_list = cyborg.environment_controller.action

# Separate the actions out into their three groups for easy viewing
green_actions = {'Sleep': {}, 'GreenLocalWork': {}, 'GreenAccessService': {}}
for agent, action in action_list.items():
    if 'green' in agent:
        action_str = str(action[0]) 
        if 'Sleep' in action_str:
            green_actions['Sleep'][agent] = action
        if 'GreenLocalWork' in action_str:
            green_actions['GreenLocalWork'][agent] = action
        if 'GreenAccessService' in action_str:
            green_actions['GreenAccessService'][agent] = action

# Print the dictionary
pprint(green_actions)
```
??? quote "Code Output"
    ```
    {'GreenAccessService': {
        'green_agent_1': [GreenAccessService 10.0.74.254 8071],
        'green_agent_11': [GreenAccessService 10.0.90.252 2469],
        'green_agent_13': [GreenAccessService 10.0.183.252 3890],
        'green_agent_15': [GreenAccessService 10.0.86.253 5190],
        'green_agent_17': [GreenAccessService 10.0.183.254 1220],
        'green_agent_18': [GreenAccessService 10.0.183.252 3799],
        'green_agent_21': [GreenAccessService 10.0.177.254 5456],
        'green_agent_25': [GreenAccessService 10.0.86.253 9220],
        'green_agent_3': [GreenAccessService 10.0.177.253 5055],
        'green_agent_36': [GreenAccessService 10.0.74.252 8282],
        'green_agent_38': [GreenAccessService 10.0.183.251 5638],
        'green_agent_39': [GreenAccessService 10.0.86.253 5796],
        'green_agent_4': [GreenAccessService 10.0.183.253 5740],
        'green_agent_44': [GreenAccessService 10.0.74.254 8071],
        'green_agent_45': [GreenAccessService 10.0.177.253 5055]
    },
    'GreenLocalWork': {
        'green_agent_0': [GreenLocalWork 10.0.26.88],
        'green_agent_2': [GreenLocalWork 10.0.26.173],
        'green_agent_22': [GreenLocalWork 10.0.183.36],
        'green_agent_24': [GreenLocalWork 10.0.183.53],
        'green_agent_26': [GreenLocalWork 10.0.183.153],
        'green_agent_29': [GreenLocalWork 10.0.74.39],
        'green_agent_40': [GreenLocalWork 10.0.90.77],
        'green_agent_42': [GreenLocalWork 10.0.90.221],
        'green_agent_43': [GreenLocalWork 10.0.90.137],
        'green_agent_47': [GreenLocalWork 10.0.32.201],
        'green_agent_6': [GreenLocalWork 10.0.27.73],
        'green_agent_7': [GreenLocalWork 10.0.27.109],
        'green_agent_8': [GreenLocalWork 10.0.27.53],
        'green_agent_9': [GreenLocalWork 10.0.27.189]
    },
    'Sleep': {
        'green_agent_10': [Sleep],
        'green_agent_12': [Sleep],
        'green_agent_14': [Sleep],
        'green_agent_16': [Sleep],
        'green_agent_19': [Sleep],
        'green_agent_20': [Sleep],
        'green_agent_23': [Sleep],
        'green_agent_27': [Sleep],
        'green_agent_28': [Sleep],
        'green_agent_30': [Sleep],
        'green_agent_31': [Sleep],
        'green_agent_32': [Sleep],
        'green_agent_33': [Sleep],
        'green_agent_34': [Sleep],
        'green_agent_35': [Sleep],
        'green_agent_37': [Sleep],
        'green_agent_41': [Sleep],
        'green_agent_46': [Sleep],
        'green_agent_5': [Sleep]
        }
    }
    ```
There are 3 actions that an EnterpriseGreenAgent can take:

- [Sleep](../03_Actions/A_Understanding_Actions/3_Sleep.md)
- [GreenLocalWork](../../reference/actions/green_actions/local_work.md)
- [GreenAccessService](../../reference/actions/green_actions/access_service.md)

> `EnterpriseGreenAgent`가 취할 수 있는 행동(Action)은 3가지입니다.
>
> - [Sleep](../03_Actions/A_Understanding_Actions/3_Sleep.md) — 아무것도 하지 않고 대기
> - [GreenLocalWork](../../reference/actions/green_actions/local_work.md) — 자기 호스트에서 로컬 작업 수행
> - [GreenAccessService](../../reference/actions/green_actions/access_service.md) — 다른 호스트의 서비스(Service)에 접속

The string output of GreenLocalWork includes the IP address of the host where the local work is taking place, and the string output of GreenAccessService includes the destination IP address and port number.

> `GreenLocalWork`의 문자열 출력에는 로컬 작업이 일어나는 호스트의 IP 주소가 포함되고, `GreenAccessService`의 문자열 출력에는 접속 대상 IP 주소와 포트(Port) 번호가 포함됩니다.

During GreenLocalWork, another subaction called [PhishingEmail](../../reference/actions/green_actions/phishing_email.md) can also occur. However as a sub action this will not appear on the action list.

> `GreenLocalWork`가 진행되는 동안 [PhishingEmail](../../reference/actions/green_actions/phishing_email.md)(피싱 이메일)이라는 또 다른 하위 행동(subaction)이 발생할 수도 있습니다. 다만 이는 하위 행동이므로 행동 목록(action list)에는 나타나지 않습니다.


## Red Agents (Red 에이전트)
CC4 has two main types of heuristic red agents: [RandomSelectRedAgent](../../reference/agents/RandomSelectRedAgent.md), and [FiniteStateRedAgent](../../reference/agents/FiniteStateRedAgent.md).

> CC4에는 휴리스틱(heuristic, 경험 규칙 기반) 방식의 Red 에이전트(공격 측)가 크게 두 종류 있습니다. [RandomSelectRedAgent](../../reference/agents/RandomSelectRedAgent.md)와 [FiniteStateRedAgent](../../reference/agents/FiniteStateRedAgent.md)입니다.


### RandomSelectRedAgent
This red agent does what it says on the tin, 'randomly selects'. 

> 이 Red 에이전트는 이름 그대로 행동을 '무작위로 선택(randomly selects)'합니다.

For red agents, there are a [10 possible actions](../../reference/agents/red_overview.md#red-agent-actions), and this agent picks a random valid one from the list. Below is an example action list output from a RandomSelectRedAgent.

> Red 에이전트가 취할 수 있는 행동(Action)은 [총 10가지](../../reference/agents/red_overview.md#red-agent-actions)이며, 이 에이전트는 그 목록에서 유효한 행동 하나를 무작위로 고릅니다. 아래는 `RandomSelectRedAgent`의 행동 목록 출력 예시입니다.

```python title="example_random_red.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, RandomSelectRedAgent

# Initialise environment
steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=RandomSelectRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Record actions of red_agent_0
red_agent_0_actions = []
for i in range(10):
    cyborg.step()
    step_actions = cyborg.environment_controller.action
    red_agent_0_actions.append(step_actions['red_agent_0'])

# Print red_agent_0's actions
pprint(red_agent_0_actions)
```
???+ quote "Code Output"
    ```
    [[AggressiveServiceDiscovery 10.0.43.13],
    [DiscoverRemoteSystems 10.0.43.0/24],
    [PrivilegeEscalate contractor_network_subnet_user_host_5],
    [DegradeServices contractor_network_subnet_user_host_5],
    [Withdraw contractor_network_subnet_user_host_5],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep]]
    ```

#### Agent Options (에이전트 옵션)
The agent has two additional options:

> 이 에이전트에는 추가 옵션이 두 가지 있습니다.

```python title="RandomSelectRedAgent.py" linenums="34"
self.print_output = False
self.disable_withdraw = False
```

If `print_output` is set to `True`, the example_random_red.py (minus the final two lines) would output the following:

> `print_output`을 `True`로 설정하면, example_random_red.py(마지막 두 줄 제외)는 다음과 같이 출력합니다.

???+ quote "Code Output"
    ```
    ** Turn 0 for red_agent_0 **
    Action: Initial Observation
    Action Success: UNKNOWN

    ** Turn 1 for red_agent_0 **
    Action: AggressiveServiceDiscovery 10.0.43.13
    Action Success: TRUE

    ** Turn 2 for red_agent_0 **
    Action: DiscoverRemoteSystems 10.0.43.0/24
    Action Success: TRUE

    ** Turn 3 for red_agent_0 **
    Action: PrivilegeEscalate contractor_network_subnet_user_host_5
    Action Success: TRUE

    ** Turn 4 for red_agent_0 **
    Action: DegradeServices contractor_network_subnet_user_host_5
    Action Success: TRUE


    *** red_agent_0 attempts to withdraw ***
    ```
This gives you much more visibility of what is happening, as you can tell what actions were successful.

> 이렇게 하면 어떤 행동이 성공했는지 알 수 있어, 무슨 일이 일어나고 있는지 훨씬 더 잘 파악할 수 있습니다.

You can tell that the final attempt to withdraw was successful as there are no turns after this.
To stop the agent trying to withdraw itself, you can set `disable_withdraw` to `True`.

> 마지막의 Withdraw(철수) 시도 이후에 더 이상 턴이 없으므로, 그 철수 시도가 성공했음을 알 수 있습니다.
> 에이전트가 스스로 철수를 시도하지 않게 하려면 `disable_withdraw`를 `True`로 설정하면 됩니다.


### FiniteStateRedAgent
This section will cover how to use the FiniteStateRedAgent. If you want more information about its [design](../../reference/agents/red_overview.md#finite-state-machine-based-red-agents) or the ability to [make variants](../../reference/agents/red_overview.md#creating-variant-fsm-red-agents) of this agent, please use the links provided.

> 이 절에서는 `FiniteStateRedAgent`의 사용 방법을 다룹니다. 이 에이전트의 [설계(design)](../../reference/agents/red_overview.md#finite-state-machine-based-red-agents)나 [변형(variant) 만들기](../../reference/agents/red_overview.md#creating-variant-fsm-red-agents)에 대한 더 자세한 정보가 필요하면 제공된 링크를 참고하세요.

The code to show the FiniteStateRedAgent actions is almost identical to `example_random_red.py` for the RandomSelectRedAgent, with only the agent name and number of steps being changed.

> `FiniteStateRedAgent`의 행동을 보여주는 코드는 `RandomSelectRedAgent`용 `example_random_red.py`와 거의 동일하며, 에이전트 이름과 스텝(step) 수만 바뀝니다.

```python title="example_fsm_red.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, RandomSelectRedAgent

# Initialise environment
steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Record actions of red_agent_0
red_agent_0_actions = []
for i in range(20):
    cyborg.step()
    step_actions = cyborg.environment_controller.action
    red_agent_0_actions.append(step_actions['red_agent_0'])

# Print red_agent_0's actions
pprint(red_agent_0_actions)
```
???+ quote "Code Output"
    ```
    [[DiscoverRemoteSystems 10.0.43.0/24],
    [AggressiveServiceDiscovery 10.0.43.251],
    [DiscoverRemoteSystems 10.0.43.0/24],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep],
    [StealthServiceDiscovery 10.0.43.253],
    [AggressiveServiceDiscovery 10.0.43.143],
    [AggressiveServiceDiscovery 10.0.43.61],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep],
    [StealthServiceDiscovery 10.0.43.224],
    [Sleep],
    [Sleep],
    [ExploitRemoteService_cc4 10.0.43.61],
    [PrivilegeEscalate contractor_network_subnet_user_host_0],
    [Impact contractor_network_subnet_user_host_0]]
    ```
The resultant actions have a more logical sequence than the RandomSelectRedAgent, with the agent first exploring the environment with discovery actions before focusing on a target to gain privileges on and impact.

> 그 결과로 나온 행동 순서는 `RandomSelectRedAgent`보다 더 논리적입니다. 이 에이전트는 먼저 탐색(discovery) 행동으로 환경을 살핀 다음, 목표 하나를 골라 권한을 획득하고(PrivilegeEscalate) 타격(Impact)을 가합니다.

While the RandomSelectRedAgent should be easy to defeat or mitigate against, the FiniteStateRedAgent and its variants shold be a more difficult challenge.

> `RandomSelectRedAgent`는 비교적 쉽게 막거나 대응할 수 있지만, `FiniteStateRedAgent`와 그 변형들은 더 까다로운 도전 과제가 될 것입니다.

#### Agent Options (에이전트 옵션)
There are a large amount of possible agent modifications for this agent; so many that a [FSM variant template](../../reference/agents/red_overview.md#creating-variant-fsm-red-agents) has been created to allow for better control and to reduce complexity.

> 이 에이전트는 변경할 수 있는 설정이 매우 많습니다. 그 수가 너무 많아, 더 나은 제어와 복잡도 감소를 위해 [FSM 변형 템플릿(variant template)](../../reference/agents/red_overview.md#creating-variant-fsm-red-agents)이 마련되어 있습니다.

However, three options have been left in the original. Two are for verbosity and one is for basic prioritisation.

> 다만 원본에는 세 가지 옵션이 남아 있습니다. 두 개는 출력 상세도(verbosity), 하나는 기본적인 우선순위 지정(prioritisation)을 위한 것입니다.

```python title="FiniteStateRedAgent.py" linenums="50"
self.print_action_output = False
self.print_obs_output = False
self.prioritise_servers = False
```

Output verbosity can be scaled to either 'low', with only actions displayed, or 'high', with the environmental observation and internal agent logic also shown. 

> 출력 상세도는 '낮음(low)'으로 두어 행동(Action)만 표시하거나, '높음(high)'으로 두어 환경 관찰값(Observation)과 에이전트 내부 로직까지 함께 표시할 수 있습니다.

Explore these two output options below:

> 아래에서 이 두 가지 출력 옵션을 살펴봅니다.

=== "Output Actions Only"
    If you want to get a grasp of what the red agent is doing, without being overwhelmed by information - this is the option for you.

    Active red agents state:

    - Who they are
    - What step they are on internally
    - What there action for that step was
    - How successful the action was

    This make it easy to tell the progress agents are making and what agents are active.

    ??? quote "Code Output: print_action_output == True"
        ```
        ** Turn 0 for red_agent_0 **
        Action: Initial Observation
        Action Success: UNKNOWN

        ** Turn 1 for red_agent_0 **
        Action: DiscoverRemoteSystems 10.0.43.0/24
        Action Success: TRUE

        ** Turn 2 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.251
        Action Success: TRUE

        ** Turn 3 for red_agent_0 **
        Action: DiscoverRemoteSystems 10.0.43.0/24
        Action Success: TRUE

        ** Turn 4 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 5 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 6 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 7 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 8 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: TRUE

        ** Turn 9 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.143
        Action Success: TRUE

        ** Turn 10 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.61
        Action Success: TRUE

        ** Turn 11 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 12 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 13 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 14 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 15 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: TRUE

        ** Turn 16 for red_agent_0 **
        Action: ExploitRemoteService_cc4 10.0.43.61
        Action Success: IN_PROGRESS

        ** Turn 17 for red_agent_0 **
        Action: ExploitRemoteService_cc4 10.0.43.61
        Action Success: IN_PROGRESS

        ** Turn 18 for red_agent_0 **
        Action: ExploitRemoteService_cc4 10.0.43.61
        Action Success: TRUE

        ** Turn 19 for red_agent_0 **
        Action: PrivilegeEscalate contractor_network_subnet_user_host_0
        Action Success: TRUE
        ```
    ---

> **=== "Output Actions Only" (행동만 출력) 탭**
>
> 정보에 압도당하지 않으면서 Red 에이전트가 무엇을 하고 있는지 감을 잡고 싶다면, 이 옵션이 적합합니다.
>
> 활성 상태인 Red 에이전트는 다음을 표시합니다.
>
> - 자신이 누구인지
> - 내부적으로 몇 번째 스텝(step)에 있는지
> - 그 스텝에서의 행동(Action)이 무엇이었는지
> - 그 행동이 얼마나 성공적이었는지
>
> 이를 통해 각 에이전트가 어떤 진척을 보이고 있는지, 어떤 에이전트가 활성 상태인지 쉽게 알 수 있습니다.
> (위 코드 출력은 `print_action_output == True`일 때의 결과입니다.)

=== "Output Actions and Observations"

    This option gives you all the output you would possibly need to determine why the agent is doing what it is doing.
    As well as showing you the action information and observation output (as discussed in the [previous tutorial](1_Observations.md#observable-hosts-dictionary)), the 'host states' dictionary is also displayed.

    The host states represent the agent's internal knowledge level for each host it is aware of. The host is identified via its IP address and given a state, which determines what future actions can be made on that state. For more information on this mechanism, look at the [reference agent design documentation](../../reference/agents/red_overview.md#finite-state-machine-based-red-agents).

    The output that you get for the initial observation, and first two steps are shown below:

    ??? quote "Code Output: print_obs_output && print_action_output == True"
        ```
        ** Turn 0 for red_agent_0 **
        Action: Initial Observation
        Action Success: UNKNOWN

        Observation:
        {'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                                                'interface_name': 'eth0',
                                                                'ip_address': IPv4Address('10.0.43.13')}],
                                                'Processes': [{'PID': 9298,
                                                                'username': 'ubuntu'}],
                                                'Sessions': [{'PID': 9298,
                                                                'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'timeout': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Architecture': <Architecture.x64: 2>,
                                                                'Hostname': 'contractor_network_subnet_user_host_5',
                                                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                                                'OSType': <OperatingSystemType.LINUX: 3>,
                                                                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                                                'position': array([0., 0.])},
                                                'User Info': [{'Groups': [{'GID': 0}],
                                                                'username': 'root'},
                                                                {'Groups': [{'GID': 1}],
                                                                'username': 'user'}]}}
        Host States:
        {'10.0.43.13': {'hostname': 'contractor_network_subnet_user_host_5',
                        'state': 'U'}}

        ** Turn 1 for red_agent_0 **
        Action: DiscoverRemoteSystems 10.0.43.0/24
        Action Success: TRUE

        Observation:
        {'10.0.43.129': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.129')}]},
        '10.0.43.13': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                    'ip_address': IPv4Address('10.0.43.13')}]},
        '10.0.43.130': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.130')}]},
        '10.0.43.143': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.143')}]},
        '10.0.43.224': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.224')}]},
        '10.0.43.251': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.251')}]},
        '10.0.43.252': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.252')}]},
        '10.0.43.253': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.253')}]},
        '10.0.43.254': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.254')}]},
        '10.0.43.61': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                    'ip_address': IPv4Address('10.0.43.61')}]},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                                                'ip_address': IPv4Address('10.0.43.13')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}}}
        Host States:
        {'10.0.43.129': {'hostname': None, 'state': 'K'},
        '10.0.43.13': {'hostname': 'contractor_network_subnet_user_host_5',
                        'state': 'UD'},
        '10.0.43.130': {'hostname': None, 'state': 'K'},
        '10.0.43.143': {'hostname': None, 'state': 'K'},
        '10.0.43.224': {'hostname': None, 'state': 'K'},
        '10.0.43.251': {'hostname': None, 'state': 'K'},
        '10.0.43.252': {'hostname': None, 'state': 'K'},
        '10.0.43.253': {'hostname': None, 'state': 'K'},
        '10.0.43.254': {'hostname': None, 'state': 'K'},
        '10.0.43.61': {'hostname': None, 'state': 'K'}}

        ** Turn 2 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.251
        Action Success: TRUE

        Observation:
        {'10.0.43.251': {'Interface': [{'ip_address': IPv4Address('10.0.43.251')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 3390}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 80}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 25}]}]},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                                                'ip_address': IPv4Address('10.0.43.13')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}}}
        Host States:
        {'10.0.43.129': {'hostname': None, 'state': 'K'},
        '10.0.43.13': {'hostname': 'contractor_network_subnet_user_host_5',
                        'state': 'UD'},
        '10.0.43.130': {'hostname': None, 'state': 'K'},
        '10.0.43.143': {'hostname': None, 'state': 'K'},
        '10.0.43.224': {'hostname': None, 'state': 'K'},
        '10.0.43.251': {'hostname': None, 'state': 'S'},
        '10.0.43.252': {'hostname': None, 'state': 'K'},
        '10.0.43.253': {'hostname': None, 'state': 'K'},
        '10.0.43.254': {'hostname': None, 'state': 'K'},
        '10.0.43.61': {'hostname': None, 'state': 'K'}}
        ```
    ---

> **=== "Output Actions and Observations" (행동과 관찰값 함께 출력) 탭**
>
> 이 옵션은 에이전트가 왜 그런 행동을 하는지 판단하는 데 필요한 모든 출력을 제공합니다.
> 행동 정보와 관찰값(Observation) 출력([이전 튜토리얼](1_Observations.md#observable-hosts-dictionary)에서 다룬 내용)에 더해, 'host states'(호스트 상태) 딕셔너리도 함께 표시됩니다.
>
> host states는 에이전트가 인지하고 있는 각 호스트에 대한 내부 지식 수준을 나타냅니다. 각 호스트는 IP 주소로 식별되며, 상태(state)가 부여됩니다. 이 상태에 따라 해당 호스트에 어떤 후속 행동을 할 수 있는지가 결정됩니다. 이 메커니즘에 대한 자세한 내용은 [에이전트 설계 레퍼런스 문서](../../reference/agents/red_overview.md#finite-state-machine-based-red-agents)를 참고하세요.
>
> 초기 관찰값(initial observation)과 처음 두 스텝(step)에 대한 출력은 위와 같습니다.
> (위 코드 출력은 `print_obs_output && print_action_output == True`일 때의 결과입니다.)

For the basic prioritisation option, you can choose to set the agent to prefer servers.

> 기본 우선순위 지정(prioritisation) 옵션에서는, 에이전트가 서버(server)를 우선하도록 설정할 수 있습니다.

**Why:**
Impact is only successful on servers that run a specific operational service. Therefore, if you want the agent to focus on impacting as many servers as possible, prioritising servers is necessarty.

> **이유(Why):**
> Impact(타격)은 특정 운영 서비스를 실행 중인 서버에서만 성공합니다. 따라서 에이전트가 가능한 한 많은 서버에 타격을 집중하길 원한다면, 서버를 우선하도록 설정하는 것이 필요합니다.

**How:**
If a server is known by the agent, there will be a 75% chance that the next action will happen on a server.

> **방법(How):**
> 에이전트가 어떤 서버를 알고 있다면, 다음 행동이 그 서버에서 일어날 확률은 75%가 됩니다.

The source code for how this is achieved is shown below:

> 이를 구현하는 소스 코드는 아래와 같습니다.

```python title="FiniteStateRedAgent.py" linenums="265"
if self.prioritise_servers and len(state_host_options) > 1:
    server_state_host_options = [h for h in state_host_options if self.host_states[h]['hostname'] is not None and 'server' in self.host_states[h]['hostname']] 
    if len(server_state_host_options) > 0:
        i = self.np_random.random()
        if i <= 0.75:
            chosen_host = self.np_random.choice(server_state_host_options)
        else:
            #pick other host type
            if not len(server_state_host_options) == len(state_host_options):
                non_server_state_host_options = [h for h in state_host_options if not h in server_state_host_options]
                chosen_host = self.np_random.choice(non_server_state_host_options)
            else:
                chosen_host = self.np_random.choice(server_state_host_options)
    else:
        chosen_host = self.np_random.choice(state_host_options)
else:
    chosen_host = self.np_random.choice(state_host_options)
```
## Blue Agents (Blue 에이전트)
The objective for competitors in CC4 is to create the best Blue agent possible. As such, there are no Blue agents provided in CC4.

> CC4 참가자의 목표는 가능한 한 최고의 Blue 에이전트(방어 측)를 만드는 것입니다. 그렇기 때문에 CC4에는 미리 제공되는 Blue 에이전트가 없습니다.

## Other Agents (그 밖의 에이전트)
### Keyboard Agent

The KeyboardAgent allows a person to manually choose actions, acting as the brains of the agent. This is useful for getting familiar the scenario. However, the observation space is given in its raw dictionary form, which means that it can be hard to follow what is happening when given a large observation.

> `KeyboardAgent`는 사람이 직접 행동(Action)을 골라 에이전트의 두뇌 역할을 하도록 해 줍니다. 시나리오(Scenario)에 익숙해지는 데 유용합니다. 다만 관찰 공간(observation space)이 가공되지 않은 원본 딕셔너리 형태로 주어지기 때문에, 관찰값(Observation)이 클 때는 무슨 일이 일어나는지 따라가기 어려울 수 있습니다.

Here is how you would use it:

> 사용 방법은 다음과 같습니다.

```python title="keyboard_agent_example.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent, KeyboardAgent

steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, # use a stand-in agent that you will overwrite the actions of
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Create the keyboard agent
agent = KeyboardAgent('blue_agent_0')
# Reset the environment
results = cyborg.reset()

for i in range(3):
    # Get the action and observation space
    obs = results.observation
    action_space = cyborg.get_action_space('blue_agent_0')

    # Prompt the keyboard agent to ask yoy for the action to take
    action = agent.get_action(obs, action_space)
    # Take a step using that action
    results = cyborg.step(agent='blue_agent_0', action=action)
```

And here is a snip-it of the output:

> 그리고 출력의 일부는 다음과 같습니다.

???+ quote "Code Output"
    ```
                                ...
                            'User Info': [{'Groups': [{'GID': 0}],
                                            'username': 'root'},
                                            {'Groups': [{'GID': 1}],
                                            'username': 'user'}]},
    'success': <TernaryEnum.UNKNOWN: 2>}

    ********************************* Turn 1: Command Selection **********************************

    0 AllowTrafficZone
    1 BlockTrafficZone
    2 Restore_cc4
    3 Remove_cc4
    4 DecoyHarakaSMPT_cc4
    5 DecoyApache_cc4
    6 DecoyTomcat_cc4
    7 DecoyVsftpd_cc4
    8 Analyse_cc4
    9 Monitor
    10 Sleep
    ----------------------------------------------------------------------------------------------
    CHOOSE A COMMAND: 5
    You chose DecoyApache_cc4.


    ******************************** Turn 1: Parameter Selection *********************************


    ------------------------------------- Session Selection --------------------------------------
    Automatically choosing 0 as it is the only option.
    -------------------------------------- Agent Selection ---------------------------------------
    Automatically choosing blue_agent_0 as it is the only option.
    ------------------------------------- Hostname Selection -------------------------------------
    0 restricted_zone_a_subnet_router
    1 restricted_zone_a_subnet_user_host_0
    2 restricted_zone_a_subnet_user_host_1
    3 restricted_zone_a_subnet_user_host_2
    4 restricted_zone_a_subnet_user_host_3
    5 restricted_zone_a_subnet_user_host_4
    6 restricted_zone_a_subnet_server_host_0
    7 restricted_zone_a_subnet_server_host_1
    8 restricted_zone_a_subnet_server_host_2
    ----------------------------------------------------------------------------------------------
    CHOOSE A PARAMETER: 5
    You chose restricted_zone_a_subnet_user_host_4.
    ----------------------------------------------------------------------------------------------
    ----------------------------------------------------------------------------------------------

    ************************************ Turn 2: BLUE_AGENT_0 ************************************

    ----------------------------------------------------------------------------------------------
    ----------------------------------------------------------------------------------------------

    ************************************ Turn 2: Observation *************************************

    {'success': <TernaryEnum.IN_PROGRESS: 4>}
    ----------------------------------------------------------------------------------------------
    Action is still executing...
    **********************************************************************************************
    ```
