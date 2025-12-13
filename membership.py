from config import *

def mu_tanah_kecil(x):
    if x <= 50: return 1
    elif 50 < x <= TANAH_SMALL_MAX: return (TANAH_SMALL_MAX-x)/(TANAH_SMALL_MAX-50)
    return 0

def mu_tanah_sedang(x):
    if TANAH_SMALL_MAX < x <= TANAH_MED_MAX: return (x-TANAH_SMALL_MAX)/(TANAH_MED_MAX-TANAH_SMALL_MAX)
    elif TANAH_MED_MAX < x <= TANAH_MED_MAX+30: return (TANAH_MED_MAX+30-x)/30
    return 0

def mu_tanah_besar(x):
    if x <= TANAH_MED_MAX: return 0
    return 1

def mu_bangun_kecil(x):
    if x <= 40: return 1
    elif 40 < x <= BANG_SMALL_MAX: return (BANG_SMALL_MAX-x)/(BANG_SMALL_MAX-40)
    return 0

def mu_bangun_sedang(x):
    if BANG_SMALL_MAX < x <= BANG_MED_MAX: return (x-BANG_SMALL_MAX)/(BANG_MED_MAX-BANG_SMALL_MAX)
    elif BANG_MED_MAX < x <= BANG_MED_MAX+30: return (BANG_MED_MAX+30-x)/30
    return 0

def mu_bangun_besar(x):
    if x <= BANG_MED_MAX: return 0
    return 1
