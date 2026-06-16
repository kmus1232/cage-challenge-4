from CybORG.Simulator.Actions.ConcreteActions.LocalAction import LocalAction
from CybORG.Simulator.Actions.ConcreteActions.PhishingEmail import PhishingEmail
from CybORG.Simulator.State import State, Session, Host
from CybORG.Shared import Observation
from ipaddress import IPv4Address

class GreenLocalWork(LocalAction):
    """An action for Green agents to do 'local work' on the host.
    
    Consists of 3 parts: 

    1. Create a new process to represent user activity.

    2. A low probability the work creates a false positive for Blue - fp_detection_rate

    3. A low probability the work is from a phishing email, creating a red session - phishing_error_rate

    Attributes
    ----------
    ip_address : IPv4Address
        the ip address of the host which the local work is happening on
    fp_detection_rate : float
        the decimal probability that a false positive is created for blue (0.0 <= value <= 1.0)
    phishing_error_rate : float
        the decimal probability that a PhishingEmail action is performed as a subaction (0.0 <= value <= 1.0)

    [한국어]
    Green 에이전트(정상 사용자)가 호스트에서 '로컬 작업'을 수행하는 행동(Action).

    다음 3가지 부분으로 구성된다:

    1. 사용자 활동을 나타내는 새 프로세스를 생성한다.
    2. 낮은 확률로 이 작업이 Blue 측에 오탐(false positive)을 발생시킨다 - fp_detection_rate.
    3. 낮은 확률로 이 작업이 피싱 이메일에서 비롯되어 Red 세션을 생성한다 - phishing_error_rate.

    속성(Attributes)
    ----------
    ip_address : IPv4Address
        로컬 작업이 일어나는 호스트의 IP 주소.
    fp_detection_rate : float
        Blue 측에 오탐이 생길 소수 확률 (0.0 <= 값 <= 1.0).
    phishing_error_rate : float
        하위 행동으로 PhishingEmail이 수행될 소수 확률 (0.0 <= 값 <= 1.0).
    """
    def __init__(self, agent: str, session_id: int, ip_address: IPv4Address, fp_detection_rate = 0.01, phishing_error_rate = 0.01):
        """Initialisation of GreenLocalWork by setting class attributes.

        Parameters
        ----------
        agent : str 
            name of agent performing action
        session_id : int
            State session id on the host
        ip_address : IPv4Address
            ip address of the host
        fp_detection_rate : float, optional
            decimal probability that a false positive is created for blue (0.0 <= value <= 1.0, default = 0.01)
        phishing_error_rate : float, optional
            decimal probability that a PhishingEmail action is performed as a subaction (0.0 <= value <= 1.0, default = 0.01)

        Raises
        ------
        ValueError
            decimal probability value is not between 0.0 and 1.0 (inclusive)

        [한국어]
        클래스 속성을 설정해 GreenLocalWork를 초기화한다.

        매개변수(Parameters)
        ----------
        agent : str
            행동을 수행하는 에이전트 이름.
        session_id : int
            호스트상의 State 세션 id.
        ip_address : IPv4Address
            호스트의 IP 주소.
        fp_detection_rate : float, optional
            Blue 측에 오탐이 생길 소수 확률 (0.0 <= 값 <= 1.0, 기본값 = 0.01).
        phishing_error_rate : float, optional
            하위 행동으로 PhishingEmail이 수행될 소수 확률 (0.0 <= 값 <= 1.0, 기본값 = 0.01).

        예외(Raises)
        ------
        ValueError
            소수 확률 값이 0.0 이상 1.0 이하 범위를 벗어나는 경우.
        """

        super().__init__(agent=agent, session=session_id)
        self.ip_address = ip_address

        # Input validation check
        # 입력값 검증: 두 확률은 모두 0.0~1.0 범위여야 한다.
        if not (0.0 <= fp_detection_rate <= 1.0):
            raise ValueError("GreenLocalWork: fp_detection_rate must be a value equal or between 0 and 1")
        self.fp_detection_rate = fp_detection_rate
        if not (0.0 <= phishing_error_rate <= 1.0):
            raise ValueError("GreenLocalWork: phishing_error_rate must be a value equal or between 0 and 1")
        self.phishing_error_rate = phishing_error_rate

    def execute(self, state: State) -> Observation:
        """ Executes the functionality of the action on the state and produces a resulting observation.

        The action execution consists of 3 parts:

        1. User trys to access local service
            - User attempts to access a service local to the host, that may have had its reliability degraded by red.
            - If no services exist on host, action also fails

        2. False alert
            - There is a small chance (1% by default) that the process will create a false positive alert for a Velociraptor Client from Blues agents action.
        
        3. User error
            - low probability the local work is malicious by accident, causing a sub action PhishingEmail.
            - if <1% by default, then this will add a session for the red agent

        Parameters
        ----------
        state : State 
            state of simulation at current step
        
        Returns
        -------
        obs : Observation
            the observation produced by the action, with the success or failure of the action set within the object.

        [한국어]
        state에 대해 행동의 기능을 실행하고 그 결과인 관찰값(Observation)을 만든다.

        행동 실행은 다음 3가지 부분으로 구성된다:

        1. 사용자가 로컬 서비스 접근을 시도한다.
            - 사용자가 호스트에 로컬한 서비스에 접근을 시도한다. 해당 서비스는
              Red에 의해 신뢰성이 저하되었을 수 있다.
            - 호스트에 서비스가 하나도 없으면 행동은 실패한다.

        2. 오탐(false alert).
            - 낮은 확률(기본 1%)로 이 프로세스가 Blue 에이전트가 보는
              Velociraptor 클라이언트의 오탐 경보를 발생시킨다.

        3. 사용자 실수(user error).
            - 낮은 확률로 로컬 작업이 의도치 않게 악성이 되어, 하위 행동인
              PhishingEmail을 유발한다.
            - 기본값 기준 1% 미만이며, 이 경우 Red 에이전트에 세션을 추가한다.

        매개변수(Parameters)
        ----------
        state : State
            현재 스텝(step)에서의 시뮬레이션 상태.

        반환값(Returns)
        -------
        obs : Observation
            행동이 만들어낸 관찰값. 행동의 성공/실패 여부가 객체 안에 설정된다.
        """
        obs = Observation()

        if self.session not in state.sessions[self.agent]:
            self.log("Session does not exist in the state.")
            obs.set_success(False)
            return obs
             
        obs.set_success(True)
        session = state.sessions[self.agent][self.session]
        hostname = session.hostname
        host = state.hosts[hostname]

        # 1. User trys to access local service
        # 1. 사용자가 로컬 서비스 접근을 시도한다.
        available_host_services = [service for service in host.services.values() if service.active]
        if len(available_host_services) > 0:
            service_to_use = state.np_random.choice(available_host_services)
            # [설명] 0~99 난수를 뽑아 서비스 신뢰성 값보다 크거나 같으면 접근 실패로 처리한다.
            #        즉 신뢰성이 낮을수록(=값이 작을수록) 실패 확률이 높아진다.
            if state.np_random.integers(100) >= service_to_use.get_service_reliability():
                # service is too unreliable, so local work fails
                # 서비스 신뢰성이 너무 낮아 로컬 작업이 실패한다.
                obs.set_success(False)
                return obs
        else:
            # no services available, so local work fails
            # 사용 가능한 서비스가 없어 로컬 작업이 실패한다.
            obs.set_success(False)
            return obs

        # 2.FALSE ALERT
        # 2. 오탐(false alert).
        # [설명] fp_detection_rate 확률로만 분기에 진입한다. 진입 시 임시 포트로
        #        프로세스 생성 이벤트를 남겨 Blue 측에 오탐 경보를 만든다.
        if state.np_random.random() < self.fp_detection_rate:
            host_port = host.get_ephemeral_port()
            pc = {'local_address': self.ip_address, 'local_port': host_port}
            host.events.process_creation.append(pc)

        # 3.USER ERROR
        # 3. 사용자 실수(user error).
        # [설명] phishing_error_rate 확률로 하위 행동 PhishingEmail을 실행하고,
        #        그 관찰값을 현재 관찰값에 합친다(combine_obs).
        if state.np_random.random() < self.phishing_error_rate:
            sub_action = PhishingEmail(
                agent=self.agent, session=self.session, ip_address=self.ip_address
            )
            sub_obs = sub_action.execute(state)
            obs.combine_obs(sub_obs)

        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.ip_address}"
