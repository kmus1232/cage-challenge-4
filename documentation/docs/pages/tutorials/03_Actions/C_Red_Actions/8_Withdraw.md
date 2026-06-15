# Withdraw (철수)

`Withdraw` removes all the agent's sessions from a local or remote host. This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

> `Withdraw`(철수)는 로컬 또는 원격 호스트에서 해당 에이전트의 모든 세션을
> 제거합니다. 이 행동(Action)이 성공적으로 실행되려면 몇 가지 다른 행동이
> 선행되어야 합니다. 이 튜토리얼에서는 그것들을 간단히 짚고 넘어가며, 더 자세한
> 내용은 각 행동의 개별 튜토리얼 페이지를 참고하세요.

Here we will first find the known subnet, discover the hosts present on that subnet, choose a host and discover its services, exploit a remote service on that host to gain a user shell on it, privilege escalate that shell to root, then finally withdraw red presence from the host.

> 여기서는 먼저 알고 있는 서브넷(Subnet)을 찾고, 그 서브넷에 존재하는
> 호스트(Host)들을 탐색한 뒤, 호스트 하나를 골라 그 서비스(Service)를
> 탐색합니다. 이어서 해당 호스트의 원격 서비스를 익스플로잇(원격 서비스 공격)해
> 사용자 셸을 획득하고, 그 셸을 root 권한으로 상승(Privilege Escalate)시킨 다음,
> 마지막으로 그 호스트에서 Red(공격 측)의 흔적을 철수(Withdraw)시킵니다.

## Red Agent Preamble (Red 에이전트 사전 준비)
=== "Step 0: Initial Observation"

    First, we check Red's initial observations to find the subnet Red starts the scenario knowing.

    > 먼저 Red(공격 측) 에이전트의 초기 관찰값(Observation)을 확인해, Red가
    > 시나리오 시작 시점에 이미 알고 있는 서브넷을 찾습니다.

    ```python title="red_withdraw.py" linenums="1"
    from pprint import pprint
    from ipaddress import IPv4Network, IPv4Address

    from CybORG import CybORG
    from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
    from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
    from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, Sleep, PrivilegeEscalate, Withdraw, DegradeServices
    from CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions import ExploitRemoteService_cc4

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

    > 여기서 서브넷은 `10.0.96.0/24` 입니다.

=== "Step 1: Discover Remote Systems"
    We then execute [DiscoverRemoteSystems](1_Discover_Remote_Systems.md) to discover the other hosts present on the subnet.

    > 다음으로 [DiscoverRemoteSystems](1_Discover_Remote_Systems.md)(원격 시스템
    > 탐색)를 실행해 해당 서브넷에 존재하는 다른 호스트들을 탐색합니다.

    ```python title="red_withdraw.py" linenums="20"
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

    > 탐색된 호스트는 다음과 같습니다: `10.0.96.108`, `10.0.96.119`,
    > `10.0.96.172`, `10.0.96.177`, `10.0.96.211`, `10.0.96.252`, `10.0.96.253`,
    > `10.0.96.254`, `10.0.96.73`.

=== "Step 2: Service Discovery"

    We then execute [ServiceDiscovery](2_Service_Discovery.md) on a host for `ExploitRemoteService_cc4` to work. Here, we are using `AggressiveServiceDiscovery` as stealth is not important for this demonstration. We are investigating the host `10.0.96.108`, but this is an abitrary choice.

    > 다음으로 호스트 한 곳에 [ServiceDiscovery](2_Service_Discovery.md)(서비스
    > 탐색)를 실행해, 이후 `ExploitRemoteService_cc4`가 동작할 수 있도록 합니다.
    > 여기서는 이 시연에서 은밀성(stealth)이 중요하지 않으므로
    > `AggressiveServiceDiscovery`를 사용합니다. 조사 대상 호스트로
    > `10.0.96.108`을 선택했으나, 이는 임의의 선택입니다.

    ```python title="red_withdraw.py" linenums="24"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
    cyborg.step(agent=red_agent_name, action=action)
    ```

    We are omitting the observation output here, as it is not necessary in this tutorial.

    > 이 단계의 관찰값 출력은 본 튜토리얼에서 꼭 필요하지 않으므로 생략합니다.

=== "Step 3: Exploit Service"

    Now, we run [ExploitRemoteService_cc4](4_Exploit_Remote_Service.md) on `10.0.96.108` to gain a user shell on it.

    > 이제 `10.0.96.108`에
    > [ExploitRemoteService_cc4](4_Exploit_Remote_Service.md)(원격 서비스
    > 익스플로잇)를 실행해 해당 호스트에서 사용자 셸을 획득합니다.

    ```python title="red_withdraw.py" linenums="26"
    action = ExploitRemoteService_cc4(ip_address=IPv4Address('10.0.96.108'), session=0, agent=red_agent_name)
    cyborg.step(agent=red_agent_name, action=action)
    cyborg.step(agent=red_agent_name, action=Sleep())
    results = cyborg.step(agent=red_agent_name, action=Sleep())
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.108': {'Interface': [{'ip_address': IPv4Address('10.0.96.108')}],
                        'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                        'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 22}],
                                        'process_type': <ProcessType.SSH: 2>},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 22,
                                                        'remote_address': IPv4Address('10.0.96.73'),
                                                        'remote_port': 54893}],
                                        'process_type': <ProcessType.SSH: 2>}],
                        'Sessions': [{'Type': <SessionType.SSH: 2>,
                                    'agent': 'red_agent_0',
                                    'session_id': 1,
                                    'username': 'user'}],
                        'System info': {'Hostname': 'contractor_network_subnet_user_host_5',
                                        'OSType': <OperatingSystemType.LINUX: 3>}},
        '10.0.96.73': {'Interface': [{'ip_address': IPv4Address('10.0.96.73')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 54893,
                                                        'remote_address': IPv4Address('10.0.96.108'),
                                                        'remote_port': 22}]}]},
        'action': ExploitRemoteService_cc4 10.0.96.108,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.108')}],
                                                'Sessions': [{'Type': <SessionType.SSH: 2>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'user'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    The important takeaway from the results observation is `10.0.96.108`'s hostname: `contractor_network_subnet_user_host_5`.

    > 이 결과 관찰값에서 중요한 점은 `10.0.96.108`의 호스트명이
    > `contractor_network_subnet_user_host_5`라는 사실입니다.

=== "Step 4: Privilege Escalate Shell"

    With the user shell acquired, we execute [PrivilegeEscalate](5_Privilege_Escalate.md) on `contractor_network_subnet_user_host_5` to escalate the shell we have on it to root privileges.

    > 사용자 셸을 획득했으므로, `contractor_network_subnet_user_host_5`에
    > [PrivilegeEscalate](5_Privilege_Escalate.md)(권한 상승)를 실행해 보유한 셸을
    > root 권한으로 끌어올립니다.

    ```python title="red_withdraw.py" linenums="32"
    action = PrivilegeEscalate(hostname='contractor_network_subnet_user_host_5', session=0, agent=red_agent_name)
    results = cyborg.step(agent=red_agent_name, action=action)
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'action': PrivilegeEscalate contractor_network_subnet_user_host_5,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.108')}],
                                                'Processes': [{'PID': 8381,
                                                                'username': 'root'}],
                                                'Sessions': [{'PID': 8381,
                                                                'Type': <SessionType.SSH: 2>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'timeout': 0,
                                                                'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    Take note of the dictionary of information under both `contractor_network_subnet_user_host_4` and `contractor_network_subnet_user_host_5`.

    > `contractor_network_subnet_user_host_4`와
    > `contractor_network_subnet_user_host_5` 양쪽 아래에 담긴 정보 딕셔너리를
    > 눈여겨봐 두세요.

---

## Withdraw (철수)

Now a Red root shell has been established on `contractor_network_subnet_user_host_5`, we execute `Withdraw` to remove this shell and all Red presence.

> 이제 `contractor_network_subnet_user_host_5`에 Red의 root 셸이 확보되었으니,
> `Withdraw`(철수)를 실행해 이 셸과 모든 Red(공격 측)의 흔적을 제거합니다.

```python title="red_withdraw.py" linenums="36"
action = Withdraw(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.73'),hostname='contractor_network_subnet_user_host_5')
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': Withdraw contractor_network_subnet_user_host_5,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

Unlike in the result observation for `PrivilegeEscalate`, there is no trace of `contractor_network_subnet_user_host_5`. This is because Red has 'withdrawn' its root shell from that host. 

> `PrivilegeEscalate`의 결과 관찰값과 달리, 이번에는
> `contractor_network_subnet_user_host_5`의 흔적이 전혀 보이지 않습니다. Red가
> 해당 호스트에서 root 셸을 '철수(withdrawn)'했기 때문입니다.


## Testing Action Success (행동 성공 검증)

To test this, we will attempt to run [Degrade_Services](6_Degrade_Services.md) on `contractor_network_subnet_user_host_5`. `Degrade_Services` requires Red to have a root shell on the target to work.

> 이를 검증하기 위해 `contractor_network_subnet_user_host_5`에
> [Degrade_Services](6_Degrade_Services.md)(서비스 성능 저하)를 실행해 봅니다.
> `Degrade_Services`가 동작하려면 Red가 대상 호스트에 root 셸을 보유하고 있어야
> 합니다.

```python title="red_withdraw.py" linenums="40"
action = DegradeServices(hostname='contractor_network_subnet_user_host_5', session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': DegradeServices contractor_network_subnet_user_host_5,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.FALSE: 3>}
    ```

`Degrade_Services` has failed:

> `Degrade_Services`가 실패했습니다:

```
'success': <TernaryEnum.FALSE: 3>
```
This confirms that the shell was removed from `contractor_network_subnet_user_host_5`.

> 이는 `contractor_network_subnet_user_host_5`에서 셸이 제거되었음을 확인해
> 줍니다.
