# Discover Deception (디코이 탐지)
`DiscoverDeception` probes a remote host to see if it is running any decoy services. This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

> `DiscoverDeception`은 원격 호스트(Host)를 탐색해 그 호스트가 디코이(Decoy, 미끼) 서비스를 실행 중인지 확인하는 행동(Action)입니다. 이 행동을 성공적으로 실행하려면 사전에 수행해야 할 몇 가지 다른 행동이 있습니다. 이 튜토리얼에서는 그 행동들을 간단히 짚고 넘어가지만, 더 자세한 내용은 각 행동의 개별 튜토리얼 페이지를 참고하세요.

Here we will first find the known subnet, discover the hosts present on that subnet, choose two hosts and discover the services on each, then finally discover deception on both hosts.

> 여기서는 먼저 이미 알고 있는 서브넷(Subnet)을 찾고, 그 서브넷에 존재하는 호스트들을 탐색한 뒤, 호스트 두 개를 골라 각각의 서비스(Service)를 탐색하고, 마지막으로 두 호스트 모두에 대해 디코이 탐지를 수행합니다.

## Red Agent Preamble (Red 에이전트 사전 준비)
=== "Step 0: Initial Observation"

    First, we check Red's initial observations to find the subnet Red starts the scenario knowing.

    > 먼저 Red 에이전트(공격 측)의 초기 관찰값(Observation)을 확인해, Red가 시나리오(Scenario) 시작 시점에 이미 알고 있는 서브넷을 찾습니다.

    ```python title="red_discover_deception.py" linenums="1"
    from pprint import pprint
    from ipaddress import IPv4Network, IPv4Address

    from CybORG import CybORG
    from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
    from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
    from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, Sleep, DiscoverDeception

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

    Here, the subnet is `10.0.96.0/24`.

    > 여기서 서브넷은 `10.0.96.0/24`입니다.

=== "Step 1: DiscoverRemoteSystems"
    We then execute [DiscoverRemoteSystems](1_Discover_Remote_Systems.md) to discover the other hosts present on the subnet.

    > 그다음 [DiscoverRemoteSystems](1_Discover_Remote_Systems.md)(원격 시스템 탐색)를 실행해, 해당 서브넷에 존재하는 다른 호스트들을 탐색합니다.
        
    ```python title="red_discover_deception.py" linenums="19"
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

    These are: `10.0.96.108`, `10.0.96.119`, `10.0.96.172`, `10.0.96.177`, `10.0.96.211`, `10.0.96.252`, `10.0.96.253`, `10.0.96.254`, and `10.0.96.73`.

    > 탐색된 호스트는 `10.0.96.108`, `10.0.96.119`, `10.0.96.172`, `10.0.96.177`, `10.0.96.211`, `10.0.96.252`, `10.0.96.253`, `10.0.96.254`, `10.0.96.73`입니다.

=== "Step 2: ServiceDiscovery"

    Running [ServiceDiscovery](2_Service_Discovery.md) on a host is necessary for `DiscoverDeception` to work, as Red needs to know the services the host is running to ascertain if any of those services are decoys. 

    > `DiscoverDeception`이 동작하려면 호스트에 대해 [ServiceDiscovery](2_Service_Discovery.md)(서비스 탐색)를 먼저 실행해야 합니다. Red가 그 서비스들 중 디코이가 있는지 확인하려면, 호스트가 실행 중인 서비스를 먼저 알아야 하기 때문입니다.

    Here, we are using `AggressiveServiceDiscovery` as stealth is not important for this demonstration. We are also investigating both hosts `10.0.96.177` and `10.0.96.108`, to demonstrate the different results `DiscoverDeception` can produce.

    > 이 예시에서는 은밀성(stealth)이 중요하지 않으므로 `AggressiveServiceDiscovery`를 사용합니다. 또한 `DiscoverDeception`이 만들어낼 수 있는 서로 다른 결과를 보여주기 위해, 호스트 `10.0.96.177`과 `10.0.96.108` 두 개를 모두 조사합니다.

    ```python title="red_discover_deception.py" linenums="23"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.177'))
    cyborg.step(agent=red_agent_name, action=action)
    ```

    ```python title="red_discover_deception.py" linenums="25"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
    cyborg.step(agent=red_agent_name, action=action)
    ```

    We are omitting the observation output here, as it is not necessary in this tutorial.

    > 이 단계의 관찰값 출력은 이 튜토리얼에서 꼭 필요하지 않으므로 생략합니다.

---

## Discover Deception - Decoy Found (디코이 탐지 - 디코이 발견됨)
This first execution of `DiscoverDeception` is on host `10.0.96.177`, which does have a decoy service. This action takes two ticks, so we must wait. 

> `DiscoverDeception`의 첫 번째 실행은 디코이 서비스를 실제로 가지고 있는 호스트 `10.0.96.177`을 대상으로 합니다. 이 행동은 두 틱(tick, 시간 단위)이 걸리므로 기다려야 합니다.

```python title="red_discover_deception.py" linenums="27"
action = DiscoverDeception(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.177'))
cyborg.step(agent=red_agent_name, action=action)
results = cyborg.step(agent=red_agent_name, action=Sleep())
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': DiscoverDeception contractor_network_subnet_user_host_0,
    'contractor_network_subnet_user_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.96.177')}],
                                            'Processes': [{'PID': 9877,
                                                            'Properties': ['decoy'],
                                                            'service_name': <ProcessName.MYSQLD: 9>,
                                                            'username': 'user'}]},
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The observation result includes a key `contractor_network_subnet_user_host_0`, whose value contains information about the host we just investigated: `10.0.96.177`. Under `Processes` within that information is the decoy process: 

> 관찰값 결과에는 `contractor_network_subnet_user_host_0`라는 키가 들어 있으며, 그 값에는 방금 조사한 호스트 `10.0.96.177`의 정보가 담겨 있습니다. 그 정보의 `Processes` 항목 아래에 디코이 프로세스(Process)가 있습니다.

```
'Processes': [{'PID': 9877,
    'Properties': ['decoy'],
    'service_name': <ProcessName.MYSQLD: 9>,
    'username': 'user'}]
```

Now Red knows not to attempt to exploit this service.

> 이제 Red 에이전트는 이 서비스를 익스플로잇(Exploit, 원격 서비스 공격)하려 시도하면 안 된다는 것을 알게 됩니다.

## Discover Deception - Decoy Not Found (디코이 탐지 - 디코이 발견되지 않음)
This next execution of `DiscoverDeception` is on host `10.0.96.108`, which does NOT have a decoy service. 

> `DiscoverDeception`의 다음 실행은 디코이 서비스를 가지고 있지 **않은** 호스트 `10.0.96.108`을 대상으로 합니다.

```python title="red_discover_deception.py" linenums="32"
action = DiscoverDeception(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
cyborg.step(agent=red_agent_name, action=action)
results = cyborg.step(agent=red_agent_name, action=Sleep())
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': DiscoverDeception contractor_network_subnet_user_host_5,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```
    
Unlike the first execution on `10.0.96.177`, the observation result for `10.0.96.108` does not include an entry for this host. This is the result when no decoy services have been detected. 

> `10.0.96.177`에 대한 첫 번째 실행과 달리, `10.0.96.108`에 대한 관찰값 결과에는 이 호스트에 대한 항목이 들어 있지 않습니다. 이는 디코이 서비스가 하나도 탐지되지 않았을 때 나오는 결과입니다.

It should be noted that the action's `success` key in the observation result has the value TRUE for `DiscoverDeception` regardless of whether a decoy has been found.

> 한 가지 유의할 점은, 디코이가 발견되었는지 여부와 관계없이 `DiscoverDeception`의 관찰값 결과에서 행동의 `success` 키 값은 항상 TRUE라는 것입니다.
