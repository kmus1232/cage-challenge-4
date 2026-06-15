# Service Discovery (서비스 탐색)
`Service Discovery` outputs all processes (which have services) on a known host.
This action is a prerequisite for getting a shell on the host, as you must know about the services that exist before exploiting one of those services.

> `Service Discovery`(서비스 탐색)는 이미 알고 있는 호스트(Host)에서 동작 중인,
> 서비스를 가진 모든 프로세스(Process)를 출력합니다. 이 행동(Action)은 해당
> 호스트에서 셸(shell)을 획득하기 위한 선행 조건입니다. 어떤 서비스를
> 익스플로잇(원격 서비스 공격)하려면 먼저 그 호스트에 어떤 서비스가 존재하는지
> 알아야 하기 때문입니다.

## Identify the Host IP (호스트 IP 식별)
In order to discover services on a host, we must first find that host. We will be investigating the host Red starts with knowledge of, so there is no need to conduct a [DiscoverRemoteSystems](1_Discover_Remote_Systems.md) action. We just need to look at Red's initial observations.

> 호스트에서 서비스를 탐색하려면 먼저 그 호스트를 찾아야 합니다. 여기서는 Red
> 에이전트(공격 측)가 처음부터 알고 있는 호스트를 조사할 것이므로,
> [DiscoverRemoteSystems](1_Discover_Remote_Systems.md)(원격 시스템 탐색)
> 행동을 수행할 필요가 없습니다. Red 에이전트의 초기 관찰값(Observation)만
> 살펴보면 됩니다.

```python title="red_service_discovery.py" linenums="1"
from pprint import pprint
from ipaddress import IPv4Network, IPv4Address

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import AggressiveServiceDiscovery, StealthServiceDiscovery, Sleep

sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=200)
cyborg = CybORG(scenario_generator=sg, seed=1000)
red_agent_name = 'red_agent_0'

reset = cyborg.reset(agent=red_agent_name)
initial_obs = reset.observation
pprint(initial_obs)
```
??? quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'interface_name': 'eth0',
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Processes': [{'PID': 5753,
                                                            'username': 'ubuntu'}],
                                            'Sessions': [{'PID': 5753,
                                                            'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'timeout': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Architecture': <Architecture.x64: 2>,
                                                            'Hostname': 'contractor_network_subnet_user_host_4',
                                                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                            'OSType': <OperatingSystemType.LINUX: 3>,
                                                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                            'position': array([0., 0.])},
                                            'User Info': [{'Groups': [{'GID': 0}],
                                                            'username': 'root'},
                                                            {'Groups': [{'GID': 1}],
                                                            'username': 'user'}]},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

Looking in `contractor_network_subnet_user_host_4`, the dictionary containing information about the Red's first known host, we can see its IP address, under `Interface` and `ip_address`: `IPv4Address('10.0.96.73')`. This is the host ip we will be investigating.

> Red 에이전트가 처음부터 알고 있는 호스트의 정보가 담긴 딕셔너리
> `contractor_network_subnet_user_host_4`를 보면, `Interface`와 `ip_address`
> 아래에서 해당 호스트의 IP 주소 `IPv4Address('10.0.96.73')`를 확인할 수
> 있습니다. 이것이 우리가 조사할 호스트 IP입니다.

## Aggressive VS Stealth Versions (Aggressive 방식과 Stealth 방식 비교)

There are two kinds of service discovery: Aggressive and Stealth. They both find the services present on the host, but Aggressive is faster and more likely to alert Blue, whereas Stealth is slower but less likely to alert Blue.

> 서비스 탐색에는 두 가지 종류, Aggressive(공격적)와 Stealth(은밀)가 있습니다.
> 둘 다 호스트에 존재하는 서비스를 찾아내지만, Aggressive는 더 빠른 대신 Blue
> 에이전트(방어 측)에게 탐지될 가능성이 높고, Stealth는 더 느린 대신 Blue
> 에이전트에게 탐지될 가능성이 낮습니다.

Some type of service discovery must always be run on a host before attempting any other actions, as it enables them (e.g. exploits, discover deceptions).

> 다른 어떤 행동(예: 익스플로잇, 기만 수단 탐색)을 시도하기 전에는 항상 호스트에
> 대해 어떤 형태로든 서비스 탐색을 먼저 실행해야 합니다. 서비스 탐색이 그러한
> 후속 행동을 가능하게 하기 때문입니다.

As shown in the results, the same services are detected with both types of service discovery.

> 결과에서 볼 수 있듯이, 두 종류의 서비스 탐색 모두 동일한 서비스를 탐지합니다.

=== "Aggressive Service Discovery"

    Here, we run the `AggressiveServiceDiscovery` action on the target host.

    > 여기서는 대상 호스트에 대해 `AggressiveServiceDiscovery` 행동을 실행합니다.

    ```python title="red_service_discovery.py" linenums="23"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.73'))
    results = cyborg.step(agent=red_agent_name, action=action)
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.73': {'Interface': [{'ip_address': IPv4Address('10.0.96.73')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 25}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 80}]}]},
        'action': AggressiveServiceDiscovery 10.0.96.73,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    The services are visible in the resulting observations within `10.0.96.73`, `Processes`, along with brief information about each, including their local address and port. In this case, these are as follows:

    > 결과 관찰값(Observation)의 `10.0.96.73` 안 `Processes`에서 서비스들이
    > 보이며, 각 서비스의 로컬 주소(local address)와 포트(Port) 등 간단한 정보가
    > 함께 표시됩니다. 이번 경우에는 다음과 같습니다.
    ```
    [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                        'local_port': 22}]},
    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                        'local_port': 25}]},
    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                        'local_port': 80}]}]
    ```

=== "Stealth Service Discovery"

    The Stealth version is carried out in exactly the same way as Aggressive, but with more time to wait for a response.

    > Stealth 방식은 Aggressive 방식과 완전히 동일한 방법으로 수행되지만, 응답을
    > 기다리는 데 더 많은 시간이 걸립니다.

    ```python title="red_service_discovery.py" linenums="27"
    action = StealthServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.73'))
    cyborg.step(agent=red_agent_name, action=action)
    cyborg.step(agent=red_agent_name, action=Sleep())
    cyborg.step(agent=red_agent_name, action=Sleep())
    cyborg.step(agent=red_agent_name, action=Sleep())
    results = cyborg.step(agent=red_agent_name, action=Sleep())
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.73': {'Interface': [{'ip_address': IPv4Address('10.0.96.73')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 25}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 80}]}]},
        'action': StealthServiceDiscovery 10.0.96.73,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

