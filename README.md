# TTCP CAGE Challenge 4: Challenge Details (TTCP CAGE Challenge 4: 챌린지 상세)

> TTCP CAGE Challenge 4: 챌린지 상세 설명입니다.

![TTCP-Logo](/documentation/docs/assets/TTCP-Logo-small.png)
![Cage-Logo](/documentation/docs/assets/CAGE-Logo-small.png)

## Published Results (발표된 연구 결과)
The results of this challenge were published at the 39th Annual AAAI Conference on Artificial Intelligence [Exploring the Efficacy of Multi-Agent Reinforcement Learning for Autonomous Cyber Defence: A CAGE Challenge 4 Perspective](https://ojs.aaai.org/index.php/AAAI/article/view/35158). Please use one or both of the following citations when citing this challenge.

> 이 챌린지의 결과는 제39회 AAAI 인공지능 학회(39th Annual AAAI Conference on Artificial Intelligence)에서 [Exploring the Efficacy of Multi-Agent Reinforcement Learning for Autonomous Cyber Defence: A CAGE Challenge 4 Perspective](https://ojs.aaai.org/index.php/AAAI/article/view/35158) 논문으로 발표되었습니다. 이 챌린지를 인용하실 때는 아래 두 인용문 중 하나 또는 둘 다 사용해 주세요.
```
@inproceedings{kiely2025exploring,
  title={Exploring the Efficacy of Multi-Agent Reinforcement Learning for Autonomous Cyber Defence: A CAGE Challenge 4 Perspective},
  author={Kiely, Mitchell and Ahiskali, Metin and Borde, Etienne and Bowman, Benjamin and Bowman, David and van Bruggen, Dirk and Cowan, KC and Dasgupta, Prithviraj and Devendorf, Erich and Edwards, Ben and others},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={39},
  number={28},
  pages={28907--28913},
  year={2025}
}
```
> (첫 번째 인용문은 위 AAAI 학회 논문입니다.)

and [CAGE challenge 4: A scalable multi-agent reinforcement learning gym for autonomous cyber defence](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021)

> 그리고 [CAGE challenge 4: A scalable multi-agent reinforcement learning gym for autonomous cyber defence](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021) 논문입니다.

```
@article{kiely2025cage,
  title={CAGE challenge 4: A scalable multi-agent reinforcement learning gym for autonomous cyber defence},
  author={Kiely, Mitchell and Ahiskali, Metin and Borde, Etienne and Bowman, Benjamin and Bowman, David and Van Bruggen, Dirk and Cowan, KC and Dasgupta, Prithviraj and Devendorf, Erich and Edwards, Ben and others},
  journal={AI Magazine},
  volume={46},
  number={3},
  pages={e70021},
  year={2025},
  publisher={Wiley Online Library}
}
```

## Introduction (소개)

The TTCP CAGE Challenges are a series of public challenges instigated to foster the development of autonomous cyber defensive agents. 
The CAGE Challenges present different cybersecurity scenarios inspired by real-world situations in a simulated environment. 

> TTCP CAGE 챌린지는 **자율 사이버 방어 에이전트**(스스로 판단해 사이버 공격을 막는 AI)의 개발을 촉진하기 위해 시작된 공개 챌린지 시리즈입니다.
> CAGE 챌린지는 실제 상황에서 착안한 다양한 사이버 보안 시나리오를 시뮬레이션 환경에서 제시합니다.

The first CAGE Challenge was released to the public in August 2021, the second in April 2022 and the third in September 2022. 
The challenges use the Cyber Operations Research Gym (CybORG) to provide a high-fidelity cyber simulation for the training and evaluation of AI algorithms such as Deep Reinforcement Learning. 
The CAGE activity aims to run a series of challenges of increasing complexity and realism.

> 첫 번째 CAGE 챌린지는 2021년 8월, 두 번째는 2022년 4월, 세 번째는 2022년 9월에 공개되었습니다.
> 이 챌린지들은 **CybORG**(Cyber Operations Research Gym)를 사용해 심층 강화학습(Deep Reinforcement Learning) 같은 AI 알고리즘의 학습과 평가를 위한 정밀도 높은 사이버 시뮬레이션을 제공합니다.
> CAGE 활동의 목표는 복잡도와 현실성을 점차 높여가는 일련의 챌린지를 운영하는 것입니다.

This CAGE Challenge 4 (CC4) returns to a defence industry enterprise environment, and introduces a Multi-Agent Reinforcement Learning (MARL) scenario.

> 이번 CAGE Challenge 4(CC4)는 방위 산업 엔터프라이즈 환경으로 돌아오며, 다중 에이전트 강화학습(Multi-Agent Reinforcement Learning, MARL) 시나리오를 새로 도입합니다.

## Scenario Narrative (시나리오 배경)

Tensions continue to escalate between the nations of Florin and Guilder. As part of regular border patrols, Florin utilises unmanned drones for reconnaissance and communication purposes. Guilder wishes to disrupt drone operations by performing a cyber-attack against the base station where the activity of the patrols is coordinated.

> 가상의 두 국가 Florin과 Guilder 사이의 긴장이 계속 고조되고 있습니다. Florin은 정기 국경 순찰의 일환으로 정찰과 통신 목적의 무인 드론을 운용합니다. Guilder는 순찰 활동을 통제하는 기지국(base station)에 사이버 공격을 가해 드론 작전을 방해하려 합니다.

You have successfully developed several cyber defence agents for Florin (CAGE Challenges 1-3) and have now been tasked with developing an agent to protect the base station. The network here consists of a range of operational and back-office enterprise networks which support various military operations. Additionally, the drones themselves are controlled via a contractor subnet which connects to the base via the internet. For security purposes the network is highly segmented into security zones and thus a multi-agent solution is required, with each agent protecting its own security zone. Additionally, communication between agents is highly restricted and bandwidth is limited.

> 여러분은 Florin을 위해 여러 사이버 방어 에이전트를 성공적으로 개발해 왔으며(CAGE Challenge 1-3), 이번에는 기지국을 보호할 에이전트를 개발하는 임무를 맡았습니다. 이 네트워크는 다양한 군사 작전을 지원하는 여러 운영용·후방 지원용 엔터프라이즈 네트워크로 구성됩니다. 또한 드론 자체는 인터넷을 통해 기지에 연결되는 협력업체 서브넷(contractor subnet)을 거쳐 제어됩니다. 보안을 위해 네트워크는 여러 **보안 영역**(security zone)으로 고도로 분할되어 있으며, 따라서 각 에이전트가 자신의 보안 영역을 보호하는 다중 에이전트 방식의 해법이 필요합니다. 게다가 에이전트 간 통신은 매우 제한적이고 대역폭(bandwidth)도 한정되어 있습니다.

The agent’s main task is to maintain operational capabilities while preventing malicious activity on the network. This is complicated by the fact that operational priorities change over time, depending on different phases of the mission. However, its general priorities within a given phase are as follows.

> 에이전트의 주된 임무는 네트워크상의 악성 활동을 막으면서 운영 능력을 유지하는 것입니다. 이는 임무 단계(phase)에 따라 운영 우선순위가 시간이 지나며 변한다는 점 때문에 더 까다로워집니다. 다만 특정 단계 안에서의 일반적인 우선순위는 다음과 같습니다.

1. Maintain service of critical network infrastructure to ensure sensitive operational capabilities are not impacted.
2. Where possible, maintain enterprise servers to ensure less sensitive, day-to-day operations are not impacted.
3. Maintain access to public services provided by Florin.

> 1. 민감한 운영 능력이 영향을 받지 않도록 핵심 네트워크 인프라의 서비스를 유지합니다.
> 2. 가능한 경우, 덜 민감한 일상 업무가 영향을 받지 않도록 엔터프라이즈 서버를 유지합니다.
> 3. Florin이 제공하는 공개 서비스(public service)에 대한 접근을 유지합니다.

## Challenge Details (챌린지 상세)

The network for this challenge is split into four smaller networks as can be seen in Figure 1. Two of these are deployed networks, one is the Headquarters (HQ) network and another is the Contractor network. These networks connect together via the internet.

> 이번 챌린지의 네트워크는 Figure 1에서 볼 수 있듯이 네 개의 작은 네트워크로 나뉩니다. 그중 두 개는 배치 네트워크(deployed network), 하나는 본부(Headquarters, HQ) 네트워크, 나머지 하나는 협력업체 네트워크(Contractor network)입니다. 이 네트워크들은 인터넷을 통해 서로 연결됩니다.

Each deployed network consists of two security zones: a restricted zone and an operational zone. The Headquarters network consists of three security zones: a Public Access Zone, an Admin Zone and an Office Network. The Contractor network only contains a single UAV control zone.

> 각 배치 네트워크는 두 개의 보안 영역, 즉 제한 영역(restricted zone)과 운영 영역(operational zone)으로 구성됩니다. 본부(HQ) 네트워크는 세 개의 보안 영역, 즉 공개 접근 영역(Public Access Zone), 관리 영역(Admin Zone), 사무 네트워크(Office Network)로 구성됩니다. 협력업체 네트워크는 단 하나의 UAV(무인기) 제어 영역만 포함합니다.

In order to encourage the development of robust agents, the number of hosts in each security zone and their services will be randomised. Indeed, each zone will have between 1-6 servers and 3-10 user hosts. Each host and server will have a minimum of 1 service with a maximum of 5.

> 견고한 에이전트의 개발을 유도하기 위해, 각 보안 영역의 호스트(host) 수와 그 서비스는 무작위로 정해집니다. 구체적으로, 각 영역은 1~6개의 서버와 3~10개의 사용자 호스트(user host)를 갖습니다. 각 호스트와 서버는 최소 1개에서 최대 5개의 서비스를 갖습니다.

<figure markdown>
  <!-- ![CAGE Network Laydown](/assets/CAGE-Network-Diagram.png) -->
  <img src="/documentation/docs/assets/CAGE-Network-Diagram.png" alt="CC4 Network Diagram" width="750">
  <figcaption>Figure 1 - Network Laydown (그림 1 - 네트워크 배치도)</figcaption>
</figure>

The network will have 5 network defenders. Each deployed network will have two, one for each security zone. The Headquarters will have a single defensive agent for all zones, while the Contractor network will be undefended.

> 네트워크에는 5명의 네트워크 방어자가 있습니다. 각 배치 네트워크에는 보안 영역별로 한 명씩, 총 두 명이 배치됩니다. 본부(HQ)는 모든 영역을 담당하는 단일 방어 에이전트를 두고, 협력업체 네트워크는 방어되지 않은 상태로 남습니다.

Red team begins the operation with access to a random machine in the contractor network and attempts to pivot throughout the network. Every turn there is a small chance that a red agent will spawn if green opens a phishing email and red can also spawn in networks, when a green user accesses a compromised service. There is a maximum of one red agent in each zone, though these agents can maintain a presence on multiple hosts. While Blue team may succeed in removing all traces of red team from a network, red will always maintain a foothold in the Contractor Network. 

> Red 팀(공격 측)은 협력업체 네트워크 내 무작위 머신에 대한 접근 권한을 가진 채 작전을 시작하며, 네트워크 전반으로 거점을 옮겨가려(pivot) 시도합니다. 매 턴마다 Green 에이전트(정상 사용자)가 피싱 이메일(phishing email)을 열면 낮은 확률로 Red 에이전트가 생성될 수 있고, Green 사용자가 침해된 서비스에 접근할 때에도 네트워크 안에서 Red 에이전트가 생성될 수 있습니다. 각 영역에는 최대 한 명의 Red 에이전트만 존재할 수 있지만, 이들은 여러 호스트에 동시에 존재(presence)할 수 있습니다. Blue 팀(방어 측)이 네트워크에서 Red 팀의 흔적을 모두 제거하는 데 성공하더라도, Red는 협력업체 네트워크에서는 항상 발판(foothold)을 유지합니다.

The red agents will each use a randomly selected strategy.

> 각 Red 에이전트는 무작위로 선택된 전략을 사용합니다.

<figure markdown>
  <!-- ![CAGE Deployed Network A](/assets/CAGE-Deployed-Network-A.png) -->
  <img src="/documentation/docs/assets/CAGE-Deployed-Network-A.png" alt="CC4 Deployed Network A Diagram" width="500">
  <figcaption>Figure 2 - Deployed Network A (그림 2 - 배치 네트워크 A)</figcaption>
</figure>

Agent actions now have a specified time duration, which varies depending on the action chosen. Agents must wait until their action is completed before they are prompted to launch another action. Once an agent has chosen it cannot be cancelled.

> 에이전트의 행동(Action)에는 이제 정해진 소요 시간이 있으며, 이는 선택한 행동에 따라 달라집니다. 에이전트는 자신의 행동이 완료될 때까지 기다린 뒤에야 다음 행동을 실행하라는 요청을 받습니다. 일단 에이전트가 행동을 선택하면 취소할 수 없습니다.

During the course of an episode, the mission shall progress linearly through three different phases Phase 1, Phase 2A and Phase 2B. During Phase 1 all missions operating in each zone have the same low priority level. During Phase 2A only missions operating in zones within Deployed Network A have the same high priority level, while all other missions have the same low priority level. During Phase 2B only missions operating in Deployed Network B have the same high priority level, while all other missions have the same low priority level.

> 하나의 에피소드(episode) 동안, 임무는 Phase 1, Phase 2A, Phase 2B의 세 단계를 순차적으로 진행합니다. Phase 1에서는 각 영역에서 수행되는 모든 임무가 동일하게 낮은 우선순위를 갖습니다. Phase 2A에서는 배치 네트워크 A(Deployed Network A) 내 영역에서 수행되는 임무만 동일하게 높은 우선순위를 가지며, 그 외 모든 임무는 동일하게 낮은 우선순위를 갖습니다. Phase 2B에서는 배치 네트워크 B(Deployed Network B)에서 수행되는 임무만 동일하게 높은 우선순위를 가지며, 그 외 모든 임무는 동일하게 낮은 우선순위를 갖습니다.

## Green Agents (Green 에이전트)

Users are represented by green agents, which are present on every host. Green agents randomly do local work or attempt to reach out to external services, either in their local or a remote zone. The service and zone a green agent chooses will be determined randomly, but are restricted to valid connections for the current mission phase as governed by the communication policy tables below. 

> 사용자는 Green 에이전트(정상 사용자)로 표현되며, 모든 호스트에 존재합니다. Green 에이전트는 무작위로 로컬 작업(local work)을 수행하거나, 자신의 로컬 영역 또는 원격 영역의 외부 서비스에 접속을 시도합니다. Green 에이전트가 선택하는 서비스와 영역은 무작위로 정해지지만, 아래 통신 정책표(communication policy table)가 규정하는 현재 임무 단계의 유효한 연결로만 제한됩니다.

Rewards are tied to these green agent actions. The blue team receives penalties when a green agent is unable to work, either because it cannot make a valid connection to service, or its host is unavailable (for example if it is currently being restored by a blue agent). Green agents in mission-critical zones generate higher penalties when their mission is active. The full list and values of penalties are shown in Table 4.

> 보상(Reward)은 이러한 Green 에이전트의 행동과 연결되어 있습니다. Green 에이전트가 작업을 수행하지 못할 때 — 서비스로의 유효한 연결을 맺지 못하거나, 호스트를 사용할 수 없을 때(예: Blue 에이전트가 그 호스트를 복원[Restore] 중인 경우) — Blue 팀은 페널티(penalty, 감점)를 받습니다. 임무상 중요한 영역의 Green 에이전트는 해당 임무가 활성화되어 있을 때 더 큰 페널티를 발생시킵니다. 페널티의 전체 목록과 값은 Table 4에 나와 있습니다.

Green agents occasionally generate false alerts while going about their work by exhibiting behavior similar to a red agent, such as transferring data between hosts. They also sometimes introduce red agents into the network via succumbing to phishing attacks, installing unapproved software, and general poor security hygiene.

> Green 에이전트는 작업을 하다가 이따금 호스트 간 데이터 전송처럼 Red 에이전트와 유사한 행동을 보여 거짓 경보(false alert)를 발생시킵니다. 또한 피싱 공격에 당하거나, 승인되지 않은 소프트웨어를 설치하거나, 전반적으로 보안 위생(security hygiene)이 나쁜 탓에 가끔 Red 에이전트를 네트워크에 끌어들이기도 합니다.

## Deception (기만 전술)

Both blue and red agents may employ deception to further their goals. Blue agents can stand up decoy services in any host or server. Decoy services resemble normal ones, but cannot replace or be instantiated along with existing services (they can use the Discover Network Services action to determine which services are already running on a given host). When a red agent attempts to compromise a decoy service, blue will be alerted and red’s exploit will automatically fail. Red agents can use the `DiscoverDeception` action to determine if they are interacting with decoy services, and their `Withdraw` action to remove their presence.

> Blue 에이전트와 Red 에이전트 모두 자신의 목표를 위해 기만(deception) 전술을 쓸 수 있습니다. Blue 에이전트는 어떤 호스트나 서버에든 Decoy(디코이, 미끼) 서비스를 세울 수 있습니다. Decoy 서비스는 정상 서비스처럼 보이지만, 기존 서비스를 대체하거나 그와 함께 동시에 띄울 수는 없습니다(원격 시스템에 어떤 서비스가 이미 실행 중인지는 Discover Network Services[네트워크 서비스 탐색] 행동으로 확인할 수 있습니다). Red 에이전트가 Decoy 서비스를 침해하려 시도하면 Blue에게 경보가 가고 Red의 익스플로잇(exploit, 공격)은 자동으로 실패합니다. Red 에이전트는 `DiscoverDeception` 행동으로 자신이 Decoy 서비스와 상호작용하고 있는지 판별할 수 있고, `Withdraw`(철수) 행동으로 자신의 존재를 지울 수 있습니다.

For their part, red agents are more likely to generate extra alerts for blue defenders using the `Aggressive Service Discovery` action on a selected host. This action is faster than the Service Discovery action but has a higher probability of generating an alert, so it may also be used simply to trade off speed over stealth. In addition, red agents with elevated privileges can use the Degrade action to cause green agent actions on the target host to fail much more frequently.

> Red 에이전트 측에서는, 선택한 호스트에 `Aggressive Service Discovery`(공격적 서비스 탐색) 행동을 쓰면 Blue 방어자에게 추가 경보를 더 많이 발생시킬 가능성이 높습니다. 이 행동은 Service Discovery(서비스 탐색) 행동보다 빠르지만 경보를 발생시킬 확률이 더 높아, 은밀함(stealth)을 포기하고 속도를 택하는 절충 수단으로 쓸 수도 있습니다. 또한 권한이 상승된(elevated privileges) Red 에이전트는 Degrade(서비스 성능 저하) 행동을 사용해 대상 호스트의 Green 에이전트 행동이 훨씬 더 자주 실패하도록 만들 수 있습니다.

## Network Connectivity and Communication Policy (네트워크 연결성과 통신 정책)

Each mission phase has an associated communication policy governing how zones are intended to connect to one another. When the mission phase changes the intended policy is communicated automatically. Only connections associated with the given mission are changed (for example, when mission 2A is activated, only connections with Restricted Zone A and Operational Zone A are affected). The policy associated with each mission phase is shown in Tables 1-3. The intended policy and actual firewall state is also communicated to blue agents in their observation vector. Blue agents can open and close firewalls between their zone and other networks, for example to prevent infections from red agents, but may incur penalties if their changes prevent green agents from accomplishing their own goals. Some blue agents may communicate with each other regardless of firewall policy via 8-bit messages. 

> 각 임무 단계에는 영역들이 서로 어떻게 연결되어야 하는지를 규정하는 통신 정책(communication policy)이 연결되어 있습니다. 임무 단계가 바뀌면 의도된 정책이 자동으로 전달됩니다. 해당 임무와 관련된 연결만 변경됩니다(예: 임무 2A가 활성화되면 Restricted Zone A와 Operational Zone A 관련 연결만 영향을 받습니다). 각 임무 단계에 연결된 정책은 Table 1-3에 나와 있습니다. 의도된 정책과 실제 방화벽(firewall) 상태도 Blue 에이전트에게 관찰값 벡터(observation vector)로 전달됩니다. Blue 에이전트는 Red 에이전트의 감염을 막기 위해 자신의 영역과 다른 네트워크 사이의 방화벽을 열고 닫을 수 있지만, 그 변경이 Green 에이전트의 목표 달성을 막으면 페널티를 받을 수 있습니다. 일부 Blue 에이전트는 방화벽 정책과 무관하게 8비트 메시지(8-bit message)로 서로 통신할 수 있습니다.

Some defending agents have the capability to communicate 8-bit messages with each other. See Table 1 for the complete (initial) network communication security policy for the mission pre-planning phase.

> 일부 방어 에이전트는 서로 8비트 메시지를 주고받는 능력을 갖추고 있습니다. 임무 사전 계획 단계(mission pre-planning phase)의 전체 (초기) 네트워크 통신 보안 정책은 Table 1을 참고하세요.

### Phase 1: Mission Pre-planning (General Operations and Maintenance) (Phase 1: 임무 사전 계획 — 일반 운영 및 유지보수)

#### Table 1: Initial Network Communication Security Policy --- Mission-Pre-planning Phase (Table 1: 초기 네트워크 통신 보안 정책 — 임무 사전 계획 단계)

|        **Zone**        | **HQ Network** | **Contractor Network** | **Restricted Zone A** | **Operational Zone A** | **Restricted Zone B** | **Operational Zone B** | **Internet** |
|:----------------------:|:--------------:|:----------------------:|:---------------------:|:----------------------:|:---------------------:|:----------------------:|:------------:|
|     **HQ Network**     |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Contractor Network** |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Restricted Zone A**  |       1        |           1            |           1           |           1            |           1           |           0            |      1       |
| **Operational Zone A** |       0        |           0            |           1           |           1            |           0           |           0            |      0       |
| **Restricted Zone B**  |       1        |           1            |           1           |           0            |           1           |           1            |      1       |
| **Operational Zone B** |       0        |           0            |           0           |           0            |           1           |           1            |      0       |
|      **Internet**      |       1        |           1            |           1           |           0            |           1           |           0            |      1       |

> **표 읽는 법**: 이 표는 영역(zone) 간 통신이 허용되는지를 나타내는 통신 정책표입니다. 행은 출발 영역, 열은 도착 영역이며, 값 **1**은 두 영역 사이 연결이 **허용(should be open)**, 값 **0**은 연결이 **차단되어야 함(should be blocked)**을 뜻합니다. 열 머리글의 영역명은 각각 HQ Network(본부 네트워크), Contractor Network(협력업체 네트워크), Restricted Zone A/B(제한 영역 A/B), Operational Zone A/B(운영 영역 A/B), Internet(인터넷)입니다. 이 Table 1은 Phase 1(임무 사전 계획 단계)의 초기 정책입니다.

<figure markdown>
  ![CAGE Phase 1 Connectivity Diagram](/documentation/docs/assets/CAGE-Phase-1-Connectivity-Diagram.png)
  <figcaption>Figure 3 - Phase 1 Connectivity Diagram (그림 3 - Phase 1 연결 구성도)</figcaption>
</figure>

### Phase 2a: Mission A Active (Phase 2a: 임무 A 활성)

When mission A is active, Operational Zone A disconnects from all other networks. Restricted zone A connects only to HQ.

> 임무 A가 활성화되면 Operational Zone A(운영 영역 A)는 다른 모든 네트워크와의 연결을 끊습니다. Restricted Zone A(제한 영역 A)는 본부(HQ)에만 연결됩니다.

#### Table 2: Initial Network Communication Security Policy --- Active Mission A Phase (Table 2: 초기 네트워크 통신 보안 정책 — 임무 A 활성 단계)

|        **Zone**        | **HQ Network** | **Contractor Network** | **Restricted Zone A** | **Operational Zone A** | **Restricted Zone B** | **Operational Zone B** | **Internet** |
|:----------------------:|:--------------:|:----------------------:|:---------------------:|:----------------------:|:---------------------:|:----------------------:|:------------:|
|     **HQ Network**     |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Contractor Network** |       1        |           1            |           0           |           0            |           1           |           0            |      1       |
| **Restricted Zone A**  |       1        |           0            |           1           |           0            |           0           |           0            |      0       |
| **Operational Zone A** |       0        |           0            |           0           |           1            |           0           |           0            |      0       |
| **Restricted Zone B**  |       1        |           1            |           0           |           0            |           1           |           1            |      1       |
| **Operational Zone B** |       0        |           0            |           0           |           0            |           1           |           1            |      0       |
|      **Internet**      |       1        |           1            |           0           |           0            |           1           |           0            |      1       |

> **표 읽는 법**: Table 1과 같은 형식의 통신 정책표입니다(행=출발 영역, 열=도착 영역, **1**=연결 허용, **0**=연결 차단). 이 Table 2는 Phase 2a(임무 A 활성 단계)의 초기 정책으로, Operational Zone A가 다른 모든 영역과 끊기고 Restricted Zone A가 HQ에만 연결되는 변화가 표의 0/1 값에 반영되어 있습니다.

<figure markdown>
  ![CAGE Phase 2a Connectivity Diagram](/documentation/docs/assets/CAGE-Phase-2a-Connectivity-Diagram.png)
  <figcaption>Figure 4 - Phase 2a Connectivity Diagram (그림 4 - Phase 2a 연결 구성도)</figcaption>
</figure>

### Phase 2b: Mission B Active (Phase 2b: 임무 B 활성)

When mission B is active, Operational Zone B disconnects from all other networks. Restricted zone B connects only to HQ.

> 임무 B가 활성화되면 Operational Zone B(운영 영역 B)는 다른 모든 네트워크와의 연결을 끊습니다. Restricted Zone B(제한 영역 B)는 본부(HQ)에만 연결됩니다.

#### Table 3: Initial Network Communication Security Policy --- Active Mission B Phase (Table 3: 초기 네트워크 통신 보안 정책 — 임무 B 활성 단계)

|        **Zone**        | **HQ Network** | **Contractor Network** | **Restricted Zone A** | **Operational Zone A** | **Restricted Zone B** | **Operational Zone B** | **Internet** |
|:----------------------:|:--------------:|:----------------------:|:---------------------:|:----------------------:|:---------------------:|:----------------------:|:------------:|
|     **HQ Network**     |       1        |           1            |           1           |           0            |           1           |           0            |      1       |
| **Contractor Network** |       1        |           1            |           1           |           0            |           0           |           0            |      1       |
| **Restricted Zone A**  |       1        |           1            |           1           |           1            |           0           |           0            |      1       |
| **Operational Zone A** |       0        |           0            |           1           |           1            |           0           |           0            |      0       |
| **Restricted Zone B**  |       1        |           0            |           0           |           0            |           1           |           0            |      0       |
| **Operational Zone B** |       0        |           0            |           0           |           0            |           0           |           1            |      0       |
|      **Internet**      |       1        |           1            |           1           |           0            |           0           |           0            |      1       |

> **표 읽는 법**: Table 1과 같은 형식의 통신 정책표입니다(행=출발 영역, 열=도착 영역, **1**=연결 허용, **0**=연결 차단). 이 Table 3은 Phase 2b(임무 B 활성 단계)의 초기 정책으로, Operational Zone B가 다른 모든 영역과 끊기고 Restricted Zone B가 HQ에만 연결되는 변화가 표의 0/1 값에 반영되어 있습니다.

<figure markdown>
  ![CAGE Phase 2b Connectivity Diagram](/documentation/docs/assets/CAGE-Phase-2b-Connectivity-Diagram.png)
  <figcaption>Figure 5 - Phase 2b Connectivity Diagram (그림 5 - Phase 2b 연결 구성도)</figcaption>
</figure>

## Rewards (보상)

Blue agents start with 0 points and are assigned penalties when green agents are unable to perform their work, when they access a compromised service, and when red chooses the `Impact` action. Penalties change during active missions to reflect the changing criticality of hosts on current operations. All rewards are shown in Tables 4A, 4B, and 4C.

> Blue 에이전트는 0점에서 시작하며, Green 에이전트가 작업을 수행하지 못할 때, 침해된 서비스에 접근할 때, 그리고 Red가 `Impact`(타격) 행동을 선택할 때 페널티(감점)를 받습니다. 페널티 값은 현재 작전에서 호스트의 중요도가 달라지는 것을 반영하기 위해 임무 활성 중에 변합니다. 모든 보상 값은 Table 4A, 4B, 4C에 나와 있습니다.

#### Table 4A: Rewards for green action failures and compromise in Phase 1 O&M (Table 4A: Phase 1 운영·유지보수[O&M] 단계의 Green 행동 실패 및 침해 시 보상)

|        **Zone**        | **Local Work Fails** | **Access Service Fails** | **Red impact/access** |
|:----------------------:|:--------------------:|:------------------------:|:---------------------:|
|     **HQ Network**     |          -1          |            -1            |          -3           |
| **Contractor Network** |          0           |            -5            |          -5           |
| **Restricted Zone A**  |          -1          |            -3            |          -1           |
| **Operational Zone A** |          -1          |            -1            |          -1           |
| **Restricted Zone B**  |          -1          |            -3            |          -1           |
| **Operational Zone B** |          -1          |            -1            |          -1           |
|      **Internet**      |          0           |            0             |          0            |

> **표 읽는 법**: 이 표는 각 영역(행)에서 발생하는 사건별 페널티(감점) 값을 보여줍니다. 모든 값은 0 또는 음수이며, 절댓값이 클수록 더 큰 페널티를 뜻합니다. 열의 의미는 다음과 같습니다.
> - **Local Work Fails** (로컬 작업 실패): Green 에이전트의 로컬 작업이 실패할 때 받는 페널티
> - **Access Service Fails** (서비스 접근 실패): Green 에이전트가 서비스에 유효하게 연결하지 못할 때 받는 페널티
> - **Red impact/access** (Red 타격/접근): Red가 해당 영역에 타격을 가하거나 접근에 성공할 때 받는 페널티
>
> 이 Table 4A는 Phase 1(운영·유지보수[O&M] 단계)의 보상표입니다.

#### Table 4B: Rewards for green action failures and compromise in Phase 2a - Mission A (Table 4B: Phase 2a 임무 A 단계의 Green 행동 실패 및 침해 시 보상)

|        **Zone**        | **Local Work Fails** | **Access Service Fails** | Red impact/access |
|:----------------------:|:--------------------:|:------------------------:|:-----------------:|
|     **HQ Network**     |          -1          |            -1            |        -3         |
| **Contractor Network** |          0           |            0             |         0         |
| **Restricted Zone A**  |          -2          |            -1            |        -3         |
| **Operational Zone A** |         -10          |            0             |        -10        |
| **Restricted Zone B**  |          -1          |            -1            |        -1         |
| **Operational Zone B** |          -1          |            -1            |        -1         |
|      **Internet**      |          0           |            0             |         0         |

> **표 읽는 법**: Table 4A와 같은 형식의 페널티표입니다(열: Local Work Fails=로컬 작업 실패, Access Service Fails=서비스 접근 실패, Red impact/access=Red 타격/접근). 이 Table 4B는 Phase 2a(임무 A 활성 단계)의 보상표로, 임무 A가 활성화되어 중요해진 Operational Zone A의 페널티(예: 로컬 작업 실패 -10, Red 타격/접근 -10)가 다른 단계보다 크게 설정되어 있습니다.

#### Table 4C: Rewards for green action failures and compromise in Phase 2b - Mission B (Table 4C: Phase 2b 임무 B 단계의 Green 행동 실패 및 침해 시 보상)

|        **Zone**        | **Local Work Fails** | **Access Service Fails** | **Red impact/access** |
|:----------------------:|:--------------------:|:------------------------:|:---------------------:|
|     **HQ Network**     |          -1          |            -1            |          -3           |
| **Contractor Network** |          0           |            0             |           0           |
| **Restricted Zone A**  |          -1          |            -3            |          -3           |
| **Operational Zone A** |          -1          |            -1            |          -1           |
| **Restricted Zone B**  |          -2          |            -1            |          -3           |
| **Operational Zone B** |         -10          |            0             |          -10          |
|      **Internet**      |          0           |            0             |           0           |

> **표 읽는 법**: Table 4A와 같은 형식의 페널티표입니다(열: Local Work Fails=로컬 작업 실패, Access Service Fails=서비스 접근 실패, Red impact/access=Red 타격/접근). 이 Table 4C는 Phase 2b(임무 B 활성 단계)의 보상표로, 이번에는 임무 B가 활성화되어 중요해진 Operational Zone B의 페널티(예: 로컬 작업 실패 -10, Red 타격/접근 -10)가 크게 설정되어 있습니다.

## How to use CybORG (CybORG 사용 방법)

We use the Cyber Operations Research Gym (CybORG) to simulate the cyber environment for each CAGE challenge.

> 각 CAGE 챌린지의 사이버 환경을 시뮬레이션하기 위해 **CybORG**(Cyber Operations Research Gym)를 사용합니다.

Please see [the Installation Instruction guide](https://cage-challenge.github.io/cage-challenge-4/pages/tutorials/01_Getting_Started/1_Introduction/) for further instructions on how to install and run the environment, and see [here](https://cage-challenge.github.io/cage-challenge-4/pages/how-to-guides/) for additional tutorials.

> 환경을 설치하고 실행하는 방법에 대한 자세한 안내는 [설치 안내 가이드](https://cage-challenge.github.io/cage-challenge-4/pages/tutorials/01_Getting_Started/1_Introduction/)를 참고하시고, 추가 튜토리얼은 [여기](https://cage-challenge.github.io/cage-challenge-4/pages/how-to-guides/)를 참고하세요.

## How to submit responses (제출 방법)

Submissions are made to the [Codalabs webpage](https://codalab.lisn.upsaclay.fr/competitions/17672) which will automatically evaluate your agent and rank them on the leaderboard. Users will be required to make a Codalabs account in order to submit their agents. Users will then need to go to the 'Participate' tab, click on the 'Submit' section, and then upload their submission.zip file. After waiting some time (depends on how fast your agent is) your result will be automatically uploaded to the leaderboard.

> 제출은 [Codalabs 웹페이지](https://codalab.lisn.upsaclay.fr/competitions/17672)에서 이루어지며, 여러분의 에이전트를 자동으로 평가하고 리더보드(leaderboard)에 순위를 매깁니다. 에이전트를 제출하려면 Codalabs 계정을 만들어야 합니다. 그런 다음 'Participate'(참가) 탭으로 가서 'Submit'(제출) 섹션을 클릭하고 submission.zip 파일을 업로드하면 됩니다. 잠시 기다리면(에이전트의 속도에 따라 다름) 결과가 자동으로 리더보드에 반영됩니다.

For detailed instructions regarding how to evaluate and submit your agents please refer to the README.md located in the Cyborg/Evaluation folder.

> 에이전트를 평가하고 제출하는 방법에 대한 자세한 안내는 Cyborg/Evaluation 폴더에 있는 README.md 파일을 참고하세요.

We welcome multiple submissions per team. If you resubmit same agent twice, please remove one of them from the leaderboard. If you retrain the same agent architecture, please add 'v2', 'v3', etc... to the agent submission file. If it is an entirely new approach, please change the name of the agent. 

> 팀당 여러 번의 제출을 환영합니다. 같은 에이전트를 두 번 다시 제출했다면 그중 하나는 리더보드에서 제거해 주세요. 같은 에이전트 구조를 다시 학습시킨 경우에는 에이전트 제출 파일명에 'v2', 'v3' 등을 붙여 주세요. 완전히 새로운 접근 방식이라면 에이전트의 이름을 바꿔 주세요.

We are also imposing an execution time limit on all submissions. Submissions should complete 100 episodes, of length 500, within 3 hours when evaluated on our Amazon EC2 C4.large instance. Any submissions will go beyond this time will be automatically cancelled.

> 모든 제출물에는 실행 시간 제한도 적용됩니다. 제출물은 저희의 Amazon EC2 C4.large 인스턴스에서 평가할 때, 길이 500인 에피소드 100개를 3시간 안에 완료해야 합니다. 이 시간을 초과하는 제출물은 자동으로 취소됩니다.

As part of your submission, we request that you share a description of the methods/techniques used in developing your agents to [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com). We will use this information as part of our in-depth analysis and comparison of the various techniques submitted to the challenge. In hosting the CAGE challenges, one of our main goals is to understand the techniques that lead to effective autonomous cyber defensive agents, as well as those that are not as effective. We are planning on publishing the analysis and taxonomy of the different approaches that create autonomous cyber defensive agents. To that end, we encourage you to also share details on any unsuccessful approaches taken. Please also feel free to share any interesting discoveries and thoughts regarding future work to help us shape the future of the CAGE Challenges.

> 제출의 일환으로, 에이전트 개발에 사용한 방법·기법에 대한 설명을 [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com)으로 공유해 주시길 요청드립니다. 저희는 이 정보를 챌린지에 제출된 다양한 기법을 심층 분석하고 비교하는 데 활용합니다. CAGE 챌린지를 운영하는 주요 목표 중 하나는 효과적인 자율 사이버 방어 에이전트로 이어지는 기법뿐 아니라 그다지 효과적이지 않은 기법까지 이해하는 것입니다. 저희는 자율 사이버 방어 에이전트를 만드는 여러 접근 방식에 대한 분석과 분류 체계(taxonomy)를 발표할 계획입니다. 그러므로 시도했으나 성공하지 못한 접근 방식에 대한 내용도 함께 공유해 주시길 권장합니다. 또한 흥미로운 발견이나 향후 연구에 대한 생각이 있다면 자유롭게 공유하여 CAGE 챌린지의 미래를 함께 만들어 가는 데 도움을 주세요.

Any queries regarding the challenge can be submitted via email to [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com).

> 챌린지에 관한 문의는 [cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com)으로 이메일을 보내 주시면 됩니다.

We also invite teams to submit full papers on their work on this CAGE challenge! 

> 또한 이 CAGE 챌린지에 대한 작업을 정식 논문(full paper)으로 제출하는 것도 환영합니다!

## Evaluation (평가)
A leaderboard for submissions will be maintained on [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672) throughout the challenge's time frame.

> 제출물에 대한 리더보드는 챌린지 기간 내내 [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672)에서 유지됩니다.

The `evaluation.py` file is designed to provide a standardised evaluation for an agent, which will be used in the Codalabs validation process. Each blue agent will be evaluated against the `FiniteStateRedAgent` in 100 randomised episodes, where each episode is 500 timesteps long.

> `evaluation.py` 파일은 에이전트에 대한 표준화된 평가를 제공하도록 설계되었으며, Codalabs 검증 과정에서 사용됩니다. 각 Blue 에이전트는 길이가 500 타임스텝(timestep)인 무작위 에피소드 100개에 걸쳐 `FiniteStateRedAgent`를 상대로 평가됩니다.

If running locally, information about the agent's actions, observations, mean reward, and standard deviation will be outputted as text files after this file completes its run. Details about how do this is in the README.md file within the Evaluation folder. If running on Codalabs, only the mean reward will be extracted and used to update the leaderboard. 

> 로컬에서 실행하는 경우, 이 파일의 실행이 끝나면 에이전트의 행동(Action), 관찰값(Observation), 평균 보상(mean reward), 표준편차(standard deviation) 정보가 텍스트 파일로 출력됩니다. 이를 수행하는 방법에 대한 자세한 내용은 Evaluation 폴더 안의 README.md 파일에 있습니다. Codalabs에서 실행하는 경우에는 평균 보상만 추출되어 리더보드 갱신에 사용됩니다.

**Disclaimer**: We reserve the right to remove any agent from the leaderboard. We will enact this right if we believe participants did not act within the spirit of the challenge by exploiting any mechanism to provide them with an unfair advantage over other participants. Please reach out to our email ([cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com)) if you're unsure about any changes you have implemented and we will make a judgement call on a case-by-case basis

> **면책 조항(Disclaimer)**: 저희는 어떤 에이전트든 리더보드에서 제거할 권리를 보유합니다. 참가자가 다른 참가자보다 부당한 우위를 점하기 위해 어떤 메커니즘을 악용하는 등 챌린지의 취지에 어긋나게 행동했다고 판단되면 이 권리를 행사합니다. 여러분이 구현한 변경 사항에 대해 확신이 서지 않는다면 저희 이메일([cage.aco.challenge@gmail.com](mailto:cage.aco.challenge@gmail.com))로 연락해 주세요. 사안별로 판단해 드리겠습니다.

## Important dates (주요 일정)

- **20 Feb 2024:** Challenge 4 released. Development phase begins. During the development phase, we will be debugging any unexpectant issues that may be found by the participants. Please ensure that you watch the repo so that you're notified if any changes are required.

- **29 Mar 2024 23:59 (UTC):** Development phase ends. Competition phase begins. During the comptetition phase, unless it is absolutely necessary, we will not be changing the code base, as this allows participants enough time to train their agents on a constant environment.

- **10 May 2024 23:59 (UTC):** Competition phase ends. Final results announced on [Codalabs](https://codalab.lisn.upsaclay.fr/competitions/17672) leaderboard.

> - **2024년 2월 20일:** Challenge 4 공개. 개발 단계(development phase) 시작. 개발 단계 동안 저희는 참가자가 발견하는 예기치 못한 문제를 디버깅합니다. 변경이 필요할 때 알림을 받을 수 있도록 레포를 watch(구독) 설정해 두시기 바랍니다.
> - **2024년 3월 29일 23:59 (UTC):** 개발 단계 종료. 경쟁 단계(competition phase) 시작. 경쟁 단계 동안에는 꼭 필요한 경우가 아니면 코드베이스를 변경하지 않습니다. 이를 통해 참가자가 일정한 환경에서 에이전트를 학습시킬 시간을 충분히 확보할 수 있습니다.
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

> 아래는 위 표를 같은 구조로 옮긴 한국어 표입니다. 행동 이름(`GreenAccessService` 등)과 코드 식별자(`fp_detection_rate` 등), 파라미터(parameter) 이름은 코드에서 사용하는 값이므로 영어 그대로 둡니다.
> 열 머리글의 뜻: **Action name**(행동 이름), **Team**(소속 팀), **Description of action**(행동 설명), **Time (ticks)**(소요 시간, 틱 단위), **Local/remote**(로컬/원격), **Chance of being flagged as malicious**(악성으로 탐지될 확률), **Chance of failure**(실패 확률), **Parameters**(파라미터), **Output**(출력 결과).

|**Action name**|**Team**|<div style = "width:200px">**행동 설명**</div>|**소요 시간 (틱)**|**로컬/원격**|**악성으로 탐지될 확률**|**실패 확률**|**파라미터**| **출력 결과** |
|:-------------:|:------:|:-----------------------:|:--------------:|:--------------:|:--------------------------------------:|:-------------------:|:------------:|:----------:|
|GreenAccessService|Green|로컬 영역 또는 다른 영역의 서버와 통신합니다. Green은 임무 단계에 따른 IP 주소 목록에서 무작위로 하나를 선택합니다. 서버에 도달하지 못하면 Blue가 페널티를 받습니다. 이 행동은 Monitor가 감지하는 거짓 네트워크 연결 경보를 낮은 확률로 발생시킵니다.|1|Remote(원격)|낮음 (1%) (`fp_detection_rate`, EnterpriseGreenAgent를 통해 설정)|없음|agent, session_id, src_ip, allowed_subnets, fp_detection_rate|성공/실패|
|GreenLocalWork|Green|통신 없이 로컬 호스트에서 작업합니다. Green 호스트는 서비스에 접근하거나 휴면(sleep) 상태가 아닐 때 이 행동을 합니다. 악성으로 탐지될 확률이 있는 것에 더해, 이 행동의 결과로 Red가 호스트에 발판을 얻을(예: 피싱 이메일의 결과) 작은 확률도 있습니다.|1|Local(로컬)|낮음 (1%) (`fp_detection_rate`, EnterpriseGreenAgent를 통해 설정)|없음|agent, session_id, ip_address,  fp_detection_rate, phishing_error_rate|성공/실패|
|Monitor|Blue|네트워크상에서 악성으로 표시된 활동에 대한 정보를 수집합니다. OpenC2 명세의 action ID 1: Scan에 해당합니다. 이 행동은 기본 행동(default action)으로 자동 수행됩니다.|1|-|없음|없음|session, agent|성공/실패. 악성으로 식별된 네트워크 연결과 관련 프로세스.|
|Analyse|Blue|특정 호스트에서 악성코드(malware)와 관련된 추가 정보를 수집하여, Blue가 시스템에 Red가 존재하는지 더 잘 식별할 수 있게 합니다. OpenC2 명세의 action ID 30: Investigate에 해당합니다.|2|-|없음|없음|session, agent, hostname|성공/실패. 최근 경보와 관련된 파일 정보.|
|DeployDecoy|Blue|지정한 호스트에 Decoy(디코이) 서비스(종류는 무작위 지정)를 설치합니다. Green 에이전트는 이 서비스에 접근하지 않으므로, 접근이 있다면 명백한 Red 활동의 지표가 됩니다. Decoy 서비스는 정상 서비스를 대체할 수 없습니다. Red 에이전트가 Decoy 서비스를 발견하거나 익스플로잇하면 Blue 에이전트는 해당 호스트나 서비스와 관련된 경보를 받습니다. Red 에이전트는 Decoy 서비스를 성공적으로 익스플로잇할 수 없습니다.|2|-|없음|없음|session, agent, hostname|정상 서비스가 아직 실행 중이지 않으면 성공. 대상에 이미 정상 서비스가 실행 중이면 실패. Red 에이전트가 새 서비스에 접근하면 Decoy도 경보를 발생시킵니다.|
|Remove|Blue|악성 프로세스·파일·서비스를 제거하여 호스트에서 Red를 제거하려 시도합니다. 이 행동은 Monitor 행동이 악성으로 식별한 모든 프로세스를 중지하려 시도합니다. OpenC2 명세의 action ID 10: Stop에 해당합니다.|3|-|없음|없음|session, agent, hostname|성공/실패|
|Restore|Blue|시스템을 알려진 정상 상태(known good state)로 복원합니다. 이는 시스템 가용성에 상당한 영향을 줍니다. OpenC2 명세의 action ID 23: Restore에 해당합니다.|5|-|없음|없음|session, agent, hostname|성공/실패|
|BlockTraffic|Blue|지정한 영역으로 오가는 트래픽을 차단합니다. Green 에이전트가 그 영역으로 통신하려 한다면 페널티가 발생합니다.|1|Local(로컬)|없음|없음|session, agent, from_subnet, to_subnet|성공/실패|
|AllowTraffic|Blue|지정한 영역으로 오가는 트래픽을 허용합니다.|1|Local(로컬)|없음|없음|session, agent, from_subnet, to_subnet|성공/실패|
|DiscoverRemoteSystems|Red|ATT&CK 기법 T1018 원격 시스템 탐색. ping 같은 도구를 활용한 능동 스캔으로 네트워크에서 새로운 호스트/IP 주소를 탐색합니다.|1|Remote(원격)|없음|없음|session, agent, subnet|성공/실패. 선택한 서브넷에서 ping에 응답하는 호스트의 IP 주소.|
|AggressiveServiceDiscovery|Red|ATT&CK 기법 T1046 네트워크 서비스 스캔. 선택한 호스트와 연결을 맺어 응답하는 서비스를 탐색합니다.|1|Remote(원격)|높음 (75%)|없음|session, agent, ip_address|성공/실패. 포트와 서비스 정보.|
|StealthServiceDiscovery|Red|AggressiveServiceDiscovery와 같지만 더 느리고 조용합니다(즉, 경보를 일으킬 확률이 더 낮습니다).|3|Remote(원격)| 중간 (25%)|없음|session, agent, ip_address|성공/실패. 포트와 서비스 정보.|
|Exploit Network Services|Red|ATT&CK 기법 T1210 원격 서비스 익스플로잇. 원격 시스템의 지정된 서비스를 익스플로잇하려 시도합니다.|4|Remote(원격)|없음|중간 (가중 익스플로잇 선택에 따라 실패 여부 결정)|session, agent, ip_address|성공/실패. 성공 시 호스트에 대한 초기 정찰 정보.|
|PrivilegeEscalate|Red|ATT&CK 전술 TA0004 권한 상승. 호스트에서 에이전트의 권한을 상승시킵니다.|2|Local(로컬)|없음|없음|session, agent, hostname|성공/실패. 호스트 접근 권한이 높아져 이제 이용 가능한 내부 정보.|
|Impact|Red|ATT&CK 기법 T1489 서비스 중지. 네트워크의 성능을 방해하며, 운영 서비스를 무력화하려는 Red의 목표를 달성합니다.|2|Local(로컬)|없음|없음|session, agent, hostname|성공/실패|
|DegradeServices|Red|Red가 호스트에 root 권한을 가지고 있으면, Green 에이전트의 사용자 경험을 저하시킬 수 있습니다(예: 키 입력을 무작위로 누락시키거나 다른 방해를 일으킴). Degrade의 영향을 받으면 GreenLocalWork 행동의 실패율이 높아집니다(그 결과 Blue는 추가 페널티를 받습니다).|2|Remote(원격)|없음|없음|session, agent, hostname|성공/실패|
|DiscoverDeception|Red|호스트를 탐침(probe)하여 Decoy 서비스를 실행 중인지 판별합니다.|2|Remote(원격)|없음|중간 (거짓 음성 50% 확률, 거짓 양성 10% 확률)|session, agent, ip_address|성공/실패. 정상으로 판단 또는 Decoy로 판단.|
|Withdraw|Red|대상 호스트에서 Red의 존재를 제거합니다.|1|Remote(원격)|없음|없음|session, agent, hostname, ip_address|성공|
|Sleep|All|이번 틱에 아무 행동도 하지 않습니다.|1|Local(로컬)|없음|없음|없음|없음|

## Appendix B – Agent observation (부록 B – 에이전트 관찰값)

The BlueEnterpriseWrapper performs utility functions that support MARL algorithms by conforming to the PettingZoo Environment. This wrapper alters the observation to enable the use of Deep Reinforcement Learning techniques. This appendix describes the altered observation.

> `BlueEnterpriseWrapper`는 PettingZoo 환경(PettingZoo Environment) 규격을 따름으로써 MARL(다중 에이전트 강화학습) 알고리즘을 지원하는 유틸리티 기능을 수행합니다. 이 래퍼(Wrapper)는 심층 강화학습(Deep Reinforcement Learning) 기법을 사용할 수 있도록 관찰값(Observation)을 변형합니다. 이 부록은 변형된 관찰값을 설명합니다.

The table below indicates what data is presented at each index of the observation of an agent. We use the symbol H to denote the maximum number of hosts in the local subnet, which is equal to 16 (10 user hosts and 6 servers). These hosts are ordered from server hosts 0-6, followed by user hosts 0-10. If a host is not present for a given episode, its corresponding slot in the vector will be zero for the duration of the episode. All ranges in the following tables are inclusive, so 1…H includes both 1 and H.

> 아래 표는 에이전트 관찰값의 각 인덱스(index)에 어떤 데이터가 들어가는지를 나타냅니다. 기호 H는 로컬 서브넷의 최대 호스트 수를 가리키며, 그 값은 16입니다(사용자 호스트 10개 + 서버 6개). 호스트는 서버 호스트 0-6, 이어서 사용자 호스트 0-10 순으로 정렬됩니다. 특정 에피소드에 어떤 호스트가 존재하지 않으면, 벡터에서 그에 해당하는 슬롯(slot)은 그 에피소드 동안 0이 됩니다. 다음 표의 모든 범위는 양 끝을 포함(inclusive)하므로, 1…H는 1과 H를 모두 포함합니다.

Similarly, we use the symbol S to denote the number of subnets, which is always equal to 9 (2 Operational Zones, 2 Restricted Zones, Internet, Contractor Network, 3 subnets in the HQ zone). To ensure consistency across runs, all subnets are sorted alphabetically.

> 마찬가지로 기호 S는 서브넷의 수를 가리키며, 그 값은 항상 9입니다(운영 영역 2개, 제한 영역 2개, 인터넷, 협력업체 네트워크, HQ 영역 내 서브넷 3개). 실행 간 일관성을 보장하기 위해 모든 서브넷은 알파벳순으로 정렬됩니다.

There general structure of the observation vector is as follows where n is the number of subnets included in the observation space:

> 관찰값 벡터(observation vector)의 전체 구조는 다음과 같으며, 여기서 n은 관찰 공간(observation space)에 포함된 서브넷의 수입니다.

<center>

|**Index**            |**Length**|**Description**|**Value**|
|:-------------------:|:--------:|:-------------:|:---------------------------|
| 0                   | 1        | Mission Phase | 0: Mission Phase 1 <br />1: Mission Phase 2A <br />2: Mission Phase 2B |
| 1                   | 3S+2H    | Subnet 0 Info | See "Subnet Info" Table |
| 3S+2H+1             | ...      | ...           | ... |
| 3(n-1)S+2(n-1)H+1   | 3S+2H    | Subnet n Info | ' ' |
| 3nS+2nH+1           | 4x8      | Message Block | User Defined (See Below) |

</center>

> 위 표를 같은 구조로 옮긴 한국어 표입니다(인덱스 수식과 식별자 토큰은 그대로 둡니다). 열 머리글의 뜻: **Index**(인덱스, 시작 위치), **Length**(길이), **Description**(설명), **Value**(값).

<center>

|**Index**            |**Length**|**설명**|**값**|
|:-------------------:|:--------:|:-------------:|:---------------------------|
| 0                   | 1        | 임무 단계(Mission Phase) | 0: 임무 단계 1 <br />1: 임무 단계 2A <br />2: 임무 단계 2B |
| 1                   | 3S+2H    | 서브넷 0 정보 | "Subnet Info"(서브넷 정보) 표 참고 |
| 3S+2H+1             | ...      | ...           | ... |
| 3(n-1)S+2(n-1)H+1   | 3S+2H    | 서브넷 n 정보 | ' ' |
| 3nS+2nH+1           | 4x8      | 메시지 블록(Message Block) | 사용자 정의 (아래 참고) |

</center>

The message block contains four, 8-bit messages from the other agents, with each index corresponding to a specific agent (0-4 in order, excluding self). The contents of these 8-bit messages are defined by the user, but will default to zero if not specified.

> 메시지 블록(message block)은 다른 에이전트로부터 온 8비트 메시지 4개를 담으며, 각 인덱스는 특정 에이전트(자신을 제외하고 0-4 순서)에 대응합니다. 이 8비트 메시지의 내용은 사용자가 정의하며, 지정하지 않으면 기본값 0이 됩니다.

The "Subnet Info" block for each subnet is further subdivided as follows:

> 각 서브넷의 "Subnet Info"(서브넷 정보) 블록은 다시 다음과 같이 세분화됩니다.

<center>

|**Relative Index**|**Length**|**Description**                   |**Element Values (Boolean)**|
|:-------------------:|:--------:|:--------------------------------:|:---------------------------|
| 0                   | S        | One-hot Encoded Subnet Vector    | 1: Current Subnet <br />0: All Other Subnets |
| S                   | S        | Blocked Subnets                  | 1: Subnet Blocked <br />0: Subnet Not Blocked |
| 2S                  | S        | Communication Policy             | 1: Subnet *Should* be Blocked <br />0: Subnet *Should Not* be Blocked |
| 3S                  | H        | Malicious Process Event Detected | 1: Malicious Process Detected on Host <br />0: No Events |
| 3S+H                | H        | Malicious Network Event Detected | 1: Malicious Connection Detected on Host <br />0: No Events |

</center>

> 위 표를 같은 구조로 옮긴 한국어 표입니다(모든 값은 불리언[Boolean, 참/거짓]). 열 머리글의 뜻: **Relative Index**(상대 인덱스, 블록 내 시작 위치), **Length**(길이), **Description**(설명), **Element Values (Boolean)**(원소 값, 불리언).

<center>

|**Relative Index**|**Length**|**설명**                   |**원소 값 (Boolean)**|
|:-------------------:|:--------:|:--------------------------------:|:---------------------------|
| 0                   | S        | 원-핫 인코딩 서브넷 벡터(One-hot Encoded Subnet Vector)    | 1: 현재 서브넷 <br />0: 그 외 모든 서브넷 |
| S                   | S        | 차단된 서브넷(Blocked Subnets)                  | 1: 서브넷 차단됨 <br />0: 서브넷 차단되지 않음 |
| 2S                  | S        | 통신 정책(Communication Policy)             | 1: 서브넷이 차단되어야 함(*Should*) <br />0: 서브넷이 차단되지 않아야 함(*Should Not*) |
| 3S                  | H        | 악성 프로세스 이벤트 탐지(Malicious Process Event Detected) | 1: 호스트에서 악성 프로세스 탐지됨 <br />0: 이벤트 없음 |
| 3S+H                | H        | 악성 네트워크 이벤트 탐지(Malicious Network Event Detected) | 1: 호스트에서 악성 연결 탐지됨 <br />0: 이벤트 없음 |

</center>

In this challenge, blue agents 0-3 are responsible for defending a single subnet each (n=1), while blue agent 4 defends three (n=3). For this reason, blue agent 4 has a longer observation than the others as the other agents only have a single subnet info block. If the `pad_spaces=True` option is supplied to `BlueEnterpriseWrapper`, the area *after* the message block will be filled with zeros for these agents.

> 이 챌린지에서 Blue 에이전트 0-3은 각자 하나의 서브넷을 방어하고(n=1), Blue 에이전트 4는 세 개를 방어합니다(n=3). 이 때문에 다른 에이전트는 서브넷 정보 블록을 하나만 갖는 반면, Blue 에이전트 4는 관찰값이 더 깁니다. `BlueEnterpriseWrapper`에 `pad_spaces=True` 옵션을 주면, 이들 에이전트의 경우 메시지 블록 *뒤*의 영역이 0으로 채워집니다.
