import math

def impedance_f(t_ij, f_name):
        def power(t_ij, b0):
            return 1 if t_ij<1 else (t_ij**-b0)

        def neg_exp(t_ij, b0):
            return math.exp(-b0*t_ij)

        def mgaus(t_ij, b0):
            return math.exp(-t_ij**2/b0)

        def cumr(t_ij, t_bar):
            return 1 if t_ij<=t_bar else 0

        def cuml(t_ij, t_bar):
            return 1-t_ij/t_bar if t_ij<=t_bar else 0

        p = {
            "POW0_8": {"f": power(t_ij, b0 = 0.8)}, 
            "POW1_0": {"f": power(t_ij, b0 = 1)},
            "POW1_5": {"f": power(t_ij, b0 = 1.5)}, 
            "POW2_0": {"f": power(t_ij, b0 = 2)},
            "POW_CUS": {"f": power(t_ij, b0 = 0.5)},
            "EXP0_12": {"f": neg_exp(t_ij, b0 = 0.12)}, 
            "EXP0_15": {"f": neg_exp(t_ij, b0 = 0.15)},
            "EXP0_22": {"f": neg_exp(t_ij, b0 = 0.22)}, 
            "EXP0_45": {"f": neg_exp(t_ij, b0 = 0.45)},
            "EXP_CUS": {"f": neg_exp(t_ij, b0 = 0.1)},
            "HN1997": {"f": neg_exp(t_ij, b0 = 0.1813)},
            "MGAUS10": {"f": mgaus(t_ij, b0 = 10)}, 
            "MGAUS40": {"f": mgaus(t_ij, b0 = 40)}, 
            "MGAUS100": {"f": mgaus(t_ij, b0 = 100)}, 
            "MGAUS180": {"f": mgaus(t_ij, b0 = 180)},
            "MGAUSCUS": {"f": mgaus(t_ij, b0 = 360)},
            "CUMR05": {"f": cumr(t_ij, t_bar = 5)},
            "CUMR10": {"f": cumr(t_ij, t_bar = 10)},
            "CUMR15": {"f": cumr(t_ij, t_bar = 15)},
            "CUMR20": {"f": cumr(t_ij, t_bar = 20)}, 
            "CUMR30": {"f": cumr(t_ij, t_bar = 30)}, 
            "CUMR40": {"f": cumr(t_ij, t_bar = 40)},
            "CUMR45": {"f": cumr(t_ij, t_bar = 45)},
            "CUMR60": {"f": cumr(t_ij, t_bar = 60)},
            "CUML10": {"f": cuml(t_ij, t_bar = 10)}, 
            "CUML20": {"f": cuml(t_ij, t_bar = 20)}, 
            "CUML30": {"f": cuml(t_ij, t_bar = 30)}, 
            "CUML40": {"f": cuml(t_ij, t_bar = 40)}
            }

        return p[f_name]["f"]