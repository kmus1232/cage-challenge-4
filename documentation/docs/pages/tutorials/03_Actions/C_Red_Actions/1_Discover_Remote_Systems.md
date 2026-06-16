# Discover Remote Systems (원격 시스템 탐색)
`DiscoverRemoteSystems` outputs, in the red agent's observation space, the IP addresses of all other hosts in a subnet. 

> `DiscoverRemoteSystems`(원격 시스템 탐색)는 Red 에이전트(공격 측)의 관찰값(Observation) 공간에 해당 서브넷(Subnet) 안에 있는 다른 모든 호스트의 IP 주소를 출력합니다.

## Identify the Subnet (서브넷 식별하기)
To perform this action, we must first find a known subnet to investigate. We do this here by looking at Red's initial observations.

> 이 행동(Action)을 수행하려면, 먼저 조사할 대상이 될 **알려진 서브넷**을 찾아야 합니다. 여기서는 Red 에이전트의 초기 관찰값을 살펴보는 방법으로 서브넷을 찾습니다.

```python title="red_discover_remote_systems.py" linenums="1"
from pprint import pprint
from ipaddress import IPv4Network

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import DiscoverRemoteSystems

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
???+ quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_4': {
        'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
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

The observation space is a dictionary that contains with information about the hosts Red is currently aware of. In this situation, the only host that Red is aware of is `contractor_network_subnet_user_host_4`. 

> 관찰값 공간은 Red가 현재 인지하고 있는 호스트들의 정보를 담은 딕셔너리(dictionary)입니다. 이 상황에서 Red가 인지하고 있는 유일한 호스트는 `contractor_network_subnet_user_host_4` 하나뿐입니다.

You can tell from the `Sessions` dictionary that this red is not only aware of this host, but also has a user shell on the host. However, having a shell on the host is not necessary for the Discover Remote Systems action to be valid. 

> `Sessions` 딕셔너리를 보면, 이 Red가 해당 호스트를 인지하고 있을 뿐 아니라 그 호스트에 **사용자 셸(user shell)**까지 확보하고 있음을 알 수 있습니다. 다만, 원격 시스템 탐색(Discover Remote Systems) 행동이 유효하기 위해 호스트에 셸을 가지고 있어야 하는 것은 아닙니다.

In the `Interface` and `Subnet` dictionaries is written the subnet that the host exists in: `IPv4Network('10.0.96.0/24')`. This is the subnet we will be investigating.

> `Interface`와 `Subnet` 딕셔너리에는 이 호스트가 속한 서브넷이 적혀 있습니다: `IPv4Network('10.0.96.0/24')`. 바로 이 서브넷이 우리가 조사할 대상입니다.

## Discover Hosts on the Subnet (서브넷의 호스트 탐색하기)
To discover the rest of the hosts on this host's subnet, `IPv4Network('10.0.96.0/24')`, we must run the `DiscoverRemoteSystems` action on the subnet, as shown below.

> 이 호스트가 속한 서브넷 `IPv4Network('10.0.96.0/24')`의 나머지 호스트들을 탐색하려면, 아래와 같이 해당 서브넷에 대해 `DiscoverRemoteSystems` 행동을 실행해야 합니다.

```python title="red_discover_remote_systems.py" linenums="20"
action = DiscoverRemoteSystems(subnet=IPv4Network('10.0.96.0/24'), session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation

pprint(obs)
```
???+ quote "Code Output"
    ```
    {'10.0.96.108': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.108')}]},
    '10.0.96.119': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.119')}]},
    '10.0.96.172': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.172')}]},
    '10.0.96.177': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.177')}]},
    '10.0.96.211': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.211')}]},
    '10.0.96.252': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.252')}]},
    '10.0.96.253': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.253')}]},
    '10.0.96.254': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.254')}]},
    '10.0.96.73': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                'ip_address': IPv4Address('10.0.96.73')}]},
    'action': DiscoverRemoteSystems 10.0.96.0/24,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The outputted observation contains the IP addresses of all hosts on the subnet.

> 출력된 관찰값에는 해당 서브넷에 있는 모든 호스트의 IP 주소가 담겨 있습니다.

In this case, there are 9 hosts on subnet `10.0.96.0/24`: 

> 이 경우, 서브넷 `10.0.96.0/24`에는 다음과 같이 9개의 호스트가 있습니다:

```10.0.96.108, 10.0.96.119, 10.0.96.172, 10.0.96.177, 10.0.96.211, 10.0.96.252, 10.0.96.253, 10.0.96.254, 10.0.96.73```.