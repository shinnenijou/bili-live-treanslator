from enum import Enum


class EHTTPStatusCode(Enum):
    OK = 200

class ESendResult(Enum):
    """
    发送结果枚举,
    """
    SendFail = -1
    Success = 0
    HighFrequency = 10030         # 弹幕发送频率过高
    DuplicateMsg = 10031          # 短期内发送了两条内容完全相同的弹幕
    Unknown = 11000               # 弹幕被吞了（具体原因未知）


class EDanmakuPosition(Enum):
    Roll = 1
    Bottom = 4
    Top = 5

class EDanmakuColor(Enum):
    White = 16777215
