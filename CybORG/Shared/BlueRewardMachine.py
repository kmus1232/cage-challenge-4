
from CybORG.Shared.RewardCalculator import RewardCalculator
from CybORG.Simulator.State import State
from CybORG.Simulator.Actions.GreenActions import GreenAccessService, GreenLocalWork
from CybORG.Simulator.Actions.AbstractActions.Impact import Impact
from CybORG.Simulator.Actions.Action import InvalidAction

class BlueRewardMachine(RewardCalculator):
    """The reward calculator for CC4

    Attributes
    ----------
    phase_rewards : Dict[str, Dict[str, int]]
        the reward mapping for the current mission phase

    [한국어]
    CC4의 보상 계산기(RewardCalculator) 구현체.
    현재 미션 단계(mission phase)에 따라 서브넷별 보상 매핑을 적용해
    Blue 에이전트가 받을 보상을 산출한다.

    Attributes
    ----------
    phase_rewards : Dict[str, Dict[str, int]]
        현재 미션 단계에 대한 보상 매핑(서브넷 이름 -> 이벤트별 보상값).
    """

    def get_phase_rewards(self, cur_mission_phase):
        """Gets the pre-set reward mapping for the current mission phase

        Rewards Key:
        - LWF = Local Work Fails
        - ASF = Access Service Fails
        - RIA = Red Impact/Access

        Parameters
        ----------
        cur_mission_phase : int
            the current mission phase of the episode

        Returns
        -------
        : Dict[str, Dict[str, int]]
            the phase reward mapping for the current mission phase

        [한국어]
        현재 미션 단계에 대해 미리 정의된 보상 매핑을 반환한다.

        보상 키(Rewards Key):
        - LWF = Local Work Fails (Green 에이전트의 로컬 작업 실패)
        - ASF = Access Service Fails (Green 에이전트의 서비스 접근 실패)
        - RIA = Red Impact/Access (Red 에이전트의 Impact 성공 = 타격/침해)

        Parameters
        ----------
        cur_mission_phase : int
            현재 에피소드의 미션 단계(0/1/2).

        Returns
        -------
        : Dict[str, Dict[str, int]]
            해당 미션 단계의 서브넷별 보상 매핑.
        """
        # [설명] 미션 단계(0/1/2)별로 서브넷마다 LWF/ASF/RIA 보상값을 지정한 표.
        # 같은 서브넷이라도 단계에 따라 값이 달라지며(예: operational_zone은 해당
        # 단계에서 보호 우선순위가 높아지면 -10으로 강하게 페널티), 이는 단계별
        # 임무 중요도를 보상에 반영하기 위한 것이다.
        phase_rewards = {
            0:{
                "public_access_zone_subnet":    {"LWF": -1, "ASF": -1, "RIA": -3}, # Part of HQ Network in ReadMe  / ReadMe 기준 HQ 네트워크의 일부
                "admin_network_subnet":         {"LWF": -1, "ASF": -1, "RIA": -3}, # Part of HQ Network in ReadMe  / ReadMe 기준 HQ 네트워크의 일부
                "office_network_subnet":        {"LWF": -1, "ASF": -1, "RIA": -3}, # Part of HQ Network in ReadMe  / ReadMe 기준 HQ 네트워크의 일부
                "contractor_network_subnet":    {"LWF":  0, "ASF": -5, "RIA": -5},
                "restricted_zone_a_subnet":     {"LWF": -1, "ASF": -3, "RIA": -1},
                "operational_zone_a_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "restricted_zone_b_subnet":     {"LWF": -1, "ASF": -3, "RIA": -1},
                "operational_zone_b_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "internet_subnet":              {"LWF":  0, "ASF":  0, "RIA": -1}}, 
            1:{
                "public_access_zone_subnet":    {"LWF": -1, "ASF": -1, "RIA": -3},
                "admin_network_subnet":         {"LWF": -1, "ASF": -1, "RIA": -3},
                "office_network_subnet":        {"LWF": -1, "ASF": -1, "RIA": -3},
                "contractor_network_subnet":    {"LWF":  0, "ASF":  0, "RIA":  0},
                "restricted_zone_a_subnet":     {"LWF": -2, "ASF": -1, "RIA": -3},
                "operational_zone_a_subnet":    {"LWF":-10, "ASF":  0, "RIA":-10},
                "restricted_zone_b_subnet":     {"LWF": -1, "ASF": -1, "RIA": -1},
                "operational_zone_b_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "internet_subnet":              {"LWF":  0, "ASF":  0, "RIA": 0}}, 
            2:{
                "public_access_zone_subnet":    {"LWF": -1, "ASF": -1, "RIA": -3},
                "admin_network_subnet":         {"LWF": -1, "ASF": -1, "RIA": -3},
                "office_network_subnet":        {"LWF": -1, "ASF": -1, "RIA": -3},
                "contractor_network_subnet":    {"LWF":  0, "ASF":  0, "RIA":  0},
                "restricted_zone_a_subnet":     {"LWF": -1, "ASF": -3, "RIA": -3},
                "operational_zone_a_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "restricted_zone_b_subnet":     {"LWF": -2, "ASF": -1, "RIA": -3},
                "operational_zone_b_subnet":    {"LWF":-10, "ASF":  0, "RIA":-10},
                "internet_subnet":              {"LWF":  0, "ASF":  0, "RIA":  0}}}
        
        return phase_rewards[cur_mission_phase]


    def calculate_reward(self, current_state: dict, action_dict: dict, agent_observations: dict, done: bool, state: State):
        """Calculate the cumulative reward based on the phase mapping.

        Parameters
        ----------
        current_state : Dict[str, _]
            the current state of all the hosts in the simulation
        action_dict : dict
        agent_observations : Dict[str, ObservationSet]
            current agent observations
        done : bool
            has the episode ended
        state: State
            current State object

        Returns
        -------
        : int
            sum of the rewards collected

        [한국어]
        현재 미션 단계의 보상 매핑을 기준으로 누적 보상을 계산한다.

        Parameters
        ----------
        current_state : Dict[str, _]
            시뮬레이션 내 모든 호스트의 현재 상태.
        action_dict : dict
            이번 스텝에 각 에이전트가 취한 행동(Action) 매핑.
        agent_observations : Dict[str, ObservationSet]
            에이전트별 현재 관찰값(Observation).
        done : bool
            에피소드 종료 여부.
        state: State
            현재 State 객체.

        Returns
        -------
        : int
            수집된 보상들의 합.
        """
        reward_list = []
        # [설명] 현재 미션 단계에 해당하는 보상 매핑을 가져와 인스턴스에 보관한다.
        self.phase_rewards = self.get_phase_rewards(state.mission_phase)

        for agent_name, action in action_dict.items():
            if not action:
                continue

            action = action[0]
            # [설명] 보상 대상이 되는 행동만 추려 호스트 이름(hostname)을 얻는다.
            # Red의 Impact(타격)는 action에 hostname이 직접 있고, Green의 작업/서비스
            # 접근은 IP만 있으므로 ip_addresses로 hostname을 역조회한다. 그 외 행동은
            # 보상에 영향을 주지 않으므로 건너뛴다.
            if isinstance(action, Impact):
                hostname = action.hostname
            elif isinstance(action, GreenAccessService) or isinstance(action, GreenLocalWork):
                hostname = state.ip_addresses[action.ip_address]
            else:
                continue

            # 호스트가 속한 서브넷 이름과, 해당 에이전트의 세션 목록을 얻는다.
            subnet_name = state.hostname_subnet_map[hostname].value
            sessions = state.sessions[agent_name].values()

            # [설명] 활성 세션이 하나라도 있을 때만 보상을 집계한다. 세션이 모두
            # 죽었다면(예: Red가 쫓겨났거나 호스트가 다운) 그 행동은 보상에 반영하지
            # 않는다. success는 해당 행동의 성공 여부 관찰값이다.
            if len([session.ident for session in sessions if session.active]) > 0:
                success = agent_observations[agent_name].observations[0].data['success']
                rewards_for_zone = self.phase_rewards[subnet_name]

                # [설명] Green의 정상 작업이 실패하면(success == False) 작업 종류에 따라
                # LWF(로컬 작업 실패)/ASF(서비스 접근 실패) 페널티를 부여한다. 즉 Blue의
                # 과도한 방어로 정상 사용자가 방해받는 상황에 음의 보상이 발생한다.
                if 'green' in agent_name and success == False:
                    if isinstance(action, GreenLocalWork):
                        reward_list.append(rewards_for_zone["LWF"])
                    elif isinstance(action, GreenAccessService):
                        reward_list.append(rewards_for_zone["ASF"])

                # [설명] Red의 Impact(타격)가 성공하면 RIA(Red 침해/타격) 페널티를 부여한다.
                elif 'red' in agent_name and success and isinstance(action, Impact):
                    reward_list.append(rewards_for_zone["RIA"])

        # 한 스텝 동안 모인 보상값(대부분 음수 페널티)의 총합을 반환한다.
        return sum(reward_list)


  
        
        
 
     
        
    