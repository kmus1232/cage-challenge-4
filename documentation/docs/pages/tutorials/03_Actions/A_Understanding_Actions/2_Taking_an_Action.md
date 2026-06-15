
# Taking an Action (행동 실행하기)

To construct an action, we choose (or import) an action class, then instantiate it by passing in the necessary parameters.

> 행동(Action)을 만들려면, 먼저 행동 클래스를 선택(또는 import)한 뒤 필요한 파라미터를 넘겨 인스턴스를 생성합니다.

A fully commented example is shown below:

> 주석을 모두 달아둔 예제는 아래와 같습니다.

```python title="example_sleep_action.py" linenums="1"
# import pprint package to allow for better readability of the observation space
from pprint import pprint

# import CybORG as a package, and all the classes needed for this script
from CybORG import CybORG
from CybORG.Agents import SleepAgent
from CybORG.Simulator.Actions import Sleep

steps = 200     

# Initialising the scenario creator for CC4
sg = EnterpriseScenarioGenerator(
    blue_agent_class=SleepAgent,    # agent class used for the blue agents
    green_agent_class=SleepAgent,   # agent class used for the green agents
    red_agent_class=SleepAgent,     # agent class used for the red agents
    steps=steps                     # the number of steps to take for this episode
)

# Initialising the CybORG environment with the CC4 scenario generator and a fixed seed 
# (seed is optional and will be generated randomly if not supplied)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()


example_agent_name = 'blue_agent_0' # name of the agent that is going to take the action

example_action = Sleep() # action that the agent is going to take

# the environment takes a step with the given agent and action, and outputs the results from that step
results = cyborg.step(agent=example_agent_name, action=example_action)

# print the observations gained for that agent from that step
pprint(results.observation)
```

The printed observation for the example agent is shown here.

> 예제 에이전트가 출력한 관찰값(Observation)은 아래와 같습니다.

???+ quote "Code Output"
    ```
    {
        'action': Sleep, 
        'success': <TernaryEnum.UNKNOWN: 2> 
    }
    ```

`'success'` can come in four forms:

1. TRUE - the action was successful
2. UNKNOWN - it is not possible to know the success of the action / the action does not support 'success' types
3. FALSE - the action was unsuccessful
4. IN_PROGRESS - the action takes multiple steps and has not been completed yet.

> `'success'` 값은 네 가지 형태로 나타날 수 있습니다.
>
> 1. TRUE - 행동이 성공했습니다.
> 2. UNKNOWN - 행동의 성공 여부를 알 수 없거나, 해당 행동이 'success' 형태를 지원하지 않습니다.
> 3. FALSE - 행동이 실패했습니다.
> 4. IN_PROGRESS - 여러 스텝(step)에 걸쳐 수행되는 행동으로, 아직 완료되지 않았습니다.


???+ tip 
    The CybORG function `parallel_step()` allows you to define the actions that multiple agents should take in one step, and get returned all the observations for all the agents.

    CybORG 함수 `parallel_step()`을 사용하면 한 스텝(step) 안에서 여러 에이전트가 취할 행동을 한꺼번에 정의하고, 모든 에이전트의 관찰값(Observation)을 한 번에 돌려받을 수 있습니다.