

from CybORG.Agents import BaseAgent
from CybORG.Shared import Scenario
from CybORG.Shared.RewardCalculator import RewardCalculator


class ScenarioGenerator:
    """The ScenarioGenerator class is an abstract class that defines the interface for other ScenarioGenerator classes.

    Attributes
    ----------
    update_each_step : bool
        default True
    background_image : str
        path for render image, default None

    [한국어]
    다른 시나리오 생성기(Scenario Generator) 클래스들이 따라야 할 인터페이스를
    정의하는 추상 클래스다. 직접 인스턴스로 쓰기보다, 이를 상속한 하위 클래스가
    실제 시나리오 생성 로직을 구현한다.

    속성
    ----
    update_each_step : bool
        매 스텝(step)마다 상태를 갱신할지 여부. 기본값 True.
    background_image : str
        렌더링에 쓸 이미지 경로. 기본값 None.
    """

    def __init__(self):
        self.update_each_step = True
        self.background_image = None

    def create_scenario(self, np_random) -> Scenario:
        """Creates a scenario object that can be used to initialise the state

        Raises
        ------
        NotImplementedError
            Abstract method that should be implemented by child classes

        [한국어]
        환경 상태(state) 초기화에 사용할 시나리오(Scenario) 객체를 생성한다.

        예외
        ----
        NotImplementedError
            하위 클래스가 반드시 구현해야 하는 추상 메서드다. 베이스 클래스에서
            직접 호출하면 이 예외가 발생한다.
        """
        raise NotImplementedError

    def determine_done(self, env_controller):
        return False

    def validate_scenario(self, scenario: Scenario):
        """Takes in a scenario object and raises errors if the scenario is misconfigured or missing important information

        Parameters
        ----------
        scenario : Scenario
            scenario to be validated

        Raises
        ------
        ValueError
            CybORG does not currently support multiple types of interfaces on a single host
        AssertionError
            Scenario validation assertions

        [한국어]
        시나리오(Scenario) 객체를 받아 설정이 잘못되었거나 핵심 정보가 빠졌으면
        오류를 발생시킨다. 환경을 띄우기 전에 시나리오 무결성을 검증하는 용도다.

        매개변수
        --------
        scenario : Scenario
            검증할 시나리오.

        예외
        ----
        ValueError
            CybORG는 한 호스트에 여러 종류의 인터페이스(유선/무선 등)를 동시에
            두는 것을 아직 지원하지 않는다.
        AssertionError
            시나리오 검증 단언(assert)이 실패한 경우.
        """
        # check that all agents are assigned to a team
        # 모든 에이전트가 팀에 배정되어 있는지 확인한다.
        for name, data in scenario.agents.items():
            # 에이전트에 팀이 지정되어 있고, 그 팀이 시나리오에 실제 존재해야 한다.
            assert data.team is not None
            assert data.team in scenario.get_teams()
            # 에이전트 이름이 해당 팀의 에이전트 목록에 포함되어 있어야 한다.
            assert name in scenario.get_team_info(data.team)['agents']
            # 팀의 보상 계산기(RewardCalculator)들이 모두 올바른 타입인지 확인한다.
            for calc in scenario.get_team_info(data.team)['calcs'].values():
                assert issubclass(type(calc), RewardCalculator)
            # 에이전트 타입이 BaseAgent를 상속하는지 확인한다.
            assert issubclass(type(data.agent_type), BaseAgent), f"agent: {name}, type {data.agent_type}"

        for host in scenario.hosts.values():
            # cannot have both wired and wireless interfaces currently because movement away from wireless will disconnect wired as well
            # [설명] 한 호스트는 유선·무선 인터페이스를 섞어 가질 수 없다. 무선에서
            # 이동(연결 해제)하면 유선까지 함께 끊기는 현재 구현 한계 때문이다.
            # 아래 루프는 호스트의 첫 인터페이스 타입을 기준으로 잡고, 이후
            # 인터페이스 타입이 하나라도 다르면 ValueError를 던진다.
            interface_type = None
            for interface in host.interfaces:
                if interface_type is None:
                    interface_type = interface.interface_type
                elif interface_type != interface.interface_type:
                    raise ValueError('CybORG does not currently support multiple types of interfaces on a single host')

    def __str__(self):
        return "BaseScenarioGenerator"
