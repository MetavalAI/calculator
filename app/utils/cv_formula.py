import math

def smart_round(value):
    value = float(value)
    if abs(value) < 1e-8:
        return 0
    if abs(value - round(value)) < 1e-8:
        return int(round(value))
    return round(value, 4)

def calculate_cv(Q, SG, DP, unit_mode="O11"):
    Q = float(Q)
    SG = float(SG)
    DP = float(DP)
    if DP == 0:
        return 0
# BASE SYSTEM
    if unit_mode == "O11":
        result = Q * math.sqrt(SG) / math.sqrt(DP)
# PSI SYSTEM
    elif unit_mode == "O10":
        result = (
            Q
            * 4.40286
            * math.sqrt(SG)
            / math.sqrt(DP * 14.2233)
        )
# ALT SYSTEM
    elif unit_mode == "O9":
        result = (
            Q
            * 4.40286
            * math.sqrt(SG)
            / math.sqrt(DP * 14.50377)
        )
    else:
        return 0
    return smart_round(result)

    