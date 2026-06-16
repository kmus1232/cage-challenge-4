# Copyright DST Group. Licensed under the MIT license.

"""
This module contains functions for parsing a YAML scenario config file

[한국어]
YAML 시나리오 설정 파일을 파싱하는 함수들을 모아둔 모듈이다.
시나리오 파일에는 서브넷·호스트·Red 행동(Action)·OSINT 정보가 정의되며,
이 모듈은 그 내용을 검증하고 내부에서 사용할 dict 구조로 변환한다.
"""
import os
import yaml
from copy import deepcopy
from prettytable import PrettyTable

from CybORG.Shared.State.Credentials import AccessLevel, Credentials
from CybORG.Shared.State.Service import Service, ServiceType
from CybORG.Shared.State.OperatingSystem import OperatingSystemType, OperatingSystemInformation

path = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(os.path.dirname(path), os.pardir)

# file path to available actions list
# 사용 가능한 행동(Action) 목록 파일 경로
AVAIL_ACTIONS_PATH = os.path.join(path, '../Simulator/Actions', 'Actions.yaml')

# file path to available images list
# 사용 가능한 이미지 목록 파일 경로
AVAIL_IMAGES_PATH = os.path.join(path, 'Images', 'Images.yaml')

# The expected properties of a scenario config file
# 시나리오 설정 파일에 기대되는 최상위 키들 (필수 / 선택)
SCENARIO_KEYS_REQ = ["Subnets", "Hosts"]
SCENARIO_KEYS_OPT = ["RedActions"]

# Expected keys for each host
# 각 호스트(Host)에 기대되는 키들 (필수 / 선택)
HOST_KEYS_REQ = ["subnet", "image"]
HOST_KEYS_OPT = ["value"]

# Optional params and default values for red actions
# Red 행동(Action)의 선택 파라미터와 기본값
RED_ACTION_OPT = {
    "success_prob": 1,
    "cost": 0,
    "detect_prob": 0}

# OSINT에서 호스트/서브넷에 대해 수집 가능한 정보 항목 목록
INT_host_list = ["IPs", "Subnets", "Creds", "OS_info", "Services", "Flag"]
INT_subnet_list = ["CIDR"]

# TODO parse simplicity of password
# TODO 비밀번호의 단순도(simplicity) 파싱 처리

def load_yaml(file_path):
    """
    Load file located at file path, throws error if theres an issue loading
    file.

    Arguments:
        file_path : path to YAML scenario config file

    Returns:
        scenario : the scenario file as a dict

    [한국어]
    주어진 경로의 YAML 파일을 읽어 dict로 반환한다. 파일 로딩에 문제가 있으면
    오류를 발생시킨다.

    인자:
        file_path : YAML 시나리오 설정 파일 경로
    반환:
        scenario : dict로 변환된 시나리오 파일
    """
    with open(file_path) as fIn:
        scenario_file = yaml.load(fIn, Loader=yaml.FullLoader)
    return scenario_file


def parse_scenario_file(scenario_file_path):
    """
    Load and parse a YAML scenario file.
    Throws exceptions if error loading file or file format is incorrect.

    Arguments:
        scenario_file_path : path to YAML scenario config file

    Returns:
        parsed_scenario : the parsed scenario as a dict

    [한국어]
    YAML 시나리오 파일을 읽어 파싱한다. 파일 로딩 오류나 형식 오류가 있으면
    예외를 발생시킨다. 서브넷·호스트·Red 행동·OSINT를 차례로 파싱하고,
    선택 항목(RedActions, OSINT)이 없으면 기본값으로 채운 뒤 하나의 dict로 묶어
    반환한다.

    인자:
        scenario_file_path : YAML 시나리오 설정 파일 경로
    반환:
        parsed_scenario : 파싱된 시나리오 dict
    """
    scenario = load_yaml(scenario_file_path)

    check_scenario_keys_correct(scenario)

    avail_actions = load_yaml(AVAIL_ACTIONS_PATH)
    avail_images_yaml = load_yaml(AVAIL_IMAGES_PATH)
    avail_images = parse_images(avail_images_yaml)

    scn_name = get_scenario_name(scenario_file_path)
    parsed_subnets = parse_subnets(scenario["Subnets"])
    parsed_hosts, num_hosts_with_pos_val = parse_hosts(scenario["Hosts"], parsed_subnets, avail_images)

    # [설명] RedActions 키가 없으면 사용 가능한 모든 행동을 기본 파라미터로 채워 쓰고,
    # 있으면 시나리오에 명시된 행동만 검증·파싱한다.
    if "RedActions" not in scenario.keys():
        parsed_red_actions = load_default_red_action_dict(avail_actions["RedActions"])
    else:
        parsed_red_actions = parse_red_action_dict(scenario["RedActions"], avail_actions["RedActions"])

    # [설명] OSINT(공개출처정보) 키가 없으면 외부에 공개된 호스트만 기본값으로 사용하고,
    # 있으면 시나리오에 명시된 OSINT 항목을 검증·파싱한다.
    if "OSINT" not in scenario.keys():
        parsed_OSINT = load_default_OSINT_dict(parsed_hosts)
    else:
        parsed_OSINT = parse_OSINT_dict(scenario["OSINT"], parsed_hosts, parsed_subnets)

    parsed_scenario = {"Name": scn_name,
                       "Hosts": parsed_hosts,
                       "Flags": num_hosts_with_pos_val,
                       "Subnets": parsed_subnets,
                       "RedActions": parsed_red_actions,
                       "OSINT": parsed_OSINT}

    return parsed_scenario


def check_scenario_keys_correct(scenario):
    """
    Checks the scenario contains all the necessary high-level keys in
    SCENARIO_KEYS

    Raises error if key incorrect or missing

    [한국어]
    시나리오에 SCENARIO_KEYS_REQ에 정의된 필수 최상위 키가 모두 있는지 확인한다.
    키가 잘못되었거나 누락되면 오류를 발생시킨다.
    """
    for req_key in SCENARIO_KEYS_REQ:
        if req_key not in scenario.keys():
            raise KeyError("Scenario: Missing required key in scenario config file: {}".format(req_key))


def get_scenario_name(scenario_file_path):
    """
    Get the scenario name from the scenario file path.

    Arguments:
        str scenario_file_path : path to YAML scenario config file

    Returns:
        str scenario_name : name of scenario

    [한국어]
    시나리오 파일 경로에서 파일명(확장자 .yaml 제외)을 떼어 시나리오 이름으로
    반환한다.

    인자:
        scenario_file_path : YAML 시나리오 설정 파일 경로
    반환:
        scenario_name : 시나리오 이름
    """
    return os.path.basename(scenario_file_path).replace('.yaml', '')


def parse_images(images):
    """
    Parses list of available images into Image objects.

    Arguments:
        images : dictionary of images

    Returns:
        parsed_images : dictionary of parsed images

    [한국어]
    사용 가능한 이미지 목록을 Image 객체로 파싱한다. 각 이미지마다 OS 정보,
    서비스(Service) 목록, 자격증명(Credentials) 목록을 읽어 Image를 만든다.

    인자:
        images : 이미지 dict
    반환:
        parsed_images : 파싱된 이미지 dict
    """
    parsed_images = {}
    for image_name, image_info in images.items():
        name = image_info["Name"]
        image_id = image_info["Image_ID"]

        os_data = image_info["OS"]
        os_type = OperatingSystemType.parse_string(os_data["Type"])
        os_dist = os_data["Distribution"]
        os_version = os_data["Version"]
        os_info = OperatingSystemInformation(os_type, os_dist, os_version)

        services = []
        for service_name, service_info in image_info["Services"].items():
            service_type = ServiceType.parse_string(service_name)
            port = service_info["port"]
            state = service_info.get("state", "open")
            version = service_info.get("version", "")
            services.append(Service(service_type, port, state, version))

        credentials = []
        for uname, access_info in image_info["Credentials"].items():
            access_level = AccessLevel.parseString(access_info["Access"])
            password = access_info.get("Password")
            key_path = access_info.get("Key")
            simplicity = access_info.get("Simplicity")
            creds = Credentials(username=uname, password=password, key_path=key_path,
                                access_level=access_level, simplicity=simplicity)
            credentials.append(creds)

        # Process AWS Instance type if there is one
        # AWS 인스턴스 타입이 있으면 처리 (없으면 None)
        inst_type = image_info.get("AWS_Instance_Type", None)

        # Whether an SSH key is required for access to image, False by default
        # 이미지 접근에 SSH 키가 필요한지 여부 (기본값 False)
        key_access = image_info.get("Key_Access", False)

        image = Image(name, services, image_id, os_info, credentials, inst_type, key_access)
        parsed_images[image_name] = image

    return parsed_images


def parse_subnets(subnets):
    """
    Parse the Subnets dict, checking it is in correct format.
    Raises errors if there is a format violation.

    Arguments:
        subnets : the subnets dict

    Returns:
        parsed_subnets : parsed Subnet dict

    [한국어]
    Subnets dict를 형식이 올바른지 검사하며 파싱한다. 형식이 어긋나면 오류를
    발생시킨다. 검사 항목은 다음과 같다.
    - 최소 2개 이상의 서브넷(공격자용 1개, 대상용 1개)이 있어야 한다.
    - 각 서브넷의 연결 목록은 항목이 1개 이상인 리스트여야 한다.
    - 연결 목록에 자기 자신(부모 서브넷)이 들어가면 안 된다.
    - 연결 대상은 최상위 서브넷 목록에 정의된 서브넷이어야 하며 중복은 불가하다.

    인자:
        subnets : 서브넷 dict
    반환:
        parsed_subnets : 파싱된 서브넷 dict
    """
    if not isinstance(subnets, dict):
        raise ValueError("Subnets must be dict with key-value pairs: {}"
                         .format("subnet_id : [subnet_id, ..., subnet_id]"))

    if len(subnets) < 2:
        raise ValueError("Not enough subnets specified, need at least two:",
                         "one for attacker and one for target")

    parsed_subnets = {}
    avail_subnets = set(subnets.keys())
    for subnet_id, connected_list in subnets.items():
        if not isinstance(connected_list, list) or len(connected_list) < 1:
            raise ValueError("Subnet values must be list with at least one entry {} is invalid"
                             .format(connected_list))

        if subnet_id in connected_list:
            raise ValueError("Subnet connected list should not contain parent subnet: {}: {} invalid"
                             .format(subnet_id, connected_list))

        for connected_id in connected_list:
            if connected_id not in avail_subnets:
                raise ValueError("Subnets can only be connected to subnets with specified in top",
                                 "level subnet list: for subnet {} connected subnet {} invalid"
                                 .format(subnet_id, connected_id))

            if connected_list.count(connected_id) > 1:
                raise ValueError("Connected subnet lists cannot have duplicates: {}: {} invalid"
                                 .format(subnet_id, connected_list))
        parsed_subnets[subnet_id] = connected_list

    return parsed_subnets


def parse_hosts(hosts, subnets, avail_images):
    """
    Parse the Hosts dict, checking it is in correct format.
    Raises errors if there is a format violation.

    Arguments:
        hosts : the hosts dict
        subnets : the parsed subnets dictionary
        avail_images : the available images dictionary

    Returns:
        parsed_hosts : the parsed hosts dict
        num_hosts_with_pos_val : the number of hosts with a value

    [한국어]
    Hosts dict를 형식이 올바른지 검사하며 파싱한다. 형식이 어긋나면 오류를
    발생시킨다. 각 호스트마다 필수 키(subnet, image)를 확인하고, 서브넷·이미지가
    실제로 존재하는지, value가 정수/실수인지 검증한다. value가 양수인 호스트는
    공격 목표(goal)를 담고 있다고 보아 개수를 센다.

    인자:
        hosts : 호스트 dict
        subnets : 파싱된 서브넷 dict
        avail_images : 사용 가능한 이미지 dict
    반환:
        parsed_hosts : 파싱된 호스트 dict
        num_hosts_with_pos_val : value가 양수인 호스트 개수
    """
    if not isinstance(hosts, dict):
        raise ValueError("Hosts: Hosts must be dict with key-values - host_ID: {}, plus optional params {}"
                         .format(HOST_KEYS_REQ, HOST_KEYS_OPT))

    if len(hosts) < 2:
        raise ValueError("Hosts: Not enough hosts specified (need at least one attacker and one host)")

    parsed_hosts = {}
    num_hosts_with_pos_val = 0
    for host_id, params in hosts.items():

        for req_key in HOST_KEYS_REQ:
            if req_key not in params:
                raise ValueError("Hosts: Host {} missing required parameter {}".format(host_id, req_key))

        parsed_host = {}
        subnet = params['subnet']
        if subnet not in subnets:
            raise ValueError("Hosts: Host subnet must be a subnet in scenario subnets: {} invalid".format(subnet))

        image = params['image']
        if image not in avail_images:
            raise ValueError(f"Hosts: Host VM image must be an image name from available VM image list: host {host_id} "
                             f"image {image} invalid.\nSee {AVAIL_IMAGES_PATH} file for list of available images")

        if "value" in params:
            value = params["value"]
            if not isinstance(value, (int, float)):
                raise ValueError("Hosts: Host value must be a valid integer or float: host {} value {} invalid"
                                 .format(host_id, value))
            value = int(value) if isinstance(value, int) else float(value)
            if value > 0:
                num_hosts_with_pos_val += 1
        else:
            value = 0

        parsed_host['subnet'] = subnet
        parsed_host['value'] = value
        parsed_host['image'] = avail_images[image]
        parsed_hosts[host_id] = parsed_host
        parsed_host['configuration'] = params.get('configuration', [])

    # [설명] value가 양수인 호스트가 하나도 없으면 공격 목표가 없는 시나리오이므로 오류.
    if num_hosts_with_pos_val < 1:
        raise ValueError("Hosts: At least one host must have a positive value (i.e. contain a goal)")

    return parsed_hosts, num_hosts_with_pos_val


def load_default_red_action_dict(avail_actions):
    """
    Loads all the available red actions for the CybORG environment with default parameter values.

    See Actions/Actions.yaml list for full list of available actions

    Arguments:
        avail_actions : dictionary of all available actions with names as keys and extra info as values

    Returns:
        parsed_actions : the parsed actions dict

    [한국어]
    CybORG 환경에서 사용 가능한 모든 Red 행동(Action)을 기본 파라미터값으로 불러온다.
    전체 행동 목록은 Actions/Actions.yaml을 참고한다.

    인자:
        avail_actions : 사용 가능한 모든 행동 dict (이름이 키, 부가 정보가 값)
    반환:
        parsed_actions : 파싱된 행동 dict
    """
    print("RedActions: No actions specified so using list of all available actions with default params: {}"
          .format(RED_ACTION_OPT))

    parsed_actions = {}
    # for action_name, action_info in avail_actions.items():
    for action_name in avail_actions:
        parsed_params = deepcopy(RED_ACTION_OPT)
        parsed_params["name"] = action_name
        # for action_property, property_value in action_info.items():
        #     parsed_params[action_property] = property_value
        parsed_actions[action_name] = parsed_params
    return parsed_actions


def parse_red_action_dict(action_dict, valid_actions):
    """
    Parse the Red Actions dict.
    Raises excepted for any format violations

    Arguments:
        action_dict : the action dict to parse
        valid_actions : dictionary of valid actions with names as keys and extra info as values

    Returns:
        parsed_actions : the parsed actions dict

    [한국어]
    Red 행동(Action) dict를 파싱한다. 형식이 어긋나면 예외를 발생시킨다.
    명시된 행동이 유효 행동 목록에 있는지 확인하고, success_prob(성공 확률, 0~1)와
    cost(비용) 같은 파라미터 값을 검증한다. 명시되지 않은 선택 파라미터는
    RED_ACTION_OPT의 기본값으로 채운다.

    인자:
        action_dict : 파싱할 행동 dict
        valid_actions : 유효 행동 dict (이름이 키, 부가 정보가 값)
    반환:
        parsed_actions : 파싱된 행동 dict
    """
    if not isinstance(action_dict, dict):
        raise ValueError("RedActions: Actions must be dict with key-value pairs: "
                         + "action_name : {action_param: value, ...}")

    for action_name in action_dict.keys():
        if action_name not in valid_actions:
            raise ValueError("RedActions: red can only choose actions from Actions list. {} invalid"
                             .format(action_name)
                             + "\nFor full list of actions see {}".format(AVAIL_ACTIONS_PATH))

    parsed_actions = {}
    for action_name, params in action_dict.items():
        if not isinstance(params, dict):
            raise ValueError("RedActions: Action parameters must be dict with key-value pairs: "
                             + "action_param: value. {}: {} is invalid. ".format(action_name, params)
                             + "\nIf you would like to use default values enter empty dictionary as '{}': "
                             + "e.g. Get_host_os: {}")

        parsed_params = {"type": valid_actions[action_name]}
        # parsed_params["name"] = action_name
        # [설명] 행동마다 명시된 파라미터를 하나씩 검증해 parsed_params에 담는다.
        for action_param, value in params.items():
            parsed_value = None
            if action_param == "success_prob":
                parsed_value = float(value)
                if 0 > parsed_value or parsed_value > 1:
                    raise ValueError('RedActions: action param "success_prob" must have value from 0 to 1.',
                                     "Value {} for action {} invalid".format(value, action_name))

            if action_param == "cost":
                if not isinstance(value, (int, float)):
                    raise ValueError('RedActions: action param "cost" must be a int or float.'
                                     + "Value {} for action {} invalid".format(value, action_name))
                parsed_value = float(value)
                if parsed_value < 0:
                    print("RedActions: Warning: negative action cost detected for action {}.".format(action_name),
                          "Action costs are typically handled as a non-negative value. Change the scenario file if",
                          "this is an incorrect value, otherwise ignore this warning.")

            parsed_params[action_param] = parsed_value

        # [설명] 시나리오에 명시되지 않은 선택 파라미터는 기본값(RED_ACTION_OPT)으로 채운다.
        for opt_param, default_value in RED_ACTION_OPT.items():
            if opt_param not in parsed_params:
                parsed_params[opt_param] = default_value

        # for action_property, property_value in valid_actions[action_name].items():
        #     parsed_params[action_property] = property_value

        parsed_actions[action_name] = parsed_params

    return parsed_actions


def load_default_OSINT_dict(avail_hosts):
    """
    Loads the default OSINT for the CybORG environment.

    Arguments:
        avail_hosts : dictionary of all available hosts with names as keys and extra info as values

    Returns:
        parsed_OSINT : the parsed OSINT dict

    [한국어]
    CybORG 환경의 기본 OSINT(공개출처정보)를 불러온다. 시나리오에 OSINT가
    지정되지 않았을 때 사용하며, 이름에 "PublicFacing"이 포함된(외부에 공개된)
    호스트의 IP만 정보로 제공한다.

    인자:
        avail_hosts : 사용 가능한 모든 호스트 dict (이름이 키, 부가 정보가 값)
    반환:
        parsed_OSINT : 파싱된 OSINT dict
    """
    print("OSINT: No OSINT specified so using publicly facing hosts")

    parsed_OSINT = {}
    # for action_name, action_info in avail_actions.items():
    for host in avail_hosts.keys():
        if "PublicFacing" in host:
            parsed_OSINT[host] = "IP"

    return parsed_OSINT


def parse_OSINT_dict(OSINT_dict, avail_hosts, avail_subnets):
    """
    Parse the Red Actions dict.
    Raises excepted for any format violations

    Arguments:
        action_dict : the action dict to parse
        valid_actions : dictionary of valid actions with names as keys and extra info as values

    Returns:
        parsed_actions : the parsed actions dict
        :param subnets:

    [한국어]
    OSINT(공개출처정보) dict를 파싱한다. 형식이 어긋나면 예외를 발생시킨다.
    (위 영어 docstring은 다른 함수에서 복사된 잔재라 인자 설명이 실제와 다르다.
    아래 설명을 따른다.)

    Hosts/Subnets 두 영역을 각각 검사한다.
    - OSINT에 적힌 호스트/서브넷이 시나리오에 실제 존재하는지 확인한다.
    - 수집 정보 항목이 허용 목록(INT_host_list / INT_subnet_list)에 있는지 확인한다.
      허용되지 않은 항목이면 오류를 발생시킨다.

    인자:
        OSINT_dict : 파싱할 OSINT dict
        avail_hosts : 파싱된 호스트 dict
        avail_subnets : 파싱된 서브넷 dict
    반환:
        parsed_OSINT : 파싱된 OSINT dict
    """
    if not isinstance(OSINT_dict, dict):
        raise ValueError("OSINT: OSINT must be dict with key-value pairs")

    parsed_OSINT = {}
    if "Hosts" in OSINT_dict:
        parsed_OSINT["Hosts"] = {}
        for host, l in OSINT_dict["Hosts"].items():
            if host in avail_hosts.keys():
                parsed_values = []
                if l is not None:
                    for v in l:
                        if v in INT_host_list:
                            parsed_values.append(v)
                        else:
                            raise ValueError("OSINT: intelligence on {} unavaliable".format(v))
                parsed_OSINT["Hosts"][host] = parsed_values
            else:
                raise ValueError("OSINT: Host {} specified by OSINT not found in scenario".format(host))
    if "Subnets" in OSINT_dict:
        parsed_OSINT["Subnets"] = {}
        for subnet, l in OSINT_dict["Subnets"].items():
            if subnet in avail_subnets.keys():
                parsed_values = []
                if l is not None:
                    for v in l:
                        if v in INT_subnet_list:
                            parsed_values.append(v)
                        else:
                            raise ValueError("OSINT: intelligence on {} unavaliable".format(v))
                parsed_OSINT["Subnets"][subnet] = parsed_values
            else:
                raise ValueError("OSINT: Subnet {} specified by OSINT not found in scenario".format(subnet))
    return parsed_OSINT

# [설명] 이 파일을 직접 실행하면 시나리오 파일을 파싱해 결과를 표(PrettyTable)로 출력한다.
# 시나리오 파일 구조를 눈으로 확인할 때 쓰는 디버깅/검사용 진입점이다.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", type=str, default='./Scenarios/scenario_6_hosts.yaml',
                        help="file path of scenario YAML file (e.g. './scenario_0.yaml')")
    args = parser.parse_args()

    print(f"Parsing scenario file {args.file_path}")
    parsed_scenario = parse_scenario_file(args.file_path)
    print("Parsing complete")

    for k, v in parsed_scenario.items():
        table = PrettyTable()
        table.title = k
        if k == "Subnets":
            table.field_names = ["Name", "ConnectedTo"]
            for subnet, connected in v.items():
                table.add_row([subnet] + [connected])
            print(f"\n{table}\n")
            print("-" * 80 + "\n")
        elif k == "Hosts":
            print("\n{}\nHosts:\n".format("-"*80))
            for name, vals in v.items():
                print(f"Name: {name}")
                for prop, prop_val in vals.items():
                    print(f"\t{prop}: {prop_val}")
                print("\n")
            print("-"*80 + "\n")
            continue
        elif k == "Name":
            print(v)
        elif k == "OSINT":
            print("OSINT: ")
            print(v)
        elif k == "Flags":
            print(f"Number of flags: {v}")
        else:
            for name, vals in v.items():
                table = PrettyTable()
                headers = list(vals.keys())
                table.field_names = headers
                table.add_row(list(vals.values()))
                print(f"\n{table}\n")
