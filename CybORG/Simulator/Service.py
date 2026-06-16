# Copyright DST Group. Licensed under the MIT license.
from CybORG.Simulator.Entity import Entity

class Service(Entity):
    """Class for services used in CybORG simulations

    Attributes
    ----------
    process : int
    active : bool
    session : Session
    percent_reliable : int

    [한국어]
    CybORG 시뮬레이션에서 사용하는 서비스(Service)를 표현하는 클래스.

    속성:
    - process : 이 서비스를 구동하는 프로세스의 PID(정수)
    - active : 서비스 활성화 여부(불리언)
    - session : 이 서비스와 연결된 세션(Session)
    - percent_reliable : 서비스 신뢰도 백분율(정수)
    """
    def __init__(self, process: int, active = True, session = None):
        super().__init__()
        self.process = process
        self.active = active
        self.session = session
        self._percent_reliable = 100

    def get_state(self) -> dict:
        """Returns the contents of the class

        [한국어]
        클래스의 현재 상태(프로세스, 활성화 여부, 세션, 신뢰도)를 딕셔너리로 반환한다.
        """
        return {
            'process': self.process,
            'active': self.active,
            'session': self.session,
            'reliability (%)': self._percent_reliable
        }
    
    def get_service_reliability(self):
        return self._percent_reliable

    def degrade_service_reliability(self, value: int = 20):
        """Degrades/decreases the service's reliability percent by the value given.

        [한국어]
        서비스의 신뢰도 백분율을 주어진 value만큼 낮춘다. 0 미만으로 내려가면 0으로 고정한다.
        """
        new_reliability = self._percent_reliable - value

        if new_reliability >= 0:
            self._percent_reliable = new_reliability
        else:
            self._percent_reliable = 0
    
    @classmethod
    def load(cls, info: dict):
        """Class loader

        [한국어]
        info 딕셔너리에서 PID·active·session 값을 꺼내 Service 인스턴스를 생성하는 로더.
        """
        return cls(
            process=info.get('PID'),
            active=info.get('active', True),
            session=info.get('session', None)
        )
    
    def __str__(self):
        active_str = 'active' if self.active else 'inactive'
        return f'Process {self.process}: {active_str}, {self._percent_reliable}% reliable'
