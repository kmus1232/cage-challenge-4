from prettytable import PrettyTable
from CybORG import CybORG
from CybORG.Agents.Wrappers import BaseWrapper


class TrueStateTableWrapper:
    """A CC4 wrapper that outputs the true state of the environment, in the form of various tables.

    The tables are created using PrettyTable package to make the output more readable.
    It is recommended that the output is piped to a text file, as the length of the output can be long.

    Attributes
    ----------
    hostnames : List[str]
        list of hostnames in the environment
    env : CybORG
        the cyborg environment that the wrapper is being added to (parent class attribute).
    agents : dict
        dictionary of agents (parent class attribute).

    [한국어]
    CC4 환경의 실제 상태(true state)를 여러 개의 표 형태로 출력하는 래퍼(Wrapper).
    에이전트가 관찰하는 부분적 관찰값(Observation)이 아니라, 환경이 실제로 보유한
    전체 상태를 사람이 읽기 좋게 정리해 디버깅·검증에 쓴다.

    표는 PrettyTable 패키지로 만들어 가독성을 높인다. 출력이 매우 길어질 수 있으므로
    텍스트 파일로 리다이렉트(piped)해서 보는 것을 권장한다.

    Attributes(속성)
    - hostnames : 환경에 존재하는 호스트 이름 목록
    - env : 이 래퍼가 감싸는 CybORG 환경 (부모 클래스 속성)
    - agents : 에이전트 딕셔너리 (부모 클래스 속성)
    """
    def __init__(self, env: CybORG = None):
        self.env = env
        self.hostnames = list(env.environment_controller.state.hosts.keys())
        
    def get_raw_full_true_state(self):
        """Gets all the raw true state data straight from the environment.

        Returns
        -------
        : dict
            the raw true state data from the env

        [한국어]
        환경에서 가공되지 않은(raw) 실제 상태 데이터 전체를 그대로 가져온다.
        모든 호스트에 대해 인터페이스·프로세스·세션·파일·사용자/시스템 정보·서비스를
        전부('All') 요청한다.

        반환값(Returns)
        - dict : 환경에서 받은 raw 실제 상태 데이터
        """
        get_all_dict = {
            'Interfaces': 'All',
            'Processes': 'All',
            'Sessions': 'All',
            'Files': 'All',
            'User info': 'All',
            'System info': 'All',
            'Services': 'All'
        }
        info = {host: get_all_dict for host in self.hostnames}
        return self.env.get_true_state(info)

    def get_host_overview_table(self):
        """Creates a table of: hostnames, IP addresses, sessions, and number of processes.

        Returns
        -------
        table : PrettyTable
            host overview table

        [한국어]
        호스트 개요 표를 만든다. 열 구성: 호스트 이름, IP 주소, 세션, 프로세스 개수.

        반환값(Returns)
        - table : PrettyTable — 호스트 개요 표
        """
        table = PrettyTable(["Hostname", "IP Address", "Sessions", "No. Processes"])

        get_dict = {
            'Interfaces': 'ip_address',
            'Processes': 'All',
            'Sessions': 'All'
        }
        get_dict_per_host = {host: get_dict for host in self.hostnames}
        true_state_dict = self.env.get_true_state(info=get_dict_per_host)
        # 'success' 키는 상태 데이터가 아닌 조회 성공 여부 플래그이므로 제거한다.
        true_state_dict.pop("success")

        for hostname, host_state in true_state_dict.items():
            state_keys = host_state.keys()
            ip_address = str(host_state['Interface'][0]['ip_address'])  # 첫 번째 인터페이스의 IP

            # 세션이 있으면 해당 세션을 점유한 에이전트 목록을, 없으면 "-" 표시
            if 'Sessions' in state_keys:
                sessions = [sess['agent'] for sess in host_state['Sessions']]
            else:
                sessions = "-"

            # 프로세스가 있으면 개수를, 없으면 "0"
            if 'Processes' in state_keys:
                num_processes = str(len(host_state['Processes']))
            else:
                num_processes = "0"

            table.add_row([hostname, ip_address, sessions, num_processes])

        return table
    
    def get_host_processes_tables(self):
        """Creates a table of: hostname, process ID, process name, process type, associated username, associated session and session ID (if any); per subnet.

        Returns
        -------
        tables : Dict[str, PrettyTable]
            dictionary of host processes tables per subnet

        [한국어]
        서브넷(subnet)별로 호스트 프로세스 표를 만든다. 각 행의 열 구성:
        호스트 이름, 프로세스 ID(PID), 프로세스 이름, 프로세스 종류,
        연관 사용자명, 연관 세션(있다면)과 세션 ID(SID).

        반환값(Returns)
        - tables : Dict[str, PrettyTable] — 서브넷 이름을 키로 하는 표 딕셔너리
        """

        # Get true state info from environment
        # 환경에서 실제 상태 정보를 가져온다.
        get_dict = {
            'Interfaces': 'All',
            'Processes': 'All',
            'Sessions': 'All'
        }
        get_dict_per_host = {host: get_dict for host in self.hostnames}
        true_state_dict = self.env.get_true_state(info=get_dict_per_host)
        true_state_dict.pop("success")  # 조회 성공 여부 플래그 제거

        # Define tables storage
        # 서브넷마다 빈 표를 하나씩 만들어 둔다. 키는 서브넷 이름(subnet_name.name).
        subnet_cidr_map = self.env.environment_controller.subnet_cidr_map
        tables = {subnet_name.name: PrettyTable(["Hostname", "PID", "Name", "Type", "Username", "Session", "SID"]) for subnet_name in subnet_cidr_map.keys()}

        # Creates table
        # 호스트별로 순회하며 각 프로세스를 해당 서브넷 표에 행으로 추가한다.
        for hostname, host_state in true_state_dict.items():
            state_keys = host_state.keys()
            row = 0  # 현재 호스트에서 몇 번째 프로세스 행인지 세는 카운터
            if 'Processes' in state_keys:
                num_procs = len(host_state['Processes'])
                for proc in host_state['Processes']:
                    pid = proc['PID']
                    row += 1

                    if "process_name" in proc.keys():
                        p_name = proc["process_name"]
                    else:
                        p_name = "-"

                    if "process_type" in proc.keys():
                        p_type = proc["process_type"]
                    else:
                        p_type = "-"

                    if "username" in proc.keys():
                        p_user = proc["username"]
                    else:
                        p_user = "-"

                    # [설명] 이 프로세스(pid)와 PID가 일치하는 세션을 찾아
                    # 점유 에이전트와 세션 ID를 채운다. 일치하는 세션이 없으면 "-" 유지.
                    p_sess = "-"
                    p_sid = "-"
                    if 'Sessions' in state_keys:

                        for sess in host_state['Sessions']:
                            if sess["PID"] == pid:
                                p_sess = sess["agent"]
                                p_sid = sess["session_id"]
                                break

                    # [설명] 호스트의 CIDR을 subnet_cidr_map에서 역조회해
                    # 이 프로세스를 넣을 서브넷 표 이름(subnet_name)을 결정한다.
                    subnet_cidr = host_state['Interface'][0]["Subnet"]
                    for name, cidr in subnet_cidr_map.items():
                        if cidr == subnet_cidr:
                            subnet_name = name.name
                            break

                    # [설명] 행을 추가하면서 divider(구분선)로 호스트 단위를 구분한다.
                    # 한 호스트의 마지막 프로세스 행에만 divider=True를 주고,
                    # 같은 호스트의 두 번째 행부터는 호스트 이름 대신 따옴표(")로 표기한다.
                    if row == num_procs and row == 1:
                        # 프로세스가 1개뿐인 호스트: 첫 행이자 마지막 행 → 이름 표시 + 구분선
                        tables[subnet_name].add_row([hostname, pid, p_name, p_type, p_user, p_sess, p_sid], divider=True)
                    elif row == 1:
                        # 여러 프로세스 중 첫 행: 호스트 이름 표시
                        tables[subnet_name].add_row([hostname, pid, p_name, p_type, p_user, p_sess, p_sid])
                    elif row == num_procs:
                        # 마지막 행: 이름 자리에 따옴표 + 구분선
                        tables[subnet_name].add_row(["\"", pid, p_name, p_type, p_user, p_sess, p_sid], divider=True)
                    else:
                        # 중간 행: 이름 자리에 따옴표
                        tables[subnet_name].add_row(["\"", pid, p_name, p_type, p_user, p_sess, p_sid])

        return tables

    def get_agent_session_tables(self):
        """Creates a table of: agent name, session ID, associated hostname, username, session type, and associated process ID; per agent team (red, blue, green).

        Returns
        -------
        team_tables: Dict[str, PrettyTable]

        [한국어]
        에이전트 팀(red, blue, green)별로 세션 표를 만든다. 각 행의 열 구성:
        에이전트 이름, 세션 ID(SID), 연관 호스트 이름, 사용자명, 세션 종류,
        연관 프로세스 ID(PID).

        반환값(Returns)
        - team_tables : Dict[str, PrettyTable] — 팀 이름('red'/'blue'/'green')을
          키로 하는 표 딕셔너리
        """

        # Get true state info from environment
        # 환경에서 세션 정보만 가져온다.
        get_dict = {
            'Sessions': 'All'
        }
        get_dict_per_host = {host: get_dict for host in self.hostnames}
        true_state_dict = self.env.get_true_state(info=get_dict_per_host)
        true_state_dict.pop("success")  # 조회 성공 여부 플래그 제거

        table_data = {
            'red' : {},
            'blue' : {},
            'green' : {}
        }

        for hostname, host_state in true_state_dict.items():
            for sess in host_state['Sessions']:
                agent = sess['agent']
                sess_id = sess['session_id']
                sess_type = sess['Type']
                sess_user = sess['username']
                sess_pid = sess['PID']

                # [설명] 에이전트 이름에 'red'/'blue'가 들어있는지로 팀을 분류하고,
                # 둘 다 아니면 green으로 본다. 분류된 팀 딕셔너리에 세션 정보를 모은다.
                team_dict = None
                if 'red' in agent:
                    team_dict = table_data['red']
                elif 'blue' in agent:
                    team_dict = table_data['blue']
                else:
                    team_dict = table_data['green']

                if not agent in team_dict.keys():
                    team_dict[agent] = []
                team_dict[agent].append((sess_id, hostname, sess_user, sess_type, sess_pid))

        team_tables = {}
        for team, team_data in table_data.items():
            team_table = PrettyTable(["Agent", "SID", "Hostname", "Username", "Type", "PID"])

            for agent, agent_data in team_data.items():
                agent_data.sort()  # 세션 ID 기준으로 정렬해 출력 순서를 안정화
                total_agent_sessions = len(agent_data)

                # [설명] 같은 에이전트의 여러 세션을 행으로 나열한다.
                # 첫 행에만 에이전트 이름을 넣고 이후 행은 "-"로 표기하며,
                # 에이전트의 마지막 세션 행에 divider(구분선)를 둔다.
                sess_count = 0
                for session_data in agent_data:
                    sess_count += 1
                    row_data = list(session_data)

                    if sess_count == 1:
                        # 첫 세션 행: 에이전트 이름 표시
                        row_data.insert(0, agent)
                        team_table.add_row(row_data)
                    elif sess_count == total_agent_sessions:
                        # 마지막 세션 행: 이름 자리에 "-" + 구분선
                        row_data.insert(0, "-")
                        team_table.add_row(row_data, divider=True)
                    else:
                        # 중간 세션 행: 이름 자리에 "-"
                        row_data.insert(0, "-")
                        team_table.add_row(row_data)

            team_tables[team] = team_table

        return team_tables

    def print_host_overview_table(self):
        """Prints the table produces by get_host_overview_table to stdout.

        [한국어]
        get_host_overview_table가 만든 호스트 개요 표를 표준출력(stdout)에 찍는다.
        """
        print(self.get_host_overview_table())

    def print_host_processes_tables(self):
        """Prints the tables produced by get_host_process_tables to stdout.

        [한국어]
        get_host_processes_tables가 만든 서브넷별 프로세스 표를 표준출력에 찍는다.
        """
        tables = self.get_host_processes_tables()
        for subnet, table in tables.items():
            print(f"Host Processes Table: Subnet {subnet} \n")
            print(table)
            print("\n")

    def print_agent_session_tables(self):
        """Prints the tables produced by get_agent_session_tables to stdout.

        [한국어]
        get_agent_session_tables가 만든 팀별 세션 표를 표준출력에 찍는다.
        """
        team_tables = self.get_agent_session_tables()
        for team, team_table in team_tables.items():
            print(f"Agent Session Table: Team {team} \n")
            print(team_table)
            print("\n")