from __future__ import annotations
from gymnasium import Space, spaces

from CybORG import CybORG
from CybORG.Agents.Wrappers import BaseWrapper
from CybORG.Simulator.Actions import Action, Sleep
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import (
    EnterpriseScenarioGenerator,
)

import functools
import numpy as np
from typing import Any

SUBNET_USER_FORMAT = "{subnet}_user_host_{host}"
SUBNET_SERVER_FORMAT = "{subnet}_server_host_{host}"
SUBNET_ROUTER_FORMAT = "{subnet}_router"

NUM_MESSAGES = 4
MESSAGE_LENGTH = 8
EMPTY_MESSAGE = np.zeros(MESSAGE_LENGTH, dtype=bool)

DISABLE_SANITY_CHECKS = True


class BlueFixedActionWrapper(BaseWrapper):
    """Maintains action spaces with fixed sizes and ordering across episodes.

    On initialization, this wrapper creates a *sorted* list of all the hosts
    and subnets each agent can interact with in the CC4 EnterpriseScenario.

    On reset, the action space is populated using these sorted lists,
    translating hostnames to IP addresses where needed, such that any
    given action index will always correspond to a specific host. If
    a host does not exist in the current episode, the action will be
    replaced with a no-op (Sleep) action. Agents can check whether an
    action corresponds to an active host by consulting action_mask().

    Note: This wrapper does not change the observation space. See the
    companion wrapper `BlueFlatWrapper` for vector observations of
    fixed length and order.

    [한국어]
    Blue 에이전트의 행동 공간(Action Space)을 에피소드 사이에서 크기와 순서가
    고정되도록 유지하는 래퍼(Wrapper)다.

    초기화 시 CC4 EnterpriseScenario에서 각 에이전트가 다룰 수 있는 모든 호스트와
    서브넷을 **정렬된** 목록으로 만든다.

    reset 시 이 정렬된 목록으로 행동 공간을 채우며, 필요하면 호스트 이름을 IP
    주소로 변환한다. 덕분에 특정 행동 인덱스는 항상 같은 호스트를 가리킨다. 현재
    에피소드에 존재하지 않는 호스트를 가리키는 행동은 아무 동작도 하지 않는
    no-op(Sleep) 행동으로 대체된다. 에이전트는 action_mask()로 어떤 행동이 실제
    존재하는 호스트를 가리키는지 확인할 수 있다.

    참고: 이 래퍼는 관찰값(Observation) 공간은 바꾸지 않는다. 길이와 순서가
    고정된 벡터 관찰값이 필요하면 짝이 되는 래퍼 `BlueFlatWrapper`를 참고한다.
    """

    def __init__(self, env: CybORG, pad_spaces: bool = False, *args, **kwargs):
        """Initialize the BlueFixedActionWrapper for blue agents.

        Parameters
        ----------
        env : CybORG
            An instance of CybORG. Must not modify action_space.
        pad_spaces : bool
            Ensure all observation and action spaces are the same size across all agents by padding the space with the Sleep action.
            This is a requirement for some RL libraries.
        *args, **kwargs
            Extra arguments are ignored.

        [한국어]
        Blue 에이전트용 BlueFixedActionWrapper를 초기화한다.

        매개변수
        - env : CybORG 인스턴스. action_space를 수정해서는 안 된다.
        - pad_spaces : bool. True면 모든 에이전트의 관찰값/행동 공간 크기를 같게
          맞추려고 Sleep 행동으로 빈자리를 채운다(padding). 일부 강화학습(RL)
          라이브러리가 동일 크기를 요구하기 때문에 필요하다.
        - *args, **kwargs : 나머지 인자는 무시된다.
        """
        super().__init__(env)

        # Filter out non-blue da ba dee da ba di
        # 이름에 "blue"가 들어간 에이전트만 남긴다(Blue 에이전트 = 방어 측).
        self.agents = self.possible_agents = [a for a in env.agents if "blue" in a]

        # Variables to track max space sizes for padding
        # padding 계산에 쓸 최대 행동 공간 크기를 추적하는 변수들
        self._pad_spaces = pad_spaces
        self._max_act_space_size = 0

        # Maintain a **sorted** record of subnets and hosts to ensure consistency
        # 일관성을 위해 서브넷과 호스트를 **정렬된** 형태로 보관한다.
        self._agent_metadata = {}
        self._action_space = {}

        for agent in self.agents:
            self._create_hardcoded_metadata(agent)
            self._populate_action_space(agent)
        self._host_sanity_check()
        self._apply_padding()

    def reset(self, *args, **kwargs) -> tuple[dict[str, Any], dict[str, dict]]:
        """Reset the environment and update the action space.

        Parameters: All arguments are forwarded to the env provided to __init__.

        Returns
        -------
        observation : dict[str, Any]
            The observations corresponding to each agent. Forwarded directly from the env provided to __init__.

        info : dict[str, dict]
            Information dictionaries corresponding to each agent.
            Each dictionary contains the key "action_mask" that maps to a list[bool] where each element corresponds to whether the action
            at the element's index targets a host or subnet that exists for the duration of the episode.

        [한국어]
        환경을 reset하고 행동 공간(Action Space)을 갱신한다.

        매개변수: 모든 인자는 __init__에 넘긴 env로 그대로 전달된다.

        반환값
        - observation : dict[str, Any]. 각 에이전트의 관찰값(Observation). env가
          돌려주는 값을 그대로 전달한다.
        - info : dict[str, dict]. 각 에이전트의 정보 딕셔너리. 각 딕셔너리는
          "action_mask" 키를 가지며, 값은 list[bool]이다. 각 원소는 그 인덱스의
          행동이 이번 에피소드 동안 존재하는 호스트/서브넷을 가리키는지 여부를
          나타낸다.
        """
        self.env.reset(*args, **kwargs)
        self.agents = self.possible_agents
        for agent in self.agents:
            self._populate_action_space(agent)
        self._host_sanity_check()
        self._apply_padding()
        observations = {a: self.env.get_observation(a) for a in self.agents}
        info = {a: {"action_mask": self._action_space[a]["mask"]} for a in self.agents}
        return observations, info

    def step(
        self,
        actions: dict[str, int | Action] = None,
        messages: dict[str, Any] = None,
        **kwargs,
    ) -> tuple[
        dict[str, Any],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        """Take a step in the enviroment using action indices.

        Parameters
        ----------
        actions : dict[str, int] 
            The action index corresponding to each agent. 
            These indices will be mapped to CybORG actions using the equivalent of `actions(agent)[index]`. 
            The meaning of each action can be found using `action_labels(agent)[index]`.
        messages : dict[str, Any]
            Messages from each agent. If an agent does not specify a message, it will send an empty message.
        **kwargs : dict[str, Any]
            Extra keywords are forwarded.

        Returns
        -------
        observation : dict[str, Any]
            The observations corresponding to each agent. 
            Forwarded directly from the env provided to __init__.
        rewards : dict[str, float]
            Rewards for each agent.
        terminated : dict[str, bool]
            Flags whether the agent finished normally.
        truncated : dict[str, bool]
            Flags whether the agent was stopped by env.
        info : dict[str, dict]
            Information dictionaries corresponding to each agent.
            Each dictionary contains the key "action_mask" that maps to a list[bool] where each element corresponds to whether the action
            at the element's index targets a host or subnet that exists for the duration of the episode.

        [한국어]
        행동 인덱스를 사용해 환경에서 한 스텝(step)을 진행한다.

        매개변수
        - actions : dict[str, int]. 각 에이전트의 행동 인덱스. 이 인덱스는
          `actions(agent)[index]`와 같은 방식으로 CybORG 행동(Action)에
          매핑된다. 각 행동의 의미는 `action_labels(agent)[index]`로 확인할 수
          있다.
        - messages : dict[str, Any]. 각 에이전트가 보내는 메시지. 메시지를
          지정하지 않은 에이전트는 빈 메시지를 보낸다.
        - **kwargs : dict[str, Any]. 나머지 키워드 인자는 그대로 전달된다.

        반환값
        - observation : dict[str, Any]. 각 에이전트의 관찰값(Observation). env가
          돌려주는 값을 그대로 전달한다.
        - rewards : dict[str, float]. 각 에이전트의 보상(Reward).
        - terminated : dict[str, bool]. 에이전트가 정상적으로 종료됐는지 여부.
        - truncated : dict[str, bool]. 에이전트가 env에 의해 중단됐는지 여부.
        - info : dict[str, dict]. 각 에이전트의 정보 딕셔너리. 각 딕셔너리는
          "action_mask" 키를 가지며, 값은 list[bool]이다. 각 원소는 그 인덱스의
          행동이 이번 에피소드 동안 존재하는 호스트/서브넷을 가리키는지 여부를
          나타낸다.
        """
        action_dict = {} if actions is None else actions
        # [설명] 이미 Action 객체로 들어온 값은 그대로 두고, 정수 인덱스로 들어온
        # 값은 해당 에이전트의 행동 공간에서 실제 Action 객체로 변환한다.
        action_dict = {
            agent: action
            if isinstance(action, Action)
            else self._action_space[agent]["actions"][action]
            for agent, action in action_dict.items()
        }

        messages = {} if messages is None else messages
        messages = {
            agent: messages.get(agent, EMPTY_MESSAGE).astype(bool)
            for agent in self.possible_agents
        }

        obs, rews, dones, info = self.env.parallel_step(
            action_dict, messages=messages, **kwargs
        )

        for agent_name in self.agents:
            if agent_name not in info:
                info[agent_name] = {}
            info[agent_name]["action_mask"] = self._action_space[agent_name]["mask"]

        self.agents = [
            agent for agent, done in dones.items() if "blue" in agent and not done
        ]

        observations = {agent: o for agent, o in obs.items() if "blue" in agent}

        rewards = {
            agent: sum(reward.values())
            for agent, reward in rews.items()
            if "blue" in agent
        }

        terminated = {agent: done for agent, done in dones.items() if "blue" in agent}
        truncated = {agent: done for agent, done in dones.items() if "blue" in agent}

        info = {
            a: {"action_mask": self._action_space[a]["mask"]}
            for a in self.possible_agents
        }

        return observations, rewards, terminated, truncated, info

    def _create_hardcoded_metadata(self, agent_name: str) -> None:
        """Identifies all hosts and subnets that the agent will ever encounter.

        The content and ordering of this list must be consistent across all
        runs, universally, as it is used to derive the full action space.

        [한국어]
        에이전트가 앞으로 마주칠 수 있는 모든 호스트와 서브넷을 식별한다.

        이 목록의 내용과 순서는 모든 실행에서 항상 동일해야 한다. 전체 행동
        공간(Action Space)을 이 목록에서 유도하기 때문이다.
        """
        state = self.env.environment_controller.state
        agent = state.scenario.agents[agent_name]

        subnets = set(agent.allowed_subnets)
        hosts = set()
        foreign_hosts = set()

        for subnet in agent.allowed_subnets:
            hosts.add(SUBNET_ROUTER_FORMAT.format(subnet=subnet))

            for i in range(EnterpriseScenarioGenerator.MAX_USER_HOSTS):
                hosts.add(SUBNET_USER_FORMAT.format(subnet=subnet, host=i))

            for i in range(EnterpriseScenarioGenerator.MAX_SERVER_HOSTS):
                hosts.add(SUBNET_SERVER_FORMAT.format(subnet=subnet, host=i))

            # Remove this condition if blue agents need to act on foreign hosts.
            # [설명] Blue 에이전트가 외부(foreign) 호스트에 행동해야 한다면 이
            # 조건을 제거한다. 현재는 Red 에이전트가 아니면 아래 처리를 건너뛴다.
            if "red" not in agent_name:
                continue

            for hostname in hosts:
                # Some hosts may not be currently active. However, these optional
                # hosts don't have any additional information, such as connections
                # to hosts on foreign subnets. This information is mostly for red.
                # 일부 호스트는 지금 활성 상태가 아닐 수 있다. 다만 이런 선택적
                # 호스트는 외부 서브넷 호스트와의 연결 같은 추가 정보가 없다. 이
                # 정보는 대체로 Red 에이전트용이다.
                if hostname not in state.scenario.hosts:
                    continue

                for foreign_hostname in state.scenario.hosts[hostname].info.keys():
                    foreign_hosts.add(foreign_hostname)

                    # Add foreign subnets to list of known subnets. This is probably
                    # unnecessary since red cannot act on foreign subnets directly.
                    # 외부 서브넷을 알려진 서브넷 목록에 추가한다. Red는 외부
                    # 서브넷에 직접 행동할 수 없으므로 사실상 불필요할 수 있다.
                    subnets.add(state.hostname_subnet_map[foreign_hostname].lower())

        hosts.update(foreign_hosts)
        self._agent_metadata[agent_name] = {
            "hosts": sorted(hosts),
            "subnets": sorted(subnets),
        }

    def _populate_action_space(self, agent_name: str) -> None:
        """Construct an agent's action space in a consistent order with labels and mask.

        [한국어]
        에이전트의 행동 공간(Action Space)을 일관된 순서로 구성하고, 사람이 읽을
        수 있는 라벨(labels)과 유효성 마스크(mask)를 함께 만든다.
        """
        state = self.env.environment_controller.state

        # This assumes that the commands will never change.
        # [설명] 사용 가능한 명령(command) 집합이 절대 바뀌지 않는다고 가정한다.
        commands = self.env.get_action_space(agent_name)["action"]
        commands = sorted(list(commands), key=str)

        # Default parameters for all actions except Sleep.
        # Sleep을 제외한 모든 행동에 공통으로 들어가는 기본 매개변수
        action_params = {"session": 0, "agent": agent_name}

        # This assumes that the existence of each subnet never changes.
        # 각 서브넷의 존재 여부가 절대 바뀌지 않는다고 가정한다.
        sorted_subnet_name_to_cidr = sorted(state.subnet_name_to_cidr.items())

        # Check if an agent has a session on a host. Host must exist.
        # [설명] 에이전트가 해당 호스트에 세션(Session)을 가지고 있는지 확인한다.
        # 호스트가 실제로 존재해야 한다.
        has_session = lambda h: 0 < len(state.hosts[h].sessions.get(agent_name, []))

        # Action space variables to populate. Order is important!
        # 채워 넣을 행동 공간 변수들. 순서가 중요하다!
        actions = []
        labels = []
        mask = []

        for command in commands:
            command_name = command.__name__

            if command_name == "Sleep":
                actions.append(command())
                labels.append("Sleep")
                mask.append(True)
                continue

            if command_name == "Monitor":
                actions.append(command(**action_params))
                labels.append("Monitor")
                mask.append(True)
                continue

            # [설명] 트래픽 허용/차단 명령은 (출발 서브넷, 도착 서브넷) 쌍마다
            # 하나씩 행동을 만든다. 출발지와 도착지가 같은 경우는 건너뛴다.
            if command_name in ("AllowTrafficZone", "BlockTrafficZone"):
                for dstname in self._agent_metadata[agent_name]["subnets"]:
                    dst = state.subnet_name_to_cidr[dstname]

                    for srcname, src in sorted_subnet_name_to_cidr:
                        srcname = srcname.lower()
                        if src == dst:
                            continue
                        actions.append(
                            command(from_subnet=srcname, to_subnet=dstname, **action_params)
                        )
                        labels.append(
                            f"{command_name} {dstname} ({dst}) <- {srcname} ({src})"
                        )
                        mask.append(True)
                continue

            # All other (host-based) commands.
            # 그 외의 모든 (호스트 단위) 명령을 처리한다.
            for hostname in self._agent_metadata[agent_name]["hosts"]:
                # Actions are disabled for router hosts.
                # 라우터 호스트에 대한 행동은 비활성화한다.
                if "router" in hostname:
                    continue

                # If the target host does not currently exist, use a no-op action.
                # [설명] 대상 호스트가 지금 존재하지 않거나 세션이 없으면, 인덱스
                # 정렬을 유지하기 위해 아무 동작도 하지 않는 no-op(Sleep)으로
                # 채우고 마스크를 False로 둔다.
                if hostname not in state.hosts or not has_session(hostname):
                    actions.append(Sleep())
                    labels.append(f"[Invalid] {command_name} {hostname}")
                    mask.append(False)
                    continue

                actions.append(command(hostname=hostname, **action_params))
                labels.append(f"{command_name} {hostname}")
                mask.append(True)

        self._max_act_space_size = max(self._max_act_space_size, len(actions))
        self._action_space[agent_name] = {
            "actions": actions,
            "labels": labels,
            "mask": mask,
        }

    def _apply_padding(self) -> None:
        """Pad all agent action spaces to match the size of the largest action space

        [한국어]
        모든 에이전트의 행동 공간(Action Space)을 가장 큰 행동 공간 크기에 맞춰
        Sleep(no-op)으로 빈자리를 채운다(padding).
        """
        if not self._pad_spaces:
            return

        def pad_actions(size, agent_name, key, value):
            self._action_space[agent_name][key].extend([value] * size)

        for agent_name in self.agents:
            space_size = len(self._action_space[agent_name]["actions"])
            pad_size = self._max_act_space_size - space_size

            if pad_size == 0:
                continue

            pad_actions(pad_size, agent_name, "actions", Sleep())
            pad_actions(pad_size, agent_name, "labels", "[Padding] Sleep")
            pad_actions(pad_size, agent_name, "mask", False)

    def _host_sanity_check(self) -> None:
        """Ensure hosts aren't missing from the wrapper's host list for each agent.

        [한국어]
        각 에이전트의 호스트 목록에서 누락된 호스트가 없는지 확인하는 점검 함수다.
        (DISABLE_SANITY_CHECKS가 True면 건너뛴다.)
        """
        if DISABLE_SANITY_CHECKS:
            return

        state = self.env.environment_controller.state
        for agent_name in self.agents:
            session_hosts = {s.hostname for s in state.sessions[agent_name].values()}
            assert session_hosts.issubset(self._agent_metadata[agent_name]["hosts"])

    def get_action_space(self, agent: str) -> dict[str, list[Action | str | bool]]:
        """Returns all information about an agent's action space.

        [한국어]
        에이전트의 행동 공간(Action Space)에 대한 모든 정보를 반환한다.
        """
        return self._action_space[agent]

    def hosts(self, agent_name: str) -> list[str]:
        """Returns an ordered list of names of hosts the agent can interact with.

        [한국어]
        에이전트가 다룰 수 있는 호스트 이름을 정렬된 순서로 반환한다.
        """
        return self._agent_metadata[agent_name]["hosts"]

    def subnets(self, agent_name: str) -> list[str]:
        """Returns an ordered list of names of subnets the agent can interact with.

        [한국어]
        에이전트가 다룰 수 있는 서브넷 이름을 정렬된 순서로 반환한다.
        """
        return self._agent_metadata[agent_name]["subnets"]

    def action_mask(self, agent_name: str) -> list[bool]:
        """Returns an ordered list corresponding to whether an action is valid or not.

        [한국어]
        각 행동이 유효한지(존재하는 호스트/서브넷을 가리키는지) 여부를 정렬된
        순서로 반환한다.
        """
        return self._action_space[agent_name]["mask"]

    def action_labels(self, agent_name: str) -> list[str]:
        """Returns an ordered list of human-readable actions.

        [한국어]
        사람이 읽을 수 있는 형태의 행동 라벨을 정렬된 순서로 반환한다.
        """
        return self._action_space[agent_name]["labels"]

    def actions(self, agent_name: str) -> list[Action]:
        """Returns an ordered list of CybORG actions.

        [한국어]
        CybORG 행동(Action) 객체를 정렬된 순서로 반환한다.
        """
        return self._action_space[agent_name]["actions"]

    @property
    def is_padded(self) -> bool:
        """Returns whether the action space has been padded with no-ops.

        [한국어]
        행동 공간(Action Space)이 no-op으로 padding되어 있는지 여부를 반환한다.
        """
        return self._pad_spaces

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent_name: str) -> Space:
        """Returns the discrete space corresponding to the given agent.

        [한국어]
        주어진 에이전트에 해당하는 이산(discrete) 행동 공간을 반환한다. padding이
        켜져 있으면 최대 크기로, 아니면 해당 에이전트의 실제 크기로 만든다.
        """
        if self._pad_spaces:
            return spaces.Discrete(self._max_act_space_size)
        return spaces.Discrete(len(self._action_space[agent_name]["actions"]))

    @functools.lru_cache(maxsize=None)
    def action_spaces(self) -> dict[str, Space]:
        """Returns discrete space with optional padding for each agent.

        [한국어]
        각 에이전트별 이산(discrete) 행동 공간을 (필요하면 padding을 적용해)
        딕셔너리로 반환한다.
        """
        return {a: self.action_space(a) for a in self.agents}
