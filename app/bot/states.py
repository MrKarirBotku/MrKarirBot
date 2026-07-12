from enum import IntEnum


class BotState(IntEnum):
    HOME = 0
    JOB_SEARCH = 1
    AI_CHAT = 2
    ATS_REVIEW = 3
    INTERVIEW_COACH = 4
