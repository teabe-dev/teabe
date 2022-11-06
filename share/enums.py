from enum import IntEnum

class MemberType(IntEnum):
    INVITE = 11    # 邀請中
    AUDIT = 12     # 審核中
    BLOCKADE = 13  # 封鎖中
    OWNER = 21     # 所有者
    ADMIN = 22     # 管理員
    MEMBER = 23    # 會員

    @classmethod
    def choices(cls):
        CHOICES = (
            (cls.INVITE.value, '邀請中'),
            (cls.AUDIT.value, '審核中'),
            (cls.BLOCKADE.value, '封鎖中'),
            (cls.OWNER.value, '所有者'),
            (cls.ADMIN.value, '管理員'),
            (cls.MEMBER.value, '會員'),
        )
        return CHOICES
