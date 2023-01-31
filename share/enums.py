from enum import Enum, IntEnum

class StrChoiceEnum(str, Enum):

    @classmethod
    def nameList(cls):
        return list(map(lambda x: x.name, cls))

    @classmethod
    def valueList(cls):
        return list(map(lambda x: x.value, cls))

    @classmethod
    def choices(cls):
        return tuple(map(lambda x: (x.value, x.name), cls))

    @classmethod
    def dictionary(cls):
        return dict(map(lambda x: x, cls.choices()))

class IntChoiceEnum(IntEnum):
    @classmethod
    def nameList(cls):
        return list(map(lambda x: x.name, cls))

    @classmethod
    def valueList(cls):
        return list(map(lambda x: x.value, cls))

    @classmethod
    def choices(cls):
        return tuple(map(lambda x: (x.value, x.name), cls))

    @classmethod
    def dictionary(cls):
        return dict(map(lambda x: x, cls.choices()))

class MemberRole(IntChoiceEnum):
    INVITE = 11    # 邀請中
    AUDIT = 12     # 審核中
    BLOCKADE = 13  # 封鎖中
    OWNER = 21     # 所有者
    ADMIN = 22     # 管理員
    MEMBER = 23    # 會員

    @classmethod
    def choices(cls):
        return tuple(map(lambda x: (x.value, MEMBER_ROLE_MAP[x]), cls))

MEMBER_ROLE_MAP = {
    MemberRole.INVITE: "邀請中",
    MemberRole.AUDIT: "審核中",
    MemberRole.BLOCKADE: "封鎖中",
    MemberRole.OWNER: "所有者",
    MemberRole.ADMIN: "管理員",
    MemberRole.MEMBER: "會員",
}
