from typing import List

from CybORG.Shared import Observation

class ObservationSet:
    """Collection of Observation objects

    Attributes
    ----------
    observations: List[Observation]
        list of Observation objects

    [한국어]
    여러 개의 관찰값(Observation) 객체를 모아 담는 컬렉션 클래스.

    Attributes
    ----------
    observations: List[Observation]
        관찰값(Observation) 객체들의 리스트
    """
    def __init__(self, observations: List[Observation]):
        """
        Parameters
        ----------
        observations: List[Observation]
            initial list of observations

        [한국어]
        Parameters
        ----------
        observations: List[Observation]
            초기 관찰값 리스트
        """
        self.observations: List[Observation] = observations
    
    def get_combined_observation(self) -> Observation:
        """Returns the observations as a single Observation or ObservationSet depending on size.

        [한국어]
        보유한 여러 관찰값(Observation)을 하나의 관찰값으로 합쳐 반환한다.
        리스트가 비어 있으면 빈 관찰값을, 1개면 그 관찰값을 그대로 돌려준다.
        """
        if len(self.observations) == 0:
            return Observation()
        # 첫 관찰값을 기준(누적 대상)으로 삼는다.
        combined_observation = self.observations[0]
        if len(self.observations) > 1:
            # [설명] 둘째 관찰값부터 차례로 첫 관찰값에 누적 병합한다.
            # combine_obs는 combined_observation을 제자리(in-place)에서 갱신하므로
            # 별도 누적 변수를 두지 않고 첫 원소에 직접 합친다.
            for observation in self.observations[1:]:
                combined_observation.combine_obs(observation)
        return combined_observation

    def append(self, observation):
        """Adds an observation to it's observations attribute list.

        [한국어]
        관찰값(Observation)을 observations 속성 리스트에 추가한다.
        """
        self.observations.append(observation)
