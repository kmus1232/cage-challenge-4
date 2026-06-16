# Copyright DST Group. Licensed under the MIT license.
from CybORG.Simulator.Actions.Action import Action
from CybORG.Shared.Observation import Observation


class ActionHandler:
    """Abstract interface for handling actions in CybORG.

    [한국어]
    CybORG에서 행동(Action)을 처리하는 추상 인터페이스(기반 클래스)다.
    실제 처리 로직은 이 클래스를 상속한 하위 클래스가 구현한다.
    """

    def __init__(self):
        pass

    def perform(self, action: Action) -> Observation:
        """Execute the given action and return the resulting observation.

        [한국어]
        주어진 행동(Action)을 실행하고 그 결과인 관찰값(Observation)을 반환한다.
        이 기반 클래스에서는 구현이 없으며, 하위 클래스에서 반드시 재정의해야 한다.
        """
        # [설명] 기반 클래스에는 구현이 없음을 알리는 표시.
        #        하위 클래스가 perform을 재정의하지 않으면 NotImplementedError가 발생한다.
        raise NotImplementedError
