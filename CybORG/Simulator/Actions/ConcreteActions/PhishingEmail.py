from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.State import State

class PhishingEmail(RemoteAction):
    """ The green agent action that represents the green agent 'opening a malicious email' from a red agent.

    The action creates a new red shell session on the Host that the green agent has a session on. This gives the red agent a foothold on that system.
    The red agent that gets the shell session should be located in the same subnet as the green agent.

    Attributes:
        ip_address (IPv4Address): IP address of the host that the green agent has a session on

    [한국어]
    Green 에이전트가 Red 에이전트의 '악성 이메일을 여는' 행위(Action)를 나타내는 Green 에이전트 행동.

    이 행동은 Green 에이전트가 세션을 가진 호스트에 새로운 Red 셸 세션을 생성한다. 이로써 Red 에이전트는
    그 시스템에 발판(foothold)을 확보한다.
    셸 세션을 얻는 Red 에이전트는 Green 에이전트와 같은 서브넷에 위치해야 한다.

    Attributes:
        ip_address (IPv4Address): Green 에이전트가 세션을 가진 호스트의 IP 주소
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """ Initalisation of PhishingEmail attributes

        Args:
            session (int): session id
            agent (str): agent name
            ip_address (IPv4Address): host IP address

        [한국어]
        PhishingEmail 속성 초기화.

        Args:
            session (int): 세션 id
            agent (str): 에이전트 이름
            ip_address (IPv4Address): 호스트 IP 주소
        """
        super().__init__(session=session, agent=agent)
        self.ip_address = ip_address

    def execute(self, state: State) -> Observation:
        """ Execute PhishingEmail action

        Args:
            state (State): current simulation State
        
        Returns:
            obs (Observation): the resulting observation space due to the action performed

        [한국어]
        PhishingEmail 행동을 실행한다.

        Args:
            state (State): 현재 시뮬레이션 State

        Returns:
            obs (Observation): 수행된 행동의 결과로 나온 관찰값(Observation) 공간
        """
        obs = Observation()
        self._create_new_session(obs, state)
        return obs
    
    def _create_new_session(self, obs: Observation, state: State) -> Observation:
        """ Creates a new red shell session on the green host object.

        Process:
            1) The green host name is discovered from the ip_address
            2) Check if a red shell session is already present on the green host
                - if so, finish action as host already 'infected'
            3) Find the red agent that is present in the green host's subnet and check routable
                - if not present, pick another routable subnet
                    - if none, return failed observation
            4) Create a new session on the green host, of the chosen red agent
            5) Add the session details to the successful Observation object and return

        Args:
            obs (Observation): a new Observation object
            state (State): current simulation state

        Returns:
            obs (Observation): the changed Observation object, due to the action occurrance

        [한국어]
        Green 호스트 객체에 새로운 Red 셸 세션을 생성한다.

        처리 절차:
            1) ip_address로부터 Green 호스트 이름을 찾는다
            2) Green 호스트에 이미 Red 셸 세션이 있는지 확인한다
                - 있으면 호스트가 이미 '감염'된 상태이므로 행동을 종료한다
            3) Green 호스트의 서브넷에 있는 Red 에이전트를 찾고 라우팅 가능 여부를 확인한다
                - 없으면 라우팅 가능한 다른 서브넷을 고른다
                    - 그래도 없으면 실패 관찰값(Observation)을 반환한다
            4) 선택된 Red 에이전트의 세션을 Green 호스트에 새로 생성한다
            5) 성공 Observation 객체에 세션 정보를 추가하고 반환한다

        Args:
            obs (Observation): 새 Observation 객체
            state (State): 현재 시뮬레이션 상태

        Returns:
            obs (Observation): 행동 발생으로 변경된 Observation 객체
        """

        red_agent_src = ""
        red_agents = []

        green_hostname = state.ip_addresses[self.ip_address]

        # Check if red already on host
        # Red가 이미 호스트에 있는지 확인한다
        for agent, sid in state.hosts[green_hostname].sessions.items():
            if not sid == [] and 'red' in agent:
                return obs.set_success(True)

        # Get red agent that 'sent' the phishing email
        # 피싱 이메일을 '보낸' Red 에이전트를 찾는다
        for hostname, host in state.hosts.items():
            for agentname, sid in host.sessions.items():
                if not sid == [] and 'red' in agentname:
                    is_routable = self.check_routable(state, green_hostname, hostname)
                    if self.ip_address in host.interfaces[0].subnet and is_routable:
                        red_agent_src = agentname
                        break
                    red_agents.append((agentname, hostname))

        while red_agent_src == "":
            if red_agents == []:
                self.log("No red_agents are routable to green host.")
                return obs.set_success(False)

            r_agent = state.np_random.choice(red_agents, replace=False)

            if self.check_routable(state=state, target=green_hostname, source=r_agent[1]):
                red_agent_src = r_agent[0]
            

        # New red shell session created
        # 새로운 Red 셸 세션을 생성한다
        new_session = RedAbstractSession(
            ident=None,
            pid=None,
            hostname=green_hostname,
            username='user',
            agent=red_agent_src,
            parent=None,
            session_type='RedAbstractSession'
        )
        state.add_session(new_session)
        session_info = {
            'hostid': green_hostname,
            'session_id': new_session.ident,
            'session_type': new_session.session_type,
            'agent': new_session.agent}
        
        # Add the session details to the successful Observation object
        # 성공한 Observation 객체에 세션 세부 정보를 추가한다
        obs.add_session_info(**session_info)
        return obs.set_success(True)
