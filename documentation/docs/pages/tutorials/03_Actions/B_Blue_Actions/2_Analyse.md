
# Analyse (분석)

`Analyse` checks for the occurance of malware, in the form of a file, on a single specified host.

> `Analyse`(분석)는 지정한 단일 호스트에서 파일 형태의 악성코드(malware)가 존재하는지 점검합니다.


## Executing Analyse (Analyse 실행하기)

The blue action `Analyse` should be executed when it is suspected that red agents have been active on the network. 

> Blue 에이전트(방어 측)의 행동(Action) `Analyse`는 네트워크에서 Red 에이전트(공격 측)가 활동한 것으로 의심될 때 실행해야 합니다.

Refer to the previous action `Monitor` for more information about possible red behaviour alerts.

> Red 에이전트의 활동을 알리는 경보에 대해서는 앞선 행동인 `Monitor`(모니터링) 문서를 참고하세요.

Below is an example of how to run the `Analyse` action:

> 다음은 `Analyse` 행동을 실행하는 예시입니다.

```python title="example_analyse.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Analyse

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
blue_action_space = cyborg.get_action_space(blue_agent_name)

action = Analyse(session=0, agent=blue_agent_name, hostname='restricted_zone_a_subnet_server_host_0')

results = cyborg.step(agent=blue_agent_name, action=action)
print("Step 1: ", results.observation)
results = cyborg.step(agent=blue_agent_name)
print("Step 2: ", results.observation)          
```

???+ quote "Code Output"
    ```
    Step 1:  {'success': <TernaryEnum.IN_PROGRESS: 4>}
    Step 2:  {'success': <TernaryEnum.TRUE: 1>, 'action': Analyse restricted_zone_a_subnet_server_host_0}
    ```

As you can see it takes two steps for the action to complete. This is due to action duration being added to CC4 as a way of disadvantaging high utility actions - similarly to how more valuable operations are normally harder/take more time in the real world.

> 보다시피 이 행동이 완료되기까지 두 스텝(step)이 걸립니다. 이는 CC4(CAGE Challenge 4)에 행동 소요 시간(action duration)이 추가되어, 효용이 높은 행동에 불이익을 주기 때문입니다. 현실에서도 더 가치 있는 작업일수록 보통 더 어렵거나 시간이 오래 걸리는 것과 비슷한 원리입니다.

However after a step, the observation space shows that the action is successful - yet there is no additional observation to return.

> 다만 한 스텝이 지나면 관찰값(Observation) 공간에 행동이 성공했다고 표시됩니다. 그러나 이때 추가로 반환되는 관찰값은 없습니다.

## Successful action after Red Agent performed Exploit Action (Red 에이전트가 Exploit 행동을 수행한 뒤 성공한 경우)

To catch a red agent adding malware to a host in the subnet, you can perform the analyse action repeatedly until you see activity.

> Red 에이전트가 서브넷(Subnet) 안의 호스트에 악성코드를 심는 것을 포착하려면, 활동이 보일 때까지 analyse 행동을 반복해서 수행하면 됩니다.

Here is a basic script that iterably performs the analyse action for a certain number of steps.

> 다음은 일정한 스텝 수 동안 analyse 행동을 반복 수행하는 기본 스크립트입니다.

```python
step = 2
while step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

pprint(new_obs)  
```

A possible output for the results of a red Exploit action is shown here:

> Red 에이전트의 Exploit(익스플로잇, 원격 서비스 공격) 행동 결과로 나타날 수 있는 출력은 다음과 같습니다.

???+ quote "Code Output Section"
    ```
    {'action': Analyse_cc4 restricted_zone_a_subnet_server_host_0,
    'restricted_zone_a_subnet_server_host_0': {'Files': [{'Density': 0.9,
                                                        'File Name': 'cmd.sh',
                                                        'Known File': <FileType.UNKNOWN: 1>,
                                                        'Known Path': <Path.TEMP: 5>,
                                                        'Path': '/tmp/'}]},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The occurence of the malware `cmd.sh` indicates that an exploit was run to get a user shell on the host.

> 악성코드 `cmd.sh`가 나타났다는 것은 호스트에서 사용자 셸(user shell)을 획득하기 위한 익스플로잇이 실행되었음을 의미합니다.

This is valuable intel that means that we may want to remove that user shell from the host before it gains root privileges, using the `Remove` action.

> 이는 중요한 정보로, 해당 사용자 셸이 루트 권한(root privileges)을 얻기 전에 `Remove`(제거) 행동을 사용해 호스트에서 그 셸을 제거하는 편이 좋다는 뜻입니다.

## Successful action after Red Agent performed PrivilegeEscalate Action (Red 에이전트가 PrivilegeEscalate 행동을 수행한 뒤 성공한 경우)

Let's also consider the successful action after the Red Agent performs `PrivilegeEscalate`.

> Red 에이전트가 `PrivilegeEscalate`(권한 상승)를 수행한 뒤 성공한 경우도 살펴보겠습니다.

???+ quote "Code Output"
    ```
    {'action': Analyse_cc4 restricted_zone_a_subnet_server_host_0,
    'restricted_zone_a_subnet_server_host_0': {'Files': [{'Density': 0.9,
                                                        'File Name': 'cmd.sh',
                                                        'Known File': <FileType.UNKNOWN: 1>,
                                                        'Known Path': <Path.TEMP: 5>,
                                                        'Path': '/tmp/'},
                                                        {'Density': 0.9,
                                                        'File Name': 'escalate.sh',
                                                        'Known File': <FileType.UNKNOWN: 1>,
                                                        'Known Path': <Path.TEMP: 5>,
                                                        'Path': '/tmp/'}]},
    'success': <TernaryEnum.TRUE: 1>} 
    ```

You can tell from the presence of the additional file `escalate.sh`, that the red has managed to get a root shell on the host. 
This means that the red agent has total control of that host, and the only way to get rid of red is to `Restore` the host.

> 추가된 파일 `escalate.sh`가 존재하는 것으로 보아, Red 에이전트가 호스트에서 루트 셸(root shell)을 획득하는 데 성공했음을 알 수 있습니다.
> 이는 Red 에이전트가 해당 호스트를 완전히 장악했다는 뜻이며, Red를 제거할 유일한 방법은 호스트를 `Restore`(복원)하는 것입니다.
