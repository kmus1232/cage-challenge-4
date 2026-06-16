import inspect
import time
from statistics import mean, stdev

from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator

from datetime import datetime

import json

import sys
import os


def rmkdir(path: str):
    """Recursive mkdir

    [한국어]
    경로를 슬래시 단위로 잘라 상위 디렉터리부터 차례로 만든다(재귀적 mkdir).
    같은 경로에 이미 파일이 존재하면 디렉터리를 만들 수 없으므로 예외를 던진다.
    """
    partial_path = ""
    # 경로를 슬래시 단위로 나눠 상위부터 한 단계씩 누적해 만든다
    for p in path.split("/"):
        partial_path += p + "/"

        if os.path.exists(partial_path):
            if os.path.isdir(partial_path):
                continue  # 이미 디렉터리면 건너뛴다
            if os.path.isfile(partial_path):
                # 같은 이름의 파일이 있으면 디렉터리를 만들 수 없다
                raise RuntimeError(f"Cannot create {partial_path} (exists as file).")

        os.mkdir(partial_path)


def load_submission(source: str):
    """Load submission from a directory or zip file

    [한국어]
    디렉터리 또는 zip 파일에서 참가자 제출물(submission)을 불러온다.
    먼저 source 경로를 import 검색 경로(sys.path) 맨 앞에 끼워 넣은 뒤
    Submission 클래스를 import 하고, 끝나면 경로를 다시 제거한다.
    """
    sys.path.insert(0, source)  # 제출물 경로를 import 검색 경로 맨 앞에 추가

    if source.endswith(".zip"):
        try:
            # Load submission from zip.
            # zip 안에서는 submission/submission.py 구조를 기대한다
            from submission.submission import Submission
        except ImportError as e:
            raise ImportError(
                """
                Error loading submission from zip.
                Please ensure the zip contains the path submission/submission.py
                """
            ).with_traceback(e.__traceback__)
    else:
        # Load submission normally
        # 디렉터리면 submission 모듈을 그대로 import 한다
        from submission import Submission

    # Remove submission from path.
    sys.path.remove(source)  # 끼워 넣었던 경로를 원상 복구한다
    return Submission


def run_evaluation(submission, log_path, max_eps=100, write_to_file=True, seed=None):
    """Run the CybORG evaluation for a submission and (optionally) write logs.

    [한국어]
    제출물(submission)을 CC4 평가 시나리오(Scenario4)에서 여러 에피소드 동안
    돌려 보상을 측정하고, 결과를 파일로 저장하는 평가 진입점이다.

    동작 순서:
    1. EnterpriseScenarioGenerator로 시나리오를 만들고 CybORG 환경을 시뮬레이션
       모드("sim")로 생성한다. 이때 Blue는 SleepAgent, Green은
       EnterpriseGreenAgent, Red는 FiniteStateRedAgent로 고정한다.
    2. 제출물의 wrap()으로 환경을 래핑(Wrapper 적용)한다.
    3. max_eps 만큼 에피소드를 반복하며, 각 에피소드는 EPISODE_LENGTH(500) 스텝을
       돈다. 매 스텝마다 제출물의 에이전트가 관찰값(observation)을 보고 행동(action)을
       고르고, 환경을 한 스텝 진행시킨다.
    4. 에피소드별 보상 합을 모아 평균·표준편차를 계산하고, write_to_file이 참이면
       요약/전체 로그/행동 로그/JSON/점수 파일로 저장한다.

    인자:
        submission: NAME/TEAM/TECHNIQUE/AGENTS/wrap()을 갖춘 제출물 객체.
        log_path: 결과를 저장할 디렉터리 경로.
        max_eps: 실행할 최대 에피소드 수.
        write_to_file: 참이면 결과를 파일로 기록한다.
        seed: CybORG 환경 난수 시드(재현성 확보용).
    """
    cyborg_version = CYBORG_VERSION
    EPISODE_LENGTH = 500  # 에피소드 1회당 스텝 수
    scenario = "Scenario4"  # CC4 평가 시나리오

    version_header = f"CybORG v{cyborg_version}, {scenario}"
    author_header = f"Author: {submission.NAME}, Team: {submission.TEAM}, Technique: {submission.TECHNIQUE}"

    # [설명] 시나리오 생성기 구성. 평가용으로 Blue/Green/Red 에이전트 클래스를
    # 고정한다. Blue를 SleepAgent로 두는 이유는, 실제 방어는 제출물 쪽 에이전트가
    # 맡고 환경 자체의 기본 Blue는 아무 행동도 하지 않게(잠자게) 하기 위함이다.
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,            # Blue(방어): 아무 행동도 안 함
        green_agent_class=EnterpriseGreenAgent,  # Green(정상 사용자)
        red_agent_class=FiniteStateRedAgent,     # Red(공격)
        steps=EPISODE_LENGTH,
    )
    cyborg = CybORG(sg, "sim", seed=seed)  # 시뮬레이션 모드로 환경 생성
    wrapped_cyborg = submission.wrap(cyborg)  # 제출물의 Wrapper 적용
    
    print(version_header)
    print(author_header)
    print(
        f"Using agents {submission.AGENTS}, if this is incorrect please update the code to load in your agent"
    )

    if write_to_file:
        if not log_path.endswith("/"):
            log_path += "/"
        print(f"Results will be saved to {log_path}")

    start = datetime.now()  # 평가 소요 시간 측정 시작

    total_reward = []  # 에피소드별 보상 합 누적
    actions_log = []   # 에피소드별 행동 기록
    obs_log = []       # 에피소드별 관찰값 기록
    # 바깥 루프: 에피소드 반복
    for i in range(max_eps):
        observations, _ = wrapped_cyborg.reset()  # 매 에피소드 시작 시 환경 초기화
        r = []  # 이번 에피소드의 스텝별 보상
        a = []  # 이번 에피소드의 스텝별 행동
        o = []  # 이번 에피소드의 스텝별 관찰값
        count = 0
        # 안쪽 루프: 한 에피소드 내 스텝 반복
        for j in range(EPISODE_LENGTH):
            # [설명] 현재 활성화된 에이전트별로 행동(Action)을 결정한다.
            # 각 에이전트는 자기 관찰값과 행동 공간(Action Space)을 받아 get_action으로
            # 행동을 고른다. wrapped_cyborg.agents에 없는 에이전트는 제외한다.
            actions = {
                agent_name: agent.get_action(
                    observations[agent_name], wrapped_cyborg.action_space(agent_name)
                )
                for agent_name, agent in submission.AGENTS.items()
                if agent_name in wrapped_cyborg.agents
            }
            # 환경을 한 스텝 진행시키고 관찰값/보상/종료 플래그를 받는다
            observations, rew, term, trunc, info = wrapped_cyborg.step(actions)
            # [설명] term(목표 달성 등으로 정상 종료) 또는 trunc(스텝 한도 초과 등으로
            # 잘려서 종료) 중 하나라도 참이면 그 에이전트는 done으로 본다.
            done = {
                agent: term.get(agent, False) or trunc.get(agent, False)
                for agent in wrapped_cyborg.agents
            }
            if all(done.values()):  # 모든 에이전트가 끝났으면 에피소드 조기 종료
                break
            r.append(mean(rew.values()))  # 이번 스텝의 평균 보상을 기록
            if write_to_file:
                # 스텝별 마지막 행동을 에이전트 이름 기준으로 기록
                a.append(
                    {
                        agent_name: cyborg.get_last_action(agent_name)
                        for agent_name in wrapped_cyborg.agents
                    }
                )
                # 스텝별 관찰값을 에이전트 이름 기준으로 기록
                o.append(
                    {
                        agent_name: observations[agent_name]
                        for agent_name in observations.keys()
                    }
                )
        total_reward.append(sum(r))  # 에피소드 보상 합 = 스텝 보상의 총합

        if write_to_file:
            actions_log.append(a)  # 에피소드 단위로 행동/관찰값 로그 누적
            obs_log.append(o)

    end = datetime.now()  # 평가 소요 시간 측정 종료
    difference = end - start  # 전체 평가에 걸린 시간

    # 에피소드별 보상 합의 평균과 표준편차를 계산한다
    reward_mean = mean(total_reward)
    reward_stdev = stdev(total_reward)
    reward_string = (
        f"Average reward is: {reward_mean} with a standard deviation of {reward_stdev}"
    )
    print(reward_string)

    print(f"File took {difference} amount of time to finish evaluation")
    if write_to_file:
        print(f"Saving results to {log_path}")
        # summary.txt: 버전·작성자·평균 보상·사용 에이전트 요약
        with open(log_path + "summary.txt", "w") as data:
            data.write(version_header + "\n")
            data.write(author_header + "\n")
            data.write(reward_string + "\n")
            data.write(f"Using agents {submission.AGENTS}")

        # full.txt: 에피소드별 행동·관찰값·보상 전체 기록
        with open(log_path + "full.txt", "w") as data:
            data.write(version_header + "\n")
            data.write(author_header + "\n")
            data.write(reward_string + "\n")
            for act, obs, sum_rew in zip(actions_log, obs_log, total_reward):
                data.write(
                    f"actions: {act},\n observations: {obs},\n total reward: {sum_rew}\n"
                )
        
        # actions.txt: 에피소드별 행동 기록만 따로 저장
        with open(log_path + "actions.txt", "w") as data:
            data.write(version_header + "\n")
            data.write(author_header + "\n")
            data.write(reward_string + "\n")
            for act in zip(actions_log):
                data.write(
                    f"actions: {act}"
                )

        # summary.json: 제출물 정보·파라미터·시간·보상·에이전트를 구조화해 저장
        with open(log_path + "summary.json", "w") as output:
            data = {
                "submission": {
                    "author": submission.NAME,
                    "team": submission.TEAM,
                    "technique": submission.TECHNIQUE,
                },
                "parameters": {
                    "seed": seed,
                    "episode_length": EPISODE_LENGTH,
                    "max_episodes": max_eps,
                },
                "time": {
                    "start": str(start),
                    "end": str(end),
                    "elapsed": str(difference),
                },
                "reward": {
                    "mean": reward_mean,
                    "stdev": reward_stdev,
                },
                "agents": {
                    agent: str(submission.AGENTS[agent]) for agent in submission.AGENTS
                },
            }
            json.dump(data, output)

        # scores.txt: 채점에 쓰는 핵심 점수(평균·표준편차)만 기록
        with open(log_path + "scores.txt", "w") as scores:
            scores.write(f"reward_mean: {reward_mean}\n")
            scores.write(f"reward_stdev: {reward_stdev}\n")


if __name__ == "__main__":
    # [설명] 스크립트를 직접 실행할 때의 진입점. 명령줄 인자를 파싱해
    # 제출물을 불러오고 run_evaluation을 호출한다.
    import argparse

    parser = argparse.ArgumentParser("CybORG Evaluation Script")
    parser.add_argument("submission_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument(
        "--append-timestamp",
        action="store_true",
        help="Appends timestamp to output_path",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Set the seed for CybORG"
    )
    parser.add_argument("--max-eps", type=int, default=100, help="Max episodes to run")
    args = parser.parse_args()
    # 입력받은 경로를 절대 경로로 변환한다
    args.output_path = os.path.abspath(args.output_path)
    args.submission_path = os.path.abspath(args.submission_path)

    if not args.output_path.endswith("/"):
        args.output_path += "/"

    # --append-timestamp가 켜져 있으면 출력 경로에 실행 시각 디렉터리를 덧붙인다
    if args.append_timestamp:
        args.output_path += time.strftime("%Y%m%d_%H%M%S") + "/"

    rmkdir(args.output_path)  # 출력 디렉터리를 재귀적으로 생성

    submission = load_submission(args.submission_path)  # 제출물 로드
    run_evaluation(
        submission, max_eps=args.max_eps, log_path=args.output_path, seed=args.seed
    )
