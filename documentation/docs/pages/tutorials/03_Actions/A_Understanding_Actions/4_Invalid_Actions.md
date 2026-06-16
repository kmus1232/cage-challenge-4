
# Invalid Actions (유효하지 않은 행동)

If you create an action that doesn't make any sense within the current scenario, CybORG will accept it, but automatically convert it to an Invalid Action. These actions automatically give a reward of -0.1.

> 현재 시나리오에서 말이 되지 않는 행동(Action)을 만들면, CybORG는 그 행동을
> 일단 받아들이되 자동으로 **Invalid Action**(유효하지 않은 행동)으로 변환합니다.
> 이런 행동에는 자동으로 **-0.1의 보상**이 부여됩니다.

```python title="perform_an_invalid_action.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.AbstractActions.Analyse import Analyse

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

example_agent_name = 'blue_agent_0'
example_action_space = cyborg.get_action_space(example_agent_name)

unknown_hostnames = [hn for hn, known in example_action_space['hostname'].items() if not known]
unknown_hostname = unknown_hostnames[0]

example_action = Analyse(0, example_agent_name, unknown_hostname)

results = cyborg.step(agent=example_agent_name, action=example_action)
pprint(results.observation)
```
???+ quote "Code Output"
    ```
    {'action': InvalidAction, 'success': <TernaryEnum.FALSE: 3>}
    ```

> 위 코드 출력(Code Output)은 유효하지 않은 호스트명으로 `Analyse`(분석) 행동을
> 시도한 결과입니다. 관찰값(Observation)에서 `action`이 `InvalidAction`으로
> 바뀌었고, `success` 값이 `FALSE`로 표시되어 행동이 실패했음을 보여줍니다.
