# Copyright DST Group. Licensed under the MIT license.
from CybORG.Simulator.Entity import Entity


class LocalGroup(Entity):
    """A local user group on a host.

    [한국어]
    호스트에 정의된 로컬 사용자 그룹을 나타내는 엔티티.
    그룹 이름(name), 그룹 식별자(gid), 그룹에 속한 사용자 목록(users)을 보관한다.
    """
    def __init__(self, name: str = None, gid: int = None, users: list = None):
        super().__init__()
        self.name = name
        self.ident = gid
        # gid(그룹 식별자)는 self.ident에 저장한다.
        self.users = users

    def get_state(self):
        """Return the group's identifying state.

        [한국어]
        그룹의 식별 정보(이름과 gid)를 딕셔너리로 반환한다.
        """
        return {"group": self.name,
                "gid": self.ident}

    def remove_user(self, user):
        """Remove a user from this group by username.

        [한국어]
        주어진 username과 일치하는 사용자를 그룹에서 제거한다.
        인자 user는 username 문자열이며, 멤버의 username 속성과 비교한다.
        """
        # [설명] user(문자열)와 멤버 객체의 username을 비교해 일치하는 멤버를 제거한다.
        for candidate in self.users:
            if user == candidate.username:
                self.users.remove(candidate)

