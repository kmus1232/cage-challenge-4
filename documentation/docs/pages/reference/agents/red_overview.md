# Red Overview (Red 에이전트 개요)
In this challenge the red agents are the attackers, and aim to interfere with green actions; causing blue to receive negative rewards.

> 이 챌린지에서 Red 에이전트(공격 측)는 공격자이며, Green 에이전트(정상 사용자)의 행동을 방해하는 것을 목표로 합니다. 그 결과 Blue 에이전트(방어 측)는 음의 보상을 받게 됩니다.

## Red Agent Actions (Red 에이전트 행동)
Red agents have 10 possible actions that they can perform during an episode:

> Red 에이전트는 한 에피소드 동안 수행할 수 있는 행동(Action)을 10가지 가지고 있습니다.

| Index | Action | Description |
| ------| ------ | ----------- |
| 0     | [DiscoverRemoteSystems](../actions/red_actions/discover_remote_systems.md) | Discovers the IP addresses of the other hosts in the subnet. |
| 1     | [AggressiveServiceDiscovery](../actions/red_actions/discover_network_services.md) | Discovers the services present on a specific known host. This is faster but more likely to alert Blue. |
| 2     | [StealthServiceDiscovery](../actions/red_actions/discover_network_services.md) | Discovers the services present on a specific known host. This is slower but less likely to alert Blue. |
| 3     | [DiscoverDeception](../actions/red_actions/detect_decoy.md) | Discovers if there are any decoys present on a specific host. |
| 4     | [ExploitRemoteService_cc4](../actions/red_actions/exploit_remote_service.md) | Exploits a service on a specific host to gain a user privileged shell. |
| 5     | [PrivilegeEscalate](../actions/red_actions/privilege_escalate.md) | Carries out an exploit on a specific host that the agent has a user shell on, to gain a shell with root privileges. |
| 6     | [Impact](../actions/red_actions/impact.md) | Impacts an operational service which is important to the mission. |
| 7     | [DegradeServices](../actions/red_actions/degrade_services.md) | Degrades a service used by green in the mission. |
| 8     | [Withdraw](../actions/red_actions/withdraw.md) | Withdraws a shell from a specific host. |
| -     | [Sleep](../../tutorials/03_Actions/A_Understanding_Actions/3_Sleep.md) | The turn passes with no impact to the environment. |

> 위 표를 한국어로 옮기면 다음과 같습니다. 액션 이름과 링크는 식별자이므로 영어를 그대로 둡니다.

| Index(색인) | Action(행동) | Description(설명) |
| ------| ------ | ----------- |
| 0     | [DiscoverRemoteSystems](../actions/red_actions/discover_remote_systems.md) | 서브넷 안에 있는 다른 호스트들의 IP 주소를 탐색합니다. |
| 1     | [AggressiveServiceDiscovery](../actions/red_actions/discover_network_services.md) | 이미 알고 있는 특정 호스트에서 동작 중인 서비스를 탐색합니다. 속도는 빠르지만 Blue 에이전트에게 탐지될 가능성이 더 큽니다. |
| 2     | [StealthServiceDiscovery](../actions/red_actions/discover_network_services.md) | 이미 알고 있는 특정 호스트에서 동작 중인 서비스를 탐색합니다. 속도는 느리지만 Blue 에이전트에게 탐지될 가능성이 더 작습니다. |
| 3     | [DiscoverDeception](../actions/red_actions/detect_decoy.md) | 특정 호스트에 Decoy(디코이, 미끼)가 있는지 탐지합니다. |
| 4     | [ExploitRemoteService_cc4](../actions/red_actions/exploit_remote_service.md) | 특정 호스트의 서비스를 익스플로잇(원격 서비스 공격)하여 사용자 권한 셸(shell)을 획득합니다. |
| 5     | [PrivilegeEscalate](../actions/red_actions/privilege_escalate.md) | 이미 사용자 셸을 확보한 특정 호스트에서 익스플로잇을 수행하여 root(루트) 권한 셸을 획득합니다. |
| 6     | [Impact](../actions/red_actions/impact.md) | 임무에 중요한 운영 서비스에 타격(Impact)을 가합니다. |
| 7     | [DegradeServices](../actions/red_actions/degrade_services.md) | 임무 수행 중 Green 에이전트가 사용하는 서비스의 성능을 저하시킵니다. |
| 8     | [Withdraw](../actions/red_actions/withdraw.md) | 특정 호스트에서 셸을 철수(Withdraw)시킵니다. |
| -     | [Sleep](../../tutorials/03_Actions/A_Understanding_Actions/3_Sleep.md) | 환경에 아무런 영향도 주지 않고 해당 턴을 넘깁니다. |

Note: Sleep is not considered as an action for the FSM agents, and therefore has no index.

> 참고: Sleep은 FSM(유한 상태 기계) 에이전트에서는 행동으로 취급되지 않으며, 따라서 색인(index)이 없습니다.

## Spreading Mechanisms (확산 메커니즘)

Red agents have two methods of spreading through the network:

> Red 에이전트가 네트워크 전반으로 확산하는 방법은 두 가지입니다.

1. Subnet 'server_host_0' takeover

2. Green-enabled vulnerability

> 1. 서브넷 'server_host_0' 탈취
>
> 2. Green 에이전트로 인해 가능해지는 취약점(Green-enabled vulnerability)

### Subnet 'server_host_0' Takeover (서브넷 'server_host_0' 탈취)
Each 'server_host_0' for every subnet contains hidden knowledge about the rest of the server_0's, that it is connected to, in the network. Therefore, when the red agent gains a root shell on the 'server_host_0', its observation space holds the hostnames and ip_addresses of additional hosts outside the subnet.

> 모든 서브넷의 각 'server_host_0'은 네트워크 안에서 자신과 연결된 다른 server_0들에 대한 숨겨진 정보를 가지고 있습니다. 따라서 Red 에이전트가 'server_host_0'에서 root 셸을 획득하면, 그 관찰값(Observation) 공간에 해당 서브넷 바깥에 있는 추가 호스트들의 호스트명과 IP 주소가 담기게 됩니다.

Here is an example of what that may look like:

> 다음은 그 예시입니다.

```
** Turn # for red_agent_0 **
Action: PrivilegeEscalate contractor_network_subnet_server_host_0
Action Success: TRUE

Observation:
{<current contractor_network_subnet sessions>,
 'public_access_zone_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.29.254')}]},
 'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.88.254')}]},
 'restricted_zone_b_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.87.254')}]}}
```

### Green-enabled Vulnerability (Green 에이전트로 인해 가능해지는 취약점)

Green agents, just like regular users on the network, can be a vector in red spreading. In this case, green does an action on its turn that results in a red shell being created on the host.

> Green 에이전트는 네트워크상의 일반 사용자와 마찬가지로 Red 에이전트가 확산하는 경로(vector)가 될 수 있습니다. 이 경우 Green 에이전트가 자기 턴에 어떤 행동을 수행하고, 그 결과로 호스트에 Red 에이전트의 셸이 생성됩니다.

The green action that causes this is [Phishing Email](../actions/green_actions/phishing_email.md) - a subaction of [Local Work](../actions/green_actions/local_work.md).

> 이를 유발하는 Green 에이전트의 행동은 [Phishing Email](../actions/green_actions/phishing_email.md)(피싱 이메일)이며, 이는 [Local Work](../actions/green_actions/local_work.md)의 하위 행동(subaction)입니다.

## Available Agents (사용 가능한 에이전트)
A number of red agents can be used with this challenge's scenario:

> 이 챌린지의 시나리오에서는 여러 종류의 Red 에이전트를 사용할 수 있습니다.

| Agent | Description |
| ----- | ----------- |
| [DiscoveryFSRed](./DiscoveryFSRed.md) | A FiniteStateRedAgent variant that specialises in spreading through the network. |
| [FiniteStateRedAgent](./FiniteStateRedAgent.md) | A red agent that uses finite state machine transitions to determine what actions to take for each known host. |
| [LinearAgent](./LinearAgent.md) | An agent designed for testing, that allows you to input a specific list of actions for an agent, which allows you to see how the environment reacts and responds. |
| [RandomSelectRedAgent](./RandomSelectRedAgent.md) | A red agent which randomly chooses which host to act on and what action to act with. |
| [VerboseFSRed](./VerboseFSRed.md) | A FiniteStateRedAgent variant that outputs its internal knowledge to the terminal. Useful for debugging. |

> 위 표를 한국어로 옮기면 다음과 같습니다. 에이전트 이름과 링크는 식별자이므로 영어를 그대로 둡니다.

| Agent(에이전트) | Description(설명) |
| ----- | ----------- |
| [DiscoveryFSRed](./DiscoveryFSRed.md) | 네트워크 전반으로 확산하는 데 특화된 FiniteStateRedAgent 변형입니다. |
| [FiniteStateRedAgent](./FiniteStateRedAgent.md) | 알고 있는 각 호스트에 대해 어떤 행동을 취할지 결정할 때 유한 상태 기계(FSM)의 상태 전이를 사용하는 Red 에이전트입니다. |
| [LinearAgent](./LinearAgent.md) | 테스트용으로 설계된 에이전트로, 에이전트가 수행할 행동 목록을 직접 입력할 수 있어 환경이 어떻게 반응하고 응답하는지 확인할 수 있습니다. |
| [RandomSelectRedAgent](./RandomSelectRedAgent.md) | 어떤 호스트에 대해 어떤 행동을 할지 무작위로 선택하는 Red 에이전트입니다. |
| [VerboseFSRed](./VerboseFSRed.md) | 내부 지식을 터미널에 출력하는 FiniteStateRedAgent 변형입니다. 디버깅에 유용합니다. |

## Finite State Machine Based Red Agents (유한 상태 기계 기반 Red 에이전트)
The red agents that instantiate from the FiniteStateRedAgent, utilise internal Finite State Machines (FSM) to control what actions the agent will choose to do based on the agent's knowledge of that host.

> FiniteStateRedAgent로부터 생성되는 Red 에이전트는 내부의 유한 상태 기계(Finite State Machine, FSM)를 활용합니다. 이 FSM은 에이전트가 특정 호스트에 대해 알고 있는 정보를 바탕으로 어떤 행동을 선택할지 제어합니다.

This results in the agent containing a list of the hosts it knowns about, alongside the 'state' of that host. This variable is called `host_states`. When an action is made on a host, that host's state may transition depending on its success and the knowledge gained.

> 그 결과 에이전트는 자신이 알고 있는 호스트 목록과 함께 각 호스트의 '상태(state)'를 보관하게 됩니다. 이 변수의 이름은 `host_states`입니다. 어떤 호스트에 행동을 수행하면, 그 행동의 성공 여부와 새로 얻은 정보에 따라 해당 호스트의 상태가 전이될 수 있습니다.

![FSM of Red Agents](../../../assets/red_FSM_diagram_3.jpg){ align=center }
*A Finite State Machine of a host that the agent has knowlege/has interacted with. The numbers reference the action list index.*

> *에이전트가 정보를 알고 있거나 상호작용한 적이 있는 호스트의 유한 상태 기계(FSM)입니다. 그림 속 숫자는 행동 목록의 색인(index)을 가리킵니다.*

### Host States (호스트 상태)
There are 9 states that a host can have, which are shown below:

> 호스트가 가질 수 있는 상태는 다음과 같이 9가지입니다.

| Abb.  | Meaning | Description |
| ----  | ------- | ----------- |
| K     | Known | The host IP address is known to the agent. |
| KD    | Known with Discovery | The host IP address is known to the agent and that host's subnet has been discovered. |
| S     | Services | The host's services are known to the agent. |
| SD    | Services with Discovery | The host's services are known to the agent and that host's subnet has been discovered. |
| U     | User shell | The host has a user session/shell on the host. |
| UD    | User shell with Discovery | The host has a user session/shell on the host and that host's subnet has been discovered. |
| R     | Root shell | The host has a root session/shell on the host. |
| RD    | Root shell with Discovery | The host has a root session/shell on the host and that host's subnet has been discovered. |
| F     | Final | An end state where there are no more progressive actions that can be performed on the host. |

> 위 표를 한국어로 옮기면 다음과 같습니다. 상태 약어(K, KD 등)는 식별자이므로 영어를 그대로 둡니다.

| Abb.(약어)  | Meaning(의미) | Description(설명) |
| ----  | ------- | ----------- |
| K     | Known (알려짐) | 에이전트가 해당 호스트의 IP 주소를 알고 있습니다. |
| KD    | Known with Discovery (탐색까지 완료, 알려짐) | 에이전트가 해당 호스트의 IP 주소를 알고 있으며, 그 호스트가 속한 서브넷도 탐색이 완료되었습니다. |
| S     | Services (서비스 파악) | 에이전트가 해당 호스트의 서비스를 알고 있습니다. |
| SD    | Services with Discovery (탐색까지 완료, 서비스 파악) | 에이전트가 해당 호스트의 서비스를 알고 있으며, 그 호스트가 속한 서브넷도 탐색이 완료되었습니다. |
| U     | User shell (사용자 셸) | 해당 호스트에 사용자 세션/셸을 확보한 상태입니다. |
| UD    | User shell with Discovery (탐색까지 완료, 사용자 셸) | 해당 호스트에 사용자 세션/셸을 확보했고, 그 호스트가 속한 서브넷도 탐색이 완료되었습니다. |
| R     | Root shell (root 셸) | 해당 호스트에 root 세션/셸을 확보한 상태입니다. |
| RD    | Root shell with Discovery (탐색까지 완료, root 셸) | 해당 호스트에 root 세션/셸을 확보했고, 그 호스트가 속한 서브넷도 탐색이 완료되었습니다. |
| F     | Final (종료) | 해당 호스트에 대해 더 이상 진행 가능한 행동이 없는 종료 상태입니다. |

### State Transition Matrices (상태 전이 행렬)
State transition matrices dictate to the red agent how to move from one state to another, to advance its internal knowledge and hold over the network. 

> 상태 전이 행렬(State Transition Matrices)은 Red 에이전트가 한 상태에서 다른 상태로 어떻게 이동할지를 규정합니다. 이를 통해 에이전트는 내부 지식을 넓히고 네트워크에 대한 장악력을 키워 갑니다.

Three state transition matrices are needed to account for all outcomes:

> 가능한 모든 결과를 다루려면 세 가지 상태 전이 행렬이 필요합니다.

- **Success** - for the host state transition when the action is successful.

- **Failure** - for the host state transition when the action fails.

- **Probability** - for the probability that each possible action is chosen when a host state is picked.

> - **Success(성공)** — 행동이 성공했을 때의 호스트 상태 전이를 담당합니다.
>
> - **Failure(실패)** — 행동이 실패했을 때의 호스트 상태 전이를 담당합니다.
>
> - **Probability(확률)** — 특정 호스트 상태가 선택되었을 때, 가능한 각 행동이 선택될 확률을 담당합니다.

In the code, these are stored in dictionaries of strings for the success and failure, and floats of values 0.0 to 1.0 for the probabilities. The success matrix reflects the FSM diagram, in a machine-readable format. 

> 코드에서는 success와 failure 행렬을 문자열 딕셔너리(dictionary)로, probability 행렬을 0.0에서 1.0 사이의 부동소수점(float) 값으로 저장합니다. success 행렬은 앞의 FSM 다이어그램을 기계가 읽을 수 있는 형식으로 옮긴 것입니다.

To create further FSM red variants, the probabilty matrix can be modified. It is important that all rows sum to 1.0. Here is an example:

> 새로운 FSM Red 에이전트 변형을 만들려면 probability 행렬을 수정하면 됩니다. 이때 각 행(row)의 합이 1.0이 되어야 한다는 점이 중요합니다. 다음은 그 예시입니다.

```python
map = {
    'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
    'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
    'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
    'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
    'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
    'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
    'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
    'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
}
```

### Host Priority (호스트 우선순위)
By default, the host that the red agent performs that action on is completely random. However two mechanisms have been added to facilitate variants being able to 'intelligently' choose what host to act on, before picking the action.

> 기본적으로 Red 에이전트가 행동을 수행할 호스트는 완전히 무작위로 정해집니다. 다만, 변형 에이전트가 행동을 고르기 전에 어떤 호스트를 대상으로 삼을지 '지능적으로' 선택할 수 있도록 두 가지 메커니즘이 추가되었습니다.

These are:

> 두 가지 메커니즘은 다음과 같습니다.

1. Prioritising servers
    - Servers are given a higher probability of being picked as the choosen host (75%) over other hosts.
    - Servers are what red want to impact and how they get additional spreading information, so this can be useful to do.

2. Prioritising host states
    - A dictionary of host states and their percentage chance of being chosen is created, and the probability the hosts are chosen are based off their states.
    - Note that if no hosts are known with states of >0%, 0% chance states are included.

> 1. 서버 우선(Prioritising servers)
>     - 서버는 다른 호스트보다 대상 호스트로 선택될 확률을 더 높게(75%) 부여받습니다.
>     - 서버는 Red 에이전트가 타격하고 싶어 하는 대상이자, 추가적인 확산 정보를 얻는 통로이므로 이렇게 하는 것이 유리할 수 있습니다.
>
> 2. 호스트 상태 우선(Prioritising host states)
>     - 호스트 상태와 그 상태가 선택될 백분율(%)을 담은 딕셔너리를 만들고, 호스트가 선택될 확률을 각 호스트의 상태에 따라 결정합니다.
>     - 참고: 확률이 0%보다 큰 상태에 해당하는 호스트가 하나도 알려져 있지 않은 경우에는 0% 확률의 상태도 후보에 포함됩니다.

### Creating Variant FSM Red Agents (변형 FSM Red 에이전트 만들기)
Here is a template for creating a variant FSM red agent.

> 다음은 변형 FSM Red 에이전트를 만들기 위한 템플릿입니다.

```python
class MyVariant(FiniteStateRedAgent):
    def __init__(self, name=None, np_random=None, agent_subnets=None):
        super().__init__(name=name, np_random=np_random, agent_subnets=agent_subnets)

        # Changable variables:
        self.print_action_output = False
        self.print_obs_output = False
        self.prioritise_servers = False

    def _set_host_state_priority_list(self):
        # percentage choice
        new_host_state_priority_list = {'K':(0->100), 'KS':?, 'KD':?, 'U':?, 'UD':?, 'R':?, 'RD':?}
        return None
    
    def _state_transitions_probability(self):
        # Create new probability mapping to use
        map = {
            'K'  : [None, 0.5 , 0.5 , None, None, None, None, None, None],
            'KS' : [None, None, None, 0.25, 0.75, None, None, None, None],
            'KD' : [None, None, None, 0.25, 0.75, None, None, None, None],
            'U'  : [0.2 , None, None, None, None, 0.8 , None, None, None],
            'UD' : [None, None, None, None, None, 1.0 , None, None, None],
            'R'  : [0.2 , None, None, None, None, None, 0.4 , 0.4 , None],
            'RD' : [None, None, None, None, None, None, 0.5 , 0.5 , None],
            'F'  : [None, None, None, None, None, None, None, None, None]
        }
        return map
```
