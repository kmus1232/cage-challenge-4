# Training RLlib Agents (RLlib 에이전트 학습시키기)
This section is a tutorial to train the defensive blue agents in the CybORG environment. 

> 이 장은 CybORG(Cyber Operations Research Gym) 환경에서 방어 측인 **Blue 에이전트**(방어 측)를 학습시키는 방법을 다루는 튜토리얼입니다.

This example is a most basic training example using RLlib. More indepth tutorials of RLlib use can be found in [Ray's documentation of RLlib](https://docs.ray.io/en/latest/rllib/rllib-training.html).

> 이 예제는 RLlib를 사용한 가장 기본적인 학습 예제입니다. RLlib 사용에 대한 더 자세한 튜토리얼은 [Ray의 RLlib 공식 문서](https://docs.ray.io/en/latest/rllib/rllib-training.html)에서 확인할 수 있습니다.

The code for this example is provided as `CybORG/Evaluation/training_examples/TrainingRay.py`.

> 이 예제의 코드는 `CybORG/Evaluation/training_examples/TrainingRay.py` 파일로 제공됩니다.

???+ Question "What if I don't want to use RLlib?"
    The submissions to CAGE challenge 4 are not limited to reinforcement learning approaches or use of RLlib. Please feel free to make your own custom wrappers!

    > CAGE 챌린지 4에 제출하는 방식은 강화학습(Reinforcement Learning) 접근법이나 RLlib 사용에만 국한되지 않습니다. 얼마든지 직접 만든 커스텀 래퍼(Wrapper)를 사용해도 됩니다!

## Importing CybORG (CybORG 임포트하기)
The initial steps are identical to the intial steps of the interfacing with the environment in the Getting Started Guide. 

> 처음 시작 단계는 Getting Started Guide(시작 안내서)에서 환경과 연동하던 초기 단계와 동일합니다.

As per [Getting Started With CybORG](2_Getting_Started.md), it is necessary to import the `CybORG` class, the `EnterpriseScenarioGenerator` and the `EnterpriseMAE` wrapper. 

> [Getting Started With CybORG](2_Getting_Started.md) 문서에서 설명한 것처럼, `CybORG` 클래스, `EnterpriseScenarioGenerator`(엔터프라이즈 시나리오 생성기), 그리고 `EnterpriseMAE` 래퍼(Wrapper)를 임포트해야 합니다.

```python title="training_agents.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.Wrappers import EnterpriseMAE
```

To train an agent, we need a Blue Agent to be interacting with the external API while Red and Green take their actions automatically in the background.

> 에이전트를 학습시키려면, **Blue 에이전트**가 외부 API와 상호작용하는 동안 **Red 에이전트**(공격 측)와 **Green 에이전트**(정상 사용자)는 백그라운드에서 자동으로 행동(Action)을 수행하도록 해야 합니다.

We can achieve this by specifying an agents dictionary to pass into CybORG when instantiating the class. Now, whenever the step function is called, the agents will take turns to perform their actions. In this example, this instantiates the `SleepAgent`, `EnterpriseGreenAgent` and `FiniteStateRedAgent`.

> 이는 클래스를 인스턴스화할 때 CybORG에 전달할 에이전트 딕셔너리(dictionary)를 지정함으로써 구현할 수 있습니다. 이렇게 하면 step 함수가 호출될 때마다 에이전트들이 번갈아 가며 자신의 행동(Action)을 수행합니다. 이 예제에서는 `SleepAgent`, `EnterpriseGreenAgent`, `FiniteStateRedAgent`를 인스턴스화합니다.

 

```python linenums="4"
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
```

This section imports key RLLib libraries, such as the register environment class and the algorithms that have been chosen to train upon.

> 이 부분에서는 환경 등록(register environment) 클래스와 학습에 사용할 알고리즘 등, 핵심 RLlib 라이브러리를 임포트합니다.

```python linenums="5"
from ray.tune import register_env
from ray.rllib.algorithms.ppo import PPOConfig, PPO
from ray.rllib.algorithms.dqn import DQNConfig, DQN
from ray.rllib.policy.policy import PolicySpec

```

## Instantiating CybORG (CybORG 인스턴스화하기)

Although CybORG uses an OpenAI gym API, it is not run by calling `gym.make()`. Instead, it has to be manually instantiated by calling the envionment creator constructor. The constructor has two mandatory string parameters: a mode-type which specifies which engine will be used under the hood and the class for the scenario which defines the network layout and agent action spaces. The `EnterpriseMAE` wrapper then wraps the environment so it is compatible with RLlib

> CybORG는 OpenAI gym API를 사용하지만, `gym.make()`를 호출해서 실행하지는 않습니다. 대신 환경 생성자(environment creator constructor)를 호출하여 수동으로 인스턴스화해야 합니다. 이 생성자는 두 개의 필수 문자열 파라미터를 받습니다. 하나는 내부적으로 어떤 엔진을 사용할지 지정하는 모드 타입(mode-type)이고, 다른 하나는 네트워크 구성과 에이전트의 행동 공간(Action Space)을 정의하는 시나리오(Scenario) 클래스입니다. 그런 다음 `EnterpriseMAE` 래퍼(Wrapper)가 이 환경을 감싸 RLlib와 호환되도록 만들어 줍니다.

Challenge 4 is instantiated as follows:

> 챌린지 4는 다음과 같이 인스턴스화합니다.

```python linenums="9"
def env_creator_CC4(env_config: dict):
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=FiniteStateRedAgent,
        steps=500
    )
    cyborg = CybORG(scenario_generator=sg)
    env = EnterpriseMAE(env=cyborg)
    return env
```

Register a custom env creator function with a string name. This function must take a single `env_config(dict)` parameter and return an env instance.
Then, to get it to work with the `tune.register_env()`, you can use your custom env with a lambda function.

> 커스텀 환경 생성 함수를 문자열 이름과 함께 등록합니다. 이 함수는 반드시 단일 `env_config(dict)` 파라미터를 받아 환경 인스턴스를 반환해야 합니다.
> 그런 다음 `tune.register_env()`와 함께 동작시키려면, 람다(lambda) 함수를 사용해 커스텀 환경을 전달하면 됩니다.

```python linenums="19"
register_env(name="CC4", env_creator=lambda config: env_creator_CC4(config))
env = env_creator_CC4({})
```

For environments with multiple groups, or mixtures of agent groups and individual agents, you can use grouping in conjunction with the policy mapping API described in prior sections. This creates a policy mapping function to map the agent to the config below.

> 여러 그룹이 있거나 에이전트 그룹과 개별 에이전트가 섞여 있는 환경에서는, 앞 장에서 설명한 정책 매핑(policy mapping) API와 그룹화(grouping)를 함께 사용할 수 있습니다. 아래 코드는 에이전트를 설정(config)에 매핑하는 정책 매핑 함수를 만듭니다.

```python linenums="21"
NUM_AGENTS = 5
POLICY_MAP = {f"blue_agent_{i}": f"Agent{i}" for i in range(NUM_AGENTS)}

def policy_mapper(agent_id, episode, worker, **kwargs):
    return POLICY_MAP[agent_id]
```

To configure the environment, use the standard RLlib config formant. For multi-agent environments such as CybORG, with five types of agents, their experiences are aggregated by policy, so from RLlib’s perspective it’s just optimizing three different types of policy. The configuration might look something like this:

> 환경을 설정하려면 표준 RLlib 설정(config) 형식을 사용합니다. CybORG처럼 다섯 종류의 에이전트가 있는 다중 에이전트(Multi-Agent) 환경에서는 각 에이전트의 경험이 정책(policy)별로 집계됩니다. 따라서 RLlib의 관점에서는 단지 세 가지 종류의 정책(policy)을 최적화하는 것일 뿐입니다. 설정은 대략 다음과 같은 모습입니다.

```python linenums="26"
algo_config = (
    PPOConfig()
    .environment(env="CC4")
    .debugging(logger_config={"logdir":"logs/PPO_Example", "type":"ray.tune.logger.TBXLogger"})
    .multi_agent(policies={
        ray_agent: PolicySpec(
            policy_class=None,
            observation_space=env.observation_space(cyborg_agent),
            action_space=env.action_space(cyborg_agent),
            config={"gamma": 0.85},
        ) for cyborg_agent, ray_agent in POLICY_MAP.items()
    },
    policy_mapping_fn=policy_mapper
))

```

## Agent Training (에이전트 학습)

To train the agents with the above config, three steps are then required - building the alogrithm, setting the number of steps you wish to run the algorithm for and then saving the results for further analysis. 

> 위 설정(config)으로 에이전트를 학습시키려면 세 단계가 필요합니다. (1) 알고리즘을 빌드(build)하고, (2) 알고리즘을 몇 스텝(step) 동안 실행할지 지정한 뒤, (3) 추후 분석을 위해 결과를 저장하는 것입니다.

```python linenums="40"
algo = algo_config.build()

for i in range(50):
    train_info=algo.train()

algo.save("results")
```

After the training has occurred you can analyse the results on your prefered platfrom. To use tensorboard run the following command:

> 학습이 끝나면 원하는 플랫폼에서 결과를 분석할 수 있습니다. tensorboard를 사용하려면 다음 명령어를 실행하세요.

`tensorboard --logdir logs/`

The link that comes up will display graphs that correspond to what the agent is learning and reward. 

> 명령을 실행하면 나타나는 링크를 열면, 에이전트가 무엇을 학습하고 있는지와 보상(Reward)에 대응하는 그래프를 확인할 수 있습니다.

