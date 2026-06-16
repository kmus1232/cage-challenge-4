# 한국어 번역 가이드 (TRANSLATION-GUIDE.ko.md)

이 문서는 `cage-challenge-4` 레포의 **한국어 번역 작업 기준**이다. 모든 번역
파일은 여기서 정한 형식·용어·원칙을 따른다. 사람이든 보조 에이전트든 번역에
손대기 전에 이 문서를 먼저 읽는다.

> **이 레포는 무엇인가?**
> CAGE Challenge 4(CC4)는 **자율 사이버 방어 에이전트**를 연구하기 위한
> 강화학습(Reinforcement Learning) 시뮬레이션 환경 **CybORG**(Cyber
> Operations Research Gym) 위에서 동작하는 공개 챌린지다. 군 기지 네트워크를
> 모사한 환경에서 방어(Blue)·공격(Red)·정상사용자(Green) 에이전트가 상호
> 작용한다.

---

## 1. 번역 범위

| 대상 | 처리 방식 |
|---|---|
| 마크다운 문서 (`README.md`, `documentation/**/*.md`) | **전량** 영문+한글 병기 |
| 코드 Tier 1 — 학습 핵심 (`env.py`, 주요 인터페이스/Action/Agent/Wrapper) | docstring 병기 + 한국어 설명 주석 보강 |
| 코드 Tier 2/3 — 시뮬레이터 내부·테스트 | 기존 영어 주석만 한국어 추가, 신규 설명 생략 |

**번역하지 않는 것**: 코드 로직, 변수·함수·클래스 이름, `import` 문, 명령어,
URL, 파일 경로, 코드 블록 안의 코드, 논문 인용(BibTeX) 블록, 라이선스 문구.

---

## 2. 마크다운 병기 형식

원문(영어)을 그대로 두고, **각 문단 바로 아래에 한국어 번역을 인용블록(`>`)으로**
붙인다.

### 규칙

1. **제목(heading)**: `## English (한국어)` 형태로 병기한다. 영어 제목을
   유지해야 MkDocs 내비게이션·앵커 링크가 깨지지 않는다.
2. **본문 문단**: 영어 문단을 두고, 빈 줄 뒤에 한국어 번역을 `>` 인용블록으로
   적는다.
3. **리스트**: 영어 리스트를 두고, 그 아래 한국어 리스트를 같은 구조로 옮긴다.
   (항목마다 인용블록을 다는 대신, 리스트 전체를 한 번에 옮겨 가독성을 지킨다.)
4. **코드 블록·명령어·인용(citation)·URL·이미지**: 번역하지 않고 그대로 둔다.
5. **MkDocs 확장 문법**(`!!! tip "..."`, `=== "탭"` 등): 구조는 그대로 두고
   안의 설명 글만 번역한다.
6. **전문 용어**: 첫 등장 시 `용어(English)` 또는 `English(한국어 풀이)` 로
   풀어주고, 이후에는 짧은 쪽으로 통일한다(§5 용어집 참고).
7. **표(table)**:
   - 셀 내용이 **숫자·기호 위주**(보상표, 통신정책표 등)이면 표 구조는
     그대로 두고, 표 **바로 위 또는 아래에 한국어 설명 문단**(헤더·행 이름의
     뜻, 표가 의미하는 바)을 인용블록으로 덧붙인다. 표 자체는 복제하지 않는다.
   - 셀 내용이 **문장·설명 위주**(예: Appendix A 액션 목록)이면, 영어 표
     아래에 **같은 구조의 한국어 표를 한 벌 더** 만든다. 표 헤더와 셀의 산문을
     한국어로 옮기되, 코드·식별자(`fp_detection_rate` 등)는 그대로 둔다.
8. **HTML 블록**(`<figure>`, `<center>`, `<img>` 등): 태그 구조·속성은 그대로
   두고, 사람이 읽는 텍스트(`<figcaption>` 캡션 등)만 영어 뒤에 한국어를
   괄호 또는 줄바꿈으로 덧붙인다. `<img src>`·`alt`는 건드리지 않는다.

### 예시

````markdown
## Introduction (소개)

The TTCP CAGE Challenges are a series of public challenges instigated to foster
the development of autonomous cyber defensive agents.

> TTCP CAGE 챌린지는 **자율 사이버 방어 에이전트**(스스로 판단해 사이버 공격을
> 막는 AI)의 개발을 촉진하기 위해 시작된 공개 챌린지 시리즈입니다.

The challenges use the Cyber Operations Research Gym (CybORG) to provide a
high-fidelity cyber simulation.

> 이 챌린지들은 **CybORG**(Cyber Operations Research Gym)를 사용해 정밀도 높은
> 사이버 시뮬레이션을 제공합니다.
````

---

## 3. 코드 주석/docstring 형식

코드 로직·이름·import는 **절대 바꾸지 않는다.** 설명 텍스트만 다룬다.

### 규칙

1. **docstring**: 영어 원문을 남기고, docstring 안 끝부분에 `[한국어]` 줄을
   넣은 뒤 번역·설명을 잇는다. 긴 docstring은 핵심을 살려 읽기 좋게 옮긴다.
2. **인라인 `#` 주석**: 짧으면 영어 옆 또는 위에 한국어를 덧붙인다. 원문 주석은
   지우지 않는다.
3. **설명 보강**: 이해가 까다로운 구간에 `# [설명] ...` 형식으로 한국어 주석을
   새로 추가한다. (어디까지나 보조 설명이며 동작을 바꾸지 않는다.)
4. **번역으로 줄 수가 바뀌어도 코드 동작에는 영향이 없어야 한다.** 문자열
   리터럴 안(실행에 쓰이는 문자열)은 건드리지 않는다.

### 예시

```python
class CybORG(CybORGLogger):
    """The main interface for the Cyber Operations Research Gym.

    The primary purpose of this class is to provide a unified interface for the
    CybORG simulation and emulation environments.

    [한국어]
    CybORG(Cyber Operations Research Gym)의 메인 인터페이스 클래스.
    시뮬레이션/에뮬레이션 환경에 대한 단일 창구를 제공하는 것이 핵심 역할이다.
    """
```

---

## 4. 톤·문체

- 문서(독자용 산문): **~합니다/~입니다** 체로 친절하게.
- 코드 주석(개발자용): **~한다/~이다** 체로 간결하게.
- 한 문단 5줄 이내, 핵심을 앞에. 영어 메타 용어는 한국어 풀이를 곁들인다.
- 직역으로 어색하면 의미 중심으로 자연스럽게 옮긴다(오역은 금지).

---

## 5. 용어집 (Glossary)

**원칙**: 챌린지의 고유 용어·역할명·고유명사는 영어를 유지하고 첫 등장 시
한국어 풀이를 붙인다. 일반 산문은 한국어로 옮긴다.

### 핵심 도메인 용어

| 영어 | 한국어 처리 |
|---|---|
| CAGE Challenge | CAGE 챌린지 |
| agent | 에이전트 |
| Blue agent | **Blue 에이전트** (방어 측) |
| Red agent | **Red 에이전트** (공격 측) |
| Green agent | **Green 에이전트** (정상 사용자) |
| autonomous cyber defence | 자율 사이버 방어 |
| Reinforcement Learning (RL) | 강화학습 |
| Multi-Agent Reinforcement Learning (MARL) | 다중 에이전트 강화학습 |
| CybORG (Cyber Operations Research Gym) | CybORG (그대로) |
| simulation / emulation | 시뮬레이션 / 에뮬레이션 |
| environment | 환경 |
| Observation | 관찰값(Observation) |
| Action | 행동(Action) |
| Action Space | 행동 공간(Action Space) |
| Reward | 보상 |
| Reward Machine | 보상 머신(Reward Machine) |
| Wrapper | 래퍼(Wrapper) |
| Scenario | 시나리오 |
| Scenario Generator | 시나리오 생성기 |
| Episode | 에피소드 |
| step | 스텝(step) |
| policy | 정책(policy) |

### 네트워크·시스템 용어

| 영어 | 한국어 처리 |
|---|---|
| Host | 호스트 |
| Subnet | 서브넷 |
| Session | 세션 |
| Service | 서비스 |
| Interface | 인터페이스 |
| Process | 프로세스 |
| Port | 포트 |
| User / privileged user | 사용자 / 권한 있는 사용자 |
| security zone | 보안 영역(security zone) |
| Enterprise network | 엔터프라이즈 네트워크 |
| deployed network | 배치 네트워크(deployed network) |
| Headquarters (HQ) | 본부(HQ) |
| Contractor network | 협력업체 네트워크(Contractor network) |
| UAV / drone | UAV(무인기) / 드론 |

### 공격·방어 액션 용어

| 영어 | 한국어 처리 |
|---|---|
| Monitor | Monitor(모니터링) |
| Analyse | Analyse(분석) |
| Decoy | Decoy(디코이, 미끼) |
| Remove | Remove(제거) |
| Restore | Restore(복원) |
| Block / Allow Traffic | 트래픽 차단/허용 |
| Discover Remote Systems | 원격 시스템 탐색 |
| Discover Network Services | 네트워크 서비스 탐색 |
| Exploit (Remote Service) | 익스플로잇(원격 서비스 공격) |
| Privilege Escalate | 권한 상승 |
| Degrade Services | 서비스 성능 저하 |
| Impact | Impact(타격) |
| Withdraw | Withdraw(철수) |
| Phishing Email | 피싱 이메일 |
| Decoy detection | 디코이 탐지 |

> 표에 없는 용어는 위 원칙(고유명사는 영어 유지+풀이, 산문은 한국어)에 따라
> 일관되게 처리하고, 새로 정한 용어는 이 표에 추가한다.
