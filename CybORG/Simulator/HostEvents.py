from ipaddress import IPv4Address
from typing import List

from CybORG.Shared.Enums import TransportProtocol


class HostEvents():
    """Object that holds 'events'/alerts that have happened on a specific host.

    Attributes
    ----------
    network_connections : List[NetworkConnection]
        current network connection alerts
    old_network_connections : List[NetworkConnection]
        past network connection alerts
    process_creation : list
        current process creation alerts
    old_process_creation : list
        past process creation alerts

    [한국어]
    특정 호스트에서 발생한 '이벤트'/알림(alert)을 보관하는 객체.

    속성(Attributes)
    ----------
    network_connections : List[NetworkConnection]
        현재 스텝의 네트워크 연결 알림
    old_network_connections : List[NetworkConnection]
        과거(이전) 네트워크 연결 알림
    process_creation : list
        현재 스텝의 프로세스 생성 알림
    old_process_creation : list
        과거(이전) 프로세스 생성 알림
    """
    def __init__(self):
        self.network_connections: List[NetworkConnection] = []
        self.old_network_connections: List[NetworkConnection] = []
        self.process_creation = []
        self.old_process_creation = []

class NetworkConnection():
    """Object that holds a network connection event/alert.

    Attributes
    ----------
    local_address : IPv4Address
    local_port : int
    remote_address : IPv4Address
    remote_port : int
    pid : int
    application_protocol : str
    transport_protocol : TransportProtocol

    [한국어]
    네트워크 연결 이벤트/알림(alert) 하나를 보관하는 객체.

    속성(Attributes)
    ----------
    local_address : IPv4Address
        로컬(자기) 측 IP 주소
    local_port : int
        로컬(자기) 측 포트
    remote_address : IPv4Address
        원격(상대) 측 IP 주소
    remote_port : int
        원격(상대) 측 포트
    pid : int
        연결을 일으킨 프로세스 ID
    application_protocol : str
        애플리케이션 계층 프로토콜
    transport_protocol : TransportProtocol
        전송 계층 프로토콜
    """
    def __init__(
        self,
        local_address: IPv4Address,
        local_port: int = None,
        remote_address: IPv4Address = None,
        remote_port: int = None,
        pid: int = None,
        application_protocol: str = None,
        transport_protocol: TransportProtocol = None
    ):
        self.local_address = local_address
        self.local_port = local_port
        self.remote_address = remote_address
        self.remote_port = remote_port
        self.pid = pid
        self.application_protocol = application_protocol
        self.transport_protocol = transport_protocol

    def get_state(self) -> dict:
        # [설명] 이 연결 정보를 관찰값(Observation)용 dict로 변환한다.
        # local_port/local_address는 항상 포함하고, 나머지 필드는 값이 있을 때만(truthy) 추가한다.
        obs = {
            "local_port": self.local_port,
            "local_address": self.local_address
        }
        if self.remote_port:
            obs["remote_port"] = self.remote_port
        if self.remote_address:
            obs["remote_address"] = self.remote_address
        if self.transport_protocol:
            obs["transport_protocol"] = self.transport_protocol
        return obs
