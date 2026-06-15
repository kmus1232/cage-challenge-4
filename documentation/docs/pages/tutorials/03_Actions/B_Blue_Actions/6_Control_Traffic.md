# Control Traffic Between Zones (영역 간 트래픽 제어)

In CC4, blue agents can make block and allow firewall rules to cut off parts of the network.

> CC4에서 Blue 에이전트(방어 측)는 방화벽 규칙으로 트래픽을 차단(block)하거나 허용(allow)하여 네트워크의 일부를 끊어낼 수 있습니다.

This is a risky move for blue, as green will penalise blue if it cannot perform remote actions (GreenAccessService). But it may be worth it to lower the risk of red infecting the network.

> 이는 Blue 입장에서 위험을 감수하는 선택입니다. Green 에이전트(정상 사용자)가 원격 행동(`GreenAccessService`)을 수행하지 못하면 Blue에게 페널티(penalise)를 주기 때문입니다. 다만 Red 에이전트(공격 측)가 네트워크를 감염시킬 위험을 낮출 수 있다면 그만한 가치가 있을 수 있습니다.

???+ info
    Red can still infect the cut off network via clicking on phishing emails. However this is a rare sub-action.

> ???+ info
>     Red는 트래픽이 끊긴 네트워크라도 피싱 이메일(phishing email) 클릭을 통해 여전히 감염시킬 수 있습니다. 다만 이는 드물게 발생하는 하위 행동(sub-action)입니다.

## BlockTrafficZone

Blocking traffic between two subnets is as simple as picking the two subnets and running the `BlockTrafficZone` action. 
Here is an example:

> 두 서브넷(subnet) 사이의 트래픽을 차단하는 것은 두 서브넷을 고른 뒤 `BlockTrafficZone` 행동(Action)을 실행하기만 하면 될 만큼 간단합니다. 예시는 다음과 같습니다.

```python title="control_traffic_example.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone, AllowTrafficZone

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
action_space = cyborg.get_action_space(blue_agent_name)

action = BlockTrafficZone(session=0, agent=blue_agent_name, from_subnet='restricted_zone_a_subnet', to_subnet='restricted_zone_b_subnet')

results = cyborg.step(agent=blue_agent_name, action=action)
obs = results.observation
pprint(obs)
```

???+ quote "Code Output"
    ```
    {'action': BlockTrafficZone, 'success': <TernaryEnum.TRUE: 1>}
    ```

> ???+ quote "Code Output (코드 실행 결과)"
>     ```
>     {'action': BlockTrafficZone, 'success': <TernaryEnum.TRUE: 1>}
>     ```

From the output, we can see that the action has been executed successfully.

> 출력 결과를 보면 행동이 성공적으로 실행된 것을 확인할 수 있습니다.

## AllowTrafficZone

The `AllowTrafficZone` action will then reverse the firewall rule.

> `AllowTrafficZone` 행동은 앞서 적용한 방화벽 규칙을 다시 원래대로 되돌립니다.

```python title="control_traffic_example.py" linenums="25"
action = AllowTrafficZone(session=0, agent=blue_agent_name, from_subnet='restricted_zone_a_subnet', to_subnet='restricted_zone_b_subnet')

results = cyborg.step(agent=blue_agent_name, action=action)
obs = results.observation
pprint(obs)
```

???+ quote "Code Output"
    ```
    {'action': AllowTrafficZone, 'success': <TernaryEnum.TRUE: 1>}
    ```

> ???+ quote "Code Output (코드 실행 결과)"
>     ```
>     {'action': AllowTrafficZone, 'success': <TernaryEnum.TRUE: 1>}
>     ```

From the output, we can see that the action has been executed successfully.

> 출력 결과를 보면 행동이 성공적으로 실행된 것을 확인할 수 있습니다.
