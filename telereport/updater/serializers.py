import datetime
import pytz

from config import timezone


def event_serializer(obj):
    """
    :param obj: (action_type: int8, peer_id: int64, local_datetime: datetime.datetime)
    :return: bytearray
    """
    bArray = bytearray()
    bArray.extend(obj[0].to_bytes(1, 'big'))
    bArray.extend(obj[1].to_bytes(8, 'big'))
    bArray.extend(int(obj[2].timestamp()).to_bytes(4, 'big'))

    return bytes(bArray)


def event_deserializer(byte):
    """
    :param byte: byte sequence
    :return: (action_type: int8, peer_id: int64, local_datetime: datetime.datetime, date: datetime.date, time: datetime.time)
    """
    action = int.from_bytes(byte[0:1], 'big')
    peer_id = int.from_bytes(byte[1:9], 'big')
    timestamp = int.from_bytes(byte[9:], 'big')

    local_datetime = datetime.datetime.fromtimestamp(timestamp, tz=pytz.timezone(timezone))

    return action, peer_id, local_datetime, local_datetime.date(), local_datetime.time()


def message_serializer(obj):
    """
    :param obj: (views_count: int32, forwards: int32, local_datetime: datetime.datetime)
    :return: bytearray
    """
    bArray = bytearray()
    bArray.extend(obj[0].to_bytes(4, 'big'))
    bArray.extend(obj[1].to_bytes(4, 'big'))
    bArray.extend(int(obj[2].timestamp()).to_bytes(4, 'big'))

    return bytes(bArray)


def message_deserializer(byte):
    """
    :param byte: byte sequence
    :return: (views_count: int32, forwards: int32, local_datetime: datetime.datetime, date: datetime.date, time: datetime.time)
    """
    views_count = int.from_bytes(byte[0:4], 'big')
    forwards = int.from_bytes(byte[4:8], 'big')
    timestamp = int.from_bytes(byte[8:], 'big')

    local_datetime = datetime.datetime.fromtimestamp(timestamp, tz=pytz.timezone(timezone))

    return views_count, forwards, local_datetime, local_datetime.date(), local_datetime.time()
