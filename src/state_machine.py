from enum import Enum


class States(Enum):
    Start_state = 0
    State_SetTimezone = 1
    State_SetTime = 2
    State_SetText = 3
    State_Done = 4
