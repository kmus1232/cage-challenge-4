# Getting Started With CybORG (CybORG 시작하기)

## Importing CybORG (CybORG 임포트하기)

To use the CybORG environment, it is necessary to import the `CybORG` class. 

> CybORG 환경을 사용하려면 `CybORG` 클래스를 임포트해야 합니다.

!!! tip "Capitalisation"
    CybORG stands for '**C**yber **O**perations **R**esearch **G**ym', so remember to capitalise correctly when importing!

    > **대소문자 표기 주의**: CybORG는 '**C**yber **O**perations **R**esearch **G**ym'의 약자입니다. 임포트할 때 대소문자를 정확히 맞춰 작성해야 합니다.

```python title="getting_started.py" linenums="1"
from CybORG import CybORG
```

## Instantiating CybORG (CybORG 인스턴스 생성하기)

CybORG has to be manually instantiated by calling the class constructor. This must be passed a `ScenarioGenerator` class, which contains the details of the scenario.
For Challenge 4, we will be using the `EnterpriseScenarioGenerator`, which creates the correct scenario.

> CybORG는 클래스 생성자를 호출해 직접 인스턴스를 만들어야 합니다. 이때 시나리오(Scenario)의 세부 정보를 담은 `ScenarioGenerator` 클래스를 인자로 넘겨야 합니다.
> Challenge 4에서는 적합한 시나리오를 생성해 주는 `EnterpriseScenarioGenerator`를 사용합니다.

```python linenums="2"
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator

sg = EnterpriseScenarioGenerator()
cyborg = CybORG(scenario_generator=sg)
```

## Interfacing with the Environment (환경과 상호작용하기)

CAGE Challenge 4 (CC4) is a multi-agent scenario consisting of several teams of agents. The Red team will be attacking the network, Blue team will be defending the network, while Green team represents the network users who will be passing messages to each other via the enterpise network. For this challenge, the roles of Red and Green will be handled by internal rules-based agents, while your task is to use an external API to train the Blue Team. This guide will walk you through the first steps for interfacing with the Blue agents.

> CAGE Challenge 4(CC4)는 여러 팀의 에이전트로 구성된 다중 에이전트(multi-agent) 시나리오입니다. Red 팀(공격 측)은 네트워크를 공격하고, Blue 팀(방어 측)은 네트워크를 방어하며, Green 팀(정상 사용자)은 엔터프라이즈 네트워크를 통해 서로 메시지를 주고받는 네트워크 사용자를 나타냅니다. 이 챌린지에서 Red와 Green의 역할은 내부에 내장된 규칙 기반(rules-based) 에이전트가 담당하고, 여러분의 과제는 외부 API를 사용해 Blue 팀을 학습시키는 것입니다. 이 가이드는 Blue 에이전트와 상호작용하는 첫 단계를 안내합니다.

A good starting point for developing your own rule-based agent is the `BlueFixedActionWrapper`. This wrapper provides a covenient API for enumerating all the actions that are available to each Blue agent in each episode, while providing direct access to CybORG's observations.

> 직접 규칙 기반 에이전트를 개발할 때 좋은 출발점은 `BlueFixedActionWrapper`입니다. 이 래퍼(Wrapper)는 각 에피소드(Episode)에서 Blue 에이전트마다 사용할 수 있는 모든 행동(Action)을 나열해 주는 편리한 API를 제공하며, 동시에 CybORG의 관찰값(Observation)에 직접 접근할 수 있게 해 줍니다.

```python linenums="6"
from CybORG.Agents.Wrappers import BlueFixedActionWrapper

env = BlueFixedActionWrapper(env=cyborg)
obs, _ = env.reset()

# optional pretty-printing
from rich import print

print(obs.keys())
```

???+ Quote "Code Output"
    > **코드 출력 결과**

    ```
    dict_keys(['blue_agent_0', 'blue_agent_1', 'blue_agent_2', 'blue_agent_3', 'blue_agent_4'])
    ```

```python linenums="15"
print(obs['blue_agent_0'])
```

??? Quote "Code Output (CybORG Observation)"
    > **코드 출력 결과 (CybORG 관찰값)**

    ???+ Note
        For more information on CybORG observations, see [Tutorial 2 - Looking Around](../02_Looking_Around/1_Observations.md).

        > CybORG 관찰값(Observation)에 대한 자세한 내용은 [Tutorial 2 - Looking Around](../02_Looking_Around/1_Observations.md)를 참고하세요.

    ```python
    {
        'success': <TernaryEnum.UNKNOWN: 2>,
        'restricted_zone_a_subnet_router': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.28'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 1, 'username': 'ubuntu', 'timeout': 0, 'PID': 3, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 3, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_router',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_0': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.192'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 2, 'username': 'ubuntu', 'timeout': 0, 'PID': 8580, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 8580, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_0',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_1': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.214'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 3, 'username': 'ubuntu', 'timeout': 0, 'PID': 9865, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 9865, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_1',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_2': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.209'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 4, 'username': 'ubuntu', 'timeout': 0, 'PID': 6978, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 6978, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_2',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_3': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.64'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 5, 'username': 'ubuntu', 'timeout': 0, 'PID': 4406, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 4406, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_3',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_4': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.215'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 6, 'username': 'ubuntu', 'timeout': 0, 'PID': 9400, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 9400, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_4',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_5': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.204'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 7, 'username': 'ubuntu', 'timeout': 0, 'PID': 5630, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 5630, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_5',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_6': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.195'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 8, 'username': 'ubuntu', 'timeout': 0, 'PID': 5546, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 5546, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_6',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_7': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.54'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 9, 'username': 'ubuntu', 'timeout': 0, 'PID': 4990, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 4990, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_7',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_0': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.254'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [
                {'session_id': 0, 'username': 'ubuntu', 'timeout': 0, 'PID': 7023, 'Type': <SessionType.VELOCIRAPTOR_SERVER: 8>, 'agent': 'blue_agent_0'}
            ],
            'Processes': [{'PID': 7023, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_0',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_1': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.253'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 10, 'username': 'ubuntu', 'timeout': 0, 'PID': 8838, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 8838, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_1',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_2': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.252'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 11, 'username': 'ubuntu', 'timeout': 0, 'PID': 1443, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 1443, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_2',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_3': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.251'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 12, 'username': 'ubuntu', 'timeout': 0, 'PID': 8640, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 8640, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_3',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        }
    }
    ```

A full list of human-readable action labels can be accessed using the `action_labels` function.
This list will always show all the actions that the given agent could take in CC4.
However, some hosts might not exist for the duration of an episode, and as a result, their corresponding
actions will have no effect. This is reflected in the list with a `[Invalid]` prefix.

> 사람이 읽기 쉬운 형태의 행동(Action) 레이블 전체 목록은 `action_labels` 함수로 확인할 수 있습니다.
> 이 목록에는 해당 에이전트가 CC4에서 취할 수 있는 모든 행동이 항상 표시됩니다.
> 다만 일부 호스트(Host)는 에피소드(Episode) 진행 중 존재하지 않을 수 있으며, 그 경우 해당 호스트에 대응하는 행동은 아무런 효과가 없습니다. 이런 행동은 목록에서 `[Invalid]` 접두사로 표시됩니다.

```python linenums="16"
print(env.action_space('blue_agent_0'))
print(env.action_labels('blue_agent_0'))
```

??? Quote "Code Output (Actions)"
    > **코드 출력 결과 (행동 목록)**

    ???+ Note
        For more information on the action helpers, see
        [Wrappers - BlueFixedActionWrapper](../02_Looking_Around/3_Wrappers.md#bluefixedactionwrapper).

        > 행동(Action) 관련 헬퍼 함수에 대한 자세한 내용은 [Wrappers - BlueFixedActionWrapper](../02_Looking_Around/3_Wrappers.md#bluefixedactionwrapper)를 참고하세요.

    ```python
    Discrete(82)
    [
        'Analyse restricted_zone_a_subnet_server_host_0',
        'Analyse restricted_zone_a_subnet_server_host_1',
        'Analyse restricted_zone_a_subnet_server_host_2',
        'Analyse restricted_zone_a_subnet_server_host_3',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_4',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_5',
        'Analyse restricted_zone_a_subnet_user_host_0',
        'Analyse restricted_zone_a_subnet_user_host_1',
        'Analyse restricted_zone_a_subnet_user_host_2',
        'Analyse restricted_zone_a_subnet_user_host_3',
        'Analyse restricted_zone_a_subnet_user_host_4',
        'Analyse restricted_zone_a_subnet_user_host_5',
        'Analyse restricted_zone_a_subnet_user_host_6',
        'Analyse restricted_zone_a_subnet_user_host_7',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_8',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_9',
        'Monitor',
        'Remove restricted_zone_a_subnet_server_host_0',
        'Remove restricted_zone_a_subnet_server_host_1',
        'Remove restricted_zone_a_subnet_server_host_2',
        'Remove restricted_zone_a_subnet_server_host_3',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_4',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_5',
        'Remove restricted_zone_a_subnet_user_host_0',
        'Remove restricted_zone_a_subnet_user_host_1',
        'Remove restricted_zone_a_subnet_user_host_2',
        'Remove restricted_zone_a_subnet_user_host_3',
        'Remove restricted_zone_a_subnet_user_host_4',
        'Remove restricted_zone_a_subnet_user_host_5',
        'Remove restricted_zone_a_subnet_user_host_6',
        'Remove restricted_zone_a_subnet_user_host_7',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_8',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_9',
        'Restore restricted_zone_a_subnet_server_host_0',
        'Restore restricted_zone_a_subnet_server_host_1',
        'Restore restricted_zone_a_subnet_server_host_2',
        'Restore restricted_zone_a_subnet_server_host_3',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_4',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_5',
        'Restore restricted_zone_a_subnet_user_host_0',
        'Restore restricted_zone_a_subnet_user_host_1',
        'Restore restricted_zone_a_subnet_user_host_2',
        'Restore restricted_zone_a_subnet_user_host_3',
        'Restore restricted_zone_a_subnet_user_host_4',
        'Restore restricted_zone_a_subnet_user_host_5',
        'Restore restricted_zone_a_subnet_user_host_6',
        'Restore restricted_zone_a_subnet_user_host_7',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_8',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_9',
        'Sleep',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- admin_network_subnet (10.0.88.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- contractor_network_subnet (10.0.48.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- internet_subnet (10.0.131.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- office_network_subnet (10.0.57.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_a_subnet (10.0.173.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_b_subnet (10.0.235.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- public_access_zone_subnet (10.0.115.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- restricted_zone_b_subnet (10.0.21.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- admin_network_subnet (10.0.88.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- contractor_network_subnet (10.0.48.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- internet_subnet (10.0.131.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- office_network_subnet (10.0.57.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_a_subnet (10.0.173.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_b_subnet (10.0.235.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- public_access_zone_subnet (10.0.115.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- restricted_zone_b_subnet (10.0.21.0/24)',
        'DeployDecoy restricted_zone_a_subnet_server_host_0',
        'DeployDecoy restricted_zone_a_subnet_server_host_1',
        'DeployDecoy restricted_zone_a_subnet_server_host_2',
        'DeployDecoy restricted_zone_a_subnet_server_host_3',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_4',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_5',
        'DeployDecoy restricted_zone_a_subnet_user_host_0',
        'DeployDecoy restricted_zone_a_subnet_user_host_1',
        'DeployDecoy restricted_zone_a_subnet_user_host_2',
        'DeployDecoy restricted_zone_a_subnet_user_host_3',
        'DeployDecoy restricted_zone_a_subnet_user_host_4',
        'DeployDecoy restricted_zone_a_subnet_user_host_5',
        'DeployDecoy restricted_zone_a_subnet_user_host_6',
        'DeployDecoy restricted_zone_a_subnet_user_host_7',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_8',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_9'
    ]
    ```

To take an action in the CybORG environment, we use the `env.step()` method.
This method takes a dictionary where the keys are the agent names and whose
values are an index corresponding to an action within the agent's action space.
If the specified action is invalid for the current episode, the agent will simply
do nothing. This function returns the next observation, rewards for the agents,
the termination and truncation signals for each agent, and the info dictionary.

> CybORG 환경에서 행동(Action)을 취할 때는 `env.step()` 메서드를 사용합니다.
> 이 메서드는 딕셔너리를 인자로 받는데, 키(key)는 에이전트 이름이고 값(value)은 해당 에이전트의 행동 공간(Action Space) 안에서 특정 행동을 가리키는 인덱스입니다.
> 지정한 행동이 현재 에피소드(Episode)에서 유효하지 않으면, 해당 에이전트는 아무 행동도 하지 않습니다. 이 함수는 다음 관찰값(Observation), 각 에이전트의 보상(Reward), 각 에이전트별 종료(termination)·중단(truncation) 신호, 그리고 info 딕셔너리를 반환합니다.

```python linenums="18"
actions = {'blue_agent_0': 42} # 'Restore restricted_zone_a_subnet_user_host_3'
obs, reward, terminated, truncated, info = env.step(actions)
print(reward['blue_agent_0'])
```

???+ Quote "Code Output"
    > **코드 출력 결과**

    ```python
    -4.0
    ```

Challenge 4 provides a mechanism to optionally send 8-bit messages between agents.
This is achieved by supplying the `step` function with a dictionary of agents and
a corresponding `np.array` with 8 binary elements.

> Challenge 4는 에이전트끼리 선택적으로 8비트 메시지를 주고받을 수 있는 메커니즘을 제공합니다.
> 이를 위해 `step` 함수에 에이전트와, 각 에이전트에 대응하는 8개의 이진(binary) 요소로 이루어진 `np.array`를 담은 딕셔너리를 함께 넘깁니다.

```python linenums="21"
import numpy as np
messages = {'blue_agent_0': np.array([1, 0, 0, 0, 0, 0, 0, 0])}
obs, reward, terminated, truncated, info = env.step(actions, messages=messages)
print(obs['blue_agent_1']['message'])
```

???+ Quote "Code Output (Messages)"
    > **코드 출력 결과 (메시지)**

    ```python
    [
        array([ True, False, False, False, False, False, False, False]), # Blue 0
        array([False, False, False, False, False, False, False, False]), # Blue 2
        array([False, False, False, False, False, False, False, False]), # Blue 3
        array([False, False, False, False, False, False, False, False])  # Blue 4
    ]
    ```

## Reinforcement Learning Agents (강화학습 에이전트)

Since CybORG observations can be quite verbose, we have included the `BlueFlatWrapper` to
convert the observations into a fixed-size vector format that is convenient for RL agents.

> CybORG의 관찰값(Observation)은 상당히 장황할 수 있기 때문에, 이를 강화학습(RL) 에이전트가 다루기 편한 고정 크기 벡터 형식으로 변환해 주는 `BlueFlatWrapper`를 함께 제공합니다.

```python linenums="6"
from CybORG.Agents.Wrappers import BlueFlatWrapper

env = BlueFlatWrapper(env=cyborg)
obs, _ = env.reset()

# optional pretty-printing
from rich import print

print('Space:', env.observation_space('blue_agent_0'), '\n')
print('Observation:', obs['blue_agent_0'])
```

???+ Quote "Code Output"
    > **코드 출력 결과**

    ???+ Note
        For a full breakdown of how the observation vectors are structured,
        see [Appendix B](../../README.md#appendix-b-agent-observation).

        > 관찰값(Observation) 벡터가 어떻게 구성되는지에 대한 전체 설명은 [Appendix B](../../README.md#appendix-b-agent-observation)를 참고하세요.

    ```python 
    Space: MultiDiscrete(
        [3 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
         2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
         2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2])

    Observation: 
        [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
    ```

???+ Note
    Some RL libraries require all agents to have observation spaces and action spaces of the same size.
    This can be enabled by passing `pad_spaces = True` to the `BlueFlatWrapper`. This will pad the
    observation space with zeros, and pad the action space with the `Sleep` action.

    > 일부 강화학습(RL) 라이브러리는 모든 에이전트의 관찰 공간(Observation Space)과 행동 공간(Action Space) 크기가 동일하기를 요구합니다.
    > 이 경우 `BlueFlatWrapper`에 `pad_spaces = True`를 넘기면 됩니다. 그러면 관찰 공간은 0으로, 행동 공간은 `Sleep` 행동으로 채워(pad) 크기를 맞춰 줍니다.

???+ Note "RLlib"
    For an RLlib-compatible, `MultiAgentEnvironment` version of the above wrapper use
    `from CybORG.Agents.Wrappers import EnterpriseMAE` in place of `BlueFlatWrapper`.

    > **RLlib**: 위 래퍼(Wrapper)를 RLlib과 호환되는 `MultiAgentEnvironment` 형태로 쓰려면, `BlueFlatWrapper` 대신 `from CybORG.Agents.Wrappers import EnterpriseMAE`를 사용하세요.
    
