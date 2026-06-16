# Wrappers (래퍼)

## Table Wrappers (테이블 래퍼)

Table Wrappers attempt to use basic logic to infer a human-friendly picture of the state by keeping track of past observations. This allows for a simplified state space and much greater human readibility. 

> Table Wrapper(테이블 래퍼)는 과거 관찰값(Observation)을 추적하면서 기본적인
> 논리를 적용해, 사람이 보기 편한 형태로 상태를 추론해 줍니다. 덕분에 상태
> 공간이 단순해지고 사람이 읽기에 훨씬 쉬워집니다.

### TrueStateTableWrapper

This wrapper contains functions that format the raw true state, gained from the CybORG environment, into tables using the [PrettyTables package](https://pypi.org/project/prettytable/). The raw true state dictionary can instead be returned as a dictionary by the `get_raw_full_true_state()` function.

> 이 래퍼(Wrapper)는 CybORG(Cyber Operations Research Gym) 환경에서 얻은 원시
> 실제 상태(true state)를 [PrettyTables 패키지](https://pypi.org/project/prettytable/)를
> 이용해 표 형태로 변환하는 함수들을 담고 있습니다. 원시 실제 상태 딕셔너리는
> `get_raw_full_true_state()` 함수를 통해 딕셔너리 형태로 그대로 받을 수도
> 있습니다.



This information should not be made available to the agents, as it contains the ground truth of the environment. Part of the CAGE challenges is about dealing with a limited observation space, to mimic real-life. In reality, Blue teams rely heavily on IDS tooling via SIEMS that produce alerts, however the tools can generate false positives alerts or can miss actual indicators of compromise (IoC). This is replicated in CC4.

> 이 정보는 환경의 실제 정답(ground truth)을 담고 있으므로 에이전트(agent)에게
> 제공해서는 안 됩니다. CAGE 챌린지의 핵심 중 하나는 현실을 모사하기 위해
> **제한된 관찰 공간**을 다루는 것입니다. 실제 현장에서 Blue 팀(방어 측)은
> SIEM(보안 정보·이벤트 관리)을 통해 알림을 만들어 내는 IDS(침입 탐지 시스템)
> 도구에 크게 의존합니다. 하지만 이런 도구들은 오탐(false positive) 알림을
> 만들거나, 실제 침해 지표(IoC, Indicator of Compromise)를 놓칠 수도 있습니다.
> CC4(CAGE Challenge 4)에서는 이런 특성을 그대로 재현합니다.

Nevertheless, it is worthwhile for the contestants and development team to have access to this 'true state' information for understanding of the environment and debugging. 

> 그렇지만 환경을 이해하고 디버깅하는 목적에서는, 참가자와 개발팀이 이
> '실제 상태(true state)' 정보에 접근할 수 있는 것이 유용합니다.

`true_state_wrapper_example.py` shows how this wrapper would be implemented:

> `true_state_wrapper_example.py`는 이 래퍼를 어떻게 사용하는지 보여 줍니다.

```python title="true_state_wrapper_example.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent, 
from CybORG.Agents.Wrappers.TrueStateWrapper import TrueStateTableWrapper

steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)
env = TrueStateTableWrapper(cyborg)
cyborg.reset()
```

This wrapper produces 3 types of output: an overview, a process perspective, and an agent perspective. The usage and outputs from these functions are further demonstrated next. The functions are further documented in the [reference section](../../reference/reference.md#outputs-and-wrappers).

> 이 래퍼는 세 가지 유형의 출력을 만듭니다. 전체 개요(overview), 프로세스
> 관점(process perspective), 에이전트 관점(agent perspective)입니다. 각 함수의
> 사용법과 출력 예시는 이어지는 내용에서 더 자세히 설명합니다. 함수에 대한
> 추가 문서는 [reference section](../../reference/reference.md#outputs-and-wrappers)에서
> 확인할 수 있습니다.

=== "Host Overview"
    ```python title="true_state_wrapper_example.py" linenums="15"
    env.print_host_overview_table()
    ```
    The function above makes a single table with these headings:
    
    - **Hostname** - The host's name
    - **IP Address** - The IP address of the host
    - **Sessions** - A list of names of the agents with sessions linked to that host
    - **No. Processes** - The number of processes running on the host

    > 위 함수는 다음 열(heading)을 가진 하나의 표를 만듭니다.
    >
    > - **Hostname** - 호스트의 이름
    > - **IP Address** - 호스트의 IP 주소
    > - **Sessions** - 해당 호스트에 연결된 세션을 가진 에이전트들의 이름 목록
    > - **No. Processes** - 해당 호스트에서 실행 중인 프로세스의 개수

    A reduced output is shown below:

    > 아래는 일부만 추린 출력 예시입니다.

    ???+ quote "Code Output"
        ```
        +-----------------------------------------+--------------+------------------------------------+---------------+
        |                 Hostname                |  IP Address  |              Sessions              | No. Processes |
        +-----------------------------------------+--------------+------------------------------------+---------------+
        |     restricted_zone_a_subnet_router     | 10.0.26.209  |          ['blue_agent_0']          |       1       |
        |   restricted_zone_a_subnet_user_host_0  |  10.0.26.88  | ['blue_agent_0', 'green_agent_0']  |       3       |
        |   restricted_zone_a_subnet_user_host_1  |  10.0.26.43  | ['blue_agent_0', 'green_agent_1']  |       5       |
        |   restricted_zone_a_subnet_user_host_2  | 10.0.26.173  | ['blue_agent_0', 'green_agent_2']  |       5       |
        |  restricted_zone_a_subnet_server_host_0 | 10.0.26.254  |          ['blue_agent_0']          |       5       |
        |  restricted_zone_a_subnet_server_host_1 | 10.0.26.253  |          ['blue_agent_0']          |       4       |
        |  restricted_zone_a_subnet_server_host_2 | 10.0.26.252  |          ['blue_agent_0']          |       2       |
        |     operational_zone_a_subnet_router    | 10.0.27.208  |          ['blue_agent_1']          |       1       |
        |  operational_zone_a_subnet_user_host_0  | 10.0.27.142  | ['blue_agent_1', 'green_agent_5']  |       6       |
        |                   ...                   |     ...      |                ...                 |      ...      |
        |           root_internet_host_0          | 10.0.30.214  |                 -                  |       0       |
        +-----------------------------------------+--------------+------------------------------------+---------------+
        ```
    

    ---

=== "Host Processes"
    ```python title="true_state_wrapper_example.py" linenums="16"
    env.print_host_processes_tables()
    ```
    The function above makes multiple tables, one for each subnet.
    
    The tables have the following headings:
    
    - **Hostname** - The host's name
    - **PID** - The process identifier
    - **Name** - The process name
    - **Type** - The process type
    - **Username** - The username associated with the process
    - **Sessions** - The name of the agent with linked to that host PID (if it exists)
    - **SID** - The session identifier linked to the PID (if it exists)

    > 위 함수는 서브넷(Subnet)마다 하나씩, 여러 개의 표를 만듭니다.
    >
    > 각 표는 다음 열을 가집니다.
    >
    > - **Hostname** - 호스트의 이름
    > - **PID** - 프로세스 식별자(process identifier)
    > - **Name** - 프로세스 이름
    > - **Type** - 프로세스 유형
    > - **Username** - 해당 프로세스와 연결된 사용자 이름
    > - **Sessions** - 해당 호스트의 PID에 연결된 에이전트의 이름 (존재하는 경우)
    > - **SID** - 해당 PID에 연결된 세션 식별자(session identifier) (존재하는 경우)

    A reduced output is shown below:

    > 아래는 일부만 추린 출력 예시입니다.
    ???+ quote "Code Output"
        ```
        Host Processes Table: Subnet RESTRICTED_ZONE_A 

        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |                Hostname                | PID  |         Name        |    Type   | Username |    Session    | SID |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |    restricted_zone_a_subnet_router     |  8   |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  1  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |  restricted_zone_a_subnet_user_host_0  | 7515 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                   "                    | 7519 |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  2  |
        |                   "                    | 7526 |     GREY_SESSION    |     -     |  ubuntu  | green_agent_0 |  0  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |  restricted_zone_a_subnet_user_host_1  | 9481 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                   "                    | 3814 |  ProcessName.MYSQLD |   MYSQL   |   user   |       -       |  -  |
        |                   "                    | 8111 | ProcessName.APACHE2 | WEBSERVER |   user   |       -       |  -  |
        |                   "                    | 9487 |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  3  |
        |                   "                    | 9496 |     GREY_SESSION    |     -     |  ubuntu  | green_agent_1 |  0  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |  restricted_zone_a_subnet_user_host_2  | 6161 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                   "                    | 1062 | ProcessName.APACHE2 | WEBSERVER |   user   |       -       |  -  |
        |                   "                    | 3599 |  ProcessName.MYSQLD |   MYSQL   |   user   |       -       |  -  |
        |                   "                    | 6168 |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  4  |
        |                   "                    | 6177 |     GREY_SESSION    |     -     |  ubuntu  | green_agent_2 |  0  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        | restricted_zone_a_subnet_server_host_0 | 7770 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                  ...                   | ...  |          ...        |    ...    |   ...    |      ...      | ... |

        ```
    ---

=== "Agent Sessions"
    ```python title="true_state_wrapper_example.py" linenums="17"
    env.print_agent_session_tables()
    ```
    The function above makes multiple tables, one for each agent type (red, blue, green).
    
    The tables have the following headings:
    
    - **Agent** - The agent name
    - **SID** - The session identifier for the agent
    - **Hostname** - The name of the host that the agent has a session on
    - **Username** - The username associated with the session
    - **Type** - The session type
    - **PID** - The process identifier associated with the session

    > 위 함수는 에이전트 유형(red, blue, green)마다 하나씩, 여러 개의 표를
    > 만듭니다.
    >
    > 각 표는 다음 열을 가집니다.
    >
    > - **Agent** - 에이전트 이름
    > - **SID** - 해당 에이전트의 세션 식별자(session identifier)
    > - **Hostname** - 해당 에이전트가 세션을 가진 호스트의 이름
    > - **Username** - 해당 세션과 연결된 사용자 이름
    > - **Type** - 세션 유형
    > - **PID** - 해당 세션과 연결된 프로세스 식별자(process identifier)

    A reduced output is shown below:

    > 아래는 일부만 추린 출력 예시입니다.
    ???+ quote "Code Output"
        ```
        Agent Session Table: Team red 

        +-------------+-----+---------------------------------------+----------+----------------------+------+
        |    Agent    | SID |                Hostname               | Username |         Type         | PID  |
        +-------------+-----+---------------------------------------+----------+----------------------+------+
        | red_agent_0 |  0  | contractor_network_subnet_user_host_2 |  ubuntu  | RED_ABSTRACT_SESSION | 9267 |
        +-------------+-----+---------------------------------------+----------+----------------------+------+
        

        Agent Session Table: Team blue 

        +--------------+-----+-----------------------------------------+----------+---------------------+------+
        |    Agent     | SID |                 Hostname                | Username |         Type        | PID  |
        +--------------+-----+-----------------------------------------+----------+---------------------+------+
        | blue_agent_0 |  0  |  restricted_zone_a_subnet_server_host_1 |  ubuntu  | VELOCIRAPTOR_SERVER | 9811 |
        |      -       |  1  |     restricted_zone_a_subnet_router     |  ubuntu  |       UNKNOWN       |  8   |
        |      -       |  2  |   restricted_zone_a_subnet_user_host_0  |  ubuntu  |       UNKNOWN       | 7519 |
        |      -       |  3  |   restricted_zone_a_subnet_user_host_1  |  ubuntu  |       UNKNOWN       | 9487 |
        |      -       |  4  |   restricted_zone_a_subnet_user_host_2  |  ubuntu  |       UNKNOWN       | 6168 |
        |      -       |  7  |  restricted_zone_a_subnet_server_host_0 |  ubuntu  |       UNKNOWN       | 7778 |
        |      -       |  8  |  restricted_zone_a_subnet_server_host_2 |  ubuntu  |       UNKNOWN       | 4345 |
        +--------------+-----+-----------------------------------------+----------+---------------------+------+
        | blue_agent_1 |  1  |     operational_zone_a_subnet_router    |  ubuntu  |       UNKNOWN       |  9   |
        |     ...      | ... |                   ...                   |   ...    |         ...         | ...  |
        ```
    ---


## Blue Wrappers (Blue 래퍼)

### BlueFixedActionWrapper
This wrapper enumerates the full action space for each Blue agent in the scenario and establishes a fixed integer-to-action mapping that is consistent across runs. Since the number of hosts and the IP addresses of each host varies between episodes, this wrapper updates the list of actions available to the agent at the start of every episode. Action indices will always correspond to a specific action against a specific host, regardless of IP address. If a host is not included in a given episode, the action is replaced with a `Sleep` placeholder and the action label is marked with an `[Invalid]` prefix.

> 이 래퍼는 시나리오(Scenario) 안의 각 Blue 에이전트(방어 측)에 대해 전체
> 행동 공간(Action Space)을 나열하고, 실행할 때마다 일관되게 유지되는
> **정수-행동 매핑(integer-to-action mapping)**을 정해 줍니다. 호스트(Host)의
> 개수와 각 호스트의 IP 주소는 에피소드(Episode)마다 달라지므로, 이 래퍼는 매
> 에피소드 시작 시점에 에이전트가 쓸 수 있는 행동 목록을 갱신합니다. 행동
> 인덱스는 IP 주소와 무관하게 언제나 **특정 호스트에 대한 특정 행동**에
> 대응합니다. 어떤 에피소드에 특정 호스트가 포함되지 않으면, 그 행동은 `Sleep`
> 자리표시자로 대체되고 행동 레이블에는 `[Invalid]` 접두사가 붙습니다.

The `step` function accepts actions as `dict[str, int]` where the key is the agent name and the value is an index corresponding to
an action within the agent's action space. A few convenience functions are provided by this wrapper to help understand the
integer-to-action mapping and avoid temporarily invalid actions:

> `step` 함수는 행동을 `dict[str, int]` 형태로 받습니다. 여기서 키(key)는
> 에이전트 이름이고, 값(value)은 해당 에이전트의 행동 공간 안에서 하나의
> 행동을 가리키는 인덱스입니다. 이 래퍼는 정수-행동 매핑을 이해하고 일시적으로
> 무효한(invalid) 행동을 피하도록 돕는 몇 가지 편의 함수를 제공합니다.

=== "action_space(agent)"

    This function returns a `gymnasium.space.Discrete` with the maximum size of the agent's action space.

    > 이 함수는 에이전트 행동 공간의 최대 크기를 담은 `gymnasium.space.Discrete`를
    > 반환합니다.

    ```python
    >>> env.action_space('blue_agent_0')
    Discrete(82)
    ```

=== "action_labels(agent)"

    Returns an ordered list of human-readable action labels.
    The `[Invalid]` prefix means that this action is temporarily unavailable for the duration of the episode.
    The order of this list will always be consistent.

    > 사람이 읽을 수 있는 행동 레이블을 순서가 정해진 리스트로 반환합니다.
    > `[Invalid]` 접두사는 해당 행동이 그 에피소드 동안 일시적으로 사용
    > 불가능함을 의미합니다. 이 리스트의 순서는 언제나 일관되게 유지됩니다.

    ```python
    [
        'Analyse restricted_zone_a_subnet_server_host_0',
        'Analyse restricted_zone_a_subnet_server_host_1',
        'Analyse restricted_zone_a_subnet_server_host_2',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_3',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_4',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_5',
        'Analyse restricted_zone_a_subnet_user_host_0',
        'Analyse restricted_zone_a_subnet_user_host_1',
        'Analyse restricted_zone_a_subnet_user_host_2',
        'Analyse restricted_zone_a_subnet_user_host_3',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_4',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_5',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_6',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_7',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_8',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_9',
        'Monitor',
        'Remove restricted_zone_a_subnet_server_host_0',
        'Remove restricted_zone_a_subnet_server_host_1',
        'Remove restricted_zone_a_subnet_server_host_2',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_3',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_4',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_5',
        'Remove restricted_zone_a_subnet_user_host_0',
        'Remove restricted_zone_a_subnet_user_host_1',
        'Remove restricted_zone_a_subnet_user_host_2',
        'Remove restricted_zone_a_subnet_user_host_3',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_4',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_5',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_6',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_7',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_8',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_9',
        'Restore restricted_zone_a_subnet_server_host_0',
        'Restore restricted_zone_a_subnet_server_host_1',
        'Restore restricted_zone_a_subnet_server_host_2',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_3',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_4',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_5',
        'Restore restricted_zone_a_subnet_user_host_0',
        'Restore restricted_zone_a_subnet_user_host_1',
        'Restore restricted_zone_a_subnet_user_host_2',
        'Restore restricted_zone_a_subnet_user_host_3',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_4',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_5',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_6',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_7',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_8',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_9',
        'Sleep',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- admin_network_subnet (10.0.57.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- contractor_network_subnet (10.0.184.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- internet_subnet (10.0.163.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- office_network_subnet (10.0.50.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_a_subnet (10.0.133.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_b_subnet (10.0.24.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- public_access_zone_subnet (10.0.63.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- restricted_zone_b_subnet (10.0.210.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- admin_network_subnet (10.0.57.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- contractor_network_subnet (10.0.184.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- internet_subnet (10.0.163.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- office_network_subnet (10.0.50.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_a_subnet (10.0.133.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_b_subnet (10.0.24.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- public_access_zone_subnet (10.0.63.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- restricted_zone_b_subnet (10.0.210.0/24)',
        'DeployDecoy restricted_zone_a_subnet_server_host_0',
        'DeployDecoy restricted_zone_a_subnet_server_host_1',
        'DeployDecoy restricted_zone_a_subnet_server_host_2',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_3',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_4',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_5',
        'DeployDecoy restricted_zone_a_subnet_user_host_0',
        'DeployDecoy restricted_zone_a_subnet_user_host_1',
        'DeployDecoy restricted_zone_a_subnet_user_host_2',
        'DeployDecoy restricted_zone_a_subnet_user_host_3',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_4',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_5',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_6',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_7',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_8',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_9'
    ]
    ```

=== "action_mask(agent)"

    Returns a list of booleans corresponding to whether an action can be executed in a given episode.
    This list is also included in the `info` dictionary returned by `reset()` and `step()`.

    > 어떤 행동이 그 에피소드에서 실행 가능한지를 나타내는 불리언(boolean)
    > 리스트를 반환합니다. 이 리스트는 `reset()`과 `step()`이 반환하는 `info`
    > 딕셔너리에도 포함됩니다.

    ```python
    >>> env.action_mask('blue_agent_0')
    [ True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False ]
    ```

???+ Note "Action Space Padding"
    By default, the action space of each agent corresponds to the size of the agent's
    full action space, however, some libraries require all agents to have the same
    action space size. In this case, the `pad_spaces = True` argument can be passed
    to the wrapper to pad the action spaces of each agent with `Sleep` actions. These
    will actions will have a `[Padding]` prefix in the list of action labels and have
    a mask value of `False`.

    > 기본적으로 각 에이전트의 행동 공간(Action Space)은 그 에이전트의 전체 행동
    > 공간 크기와 같습니다. 하지만 일부 라이브러리는 모든 에이전트가 동일한 행동
    > 공간 크기를 갖기를 요구합니다. 이 경우 래퍼에 `pad_spaces = True` 인자를
    > 넘기면, 각 에이전트의 행동 공간을 `Sleep` 행동으로 채워(padding) 크기를
    > 맞춥니다. 이렇게 채워진 행동들은 행동 레이블 리스트에서 `[Padding]` 접두사를
    > 가지며, 마스크 값은 `False`가 됩니다.

### BlueFlatWrapper

This wrapper is an extension of the `BlueFixedActionWrapper` that flattens the CybORG
observation into a vector of fixed-size and fixed-order for training RL agents.
A full breakdown of how the observation vectors are structured is available at
[Appendix B](../../README.md#appendix-b-agent-observation).

> 이 래퍼는 `BlueFixedActionWrapper`를 확장한 것으로, 강화학습(RL,
> Reinforcement Learning) 에이전트 학습을 위해 CybORG 관찰값(Observation)을
> 크기와 순서가 고정된 벡터로 평탄화(flatten)합니다. 관찰값 벡터가 어떻게
> 구성되는지에 대한 전체 설명은
> [Appendix B](../../README.md#appendix-b-agent-observation)에서 볼 수 있습니다.

???+ Note "Observation Space Padding"
    Setting `pad_spaces = True` will pad the observation vector of each agent to the
    largest observation space by filling the remaining space with zeros. This will
    also pad the action space as needed.

    > `pad_spaces = True`로 설정하면, 각 에이전트의 관찰값 벡터를 가장 큰 관찰
    > 공간(observation space) 크기에 맞춰 남는 자리를 0으로 채워(padding) 줍니다.
    > 이때 필요에 따라 행동 공간도 함께 채워집니다.

### BlueEnterpriseWrapper

`BlueEnterpriseWrapper` is an alias of `BlueFlatWrapper`.

> `BlueEnterpriseWrapper`는 `BlueFlatWrapper`의 별칭(alias)입니다.


## Library-Specific Wrappers (라이브러리별 전용 래퍼)
If you are utilising a machine learning library, such as TensorFlow, PyTorch, or Scikit-learn, you may need to create a library specific wrapper to interface between CybORG and your library of choice in order to create/train your algorithm.

> TensorFlow, PyTorch, Scikit-learn 같은 머신러닝 라이브러리를 사용한다면,
> 알고리즘을 만들거나 학습시키기 위해 CybORG와 사용하는 라이브러리를 연결해 줄
> **라이브러리별 전용 래퍼**를 직접 만들어야 할 수 있습니다.

**We highly encourage solutions made incorporating ML and hope that this documentation can help you with this task.**

> **머신러닝(ML)을 접목한 솔루션을 적극 권장하며, 이 문서가 그 작업에 도움이
> 되기를 바랍니다.**

Unfortunately we cannot create wrappers for everyone, so we have created one for RLlib - a widely used python reinforcement learning library - and hope that this example will be a sufficient basis when making your own.

> 모두를 위한 래퍼를 일일이 만들어 드릴 수는 없으므로, 널리 쓰이는 파이썬
> 강화학습 라이브러리인 **RLlib**용 래퍼를 하나 만들어 두었습니다. 이 예시가
> 여러분이 직접 래퍼를 만들 때 충분한 출발점이 되기를 바랍니다.

### EnterpriseMAE
This wrapper is a `BlueEnterpriseWrapper` that is compatible with RLlib's `MultiAgentEnv` class to interface between CybORG and RLlib agents.

> 이 래퍼는 CybORG와 RLlib 에이전트를 연결하기 위해 RLlib의 `MultiAgentEnv`
> 클래스와 호환되도록 만든 `BlueEnterpriseWrapper`입니다.

A step-by-step guide for getting started with this wrapper is available in [Tutorial 1 - Training RLlib Agents](../01_Getting_Started/3_Training_Agents.md).

> 이 래퍼를 시작하는 단계별 가이드는
> [Tutorial 1 - Training RLlib Agents](../01_Getting_Started/3_Training_Agents.md)에서
> 확인할 수 있습니다.
