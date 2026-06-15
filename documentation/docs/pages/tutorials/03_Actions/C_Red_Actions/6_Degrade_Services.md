# Degrade Services (서비스 성능 저하)
`DegradeServices` attempts to degrade services used by green in the mission. This is achieved by lowering the reliability of each service on the host, making a green agent's local work less likely to succeed. The more a service is degraded, the less likely green is to succeed in performing their local work for the mission.

> `DegradeServices`는 임무 수행 중 Green 에이전트(정상 사용자)가 사용하는 서비스의 성능을 저하시키려는 행동(Action)입니다. 이는 호스트에 있는 각 서비스의 신뢰도(reliability)를 낮추어, Green 에이전트의 로컬 작업이 성공할 가능성을 줄이는 방식으로 이뤄집니다. 서비스가 더 많이 저하될수록, Green 에이전트가 임무를 위한 로컬 작업을 성공적으로 수행할 가능성은 더 낮아집니다.

This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

> 이 행동을 성공적으로 실행하려면 몇 가지 다른 행동을 사전 조건(prerequisite)으로 먼저 거쳐야 합니다. 이 튜토리얼에서는 그 행동들을 간략히 다루지만, 더 자세한 내용은 각 행동의 개별 튜토리얼 페이지를 확인하시기 바랍니다.

## Red Agent Preamble (Red 에이전트 준비 단계)
Here we will first find the known subnet, discover the hosts present on that subnet, choose a host and discover its services, exploit a remote service on that host to gain a user shell on it, privilege escalate that shell to root, then finally degrade services.

> 여기서는 다음 순서를 따릅니다. 먼저 이미 알고 있는 서브넷(subnet)을 찾고, 그 서브넷에 존재하는 호스트들을 탐색하며, 호스트 하나를 골라 그 서비스를 탐색합니다. 이어서 해당 호스트의 원격 서비스를 익스플로잇(원격 서비스 공격)해 사용자 셸(user shell)을 획득하고, 그 셸의 권한을 root로 상승시킨 뒤, 마지막으로 서비스를 저하시킵니다.

=== "Step 0: Initial Observation"

    First, we check Red's initial observations to find the subnet Red starts the scenario knowing.

    > 먼저 Red 에이전트의 초기 관찰값(Observation)을 확인하여, Red가 시나리오 시작 시점에 이미 알고 있는 서브넷을 찾습니다.

    ```python title="red_degrade_services.py" linenums="1"
    from pprint import pprint
    from ipaddress import IPv4Network, IPv4Address

    from CybORG import CybORG
    from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
    from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
    from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, Sleep, PrivilegeEscalate, DegradeServices
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

    > 그다음 [DiscoverRemoteSystems](1_Discover_Remote_Systems.md)(원격 시스템 탐색)를 실행하여 서브넷에 존재하는 다른 호스트들을 탐색합니다.

    ```python title="red_degrade_services.py" linenums="20"
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

    > 탐색된 호스트는 다음과 같습니다: `10.0.96.108`, `10.0.96.119`, `10.0.96.172`, `10.0.96.177`, `10.0.96.211`, `10.0.96.252`, `10.0.96.253`, `10.0.96.254`, 그리고 `10.0.96.73`.

=== "Step 2: Service Discovery"

    We then execute [ServiceDiscovery](2_Service_Discovery.md) on a host for `ExploitRemoteService_cc4` to work. Here, we are using `AggressiveServiceDiscovery` as stealth is not important for this demonstration. We are investigating the host `10.0.96.108`, but this is an abitrary choice.

    > 그다음 `ExploitRemoteService_cc4`가 동작하려면 먼저 호스트 하나에 대해 [ServiceDiscovery](2_Service_Discovery.md)(서비스 탐색)를 실행해야 합니다. 여기서는 이 시연에서 은밀함(stealth)이 중요하지 않으므로 `AggressiveServiceDiscovery`를 사용합니다. 호스트 `10.0.96.108`을 조사하고 있는데, 이는 임의로 선택한 것입니다.

    ```python title="red_degrade_services.py" linenums="24"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
    results = cyborg.step(agent=red_agent_name, action=action)
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.108': {'Interface': [{'ip_address': IPv4Address('10.0.96.108')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 80}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 25}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 3390}]}]},
        'action': AggressiveServiceDiscovery 10.0.96.108,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    The services are visible in the resulting observations within `10.0.96.108`, `Processes`. In this case, these are as follows:

    > 탐색된 서비스들은 결과 관찰값 안의 `10.0.96.108` 항목 중 `Processes`에서 확인할 수 있습니다. 이 경우 다음과 같습니다.

    ```
    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 22}]},
        {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 80}]},
        {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 25}]},
        {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 3390}]}],
    ```
    Keep these in mind for later...

    > 이 서비스들을 뒤 단계를 위해 기억해 둡니다...

=== "Step 3: Exploit Service"

    Now, we run [ExploitRemoteService_cc4](4_Exploit_Remote_Service.md) on `10.0.96.108` to gain a user shell on it.

    > 이제 `10.0.96.108`에서 사용자 셸을 획득하기 위해 [ExploitRemoteService_cc4](4_Exploit_Remote_Service.md)(원격 서비스 익스플로잇)를 실행합니다.

    ```python title="red_degrade_services.py" linenums="28"
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

    > 결과 관찰값에서 중요한 점은 `10.0.96.108`의 호스트 이름(hostname)이 `contractor_network_subnet_user_host_5`라는 것입니다.

=== "Step 4: Privilege Escalate Shell"

    With the user shell acquired, we execute [PrivilegeEscalate](5_Privilege_Escalate.md) on `contractor_network_subnet_user_host_5` to escalate the shell we have on it to root privileges.

    > 사용자 셸을 획득했으니, 이제 `contractor_network_subnet_user_host_5`에서 [PrivilegeEscalate](5_Privilege_Escalate.md)(권한 상승)를 실행하여 보유한 셸의 권한을 root 권한으로 상승시킵니다.

    ```python title="red_degrade_services.py" linenums="34"
    action = PrivilegeEscalate(hostname='contractor_network_subnet_user_host_5', session=0, agent=red_agent_name)
    cyborg.step(agent=red_agent_name, action=action)
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
                                                'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```
---

## Degrade Services (서비스 성능 저하)

Finally, we can run `DegradeServices` on `contractor_network_subnet_user_host_5`.

> 마지막으로, `contractor_network_subnet_user_host_5`에서 `DegradeServices`를 실행할 수 있습니다.

```python title="red_degrade_services.py" linenums="36"
action = DegradeServices(hostname='contractor_network_subnet_user_host_5', session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation
pprint(obs)
```
??? quote "Code Output"
    ```
    {'action': DegradeServices contractor_network_subnet_user_host_5,
    'contractor_network_subnet_user_host_4': {
        'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                        'ip_address': IPv4Address('10.0.96.73')}],
        'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                        'agent': 'red_agent_0',
                        'session_id': 0,
                        'username': 'ubuntu'}],
        'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'contractor_network_subnet_user_host_5': {
        'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                        'ip_address': IPv4Address('10.0.96.108')}],
        'Processes': [{'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 22}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.SSHD: 7>,
                        'PID': 3761,
                        'Path': '/ usr / '
                                'sbin',
                        'process_name': <ProcessName.SSHD: 7>,
                        'process_type': <ProcessType.SSH: 2>,
                        'username': 'user'},
                        {'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 80}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.APACHE2: 13>,
                        'PID': 5783,
                        'Path': '/ usr / '
                                'sbin',
                        'process_name': <ProcessName.APACHE2: 13>,
                        'process_type': <ProcessType.WEBSERVER: 7>,
                        'username': 'user'},
                        {'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 25}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.SMTP: 11>,
                        'PID': 6815,
                        'Path': '/ usr / '
                                'sbin',
                        'Process Version': <ProcessVersion.HARAKA_2_8_9: 8>,
                        'process_name': <ProcessName.SMTP: 11>,
                        'process_type': <ProcessType.SMTP: 5>,
                        'username': 'user'},
                        {'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 3390}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.MYSQLD: 9>,
                        'PID': 8372,
                        'Path': '/ usr / '
                                'sbin',
                        'process_name': <ProcessName.MYSQLD: 9>,
                        'process_type': <ProcessType.MYSQL: 12>,
                        'username': 'user'}],
        'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                        'agent': 'red_agent_0',
                        'session_id': 1,
                        'username': 'root'}],
        'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```
This output is quite long, but in summary it tells us three things:

> 이 출력은 꽤 길지만, 요약하면 다음 세 가지를 알려줍니다.

- The action `DegradeServices` ran.
- The action was executed successfully.
- All the processes listed on the host that the action was run on were degraded.

> - `DegradeServices` 행동이 실행되었습니다.
> - 그 행동이 성공적으로 수행되었습니다.
> - 행동이 실행된 호스트에 나열된 모든 프로세스가 저하(degrade)되었습니다.

While the observation space output does not directly tell red (or blue) how much each service has been degraded by, the rewards received when green fails their [`GreenLocalWork`](../../../reference/actions/green_actions/local_work.md) action should be taken as the indication of the 'health' of the host and how much the operation is being affected by red.

> 관찰 공간(observation space)의 출력은 각 서비스가 얼마나 저하되었는지를 Red(나 Blue) 에이전트에게 직접 알려주지는 않습니다. 대신, Green 에이전트가 [`GreenLocalWork`](../../../reference/actions/green_actions/local_work.md)(Green 로컬 작업) 행동에 실패할 때 받게 되는 보상(Reward)을, 해당 호스트의 '건강 상태(health)'와 Red 에이전트의 작전이 임무에 얼마나 영향을 주고 있는지를 나타내는 지표로 받아들여야 합니다.
