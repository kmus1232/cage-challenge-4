# Copyright DST Group. Licensed under the MIT license.

import pprint
from copy import deepcopy

from CybORG.Shared.Observation import Observation


class Results:
    """ Results class that is returned after each step

    Only the observation attribute is used in CC4.

    Attributes
    ----------
    observation : Dict[str, _]
        observation data for the scenario host network

    [한국어]
    매 스텝(step)마다 환경이 반환하는 결과 클래스.
    CC4(CAGE Challenge 4)에서는 observation 속성만 실제로 사용한다.

    Attributes(속성)
    - observation: Dict[str, _]
        시나리오의 호스트 네트워크에 대한 관찰값(Observation) 데이터
    """

    def __init__(self,
                 observation: dict = None,
                 done: bool = None,
                 reward: float = None,
                 info=None,
                 parameter_mask=None,
                 action_space=None,
                 error: Exception = None,
                 error_msg: str = None,
                 next_observation=None,
                 action=None,
                 action_name: str = None):
        """

        Parameters
        ----------
        observation: Dict[str, _]
            observation data for the scenario host network
        done: bool
        reward: float
        info
        parameter_mask
        action_space
        error : Exception
            contains any exception produced by the environment
        error_msg : str
            error message for the exception
        next_observation : Dict[str, _]
        action
        action_name: str

        [한국어]
        Parameters(매개변수)
        - observation: Dict[str, _]
            시나리오의 호스트 네트워크에 대한 관찰값(Observation) 데이터
        - done: bool — 에피소드(Episode) 종료 여부
        - reward: float — 해당 스텝의 보상
        - info — 부가 정보
        - parameter_mask — 행동(Action) 매개변수 마스크
        - action_space — 행동 공간(Action Space)
        - error: Exception — 환경이 발생시킨 예외(있을 경우)
        - error_msg: str — 예외에 대한 에러 메시지
        - next_observation: Dict[str, _] — 다음 스텝의 관찰값
        - action — 수행된 행동(Action)
        - action_name: str — 행동의 이름
        """
        self.observation = observation
        self.next_observation = next_observation
        self.done = done
        self.reward = reward
        self.action = action
        self.info = info
        self.parameter_mask = parameter_mask
        self.action_space = action_space
        self.error = error
        self.error_msg = error_msg
        self.action_name = action_name
        self.selection_masks = None

    def has_error(self):
        """Return class attribute `error`

        [한국어]
        error 속성이 존재하는지(None이 아닌지) 여부를 반환한다.
        """
        return self.error is not None

    def copy(self):
        """Return a new instance of Results with the same class attributes.

        Returns
        -------
        : Results
            a duplicate Results object

        [한국어]
        같은 속성값을 가진 새로운 Results 인스턴스를 반환한다.

        observation/next_observation이 Observation 객체이면 해당 객체의
        copy()로 복사하고, 그 외 타입이면 deepcopy로 깊은 복사한다.
        """
        copy_kwargs = {
            "done": self.done,
            "reward": self.reward,
            "error": deepcopy(self.error),
            "error_msg": deepcopy(self.error_msg),
            "action": deepcopy(self.action),
            "info": deepcopy(self.info),
            "action_space": deepcopy(self.action_space)
        }

        if isinstance(self.observation, Observation):
            copy_kwargs["observation"] = self.observation.copy()
        else:
            copy_kwargs["observation"] = deepcopy(self.observation)

        if isinstance(self.next_observation, Observation):
            copy_kwargs["next_observation"] = self.next_observation.copy()
        else:
            copy_kwargs["next_observation"] = deepcopy(self.next_observation)

        return Results(**copy_kwargs)

    def __str__(self):
        output = [f"{self.__class__.__name__}:"]
        for attr, v in self.__dict__.items():
            if v is None:
                continue
            if isinstance(v, dict):
                v_str = pprint.pformat(v)
            else:
                v_str = str(v)
            output.append(f"{attr}={v_str}")
        return "\n".join(output)

    def __eq__(self, other):
        # [설명] 같은 타입이 아니면 다른 객체로 간주한다.
        if not isinstance(other, type(self)):
            return False

        # [설명] 모든 속성을 키별로 비교해 하나라도 다르면 False를 반환한다.
        for k, v in self.__dict__.items():
            if k not in other.__dict__:
                return False
            if v != other.__dict__[k]:
                return False
        return True
