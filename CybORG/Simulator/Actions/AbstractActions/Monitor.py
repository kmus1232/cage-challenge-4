from copy import deepcopy

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Shared.Session import VelociraptorServer
from CybORG.Simulator.State import State


class Monitor(Action):
    """ Collects events on hosts and informs Blue Agent.

    This action runs automatically at the end of each step. If a Blue agent calls it will have no effect. Host events are cleared from the host after this action runs.

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action

    [한국어]
    호스트에서 발생한 이벤트를 수집해 Blue 에이전트에게 전달하는 Monitor(모니터링) 행동(Action).

    이 행동은 매 스텝(step)이 끝날 때 자동으로 실행된다. Blue 에이전트가 직접
    호출하더라도 효과가 없다. 이 행동이 실행된 뒤에는 호스트의 이벤트가 비워진다.

    속성
    - session: 세션 id
    - agent: 이 행동을 실행하는 에이전트의 이름
    """
    def __init__(self, session: int, agent: str):
        """ Instantiates Monitor class.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action

        [한국어]
        Monitor 클래스를 생성한다.

        매개변수
        - session: 세션 id
        - agent: 이 행동을 실행하는 에이전트의 이름
        """
        super().__init__()
        self.agent = agent
        self.session = session

    def execute(self, state: State) -> Observation:
        """ Executes the Monitor Action
        Parameters
        ----------
        state: State
            The current state of CybORG.

        Returns
        -------
        obs: Observation
            The observation to be returned to the Blue Agent.
            Consists of events collected from all hosts the agent has access to.
            Events are limited to Network Connection events and Process Creation events.

        [한국어]
        Monitor 행동(Action)을 실행한다.

        매개변수
        - state: 현재 CybORG의 상태(State).

        반환값
        - obs: Blue 에이전트에게 돌려줄 관찰값(Observation).
          에이전트가 접근 가능한 모든 호스트에서 수집한 이벤트로 구성된다.
          이벤트는 네트워크 연결(Network Connection) 이벤트와
          프로세스 생성(Process Creation) 이벤트로 한정된다.
        """
        obs = Observation(True)
        session: VelociraptorServer = state.sessions[self.agent][self.session]
        # [설명] Blue 에이전트의 메인 세션과 그 하위(child) 세션들을 모두 모은다.
        # 모니터링 대상은 이 세션들이 올라가 있는 호스트 전체다.
        blue_sessions = [child for child in session.children.values()] + [session]

        for child in blue_sessions:
            host = state.hosts[child.hostname]
            # 네트워크 연결 이벤트 수집
            network_connections = host.events.network_connections
            if len(network_connections) > 0:
                obs.add_system_info(hostid=child.hostname, **host.get_state())
            for event in network_connections:
                # [설명] 이벤트에 pid가 있으면 의심 프로세스(sus pid)로 세션에 기록한다.
                # 이후 Analyse/Remove 등 후속 방어 행동의 판단 근거가 된다.
                if event.pid:
                    session.add_sus_pids(hostname=child.hostname, pid=event.pid)
                obs.add_process(hostid=child.hostname, **vars(event))
            # [설명] 처리한 이벤트는 old_*에 깊은 복사로 보관한 뒤 원본을 비운다.
            # 따라서 같은 이벤트가 다음 스텝(step)에 중복 보고되지 않는다.
            host.events.old_network_connections = deepcopy(network_connections)
            network_connections.clear()

            # 프로세스 생성 이벤트 수집 (위 네트워크 연결과 동일한 흐름)
            processes = host.events.process_creation
            if len(processes) > 0:
                obs.add_system_info(hostid=child.hostname, **state.hosts[child.hostname].get_state())
            for event in processes:
                # pid가 있으면 의심 프로세스로 기록한다.
                if 'pid' in event:
                    session.add_sus_pids(hostname=child.hostname, pid=event['pid'])
                obs.add_process(hostid=child.hostname, **event)
            host.events.old_process_creation = deepcopy(processes)
            processes.clear()
        return obs

    def __str__(self):
        return f"{self.__class__.__name__}"
