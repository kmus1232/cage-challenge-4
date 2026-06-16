# The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
# Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

"""
Handling of privilege escalation action selection and execution

[한국어]
권한 상승(Privilege Escalate) 행동(Action)의 선택과 실행을 담당하는 모듈.
Red 에이전트가 이미 일반 사용자 셸을 확보한 호스트에서, root/SYSTEM 권한
셸로 격상하려는 시도를 처리한다.
"""
#pylint: disable=invalid-name

from typing import Tuple, Optional, List

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.EscalateActions.EscalateAction import (
        ExploreHost, EscalateAction
        )
from CybORG.Simulator.Actions.ConcreteActions.EscalateActions.JuicyPotato import JuicyPotato
from CybORG.Simulator.Actions.ConcreteActions.EscalateActions.V4L2KernelExploit import V4L2KernelExploit
from CybORG.Shared.Enums import (
    OperatingSystemType, TernaryEnum)
from CybORG.Simulator.State import State
from CybORG.Shared.Session import RedAbstractSession, Session

# pylint: disable=too-few-public-methods
class EscalateActionSelector:
    """
    Examines the target host and returns a selected applicable escalate action
    if any, as well as processes that are required to be genuine

    [한국어]
    대상 호스트를 조사해, 적용 가능한 권한 상승 하위 행동(escalate action)이 있으면
    선택해 반환한다. 함께 필요한(genuine) 프로세스 정보도 다룬다.
    이 클래스는 선택 전략의 추상 베이스이며, 실제 선택 로직은 하위 클래스가 구현한다.
    """
    # pylint: disable=missing-function-docstring
    def get_escalate_action(self, *, state: State, session: int, target_session: int,
            agent: str, hostname: str) -> \
                    Optional[EscalateAction]:
        raise NotImplementedError

class DefaultEscalateActionSelector(EscalateActionSelector):
    """
    Attempts to use Juicy Potato if windows, otherwise V4l2 kernel

    [한국어]
    대상 OS가 Windows면 Juicy Potato 익스플로잇을, 그 외(리눅스)면 V4L2 커널
    익스플로잇을 권한 상승 수단으로 선택하는 기본 선택기.
    """
    def get_escalate_action(self, *, state: State, session: int, target_session: int,
            agent: str, hostname: str) -> Optional[EscalateAction]:
        session_obj = state.sessions[agent].get(session)
        if session_obj is None:
            return
        # Red 에이전트의 추상 세션이 아니면 권한 상승 대상이 될 수 없다
        if not isinstance(session_obj, RedAbstractSession):
            return
        # [설명] OS 종류에 따라 사용할 익스플로잇이 갈린다: Windows면 Juicy Potato
        if session_obj.operating_system.get(hostname, None) == OperatingSystemType.WINDOWS:
            return JuicyPotato(session=session, target_session=target_session, agent=agent)
        # Windows가 아니면 리눅스로 보고 V4L2 커널 익스플로잇을 사용한다
        return V4L2KernelExploit(session=session, target_session=target_session, agent=agent)
_default_escalate_action_selector = DefaultEscalateActionSelector()


class PrivilegeEscalate(Action):
    """
    A Red action that attempts to conduct privilege escalation on a host that the agent has a user shell on, to gain a shell with root privileges.
    
    Attributes
    ----------
    hostname: str
        The name of the target host.
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    escalate_action_selector: EscalateActionSelector
        A selector that chooses an applicable escalate action for the target host, as well as required processes.

    [한국어]
    이미 사용자(user) 셸을 가진 호스트에서 root 권한 셸을 얻으려고 권한 상승을
    시도하는 Red 행동(Action).

    속성(Attributes)
    - hostname: 대상 호스트 이름
    - session: 출발(소스) 세션 id
    - agent: 이 행동을 실행하는 Red 에이전트 이름
    - escalate_action_selector: 대상 호스트에 적용할 권한 상승 하위 행동과 필요한
      프로세스를 골라주는 선택기(EscalateActionSelector)
    """
    def __init__(self, hostname: str, session: int, agent: str):
        """ Parameters
        ----------
        hostname: str
            The name of the target host.
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.

        [한국어]
        매개변수(Parameters)
        - hostname: 대상 호스트 이름
        - session: 출발(소스) 세션 id
        - agent: 이 행동을 실행하는 Red 에이전트 이름
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.escalate_action_selector = _default_escalate_action_selector
        self.duration=2  # 이 행동이 소요하는 스텝(step) 수
    

    def __perform_escalate(self, state:State, sessions:List[Session]) -> Tuple[Observation, int]:
        """ 
        Chooses a random session the agent has on the target host, and (if it is not in a sandbox) chooses and executes a privilege escalation action on that session.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        sessions: List[Session]
            A list of the sessions the red agent has on the target host.
        
        Returns
        -------
        : Observation
            An observation containing an indication of the action's successful execution as True/False.
        : int
            The target session's ident on the target host. This is -1 for an unsuccessful execution.

        [한국어]
        에이전트가 대상 호스트에 가진 세션 중 하나를 무작위로 고르고, 그 세션이
        샌드박스(sandbox, 격리 환경)가 아니면 권한 상승 하위 행동을 골라 실행한다.

        매개변수(Parameters)
        - state: 현재 스텝의 시뮬레이션 네트워크 상태
        - sessions: Red 에이전트가 대상 호스트에 가진 세션 목록

        반환(Returns)
        - Observation: 실행 성공 여부(True/False)를 담은 관찰값(Observation)
        - int: 대상 호스트에서의 대상 세션 ident. 실행 실패 시 -1
        """
        # 대상 호스트의 세션 중 하나를 무작위로 선택한다
        target_session = state.np_random.choice(sessions)

        #print(f"""
        #Host {self.hostname} attempting escalate:
        #Session {target_session.__dict__}""")

        # test if session is in a sandbox
        # [설명] 선택한 세션이 권한 상승 샌드박스(디코이/함정)면, 해당 프로세스를
        # 제거하고 실패를 반환한다. Blue가 깔아둔 미끼에 걸린 상황이다.
        if target_session.is_escalate_sandbox:
            state.remove_process(target_session.hostname, target_session.pid)
            return Observation(success=False), -1

        target_session_ident = target_session.ident

        sub_action = self.escalate_action_selector.get_escalate_action(
                state=state, session=self.session, target_session=target_session_ident,
                agent=self.agent, hostname=self.hostname)

        self.sub_action = sub_action

        if sub_action is None:
            return Observation(success=False), -1

        return sub_action.execute(state), target_session_ident

    def execute(self, state: State) -> Observation:
        """ 
        Attempts to privilege escalate a user shell on the target host to gain a root privileged shell.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False.

        [한국어]
        대상 호스트의 사용자 셸을 root 권한 셸로 격상하려고 시도한다.

        매개변수(Parameters)
        - state: 현재 스텝의 시뮬레이션 네트워크 상태

        반환(Returns)
        - obs: 실행 성공 여부(True/False)를 담은 관찰값(Observation)
        """
        # find session on the chosen host
        # 선택한 호스트 위에 있는 에이전트 세션들을 모은다
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            # no valid session could be found on chosen host
            # 선택한 호스트에서 유효한 세션을 찾지 못한 경우다
            return Observation(success=False)
        # find if any session are already SYSTEM or root
        # [설명] 이미 SYSTEM/root(권한 있는) 세션이 있으면 권한 상승을 새로 할 필요가
        # 없다. 그 세션을 그대로 대상으로 잡고 성공으로 처리한다.
        target_session = None
        obs = Observation(False)
        for sess in sessions:
            # else find if session is Admin or sudo
            # 세션이 Admin/sudo 등 권한 있는 접근을 가졌는지 확인한다
            if sess.has_privileged_access():
                target_session = sess.ident
                obs = Observation(success=True)
                obs.add_session_info(hostid=self.hostname, **sess.get_state())
                break
        # else use random session
        # 권한 있는 세션이 없으면, 무작위 세션을 골라 실제 권한 상승을 시도한다
        if target_session is None:
            obs, target_session = self.__perform_escalate(state, sessions)

        # 권한 상승이 성공하지 못했으면 여기서 관찰값을 반환하고 종료한다
        if obs.data['success'] is not TernaryEnum.TRUE:
            return obs

        # [설명] 권한 상승에 성공했으면, ExploreHost로 호스트를 탐색해 추가 정보를
        # 수집한다. 결과 프로세스 중 'OTService'(운영기술 서비스)가 있으면 세션에
        # 표시해 둔다. 이후 Impact 등 OT 대상 행동의 단서가 된다.
        sub_action = ExploreHost(session=self.session, target_session=target_session,
                agent=self.agent)
        obs2 = sub_action.execute(state)
        for host in obs2.data.values():
            try:
                host_processes = host['Processes']
                for proc in host_processes:
                    if proc.get('service_name') == 'OTService':
                        state.sessions[self.agent][self.session].ot_service = 'OTService'
                        break
            # 관찰값 딕셔너리에 기대한 키/타입이 없으면 그냥 건너뛴다
            except KeyError:
                pass
            except TypeError:
                pass

        # 권한 상승 관찰값과 호스트 탐색 관찰값을 합쳐서 반환한다
        obs.combine_obs(obs2)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name, 
            self.hostname == other.hostname,
            self.agent == other.agent,
            self.session == other.session,
        ))
