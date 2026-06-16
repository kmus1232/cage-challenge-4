from CybORG.Agents import BaseAgent
from CybORG.Shared.ActionSpace import ActionSpace
from CybORG.Simulator.Actions import Sleep, Action
from CybORG.Simulator.Actions.GreenActions import GreenAccessService, GreenLocalWork
from ipaddress import IPv4Address
from CybORG.Shared import Observation

class EnterpriseGreenAgent(BaseAgent):
    """ Green Agent to be used for the Enterprise scenario (CC4).

    Attributes
    ----------
    own_ip : IPv4Address
        ip address of the host the green agent is located on
    fp_detection_rate : float
        the decimal rate at which a blue detection false positive occurs from the green action (0 <= value <= 1)
    phishing_error_rate : float
        the decimal rate at which a phishing email subaction occurs due to a green action (0 <= value <= 1)

    [한국어]
    엔터프라이즈 시나리오(CC4)에서 사용하는 Green 에이전트(정상 사용자)다.

    속성(Attributes)
    - own_ip : IPv4Address
        이 Green 에이전트가 위치한 호스트의 IP 주소.
    - fp_detection_rate : float
        Green 행동(Action)이 Blue 측의 탐지 오탐(false positive)을 유발하는 비율
        (0 이상 1 이하의 소수).
    - phishing_error_rate : float
        Green 행동으로 인해 피싱 이메일 하위 행동(subaction)이 발생하는 비율
        (0 이상 1 이하의 소수).
    """
    def __init__(self, name: str, own_ip: IPv4Address, np_random = None, fp_detection_rate: float = 0.01, phishing_error_rate: float = 0.01):
        """ Initialisation of the EnterpriseGreenAgent class.

        Parameters
        ----------
        name : str
            name of the agent (form of unique id)
        own_ip : IPv4Address
            ip address of the host the agent is located on
        fp_detection_rate : float
            the decimal rate at which a blue detection false positive occurs from the green action (0 <= value <= 1)
        phishing_error_rate : float
            the decimal rate at which a phishing email subaction occurs due to a green action (0 <= value <= 1)

        [한국어]
        EnterpriseGreenAgent 클래스의 초기화 메서드다.

        매개변수(Parameters)
        - name : str
            에이전트 이름(고유 식별자 역할).
        - own_ip : IPv4Address
            이 에이전트가 위치한 호스트의 IP 주소.
        - fp_detection_rate : float
            Green 행동이 Blue 측 탐지 오탐(false positive)을 유발하는 비율
            (0 이상 1 이하의 소수).
        - phishing_error_rate : float
            Green 행동으로 인해 피싱 이메일 하위 행동이 발생하는 비율
            (0 이상 1 이하의 소수).
        """
        super().__init__(name=name, np_random=np_random)
        self.own_ip = own_ip
        self.fp_detection_rate = fp_detection_rate
        self.phishing_error_rate = phishing_error_rate
        
    def train(self):
        pass

    def get_action(self, observation: Observation, action_space: dict) -> Action:
        """ Returns one of the 3 possible actions of the green agent in CC4

        The 3 possible actions are: GreenLocalWork, GreenAccessService, and Sleep. The action is chosen at random from this list.

        Parameters
        ----------
        observation : Observation
            current observation of the state
        action_space : ActionSpace
            the action space of the agent at the current step

        Returns
        -------
        Action
            One of the 3 listed actions, where each inherit from base class Action

        [한국어]
        CC4에서 Green 에이전트가 취할 수 있는 3가지 행동(Action) 중 하나를 반환한다.

        3가지 행동은 GreenLocalWork, GreenAccessService, Sleep이며, 이 목록에서
        무작위로 하나를 고른다.

        매개변수(Parameters)
        - observation : Observation
            현재 상태의 관찰값(Observation).
        - action_space : ActionSpace
            현재 스텝(step)에서의 에이전트 행동 공간(Action Space).

        반환값(Returns)
        - Action
            위 3가지 중 하나의 행동. 셋 다 기반 클래스 Action을 상속한다.
        """
        # 행동 공간에 담긴 행동 클래스 목록을 꺼낸다.
        actions = list(action_space['action'].keys())
        # 그중 하나를 무작위로 선택한다.
        action = self.np_random.choice(actions)

        if action == GreenAccessService:
            return GreenAccessService(
                agent=self.name,
                src_ip = self.own_ip,
                allowed_subnets=action_space['allowed_subnets'],
                session_id=0,
                fp_detection_rate = self.fp_detection_rate
            )
        if action == GreenLocalWork:
            return GreenLocalWork(
                agent=self.name,
                session_id=0,
                ip_address = self.own_ip,
                fp_detection_rate = self.fp_detection_rate,
                phishing_error_rate = self.phishing_error_rate
            )
        return Sleep()

    def end_episode(self):
        # [설명] 에피소드가 끝나면 __init__을 다시 호출해 에이전트 상태를 초기값으로 되돌린다.
        # name/own_ip/np_random은 유지하고, fp_detection_rate·phishing_error_rate는 기본값으로 리셋된다.
        self.__init__(name=self.name, own_ip=self.own_ip, np_random=self.np_random)

    def set_initial_values(self, action_space: ActionSpace, observation: Observation):
        pass

