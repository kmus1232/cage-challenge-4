---
hide:
  - toc
---

# Welcome to the CC4 Tutorials (CC4 튜토리얼에 오신 것을 환영합니다)

This series of 5 tutorials has been created to help you get to grips with the CybORG environment faster. So you can focus on what you're here for, developing blue agents!

> 이 5개의 튜토리얼 시리즈는 여러분이 **CybORG**(Cyber Operations Research Gym) 환경에 더 빠르게 익숙해지도록 돕기 위해 만들어졌습니다. 그래서 여러분이 이곳을 찾은 진짜 목적, 즉 **Blue 에이전트**(방어 측 에이전트) 개발에 집중할 수 있게 합니다!


<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Tutorial 1 - Getting Started__

    ---

    This is the tutorial for if you are new to CC4 and want to get up and running fast.

    > __튜토리얼 1 - 시작하기 (Getting Started)__
    >
    > CC4를 처음 접하며 빠르게 환경을 띄우고 실행해 보고 싶은 분을 위한 튜토리얼입니다.

    [:octicons-arrow-right-24: Installation Instructions](tutorials/01_Getting_Started/1_Introduction.md)

    [:octicons-arrow-right-24: Getting Started with CybORG](tutorials/01_Getting_Started/2_Getting_Started.md)

    [:octicons-arrow-right-24: Training RLlib Agents](tutorials/01_Getting_Started/3_Training_Agents.md)

-   :material-binoculars:{ .lg .middle } __Tutorial 2 - Looking Around__

    ---

    Ready to start interacting with the environment? Do you want to directly communicate with the environment? Or maybe you want to write your own custom wrappers?

    If so, this is the tutorial for you.

    > __튜토리얼 2 - 둘러보기 (Looking Around)__
    >
    > 이제 환경과 상호작용을 시작할 준비가 되셨나요? 환경과 직접 소통하고 싶으신가요? 아니면 자신만의 커스텀 래퍼(Wrapper)를 작성하고 싶으신가요?
    >
    > 그렇다면 이 튜토리얼이 바로 여러분을 위한 것입니다.

    [:octicons-arrow-right-24: Observations](tutorials/02_Looking_Around/1_Observations.md)

    [:octicons-arrow-right-24: Agents](tutorials/02_Looking_Around/2_Agents.md)

    [:octicons-arrow-right-24: Wrappers](tutorials/02_Looking_Around/3_Wrappers.md)

    [:octicons-arrow-right-24: Visualisation](tutorials/02_Looking_Around/4_Visualisation.md)

    [:octicons-arrow-right-24: Debugging Tools](tutorials/02_Looking_Around/5_Debugging_Tools.md)

-   :material-thought-bubble-outline:{ .lg .middle } __Tutorial 3 - Understanding Actions__

    ---

    Now that you have a general understanding of the environment; of what comes in and goes out. It is time to get a firm foundation in how actions are taken in CybORG.

    > __튜토리얼 3 - 행동 이해하기 (Understanding Actions)__
    >
    > 이제 환경에 대해, 그리고 무엇이 입력되고 무엇이 출력되는지에 대해 전반적으로 이해하셨을 것입니다. 이번에는 CybORG에서 행동(Action)이 어떻게 수행되는지 탄탄한 기초를 다질 차례입니다.

    [:octicons-arrow-right-24: The Action Space](tutorials/03_Actions/A_Understanding_Actions/1_Action_Space.md)

    [:octicons-arrow-right-24: Taking an Action](tutorials/03_Actions/A_Understanding_Actions/2_Taking_an_Action.md)

    [:octicons-arrow-right-24: Sleep Action](tutorials/03_Actions/A_Understanding_Actions/3_Sleep.md)

    [:octicons-arrow-right-24: Invalid Actions](tutorials/03_Actions/A_Understanding_Actions/4_Invalid_Actions.md)

-   :material-walk:{ .lg .middle } __Tutorial 4 - Blue Actions Walkthrough__

    ---

    In CC4, blue agents are limited to a several possible actions. This tutorial will walk you through all of these, allowing you to better interpret your returned observations.

    > __튜토리얼 4 - Blue 행동 둘러보기 (Blue Actions Walkthrough)__
    >
    > CC4에서 **Blue 에이전트**(방어 측 에이전트)는 몇 가지 가능한 행동(Action)으로 제한됩니다. 이 튜토리얼은 그 행동들을 하나씩 안내하여, 여러분이 반환된 관찰값(Observation)을 더 잘 해석할 수 있도록 돕습니다.

    [:octicons-arrow-right-24: Monitor](tutorials/03_Actions/B_Blue_Actions/1_Monitor.md)

    [:octicons-arrow-right-24: Analyse](tutorials/03_Actions/B_Blue_Actions/2_Analyse.md)

    [:octicons-arrow-right-24: Decoy](tutorials/03_Actions/B_Blue_Actions/3_Decoy.md)

    [:octicons-arrow-right-24: Remove](tutorials/03_Actions/B_Blue_Actions/4_Remove.md)

    [:octicons-arrow-right-24: Restore](tutorials/03_Actions/B_Blue_Actions/5_Restore.md)

    [:octicons-arrow-right-24: Control Traffic](tutorials/03_Actions/B_Blue_Actions/6_Control_Traffic.md)

-   :material-incognito:{ .lg .middle } __Tutorial 5 - Red Action Walkthrough__

    ---

    Want a sneak peak at what the adversary is capable of? This tutorial will walk you through all the actions that red agents can take in CC4.

    > __튜토리얼 5 - Red 행동 둘러보기 (Red Action Walkthrough)__
    >
    > 적(공격자)이 무엇을 할 수 있는지 미리 살짝 엿보고 싶으신가요? 이 튜토리얼은 CC4에서 **Red 에이전트**(공격 측 에이전트)가 취할 수 있는 모든 행동(Action)을 하나씩 안내합니다.

    [:octicons-arrow-right-24: Discover Remote Systems](tutorials/03_Actions/C_Red_Actions/1_Discover_Remote_Systems.md)

    [:octicons-arrow-right-24: Service Discovery](tutorials/03_Actions/C_Red_Actions/2_Service_Discovery.md)

    [:octicons-arrow-right-24: Discover Deception](tutorials/03_Actions/C_Red_Actions/3_Discover_Deception.md)

    [:octicons-arrow-right-24: Exploit Remote Service](tutorials/03_Actions/C_Red_Actions/4_Exploit_Remote_Service.md)

    [:octicons-arrow-right-24: Privilege Escalate](tutorials/03_Actions/C_Red_Actions/5_Privilege_Escalate.md)

    [:octicons-arrow-right-24: Degrade Services](tutorials/03_Actions/C_Red_Actions/6_Degrade_Services.md)

    [:octicons-arrow-right-24: Impact](tutorials/03_Actions/C_Red_Actions/7_Impact.md)

    [:octicons-arrow-right-24: Withdraw](tutorials/03_Actions/C_Red_Actions/8_Withdraw.md)

</div>
