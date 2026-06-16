from CybORG.Shared import Observation
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.Actions.ConcreteActions.StopProcess import StopProcess
from CybORG.Simulator.State import State
from ipaddress import IPv4Address

class Withdraw(RemoteAction):
    """ A red action that removes all the agent's sessions from a local or remote host.

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the red agent executing the action. Used within RemoteAction.
    hostname: str
        The name of the target host.

    [한국어]
    로컬 또는 원격 호스트에서 해당 에이전트의 모든 세션을 제거하는 Red 에이전트(공격 측)의 행동(Action).
    Withdraw(철수)는 공격자가 점거했던 호스트에서 자신의 흔적(세션)을 거두어들이는 동작이다.

    Attributes
    ----------
    session: int
        출발 세션 id.
    agent: str
        이 행동을 실행하는 Red 에이전트의 이름.
    ip_address: IPv4Address
        이 행동을 실행하는 Red 에이전트의 ip_address. RemoteAction 내부에서 사용된다.
    hostname: str
        대상(target) 호스트의 이름.
    """
    def __init__(self, session: int, agent: str, ip_address:IPv4Address, hostname: str):
        """
        Parameters
        ----------
        session: int
            The source session id.
        agent: int
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the red agent executing the action. Used within RemoteAction.
        hostname: str
            The name of the target host.

        [한국어]
        Parameters
        ----------
        session: int
            출발 세션 id.
        agent: int
            이 행동을 실행하는 Red 에이전트의 이름.
        ip_address: IPv4Address
            이 행동을 실행하는 Red 에이전트의 ip_address. RemoteAction 내부에서 사용된다.
        hostname: str
            대상(target) 호스트의 이름.
        """
        super().__init__(session, agent)
        self.hostname = hostname
        self.ip_address = ip_address
    
    def execute(self, state: State) -> Observation:
        """
        Removes all the agent's sessions from the target host.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.

        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False.

        [한국어]
        대상(target) 호스트에서 해당 에이전트의 모든 세션을 제거한다.

        Parameters
        ----------
        state: State
            현재 스텝(step)에서 시뮬레이션 네트워크의 상태(State).

        Returns
        -------
        obs: Observation
            행동이 성공적으로 실행됐는지를 True/False로 나타내는 관찰값(Observation).
        """
        session = state.sessions[self.agent].get(self.session, None)
        if not session:
            self.log(f"Session '{self.session}' not found for agent '{self.agent}'.")
            return Observation(False)

        # can we connect to from the source to target host
        # 출발 호스트에서 대상 호스트로 연결할 수 있는지 확인한다
        route = self.get_route(state, target=self.hostname, source=session.hostname)
        if route is None:
            self.log(f"No route found from '{session.hostname}' to '{self.hostname}'")
            return Observation(False)
        
        # find relevant sessions on the chosen host
        # 선택한 호스트에서 관련 세션들을 찾는다
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        child_sessions = [s for s in sessions if s.parent!=None]
        parent_sessions = [s for s in sessions if s.parent==None and s.ident!=0]
        
        # reorder the sessions to have the parent session last
        # 부모(parent) 세션이 맨 뒤에 오도록 세션 순서를 재정렬한다
        all_agents_sessions = child_sessions + parent_sessions
        if state.sessions[self.agent][self.session].hostname==self.hostname:
            all_agents_sessions.append(state.sessions[self.agent][self.session])
        if not all_agents_sessions:
            self.log(f"No relevant sessions found for '{self.hostname}'.")
            return Observation(False)
        
        # iterate over child sessions first before eventually removing the parent process last
        # 자식(child) 세션을 먼저 순회하고, 부모 프로세스는 맨 마지막에 제거한다
        for remove_session in all_agents_sessions:
            # remove all the agents processes and sessions on a host (user/ priviledged)
            # 호스트에서 해당 에이전트의 모든 프로세스와 세션을 제거한다 (user/권한 있는 사용자 모두)
            action = StopProcess(
                session=self.session,
                agent=self.agent,
                target_session=remove_session.ident,
                pid=remove_session.pid,
                stop_all=True
            )
            obs = action.execute(state)
            # if any sub-action returns False then break
            # 하위 행동(sub-action) 중 하나라도 False를 반환하면 중단한다
            if obs.success==False:
                self.log("Failed to stop process.")
                return obs
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
