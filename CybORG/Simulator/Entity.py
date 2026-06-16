# Copyright DST Group. Licensed under the MIT license.


class Entity:
    """An abstract base class with the empty methods `__init__` and `get_state`, to be overwritten by child classes.

    [한국어]
    `__init__`과 `get_state`가 비어 있는 추상 베이스 클래스다.
    자식 클래스에서 이 메서드들을 오버라이드한다.
    """
    def __init__(self):
        pass

    def get_state(self):
        pass
