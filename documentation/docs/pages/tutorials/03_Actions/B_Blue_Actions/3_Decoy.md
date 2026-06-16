# DeployDecoy

`DeployDecoy` creates a decoy service on the specified host, reminiscent of a honeypot. 

> `DeployDecoy`는 지정한 호스트에 **디코이(Decoy, 미끼) 서비스**를 만듭니다. 허니팟(honeypot, 공격자를 유인하는 가짜 서비스)과 비슷한 개념입니다.

This results in red wasting their time on a service that they cannot use, and gives blue more alerts on what is happening in the environment.

> 그 결과 Red 에이전트(공격 측)는 실제로는 사용할 수 없는 서비스에 시간을 허비하게 되고, Blue 에이전트(방어 측)는 환경에서 무슨 일이 벌어지는지에 대한 경보(alert)를 더 많이 얻게 됩니다.

## Red Preamble (Red 사전 설정)
For this tutorial, red has successfully gained a root shell on `contractor_network_subnet_server_host_0`, and is starting to branch out into other networks.

> 이 튜토리얼에서는 Red 에이전트가 이미 `contractor_network_subnet_server_host_0`에서 root 셸(최고 권한 셸) 획득에 성공했고, 다른 네트워크로 뻗어 나가기 시작한 상태를 가정합니다.

This is difficult to orchestrate, so a full function has been provided to get you to this point, with environment seed 100. 

> 이 상태를 직접 만들어 내기는 까다롭기 때문에, 환경 시드(seed) 100으로 이 지점까지 도달시켜 주는 함수를 통째로 제공합니다.

??? info "Helper Function"
    ```python
    red_agent_name = ['red_agent_0', 'red_agent_1']
    blue_agent_name = 'blue_agent_0'


    def cyborg_with_root_shell_on_cns0() -> CybORG:
        """Get red_agent_0 a root shell on 'contractor_network_subnet_server_host_0' 
        
        Observation gained from last PrivilegeEscalate:
            'public_access_zone_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.176.254')}]},
            'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}]},
            'restricted_zone_b_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.100.254')}]},

        Returns
        -------
        cyborg : CybORG
            a cyborg environment with a root shell on cns0
        """
        ent_sg = EnterpriseScenarioGenerator(
                blue_agent_class=SleepAgent,
                red_agent_class=SleepAgent,
                green_agent_class=SleepAgent,
                steps=100
            )
        cyborg = CybORG(scenario_generator=ent_sg, seed=100)
        cyborg.reset()
        env = cyborg.environment_controller

        s0_hostname = 'contractor_network_subnet_server_host_0'
        s0_ip_addr = env.state.hostname_ip_map[s0_hostname]
        cn_subnet_ip = env.subnet_cidr_map[env.state.hostname_subnet_map[s0_hostname]]

        action = DiscoverRemoteSystems(subnet=cn_subnet_ip, session=0, agent=red_agent_name[0])
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])

        action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=s0_ip_addr)
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])

        action = ExploitRemoteService(ip_address=s0_ip_addr, session=0, agent=red_agent_name[0])
        action.duration = 1
        results = cyborg.step(agent=red_agent_name[0], action=Sleep())
        obs = results.observation
        print(obs['action'], obs['success'])

        action = PrivilegeEscalate(hostname=s0_hostname, session=0, agent=red_agent_name[0])
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])

        return cyborg
    ```

This function then needs to be called, and some host knowledge defined. Additional processes and services have been removed from the target host in this example.

> 그다음 이 함수를 호출하고, 호스트 관련 정보를 몇 가지 정의해야 합니다. 이 예시에서는 대상 호스트에서 추가 프로세스와 서비스를 제거해 두었습니다.

??? info "Tutorial set-up code"
    ```python
    cyborg = cyborg_with_root_shell_on_cns0()

    target_subnet = 'restricted_zone_a_subnet'
    target_host = target_subnet + '_server_host_0'
    target_ip = cyborg.environment_controller.state.hostname_ip_map[target_host]
    shell_ip = cyborg.environment_controller.state.hostname_ip_map['contractor_network_subnet_server_host_3']

    cyborg.environment_controller.state.hosts[target_host].processes = []
    cyborg.environment_controller.state.hosts[target_host].services = {}
    ```

However, feel free to follow along without implementing the code. The summary of the red actions performed is:

> 다만 코드를 직접 구현하지 않고 그대로 따라 읽기만 해도 괜찮습니다. 위에서 수행된 Red 행동(Action)을 요약하면 다음과 같습니다.

```
DiscoverRemoteSystems 10.0.157.0/24 TRUE
AggressiveServiceDiscovery 10.0.157.254 TRUE
ExploitRemoteService 10.0.157.254 TRUE
PrivilegeEscalate contractor_network_subnet_server_host_0 TRUE
```

???+ warning
    For demonstration purposes, the action durations in these tutorial scripts are sometimes set to 1 in order to show the immediate results.

    > 시연을 위해, 이 튜토리얼 스크립트에서는 즉각적인 결과를 보여주려고 행동 지속 시간(action duration)을 가끔 1로 설정합니다.

    **This is _NOT_ permitted in challenge submissions!**

    > **이런 설정은 챌린지 제출물에서는 _허용되지 않습니다_!**

## Deploying a Decoy (디코이 배치하기)
The DeployDecoy action for blue is quite simple. Specify the agent performing the action (`blue_agent_name = 'blue_agent_0'`), the name of the host to have the decoy on it, and the agent session.

> Blue 에이전트의 DeployDecoy 행동은 꽤 단순합니다. 행동을 수행하는 에이전트(`blue_agent_name = 'blue_agent_0'`), 디코이를 올릴 호스트의 이름, 그리고 에이전트 세션(session)을 지정하면 됩니다.

```python
action = DeployDecoy(session=0, agent=blue_agent_name, hostname=target_host)
action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: action})

print("DeployDecoy:")
print("Blue:")
pprint(obs[blue_agent_name])
print("\n")
```

This results in the following output that shows the new process, linked to the new service, on the host. The action and success is also displayed as standard.

> 그 결과 다음과 같은 출력이 나오며, 호스트에 새 서비스와 연결된 새 프로세스가 보입니다. 행동(action)과 성공 여부(success)도 표준 형식으로 함께 표시됩니다.

???+ quote "Code Output"
    ```
    DeployDecoy:
    Blue:
    {'action': DeployDecoy restricted_zone_a_subnet_server_host_0,
    'restricted_zone_a_subnet_server_host_0': {'Processes': [{'PID': 4,
                                                            'PPID': 1,
                                                            'service_name': 'haraka',
                                                            'username': 'ubuntu'}]},
    'success': <TernaryEnum.TRUE: 1>}
    ```

## Red Discovering the Service (Red가 서비스를 발견함)
It is then only a matter of time before red attempts to discover the services running on the host.

> 이제 Red 에이전트가 그 호스트에서 실행 중인 서비스를 탐색하려 시도하는 것은 시간문제일 뿐입니다.

```python
red_action = StealthServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
red_action.duration = 1
red_action.detection_rate = 0
obs, _, _, _ = cyborg.parallel_step(actions={red_agent_name[0]: red_action})

print("StealthServiceDiscovery:")
print("Red:")
pprint(obs[red_agent_name[0]])
print("\n")
print("Blue:")
pprint(obs[blue_agent_name])
print("\n")
```

The `detection_rate` of the red action is this example has been affectively 'turned off' so that you only see the detections resulting from the decoy service.

> 이 예시에서는 Red 행동의 `detection_rate`(탐지율)를 사실상 '꺼 둔' 상태로 설정했습니다. 그래야 디코이 서비스에서 비롯된 탐지만 따로 볼 수 있기 때문입니다.

=== "Red Observation"
    In red's observation you can see a number of things:

    > Red 에이전트의 관찰값(Observation)에서는 여러 가지를 확인할 수 있습니다.

    - the action - StealthServiceDiscovery
    - the action's success - which is successful
    - the services that red has discovered - a process with local port 25
    - the two shells the red agent currently has:
        1. contractor_network_subnet_server_host_0
        2. contractor_network_subnet_server_host_3

    > - 수행한 행동 - StealthServiceDiscovery
    > - 행동의 성공 여부 - 성공함
    > - Red가 발견한 서비스 - 로컬 포트(local port) 25를 사용하는 프로세스
    > - Red 에이전트가 현재 가지고 있는 두 개의 셸:
    >     1. contractor_network_subnet_server_host_0
    >     2. contractor_network_subnet_server_host_3

    ??? quote "Code Output"
        ```
        Red:
        {'10.0.7.254': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 25}]}]},
        'action': StealthServiceDiscovery 10.0.7.254,
        'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
        'contractor_network_subnet_server_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.250')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_3'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```


=== "Blue Observation"
    In blue's observation, you can see a network connection alert has come in from the Monitor default action that runs every step (even when the agent is sleeping).

    > Blue 에이전트의 관찰값에서는, 매 스텝(step)마다 실행되는 기본 행동인 Monitor(모니터링)로부터 네트워크 연결 경보가 들어온 것을 볼 수 있습니다. 이 Monitor는 에이전트가 잠자고(sleep) 있을 때도 실행됩니다.

    This connection is from the local host 'restricted_zone_a_subnet_server_host_0', on their local port 25 (where the decoy service is). The connection is coming from an IP address in the contractor network... how mysterious.

    > 이 연결은 로컬 호스트 'restricted_zone_a_subnet_server_host_0'의 로컬 포트 25(디코이 서비스가 있는 곳)에서 발생했습니다. 그리고 그 연결은 협력업체 네트워크(Contractor network)에 속한 IP 주소에서 들어오고 있습니다... 어딘가 수상하죠.

    ??? quote "Code Output"
        ```
        Blue:
        {'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                                                    'local_port': 25,
                                                                                    'remote_address': IPv4Address('10.0.157.250'),
                                                                                    'remote_port': 58659}]}],
                                                    'System info': {'Architecture': <Architecture.x64: 2>,
                                                                    'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                                                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                                                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                                    'position': array([0., 0.])}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```

    The eagle-eyed may have noticed that '10.0.157.250' is the IP address of the original red shell (with session id 0), not the host that has the red reverse shell.

    > 눈썰미가 좋은 분이라면 '10.0.157.250'이 Red 리버스 셸(reverse shell)을 가진 호스트가 아니라, 원래의 Red 셸(세션 id 0)의 IP 주소라는 점을 알아챘을 것입니다.

---

## Red Attempts to Exploit the Decoy (Red가 디코이를 익스플로잇하려 시도함)
Once red has discovered the service, they can now try to exploit it. However it may not go as they planned :smiling_imp:.

> 일단 Red 에이전트가 서비스를 발견하면, 이제 그것을 익스플로잇(exploit, 취약점 공격)하려 시도할 수 있습니다. 하지만 계획대로 풀리지 않을 수도 있습니다 :smiling_imp:.

In the code below, 'red_agent_0' attempts to exploit the target host which has only a decoy service on it.

> 아래 코드에서 'red_agent_0'는 디코이 서비스만 올라가 있는 대상 호스트를 익스플로잇하려 시도합니다.

```python
action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={red_agent_name[0]: action})

print("ExploitRemoteService:")
print("Red:")
pprint(obs[red_agent_name[0]])
print("\n")
print("Blue:")
pprint(obs[blue_agent_name])
print("\n")
```

=== "Red's Observation"
    In red's observation, they get a confirmation that there is an process at port 25 with an SMTP service running.
    However their action failed for some reason. The ExploitRemoteService action is not 100% successful everytime, so why not try again?

    > Red 에이전트의 관찰값에서는, 포트 25에 SMTP 서비스가 실행 중인 프로세스가 있다는 확인을 얻습니다. 하지만 무슨 이유에서인지 행동은 실패했습니다. ExploitRemoteService 행동이 매번 100% 성공하는 것은 아니니, 다시 한번 시도해 보면 어떨까요?

    This results in red wasting more of their steps on a service they can never properly utilise. 

    > 그 결과 Red는 결코 제대로 활용할 수 없는 서비스에 더 많은 스텝(step)을 허비하게 됩니다.

    ??? quote "Code Output"
        ```
        Red:
        {'10.0.7.254': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                        'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                        'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 25}],
                                    'process_type': <ProcessType.SMTP: 5>}]},
        'action': ExploitRemoteService 10.0.7.254,
        'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
        'contractor_network_subnet_server_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.250')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_3'}},
        'success': <TernaryEnum.FALSE: 3>}
        ```

    **Note:** If there are services that are not decoys on the host, red may be able to exploit those services to get a shell on the host.
    Having one decoy on a host does not make the host immune to compromise, it is designed to give blue better visibility.

    > **참고:** 호스트에 디코이가 아닌 실제 서비스가 있다면, Red는 그 서비스를 익스플로잇해서 호스트에 셸을 얻을 수도 있습니다. 호스트에 디코이를 하나 두었다고 해서 그 호스트가 침해(compromise)로부터 안전해지는 것은 아닙니다. 디코이는 Blue에게 더 나은 가시성(visibility)을 주기 위한 장치입니다.


=== "Blue's Observation"
    In blue's observation, they have two additional alerts. One is the connection between the red and the open port 25, and the other between the host and red on epherimeral ports that represents an attempted C2 connection. 

    > Blue 에이전트의 관찰값에는 추가 경보 두 개가 들어옵니다. 하나는 Red와 열린 포트 25 사이의 연결이고, 다른 하나는 임시 포트(ephemeral port)를 통한 호스트와 Red 사이의 연결로, C2(Command and Control, 공격자 원격 제어) 연결 시도를 나타냅니다.

    Due to there being no PID value in the connection, a process was not created by this.

    > 이 연결에는 PID(프로세스 식별자) 값이 없기 때문에, 이로 인해 프로세스가 생성되지는 않았습니다.

    ??? quote "Code Output"
        ```
        Blue:
        {'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                                                    'local_port': 25,
                                                                                    'remote_address': IPv4Address('10.0.157.250'),
                                                                                    'remote_port': 57563}]},
                                                                {'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                                                    'local_port': 51672,
                                                                                    'remote_address': IPv4Address('10.0.157.250'),
                                                                                    'remote_port': 58056}]}],
                                                    'System info': {'Architecture': <Architecture.x64: 2>,
                                                                    'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                                                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                                                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                                    'position': array([0., 0.])}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```
