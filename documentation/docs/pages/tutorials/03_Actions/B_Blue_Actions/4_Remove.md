# Remove (제거)
`Remove` results in a red user level shell being removed from the target host.

> `Remove`(제거)는 대상 호스트(target host)에서 Red 에이전트(공격 측)의 **사용자 권한(user level) 셸을 제거**하는 행동(Action)입니다.

As this action takes a few time steps, is is worthwhile being sure that a red agent is actually on the host. 
The feedback in the observation space every step, from the `Monitor` action, can be used as evidence however `Analyse` will provide better proof of a shell being on the host.

> 이 행동은 몇 스텝(step)의 시간이 걸리므로, Red 에이전트가 정말로 그 호스트에 있는지 먼저 확인해 두는 것이 좋습니다.
> 매 스텝마다 `Monitor`(모니터링) 행동을 통해 관찰값(Observation)으로 들어오는 피드백을 근거로 쓸 수 있지만, 셸이 호스트에 존재한다는 더 확실한 증거는 `Analyse`(분석)가 제공합니다.

???+ warning "User vs Root Shells"
    `Remove` is not as powerful an action as `Restore`, which is the equivalent of starting from scratch via backups, which is partially why it takes less time steps to perform. Therefore `Remove` will **NOT** be effective against red root shells, only against user shells.

    > `Remove`(제거)는 `Restore`(복원)만큼 강력한 행동은 아닙니다. `Restore`는 백업본으로 처음부터 다시 시작하는 것에 해당하며, `Remove`가 더 적은 스텝으로 수행되는 이유 중 하나가 바로 이 차이입니다. 따라서 `Remove`는 Red의 root(루트, 최상위 권한) 셸에는 **효과가 없으며**, 오직 사용자 권한(user) 셸에만 효과가 있습니다.


## Red Preamble (Red 사전 준비)

This tutorial will use the same initial [red preamble](3_Decoy.md#red-preamble) as the `DeployDecoy` tutorial, please refer to that for more details about getting a root shell on `contractor_network_subnet_server_host_0`.

> 이 튜토리얼은 `DeployDecoy` 튜토리얼과 동일한 초기 [Red 사전 준비](3_Decoy.md#red-preamble)를 사용합니다. `contractor_network_subnet_server_host_0`에서 root 셸을 얻는 방법에 대한 자세한 내용은 그 문서를 참고해 주세요.

However this tutorial will also require another helper function to get a shell on `restricted_zone_a_subnet_server_host_0`. In this example, `target_subnet` and `target_host` are global variables.

> 다만 이 튜토리얼에서는 `restricted_zone_a_subnet_server_host_0`에서 셸을 얻기 위한 또 하나의 보조 함수(helper function)도 필요합니다. 이 예시에서 `target_subnet`과 `target_host`는 전역 변수(global variable)입니다.

??? info "Helper Function"
    ```python
    target_subnet = 'restricted_zone_a_subnet'
    target_host = target_subnet + '_server_host_0'

    def get_shell_on_rzas0(cyborg:CybORG, shell_type:str = 'root'):
        # shell_type = user or root

        env = cyborg.environment_controller
        target_ip = env.state.hostname_ip_map[target_host]

        # Discover a service on restricted_zone_a_subnet_server_host_0
        red_action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
        results = cyborg.step(agent=red_agent_name[0], action=red_action)
        obs = results.observation
        assert 'AggressiveServiceDiscovery' in str(obs['action'])
        print(obs['action'], obs['success'])
        assert obs['success'] == True

        # Red exploits restricted_zone_a_subnet_server_host_0 to gain a user shell
        action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
        action.duration = 1
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])
        assert 'Exploit' in str(obs['action'])
        assert obs['success'] == True

        if shell_type == 'user':
            return cyborg

        # Red privilege escalates restricted_zone_a_subnet_server_host_0 to gain a user shell
        red_action = PrivilegeEscalate(hostname=target_host, session=0, agent=red_agent_name[1])
        action.duration = 1
        results = cyborg.step(agent=red_agent_name[1], action=red_action)
        obs = results.observation
        print(obs['action'], obs['success'])
        assert 'PrivilegeEscalate' in str(obs['action'])
        assert obs['success'] == True

        return cyborg
    ```

When nesting both helper functions, as shown here:

> 아래처럼 두 보조 함수를 중첩해서 호출하면:

```python
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='user')
```

You should get the following list of actions:

> 다음과 같은 행동 목록이 출력됩니다:

```
DiscoverRemoteSystems 10.0.157.0/24 TRUE
AggressiveServiceDiscovery 10.0.157.254 TRUE
ExploitRemoteService 10.0.157.254 TRUE
PrivilegeEscalate contractor_network_subnet_server_host_0 TRUE
AggressiveServiceDiscovery 10.0.7.254 TRUE
ExploitRemoteService 10.0.7.254 TRUE
```

## Successfully Removing a User Shell (사용자 셸을 성공적으로 제거하기)
The aim of using the `Remove` action is to remove a user shell from a target host.

> `Remove`(제거) 행동을 사용하는 목적은 대상 호스트에서 사용자 권한(user) 셸을 제거하는 것입니다.

So let's see from both a blue and red perspective, how this action functions successfully.
In this scenario, red has managed to get a user shell on `restricted_zone_a_subnet_server_host_0`.

> 이제 이 행동이 성공적으로 작동하는 모습을 Blue 에이전트(방어 측)와 Red 에이전트(공격 측) 양쪽 관점에서 살펴보겠습니다.
> 이 시나리오(Scenario)에서 Red는 `restricted_zone_a_subnet_server_host_0`에 사용자 권한 셸을 확보한 상태입니다.

```python
# start with a cyborg environment with a user shell on `restricted_zone_a_subnet_server_host_0`
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='user')
env = cyborg.environment_controller
target_ip = env.state.hostname_ip_map[target_host]

print("Red: Before Remove")
pprint(cyborg.get_observation(agent=red_agent_name[1]))
print("\n")

# Run the Remove action
blue_action = Remove(session=0, agent=blue_agent_name, hostname=target_host)
blue_action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})
assert obs['blue_agent_0']['success'] == True

print("Blue: Remove Step")
pprint(obs['blue_agent_0'])
print("\n")

print("Red: Remove Step")
pprint(obs[red_agent_name[1]] if red_agent_name[1] in cyborg.active_agents else "not an active agents")
```

=== "Red: Before Remove"

    Before the shell is removed, you can tell from red's observation that they have managed to get a red abstract session (shell) with username 'user' (indicating it is a user level shell) on `restricted_zone_a_subnet_server_host_0`. This is the shell that blue will be trying to remove.

    > 셸이 제거되기 전, Red의 관찰값을 보면 `restricted_zone_a_subnet_server_host_0`에 username이 'user'인(즉 사용자 권한 셸임을 나타내는) Red abstract session(셸)을 확보했음을 알 수 있습니다. 바로 이 셸이 Blue가 제거하려는 대상입니다.

    There are no other shells that this agent has in this network.

    > 이 에이전트가 이 네트워크에서 가지고 있는 셸은 이것 외에는 없습니다.

    ??? quote "Code Output"
        ```
        Red: Before Remove
        {'10.0.7.254': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                        'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                        'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 22}],
                                    'process_type': <ProcessType.SSH: 2>},
                                    {'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 22,
                                                        'remote_address': IPv4Address('10.0.157.250'),
                                                        'remote_port': 55532}],
                                    'process_type': <ProcessType.SSH: 2>}],
                        'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                    'agent': 'red_agent_1',
                                    'session_id': 0,
                                    'username': 'user'}],
                        'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                        'OSType': <OperatingSystemType.LINUX: 3>}},
        'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.7.0/24'),
                                                                'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_1',
                                                                'session_id': 0,
                                                                'username': 'user'}],
                                                    'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0'}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```


=== "Blue: Remove Step"

    It is confirmed through blue's observation that their action was successful. But there is nothing in the observation space to indicate that the shell has been removed.

    > Blue의 관찰값을 통해 행동이 성공했음을 확인할 수 있습니다. 다만 관찰값 공간(observation space)에는 셸이 실제로 제거되었음을 알려주는 정보는 따로 들어 있지 않습니다.

    ???+ quote "Code Output"
        ```
        Blue: Remove Step
        {'action': Remove restricted_zone_a_subnet_server_host_0,
        'success': <TernaryEnum.TRUE: 1>}
        ```


=== "Red: Remove Step"
    
    We can confirm through the active agents list in cyborg that the red agent is no longer active.
    This is because their only shell has been removed - if they had another shell, the observation would show that one of the shells had disappeared.

    > CybORG의 활성 에이전트(active agents) 목록을 통해 해당 Red 에이전트가 더 이상 활성 상태가 아님을 확인할 수 있습니다.
    > 이는 그 에이전트가 가진 유일한 셸이 제거되었기 때문입니다. 만약 다른 셸이 더 있었다면, 관찰값에서 셸 중 하나가 사라진 것으로 표시되었을 것입니다.

    ???+ quote "Code Output"
        ```
        Red: Remove Step
        'not an active agents'
        ```

## Attempting to Remove a Root Shell (root 셸 제거 시도하기)
Here is an example of what would happen if blue tried to remove a root shell.

> Blue가 root(루트, 최상위 권한) 셸을 제거하려고 시도하면 어떤 일이 벌어지는지 보여주는 예시입니다.

It only requires changing one line in our python file. Now instead of a user shell, we have a root shell.

> Python 파일에서 단 한 줄만 바꾸면 됩니다. 이제 사용자 권한 셸 대신 root 셸을 가진 상태가 됩니다.

```python
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='root')
```

=== "Red: Before Remove"
    You can see from red's observation that the PrivilegeEscalate action was successfull and they now have a red abstract session (shell) with username 'root' (indicating root level privileges).

    > Red의 관찰값을 보면 PrivilegeEscalate(권한 상승) 행동이 성공했으며, 이제 username이 'root'인(root 수준의 권한을 나타내는) Red abstract session(셸)을 가지고 있음을 알 수 있습니다.

    ??? quote "Code Output"
        ```
        Red: Before Remove
        {'action': PrivilegeEscalate restricted_zone_a_subnet_server_host_0,
        'contractor_network_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.157.254')}]},
        'operational_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.58.254')}]},
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.7.0/24'),
                                                                'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_1',
                                                                'session_id': 0,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

=== "Blue: Remove Step"
    The blue observation is the same as for the user level shell. That is because the `Remove` action has successfully removed any user level shells, there just weren't any to remove.

    > Blue의 관찰값은 사용자 권한 셸일 때와 동일합니다. 이는 `Remove`(제거) 행동이 사용자 권한 셸을 성공적으로 제거하긴 했지만, 애초에 제거할 사용자 권한 셸이 하나도 없었기 때문입니다.

    ???+ quote "Code Output"
        ```
        Blue: Remove Step
        {'action': Remove restricted_zone_a_subnet_server_host_0,
        'success': <TernaryEnum.TRUE: 1>}
        ```

=== "Red: Remove Step"
    You can then see from red's observation that the root shell is still there. This action has been a waste of time for blue.

    > 그 후 Red의 관찰값을 보면 root 셸이 여전히 남아 있는 것을 확인할 수 있습니다. 결국 이 행동은 Blue에게 시간 낭비가 된 셈입니다.

    ???+ quote "Code Output"
        ```
        Red: Remove Step
        {'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.7.0/24'),
                                                                'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_1',
                                                                'session_id': 0,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0'}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```