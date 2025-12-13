from config import *

def rule_inference(tanah, bangun):
    rules = []

    a1 = min(tanah["kecil"], bangun["kecil"])
    z1 = PRICE_LOW
    rules.append((a1, z1))

    a2 = min(tanah["sedang"], bangun["sedang"])
    z2 = PRICE_MED
    rules.append((a2, z2))

    a3 = min(tanah["besar"], bangun["besar"])
    z3 = PRICE_HIGH
    rules.append((a3, z3))

    return rules
