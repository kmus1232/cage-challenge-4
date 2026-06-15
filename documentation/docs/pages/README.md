---
hide:
  - navigation
---

# TTCP CAGE Challenge 4: Challenge Details
## Introduction (소개)

The TTCP CAGE Challenges are a series of public challenges instigated to foster the development of autonomous cyber defensive agents. 
The CAGE Challenges present different cybersecurity scenarios inspired by real-world situations in a simulated environment. 

> TTCP CAGE 챌린지(CAGE Challenge)는 **자율 사이버 방어**(autonomous cyber defence, 스스로 판단해 사이버 공격을 막는) 에이전트의 개발을 촉진하기 위해 시작된 공개 챌린지 시리즈입니다.
> CAGE 챌린지는 실제 상황에서 영감을 얻은 다양한 사이버보안 시나리오를 시뮬레이션 환경 안에서 제시합니다.

The first CAGE Challenge was released to the public in August 2021, the second in April 2022 and the third in September 2022. 
The challenges use the Cyber Operations Research Gym (CybORG) to provide a high-fidelity cyber simulation for the training and evaluation of AI algorithms such as Deep Reinforcement Learning. 
The CAGE activity aims to run a series of challenges of increasing complexity and realism.

> 첫 번째 CAGE 챌린지는 2021년 8월, 두 번째는 2022년 4월, 세 번째는 2022년 9월에 일반에 공개되었습니다.
> 이 챌린지들은 **CybORG**(Cyber Operations Research Gym)를 사용해 정밀도 높은 사이버 시뮬레이션을 제공하며, 이를 통해 심층 강화학습(Deep Reinforcement Learning) 같은 AI 알고리즘을 학습·평가합니다.
> CAGE 활동은 복잡도와 현실성을 점점 높여 가는 일련의 챌린지를 운영하는 것을 목표로 합니다.

This CAGE Challenge 4 (CC4) returns to a defence industry enterprise environment, and introduces a Multi-Agent Reinforcement Learning (MARL) scenario.

> 이번 CAGE Challenge 4(CC4)는 방위산업 엔터프라이즈 환경으로 돌아오며, **다중 에이전트 강화학습**(Multi-Agent Reinforcement Learning, MARL) 시나리오를 새로 도입합니다.

## Scenario Narrative (시나리오 배경)

Tensions continue to escalate between the nations of Florin and Guilder. As part of regular border patrols, Florin utilises unmanned drones for reconnaissance and communication purposes. Guilder wishes to disrupt drone operations by performing a cyber-attack against the base station where the activity of the patrols is coordinated.

> Florin과 Guilder 두 국가 사이의 긴장이 계속 고조되고 있습니다. Florin은 정기 국경 순찰의 일환으로 정찰과 통신 목적의 무인 드론을 운용합니다. Guilder는 순찰 활동을 총괄하는 기지국(base station)을 사이버 공격해 드론 운용을 방해하려고 합니다.

You have successfully developed several cyber defence agents for Florin (CAGE Challenges 1-3) and have now been tasked with developing an agent to protect the base station. The network here consists of a range of operational and back-office enterprise networks which support various military operations. Additionally, the drones themselves are controlled via a contractor subnet which connects to the base via the internet. For security purposes the network is highly segmented into security zones and thus a multi-agent solution is required, with each agent protecting its own security zone. Additionally, communication between agents is highly restricted and bandwidth is limited.

> 여러분은 Florin을 위해 여러 사이버 방어 에이전트를 성공적으로 개발했고(CAGE Challenges 1-3), 이제 기지국을 보호할 에이전트를 개발하는 임무를 맡았습니다. 이 네트워크는 다양한 군사 작전을 지원하는 운영 네트워크와 후방 업무용(back-office) 엔터프라이즈 네트워크로 구성됩니다. 또한 드론 자체는 인터넷을 통해 기지에 연결되는 협력업체 서브넷(contractor subnet)을 통해 제어됩니다. 보안을 위해 네트워크는 보안 영역(security zone)으로 촘촘히 분할되어 있으며, 따라서 각 에이전트가 자기 보안 영역을 보호하는 다중 에이전트 방식의 해법이 필요합니다. 게다가 에이전트 간 통신은 크게 제한되며 대역폭도 한정되어 있습니다.

The agent’s main task is to maintain operational capabilities while preventing malicious activity on the network. This is complicated by the fact that operational priorities change over time, depending on different phases of the mission. However, its general priorities within a given phase are as follows.

> 에이전트의 핵심 임무는 네트워크상의 악성 활동을 막으면서 작전 수행 능력을 유지하는 것입니다. 이는 작전 우선순위가 임무 단계(phase)에 따라 시간이 지나며 바뀐다는 점 때문에 복잡해집니다. 다만 특정 단계 안에서의 일반적인 우선순위는 다음과 같습니다.

1. Maintain service of critical network infrastructure to ensure sensitive operational capabilities are not impacted.
2. Where possible, maintain enterprise servers to ensure less sensitive, day-to-day operations are not impacted.
3. Maintain access to public services provided by Florin.

> 1. 핵심 네트워크 인프라의 서비스를 유지하여 민감한 작전 수행 능력이 영향을 받지 않도록 합니다.
> 2. 가능하다면 엔터프라이즈 서버를 유지하여, 덜 민감한 일상 업무가 영향을 받지 않도록 합니다.
> 3. Florin이 제공하는 공개 서비스(public service)에 대한 접근을 유지합니다.

## Challenge Details (챌린지 상세)

The network for this challenge is split into four smaller networks as can be seen in Figure 1. Two of these are deployed networks, one is the Headquarters (HQ) network and another is the Contractor network. These networks connect together via the internet.

> 이 챌린지의 네트워크는 그림 1(Figure 1)에서 보듯 네 개의 작은 네트워크로 나뉩니다. 그중 둘은 배치 네트워크(deployed network), 하나는 본부(HQ) 네트워크, 나머지 하나는 협력업체 네트워크(Contractor network)입니다. 이 네트워크들은 인터넷을 통해 서로 연결됩니다.

Each deployed network consists of two security zones: a restricted zone and an operational zone. The Headquarters network consists of three security zones: a Public Access Zone, an Admin Zone and an Office Network. The Contractor network only contains a single UAV control zone.

> 각 배치 네트워크는 두 개의 보안 영역(security zone), 즉 제한 영역(restricted zone)과 운영 영역(operational zone)으로 구성됩니다. 본부 네트워크는 세 개의 보안 영역, 즉 공개 접근 영역(Public Access Zone), 관리자 영역(Admin Zone), 사무 네트워크(Office Network)로 구성됩니다. 협력업체 네트워크는 단 하나의 UAV(무인기) 제어 영역만 포함합니다.

In order to encourage the development of robust agents, the number of hosts in each security zone and their services will be randomised. Indeed, each zone will have between 1-6 servers and 3-10 user hosts. Each host and server will have a minimum of 1 service with a maximum of 5.

> 견고한(robust) 에이전트의 개발을 유도하기 위해, 각 보안 영역의 호스트 수와 그 서비스는 무작위로 결정됩니다. 구체적으로 각 영역에는 서버 1-6대와 사용자 호스트 3-10대가 배치됩니다. 각 호스트와 서버는 최소 1개에서 최대 5개의 서비스를 갖습니다.

<figure markdown>
  <img src="../assets/CAGE-Network-Diagram.png" alt="CC4 Network Diagram" width="750">
  <figcaption>Figure 1 - Network Laydown (그림 1 - 네트워크 배치도)</figcaption>
</figure>

The network will have 5 network defenders. Each deployed network will have two, one for each security zone. The Headquarters will have a single defensive agent for all zones, while the Contractor network will be undefended.

> 네트워크에는 5명의 네트워크 방어자(network defender)가 있습니다. 각 배치 네트워크에는 보안 영역마다 하나씩, 두 명이 배치됩니다. 본부는 모든 영역을 담당하는 단일 방어 에이전트를 두며, 협력업체 네트워크는 방어되지 않습니다.

Red team begins the operation with access to a random machine in the contractor network and attempts to pivot throughout the network. Every turn there is a small chance that a red agent will spawn if green opens a phishing email and red can also spawn in networks, when a green user accesses a compromised service. There is a maximum of one red agent in each zone, though these agents can maintain a presence on multiple hosts. While Blue team may succeed in removing all traces of red team from a network, red will always maintain a foothold in the Contractor Network. 

> Red 팀(Red 에이전트, 공격 측)은 협력업체 네트워크의 임의의 머신에 접근한 상태로 작전을 시작하며, 네트워크 전반으로 측면 이동(pivot)을 시도합니다. 매 턴마다 Green 에이전트(정상 사용자)가 피싱 이메일을 열면 Red 에이전트가 생성될 약간의 확률이 있고, Green 사용자가 손상된(compromised) 서비스에 접근할 때도 네트워크 안에서 Red 에이전트가 생성될 수 있습니다. 각 영역에는 Red 에이전트가 최대 한 명까지 존재하지만, 이 에이전트는 여러 호스트에 동시에 존재(presence)를 유지할 수 있습니다. Blue 팀(Blue 에이전트, 방어 측)이 네트워크에서 Red 팀의 모든 흔적을 제거하는 데 성공하더라도, Red는 협력업체 네트워크에서는 항상 거점(foothold)을 유지합니다.

The red agents will each use a randomly selected strategy.

> Red 에이전트들은 각각 무작위로 선택된 전략(strategy)을 사용합니다.

<figure markdown>
  <img src="../assets/CAGE-Deployed-Network-A.png" alt="CC4 Deployed Network A Diagram" width="500">
  <figcaption>Figure 2 - Deployed Network A (그림 2 - 배치 네트워크 A)</figcaption>
</figure>

Agent actions now have a specified time duration, which varies depending on the action chosen. Agents must wait until their action is completed before they are prompted to launch another action. Once an agent has chosen it cannot be cancelled.

> 이제 에이전트의 행동(Action)에는 정해진 소요 시간이 있으며, 이는 선택한 행동에 따라 달라집니다. 에이전트는 자신의 행동이 완료될 때까지 기다려야 다음 행동을 실행하라는 요청을 받습니다. 한번 선택한 행동은 취소할 수 없습니다.

During the course of an episode, the mission shall progress linearly through three different phases Phase 1, Phase 2A and Phase 2B. During Phase 1 all missions operating in each zone have the same low priority level. During Phase 2A only missions operating in zones within Deployed Network A have the same high priority level, while all other missions have the same low priority level. During Phase 2B only missions operating in Deployed Network B have the same high priority level, while all other missions have the same low priority level.

> 한 에피소드(Episode)가 진행되는 동안, 임무는 Phase 1, Phase 2A, Phase 2B의 세 단계를 차례대로(선형적으로) 거칩니다. Phase 1에서는 각 영역에서 수행되는 모든 임무가 동일한 낮은 우선순위를 갖습니다. Phase 2A에서는 배치 네트워크 A(Deployed Network A) 내 영역에서 수행되는 임무만 동일한 높은 우선순위를 갖고, 나머지 모든 임무는 동일한 낮은 우선순위를 갖습니다. Phase 2B에서는 배치 네트워크 B(Deployed Network B)에서 수행되는 임무만 동일한 높은 우선순위를 갖고, 나머지 모든 임무는 동일한 낮은 우선순위를 갖습니다.

## Green Agents (Green 에이전트)

Users are represented by green agents, which are present on every host. Green agents randomly do local work or attempt to reach out to external services, either in their local or a remote zone. The service and zone a green agent chooses will be determined randomly, but are restricted to valid connections for the current mission phase as governed by the communication policy tables below. 

> 사용자는 Green 에이전트(정상 사용자)로 표현되며, 모든 호스트에 존재합니다. Green 에이전트는 무작위로 로컬 작업(local work)을 하거나, 자신이 속한 로컬 영역 또는 원격 영역의 외부 서비스에 접속을 시도합니다. Green 에이전트가 선택하는 서비스와 영역은 무작위로 결정되지만, 아래의 통신 정책(communication policy) 표가 규정하는 현재 임무 단계의 유효한 연결로 제한됩니다.

Rewards are tied to these green agent actions. The blue team receives penalties when a green agent is unable to work, either because it cannot make a valid connection to service, or its host is unavailable (for example if it is currently being restored by a blue agent). Green agents in mission-critical zones generate higher penalties when their mission is active. The full list and values of penalties are shown in Table 4.

> 보상(Reward)은 이러한 Green 에이전트의 행동에 연동됩니다. Green 에이전트가 작업을 수행하지 못하면 Blue 팀이 페널티(penalty, 감점)를 받습니다. 작업을 못 하는 이유는 서비스에 유효한 연결을 맺지 못했거나, 호스트를 사용할 수 없는 경우(예: Blue 에이전트가 현재 그 호스트를 복원(Restore) 중인 경우)입니다. 임무상 핵심(mission-critical) 영역의 Green 에이전트는 해당 임무가 활성화되어 있을 때 더 큰 페널티를 발생시킵니다. 페널티의 전체 목록과 값은 Table 4에 나와 있습니다.

Green agents occasionally generate false alerts while going about their work by exhibiting behavior similar to a red agent, such as transferring data between hosts. They also sometimes introduce red agents into the network via succumbing to phishing attacks, installing unapproved software, and general poor security hygiene.

> Green 에이전트는 작업을 수행하다가 호스트 간 데이터 전송처럼 Red 에이전트와 비슷한 행동을 보이면서 때때로 거짓 경보(false alert)를 발생시킵니다. 또한 피싱 공격에 당하거나, 승인되지 않은 소프트웨어를 설치하거나, 전반적인 보안 위생(security hygiene)이 나빠서 때때로 Red 에이전트를 네트워크에 끌어들이기도 합니다.

## Deception (기만 전술)

Both blue and red agents may employ deception to further their goals. Blue agents can stand up decoy services in any host or server. Decoy services resemble normal ones, but cannot replace or be instantiated along with existing services (they can use the Discover Network Services action to determine which services are already running on a given host). When a red agent attempts to compromise a decoy service, blue will be alerted and red’s exploit will automatically fail. Red agents can use the `DiscoverDeception` action to determine if they are interacting with decoy services, and their `Withdraw` action to remove their presence.

> Blue 에이전트와 Red 에이전트 모두 자신의 목표를 위해 기만(deception)을 활용할 수 있습니다. Blue 에이전트는 임의의 호스트나 서버에 디코이 서비스(Decoy, 미끼 서비스)를 세울 수 있습니다. 디코이 서비스는 정상 서비스처럼 보이지만, 기존 서비스를 대체하거나 기존 서비스와 함께 생성될 수는 없습니다(Discover Network Services 행동을 사용해 해당 호스트에서 이미 실행 중인 서비스를 파악할 수 있습니다). Red 에이전트가 디코이 서비스를 손상시키려 시도하면 Blue에게 경보가 가고 Red의 익스플로잇(exploit, 공격)은 자동으로 실패합니다. Red 에이전트는 `DiscoverDeception` 행동으로 자신이 디코이 서비스와 상호작용 중인지 판별할 수 있고, `Withdraw` 행동으로 자신의 존재를 제거할 수 있습니다.

For their part, red agents are more likely to generate extra alerts for blue defenders using the `Aggressive Service Discovery` action on a selected host. This action is faster than the Service Discovery action but has a higher probability of generating an alert, so it may also be used simply to trade off speed over stealth. In addition, red agents with elevated privileges can use the Degrade action to cause green agent actions on the target host to fail much more frequently.

> Red 에이전트 쪽에서는, 선택한 호스트에 `Aggressive Service Discovery`(공격적 서비스 탐색) 행동을 사용하면 Blue 방어자에게 추가 경보를 발생시킬 가능성이 더 큽니다. 이 행동은 Service Discovery 행동보다 빠르지만 경보 발생 확률이 더 높으므로, 은밀성(stealth)을 속도와 맞바꾸는 용도로도 단순히 사용할 수 있습니다. 또한 권한이 상승된(elevated privileges) Red 에이전트는 Degrade(서비스 성능 저하) 행동을 사용해 대상 호스트의 Green 에이전트 행동이 훨씬 더 자주 실패하도록 만들 수 있습니다.

## Network Connectivity and Communication Policy (네트워크 연결성과 통신 정책)

Each mission phase has an associated communication policy governing how zones are intended to connect to one another. When the mission phase changes the intended policy is communicated automatically. Only connections associated with the given mission are changed (for example, when mission 2A is activated, only connections with Restricted Zone A and Operational Zone A are affected). The policy associated with each mission phase is shown in Tables 1-3. The intended policy and actual firewall state is also communicated to blue agents in their observation vector. Blue agents can open and close firewalls between their zone and other networks, for example to prevent infections from red agents, but may incur penalties if their changes prevent green agents from accomplishing their own goals. Some blue agents may communicate with each other regardless of firewall policy via 8-bit messages. 

> 각 임무 단계에는 영역들이 서로 어떻게 연결되어야 하는지를 규정하는 통신 정책(communication policy)이 연계되어 있습니다. 임무 단계가 바뀌면 의도된 정책이 자동으로 통보됩니다. 해당 임무와 관련된 연결만 변경됩니다(예: 임무 2A가 활성화되면 Restricted Zone A와 Operational Zone A에 관련된 연결만 영향을 받습니다). 각 임무 단계에 연계된 정책은 Table 1-3에 나와 있습니다. 의도된 정책과 실제 방화벽 상태는 Blue 에이전트의 관찰값(Observation) 벡터로도 전달됩니다. Blue 에이전트는 자기 영역과 다른 네트워크 사이의 방화벽을 열거나 닫을 수 있습니다(예: Red 에이전트의 감염을 막기 위해). 다만 그 변경이 Green 에이전트의 목표 달성을 방해하면 페널티를 받을 수 있습니다. 일부 Blue 에이전트는 방화벽 정책과 무관하게 8비트 메시지(8-bit message)를 통해 서로 통신할 수 있습니다.

Some defending agents have the capability to communicate 8-bit messages with each other. See Table 1 for the complete (initial) network communication security policy for the mission pre-planning phase.

> 일부 방어 에이전트는 서로 8비트 메시지를 주고받는 능력을 가지고 있습니다. 임무 사전 계획 단계(mission pre-planning phase)의 전체(초기) 네트워크 통신 보안 정책은 Table 1을 참고하세요.

### Phase 1: Mission Pre-planning (General Operations and Maintenance) (Phase 1: 임무 사전 계획 — 일반 운영 및 유지보수)

#### Table 1: Initial Network Communication Security Policy --- Mission-Pre-planning Phase

|        **Zone**        | **HQ Network** | **Contractor Network** | **Restricted Zone A** | **Operational Zone A** | **Restricted Zone B** | **Operational Zone B** | **Internet** |
|:----------------------:|:--------------:|:----------------------:|:---------------------:|:----------------------:|:---------------------:|:----------------------:|:------------:|
|     **HQ Network**     |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Contractor Network** |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Restricted Zone A**  |       1        |           1            |           1           |           1            |           1           |           0            |      1       |
| **Operational Zone A** |       0        |           0            |           1           |           1            |           0           |           0            |      0       |
| **Restricted Zone B**  |       1        |           1            |           1           |           0            |           1           |           1            |      1       |
| **Operational Zone B** |       0        |           0            |           0           |           0            |           1           |           1            |      0       |
|      **Internet**      |       1        |           1            |           1           |           0            |           1           |           0            |      1       |

> **표 해설(Table 1):** 임무 사전 계획 단계(Phase 1)의 초기 네트워크 통신 보안 정책입니다. 행(row)은 출발 영역(Zone), 열(column)은 도착 영역을 뜻합니다. 셀 값 **1**은 두 영역 사이의 통신이 허용됨을, **0**은 차단됨을 의미합니다. 영역 이름: HQ Network(본부), Contractor Network(협력업체), Restricted Zone A/B(제한 영역 A/B), Operational Zone A/B(운영 영역 A/B), Internet(인터넷).

<figure markdown>
  ![CAGE Phase 1 Connectivity Diagram](../assets/CAGE-Phase-1-Connectivity-Diagram.png)
  <figcaption>Figure 3 - Phase 1 Connectivity Diagram (그림 3 - Phase 1 연결성 다이어그램)</figcaption>
</figure>

### Phase 2a: Mission A Active (Phase 2a: 임무 A 활성)

When mission A is active, Operational Zone A disconnects from all other networks. Restricted zone A connects only to HQ.

> 임무 A가 활성화되면 Operational Zone A(운영 영역 A)는 다른 모든 네트워크와의 연결이 끊깁니다. Restricted Zone A(제한 영역 A)는 본부(HQ)에만 연결됩니다.

#### Table 2: Initial Network Communication Security Policy --- Active Mission A Phase

|        **Zone**        | **HQ Network** | **Contractor Network** | **Restricted Zone A** | **Operational Zone A** | **Restricted Zone B** | **Operational Zone B** | **Internet** |
|:----------------------:|:--------------:|:----------------------:|:---------------------:|:----------------------:|:---------------------:|:----------------------:|:------------:|
|     **HQ Network**     |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Contractor Network** |       1        |           1            |           0           |           0            |           1           |           0            |      1       |
| **Restricted Zone A**  |       1        |           0            |           1           |           0            |           0           |           0            |      0       |
| **Operational Zone A** |       0        |           0            |           0           |           1            |           0           |           0            |      0       |
| **Restricted Zone B**  |       1        |           1            |           0           |           0            |           1           |           1            |      1       |
| **Operational Zone B** |       0        |           0            |           0           |           0            |           1           |           1            |      0       |
|      **Internet**      |       1        |           1            |           0           |           0            |           1           |           0            |      1       |

> **표 해설(Table 2):** 임무 A 활성 단계(Phase 2a)의 초기 네트워크 통신 보안 정책입니다. 행은 출발 영역, 열은 도착 영역이며, **1**은 통신 허용, **0**은 차단을 의미합니다. Phase 1과 비교하면 Operational Zone A가 자기 자신을 제외한 모든 영역과 단절되고, Restricted Zone A는 HQ Network와만 연결되는 점이 달라집니다.

<figure markdown>
  ![CAGE Phase 2a Connectivity Diagram](../assets/CAGE-Phase-2a-Connectivity-Diagram.png)
  <figcaption>Figure 4 - Phase 2a Connectivity Diagram (그림 4 - Phase 2a 연결성 다이어그램)</figcaption>
</figure>

### Phase 2b: Mission B Active (Phase 2b: 임무 B 활성)

When mission B is active, Operational Zone B disconnects from all other networks. Restricted zone B connects only to HQ.

> 임무 B가 활성화되면 Operational Zone B(운영 영역 B)는 다른 모든 네트워크와의 연결이 끊깁니다. Restricted Zone B(제한 영역 B)는 본부(HQ)에만 연결됩니다.

#### Table 3: Initial Network Communication Security Policy --- Active Mission B Phase

|        **Zone**        | **HQ Network** | **Contractor Network** | **Restricted Zone A** | **Operational Zone A** | **Restricted Zone B** | **Operational Zone B** | **Internet** |
|:----------------------:|:--------------:|:----------------------:|:---------------------:|:----------------------:|:---------------------:|:----------------------:|:------------:|
|     **HQ Network**     |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Contractor Network** |       1        |           1            |           1           |           0            |           0           |           0            |      1       |
| **Restricted Zone A**  |       1        |           1            |           1           |           1            |           0           |           0            |      1       |
| **Operational Zone A** |       0        |           0            |           1           |           1            |           0           |           0            |      0       |
| **Restricted Zone B**  |       1        |           0            |           0           |           0            |           1           |           0            |      0       |
| **Operational Zone B** |       0        |           0            |           0           |           0            |           0           |           1            |      0       |
|      **Internet**      |       1        |           1            |           1           |           0            |           0           |           0            |      1       |

> **표 해설(Table 3):** 임무 B 활성 단계(Phase 2b)의 초기 네트워크 통신 보안 정책입니다. 행은 출발 영역, 열은 도착 영역이며, **1**은 통신 허용, **0**은 차단을 의미합니다. Phase 2a와 대칭적으로, 이번에는 Operational Zone B가 자기 자신을 제외한 모든 영역과 단절되고 Restricted Zone B는 HQ Network와만 연결됩니다.

<figure markdown>
  ![CAGE Phase 2b Connectivity Diagram](../assets/CAGE-Phase-2b-Connectivity-Diagram.png)
  <figcaption>Figure 5 - Phase 2b Connectivity Diagram (그림 5 - Phase 2b 연결성 다이어그램)</figcaption>
</figure>

## Rewards (보상)

Blue agents start with 0 points and are assigned penalties when green agents are unable to perform their work, when they access a compromised service, and when red chooses the `Impact` action. Penalties change during active missions to reflect the changing criticality of hosts on current operations. All rewards are shown in Tables 4A, 4B, and 4C.

> Blue 에이전트는 0점에서 시작하며, 다음 경우에 페널티(감점)를 받습니다: Green 에이전트가 작업을 수행하지 못할 때, Green 에이전트가 손상된 서비스에 접근할 때, 그리고 Red가 `Impact`(타격) 행동을 선택할 때입니다. 페널티는 현재 작전에서 호스트의 중요도(criticality)가 변하는 것을 반영하기 위해 임무 활성 중에 바뀝니다. 모든 보상은 Table 4A, 4B, 4C에 나와 있습니다.

#### Table 4A: Rewards for green action failures and compromise in Phase 1 O&M

|        **Zone**        | **Local Work Fails** | **Access Service Fails** | **Red impact/access** |
|:----------------------:|:--------------------:|:------------------------:|:---------------------:|
|     **HQ Network**     |          -1          |            -1            |          -3           |
| **Contractor Network** |          0           |            -5            |          -5           |
| **Restricted Zone A**  |          -1          |            -3            |          -1           |
| **Operational Zone A** |          -1          |            -1            |          -1           |
| **Restricted Zone B**  |          -1          |            -3            |          -1           |
| **Operational Zone B** |          -1          |            -1            |          -1           |
|      **Internet**      |          0           |            0             |          0            |

> **표 해설(Table 4A):** Phase 1(운영 및 유지보수, O&M = Operations and Maintenance) 단계에서 Green 행동 실패와 손상에 따른 페널티 값입니다. 행은 영역(Zone), 열의 의미는 다음과 같습니다. **Local Work Fails**: Green의 로컬 작업이 실패했을 때의 감점, **Access Service Fails**: Green이 서비스 접속에 실패했을 때의 감점, **Red impact/access**: Red가 해당 영역을 타격(Impact)하거나 접근했을 때의 감점. 음수 값일수록 더 큰 페널티이며, 값이 클(덜 음수일)수록 영향이 작음을 뜻합니다.

#### Table 4B: Rewards for green action failures and compromise in Phase 2a - Mission A

|        **Zone**        | **Local Work Fails** | **Access Service Fails** | Red impact/access |
|:----------------------:|:--------------------:|:------------------------:|:-----------------:|
|     **HQ Network**     |          -1          |            -1            |        -3         |
| **Contractor Network** |          0           |            0             |         0         |
| **Restricted Zone A**  |          -2          |            -1            |        -3         |
| **Operational Zone A** |         -10          |            0             |        -10        |
| **Restricted Zone B**  |          -1          |            -1            |        -1         |
| **Operational Zone B** |          -1          |            -1            |        -1         |
|      **Internet**      |          0           |            0             |         0         |

> **표 해설(Table 4B):** Phase 2a(임무 A 활성) 단계의 페널티 값입니다. 열 의미는 Table 4A와 같습니다. 임무 A가 활성화되면서 배치 네트워크 A의 중요도가 올라가므로, Operational Zone A의 **Local Work Fails**와 **Red impact/access** 페널티가 -10으로 크게 커지는 점이 핵심입니다.

#### Table 4C: Rewards for green action failures and compromise in Phase 2b - Mission B

|        **Zone**        | **Local Work Fails** | **Access Service Fails** | **Red impact/access** |
|:----------------------:|:--------------------:|:------------------------:|:---------------------:|
|     **HQ Network**     |          -1          |            -1            |          -3           |
| **Contractor Network** |          0           |            0             |           0           |
| **Restricted Zone A**  |          -1          |            -3            |          -3           |
| **Operational Zone A** |          -1          |            -1            |          -1           |
| **Restricted Zone B**  |          -2          |            -1            |          -3           |
| **Operational Zone B** |         -10          |            0             |          -10          |
|      **Internet**      |          0           |            0             |           0           |

> **표 해설(Table 4C):** Phase 2b(임무 B 활성) 단계의 페널티 값입니다. 열 의미는 Table 4A와 같습니다. Table 4B와 대칭적으로, 이번에는 임무 B의 중요도가 올라가 Operational Zone B의 **Local Work Fails**와 **Red impact/access** 페널티가 -10으로 커집니다.

## How to use CybORG (CybORG 사용 방법)

We use the Cyber Operations Research Gym (CybORG) to simulate the cyber environment for each CAGE challenge.

> 우리는 각 CAGE 챌린지의 사이버 환경을 시뮬레이션하기 위해 **CybORG**(Cyber Operations Research Gym)를 사용합니다.

Please see [the Installation Instruction guide](tutorials/01_Getting_Started/1_Introduction.md) for further instructions on how to install and run the environment and see [here](how-to-guides.md) for additional tutorials.

> 환경을 설치하고 실행하는 자세한 안내는 [설치 안내 가이드](tutorials/01_Getting_Started/1_Introduction.md)를 참고하시고, 추가 튜토리얼은 [여기](how-to-guides.md)를 참고하세요.

## How to submit responses (제출 방법)

Submissions are made to the [Codalabs webpage](https://codalab.lisn.upsaclay.fr/competitions/17672) which will automatically evaluate your agent and rank them on the leaderboard. Users will be required to make a Codalabs account in order to submit their agents. Users will then need to go to the 'Participate' tab, click on the 'Submit' section, and then upload their submission.zip file. After waiting some time (depends on how fast your agent is) your result will be automatically uploaded to the leaderboard.

> 제출은 [Codalabs 웹페이지](https://codalab.lisn.upsaclay.fr/competitions/17672)에서 이루어지며, 이 페이지가 자동으로 여러분의 에이전트를 평가하고 리더보드(leaderboard)에 순위를 매깁니다. 에이전트를 제출하려면 Codalabs 계정을 만들어야 합니다. 그런 다음 'Participate' 탭으로 이동해 'Submit' 섹션을 클릭하고 submission.zip 파일을 업로드하면 됩니다. 잠시 기다리면(에이전트가 얼마나 빠른지에 따라 다름) 결과가 자동으로 리더보드에 올라갑니다.

For detailed instructions regarding how to evaluate and submit your agents please refer to the README.md located in the Cyborg/Evaluation folder.

> 에이전트를 평가하고 제출하는 방법에 대한 자세한 안내는 Cyborg/Evaluation 폴더에 있는 README.md를 참고하세요.

We welcome multiple submissions per team. If you resubmit same agent twice, please remove one of them from the leaderboard. If you retrain the same agent architecture, please add 'v2', 'v3', etc... to the agent submission file. If it is an entirely new approach, please change the name of the agent. 

> 팀당 여러 번 제출하는 것을 환영합니다. 동일한 에이전트를 두 번 다시 제출했다면 리더보드에서 그중 하나를 제거해 주세요. 같은 에이전트 아키텍처를 재학습한 경우에는 제출 파일에 'v2', 'v3' 등을 붙여 주세요. 완전히 새로운 접근 방식이라면 에이전트 이름을 변경해 주세요.

We are also imposing an execution time limit on all submissions. Submissions should complete 100 episodes, of length 500, within 3 hours when evaluated on our Amazon EC2 C4.large instance. Any submissions will go beyond this time will be automatically cancelled.

> 또한 모든 제출에는 실행 시간 제한을 둡니다. 제출물은 우리의 Amazon EC2 C4.large 인스턴스에서 평가할 때 길이 500의 에피소드 100개를 3시간 이내에 완료해야 합니다. 이 시간을 초과하는 제출물은 자동으로 취소됩니다.

As part of your submission, we request that you share a description of the methods/techniques used in developing your agents to [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com). We will use this information as part of our in-depth analysis and comparison of the various techniques submitted to the challenge. In hosting the CAGE challenges, one of our main goals is to understand the techniques that lead to effective autonomous cyber defensive agents, as well as those that are not as effective. We are planning on publishing the analysis and taxonomy of the different approaches that create autonomous cyber defensive agents. To that end, we encourage you to also share details on any unsuccessful approaches taken. Please also feel free to share any interesting discoveries and thoughts regarding future work to help us shape the future of the CAGE Challenges.

> 제출의 일환으로, 에이전트 개발에 사용한 방법·기법에 대한 설명을 [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com)으로 공유해 주시기를 요청합니다. 우리는 이 정보를 챌린지에 제출된 다양한 기법을 심층 분석·비교하는 데 활용합니다. CAGE 챌린지를 주최하는 주요 목표 중 하나는, 효과적인 자율 사이버 방어 에이전트로 이어지는 기법은 물론 그다지 효과적이지 않은 기법까지 이해하는 것입니다. 우리는 자율 사이버 방어 에이전트를 만드는 다양한 접근 방식의 분석과 분류 체계(taxonomy)를 발표할 계획입니다. 이를 위해, 시도했으나 성공하지 못한 접근 방식에 대한 세부 내용도 공유해 주시기를 권합니다. 또한 흥미로운 발견이나 향후 연구에 대한 생각도 자유롭게 공유해 주시면 CAGE 챌린지의 미래를 함께 만들어 가는 데 도움이 됩니다.

Any queries regarding the challenge can be submitted via email to [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com).

> 챌린지에 관한 문의는 [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com)으로 이메일을 보내 주시면 됩니다.

We also invite teams to submit full papers on their work on this CAGE challenge or using the CybORG environment to IJCAI, AAAI, ICML or any other venue of their choice. 

> 또한 각 팀이 이번 CAGE 챌린지에 대한 연구나 CybORG 환경을 활용한 연구를 정식 논문으로 IJCAI, AAAI, ICML 또는 원하는 다른 학회에 제출하도록 권장합니다.

Please cite the challenge announcement as follows to reference the challenge:

> 챌린지를 인용할 때는 챌린지 공지(announcement)를 다음과 같이 인용해 주세요.

```
@misc{cage_challenge_4_announcement,
  author = {TTCP CAGE Working Group},
  Title = {TTCP CAGE Challenge 4},
  Publisher = {GitHub}, 
  Howpublished = {\url{https://github.com/cage-challenge/cage-challenge-4}},
  Year = {2023}
}
```

In addition, authors may reference the following paper that describes CybORG:

> 추가로, 저자들은 CybORG를 설명하는 다음 논문을 인용할 수 있습니다.

```
@PROCEEDINGS{cyborg_acd_2021,
  author = {Maxwell Standen, Martin Lucas, David Bowman, Toby J\. Richer, Junae Kim and Damian Marriott},
  Title = {CybORG: A Gym for the Development of Autonomous Cyber Agents},
  booktitle = {IJCAI-21 1st International Workshop on Adaptive Cyber Defense.} 
  Publisher = {arXiv},
  Year = {2021}
}
```

The challenge software can be referenced as:

> 챌린지 소프트웨어는 다음과 같이 인용할 수 있습니다.

```
@misc{cage_cyborg_2023,
  Title = {Cyber Operations Research Gym},
  Note = {Created by Maxwell Standen, David Bowman, Olivia Naish, Ben Edwards, James Drane, Claire Owens, KC Cowan, Wayne Gould, Mitchell Kiely, Son Hoang, Toby Richer, Martin Lucas, Richard Van Tassel, Phillip Vu, Natalie Konschnik, Joshua Collyer, Calum Fairchild, Thomas Harding},
  Publisher = {GitHub},
  Howpublished = {\url{https://github.com/cage-challenge/CybORG}},
  Year = {2022}
}

```

## Evaluation (평가)
A leaderboard for submissions will be maintained on [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672) throughout the challenge's time frame.

> 제출물에 대한 리더보드는 챌린지 기간 내내 [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672)에서 유지됩니다.

The `evaluation.py` file is designed to provide a standardised evaluation for an agent, which will be used in the Codalabs validation process. Each blue agent will be evaluated against the `FiniteStateRedAgent` in 100 randomised episodes, where each episode is 500 timesteps long.

> `evaluation.py` 파일은 에이전트에 대한 표준화된 평가를 제공하도록 설계되었으며, Codalabs 검증 과정에서 사용됩니다. 각 Blue 에이전트는 무작위로 생성된 100개의 에피소드에서 `FiniteStateRedAgent`를 상대로 평가되며, 각 에피소드는 500스텝(timestep) 길이입니다.

If running locally, information about the agent's actions, observations, mean reward, and standard deviation will be outputted as text files after this file completes its run. Details about how do this is in the README.md file within the Evaluation folder. If running on Codalabs, only the mean reward will be extracted and used to update the leaderboard. 

> 로컬에서 실행하는 경우, 이 파일의 실행이 끝난 뒤 에이전트의 행동(Action), 관찰값(Observation), 평균 보상(mean reward), 표준편차(standard deviation) 정보가 텍스트 파일로 출력됩니다. 이를 수행하는 방법에 대한 자세한 내용은 Evaluation 폴더 안의 README.md에 있습니다. Codalabs에서 실행하는 경우에는 평균 보상만 추출되어 리더보드 갱신에 사용됩니다.

## Important dates (주요 일정)

- **20 Feb 2024:** Challenge 4 released. Development phase begins. During the development phase, we will be debugging any unexpectant issues that may be found by the participants. Please ensure that you watch the repo so that you're notified if any changes are required.

- **29 Mar 2024 23:59 (UTC):** Development phase ends. Competition phase begins. During the comptetition phase, unless it is absolutely necessary, we will not be changing the code base, as this allows participants enough time to train their agents on a constant environment.

- **10 May 2024 23:59 (UTC):** Competition phase ends. Final results announced on [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672) leaderboard.

> - **2024년 2월 20일:** Challenge 4 공개. 개발 단계(development phase) 시작. 개발 단계 동안 우리는 참가자가 발견할 수 있는 예기치 못한 문제를 디버깅합니다. 변경이 필요할 때 알림을 받을 수 있도록 레포를 watch 설정해 두세요.
> - **2024년 3월 29일 23:59 (UTC):** 개발 단계 종료. 경쟁 단계(competition phase) 시작. 경쟁 단계 동안에는 꼭 필요한 경우가 아니면 코드베이스를 변경하지 않습니다. 이를 통해 참가자가 변하지 않는 환경에서 에이전트를 충분히 학습할 시간을 확보할 수 있습니다.
> - **2024년 5월 10일 23:59 (UTC):** 경쟁 단계 종료. 최종 결과를 [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672) 리더보드에 발표.

## Appendix A – Action sets (부록 A – 행동 집합)

|**Action name**|**Team**|<div style = "width:200px">**Description of action**</div>|**Time (ticks)**|**Local/ remote**|**Chance of being flagged as malicious**|**Chance of faliure**|**Parameters**| **Output** |
|:-------------:|:------:|:-----------------------:|:--------------:|:--------------:|:--------------------------------------:|:-------------------:|:------------:|:----------:|
|GreenAccessService|Green|Communicate with a server in the local zone or another zone. Green will randomly choose from a list of IP addresses depending on the mission phase. If it can’t reach the server then blue receives a penalty. This action triggers a false network connection alert picked up by Monitor, with a low probability of occurrence.|1|Remote|Low (1%) (`fp_detection_rate` set through EnterpriseGreenAgent)|None|agent, session_id, src_ip, allowed_subnets, fp_detection_rate|Success/Failure|
|GreenLocalWork|Green|Do work on the local host without communicating. Green hosts take this action when they are not accessing services or sleeping. In addition to a chance of being flagged as malicious, there is a small chance that this action results in red gaining a foothold on the host (e.g. as a result of a Phishing email).|1|Local|Low (1%) (`fp_detection_rate` set through EnterpriseGreenAgent)|None|agent, session_id, ip_address,  fp_detection_rate, phishing_error_rate|Success/Failure|
|Monitor|Blue|Collection of information about flagged malicious activity on the network. Corresponds to action ID 1: Scan in the OpenC2 specification. This action occurs automatically as a default action.|1|-|None|None|session, agent|Success/Failure. Network connections and associated processes that are identified as malicious.|
|Analyse|Blue|Collection of further information relating to malware, on a specific host to enable blue to better identify if red is present on the system. Corresponds to action ID 30: Investigate in the OpenC2 specification.|2|-|None|None|session, agent, hostname|Success/Failure. Information on files associated with recent alerts|
|DeployDecoy|Blue|Setup of a decoy service (type randomly assigned) on a specified host. Green agents do not access these services, so any access is an unambiguous indicator of red activity. Decoy services cannot replace legitimate services. When a red agent discovers or exploits a decoy service, the blue agent will receive alerts involving that host or service. The red agent will not be able to successfully exploit the decoy service.|2|-|None|None|session, agent, hostname|Success, if a legitimate service is not already running. Failure if there is already a legitimate service running on the target. Decoys also generate an alert if the red agent accesses the new service.|
|Remove|Blue|Attempting to remove red from a host by destroying malicious processes, files and services. This action attempts to stop all processes identified as malicious by the monitor action. Corresponds to action ID 10: Stop in the OpenC2 specification.|3|-|None|None|session, agent, hostname|Success/Failure|
|Restore|Blue|Restoring a system to a known good state. This has significant consequences for system availability. Corresponds to action ID 23: Restore in the OpenC2 specification.|5|-|None|None|session, agent, hostname|Success/Failure|
|BlockTraffic|Blue|Block traffic to and from the specified zone. If green agents are attempting to communicate to that zone this will result in penalties.|1|Local|None|None|session, agent, from_subnet, to_subnet|Success/Failure|
|AllowTraffic|Blue|Allow traffic to and from the specified zone.|1|Local|None|None|session, agent, from_subnet, to_subnet|Success/Failure|
|DiscoverRemoteSystems|Red|ATT&CK Technique T1018 Remote System Discovery. Discovers new hosts/IP addresses in the network through active scanning using tools such as ping.|1|Remote|None|None|session, agent, subnet|Success/Failure. IP addresses in the chosen subnet from hosts that respond to ping.|
|AggressiveServiceDiscovery|Red|ATT&CK Technique T1046 Network Service Scanning. Discovers responsive services on a selected host by initiating a connection with that host.|1|Remote|High (75%)|None|session, agent, ip_address|Success/Failure. Ports and service information.|
|StealthServiceDiscovery|Red|Same as AggressiveServiceDiscovery but slower and quieter (i.e., lower chance of raising alerts).|3|Remote| Medium (25%)|None|session, agent, ip_address|Success/Failure. Ports and service information.|
|Exploit Network Services|Red|ATT&CK Technique T1210 Exploitation of Remote Services. This action attempts to exploit a specified service on a remote system.|4|Remote|None|Medium (Failure dependant on weighted exploit choice)|session, agent, ip_address|Success/Failure. Initial recon of host if successful.|
|PrivilegeEscalate|Red|ATT&CK Tactic TA0004 Privilege Escalation. This action escalates the agent’s privilege on the host.|2|Local|None|None|session, agent, hostname|Success/Failure. Internal information now available due to increased access to host.|
|Impact|Red|ATT&CK Technique T1489 Service Stop. This action disrupts the performance of the network and fulfils red’s objective of denying the operational service.|2|Local|None|None|session, agent, hostname|Success/Failure|
|DegradeServices|Red|If red has root privileges on a host, it may degrade the user experience for a green agent (for example by randomly dropping keystrokes or causing other mischief). Under the effect of Degrade, GreenLocalWork actions have higher failure rates (resulting in additional penalties for blue).|2|Remote|None|None|session, agent, hostname|Success/Failure|
|DiscoverDeception|Red|Probe a host to determine if it is running decoy services.|2|Remote|None|Medium (50% chance false negative, 10% chance false positive)|session, agent, ip_address|Success/Failure. Believe legitimate or believe decoy.|
|Withdraw|Red|Remove red presence from target host.|1|Remote|None|None|session, agent, hostname, ip_address|Success|
|Sleep|All|Take no action this tick.|1|Local|None|None|None|None|

> 아래는 위 행동 표를 한국어로 옮긴 것입니다. 행동 이름과 식별자(예: `fp_detection_rate`), ATT&CK 기법 번호, 파라미터 이름은 코드 토큰이므로 영어 그대로 둡니다. 열 머리글의 뜻: **Action name**(행동 이름), **Team**(소속 팀), **Description of action**(행동 설명), **Time (ticks)**(소요 시간, 틱 단위), **Local/ remote**(로컬/원격), **Chance of being flagged as malicious**(악성으로 탐지될 확률), **Chance of failure**(실패 확률), **Parameters**(파라미터), **Output**(출력 결과).

|**행동 이름**|**팀**|<div style = "width:200px">**행동 설명**</div>|**소요 시간 (틱)**|**로컬/원격**|**악성으로 탐지될 확률**|**실패 확률**|**파라미터**| **출력** |
|:-------------:|:------:|:-----------------------:|:--------------:|:--------------:|:--------------------------------------:|:-------------------:|:------------:|:----------:|
|GreenAccessService|Green|로컬 영역 또는 다른 영역의 서버와 통신합니다. Green은 임무 단계에 따라 IP 주소 목록에서 무작위로 선택합니다. 서버에 도달하지 못하면 Blue가 페널티를 받습니다. 이 행동은 Monitor가 포착하는 거짓 네트워크 연결 경보를 낮은 확률로 발생시킵니다.|1|Remote(원격)|낮음(1%) (`fp_detection_rate`는 EnterpriseGreenAgent를 통해 설정)|없음|agent, session_id, src_ip, allowed_subnets, fp_detection_rate|성공/실패|
|GreenLocalWork|Green|통신 없이 로컬 호스트에서 작업합니다. Green 호스트는 서비스에 접근하거나 대기(sleep)하지 않을 때 이 행동을 취합니다. 악성으로 탐지될 확률에 더해, 이 행동으로 Red가 호스트에 거점을 얻을 작은 확률이 있습니다(예: 피싱 이메일의 결과).|1|Local(로컬)|낮음(1%) (`fp_detection_rate`는 EnterpriseGreenAgent를 통해 설정)|없음|agent, session_id, ip_address,  fp_detection_rate, phishing_error_rate|성공/실패|
|Monitor|Blue|네트워크상에서 악성으로 표시된 활동에 대한 정보를 수집합니다. OpenC2 규격의 action ID 1: Scan에 해당합니다. 이 행동은 기본 행동으로 자동 수행됩니다.|1|-|없음|없음|session, agent|성공/실패. 악성으로 식별된 네트워크 연결과 관련 프로세스.|
|Analyse|Blue|특정 호스트에서 멀웨어 관련 추가 정보를 수집하여, Blue가 시스템에 Red가 있는지 더 잘 식별하도록 합니다. OpenC2 규격의 action ID 30: Investigate에 해당합니다.|2|-|없음|없음|session, agent, hostname|성공/실패. 최근 경보와 관련된 파일 정보.|
|DeployDecoy|Blue|지정한 호스트에 디코이 서비스(유형은 무작위 지정)를 설치합니다. Green 에이전트는 이 서비스에 접근하지 않으므로, 모든 접근은 Red 활동의 명백한 신호가 됩니다. 디코이 서비스는 정상 서비스를 대체할 수 없습니다. Red 에이전트가 디코이 서비스를 발견하거나 익스플로잇하면 Blue 에이전트는 해당 호스트·서비스 관련 경보를 받습니다. Red 에이전트는 디코이 서비스를 성공적으로 익스플로잇할 수 없습니다.|2|-|없음|없음|session, agent, hostname|대상에 정상 서비스가 이미 실행 중이 아니면 성공. 이미 정상 서비스가 실행 중이면 실패. Red 에이전트가 새 서비스에 접근하면 디코이가 경보도 발생시킵니다.|
|Remove|Blue|악성 프로세스·파일·서비스를 파괴하여 호스트에서 Red를 제거하려 시도합니다. 이 행동은 monitor 행동이 악성으로 식별한 모든 프로세스를 중지하려 합니다. OpenC2 규격의 action ID 10: Stop에 해당합니다.|3|-|없음|없음|session, agent, hostname|성공/실패|
|Restore|Blue|시스템을 알려진 정상 상태(known good state)로 복원합니다. 이는 시스템 가용성에 상당한 영향을 줍니다. OpenC2 규격의 action ID 23: Restore에 해당합니다.|5|-|없음|없음|session, agent, hostname|성공/실패|
|BlockTraffic|Blue|지정한 영역을 오가는 트래픽을 차단합니다. Green 에이전트가 그 영역으로 통신하려 한다면 페널티로 이어집니다.|1|Local(로컬)|없음|없음|session, agent, from_subnet, to_subnet|성공/실패|
|AllowTraffic|Blue|지정한 영역을 오가는 트래픽을 허용합니다.|1|Local(로컬)|없음|없음|session, agent, from_subnet, to_subnet|성공/실패|
|DiscoverRemoteSystems|Red|ATT&CK Technique T1018 Remote System Discovery(원격 시스템 탐색). ping 같은 도구를 사용한 능동 스캔으로 네트워크에서 새로운 호스트/IP 주소를 탐색합니다.|1|Remote(원격)|없음|없음|session, agent, subnet|성공/실패. 선택한 서브넷에서 ping에 응답한 호스트의 IP 주소.|
|AggressiveServiceDiscovery|Red|ATT&CK Technique T1046 Network Service Scanning(네트워크 서비스 스캐닝). 선택한 호스트와 연결을 시작해 응답하는 서비스를 탐색합니다.|1|Remote(원격)|높음(75%)|없음|session, agent, ip_address|성공/실패. 포트와 서비스 정보.|
|StealthServiceDiscovery|Red|AggressiveServiceDiscovery와 같지만 더 느리고 조용합니다(즉, 경보를 일으킬 확률이 더 낮음).|3|Remote(원격)|중간(25%)|없음|session, agent, ip_address|성공/실패. 포트와 서비스 정보.|
|Exploit Network Services|Red|ATT&CK Technique T1210 Exploitation of Remote Services(원격 서비스 익스플로잇). 원격 시스템의 지정된 서비스를 익스플로잇하려 시도합니다.|4|Remote(원격)|없음|중간(가중치가 적용된 익스플로잇 선택에 따라 실패 여부 결정)|session, agent, ip_address|성공/실패. 성공 시 호스트에 대한 초기 정찰 정보.|
|PrivilegeEscalate|Red|ATT&CK Tactic TA0004 Privilege Escalation(권한 상승). 호스트에서 에이전트의 권한을 상승시킵니다.|2|Local(로컬)|없음|없음|session, agent, hostname|성공/실패. 호스트 접근 권한이 높아져 이제 이용 가능한 내부 정보.|
|Impact|Red|ATT&CK Technique T1489 Service Stop(서비스 중지). 네트워크 성능을 방해하며, 운영 서비스를 거부(denial)한다는 Red의 목표를 달성합니다.|2|Local(로컬)|없음|없음|session, agent, hostname|성공/실패|
|DegradeServices|Red|Red가 호스트에 root 권한을 가지고 있으면 Green 에이전트의 사용자 경험을 저하시킬 수 있습니다(예: 키 입력을 무작위로 누락시키거나 다른 방해를 가함). Degrade 효과가 적용되면 GreenLocalWork 행동의 실패율이 높아집니다(Blue에 추가 페널티 발생).|2|Remote(원격)|없음|없음|session, agent, hostname|성공/실패|
|DiscoverDeception|Red|호스트가 디코이 서비스를 실행 중인지 판별하기 위해 탐침(probe)합니다.|2|Remote(원격)|없음|중간(거짓 음성 50%, 거짓 양성 10% 확률)|session, agent, ip_address|성공/실패. 정상으로 판단 또는 디코이로 판단.|
|Withdraw|Red|대상 호스트에서 Red의 존재를 제거합니다.|1|Remote(원격)|없음|없음|session, agent, hostname, ip_address|성공|
|Sleep|All(전체)|이번 틱에 아무 행동도 하지 않습니다.|1|Local(로컬)|없음|없음|없음|없음|

## Appendix B – Agent observation (부록 B – 에이전트 관찰값)

The BlueEnterpriseWrapper performs utility functions that support MARL algorithms by conforming to the PettingZoo Environment. This wrapper alters the observation to enable the use of Deep Reinforcement Learning techniques. This appendix describes the altered observation.

> `BlueEnterpriseWrapper`는 PettingZoo Environment 규격을 따름으로써 MARL(다중 에이전트 강화학습) 알고리즘을 지원하는 유틸리티 기능을 수행합니다. 이 래퍼(Wrapper)는 심층 강화학습 기법을 사용할 수 있도록 관찰값(Observation)을 변형합니다. 이 부록에서는 변형된 관찰값을 설명합니다.

The table below indicates what data is presented at each index of the observation of an agent. We use the symbol H to denote the maximum number of hosts in the local subnet, which is equal to 16 (10 user hosts and 6 servers). These hosts are ordered from server hosts 0-6, followed by user hosts 0-10. If a host is not present for a given episode, its corresponding slot in the vector will be zero for the duration of the episode. All ranges in the following tables are inclusive, so 1…H includes both 1 and H.

> 아래 표는 에이전트 관찰값의 각 인덱스(index)에 어떤 데이터가 들어 있는지를 나타냅니다. 기호 H는 로컬 서브넷의 최대 호스트 수를 뜻하며, 그 값은 16입니다(사용자 호스트 10대와 서버 6대). 이 호스트들은 서버 호스트 0-6 순으로 먼저 정렬되고, 그다음 사용자 호스트 0-10 순으로 정렬됩니다. 특정 에피소드에 존재하지 않는 호스트가 있으면, 벡터에서 그에 대응하는 슬롯은 해당 에피소드 동안 0이 됩니다. 다음 표들의 모든 범위는 양 끝을 포함하므로, 1…H는 1과 H를 모두 포함합니다.

Similarly, we use the symbol S to denote the number of subnets, which is always equal to 9 (2 Operational Zones, 2 Restricted Zones, Internet, Contractor Network, 3 subnets in the HQ zone). To ensure consistency across runs, all subnets are sorted alphabetically.

> 마찬가지로 기호 S는 서브넷의 수를 뜻하며, 그 값은 항상 9입니다(운영 영역 2개, 제한 영역 2개, Internet, 협력업체 네트워크, HQ 영역 내 서브넷 3개). 실행 간 일관성을 보장하기 위해 모든 서브넷은 알파벳순으로 정렬됩니다.

There general structure of the observation vector is as follows where n is the number of subnets included in the observation space:

> 관찰값 벡터의 전반적인 구조는 다음과 같으며, 여기서 n은 관찰 공간에 포함된 서브넷의 수입니다.

<center>

|**Index**            |**Length**|**Description**|**Value**|
|:-------------------:|:--------:|:-------------:|:---------------------------|
| 0                   | 1        | Mission Phase | 0: Mission Phase 1 <br />1: Mission Phase 2A <br />2: Mission Phase 2B |
| 1                   | 3S+2H    | Subnet 0 Info | See "Subnet Info" Table |
| 3S+2H+1             | ...      | ...           | ... |
| 3(n-1)S+2(n-1)H+1   | 3S+2H    | Subnet n Info | ' ' |
| 3nS+2nH+1           | 4x8      | Message Block | User Defined (See Below) |

</center>

> **표 해설(관찰값 전체 구조):** 행은 관찰값 벡터 내 위치를 나타냅니다. 열 머리글의 뜻은 다음과 같습니다. **Index**(시작 인덱스), **Length**(차지하는 길이), **Description**(설명), **Value**(값). 각 행의 의미: 인덱스 0에는 임무 단계(Mission Phase, 0=Phase 1, 1=Phase 2A, 2=Phase 2B)가 길이 1로 들어갑니다. 인덱스 1부터는 서브넷별 정보(Subnet Info) 블록이 각 3S+2H 길이로 반복되며(아래 "Subnet Info" 표 참고), 마지막에 메시지 블록(Message Block)이 4×8 = 32비트로 들어갑니다(값은 사용자 정의, 아래 설명 참고). S는 서브넷 수, H는 최대 호스트 수, n은 해당 에이전트가 관찰하는 서브넷 수입니다.

The message block contains four, 8-bit messages from the other agents, with each index corresponding to a specific agent (0-4 in order, excluding self). The contents of these 8-bit messages are defined by the user, but will default to zero if not specified.

> 메시지 블록(Message Block)에는 다른 에이전트들이 보낸 8비트 메시지 4개가 들어 있으며, 각 인덱스는 특정 에이전트(자기 자신을 제외하고 0-4 순서)에 대응합니다. 이 8비트 메시지의 내용은 사용자가 정의하지만, 지정하지 않으면 기본값 0이 됩니다.

The "Subnet Info" block for each subnet is further subdivided as follows:

> 각 서브넷에 대한 "Subnet Info"(서브넷 정보) 블록은 다음과 같이 더 세분화됩니다.

<center>

|**Relative Index**|**Length**|**Description**                   |**Element Values (Boolean)**|
|:-------------------:|:--------:|:--------------------------------:|:---------------------------|
| 0                   | S        | One-hot Encoded Subnet Vector    | 1: Current Subnet <br />0: All Other Subnets |
| S                   | S        | Blocked Subnets                  | 1: Subnet Blocked <br />0: Subnet Not Blocked |
| 2S                  | S        | Communication Policy             | 1: Subnet *Should* be Blocked <br />0: Subnet *Should Not* be Blocked |
| 3S                  | H        | Malicious Process Event Detected | 1: Malicious Process Detected on Host <br />0: No Events |
| 3S+H                | H        | Malicious Network Event Detected | 1: Malicious Connection Detected on Host <br />0: No Events |

</center>

> **표 해설(Subnet Info 블록):** 한 서브넷 정보 블록 안의 상대 위치별 구성입니다. 열 머리글의 뜻: **Relative Index**(블록 내 상대 인덱스), **Length**(길이), **Description**(설명), **Element Values (Boolean)**(원소 값, 불리언). 각 구간의 의미는 다음과 같습니다.
> - **One-hot Encoded Subnet Vector**(원-핫 인코딩 서브넷 벡터, 길이 S): 1=현재 서브넷, 0=그 외 모든 서브넷.
> - **Blocked Subnets**(차단된 서브넷, 길이 S): 1=서브넷 차단됨, 0=차단되지 않음.
> - **Communication Policy**(통신 정책, 길이 S): 1=차단되어야 함(*should* be blocked), 0=차단되지 않아야 함.
> - **Malicious Process Event Detected**(악성 프로세스 이벤트 탐지, 길이 H): 1=호스트에서 악성 프로세스 탐지됨, 0=이벤트 없음.
> - **Malicious Network Event Detected**(악성 네트워크 이벤트 탐지, 길이 H): 1=호스트에서 악성 연결 탐지됨, 0=이벤트 없음.

In this challenge, blue agents 0-3 are responsible for defending a single subnet each (n=1), while blue agent 4 defends three (n=3). For this reason, blue agent 4 has a longer observation than the others as the other agents only have a single subnet info block. If the `pad_spaces=True` option is supplied to `BlueEnterpriseWrapper`, the area *after* the message block will be filled with zeros for these agents.

> 이 챌린지에서 Blue 에이전트 0-3은 각각 단일 서브넷을 방어하고(n=1), Blue 에이전트 4는 세 개를 방어합니다(n=3). 이 때문에 다른 에이전트는 서브넷 정보 블록이 하나뿐인 반면, Blue 에이전트 4는 관찰값이 더 깁니다. `BlueEnterpriseWrapper`에 `pad_spaces=True` 옵션을 주면, 이 에이전트들의 경우 메시지 블록 *뒤*의 영역이 0으로 채워집니다.
