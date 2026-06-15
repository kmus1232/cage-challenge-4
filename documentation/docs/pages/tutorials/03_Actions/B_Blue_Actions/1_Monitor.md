# Monitor (모니터링)

` Monitor` collects events on hosts and informs the Blue Agent. Events are limited to Network Connection events and Process Creation events.

> `Monitor`(모니터링)는 호스트에서 발생한 이벤트를 수집해 **Blue 에이전트**(방어 측)에게
> 알려줍니다. 수집되는 이벤트는 네트워크 연결(Network Connection) 이벤트와
> 프로세스 생성(Process Creation) 이벤트로 한정됩니다.

???+ tip
    The Monitor action runs _automatically_ at the end of each step and if a Blue Agent calls it, it will have no additional effect. 

    > Monitor 행동(Action)은 매 스텝(step)이 끝날 때 _자동으로_ 실행됩니다. 따라서
    > Blue 에이전트가 이 행동을 직접 호출하더라도 추가로 발생하는 효과는 없습니다.

## Understanding Blue's Network (Blue 네트워크 이해하기)
In CC4, the scenario is too vast for one blue agent to monitor everything happening and be able to respond.
Therefore the scenario is broken down into multiple networks that are connected to eachother; each with a blue agent.

> CC4(CAGE Challenge 4)에서는 시나리오(Scenario) 규모가 너무 커서 하나의 Blue 에이전트가
> 일어나는 모든 일을 감시하고 대응할 수 없습니다. 그래서 시나리오는 서로 연결된 여러
> 네트워크로 나뉘며, 각 네트워크마다 Blue 에이전트가 한 명씩 배치됩니다.

In this example we will look at what `blue_agent_0` has visibility over and can act on.

> 이 예제에서는 `blue_agent_0`이 어떤 범위를 관측할 수 있고 어디에 행동할 수 있는지
> 살펴봅니다.

```python title="blue_monitor_with_red.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor

sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=200)
cyborg = CybORG(scenario_generator=sg, seed=1000)
blue_agent_name = 'blue_agent_0'

reset = cyborg.reset(agent=blue_agent_name)
initial_obs = reset.observation

pprint(initial_obs)
```

??? quote "Code Output"
    ```
    {
        'restricted_zone_a_subnet_router': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.70')}],
            'Processes': [{'PID': 7,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 7,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 1,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_router',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                        {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_server_host_0': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.254')}],
            'Processes': [{'PID': 8263,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 8263,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 11,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_server_host_0',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_0': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.217')}],
            'Processes': [{'PID': 5243,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 5243,
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
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_1': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.210')}],
            'Processes': [{'PID': 9300,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9300,
                            'Type': <SessionType.VELOCIRAPTOR_SERVER: 8>,
                            'agent': 'blue_agent_0',
                            'session_id': 0,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_1',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_2': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.249')}],
            'Processes': [{'PID': 7061,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 7061,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 3,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_2',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_3': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.2')}],
            'Processes': [{'PID': 5707,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 5707,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 4,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_3',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_4': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.139')}],
            'Processes': [{'PID': 5956,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 5956,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 5,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_4',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_5': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.220')}],
            'Processes': [{'PID': 9148,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9148,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 6,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_5',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_6': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.150')}],
            'Processes': [{'PID': 9879,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9879,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 7,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_6',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_7': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.218')}],
            'Processes': [{'PID': 6681,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 6681,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 8,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_7',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_8': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.137')}],
            'Processes': [{'PID': 3109,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 3109,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 9,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_8',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_9': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.165')}],
            'Processes': [{'PID': 3557,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 3557,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 10,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_9',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'success': <TernaryEnum.UNKNOWN: 2>
    }
    ```
In `blue_agent_0`'s initial observation space (before any steps are taken), you can see all the hosts that it is responsible for.
As you can see, the observation space is quite large to accommodate for all the hosts and their details.

> `blue_agent_0`의 초기 관찰값(Observation) 공간(아직 어떤 스텝도 진행하지 않은 상태)에는
> 이 에이전트가 책임지는 모든 호스트가 나타납니다. 보다시피 모든 호스트와 그 세부 정보를
> 담아야 하므로 관찰값 공간은 상당히 큽니다.

The output shows that `'Subnet': IPv4Network('10.0.114.0/24'`, the network that `blue_agent_0` is responsible for, consists of 12 hosts in total. 
That is 10 user hosts (0-9), 1 server host, and a router. In this scenario, routers are seen as connective devices that provide a firewall to the network and can therefore not be taken control of by red. You can also tell by the naming convention of the hosts that this network is called 'Restricted Zone A'.

> 출력 결과를 보면 `blue_agent_0`이 책임지는 네트워크인 `'Subnet': IPv4Network('10.0.114.0/24'`는
> 총 12개의 호스트로 구성됩니다. 사용자 호스트 10개(0~9), 서버 호스트 1개, 그리고 라우터 1개입니다.
> 이 시나리오에서 라우터는 네트워크에 방화벽을 제공하는 연결 장치로 취급되며, 따라서 Red
> 에이전트(공격 측)가 장악할 수 없습니다. 또한 호스트 이름 규칙을 보면 이 네트워크의 이름이
> 'Restricted Zone A'(제한 구역 A)임을 알 수 있습니다.


## Monitoring the Subnet (서브넷 모니터링하기)

Here we execute the `Monitor` action in the first step, and collect events on the subnet.

> 여기서는 첫 번째 스텝에서 `Monitor` 행동을 실행해 서브넷(Subnet)에서 발생한 이벤트를
> 수집합니다.

Only events that have been raised on the current step will be visible to the blue agent. Past records of observations are not maintained.

> Blue 에이전트에게는 **현재 스텝에서 발생한 이벤트만** 보입니다. 과거 관찰값 기록은
> 유지되지 않습니다.

```python title="blue_monitor_with_red.py" linenums="20"
action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation          

print(f"Step count: {step}")
pprint(base_obs)
```

???+ quote "Code Output"
    ```
    Step count: 1
    {'action': Monitor, 'success': <TernaryEnum.TRUE: 1>}
    ```

The output shows that the action ran successfully, however there were no events to collect.

> 출력 결과를 보면 행동은 성공적으로 실행되었지만, 수집할 이벤트는 없었음을 알 수 있습니다.


## When Red makes a move ... (Red가 움직일 때 ...)
In this example, steps are taken until the previous agent observation is different from the current one - indicating that an event has been collected.

> 이 예제에서는 이전 스텝의 에이전트 관찰값과 현재 관찰값이 달라질 때까지(즉, 이벤트가
> 수집되었다는 신호가 나타날 때까지) 스텝을 진행합니다.

Due to green agents being sleep agents, we can assume red has caused the alert.

> Green 에이전트(정상 사용자)가 SleepAgent(아무 행동도 하지 않는 에이전트)로 설정되어 있으므로,
> 이 알림은 Red 에이전트가 일으켰다고 볼 수 있습니다.

The printed `Monitor` output returns the step where the red agent has broken out of the contractor network and has compromised a host on the blue agent's network.

> 출력된 `Monitor` 결과는 Red 에이전트가 협력업체 네트워크(Contractor network)를 뚫고 나와
> Blue 에이전트의 네트워크에 있는 호스트를 침해한 스텝을 보여줍니다.

```python title="blue_monitor_with_red.py" linenums="28"
new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

print(f"Step count: {step}")
pprint(new_obs)

```
??? quote "Code Output"
    ```
    Step count: 127
    {'action': Monitor,
    'restricted_zone_a_subnet_router': {'Interface': [{'ip_address': IPv4Address('10.0.114.254')}],
                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                    'remote_address': IPv4Address('10.0.96.73'),
                                    'remote_port': 3390}]}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'restricted_zone_a_subnet_router',
                                    'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                    'position': array([0., 0.])}},
    'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.114.254')}],
                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                    'remote_address': IPv4Address('10.0.96.73'),
                                    'remote_port': 3390}]},
                                {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                    'local_port': 3390,
                                    'remote_address': IPv4Address('10.0.96.73'),
                                    'remote_port': 49190}]},
                                    {'PID': 8264}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                    'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                    'position': array([0., 0.])}},
    'success': <TernaryEnum.TRUE: 1>}
    ```
The output tells us that at step 127, there were network connection events at both 'restricted_zone_a_subnet_router' and 'restricted_zone_a_subnet_server_host_0', as well as a process creation event on 'restricted_zone_a_subnet_server_host_0'.

> 출력 결과는 스텝 127에서 'restricted_zone_a_subnet_router'와
> 'restricted_zone_a_subnet_server_host_0' 양쪽 모두에 네트워크 연결 이벤트가 발생했고,
> 'restricted_zone_a_subnet_server_host_0'에서는 프로세스 생성 이벤트도 발생했음을 알려줍니다.

???+ tip "Hint"
    This output indicates that red has managed to get a user shell on host 'restricted_zone_a_subnet_server_host_0'.

    > 이 출력은 Red 에이전트가 'restricted_zone_a_subnet_server_host_0' 호스트에서 사용자
    > 셸(user shell)을 획득하는 데 성공했음을 시사합니다.

## Green False Positives (Green 에이전트로 인한 오탐)

While red agents are performing actions that may alert blue agents to their presence, green agents are also just trying to do their jobs.

> Red 에이전트가 자신의 존재를 Blue 에이전트에게 노출시킬 수 있는 행동을 하는 동안,
> Green 에이전트는 그저 자신의 일상 업무를 수행하고 있을 뿐입니다.

Green actions, though not malicious, have the chance to create misleading events for blue agents. These false positives are going to be explored in this example.

> Green 에이전트의 행동은 악의적이지 않지만, Blue 에이전트를 헷갈리게 만드는 이벤트를
> 일으킬 수 있습니다. 이 예제에서는 이러한 오탐(false positive, 정상 활동을 위협으로
> 잘못 인식하는 것)을 살펴봅니다.

To isolate the events caused by the Green Agent, the Red Agent is set to 'SleepAgent' and the `Monitor` function is executed, iterating through steps until there is an observation space change.

> Green 에이전트가 일으킨 이벤트만 분리해서 보기 위해, Red 에이전트를 'SleepAgent'로
> 설정한 뒤 `Monitor` 함수를 실행합니다. 그리고 관찰값 공간에 변화가 생길 때까지 스텝을
> 반복합니다.

```python title="blue_monitor_with_green.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
blue_action_space = cyborg.get_action_space(blue_agent_name)

action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation
new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

print(f"Step count: {step}")
pprint(new_obs)

```
???+ quote "Code Output"
    ```
    Step count: 51
    {'action': Monitor,
    'restricted_zone_a_subnet_user_host_6': {'Interface': [{'ip_address': IPv4Address('10.0.114.150')}],
                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.150'),
                                    'local_port': 56672}]}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'restricted_zone_a_subnet_user_host_6',
                                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                    'position': array([0., 0.])}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The action has executed successfully and found an event at step 51 on 'restricted_zone_a_subnet_user_host_6' that is caused by a green agent's action. 

> 행동이 성공적으로 실행되었고, 스텝 51에서 'restricted_zone_a_subnet_user_host_6'에 Green
> 에이전트의 행동으로 인해 발생한 이벤트가 발견되었습니다.

