---
hide:
  - navigation
  - toc
---


![TTCP CAGE Challenges Logo](assets/CAGE-Logo-small.png){ align=right }
# TTCP CAGE Challenge 4

The TTCP CAGE Challenges are a series of public challenges instigated to foster the development of autonomous cyber defensive agents. The CAGE Challenges use cybersecurity scenarios inspired by real-world situations. 

> TTCP CAGE 챌린지는 **자율 사이버 방어 에이전트**(스스로 판단해 사이버 공격을
> 막는 AI)의 개발을 촉진하기 위해 시작된 공개 챌린지 시리즈입니다. CAGE 챌린지는
> 실제 상황에서 영감을 얻은 사이버 보안 시나리오를 사용합니다.

The challenges use the Cyber Operations Research Gym (CybORG) to provide a cyber simulation for the training and evaluation AI algorithms, such as Deep Reinforcement Learning. The CAGE activity aims to run a series of challenges of increasing complexity and realism. 

> 이 챌린지들은 **CybORG**(Cyber Operations Research Gym)를 사용해, 심층
> 강화학습(Deep Reinforcement Learning)과 같은 AI 알고리즘을 학습·평가하기 위한
> 사이버 시뮬레이션을 제공합니다. CAGE 활동의 목표는 복잡도와 현실성이 점점
> 높아지는 일련의 챌린지를 운영하는 것입니다.

## Where to get started (시작하는 방법)

1. Download the CybORG package provided with the challenge or download the [repository](https://github.com/cage-challenge/cage-challenge-4).
2. Read through the CybORG README, also available on the ['Challenge Details' tab](pages/README.md) of the documentation.
3. Read the [Tutorials](pages/how-to-guides.md) to get a better understanding of CybORG and how to train agents using it.
4. Explore the [Reference](pages/reference/reference.md) section for more in-depth class explanations.
5. Develop your agent!
6. Look at the [Codalabs webpage](https://codalab.lisn.upsaclay.fr/competitions/17672) for how to submit.

> 1. 챌린지와 함께 제공되는 CybORG 패키지를 내려받거나 [저장소](https://github.com/cage-challenge/cage-challenge-4)를 내려받습니다.
> 2. CybORG README를 읽어봅니다. 이 문서의 ['Challenge Details' 탭](pages/README.md)에서도 볼 수 있습니다.
> 3. [Tutorials](pages/how-to-guides.md)를 읽고 CybORG와 이를 사용해 에이전트를 학습시키는 방법을 더 잘 이해합니다.
> 4. 더 깊이 있는 클래스 설명은 [Reference](pages/reference/reference.md) 섹션에서 살펴봅니다.
> 5. 여러분의 에이전트를 개발합니다!
> 6. 제출 방법은 [Codalabs 웹페이지](https://codalab.lisn.upsaclay.fr/competitions/17672)에서 확인합니다.

## Important Dates (주요 일정)

- **20 Feb 2024:** Challenge 4 released. Development phase begins.

- **29 Mar 2024 23:59 (UTC):** Development phase ends. Competition phase begins.

- **10 May 2024 23:59 (UTC):** Competition phase ends. Final results announced on Codalabs leaderboard.

> - **2024년 2월 20일:** Challenge 4 공개. 개발 단계(development phase) 시작.
> - **2024년 3월 29일 23:59 (UTC):** 개발 단계 종료. 경쟁 단계(competition phase) 시작.
> - **2024년 5월 10일 23:59 (UTC):** 경쟁 단계 종료. 최종 결과를 Codalabs 리더보드에 발표.

## Preparing a submission (제출물 준비하기)

Now that your agent has been developed and trained, it's time to get it ready for submission.
Submissions are uploaded as zip files containing a `submission.py` file, any model weights,
and your agent code that loads the model (if applicable).

> 이제 에이전트를 개발하고 학습까지 마쳤으니, 제출할 수 있도록 준비할 차례입니다.
> 제출물은 `submission.py` 파일과 모델 가중치(model weights), 그리고 (해당되는
> 경우) 모델을 로드하는 에이전트 코드를 담은 zip 파일로 업로드합니다.

To get started, create and move to a staging directory using `mkdir staging; cd staging`.

> 시작하려면 `mkdir staging; cd staging` 명령으로 스테이징 디렉터리(staging
> directory, 제출물을 모아두는 작업 폴더)를 만들고 그곳으로 이동합니다.

Submissions for this challenge must adhere to the following outline:

> 이 챌린지의 제출물은 다음 형식을 반드시 따라야 합니다.

```python
from CybORG import CybORG
from CybORG.Agents import BaseAgent

from ray.rllib.env.multi_agent_env import MultiAgentEnv
from CybORG.Agents.Wrappers.EnterpriseMAE import EnterpriseMAE

### Import custom agents here ###
from dummy_agent import DummyAgent


class Submission:

    # Submission name
    NAME: str = "SUBMISSION NAME"

    # Name of your team
    TEAM: str = "TEAM NAME"

    # What is the name of the technique used? (e.g. Masked PPO)
    TECHNIQUE: str = "TECHNIQUE NAME"

    # Use this function to define your agents.
    AGENTS: dict[str, BaseAgent] = {
        f"blue_agent_{agent}": DummyAgent() for agent in range(5)
    }

    # Use this function to optionally wrap CybORG with your custom wrapper(s).
    def wrap(env: CybORG) -> MultiAgentEnv:
        return EnterpriseMAE(env)

```

Copy this template to your staging directory as `submission.py` and modify the value of
each field to reflect your submission. Agent code can be included directly in this file
or be copied to the staging directory and be imported by name.

> 이 템플릿을 스테이징 디렉터리에 `submission.py`라는 이름으로 복사한 뒤, 각 필드의
> 값을 여러분의 제출물에 맞게 수정합니다. 에이전트 코드는 이 파일 안에 직접 포함하거나,
> 스테이징 디렉터리에 복사해 두고 이름으로 임포트(import)할 수 있습니다.

As seen in the submission template, your custom agents and wrappers *must* conform to the
`BaseAgent` and `MultiAgentEnv` types, respectively. Please keep this in mind during
development.

> 제출 템플릿에서 볼 수 있듯이, 여러분이 직접 만든 에이전트와 래퍼(Wrapper)는 각각
> `BaseAgent` 타입과 `MultiAgentEnv` 타입을 *반드시* 따라야 합니다. 개발할 때 이
> 점을 염두에 두시기 바랍니다.

#### Tip for loading weights from file (파일에서 가중치 로드하기 팁)

If your agent is a trained model with weights, include a copy of these weights in the
staging directory. Your agent code should load these weights from file using a relative
path: `load_weights(os.path.dirname(__file__) + "/agent_weights.pkl")`.

> 여러분의 에이전트가 가중치를 가진 학습된 모델이라면, 그 가중치 파일의 사본을
> 스테이징 디렉터리에 함께 넣으세요. 에이전트 코드는 상대 경로(relative path)를
> 사용해 파일에서 가중치를 로드해야 합니다:
> `load_weights(os.path.dirname(__file__) + "/agent_weights.pkl")`.

### Testing your submission (제출물 테스트하기)

To verify that your agent and associated wrappers will be properly picked up by the evaluation
script, test your submission using the evaluation script provided with CybORG:
`python3 -m CybORG.Evaluation.evaluation --max-eps 2 /path/to/staging /tmp/output`.
The standard output from this command should closely resemble the following output:

> 여러분의 에이전트와 관련 래퍼가 평가 스크립트(evaluation script)에 제대로 인식되는지
> 확인하려면, CybORG와 함께 제공되는 평가 스크립트로 제출물을 테스트하세요:
> `python3 -m CybORG.Evaluation.evaluation --max-eps 2 /path/to/staging /tmp/output`.
> 이 명령의 표준 출력(standard output)은 다음 출력과 거의 비슷해야 합니다.

```
CybORG v4, Scenario4
Author: SUBMISSION NAME, Team: TEAM NAME, Technique: TECHNIQUE NAME
Using agents {'blue_agent_0': DummyAgent, 'blue_agent_1': DummyAgent, 'blue_agent_2': DummyAgent, 'blue_agent_3': DummyAgent, 'blue_agent_4': DummyAgent}
Results will be saved to /tmp/output/
Average reward is: -18386 with a standard deviation of 2904.794657114337
File took 0:01:33.236403 amount of time to finish evaluation
Saving results to /tmp/output/
```

### Packaging and submitting (패키징 및 제출하기)

The last step before packaging is to create an empty `metadata` file using `touch metadata`.
This ensures CodaLabs will treat the submission as a code submission and will be forwarded
to the evaluation script. It is imperative that this `metadata` file is empty.

> 패키징 전 마지막 단계는 `touch metadata` 명령으로 빈 `metadata` 파일을 만드는
> 것입니다. 이렇게 하면 CodaLabs가 제출물을 코드 제출물로 인식해 평가 스크립트로
> 전달합니다. 이 `metadata` 파일은 반드시 비어 있어야 합니다.

Finally, all the files in the staging directory can be packaged into a zip file for
submission using `zip ../name_of_your_submission.zip *`. If you are using a graphical zip
utility, ensure that only the files within the `staging` directory and not the directory
itself are included in the zip file. The final package should be similar to the following:

> 마지막으로, 스테이징 디렉터리 안의 모든 파일을 `zip ../name_of_your_submission.zip *`
> 명령으로 제출용 zip 파일에 담을 수 있습니다. 그래픽(GUI) zip 도구를 사용한다면,
> `staging` 디렉터리 자체가 아니라 그 안의 파일들만 zip 파일에 포함되도록 주의하세요.
> 최종 패키지는 다음과 비슷한 모습이어야 합니다.

```shell
name_of_your_submission.zip
├ metadata
├ submission.py
├ agent_code.py
└ agent_weights.pkl
```

Once the package contents have been verified, upload the zip file to the competition and
verify that the submission status is `running`. At this point, the evaluation process can
take up to several hours, so be sure to check back periodically to ensure that the process
has not failed.

> 패키지 내용을 확인했다면, zip 파일을 대회에 업로드하고 제출 상태가 `running`인지
> 확인하세요. 이 시점에서 평가 과정은 최대 몇 시간까지 걸릴 수 있으니, 과정이
> 실패하지 않았는지 주기적으로 다시 확인하시기 바랍니다.


## Additional information (추가 정보)

### Description of approach (접근 방법 설명)

As part of your submission, we request that you share a description of the methods/techniques
used in developing your agents. We will use this information as part of our in-depth analysis
and comparison of the various techniques submitted to the challenge. In hosting the CAGE
challenges, one of our main goals is to understand the techniques that lead to effective
autonomous cyber defensive agents, as well as those that are not as effective. We are
planning on publishing the analysis and taxonomy of the different approaches that create
autonomous cyber defensive agents. To that end, we encourage you to also share details on
any unsuccessful approaches taken. Please also feel free to share any interesting discoveries
and thoughts regarding future work to help us shape the future of the CAGE Challenges.

> 제출의 일부로, 여러분의 에이전트를 개발하는 데 사용한 방법·기법에 대한 설명을
> 함께 공유해 주시기를 요청합니다. 저희는 이 정보를 챌린지에 제출된 다양한 기법을
> 심층 분석·비교하는 데 활용합니다. CAGE 챌린지를 운영하는 주요 목표 중 하나는
> 효과적인 자율 사이버 방어 에이전트로 이어지는 기법은 무엇이고, 그렇지 못한 기법은
> 무엇인지를 이해하는 것입니다. 저희는 자율 사이버 방어 에이전트를 만드는 여러
> 접근 방법에 대한 분석과 분류 체계(taxonomy)를 발표할 계획입니다. 이를 위해
> 성공하지 못한 접근 방법에 대한 세부 내용도 함께 공유해 주시기를 권장합니다. 또한
> 흥미로운 발견이나 향후 연구에 대한 생각이 있다면 자유롭게 공유해 주셔서, CAGE
> 챌린지의 미래를 함께 만들어 가는 데 도움을 주시기 바랍니다.

We provide a [latex template](https://github.com/cage-challenge/CybORG/blob/main/CybORG/Evaluation/submission/submission_template_example/template_readme.md) as a guide for writing your description.
An examplar description can be found [here](https://arxiv.org/pdf/2211.15557.pdf).

> 설명 작성에 참고할 수 있도록 [latex 템플릿](https://github.com/cage-challenge/CybORG/blob/main/CybORG/Evaluation/submission/submission_template_example/template_readme.md)을 제공합니다.
> 예시 설명은 [여기](https://arxiv.org/pdf/2211.15557.pdf)에서 볼 수 있습니다.


### Evaluation results (평가 결과)

If you have run the evaluation script locally, please feel free to include your results
as part of the submission in an `evaluation_output` directory in your submission zip file.

> 평가 스크립트를 로컬에서 실행했다면, 그 결과를 제출 zip 파일 안의
> `evaluation_output` 디렉터리에 포함해 제출의 일부로 함께 넣으셔도 좋습니다.

To run the evaluation locally, use
`python3 -m CybORG.Evaluation.evaluation /path/to/staging /path/to/staging/evaluation_output`.

> 평가를 로컬에서 실행하려면 다음 명령을 사용하세요:
> `python3 -m CybORG.Evaluation.evaluation /path/to/staging /path/to/staging/evaluation_output`.

### Issues (문의 및 오류 신고)

If you have any questions or encounter an error, please submit an issue on the challenge forum
on CodaLabs. In the case of an error, please provide a detailed description of the circumstances
surrounding the error and the full output where possible so that we can replicate the error.

> 질문이 있거나 오류가 발생한 경우, CodaLabs의 챌린지 포럼에 이슈(issue)를 등록해
> 주세요. 오류의 경우에는 저희가 그 오류를 재현할 수 있도록, 오류가 발생한 상황에
> 대한 상세한 설명과 가능한 한 전체 출력(full output)을 함께 제공해 주시기 바랍니다.

