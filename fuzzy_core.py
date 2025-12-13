from membership import *
from model_rules import rule_inference

def sugeno_defuzz(rules):
    num = sum(a*z for (a,z) in rules)
    den = sum(a for (a,z) in rules)
    if den == 0: return 0
    return num / den

def fuzzy_predict(land_val, build_val):

    tanah = {
        "kecil":  mu_tanah_kecil(land_val),
        "sedang": mu_tanah_sedang(land_val),
        "besar":  mu_tanah_besar(land_val)
    }

    bangun = {
        "kecil":  mu_bangun_kecil(build_val),
        "sedang": mu_bangun_sedang(build_val),
        "besar":  mu_bangun_besar(build_val)
    }

    rules = rule_inference(tanah, bangun)

    return sugeno_defuzz(rules)
