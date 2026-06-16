from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent

""" *Creating Variant Red Agents*

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
            'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
            'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
            'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
            'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
            'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
            'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
            'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
            'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
        }
        return map
```

[한국어]
*변종(Variant) Red 에이전트 만드는 법*

`FiniteStateRedAgent`(유한 상태 기계 기반 Red 에이전트)를 상속해 동작을
바꾸는 변종 에이전트를 정의하는 예시다. 주요 커스터마이즈 지점은 다음과 같다.

- 조정 가능한 변수: `print_action_output`(행동 출력 여부),
  `print_obs_output`(관찰값 출력 여부), `prioritise_servers`(서버 우선 공략 여부).
- `_set_host_state_priority_list`: 호스트 상태별 우선순위를 백분율(0~100)로
  지정한다. 상태 키 의미 — K/KS/KD/U/UD/R/RD 등(K=Known 발견됨, S=Scanned 스캔됨,
  U=User 사용자 권한, R=Root 루트 권한, 끝의 D=Decoy 디코이 관련).
- `_state_transitions_probability`: 각 상태에서 다음 행동(Action)으로 전이할
  확률 매핑을 만든다. 리스트의 각 위치가 특정 행동에 대응하며, `None`은 해당
  상태에서 그 행동이 불가능함을 뜻한다.
"""

class VerboseFSRed(FiniteStateRedAgent):
    """A variant of the FiniteStateRedAgent that outputs success, action and internal observation knowlege to the terminal.
    
    Example:
    ```
    ** Turn 0 for red_agent_0 **
    Action: Initial Observation
    Action Success: UNKNOWN

    Observation:
    {'contractor_network_subnet_user_host_5': {
        'Interface': [{'Subnet': IPv4Network('10.0.171.0/24'),
                        'interface_name': 'eth0',
                        'ip_address': IPv4Address('10.0.171.186')}],
        'Processes': [{'PID': 8888,
                        'username': 'ubuntu'}],
        'Sessions': [{'PID': 8888,
                        'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                        'agent': 'red_agent_0',
                        'session_id': 0,
                        'timeout': 0,
                        'username': 'ubuntu'}],
        'System info': {'Architecture': <Architecture.x64: 2>,
                        'Hostname': 'contractor_network_subnet_user_host_5',
                        'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                        'OSType': <OperatingSystemType.LINUX: 3>,
                        'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                        'position': array([0., 0.])},
        'User Info': [{'Groups': [{'GID': 0}],
                        'username': 'root'},
                        {'Groups': [{'GID': 1}],
                        'username': 'user'}]}}
    Host States:
    {'10.0.171.186': {'hostname': 'contractor_network_subnet_user_host_5',
                    'state': 'U'}}
    ```

    [한국어]
    `FiniteStateRedAgent`의 변종으로, 행동 성공 여부·수행한 행동(Action)·내부
    관찰값(Observation) 정보를 터미널에 출력한다.

    위 예시는 한 턴에서 출력되는 형태를 보여준다. 수행한 Action, 그 성공 여부,
    관찰값 딕셔너리, 그리고 각 호스트의 상태(state)가 함께 표시된다.
    디버깅이나 에이전트 동작 관찰 용도로 쓴다.
    """
    def __init__(self, name=None, np_random=None, agent_subnets=None):
        super().__init__(name=name, np_random=np_random, agent_subnets=agent_subnets)
        # 행동·관찰값 출력을 켜서 매 턴 내부 상태를 터미널에 보여준다
        self.print_action_output = True
        self.print_obs_output = True


class DiscoveryFSRed(FiniteStateRedAgent):
    """An FiniteStateRedAgent variant that aims to prioritise discovery.

    [한국어]
    탐색(discovery)을 우선하도록 설계된 `FiniteStateRedAgent`의 변종.
    호스트 상태 우선순위와 상태 전이 확률을 조정해, 익스플로잇·권한 상승보다
    원격 시스템·서비스 탐색 단계에 비중을 둔다.
    """
    def __init__(self, name=None, np_random=None, agent_subnets=None):
        super().__init__(name=name, np_random=np_random, agent_subnets=agent_subnets)
        self.print_action_output = False
        self.print_obs_output = False
        self.prioritise_servers = True

    def set_host_state_priority_list(self):
        """Returns a custom host priority list, optimised for discovery.

        Returns
        -------
        host_state_priority_list : Dict[str, num]

        [한국어]
        탐색에 최적화된 호스트 상태 우선순위 리스트를 반환한다.
        값이 클수록 해당 상태의 호스트를 먼저 다루며, 발견·스캔 단계(K/S)에
        높은 가중치를 주고 권한 획득 단계(R)에는 0을 주어 탐색을 우선시한다.

        반환값
        -------
        host_state_priority_list : Dict[str, num]
        """
        host_state_priority_list = {
            'K':20, 'KD':20, 
            'S':20, 'SD':20,
            'U':10, 'UD':10, 
            'R':0,  'RD':0
        }
        return host_state_priority_list
    
    def state_transitions_probability(self):
        """Returns a custom state transitions probability matrix, optimised for discovery.

        Returns
        -------
        matrix : Dict[str, List[float]]

        [한국어]
        탐색에 최적화된 상태 전이 확률 행렬을 반환한다.
        키는 현재 상태, 값 리스트의 각 위치는 다음 행동(Action)에 대응하며
        그 값이 전이 확률이다. `None`은 해당 상태에서 불가능한 행동을 뜻한다.
        탐색 단계로의 전이 확률을 높이고 권한 획득 쪽은 0으로 막아, 에이전트가
        탐색에 머무르도록 유도한다.

        반환값
        -------
        matrix : Dict[str, List[float]]
        """

        map = {
            'K'  : [0.25, 0.75, 0.0,  None, None, None, None, None, None],
            'KD' : [None, 1.0,  0.0,  None, None, None, None, None, None],
            'S'  : [0.25, None, None, 0.0,  0.75, None, None, None, None],
            'SD' : [None, None, None, 0.0,  1.0,  None, None, None, None],
            'U'  : [0.0 , None, None, None, None, 1.0 , None, None, 0.0 ],
            'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
            'R'  : [1.0,  None, None, None, None, None, 0.0,  0.0,  0.0 ],
            'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
        }

        return map
