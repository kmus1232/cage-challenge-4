# Impact (Impact 타격)
`Impact` attempts to affect services used by green in the mission. This is achieved by stopping the OT (operational technology) service currently running on a host that red has root priviliges on. 

> `Impact`(타격)은 임무 수행 중 **Green 에이전트(정상 사용자)가 사용하는 서비스에
> 타격을 주려는** 행동입니다. Red 에이전트(공격 측)가 root 권한을 가진 호스트에서
> 현재 실행 중인 **OT 서비스**(Operational Technology, 운영 기술 서비스)를 중단시키는
> 방식으로 이뤄집니다.

This is a powerful action for red, as OT services are essential to the mission and have a large affect on Blue's reward, however OT services are only present on servers in the Operational Zones - which limits this. Consequently, if the OT service is not present on the host that has been impacted, the action will fail.

> OT 서비스는 임무에 필수적이고 Blue 에이전트(방어 측)의 보상에 큰 영향을 주므로,
> 이 행동은 Red 에이전트에게 **강력한 수단**입니다. 다만 OT 서비스는 운영 영역
> (Operational Zones)의 서버에만 존재하기 때문에 사용에 제약이 따릅니다. 따라서
> 타격 대상 호스트에 OT 서비스가 없으면 이 행동은 **실패합니다**.

This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

> 이 행동을 성공적으로 실행하려면 몇 가지 선행 행동이 필요합니다. 이 튜토리얼에서는
> 그 행동들을 간략히 살펴보며, 더 자세한 내용은 각각의 튜토리얼 페이지를 참고하세요.

## Red Agent Preamble (Red 에이전트 사전 준비)

The red agent will only be successful with the Impact action, if they are in Operational Zones A and B. However it can take a while to expand from the contractor network into the operational networks. For this example, a OT service has been created on `contractor_network_subnet_server_host_0` to demonstrate a successful Impact action quickly, however this means that this tutorial is not directly repeatable.

> Red 에이전트는 운영 영역 A와 B(Operational Zones A and B)에 있을 때에만 Impact
> 행동을 성공시킬 수 있습니다. 다만 협력업체 네트워크(Contractor network)에서 운영
> 네트워크로 확장하는 데에는 시간이 걸릴 수 있습니다. 이 예시에서는 성공적인 Impact
> 행동을 빠르게 보여주기 위해 `contractor_network_subnet_server_host_0`에 OT 서비스를
> 미리 만들어 두었습니다. 따라서 이 튜토리얼은 그대로 똑같이 재현되지는 않습니다.

The Impact action also requires a red root shell on the host. To get this the following actions must be run:

> 또한 Impact 행동은 해당 호스트에서 Red 측의 root 셸(root shell)을 필요로 합니다.
> 이를 확보하려면 다음 행동들을 실행해야 합니다.

- `DiscoverRemoteSystems` - to find all the hosts on the contractor network.
- `AggressiveServiceDiscovery` (or `StealthServiceDiscovery`) - to find the services on host `contractor_network_subnet_server_host_0`.
- `ExploitRemoteService_cc4` - to get a user level shell on the host.
- `PrivilegeEscalate` - to get a root level shell on the host.

- `DiscoverRemoteSystems` — 협력업체 네트워크의 모든 호스트를 찾습니다.
- `AggressiveServiceDiscovery` (또는 `StealthServiceDiscovery`) — 호스트 `contractor_network_subnet_server_host_0`의 서비스를 찾습니다.
- `ExploitRemoteService_cc4` — 해당 호스트에서 사용자 수준 셸(user level shell)을 확보합니다.
- `PrivilegeEscalate` — 해당 호스트에서 root 수준 셸(root level shell)을 확보합니다.

You can refer to the [DegradeServices preamble](6_Degrade_Services.md#red-agent-preamble) for more details.

> 더 자세한 내용은 [DegradeServices 사전 준비](6_Degrade_Services.md#red-agent-preamble)
> 문서를 참고하세요.

Here is the observation space output for the PrivilegeEscalate action, for comparison later:

> 나중에 비교할 수 있도록, PrivilegeEscalate 행동의 관찰값(Observation) 출력은 다음과
> 같습니다.

??? quote "Code Output"
    ```
    {'action': PrivilegeEscalate contractor_network_subnet_server_host_0,
    'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                                'ip_address': IPv4Address('10.0.120.254')}],
                                                'Sessions': [{'Type': <SessionType.SSH: 2>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 1,
                                                            'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
    'contractor_network_subnet_user_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                            'ip_address': IPv4Address('10.0.120.47')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_3'}},
    'public_access_zone_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.188.254')}]},
    'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.28.254')}]},
    'restricted_zone_b_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.15.254')}]},
    'success': <TernaryEnum.TRUE: 1>}

    ```

## Impact Action (Impact 행동)

To perform the Impact action, you only require the hostname, session, and agent parameters.

> Impact 행동을 실행하는 데에는 `hostname`(호스트명), `session`(세션), `agent`(에이전트)
> 매개변수만 있으면 됩니다.

``` python
def perform_impact_action(cyborg):
    action = Impact(hostname='contractor_network_subnet_server_host_0', session=0, agent='red_agent_0')
    return cyborg.step(agent='red_agent_0', action=action)
```

A successful observation is shown below:

> 성공한 경우의 관찰값(Observation)은 다음과 같습니다.

???+ quote "Code Output"
    ```
    {'action': Impact contractor_network_subnet_server_host_0,
    'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                                'ip_address': IPv4Address('10.0.120.254')}],
                                                'Processes': [{'Known Process': <ProcessName.OTSERVICE: 29>,
                                                                'PID': 8029,
                                                                'process_name': <ProcessName.OTSERVICE: 29>,
                                                                'process_type': <ProcessType.UNKNOWN: 1>,
                                                                'username': 'user'}],
                                                'Sessions': [{'Type': <SessionType.SSH: 2>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 1,
                                                            'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
    'contractor_network_subnet_user_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                            'ip_address': IPv4Address('10.0.120.47')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_3'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

In the processes dictionary of the observation space, you can see the stopped OT service.

> 관찰값(Observation)의 프로세스(Processes) 딕셔너리에서 중단된 OT 서비스를 확인할 수
> 있습니다.

```
'Processes': [{'Known Process': <ProcessName.OTSERVICE: 29>,
    'PID': 8029,
    'process_name': <ProcessName.OTSERVICE: 29>,
    'process_type': <ProcessType.UNKNOWN: 1>,
    'username': 'user'}],
```

This information, alongside `'success': <TernaryEnum.TRUE: 1>`, shows that the OT service was stopped.

> 이 정보는 `'success': <TernaryEnum.TRUE: 1>`와 함께 OT 서비스가 중단되었음을 보여줍니다.
