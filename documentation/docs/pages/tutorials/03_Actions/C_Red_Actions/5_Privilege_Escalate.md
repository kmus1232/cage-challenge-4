# Privilege Escalate (권한 상승)

`PrivilegeEscalate` carries out an exploit on a specific host that Red has a user shell on, to gain a shell with root privileges.

> `PrivilegeEscalate`는 Red 에이전트(공격 측)가 이미 사용자 셸(user shell)을 확보한
> 특정 호스트(Host)에서 익스플로잇(원격 서비스 공격)을 수행해, root 권한 셸을 획득하는
> 행동(Action)입니다.

Here, we will be privilege escalating the first host that Red knows.

> 여기서는 Red 에이전트가 알고 있는 첫 번째 호스트를 대상으로 권한 상승을 수행해 보겠습니다.

## Identify Host with User Shell (사용자 셸을 가진 호스트 식별)

In order to run privilege escalation, we must find the target host's name. We do this by looking at Red's initial observation.

> 권한 상승을 실행하려면 먼저 대상 호스트의 이름을 알아내야 합니다. 이는 Red 에이전트의
> 초기 관찰값(initial observation)을 살펴봄으로써 확인합니다.

```python title="red_privilege_escalate.py" linenums="1"
from pprint import pprint
from ipaddress import IPv4Network, IPv4Address

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import PrivilegeEscalate

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

The only host Red is currently aware of has a hostname visible in the key `contractor_network_subnet_user_host_4`. 

> 현재 Red 에이전트가 인지하고 있는 유일한 호스트는 `contractor_network_subnet_user_host_4`
> 라는 키로 호스트명이 드러나 있습니다.

We already have a user shell on `contractor_network_subnet_user_host_4` - this is shown in Red's initial observations above:

> 우리는 이미 `contractor_network_subnet_user_host_4`에 사용자 셸을 확보하고 있습니다.
> 이는 위의 Red 에이전트 초기 관찰값에서 다음과 같이 드러납니다.
```
'Sessions': [{'PID': 5753,
    'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
    'agent': 'red_agent_0',
    'session_id': 0,
    'timeout': 0,
    'username': 'ubuntu'}],
```
As such, we can immediately execute `PrivilegeEscalate` on `contractor_network_subnet_user_host_4`.

> 따라서 `contractor_network_subnet_user_host_4`에 대해 곧바로 `PrivilegeEscalate`를
> 실행할 수 있습니다.

If we did not have a user shell on the host that we want to perform a privilege escalate on, we would need to do that first.

> 만약 권한 상승을 수행하려는 호스트에 사용자 셸이 아직 없다면, 먼저 사용자 셸을 확보하는
> 작업부터 해야 합니다.

## Privilege Escalate (권한 상승 실행)

```python title="red_privilege_escalate.py" linenums="19"
action = PrivilegeEscalate(hostname='contractor_network_subnet_user_host_4', session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': PrivilegeEscalate contractor_network_subnet_user_host_4,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'root'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

Comparing the resulting observation to Red's initial observation, the `username` in Red's session on `contractor_network_subnet_user_host_4` has changed to `root`, demonstrating the success of the privilege escalation:

> 실행 결과 관찰값을 Red 에이전트의 초기 관찰값과 비교해 보면,
> `contractor_network_subnet_user_host_4`의 Red 세션(Session)에서 `username`이 `root`로
> 바뀐 것을 알 수 있습니다. 이는 권한 상승이 성공했음을 보여줍니다.
```
'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
    'agent': 'red_agent_0',
    'session_id': 0,
    'username': 'root'}],
```