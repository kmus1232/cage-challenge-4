import networkx as nx
from networkx import connected_components
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import time
import numpy as np
from copy import deepcopy

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent


class VisualiseRedExpansion():
    """Visualisation wrapper that displays the user and root shells acquired by red agents over time, in a series of network graph plots.

    Attributes
    ----------
    fig : matplotlib.pyplot.figure.Figure
        graph figure
    ax : matplotlib.pyplot.axes.Axes
        graph axes
    slider : matplotlib.widgets.Slider
        slider to control graph in GUI
    collected_networks : networkx.Graph
        graph of the network
    play_view_flag : bool
        flag for if the graph display is iterating through steps
    env : SimulationController
        CybORG environment used
    total_steps : int
        total number of steps to iterate over
    node_label_mapping : Dict[str, str]
        dictionary mapping host names to the abbreviated labels shown of the graph
    host_nodes : Dict[str, str]
        grouping of host types to hosts
    host_interfaces : list
        list of interfaces as edges between two hosts
    pos : Dict[str, float]
        position of nodes on graph

    [한국어]
    Red 에이전트(공격 측)가 시간이 지나며 확보한 user/root 셸을 네트워크 그래프
    여러 장으로 시각화하는 래퍼(Wrapper). 스텝(step)마다 네트워크 상태를 수집해
    두었다가, 슬라이더로 스텝을 넘기며 Red의 침투 확장 과정을 다시 볼 수 있게 한다.

    속성(Attributes)
    ----------
    fig : matplotlib 그래프 figure
    ax : matplotlib 그래프 axes
    slider : GUI에서 그래프(스텝)를 조작하는 슬라이더
    collected_networks : 스텝별로 수집한 네트워크 정보 목록
    play_view_flag : 그래프가 스텝을 자동 재생 중인지 나타내는 플래그
    env : 사용 중인 CybORG 환경(SimulationController)
    total_steps : 순회할 전체 스텝 수
    node_label_mapping : 호스트 이름 -> 그래프에 표시할 축약 라벨 매핑
    host_nodes : 호스트 유형(user/server/other)별로 묶은 호스트 목록
    host_interfaces : 두 호스트를 잇는 인터페이스(간선) 목록
    pos : 그래프 상의 노드 좌표
    """
    def __init__(self, cyborg, steps):
        self.fig = None
        self.ax = None
        self.slider = None
        self.collected_networks = []
        self.play_view_flag = False
        
        self.env = cyborg.environment_controller
        self.total_steps = steps

        # Fixed graph nodelists (of host)
        # 고정 노드 목록(호스트). link_diagram은 호스트-인터페이스 연결 그래프이며, 시각화 전체에서 변하지 않는 뼈대다.
        env_netmap = self.env.state.link_diagram.copy()
        self.node_label_mapping = self._get_node_label_mapping(env_netmap)
        self.host_nodes = self._get_host_nodes(env_netmap)
        self.host_interfaces = list(env_netmap.edges()).copy()

        # Create initial network nodelists
        # 초기 네트워크 상태(에이전트·세션) 수집
        initial_network_info = self._set_initial_agents_and_sessions()

        # Add the new edges and nodes to the graph
        # 수집한 에이전트(노드)와 세션(간선)을 그래프에 추가한다.
        env_netmap.add_nodes_from(initial_network_info['active_agents']['blue'])
        env_netmap.add_edges_from(initial_network_info['host_sessions'])

        # [설명] 노드 좌표는 Blue 추가 후·Red 추가 전에 한 번 계산해 self.pos에 고정한다.
        # 이렇게 하면 스텝마다 Red가 늘어도 기존 노드 위치가 흔들리지 않는다.
        self.pos = self._set_network_host_and_agents_positions(env_netmap)
        env_netmap.add_nodes_from(initial_network_info['active_agents']['red'])

        initial_network_info['network_map'] = env_netmap
        self.collected_networks.append(initial_network_info)

    def run(self):
        """Automating the running of the visualisation, with visualising each step then outputting the graph.

        [한국어]
        환경을 total_steps만큼 진행시키며 매 스텝의 상태를 수집한 뒤, 최종적으로
        그래프를 띄운다. 시각화 실행의 진입점이다.
        """
        for step in range(self.total_steps):
            self.env.step()
            self.visualise_step()
        self.show_graph()
    
    def visualise_step(self):
        """Collecting all the information at each step and adding it to a dictionary, to be used later for the visualisation.

        [한국어]
        한 스텝에서의 네트워크 상태(침해된 호스트, Red/Blue 세션, 라벨 등)를 모아
        딕셔너리로 만들고 collected_networks에 누적한다. 나중에 슬라이더로 되돌려
        볼 때 이 누적 데이터를 그대로 사용한다.

        [설명] Red 에이전트가 새로 늘어난 스텝에서만 그래프를 복사해 노드를 추가하고,
        그렇지 않으면 직전 스텝의 그래프 객체를 그대로 재사용한다(불필요한 복사 회피).
        """

        host_nodes_compromised, red_agents = self._get_compromised_nodes()
        all_session_agents, all_host_sessions, agent_label_mapping, red_root_nodes = self._get_compromised_edges()
        
        # 직전 스텝까지 알려진 Red 에이전트 목록
        known_red_agents = self.collected_networks[-1]['active_agents']['red']
        # Red 에이전트 수가 늘었으면(=새 Red 등장) 그래프를 복사해 새 노드를 추가한다.
        if len(all_session_agents['red'])>len(known_red_agents):
            new_network = self.collected_networks[-1]['network_map'].copy()
            for new_red in all_session_agents['red']:
                if new_red not in known_red_agents:
                    new_network.add_node(new_red)


            new_network_info = {
                'network_map' : new_network,
                'active_agents' : all_session_agents,
                'agent_label_mapping' : agent_label_mapping,
                'host_sessions' : all_host_sessions,
                'compromised_hosts' : host_nodes_compromised,
                'red_root_nodes' : red_root_nodes
            }
        else:
            # Red가 늘지 않았으면 직전 그래프 객체를 그대로 재사용한다.
            new_network_info = {
                'network_map' : self.collected_networks[-1]['network_map'],
                'active_agents' : all_session_agents,
                'agent_label_mapping' : agent_label_mapping,
                'host_sessions' : all_host_sessions,
                'compromised_hosts' : host_nodes_compromised,
                'red_root_nodes' : red_root_nodes
            }

        self.collected_networks.append(new_network_info)
        
    def show_graph(self):
        """Render for the visualisation graph plot.

        [한국어]
        matplotlib figure를 만들고, 0번 스텝 그래프를 그린 뒤 슬라이더와 재생/정지/
        앞뒤 이동 버튼을 배치한다. 콜백을 연결한 다음 plt.show()로 GUI를 띄운다.
        """
        self.fig, self.ax = plt.subplots(num="CC4 Visualisation")
        # [설명] 마우스 좌표 표시를 빈 문자열로 덮어 좌표가 화면에 뜨지 않게 한다.
        self.ax.format_coord = lambda x, y: ""
        self._draw_network(0, init=True)
        plt.subplots_adjust(bottom=0.25)

        axcolor = 'lightgoldenrodyellow'

        # 슬라이더·버튼들의 위치(figure 기준 비율 좌표 [left, bottom, width, height])
        ax_pos_slider = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
        ax_pos_btn_back = plt.axes([0.125, 0.15, 0.02, 0.03], facecolor='w')
        ax_pos_btn_play = plt.axes([0.15, 0.15, 0.02, 0.03], facecolor='w')
        ax_pos_btn_pause = plt.axes([0.175, 0.15, 0.02, 0.03], facecolor='w')
        ax_pos_btn_forward = plt.axes([0.20, 0.15, 0.02, 0.03], facecolor='w')

        btn_forward = Button(ax_pos_btn_forward, '>', color='w', hovercolor='b')
        btn_back = Button(ax_pos_btn_back, '<', color='w', hovercolor='b')
        btn_play = Button(ax_pos_btn_play, 'P', color='w', hovercolor='b')
        btn_pause = Button(ax_pos_btn_pause, '||', color='w', hovercolor='b')


        self.slider = Slider(
            ax=ax_pos_slider,
            label="",
            # label='Step Progression',
            valmin=0,
            valmax=self.total_steps,
            valinit=0,
            valstep=1
        )
        # 슬라이더 값이 바뀔 때마다 해당 스텝 그래프를 다시 그린다.
        self.slider.on_changed(self._draw_network)
        btn_forward.on_clicked(self._btn_forward)
        btn_back.on_clicked(self._btn_back)
        btn_play.on_clicked(self._btn_play)
        btn_pause.on_clicked(self._btn_pause)

        plt.show()

    def _btn_forward(self, ev):
        # 앞으로 한 스텝 이동(마지막 스텝 전까지)
        pos = self.slider.val
        if pos < self.total_steps:
            self.slider.set_val(pos+1)

    def _btn_back(self, ev):
        # 뒤로 한 스텝 이동(0번 스텝 이후부터)
        pos = self.slider.val
        if pos > 0:
            self.slider.set_val(pos-1)

    def _btn_play(self, ev):
        # 재생: 마지막 스텝에 닿을 때까지 0.3초 간격으로 자동으로 한 스텝씩 넘긴다.
        self.play_view_flag = True

        while self.play_view_flag:
            pos = self.slider.val
            if pos < self.total_steps:
                self.slider.set_val(pos+1)
            else:
                self.play_view_flag = False
            plt.pause(0.3)

    def _btn_pause(self, ev):
        # 일시정지: 자동 재생 루프를 멈춘다.
        self.play_view_flag = False

    def _draw_network(self, idx, init:bool = False):
        # [설명] idx번 스텝의 네트워크 그래프를 그린다. 노드 유형·에이전트·세션·침해
        # 상태를 색과 모양으로 구분해 겹쳐 그린다. init=True일 때만 자동 축 범위를
        # 쓰고, 이후에는 직전 확대/이동(zoom/pan) 상태를 유지한다.

        # 다시 그리기 전에 현재 축 범위(확대/이동 상태)를 저장해 둔다.
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.clear()

        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.host_nodes['users'], node_size=200, node_color='#C0C0C0', alpha=0.9, node_shape='o')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.host_nodes['servers'], node_size=200, node_color='#C0C0C0', alpha=0.9, node_shape='s')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.host_nodes['other'], node_size=400, node_color='#C0C0C0', alpha=0.9, node_shape='H')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['active_agents']['red'], node_size=200, node_color='#EE4B2B', node_shape='^')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['active_agents']['blue'], node_size=200, node_color='#0096FF', node_shape='^')
        nx.draw_networkx_edges(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, edgelist=self.host_interfaces)
        nx.draw_networkx_edges(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, edgelist=self.collected_networks[idx]['host_sessions'], style=':')
        nx.draw_networkx_labels(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, labels=self.node_label_mapping, font_size=10)
        nx.draw_networkx_labels(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, labels=self.collected_networks[idx]['agent_label_mapping'], font_size=10)
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['compromised_hosts'], node_size=200, node_color='#FFA500', alpha=0.8)
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['red_root_nodes'], node_size=200, node_color='#EE4B2B', alpha=0.8)

        self.ax.legend([
            'user host', 'server host', 'router', 
            'red agent', 'blue agent', 
            'host link', 'session link', 
            'user compromised host', 'root compromised host'
        ])

        # 첫 그리기(init)가 아니면, 저장해 둔 확대/이동 상태를 복원한다.
        if not init:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        self.fig.canvas.draw_idle()
        pass

    # get the compromised nodes for colour coding
    # 색 구분을 위해 침해된(compromised) 호스트 노드를 구한다.
    def _get_compromised_nodes(self):
        # [설명] Red 팀의 모든 에이전트가 가진 세션을 훑어, 세션이 올라가 있는
        # 호스트 이름과 활성 Red 에이전트 이름을 모은다(중복 제거 후 반환).
        host_nodes_compromised=[]
        agents_active=[]
        for red_agent_name in self.env.team['Red']:
            for sess in self.env.state.sessions[red_agent_name].values():
                host_nodes_compromised.append(sess.hostname)
                agents_active.append(red_agent_name)
        return list(set(host_nodes_compromised)), list(set(agents_active))

    def _get_compromised_edges(self):
        # [설명] 직전 스텝 정보를 복사해 와서, 이번 스텝에 새로 생긴 Red 세션을
        # 간선(host-agent)·노드(agent)로 추가한다. root 권한 세션이 있는 호스트는
        # red_root_nodes로 따로 모은다(나중에 root 침해 색으로 표시).
        last_collected_network = self.collected_networks[-1]

        all_session_agents = deepcopy(last_collected_network['active_agents'])
        all_host_sessions = deepcopy(last_collected_network['host_sessions'])
        agent_label_mapping = deepcopy(last_collected_network['agent_label_mapping'])

        agent_root_nodes = self._get_agent_root_nodes()
        red_root_nodes = []

        # For each host in the state, add their agent sessions to the new edges list and the agents to the new nodes list (grouped by agent type)
        # 상태의 각 호스트를 돌며, 에이전트 세션을 간선 목록에, 에이전트를 노드 목록에 (유형별로) 추가한다.
        for hostname, host in self.env.state.hosts.items():
            for agent, sids in host.sessions.items():
                if not sids == []:
                    if "red" in agent:
                        # 아직 등록되지 않은 Red 에이전트면 간선·노드·라벨을 새로 추가한다.
                        if agent not in all_session_agents['red']:
                            all_host_sessions.append((hostname, agent))
                            all_session_agents["red"].append(agent)
                            agent_label_mapping[agent] = "R" + agent.split("_")[-1]
                        # 이 호스트에 root 권한 세션이 있으면 red_root_nodes에 기록한다.
                        for sid in sids:
                            if sid in agent_root_nodes[agent]:
                                red_root_nodes.append(hostname)
                            # agent_label_mapping[hostname] = str(sid)
        #all_session_agents["red"] = list(set(all_session_agents["red"]))
        return all_session_agents, all_host_sessions, agent_label_mapping, red_root_nodes

    def _get_agent_root_nodes(self):
        # [설명] Red 에이전트별로, username이 "root"인 세션의 세션 id 목록을 만든다.
        # 즉 "어떤 Red 에이전트가 어디서 root 권한을 가졌는지" 판별용 자료다.
        agent_root_nodes = {}

        for agent, sessions in self.env.state.sessions.items():
            if 'red' in agent:
                agent_root_nodes[agent] = []
                for i, sess in sessions.items():
                    if sess.username == "root":
                        agent_root_nodes[agent].append(i)
        
        return agent_root_nodes

    def _get_node_label_mapping(self, env_netmap):
        # Node label mapping
        # 노드 라벨 매핑.
        # [설명] user_host/server_host(개별 호스트)는 라벨을 붙이지 않고, 서브넷·존을
        # 나타내는 노드만 보안 영역(zone) 약어로 라벨링한다. 예: restricted_zone -> "RZ".
        # 이름에 "_a_"/"_b_"가 있으면 파티션 A/B를 뒤에 덧붙인다(예: "RZA").
        node_label_mapping = {}
        for node in env_netmap._node.keys():
            if not "user_host" in node and not "server_host" in node:
                new_node_label = ""

                # Zone name
                # 보안 영역(zone) 이름 -> 약어
                if "restricted_zone" in node:
                    new_node_label = "RZ"
                elif "operational_zone" in node:
                    new_node_label = "OZ"
                elif "contractor_network" in node:
                    new_node_label = "CN"
                elif "public_access_zone" in node:
                    new_node_label = "PAZ"
                elif "admin_network" in node:
                    new_node_label = "AN"
                elif "office_network" in node:
                    new_node_label = "ON"
                else:
                    # 어느 존에도 해당하지 않으면 인터넷 루트 노드로 라벨링하고 넘어간다.
                    new_node_label = "Internet Root"
                    node_label_mapping[node] = new_node_label
                    continue

                # Partition
                # 파티션 구분(A/B)을 약어 뒤에 덧붙인다.
                if "_a_" in node:
                    new_node_label = new_node_label + "A"
                elif "_b_" in node:
                    new_node_label = new_node_label + "B"

                node_label_mapping[node] = new_node_label

        return node_label_mapping

    def _get_host_nodes(self, env_netmap):
        # [설명] 노드 이름에 'server'/'user'가 들어있는지로 호스트를 server/user/other
        # 세 묶음으로 나눈다. other에는 라우터·존 노드 등이 들어간다. 그래프에서
        # 묶음마다 다른 모양/크기로 그리기 위한 분류다.
        host_nodes = {}

        all_host_nodes = list(env_netmap.nodes()).copy()
        host_nodes['servers'] = [host for host in all_host_nodes if 'server' in host]
        host_nodes['users'] = [host for host in all_host_nodes if 'user' in host]
        host_nodes['other'] = [host for host in all_host_nodes if 'user' not in host and 'server' not in host]

        return host_nodes

    def _set_initial_agents_and_sessions(self):
        # [설명] 0번 스텝(초기 상태)의 에이전트·세션을 한 번 훑어 수집한다.
        # _get_compromised_edges와 비슷하나, Blue까지 포함하고 침해 호스트 목록도
        # 함께 만든다는 점이 다르다. 결과 딕셔너리는 첫 collected_networks 항목이 된다.
        all_session_agents = {"blue": [], "red": []}
        agent_label_mapping = {}
        all_host_sessions = []
        compromised_hosts = []

        agent_root_nodes = self._get_agent_root_nodes()
        red_root_nodes = []

        # For each host in the state, add their agent sessions to the new edges list and the agents to the new nodes list (grouped by agent type)
        # 상태의 각 호스트를 돌며, 에이전트 세션을 간선 목록에, 에이전트를 노드 목록에 (유형별로) 추가한다.
        for hostname, host in self.env.state.hosts.items():
            for agent, sids in host.sessions.items():
                if not sids == []:
                    if "blue" in agent:
                        # Blue 에이전트: 라벨은 "B" + 번호 (예: "B0")
                        all_session_agents["blue"].append(agent)
                        agent_label_mapping[agent] = "B" + agent.split("_")[-1]
                        all_host_sessions.append((hostname, agent))
                    elif "red" in agent:
                        # Red 에이전트: 라벨은 "R" + 번호. 세션이 있는 호스트는 침해된 것으로 본다.
                        all_session_agents["red"].append(agent)
                        agent_label_mapping[agent] = "R" + agent.split("_")[-1]
                        all_host_sessions.append((hostname, agent))
                        compromised_hosts.append(hostname)

                        # root 권한 세션이 있으면 red_root_nodes에 기록한다.
                        for sid in sids:
                            if sid in agent_root_nodes[agent]:
                                red_root_nodes.append(hostname)

        # Duplicates are removed from lists
        # 목록에서 중복을 제거한다.
        all_session_agents["blue"] = list(set(all_session_agents["blue"]))
        all_session_agents["red"] = list(set(all_session_agents["red"]))

        info = {
            'active_agents' : all_session_agents,
            'agent_label_mapping' : agent_label_mapping,
            'host_sessions' : all_host_sessions,
            'compromised_hosts' : compromised_hosts,
            'red_root_nodes' : red_root_nodes
        }
        return info

    def _set_network_host_and_agents_positions(self, env_netmap):
        # [설명] 그래프 노드들의 좌표를 정한다. 호스트는 spring layout으로 자동
        # 배치하고, 6개 Red 에이전트는 각자 활동 가능한 서브넷에 속한 호스트들의
        # 평균 좌표에 살짝(1.15배) 바깥쪽으로 떨어뜨려 배치한다(겹침 완화).
        # seed를 고정해 매 실행마다 같은 배치가 나오도록 한다.
        all_red_agents = ['red_agent_0', 'red_agent_1', 'red_agent_2', 'red_agent_3', 'red_agent_4', 'red_agent_5', ]

        # 각 Red 에이전트(인덱스 0~5)가 활동할 수 있는 서브넷 목록
        red_agent_allowed_subnets = [
            [SUBNET.CONTRACTOR_NETWORK.value],
            [SUBNET.RESTRICTED_ZONE_A.value],
            [SUBNET.OPERATIONAL_ZONE_A.value],
            [SUBNET.RESTRICTED_ZONE_B.value],
            [SUBNET.OPERATIONAL_ZONE_B.value],
            [SUBNET.PUBLIC_ACCESS_ZONE.value, SUBNET.ADMIN_NETWORK.value, SUBNET.OFFICE_NETWORK.value]
        ]

        # 호스트 노드 배치(seed 고정으로 재현 가능)
        positions = nx.spring_layout(env_netmap, seed=2, iterations=300)

        # get the position of hosts in each subnet - used for new red agent positions
        # 서브넷별 호스트 좌표를 모은다 - 새 Red 에이전트 위치 계산에 쓰인다.
        subnet_host_positions = {}
        for subnet in self.env.state.subnets.values():
            subnet_name = subnet.name
            subnet_host_positions[subnet_name] = []
            for host_name in self.env.state.hosts.keys():
                if subnet_name in host_name:
                    subnet_host_positions[subnet_name].append(list(positions[host_name]))
                    
        for r in range(6):
            red_agent_name = 'red_agent_' + str(r)

            # 활동 서브넷이 하나면 그 서브넷 호스트들의 평균 좌표에 배치한다.
            if len(red_agent_allowed_subnets[r]) == 1:
                positions[red_agent_name] = np.array(subnet_host_positions[red_agent_allowed_subnets[r][0]]).mean(axis=0)*1.15

            else:
                # 여러 서브넷이면 그 서브넷들의 호스트 좌표를 모두 합쳐 평균을 낸다.
                combined_subnet_hosts = []
                for s in red_agent_allowed_subnets[r]:
                    combined_subnet_hosts.extend(subnet_host_positions[s])
                positions[red_agent_name] = np.array(combined_subnet_hosts).mean(axis=0)*1.15

        return positions
        