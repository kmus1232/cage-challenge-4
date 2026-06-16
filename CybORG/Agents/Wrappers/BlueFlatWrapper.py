from __future__ import annotations
from gymnasium import Space, spaces

from CybORG import CybORG
from CybORG.Simulator import State
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import (
    EnterpriseScenarioGenerator,
)

from typing import Any

import numpy as np
import networkx as nx

import functools
import itertools

from CybORG.Agents.Wrappers.BlueFixedActionWrapper import (
    BlueFixedActionWrapper,
    MESSAGE_LENGTH,
    EMPTY_MESSAGE,
    NUM_MESSAGES,
)

NUM_SUBNETS = 9
NUM_HQ_SUBNETS = 3

MAX_USER_HOSTS = EnterpriseScenarioGenerator.MAX_USER_HOSTS
MAX_SERVER_HOSTS = EnterpriseScenarioGenerator.MAX_SERVER_HOSTS
MAX_HOSTS = MAX_USER_HOSTS + MAX_SERVER_HOSTS


class BlueFlatWrapper(BlueFixedActionWrapper):
    """Converts observation spaces to vectors of fixed size and ordering across episodes.

    This is a companion wrapper to the BlueFixedActionWrapper and inherits the fixed
    action space and int-to-action mappings as a result.

    Using the *sorted* host and subnet lists from FixedAction wrapper, this wrapper
    establishes the maximum observation space for each agent. On each step, the
    observation vectors are populated such that each element within a vector will
    have a consistent meaning across runs. This is critical for RL-based agents.

    [한국어]
    Blue 에이전트(방어 측)의 관찰값(Observation)을, 에피소드가 바뀌어도 크기와
    순서가 고정된 벡터로 변환하는 래퍼(Wrapper)다.

    BlueFixedActionWrapper와 짝을 이루는 래퍼이며, 그 래퍼로부터 고정된 행동
    공간(Action Space)과 정수↔행동(Action) 매핑을 그대로 물려받는다.

    FixedAction 래퍼가 제공하는 *정렬된* 호스트·서브넷 목록을 사용해 각 에이전트의
    최대 관찰 공간을 정해 둔다. 매 스텝(step)마다 관찰 벡터를 채울 때, 벡터의 각
    원소가 실행이 달라져도 항상 같은 의미를 갖도록 만든다. 이는 강화학습(RL) 기반
    에이전트에게 결정적으로 중요하다.
    """

    def __init__(self, env: CybORG, *args, **kwargs):
        """Initialize the BlueFlatWrapper for blue agents.

        Note: The padding setting is inherited from BlueFixedActionWrapper.

        Args:
            env (CybORG): The environment to wrap.

            *args, **kwargs: Extra arguments are ignored.

        [한국어]
        Blue 에이전트용 BlueFlatWrapper를 초기화한다.

        참고: 패딩(padding) 설정은 BlueFixedActionWrapper로부터 물려받는다.

        인자:
            env (CybORG): 래핑할 환경(environment).

            *args, **kwargs: 그 외 인자는 무시된다.
        """
        super().__init__(env, *args, **kwargs)
        self._short_obs_space, self._long_obs_space = self._get_init_obs_spaces()
        self.comms_policies = self._build_comms_policy()
        self.policy = {}

    def reset(self, *args, **kwargs) -> tuple[dict[str, Any], dict[str, Any]]:
        """Reset the environment and update the observation space.

        Args: All arguments are forwarded to the env provided to __init__.

        Returns
        -------
        observation : dict[str, Any]
            The observations corresponding to each agent, translated into a vector format.
        info : dict[str, dict]
            Forwarded from self.env.

        [한국어]
        환경을 리셋하고 관찰 공간을 갱신한다.

        인자: 모든 인자는 __init__에 전달된 env로 그대로 넘긴다.

        반환값
        -------
        observation : dict[str, Any]
            각 에이전트에 대응하는 관찰값으로, 벡터 형식으로 변환된 것.
        info : dict[str, dict]
            self.env에서 그대로 전달된 정보.
        """
        observations, info = super().reset(*args, **kwargs)
        self.comms_policies = self._build_comms_policy()
        observations = {
            a: self.observation_change(a, observations[a]) for a in self.agents
        }
        return observations, info

    def step(
        self,
        actions: dict[str, int | Action] = None,
        messages: dict[str, Any] = None,
        **kwargs,
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        """Take a step in the enviroment.

        Parameters:
            action_dict : dict[str, int | Action]
                The action or action index corresponding to each agent.
                Indices will be mapped to CybORG actions using the equivalent of `actions(k)[v]`.
                The meaning of each action can be found using `action_labels(k)[v]`.
            messages : dict[str, Any]
                Messages from each agent. If an agent does not specify a message, it will send an empty message.
            **kwargs : dict[str, Any]
                Extra keywords are forwarded.

        Returns
        -------
        observation : dict[str, np.ndarray]
            Observations for each agent as vectors.
        rewards : dict[str, float]
            Rewards for each agent.
        terminated : dict[str, bool]
            Flags whether the agent finished normally.
        truncated : dict[str, bool]
            Flags whether the agent was stopped by env.
        info : dict[str, dict]
            Forwarded from BlueFixedActionWrapper.

        [한국어]
        환경에서 한 스텝(step)을 진행한다.

        인자:
            action_dict : dict[str, int | Action]
                각 에이전트에 대응하는 행동(Action) 또는 행동 인덱스.
                인덱스는 `actions(k)[v]`에 해당하는 방식으로 CybORG 행동에 매핑된다.
                각 행동의 의미는 `action_labels(k)[v]`로 확인할 수 있다.
            messages : dict[str, Any]
                각 에이전트가 보내는 메시지. 메시지를 지정하지 않은 에이전트는 빈
                메시지를 보낸다.
            **kwargs : dict[str, Any]
                그 외 키워드 인자는 그대로 전달된다.

        반환값
        -------
        observation : dict[str, np.ndarray]
            각 에이전트의 관찰값을 벡터 형태로 담은 것.
        rewards : dict[str, float]
            각 에이전트의 보상.
        terminated : dict[str, bool]
            에이전트가 정상적으로 종료되었는지를 나타내는 플래그.
        truncated : dict[str, bool]
            에이전트가 환경에 의해 중단되었는지를 나타내는 플래그.
        info : dict[str, dict]
            BlueFixedActionWrapper에서 그대로 전달된 정보.
        """
        observations, rewards, terminated, truncated, info = super().step(
            actions=actions, messages=messages, **kwargs
        )

        # [설명] super().step()이 돌려준 관찰값 딕셔너리에서 Blue 에이전트만
        # 골라, 각 관찰값을 고정 크기·고정 순서의 벡터로 변환한다.
        # sorted()로 에이전트 순서를 고정해 실행마다 결과가 일관되게 한다.
        observations = {
            agent: self.observation_change(agent, obs)
            for agent, obs in sorted(observations.items())
            if "blue" in agent
        }
        return observations, rewards, terminated, truncated, info

    def _get_init_obs_spaces(self):
        """Calculates the size of the largest observation space for each agent.

        [한국어]
        각 에이전트가 가질 수 있는 가장 큰 관찰 공간(Observation Space)의 크기를
        계산한다.
        """
        # [설명] 각 항목은 [관찰 벡터 한 구획의 카테고리 수]를 모은 것이다.
        # 예: NUM_SUBNETS * [2]는 "서브넷 개수만큼의, 값이 0/1(2가지)인 칸"을 뜻한다.
        # MultiDiscrete 공간을 만들 때 각 칸의 선택지 개수로 쓰인다.
        observation_space_components = {
            "mission": [3],
            "blocked_subnets": NUM_SUBNETS * [2],
            "comms_policy": NUM_SUBNETS * [2],
            "malicious_processes": MAX_HOSTS * [2],
            "network_connections": MAX_HOSTS * [2],
            "subnet": NUM_SUBNETS * [2],
            "messages": (NUM_MESSAGES * MESSAGE_LENGTH) * [2],
        }

        # [설명] 관찰 벡터는 [머리(mission) + 중간(subnet 관련) + 꼬리(messages)]
        # 순으로 이어 붙인다. 중간 구획(middle)은 mission/messages를 제외한 나머지
        # 항목들을 하나로 펼친 것이다.
        observation_head = observation_space_components["mission"]
        observation_tail = observation_space_components["messages"]
        observation_middle = list(
            itertools.chain(
                *[
                    v
                    for k, v in observation_space_components.items()
                    if k not in ("mission", "messages")
                ]
            )
        )

        # [설명] short는 중간 구획을 1번, long은 NUM_HQ_SUBNETS배만큼 반복한다.
        # 본부(HQ) 에이전트(blue_agent_4)나 패딩이 켜진 경우 long 공간을 쓴다.
        short_observation_components = (
            observation_head + observation_middle + observation_tail
        )

        long_observation_components = (
            observation_head + (NUM_HQ_SUBNETS * observation_middle) + observation_tail
        )

        short_observation_space = spaces.MultiDiscrete(short_observation_components)
        long_observation_space = spaces.MultiDiscrete(long_observation_components)

        self._observation_space = {
            agent: long_observation_space
            if self.is_padded or agent == "blue_agent_4"
            else short_observation_space
            for agent in self.agents
        }

        return short_observation_space, long_observation_space

    def observation_change(self, agent_name: str, observation: dict) -> np.ndarray:
        """Converts an observation dictionary to a vector of fixed size and ordering.

        Parameters
        ----------
        agent_name : str
            Agent corresponding to the observation.
        observation : dict
            Observation to convert to a fixed vector.

        Returns
        -------
        output : np.ndarray

        [한국어]
        관찰값 딕셔너리를, 크기와 순서가 고정된 벡터로 변환한다.

        매개변수
        ----------
        agent_name : str
            해당 관찰값에 대응하는 에이전트.
        observation : dict
            고정 길이 벡터로 변환할 관찰값.

        반환값
        -------
        output : np.ndarray
        """
        state = self.env.environment_controller.state

        proto_observation = []

        # Mission Phase
        # 임무 단계(미션 페이즈)
        mission_phase = state.mission_phase
        proto_observation.append(mission_phase)

        # Useful (sorted) information
        # 유용한 (정렬된) 정보
        # [설명] 서브넷 이름을 정렬해 두어, 매 실행마다 벡터 내 서브넷 순서가
        # 일정하도록 한다. 이름은 소문자로 통일한다.
        sorted_subnet_name_to_cidr = sorted(state.subnet_name_to_cidr.items())
        subnet_names, subnet_cidrs = zip(*sorted_subnet_name_to_cidr)
        subnet_names = [name.lower() for name in subnet_names]
        hosts = self.hosts(agent_name)

        for subnet in self.subnets(agent_name):
            # One-hot encoded subnet vector
            # 현재 서브넷을 가리키는 원-핫(one-hot) 벡터 (해당 서브넷만 1)
            subnet_subvector = [subnet == name for name in subnet_names]

            # Get blocklist
            # 차단 목록(blocklist) 조회: 이 서브넷이 차단한 서브넷들을 1로 표시
            blocked_subnets = state.blocks.get(subnet, [])
            blocked_subvector = [s in blocked_subnets for s in subnet_names]

            # Comms
            # 통신 정책(comms policy)
            # [설명] 임무 단계별 통신 허용 그래프를 인접행렬로 만든 뒤, 현재 서브넷
            # 행을 꺼낸다. logical_not으로 뒤집어 "통신이 막힌 곳"을 1로 표현한다.
            comms_policy = self.comms_policies[state.mission_phase]
            comms_matrix = nx.to_numpy_array(comms_policy, nodelist=subnet_names)
            comms_policy_subvector = comms_matrix[subnet_names.index(subnet)]
            comms_policy_subvector = np.logical_not(comms_policy_subvector)
            self.policy[agent_name] = comms_policy

            # Process malware events for users, then servers
            # 사용자 호스트, 이어서 서버 호스트의 악성 이벤트를 처리한다.
            # 라우터는 제외하고, 이 서브넷에 속한 호스트만 추린다.
            subnet_hosts = [h for h in hosts if subnet in h and "router" not in h]

            # 각 호스트에 의심스러운 프로세스 이벤트가 하나라도 있으면 1
            process_subvector = [
                h in state.hosts and 0 < len(self._get_procesess(state, h))
                for h in subnet_hosts
            ]

            # 각 호스트에 네트워크 연결 이벤트가 하나라도 있으면 1
            connection_subvector = [
                h in state.hosts and 0 < len(self._get_connections(state, h))
                for h in subnet_hosts
            ]

            proto_observation.extend(
                itertools.chain(
                    subnet_subvector,
                    blocked_subvector,
                    comms_policy_subvector,
                    process_subvector,
                    connection_subvector,
                )
            )

        output = np.array(proto_observation, dtype=np.int64)

        # Messages from other agents
        # This assumes CybORG provides a consistent ordering.
        # 다른 에이전트들로부터 온 메시지.
        # CybORG가 일관된 순서로 메시지를 제공한다고 가정한다.
        messages = observation.get("message", [EMPTY_MESSAGE] * NUM_MESSAGES)
        assert len(messages) == NUM_MESSAGES

        message_subvector = np.concatenate(messages)
        assert len(message_subvector) == NUM_MESSAGES * MESSAGE_LENGTH

        output = np.concatenate([output, message_subvector])

        # Apply padding as required
        # [설명] 패딩이 켜져 있으면, 짧은 관찰 벡터를 long 관찰 공간 길이에 맞춰
        # 뒤를 0으로 채운다. 그래야 모든 에이전트의 벡터 길이가 같아진다.
        if self.is_padded:
            output = np.pad(
                output, (0, self._long_obs_space.shape[0] - output.shape[0])
            )

        return output

    def _build_comms_policy(self):
        # [설명] 임무 단계(Preplanning/MissionA/MissionB)별로 서브넷 간 통신 허용
        # 그래프를 만들어, {단계 인덱스: 그래프} 형태의 딕셔너리로 돌려준다.
        policy_dict = {}
        mission_phases = ["Preplanning", "MissionA", "MissionB"]
        for mission in mission_phases:
            network = self._build_comms_policy_network(mission)
            index = mission_phases.index(mission)
            policy_dict[index] = network
        return policy_dict

    def _build_comms_policy_network(self, mission: str):
        # [설명] 기본은 주요 서브넷들이 서로 모두 연결된 완전 그래프(complete graph)다.
        # 여기에 제한 구역(restricted)–운영 구역(operational) 연결을 추가한 뒤,
        # 임무 단계(MissionA/MissionB)에 따라 일부 연결을 끊어 통신을 제한한다.
        hosts = (
            "internet_subnet",
            "admin_network_subnet",
            "office_network_subnet",
            "public_access_zone_subnet",
            "contractor_network_subnet",
            "restricted_zone_a_subnet",
            "restricted_zone_b_subnet",
        )

        # 정수 노드로 된 완전 그래프를 만든 뒤, 노드 이름을 서브넷 이름으로 바꾼다.
        network = nx.complete_graph(len(hosts))
        node_mapping = dict(enumerate(hosts))
        network = nx.relabel_nodes(network, node_mapping)

        # 제한 구역과 그에 대응하는 운영 구역 사이의 연결을 추가한다.
        network.add_edges_from((
            ("restricted_zone_a_subnet", "operational_zone_a_subnet"),
            ("restricted_zone_b_subnet", "operational_zone_b_subnet"),
        ))

        # MissionA에서는 제한 구역 A의 외부 연결을 끊어 격리한다.
        if mission == "MissionA":
            network.remove_edges_from((
                ("restricted_zone_a_subnet", "operational_zone_a_subnet"),
                ("restricted_zone_a_subnet", "contractor_network_subnet"),
                ("restricted_zone_a_subnet", "restricted_zone_b_subnet"),
                ("restricted_zone_a_subnet", "internet_subnet"),
            ))
        # MissionB에서는 제한 구역 B의 외부 연결을 끊어 격리한다.
        elif mission == "MissionB":
            network.remove_edges_from((
                ("restricted_zone_b_subnet", "operational_zone_b_subnet"),
                ("restricted_zone_b_subnet", "contractor_network_subnet"),
                ("restricted_zone_b_subnet", "restricted_zone_a_subnet"),
                ("restricted_zone_b_subnet", "internet_subnet"),
            ))

        return network

    def _get_procesess(self, state: State, hostname: str):
        # [설명] 해당 호스트의 프로세스 생성 이벤트를 모아 돌려준다.
        # 이미 관찰된(old) 이벤트와 아직 관찰되지 않은 이벤트를 합친다.
        observed_proc_events = state.hosts[hostname].events.old_process_creation
        unobserved_proc_events = state.hosts[hostname].events.process_creation
        return observed_proc_events + unobserved_proc_events

    def _get_connections(self, state: State, hostname: str):
        # [설명] 해당 호스트의 네트워크 연결 이벤트를 모아 돌려준다.
        # 이미 관찰된(old) 연결과 아직 관찰되지 않은 연결을 합친다.
        observed_conn_events = state.hosts[hostname].events.old_network_connections
        unobserved_conn_events = state.hosts[hostname].events.network_connections
        return observed_conn_events + unobserved_conn_events

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent_name: str) -> Space:
        """Returns the multi-discrete space corresponding to the given agent.

        [한국어]
        주어진 에이전트에 대응하는 MultiDiscrete 관찰 공간을 돌려준다.
        """
        return self._observation_space[agent_name]

    @functools.lru_cache(maxsize=None)
    def observation_spaces(self) -> dict[str, Space]:
        """Returns multi-discrete spaces corresponding to each agent.

        [한국어]
        각 에이전트에 대응하는 MultiDiscrete 관찰 공간들을 딕셔너리로 돌려준다.
        """
        return {a: self.observation_space(a) for a in self.possible_agents}
