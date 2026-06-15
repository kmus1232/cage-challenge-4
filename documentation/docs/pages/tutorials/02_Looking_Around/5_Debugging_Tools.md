# Debugging Tools (디버깅 도구)

## The True State (실제 상태)

In order to help users understand what is going on, it is necessary to be able to pull out the true state of the network at any time. This is obtained by calling the `get_agent_state` method and passing in agent's name. 

> 사용자가 환경에서 무슨 일이 벌어지고 있는지 이해하도록 돕기 위해서는, 언제든 네트워크의 **실제 상태(true state)**를 꺼내 볼 수 있어야 합니다. 이 값은 `get_agent_state` 메서드를 호출하면서 에이전트 이름을 넘겨주면 얻을 수 있습니다.

```python title="debugging_tools_example.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent


seed = 1234
sg = EnterpriseScenarioGenerator(
    blue_agent_class=SleepAgent,
    green_agent_class=EnterpriseGreenAgent,
    red_agent_class=FiniteStateRedAgent,
    steps=100
)
cyborg = CybORG(scenario_generator=sg, seed=seed)
cyborg.reset()

true_state = cyborg.get_agent_state('red_agent_0')
pprint(true_state)
```

??? quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_2': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
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
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

Red's observation is relatively readable, however as Blue and Green have larger observation spaces it can be better to visualise this data as a table.

> Red 에이전트(공격 측)의 관찰값(Observation)은 비교적 읽기 쉽지만, Blue 에이전트(방어 측)와 Green 에이전트(정상 사용자)는 관찰 공간이 더 크기 때문에 이 데이터를 표 형태로 시각화하는 편이 나을 수 있습니다.

The [TrueStateTableWrapper](3_Wrappers.md#truestatetablewrapper) can show you how to use this wrapper to get out more information about the true state of the environment.

> [TrueStateTableWrapper](3_Wrappers.md#truestatetablewrapper) 문서에서 이 래퍼(Wrapper)를 사용해 환경의 실제 상태에 대한 정보를 더 풍부하게 꺼내는 방법을 확인할 수 있습니다.

## Other Debugging Tools (그 밖의 디버깅 도구)

CybORG has a host of other tools to help understand the agent state. 

> CybORG(Cyber Operations Research Gym)에는 에이전트 상태를 이해하는 데 도움이 되는 여러 가지 다른 도구가 마련되어 있습니다.

### Get Observation (관찰값 가져오기)

You can use the `get_observation` method instead of examining the return from `step` or `parallel_step` functions.

> `step`이나 `parallel_step` 함수의 반환값을 일일이 살펴보는 대신, `get_observation` 메서드를 사용할 수 있습니다.

```python title="debugging_tools_example.py" linenums="21"

cyborg.step()

obs = cyborg.get_observation('red_agent_0')
pprint(obs)
```


??? quote "Code Output"
    ```
    {'10.0.74.157': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.157')}]},
    '10.0.74.171': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.171')}]},
    '10.0.74.183': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.183')}]},
    '10.0.74.241': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.241')}]},
    '10.0.74.252': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.252')}]},
    '10.0.74.253': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.253')}]},
    '10.0.74.254': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.254')}]},
    '10.0.74.39': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.39')}]},
    '10.0.74.45': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.45')}]},
    '10.0.74.49': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.49')}]},
    '10.0.74.72': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.72')}]},
    '10.0.74.95': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.95')}]},
    'action': DiscoverRemoteSystems 10.0.74.0/24,
    'contractor_network_subnet_user_host_2': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                                            'ip_address': IPv4Address('10.0.74.39')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_2'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

Here you can see the observation that `red_agent_0` gained from its last action `DiscoverRemoteSystems`.

> 여기서 `red_agent_0`가 마지막 행동(Action)인 `DiscoverRemoteSystems`(원격 시스템 탐색)를 통해 얻은 관찰값을 확인할 수 있습니다.

### Get Last Action (마지막 행동 가져오기)

We have also seen the `get_last_action` method.

> 앞서 `get_last_action` 메서드도 살펴본 적이 있습니다.

```python title="debugging_tools_example.py" linenums="26"
red_last_action = cyborg.get_last_action('red_agent_0')
green_last_action = cyborg.get_last_action('green_agent_0')
blue_last_action = cyborg.get_last_action('blue_agent_0')

print("red_agent_0 last action: ", red_last_action)
print("green_agent_0 last action: ", green_last_action)
print("blue_agent_0 last action: ", blue_last_action)
```

???+ quote "Code Output"
    ```
    red_agent_0 last action:  [DiscoverRemoteSystems 10.0.74.0/24]
    green_agent_0 last action:  [GreenLocalWork 10.0.26.88]
    blue_agent_0 last action:  [Sleep]
    ```

Note that though blue agent's last action is Sleep, blue has also run its default action 'Monitor'. However, due to it being run every time it is not displayed.

> Blue 에이전트의 마지막 행동은 Sleep으로 표시되지만, Blue는 기본 행동인 'Monitor'(모니터링)도 함께 실행했다는 점에 유의하세요. 다만 Monitor는 매 스텝(step)마다 실행되기 때문에 따로 표시되지 않습니다.

### Get Action Space (행동 공간 가져오기)

The `get_action_space` method allows us to get the action space of any agent. This is space is quite large, so only the keys are printed in this example.

> `get_action_space` 메서드를 사용하면 어떤 에이전트든 그 행동 공간(Action Space)을 가져올 수 있습니다. 이 공간은 상당히 크기 때문에, 이 예제에서는 키(keys)만 출력합니다.

```python title="debugging_tools_example.py" linenums="34"
red_action_space = cyborg.get_action_space('red_agent_0')
print(list(red_action_space.keys()))
```

???+ quote "Code Output"
    ```
    ['action', 'allowed_subnets', 'subnet', 'ip_address', 'session', 'username', 'password', 'process', 'port', 'target_session', 'agent', 'hostname']
    ```

### Get IP Addresses Map (IP 주소 맵 가져오기)

The `get_ip_map` method allows us to see which hostnames are associated with each ip. 

> `get_ip_map` 메서드를 사용하면 어떤 호스트 이름(hostname)이 각 IP와 연결되어 있는지 확인할 수 있습니다.

???+ info "Remember"
    Blue agents are aware of the whole network from the start, however red finds out more depending on its actions.

    [한국어] Blue 에이전트(방어 측)는 처음부터 네트워크 전체를 알고 있지만, Red 에이전트(공격 측)는 자신의 행동에 따라 점점 더 많은 정보를 알아냅니다.

The CC4 scenario has a large number of hosts, so a smaller subsection is shown in the example.

> CC4 시나리오에는 호스트가 매우 많기 때문에, 예제에서는 그중 일부만 추려서 보여 줍니다.

```python title="debugging_tools_example.py" linenums="37"
ip_map = cyborg.get_ip_map()
router_ip_maps = {host: ip for host, ip in ip_map.items() if 'router' in host}
pprint(router_ip_maps)
```

???+ quote "Code Output"
    ```
    {'admin_network_subnet_router': IPv4Address('10.0.90.243'),
    'contractor_network_subnet_router': IPv4Address('10.0.74.121'),
    'office_network_subnet_router': IPv4Address('10.0.32.51'),
    'operational_zone_a_subnet_router': IPv4Address('10.0.27.208'),
    'operational_zone_b_subnet_router': IPv4Address('10.0.183.241'),
    'public_access_zone_subnet_router': IPv4Address('10.0.177.163'),
    'restricted_zone_a_subnet_router': IPv4Address('10.0.26.209'),
    'restricted_zone_b_subnet_router': IPv4Address('10.0.86.23')}
    ```

### Get Rewards (보상 가져오기)

The `get_rewards` method allows us to see the rewards for all agents.

> `get_rewards` 메서드를 사용하면 모든 에이전트의 보상(Reward)을 확인할 수 있습니다.

```python title="debugging_tools_example.py" linenums="41"
rewards = cyborg.get_rewards()
pprint(rewards)
```
???+ quote "Code Output"
    ```
    {'Blue': {'BlueRewardMachine': 0, 'action_cost': 0},
    'Green': {'None': 0.0, 'action_cost': 0},
    'Red': {'None': 0.0, 'action_cost': 0}}
    ```

