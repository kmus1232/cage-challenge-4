# The Action Space (행동 공간)

Without the use of wrappers,  CybORG actions need to be constructed by the agent before being passed in.

> 래퍼(Wrapper)를 사용하지 않으면, CybORG의 행동(Action)은 에이전트가 직접 만들어서
> 환경에 전달해야 합니다.

The action space is updated every step and can returned from the environment using the `get_action_space` function. 
Because this dictionary is quite large, we will only print the keys below.

> 행동 공간(Action Space)은 매 스텝(step)마다 갱신되며, `get_action_space` 함수를 통해
> 환경에서 받아올 수 있습니다. 이 딕셔너리는 상당히 크기 때문에, 아래에서는 키(key)만
> 출력해 보겠습니다.

```python title="explore_action_space.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Agents import SleepAgent

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

example_agent_name = 'red_agent_0'
example_action_space = cyborg.get_action_space(example_agent_name)

pprint(example_action_space.keys())

```

???+ quote "Code Output"
    ```shell
    dict_keys(
        ['action', 'allowed_subnets', 'subnet', 'ip_address', 
        'session', 'username', 'password', 'process', 'port', 
        'target_session', 'agent', 'hostname'])
    ```

The CybORG action space is divided into "actions" and "parameters". Actions represent the use of specific cyber tools (for example, a network scanning tool like nmap), while parameters represent the inputs the tool requires to function (to scan the interfaces of a host with nmap, you need to provide the ip address of the host).

> CybORG의 행동 공간은 "actions"(행동)와 "parameters"(파라미터)로 나뉩니다. 행동은
> 특정 사이버 도구의 사용을 나타내고(예: nmap 같은 네트워크 스캔 도구), 파라미터는 그
> 도구가 동작하는 데 필요한 입력값을 나타냅니다(nmap으로 어떤 호스트(Host)의
> 인터페이스(Interface)를 스캔하려면 해당 호스트의 IP 주소를 제공해야 합니다).

The "actions" are located under the `action` key in the `action_space` dictionary.

> "actions"(행동)는 `action_space` 딕셔너리의 `action` 키 아래에 들어 있습니다.

```python title="explore_action_space.py" linenums="22"

pprint(example_action_space['action'])

```
???+ quote "Code Output"
    ```shell
    {<class 'CybORG.Simulator.Actions.Action.Sleep'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverRemoteSystems.DiscoverRemoteSystems'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices.StealthServiceDiscovery'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices.AggressiveServiceDiscovery'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.PrivilegeEscalate.PrivilegeEscalate'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.Impact.Impact'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DegradeServices.DegradeServices'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverDeception.DiscoverDeception'>: True,
    <class 'CybORG.Simulator.Actions.ConcreteActions.Withdraw.Withdraw'>: True,
    <class 'CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions.ExploitRemoteService_cc4'>: True}

    ```

We can see that our actions are each custom classes that form the keys of the above dictionary. The values specify whether this action is currently valid. 

> 각 행동(Action)이 위 딕셔너리의 키를 이루는 별도의 커스텀 클래스라는 것을 알 수
> 있습니다. 값(value)은 해당 행동이 현재 유효한지 여부를 나타냅니다.

The remaining keys in the scenario dictionary represent different classes of parameters. For example, if we examine the `ip_address` key we will get a dictionary whose keys are the various ip addresses on the network. The values are again booleans, which represents whether Red knows about this ip address or not.

> 시나리오(Scenario) 딕셔너리의 나머지 키들은 서로 다른 종류의 파라미터를 나타냅니다.
> 예를 들어 `ip_address` 키를 살펴보면, 네트워크상의 여러 IP 주소를 키로 갖는 딕셔너리를
> 얻게 됩니다. 이때 값은 다시 불리언(boolean)으로, Red 에이전트(공격 측)가 이 IP 주소를
> 알고 있는지 여부를 나타냅니다.

```python title="explore_action_space.py" linenums="24"

pprint(example_action_space['ip_address'])

```
???+ quote "Code Output"
    ```shell
    {IPv4Address('10.0.20.9'): False,
    IPv4Address('10.0.20.30'): False,
    IPv4Address('10.0.20.38'): False,
    ...
    IPv4Address('10.0.96.73'): True,
    ...}
    ```
