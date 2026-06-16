# Restore (복원)

`Restore` reimages a host, removing all malicious activity. Any files altered by the Red Agent will be restored to their previous state.

> `Restore`(복원)는 호스트를 다시 이미지화(reimage, 백업 상태로 재설치)하여 모든 악성 활동을 제거합니다. Red 에이전트(공격 측)가 변경한 파일은 모두 이전 상태로 되돌려집니다.

<!-- This function has a flat penalty of -1, representing the downtime of the host. -->

## Red Preamble (Red 에이전트 사전 작업)
The red preamble is the same as for the [Remove](4_Remove.md) tutorial, but with `shell_type='root'`.

> Red 에이전트의 사전 작업은 [Remove](4_Remove.md) 튜토리얼과 동일하지만, `shell_type='root'`(루트 권한 셸)을 사용한다는 점만 다릅니다.

The series of actions is as follows:

> 수행되는 행동(Action) 순서는 다음과 같습니다.
```
DiscoverRemoteSystems 10.0.157.0/24 TRUE
AggressiveServiceDiscovery 10.0.157.254 TRUE
ExploitRemoteService 10.0.157.254 TRUE
PrivilegeEscalate contractor_network_subnet_server_host_0 TRUE
AggressiveServiceDiscovery 10.0.7.254 TRUE
ExploitRemoteService 10.0.7.254 TRUE
PrivilegeEscalate restricted_zone_a_subnet_server_host_0 TRUE
```

## Restore a Host with a Root Shell (루트 셸이 있는 호스트 복원하기)
Here is an example of a blue agent successfully removing a red root level shell from a host.

> 다음은 Blue 에이전트(방어 측)가 호스트에서 Red의 루트 권한 셸(root level shell)을 성공적으로 제거하는 예시입니다.

```python
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='root')
env = cyborg.environment_controller
target_ip = env.state.hostname_ip_map[target_host]

print("Red: Before Restore")
pprint(cyborg.get_observation(agent=red_agent_name[1]))
print("\n")

blue_action = Restore(session=0, agent=blue_agent_name, hostname=target_host)
blue_action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})

assert obs['blue_agent_0']['success'] == True

print("Blue: Restore Step")
pprint(obs['blue_agent_0'])
print("\n")

print("Red: Restore Step")
pprint(obs[red_agent_name[1]] if red_agent_name[1] in cyborg.active_agents else "not an active agents")
```

=== "Red: Before Restore"
    You can see from red's observation that the PrivilegeEscalate action was successfull and they now have a red abstract session (shell) with username 'root' (indicating root level privileges).

    > Red의 관찰값(Observation)을 보면 PrivilegeEscalate(권한 상승) 행동이 성공했고, 이제 사용자명이 'root'(루트 권한을 의미)인 red abstract session(셸)을 확보했음을 알 수 있습니다.

    ??? quote "Code Output"
        ````
        Red: Before Restore
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
    The `Restore` actions executes successfully. Remember that the success is an indication of whether the action has successful run through. In this case everything has been restored from a backup so if it is successful then there is no red presence on the host.

    > `Restore`(복원) 행동이 성공적으로 실행됩니다. 여기서 success(성공)는 행동이 끝까지 정상 수행되었는지를 나타내는 값이라는 점을 기억하세요. 이 경우 모든 것이 백업에서 복원되므로, 성공했다면 해당 호스트에는 Red의 흔적이 남아 있지 않습니다.

    ???+ quote "Code Output"
        ```
        Blue: Restore Step
        {'action': Restore restricted_zone_a_subnet_server_host_0,
        'success': <TernaryEnum.TRUE: 1>}
        ```

=== "Red: Remove Step"
    The contents of cyborg's active agent variable shows that the red is no longer active, due to their only shell being removed.

    > cyborg의 active agent(활성 에이전트) 변수 내용을 보면, Red가 가지고 있던 유일한 셸이 제거되어 더 이상 활성 상태가 아님을 알 수 있습니다.

    ???+ quote "Code Output"
        ```
        Red: Restore Step
        'not an active agents'
        ```