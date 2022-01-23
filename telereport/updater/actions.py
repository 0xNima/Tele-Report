"""Action Types: an integer between 0-255"""
JOIN = 0
LEAVE = 1
INVITE = 2
JOIN_BY_INVITE = 3


class Action:
    from telethon.tl import types

    def __new__(cls, action):
        if isinstance(action, cls.types.ChannelAdminLogEventActionParticipantJoin):
            return JOIN
        if isinstance(action, cls.types.ChannelAdminLogEventActionParticipantLeave):
            return LEAVE
        if isinstance(action, cls.types.ChannelAdminLogEventActionParticipantInvite):
            return INVITE
        if isinstance(action, cls.types.ChannelAdminLogEventActionParticipantJoinByInvite):
            return JOIN_BY_INVITE

        return None
