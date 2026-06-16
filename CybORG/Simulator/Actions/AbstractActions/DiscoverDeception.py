from CybORG.Shared import Observation
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.State import State
from ipaddress import IPv4Address

class DiscoverDeception(RemoteAction):
    """ A Red action that probes a remote host to see if it is running any decoy services. 

    Attributes
    ----------
    session : int
        The source session id.
    agent : str
        The name of the red agent executing the action.
    ip_address : IPv4Address
        The ip_address of the target host.
    target_hostname : str
        The name of the target host. 
    duration : int
        This action takes 2 steps to complete, instead of the default 1.
    detection_rate : float
        The True Positive rate of the red agent to accurately detect whether the host is running a decoy service. A True Positive Rate only includes True Positives and False Negatives.
    fp_rate : float
        The False Positive rate of the red agent to incorrectly detect a normal service as a decoy. Defaults to 10%.

    [한국어]
    원격 호스트를 탐색해 그 호스트가 Decoy(디코이, 미끼) 서비스를 돌리고 있는지
    확인하는 Red 에이전트의 행동(Action)이다.

    속성(Attributes)
    - session : int — 출발지 세션 id.
    - agent : str — 이 행동을 수행하는 Red 에이전트 이름.
    - ip_address : IPv4Address — 대상 호스트의 IP 주소.
    - target_hostname : str — 대상 호스트 이름.
    - duration : int — 기본 1스텝이 아니라 완료까지 2스텝이 걸린다.
    - detection_rate : float — 호스트가 디코이 서비스를 돌리는지 정확히 탐지하는
      Red 에이전트의 True Positive(참 양성) 비율. 참 양성과 거짓 음성만 포함한다.
    - fp_rate : float — 정상 서비스를 디코이로 잘못 탐지하는 False Positive(거짓 양성)
      비율. 기본값 10%.
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """
        Parameters
        ----------
        session : int
            The source session id.
        agent : str
            The name of the red agent executing the action.
        ip_address : IPv4Address
            The ip_address of the target host.

        [한국어]
        매개변수(Parameters)
        - session : int — 출발지 세션 id.
        - agent : str — 이 행동을 수행하는 Red 에이전트 이름.
        - ip_address : IPv4Address — 대상 호스트의 IP 주소.
        """
        super().__init__(session, agent)
        self.ip_address = ip_address
        self.duration = 2
        self.detection_rate = 0.5
        self.fp_rate = 0.1
        self.target_hostname = None
    
    def execute(self, state: State) -> Observation:
        """
        Probes the target host for decoy services.

        Action process:  
        1) Check if there are sessions for the agent on this host\n
        - if not, return unsuccessful obs\n
        2) Get the route between the source and target/remote host\n
        - if there is not a valid route (None), return unsuccessful obs\n
        3) Given that there is a valid route, connect to the remote host\n
        - iterate over all processes on the remote host\n
        - after a detection_rate attribute check (defaults to 50%), add the process to the obs if it passes\n
        - return a successful obs regardless of whether a decoy was found\n

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False, and any detected decoy processes.

        [한국어]
        대상 호스트에 디코이 서비스가 있는지 탐색한다.

        행동 처리 순서:
        1) 이 호스트에 해당 에이전트의 세션이 있는지 확인한다.
           - 없으면 실패 관찰값(obs)을 반환한다.
        2) 출발지 호스트와 대상(원격) 호스트 사이의 경로(route)를 구한다.
           - 유효한 경로가 없으면(None) 실패 관찰값을 반환한다.
        3) 유효한 경로가 있으면 원격 호스트에 연결한다.
           - 원격 호스트의 모든 프로세스를 순회한다.
           - detection_rate(기본 50%) 판정을 통과한 프로세스만 관찰값에 추가한다.
           - 디코이를 찾았는지 여부와 무관하게 성공 관찰값을 반환한다.

        매개변수(Parameters)
        - state : State — 현재 스텝의 시뮬레이션 네트워크 상태.

        반환값(Returns)
        - obs : Observation — 행동의 성공 여부(True/False)와 탐지된 디코이 프로세스를
          담은 관찰값(Observation).
        """
        obs = Observation(False)
        # (1) check the session exists for this agent
        # (1) 이 에이전트의 세션이 존재하는지 확인한다
        if self.session not in state.sessions[self.agent]:
            self.log(f"Session '{self.session}' not found for agent '{self.agent}'.")
            return obs
        
        # (2) get the route between the source and target/remote host
        # (2) 출발지 호스트와 대상(원격) 호스트 사이의 경로를 구한다
        source_hostname = state.sessions[self.agent][self.session].hostname
        self.target_hostname = state.ip_addresses[self.ip_address]
        # can we connect to from the source to target host
        # 출발지에서 대상 호스트로 연결할 수 있는지 확인한다
        route = self.get_route(state, target=self.target_hostname, source=source_hostname)
        if route is None:
            self.log("No route found.")
            return obs
        # (3) observation is set to true, even if no decoy is detected
        # (3) 디코이를 탐지하지 못해도 관찰값의 성공 여부는 True로 설정한다
        obs.set_success(True)
        # (a) obtain the list of processes running on the target host
        # (a) 대상 호스트에서 실행 중인 프로세스 목록을 가져온다
        processes = state.hosts[self.target_hostname].processes
        for process in processes:
            # (b) we only detect decoys if detection_rate is lower than random float
            # can result in false negatives or positive as every process has the 'decoy' property added
            # (b) 난수가 detection_rate 이하일 때만 디코이로 탐지한다
            # 모든 프로세스에 'decoy' 속성이 붙으므로 거짓 음성/거짓 양성이 생길 수 있다
            # [설명] 두 분기는 디코이 탐지의 확률 모델이다. 첫 분기는 실제 디코이
            # (decoy_type.name == 'EXPLOIT')를 detection_rate(참 양성률) 확률로 잡아내고,
            # 아래 elif는 정상 프로세스를 fp_rate(거짓 양성률) 확률로 디코이로 오탐한다.
            # 두 경우 모두 process.properties에 'decoy'를 덧붙여 관찰값에 추가한다.
            if state.np_random.random() <= self.detection_rate and process.decoy_type.name == 'EXPLOIT':
                obs.add_process(hostid=self.target_hostname, pid=process.pid,
                    parent_pid=process.ppid, name=process.name,
                    username=process.user, service_name=process.name,
                    properties=process.properties + ['decoy',])
                obs.add_interface_info(hostid=self.target_hostname, ip_address=self.ip_address)
            # 정상 프로세스를 fp_rate 확률로 디코이로 오탐하는 분기(거짓 양성)
            elif state.np_random.random() <= self.fp_rate and process.decoy_type.name != 'EXPLOIT':
                obs.add_process(hostid=self.target_hostname, pid=process.pid,
                    parent_pid=process.ppid, name=process.name,
                    username=process.user, service_name=process.name,
                    properties=process.properties + ['decoy',])
                obs.add_interface_info(hostid=self.target_hostname, ip_address=self.ip_address)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.target_hostname}"
