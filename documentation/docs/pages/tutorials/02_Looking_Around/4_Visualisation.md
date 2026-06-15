---
hide:
  - toc
---

# Visualisation (시각화)
CC4 does not have a supported rendered, however it does have a visualisation module. This allows the user to produce an interactive diagram of what is happening to nodes on the network, regarding red shell sessions.

> CC4에는 정식으로 지원되는 렌더러(rendered)가 없지만, 대신 **시각화(visualisation) 모듈**이 있습니다. 이 모듈을 사용하면 네트워크의 노드들에서 Red 셸 세션(shell session, Red 에이전트가 장악한 원격 셸 접속)과 관련해 무슨 일이 일어나고 있는지를 대화형(interactive) 다이어그램으로 만들 수 있습니다.


First the environment needs to be set up:

> 먼저 환경을 설정해야 합니다.

```python title="visualise_cc4.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, DiscoveryFSRed
from CybORG.render.visualisation.VisualiseRedExpansion import VisualiseRedExpansion

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=DiscoveryFSRed,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=7629)
```

You can then run the visualisation internally, where the steps are handled for you, or record the visualisations for each step and display it at the end.

> 그다음에는 두 가지 방법으로 시각화를 실행할 수 있습니다. 스텝(step) 진행을 모듈이 대신 처리해 주는 **내부 실행(run internally)** 방식을 쓰거나, 각 스텝의 시각화를 직접 기록해 두었다가 마지막에 한꺼번에 보여주는 방식을 쓸 수 있습니다.

=== "Run internally"
    ```python title="visualise_cc4.py" linenums="13"
    visualise = VisualiseRedExpansion(cyborg, steps)
    visualise.run()
    ```

=== "Visualise step-by-step"
    ```python title="visualise_cc4.py" linenums="13"

    cyborg.reset()
    visualise = VisualiseRedExpansion(cyborg, steps)

    for i in range(steps):
        # Whatever you want to do before each step
        cyborg.step()
        # Whatever you want to do after each step

        # Make a record of the environment state for the visualisation
        visualise.visualise_step()

    # Whatever you want to do once the episode is finished ...

    # Visualise the episode
    visualise.show_graph()
    ```

> 위의 탭은 두 가지 실행 방식을 보여줍니다.
>
> - **"Run internally"(내부 실행)**: `visualise.run()` 한 줄로 스텝 진행과 시각화를 모듈이 알아서 처리합니다.
> - **"Visualise step-by-step"(스텝별 시각화)**: 직접 반복문으로 `cyborg.step()`을 호출하며 각 스텝마다 `visualise.visualise_step()`으로 환경 상태를 기록하고, 에피소드(episode)가 끝난 뒤 `visualise.show_graph()`로 그래프를 표시합니다. 각 스텝 전후에 원하는 작업을 끼워 넣을 수 있다는 점이 장점입니다.

## Visualisation Output (시각화 출력 결과)
  The visualisation consists of a network graph with a key, and a step scroll bar along the bottom to change the step displayed.

> 시각화 화면은 범례(key)가 달린 네트워크 그래프와, 아래쪽에 표시할 스텝을 바꿀 수 있는 스텝 스크롤 바(step scroll bar)로 구성됩니다.

  There are 4 control buttons:

> 4개의 제어 버튼이 있습니다.

  - '<' is step back
  - '>' is step forwards
  - 'P' is step through episode (play)
  - '||' is pause the play

> - '<' : 한 스텝 뒤로 이동
> - '>' : 한 스텝 앞으로 이동
> - 'P' : 에피소드를 스텝 단위로 자동 진행(재생, play)
> - '||' : 자동 재생 일시정지(pause)

=== "Step 0"
    Looking at the environment, there are 8 subnets divided between 4 'zones'. 
    There are also 5 blue agents spread between 3 of the zones, and no blue agent in the contractor network (CN).
    
    Initially there is only one red agent located in the contractor network, which has compromised a single user-level host.
    The rest of the network is compromise free ... but not for long!

    > 이 환경을 살펴보면, 8개의 서브넷(subnet)이 4개의 '존(zone)'으로 나뉘어 있습니다.
    > 또한 5개의 Blue 에이전트(방어 측)가 그중 3개 존에 흩어져 배치되어 있고, 협력업체 네트워크(contractor network, CN)에는 Blue 에이전트가 없습니다.
    >
    > 처음에는 협력업체 네트워크에 단 하나의 Red 에이전트(공격 측)만 있으며, 이 에이전트는 사용자 권한 수준(user-level)의 호스트 한 대를 이미 장악(compromise)한 상태입니다.
    > 나머지 네트워크는 아직 침해되지 않았습니다... 하지만 그것도 오래가지 않습니다!

    <figure markdown>
      <img src="/assets/CC4_Visualisation_0.png" alt="CC4 Visualisation at step 0" width="1000">
    </figure>


=== "Step 20"
    <figure markdown>
      <img src="/assets/CC4_Visualisation_20.png" alt="CC4 Visualisation at step 0" width="1000">
      <figcaption>Figure 1 - CC4 Visualisation at step 20 (그림 1 - 스텝 20에서의 CC4 시각화)</figcaption>
    </figure>

=== "Step 100"
    <figure markdown>
      <img src="/assets/CC4_Visualisation_100.png" alt="CC4 Visualisation at step 0" width="1000">
      <figcaption>Figure 1 - CC4 Visualisation at step 100 (그림 1 - 스텝 100에서의 CC4 시각화)</figcaption>
    </figure>
