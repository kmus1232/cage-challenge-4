# Observations (관찰값)
The observation space is one of the main outputs that an agent gets from the environment, as it tells the agent all that it can sense happening in the environment. It is therefore important to understand the output - especially when making your own wrapper.

> 관찰 공간(observation space)은 에이전트가 환경(environment)으로부터 받는 주요 출력 중 하나입니다. 환경에서 일어나는 일 중 에이전트가 감지할 수 있는 모든 것을 알려주기 때문입니다. 따라서 이 출력을 이해하는 것이 중요하며, 특히 직접 래퍼(Wrapper)를 만들 때 더욱 그렇습니다.

## Active Agents (활성 에이전트)
Not all agents are active every step. If an agent is not active its observation space will not be accurate and it will not be able to take any actions.

> 모든 에이전트가 매 스텝(step)마다 활성 상태인 것은 아닙니다. 어떤 에이전트가 활성 상태가 아니라면 그 에이전트의 관찰 공간은 정확하지 않으며, 어떠한 행동(Action)도 취할 수 없습니다.

You can check what agents are active in the environment by checking the variable `active_agents` in the `CybORG` class.

> 환경에서 어떤 에이전트가 활성 상태인지는 `CybORG` 클래스의 `active_agents` 변수를 확인해서 알 수 있습니다.

Here is an example:

> 다음은 그 예시입니다.

```python title="active_agents.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

cyborg.reset()

print(cyborg.active_agents)
```
???+ quote "Code Output"
    ```
    [
        'blue_agent_0', 'blue_agent_1', 'blue_agent_2', 'blue_agent_3', 
        'blue_agent_4', 
        
        'green_agent_0', 'green_agent_1', 'green_agent_2', 'green_agent_3',
        'green_agent_4', 'green_agent_5', 'green_agent_6', 'green_agent_7', 
        'green_agent_8', 'green_agent_9', 'green_agent_10', 'green_agent_11', 
        'green_agent_12', 'green_agent_13', 'green_agent_14', 'green_agent_15',
        'green_agent_16', 'green_agent_17', 'green_agent_18', 'green_agent_19', 
        'green_agent_20', 'green_agent_21', 'green_agent_22', 'green_agent_23', 
        'green_agent_24', 'green_agent_25', 'green_agent_26', 'green_agent_27', 
        'green_agent_28', 'green_agent_29', 'green_agent_30', 'green_agent_31', 
        'green_agent_32', 'green_agent_33', 'green_agent_34', 'green_agent_35', 
        'green_agent_36', 'green_agent_37', 'green_agent_38', 'green_agent_39', 
        'green_agent_40', 'green_agent_41', 'green_agent_42', 'green_agent_43', 
        'green_agent_44', 'green_agent_45', 'green_agent_46', 'green_agent_47', 
        
        'red_agent_0'
    ]
    ```

You can see at the initialisation of this environment, there are:

- all 5 blue agent active, 
- all 48 green agents active, and 
- only 1 of the red agents active.

> 이 환경의 초기화 시점에 다음과 같은 상태임을 알 수 있습니다.
>
> - Blue 에이전트(방어 측) 5개 전체가 활성 상태이고,
> - Green 에이전트(정상 사용자) 48개 전체가 활성 상태이며,
> - Red 에이전트(공격 측)는 단 1개만 활성 상태입니다.

There are always 6 red agents and 5 blue agents in an environment, but the number of green agents depends in the number of hosts - which is dynamic in environment and depends on the environmental seed.

> 환경에는 항상 Red 에이전트 6개와 Blue 에이전트 5개가 있지만, Green 에이전트의 수는 호스트(Host) 수에 따라 달라집니다. 호스트 수는 환경마다 동적으로 정해지며 환경 시드(seed)에 따라 결정됩니다.

The environment will always start with only 1 active red agent, `red_agent_0`, located in the contractor network.

> 환경은 항상 협력업체 네트워크(Contractor network)에 위치한 `red_agent_0` 하나만 활성 Red 에이전트로 둔 채 시작됩니다.

## Red Observations (Red 에이전트의 관찰값)
### Initial Observation (초기 관찰값)

We will begin by instantiating CybORG and looking at `red_agent_0`'s initial observation.

> 먼저 CybORG를 인스턴스화하고 `red_agent_0`의 초기 관찰값을 살펴보는 것으로 시작하겠습니다.

```python title="cc4_red_observations.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent
from CybORG.Simulator.Actions.AbstractActions import PrivilegeEscalate

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

reset = cyborg.reset(agent='red_agent_0')
first_session_host = list(reset.observation.keys())[1]
initial_obs = reset.observation

print("\nRed Agent 0: Initial Observation \n")
pprint(initial_obs)

```

???+ quote "Code Output"
    ```
    Red Agent 0: Initial Observation 

    {
        'contractor_network_subnet_user_host_2': {
            'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.74.39')}],
            'Processes': [{'PID': 9267,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9267,
                            'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                            'agent': 'red_agent_0',
                            'session_id': 0,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'contractor_network_subnet_user_host_2',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'success': <TernaryEnum.UNKNOWN: 2>
    }
    ```

The dictionary above has two keys: 

- `success` 
- `contractor_network_subnet_user_host_2` 

> 위 딕셔너리에는 두 개의 키가 있습니다.
>
> - `success`
> - `contractor_network_subnet_user_host_2`

The `success` value indicates whether the previous action ran successfully, or whether it encountered an error. 
Since this is the start of the scenario, the success value is set to UNKNOWN.

> `success` 값은 직전 행동(Action)이 성공적으로 실행되었는지, 아니면 오류를 만났는지를 나타냅니다. 지금은 시나리오의 시작 시점이므로 success 값은 UNKNOWN으로 설정되어 있습니다.

The key `contractor_network_subnet_user_host_2` is a host identifier, indicating its corresponding value is data about that host. 
Here the host identifier is equal to the name of the host, although this can also be ip addresses depending on the previous action.

> `contractor_network_subnet_user_host_2` 키는 호스트 식별자이며, 그에 대응하는 값이 해당 호스트에 대한 데이터임을 나타냅니다. 여기서는 호스트 식별자가 호스트 이름과 같지만, 직전 행동에 따라 IP 주소가 될 수도 있습니다.

???+ Tip "Having trouble reading the outputs?"
    Due to the complex nature of computer security, CybORG's raw observations contain a lot of information presented in a standardised format which takes the form of a series of nested dictionaries and lists. It is recommended that you use `prettyprint` whenever printing a CybORG observation.

    출력을 읽기 어렵나요? 컴퓨터 보안은 본질적으로 복잡하기 때문에, CybORG의 원시(raw) 관찰값에는 표준화된 형식으로 표현된 많은 정보가 담겨 있으며, 그 형식은 중첩된 딕셔너리와 리스트가 연달아 이어진 형태입니다. CybORG 관찰값을 출력할 때는 언제나 `prettyprint`를 사용하기를 권장합니다.

### Observable Host's Dictionary (관찰 가능한 호스트 딕셔너리)
Take a closer look at the `contractor_network_subnet_user_host_2` dictionary, shown in the code output.

> 코드 출력에 표시된 `contractor_network_subnet_user_host_2` 딕셔너리를 좀 더 자세히 살펴보겠습니다.

```
{
    'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                    'interface_name': 'eth0',
                    'ip_address': IPv4Address('10.0.74.39')}],
    'Processes': [{'PID': 9267,
                    'username': 'ubuntu'}],
    'Sessions': [{'PID': 9267,
                    'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                    'agent': 'red_agent_0',
                    'session_id': 0,
                    'timeout': 0,
                    'username': 'ubuntu'}],
    'System info': {'Architecture': <Architecture.x64: 2>,
                    'Hostname': 'contractor_network_subnet_user_host_2',
                    'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                    'OSType': <OperatingSystemType.LINUX: 3>,
                    'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                    'position': array([0., 0.])},
    'User Info': [{'Groups': [{'GID': 0}],
                    'username': 'root'},
                    {'Groups': [{'GID': 1}],
                    'username': 'user'}]}
```

The `contractor_network_subnet_user_host_2` dictionary contains various information about the host, that the red agent knows about. 

> `contractor_network_subnet_user_host_2` 딕셔너리에는 Red 에이전트가 알고 있는 해당 호스트에 대한 다양한 정보가 담겨 있습니다.

- `Interface` gives us networking information such as the host's IP address and subnet.

- `Processes` lets us know any external facing processes running on the host that the red agent knows about.

- `Sessions` lets us know any sessions is aware of, especially shells. 

- `System info` tells us information about the general system and operating system.

- `User Info` gives the different users avaliable on the system, usually 'root' and 'user'.

> - `Interface`(인터페이스)는 호스트의 IP 주소와 서브넷(Subnet) 같은 네트워크 정보를 알려줍니다.
>
> - `Processes`(프로세스)는 Red 에이전트가 알고 있는, 호스트에서 실행 중인 외부 노출(external facing) 프로세스를 알려줍니다.
>
> - `Sessions`(세션)는 인지하고 있는 세션, 특히 셸(shell)을 알려줍니다.
>
> - `System info`(시스템 정보)는 시스템 전반과 운영체제에 대한 정보를 알려줍니다.
>
> - `User Info`(사용자 정보)는 시스템에 존재하는 여러 사용자(보통 'root'와 'user')를 알려줍니다.

You may notice that `Interface`, `Processes` and `Sessions` all have lists as values. This is because a host can and usually will have multiple of these running at the same time.

> `Interface`, `Processes`, `Sessions`의 값이 모두 리스트(list)라는 점을 눈치챘을 수 있습니다. 이는 호스트가 이들을 동시에 여러 개 가질 수 있고, 보통 실제로도 그렇기 때문입니다.

### Level of Red Control over Host (Red 에이전트의 호스트 제어 수준)
When a red agent has a session on a host, it can have either a user or root privilege level access. In order to perform actions that affect the performance of the host, root level access is needed.

> Red 에이전트가 호스트에 세션(Session)을 가지고 있을 때, 그 접근 권한은 user(사용자) 수준이거나 root(루트) 수준일 수 있습니다. 호스트의 성능에 영향을 주는 행동을 수행하려면 root 수준의 접근 권한이 필요합니다.

Getting from user to root level access can be done in CC4 by using the PrivilegeEscalate action - which is further demonstrated in the [privilege escalate action tutorial](../03_Actions/C_Red_Actions/5_Privilege_Escalate.md). 

> CC4에서 user 수준에서 root 수준 접근 권한으로 올라가는 것은 PrivilegeEscalate(권한 상승) 행동을 사용해서 할 수 있으며, 이는 [권한 상승 행동 튜토리얼](../03_Actions/C_Red_Actions/5_Privilege_Escalate.md)에서 더 자세히 다룹니다.

```python title="cc4_red_observations.py" linenums="21"
first_action = PrivilegeEscalate(hostname=first_session_host, session=0, agent='red_agent_0')
results = cyborg.step(agent='red_agent_0', action=first_action)
first_action_obs = results.observation

print("\nRed Agent 0: Observation #1 \n")
pprint(first_action_obs)
```

Let's compare the observation data before and after a successful PrivilegeEscalate action, using the code above:

> 위 코드를 사용해, PrivilegeEscalate 행동이 성공하기 전과 후의 관찰 데이터를 비교해 보겠습니다.

=== "Initial Observation (초기 관찰값)"
    ???+ quote "Code Output"
        ```
        Red Agent 0: Initial Observation 

        {
            'contractor_network_subnet_user_host_2': 
                {
                    'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'interface_name': 'eth0',
                                    'ip_address': IPv4Address('10.0.74.39')}],
                    'Processes': [{'PID': 9267,
                                    'username': 'ubuntu'}],
                    'Sessions': [{'PID': 9267,
                                    'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                    'agent': 'red_agent_0',
                                    'session_id': 0,
                                    'timeout': 0,
                                    'username': 'ubuntu'}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'contractor_network_subnet_user_host_2',
                                    'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                    'position': array([0., 0.])},
                    'User Info': [{'Groups': [{'GID': 0}],
                                    'username': 'root'},
                                    {'Groups': [{'GID': 1}],
                                    'username': 'user'}]
                },
            'success': <TernaryEnum.UNKNOWN: 2>
        }

        ```
    ---

=== "Observation #1 (관찰값 #1)"
    ???+ quote "Code Output"
        ```
        Red Agent 0: Observation #1 

        {
            'action': PrivilegeEscalate contractor_network_subnet_user_host_2,
            'contractor_network_subnet_user_host_2': 
                {
                    'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.39')}],
                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                    'agent': 'red_agent_0',
                                    'session_id': 0,
                                    'username': 'root'}],
                    'System info': {'Hostname': 'contractor_network_subnet_user_host_2'}
                },
            'success': <TernaryEnum.TRUE: 1>
        }
        ```
    ---

The way to tell the current privileges is by looking at the session username. If the username is `root` it has root level access, otherwise it has user level access.

> 현재 권한 수준을 알아내는 방법은 세션의 username을 확인하는 것입니다. username이 `root`이면 root 수준 접근 권한을 가진 것이고, 그렇지 않으면 user 수준 접근 권한을 가진 것입니다.


## Blue Observations (Blue 에이전트의 관찰값)
### Initial Blue Observation (Blue 에이전트의 초기 관찰값)
For the initial observation space of a blue agent, it sees all the hosts that it is in-charge of protecting.
This initial observation is large, so we will initially only print out the keys.

> Blue 에이전트의 초기 관찰 공간에서는, 자신이 보호를 담당하는 모든 호스트를 볼 수 있습니다. 이 초기 관찰값은 크기 때문에, 처음에는 키(key)만 출력해 보겠습니다.

```python title="cc4_blue_observations.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Sleep

steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

reset = cyborg.reset(agent='blue_agent_0')
initial_obs = reset.observation

print("\nBlue Agent 0: Initial Observation")
print("\nKeys Only: \n")
pprint(initial_obs.keys())
```
???+ quote "Code Output"
    ```
    Blue Agent 0: Initial Observation

    Keys Only: 

    dict_keys([
        'success', 'restricted_zone_a_subnet_router', 'restricted_zone_a_subnet_user_host_0', 
        'restricted_zone_a_subnet_user_host_1', 'restricted_zone_a_subnet_user_host_2', 
        'restricted_zone_a_subnet_user_host_3', 'restricted_zone_a_subnet_user_host_4', 
        'restricted_zone_a_subnet_server_host_0', 'restricted_zone_a_subnet_server_host_1', 
        'restricted_zone_a_subnet_server_host_2'
    ])
    ```
From this output, we can tell that `blue_agent_0` is in-charge of protecting the restricted zone A subnet.

> 이 출력을 통해 `blue_agent_0`가 restricted zone A 서브넷(restricted zone A subnet)의 보호를 담당하고 있음을 알 수 있습니다.

When printing out the observation contents of the first host, we can see it has the same keys as in the [red observation](#observable-hosts-dictionary). 
But this time with a blue agent user session.

> 첫 번째 호스트의 관찰값 내용을 출력해 보면, [Red 에이전트의 관찰값](#observable-hosts-dictionary)과 동일한 키를 가지고 있음을 알 수 있습니다. 다만 이번에는 Blue 에이전트의 user 세션이 들어 있습니다.

```python linenums="20"
print("\nSingle Host: \n")
pprint(initial_obs[list(initial_obs.keys())[2]])
```
???+ quote "Code Output"
    ```
    Single Host: 

    {'Interface': [{'Subnet': IPv4Network('10.0.26.0/24'),
                    'interface_name': 'eth0',
                    'ip_address': IPv4Address('10.0.26.88')}],
    'Processes': [{'PID': 7519, 'username': 'ubuntu'}],
    'Sessions': [{'PID': 7519,
                'Type': <SessionType.UNKNOWN: 1>,
                'agent': 'blue_agent_0',
                'session_id': 2,
                'timeout': 0,
                'username': 'ubuntu'}],
    'System info': {'Architecture': <Architecture.x64: 2>,
                    'Hostname': 'restricted_zone_a_subnet_user_host_0',
                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                    'OSType': <OperatingSystemType.LINUX: 3>,
                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                    'position': array([0., 0.])},
    'User Info': [{'Groups': [{'GID': 0}], 'username': 'root'},
                {'Groups': [{'GID': 1}], 'username': 'user'}]}
    ```

### Uneventful Steps (이벤트가 없는 스텝)

Blue agents do the Monitor action every step as their 'end of turn' action. 
This means that they get feedback from the environment on what is happening to the hosts they have visibility of.

> Blue 에이전트는 매 스텝마다 '턴 종료(end of turn)' 행동으로 Monitor(모니터링) 행동을 수행합니다. 이는 자신이 가시성을 가진 호스트들에서 무슨 일이 일어나고 있는지 환경으로부터 피드백을 받는다는 뜻입니다.

If no events are triggered, such as in the code below, nothing apart from the action and its success are returned in the observation space.

> 아래 코드처럼 아무 이벤트도 발생하지 않으면, 관찰 공간에는 행동(action)과 그 성공 여부(success) 외에 아무것도 반환되지 않습니다.

```python linenums="23"
obs_1 = cyborg.step(agent='blue_agent_0', action=Sleep()).observation

print("\nBlue Agent 0: Step #1 \n")
pprint(obs_1)
```
???+ quote "Code Output"
    ```
    Blue Agent 0: Step #1 

    {'action': Sleep, 'success': <TernaryEnum.UNKNOWN: 2>}
    ```
### Eventful Steps (이벤트가 있는 스텝)
When something does happen on a host that the blue agent has a session on, it can appear in its observation space.

> Blue 에이전트가 세션을 가지고 있는 호스트에서 무언가 실제로 일어나면, 그 내용이 관찰 공간에 나타날 수 있습니다.

In the example below, the false positive (fp) detection rate of the green agents have been set to `1.0` so that any action that could trigger a false positive security event will. This value can be set at any float but is usually set at 0.01.

> 아래 예시에서는 Green 에이전트의 오탐(false positive, fp) 탐지율을 `1.0`으로 설정해, 오탐 보안 이벤트를 유발할 수 있는 행동이라면 무엇이든 실제로 유발되도록 했습니다. 이 값은 임의의 실수(float)로 설정할 수 있지만 보통은 0.01로 설정합니다.

This means there is now a high likelihood that something will appear in the agent's observation ...

> 즉, 이제 에이전트의 관찰값에 무언가가 나타날 가능성이 높아진 상태입니다 ...

```python linenums="28"
for agent_name, ai in cyborg.environment_controller.agent_interfaces.items():
    if 'green' in agent_name and isinstance(ai.agent, EnterpriseGreenAgent):
        ai.agent.fp_detection_rate = 1.0

obs_2 = cyborg.step(agent='blue_agent_0', action=Sleep()).observation

print("\nBlue Agent 0: Step #2 with Green False Positive \n")
pprint(obs_2)
```
???+ quote "Code Output"
    ```
    Blue Agent 0: Step #2 with Green False Positive 

    {'action': Sleep,
    'restricted_zone_a_subnet_user_host_4': {'Interface': [{'ip_address': IPv4Address('10.0.26.104')}],
                                            'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.26.104'),
                                                                            'local_port': 58063}]}],
                                            'System info': {'Architecture': <Architecture.x64: 2>,
                                                            'Hostname': 'restricted_zone_a_subnet_user_host_4',
                                                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                            'OSType': <OperatingSystemType.LINUX: 3>,
                                                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                            'position': array([0., 0.])}},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

Just as in real-life, there may be false-positives or incorrect negatives. 
The monitor function may be triggered by green actions, as is the case in the code above, or it may miss a malicious red action.
It is the blue agents job to decide how it wants to react to these observations.

> 실제 현실에서와 마찬가지로, 오탐(false-positive)이나 잘못된 미탐(incorrect negative)이 있을 수 있습니다. 위 코드의 경우처럼 모니터링 기능이 Green 에이전트의 행동에 의해 유발될 수도 있고, 악의적인 Red 에이전트의 행동을 놓칠 수도 있습니다. 이러한 관찰값에 어떻게 대응할지 결정하는 것이 Blue 에이전트의 역할입니다.
