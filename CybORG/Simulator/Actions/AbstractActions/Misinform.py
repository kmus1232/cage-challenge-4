## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

"""
Implements misinformation actions for blue agents

[한국어]
Blue 에이전트(방어 측)의 허위정보(misinformation) 행동(Action)을 구현한다.
호스트에 가짜로 취약해 보이는 디코이(Decoy) 프로세스를 심어, Red 에이전트
(공격 측)가 실제 자산 대신 미끼를 공격하도록 유인하는 것이 목적이다.
"""
# pylint: disable=invalid-name

from typing import List, Optional
from dataclasses import dataclass

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Host import Host
from CybORG.Shared.Session import Session
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Service import Service
from CybORG.Simulator.State import State


@dataclass
class Decoy:
    """
    Contains information necessary to create a misinform process on a host

    [한국어]
    호스트에 허위정보용(misinform) 프로세스를 생성하는 데 필요한 정보를 담는
    데이터 클래스. 디코이로 위장할 서비스 이름·프로세스 이름·열린 포트 등을
    한데 묶어 전달한다.
    """
    service_name: str
    name: str
    open_ports: List[dict]
    process_type: str
    process_path: Optional[str] = None
    version: Optional[str] = None
    properties: Optional[List[str]] = None

class DecoyFactory:
    """
    Assembles process informationt to appear as a vulnerable process

    [한국어]
    취약한 프로세스처럼 보이도록 프로세스 정보를 조립하는 팩토리(factory)
    기반 클래스. 하위 클래스가 포트·서비스 이름 등 클래스 속성을 채우면,
    그 값으로 Decoy 인스턴스를 만들어 낸다.
    """
    PORT: int = None
    SERVICE_NAME: str = None
    NAME: str = None
    PROCESS_TYPE: str = None
    PROCESS_PATH: str = None
    PROPERTIES: List[str] = None
    VERSION: str = None

    def make_decoy(self, host: Host) -> Decoy:
        """
        Creates a Decoy instance that contains the necessary information
        to put a decoy on a given host.

        Parameters
        ---------
        host : Host
            a host that this decoy will be placed on

        [한국어]
        주어진 호스트에 디코이를 배치하는 데 필요한 정보를 담은 Decoy
        인스턴스를 생성한다.

        Parameters
        ---------
        host : Host
            이 디코이가 배치될 호스트
        """
        # [설명] 기반 클래스는 host 인자를 실제로 쓰지 않는다. 하위 클래스가
        # 호스트별로 값을 바꿔야 할 때 시그니처를 맞추기 위해 받기만 하고,
        # del로 명시적으로 버린다.
        del host
        return Decoy(
            service_name=self.SERVICE_NAME,
            name=self.NAME,
            open_ports=[{'local_port': self.PORT, 'local_address': '0.0.0.0'}],
            process_type=self.PROCESS_TYPE,
            process_path=self.PROCESS_PATH,
            properties=self.PROPERTIES,
            version=self.VERSION
        )

    def is_host_compatible(self, host: Host) -> bool:
        """
        Determines whether an instance of this decoy can be placed
        successfully on the given host

        Parameters
        ---------
        host : Host
            Host to examine for compatibility with this decoy.

        [한국어]
        이 디코이를 주어진 호스트에 성공적으로 배치할 수 있는지 판정한다.

        Parameters
        ---------
        host : Host
            이 디코이와의 호환성을 검사할 호스트

        [설명] 디코이가 쓰려는 포트(self.PORT)를 호스트가 이미 사용 중이면
        배치 불가로 본다. 따라서 포트가 비어 있을 때만 True를 반환한다.
        """
        return not host.is_using_port(self.PORT)

class SSHDDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an ssh server

    [한국어]
    ssh 서버처럼 보이도록 프로세스 정보를 조립하는 디코이 팩토리.
    """
    PORT = 22
    SERVICE_NAME = "sshd"
    NAME = "Sshd.exe"
    PROCESS_TYPE = "sshd"
    PROCESS_PATH = "C:\\Program Files\\OpenSSH\\usr\\sbin"

sshd_decoy_factory = SSHDDecoyFactory()


class ApacheDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server

    [한국어]
    apache 웹 서버처럼 보이도록 프로세스 정보를 조립하는 디코이 팩토리.
    """
    PORT = 80
    SERVICE_NAME = "apache2"
    NAME = "apache2"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]
    PROCESS_PATH = "/usr/sbin"

apache_decoy_factory = ApacheDecoyFactory()


class SMSSDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as smss

    [한국어]
    smss(Windows 세션 관리자) 프로세스처럼 보이도록 정보를 조립하는 디코이
    팩토리.
    """
    PORT = 139
    SERVICE_NAME = "smss"
    NAME = "Smss.exe"
    PROCESS_TYPE = "smss"

smss_decoy_factory = SMSSDecoyFactory()


class TomcatDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as a tomcat server

    [한국어]
    tomcat 웹 서버처럼 보이도록 프로세스 정보를 조립하는 디코이 팩토리.
    """
    PORT = 443
    SERVICE_NAME = "tomcat"
    NAME = "Tomcat.exe"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]

tomcat_decoy_factory = TomcatDecoyFactory()


class SvchostDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as svchost

    [한국어]
    svchost(Windows 서비스 호스트) 프로세스처럼 보이도록 정보를 조립하는
    디코이 팩토리.
    """
    PORT = 3389
    SERVICE_NAME = "svchost"
    NAME = "Svchost.exe"
    PROCESS_TYPE = "svchost"

svchost_decoy_factory = SvchostDecoyFactory()


class Misinform(Action):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        PLACEHOLDER

    [한국어]
    지정된 호스트에 사용 가능하고 호환되는 옵션 중 하나를 골라, 공격자를
    오도하는(misleading) 디코이 프로세스를 생성하는 행동(Action) 클래스.

    Attributes
    ----------
    session: int
        세션 id
    agent: str
        이 행동을 실행하는 에이전트의 이름
    hostname: str
        디코이를 배치할 대상 호스트 이름
    """
    def __init__(self, *, session: int, agent: str, hostname: str):
        """ PLACEHOLDER

        Parameters
        ----------
        session: int
            PLACEHOLDER
        agent: str
            PLACEHOLDER
        hostname: int
            PLACEHOLDER

        [한국어]
        Misinform 행동을 초기화한다.

        Parameters
        ----------
        session: int
            행동에 사용할 세션 id
        agent: str
            이 행동을 실행하는 에이전트의 이름
        hostname: str
            디코이를 배치할 대상 호스트 이름
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.decoy_type = DecoyType.EXPLOIT
        # 후보 디코이 팩토리 목록. execute 시 호스트와 호환되는 것 중 하나를
        # 무작위로 골라 디코이를 만든다.
        self.candidate_decoys = (
                sshd_decoy_factory,
                apache_decoy_factory,
                smss_decoy_factory,
                tomcat_decoy_factory,
                svchost_decoy_factory)

    def execute(self, state: State) -> Observation:
        """ PLACEHOLDER DESC
        Parameters
        ----------
        state: State
            PLACEHOLDER

        Returns
        -------
        obs: Observation
            PLACEHOLDER

        [한국어]
        대상 호스트에 디코이 프로세스를 실제로 생성하는 실행 메서드.

        진행 흐름:
        1. 대상 호스트 위에 있는 세션을 찾는다. 없으면 실패 관찰값(Observation)을 반환한다.
        2. 호환되는 디코이 팩토리를 무작위로 하나 골라 디코이를 만든다.
        3. 그 디코이로 프로세스/서비스를 생성하고 성공 관찰값을 반환한다.
        4. 호환 팩토리가 없으면 RuntimeError가 발생하며, 이를 잡아 실패 관찰값을 반환한다.

        Parameters
        ----------
        state: State
            행동이 적용되는 시뮬레이터 상태(State)

        Returns
        -------
        obs: Observation
            행동 성공 여부와 생성된 프로세스 정보를 담은 관찰값(Observation)
        """
        obs_fail = Observation(False)
        obs_succeed = Observation(True)

        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            self.log(f"No sessions could be found on chosen host '{self.hostname}'.")
            return obs_fail

        # [설명] 같은 호스트에 세션이 여러 개면 그중 하나를 무작위로 고른다.
        # state.np_random은 시드 고정된 난수 생성기라 결과를 재현할 수 있다.
        session = state.np_random.choice(sessions)
        host = state.hosts[self.hostname]

        try:
            decoy_factory = self.__select_one_factory(host, state)
            decoy = decoy_factory.make_decoy(host)
            self.__create_process(obs_succeed, session, host, decoy)
            #print ("Misinform Success. Result: {}".format(result))
            return obs_succeed

        except RuntimeError as err:
            self.log(str(err))
            return obs_fail

    def __select_one_factory(self, host: Host, state: State) -> DecoyFactory:
        """
        Examines all decoy factories and returns one randomly compatible one.
        Raises RuntimeError if no compatible ones are found.

        [한국어]
        모든 디코이 팩토리를 검사해 호환되는 것 중 하나를 무작위로 반환한다.
        호환되는 팩토리가 하나도 없으면 RuntimeError를 발생시킨다.
        """

        # [설명] 후보 팩토리 중 대상 호스트와 호환되는(포트가 비어 있는) 것만 추린다.
        compatible_factories = [factory for factory in self.candidate_decoys
                if factory.is_host_compatible(host)]

        if len(compatible_factories) == 0:
            raise RuntimeError("No compatible factory")

        return state.np_random.choice(list(compatible_factories))

    def __create_process(self, obs: Observation, sess: Session, host: Host,
            decoy: Decoy) -> None:
        """
        Creates a process & service from Decoy on current host, adds it
        to the observation.

        [한국어]
        Decoy 정보를 바탕으로 현재 호스트에 프로세스와 서비스를 생성하고,
        그 결과를 관찰값(Observation)에 추가한다.
        """
        parent_pid = 1
        pid = host.create_pid()
        host.processes.append(Process(
            pid=pid,
            parent_pid=parent_pid,
            process_name=decoy.name,
            username=sess.username,
            process_version=decoy.version,
            open_ports=decoy.open_ports,
            process_type=decoy.process_type,
            properties=decoy.properties
        ))
        host.services[decoy.service_name] = Service(process=pid, session=sess)
        obs.add_process(
            hostid=self.hostname,
            pid=pid,
            parent_pid=parent_pid,
            name=decoy.name,
            username=sess.username,
            service_name=decoy.service_name,
            properties=decoy.properties
        )

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
