
# Sleep - The Universal Action (Sleep - 공용 행동)

Sleep is a valid action for all agents, and results in the agent not choosing to affect the environment on their turn.
The action also does not require any parameters to be performed.

> Sleep는 모든 에이전트가 쓸 수 있는 유효한 행동(Action)으로, 해당 에이전트가 자기 차례에 환경(environment)에
> 아무런 영향을 주지 않기로 선택한 결과가 됩니다.
> 또한 이 행동은 수행하는 데 어떤 파라미터도 필요하지 않습니다.

```python title="example_sleep_action.py" linenums="18"
example_action = Sleep()

results = cyborg.step(agent=example_agent_name, action=example_action)
pprint(results.observation)
```


However, the returned observations vary slightly between the different agent types, as can be seen below.

> 다만 반환되는 관찰값(Observation)은 아래에서 볼 수 있듯이 에이전트 종류에 따라 조금씩 달라집니다.

=== "'blue_agent_0'" 
    ``` shell
    {'action': Sleep, 'success': <TernaryEnum.UNKNOWN: 2>}
    ```

=== "'red_agent_0'"
    ``` shell
    {'action': Sleep,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

=== "'green_agent_0'"
    ``` shell
    {'action': Sleep, 'success': <TernaryEnum.UNKNOWN: 2>}
    ```

All agents have the same action and success value, however red receives information about what active shell sessions it has in the environment.

> 모든 에이전트는 동일한 `action` 값과 `success` 값을 받습니다. 다만 Red 에이전트(공격 측)는 자신이 환경 안에서
> 보유한 활성 셸 세션(Session)이 무엇인지에 대한 정보를 추가로 받습니다.

> **위 탭별 관찰값(Observation) 해설**
>
> 세 개의 탭(`=== "..."`)은 각각 Blue/Red/Green 에이전트가 Sleep 행동을 했을 때 받는 관찰값 딕셔너리를 보여줍니다.
> 공통으로 등장하는 키의 의미는 다음과 같습니다.
>
> - `action`: 수행된 행동의 종류. 여기서는 모두 `Sleep`입니다.
> - `success`: 행동의 성공 여부. `<TernaryEnum.UNKNOWN: 2>`는 "성공/실패를 알 수 없음"을 뜻하는 3치 열거값(Ternary Enum)입니다. Sleep는 환경에 영향을 주지 않으므로 성공 여부가 정의되지 않습니다.
>
> Red 에이전트의 관찰값에만 추가로 들어 있는 키는 다음과 같습니다.
>
> - `contractor_network_subnet_user_host_4`: Red 에이전트가 세션을 보유한 호스트(Host) 이름이며, 그 값으로 해당 호스트의 정보를 담습니다.
> - `Interface`: 호스트의 네트워크 인터페이스 정보로, 소속 서브넷(`Subnet`)과 IP 주소(`ip_address`)를 담습니다.
> - `Sessions`: 해당 호스트에서 Red 에이전트가 가진 활성 셸 세션 목록. 세션 종류(`Type`), 소유 에이전트(`agent`), 세션 ID(`session_id`), 사용자명(`username`)을 포함합니다.
> - `System info`: 호스트의 시스템 정보로, 여기서는 호스트명(`Hostname`)을 담습니다.