#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comparing systems

"""
# import 
import numpy as np
from scipy.stats import t

#%% The given data 
# store the mean response times in 2-D numpy arrays
# Each column is for a system
mrt_sys = np.array([ [255.4681, 115.9830, 2.0378, 1.3385, 1.2385, 1.2514, 3.5463, 11.2547, 22.0430],
                     [256.9938, 116.9345, 2.7114, 1.3456, 1.2182, 1.2761, 1.6443, 12.3897, 21.1709],
                     [267.5571, 109.3999, 2.2161, 1.3725, 1.2405, 1.2463, 2.2030, 13.7304, 21.2049],
                     [277.7778, 115.0480, 2.3571, 1.3042, 1.2166, 1.2299, 2.4591, 13.5199, 20.0498],
                     [261.8503, 106.8980, 2.0405, 1.3622, 1.2363, 1.2626, 2.2128, 12.2453, 19.1446],
                     [247.3947, 106.7058, 2.3168, 1.3354, 1.2293, 1.2584, 1.9963, 11.7397, 20.9306],
                     [257.7656, 104.1080, 2.0971, 1.3721, 1.2267, 1.2380, 3.2049, 11.3209, 20.7089],
                     [243.0247, 114.0377, 2.5007, 1.3512, 1.2393, 1.2589, 1.7564, 12.7926, 19.9358]])
#the significance
p = 0.95 

#%% Solution
# Compute the following differenes
# System n0=1 - System n0=2
dt12 = mrt_sys[:,0]- mrt_sys[:,1]
# System n0=2 - System n0=3
dt23 = mrt_sys[:,1]- mrt_sys[:,2]
# System n0=3 - System n0=4
dt34 = mrt_sys[:,2]- mrt_sys[:,3]
# System n0=4 - System n0=5
dt45 = mrt_sys[:,3]- mrt_sys[:,4]
# System n0=5 - System n0=6
dt56 = mrt_sys[:,4]- mrt_sys[:,5]
# System n0=6 - System n0=7
dt67 = mrt_sys[:,5]- mrt_sys[:,6]
# System n0=7 - System n0=8
dt78 = mrt_sys[:,6]- mrt_sys[:,7]
# System n0=8 - System n0=9
dt89 = mrt_sys[:,7]- mrt_sys[:,8]

# multiplier for confidence interval
num_tests = mrt_sys.shape[0]
mf = t.ppf(1-(1-p)/2,num_tests-1)/np.sqrt(num_tests)

# To compute the confidence interval
pm1 = np.array([-1,1])

# confidence interval for dt12
ci12 = np.mean(dt12) + pm1 * np.std(dt12, ddof=1) * mf

# confidence interval for dt23
ci23 = np.mean(dt23) + pm1 * np.std(dt23, ddof=1) * mf

# confidence interval for dt34
ci34 = np.mean(dt34) + pm1 * np.std(dt34, ddof=1) * mf

# confidence interval for dt45
ci45 = np.mean(dt45) + pm1 * np.std(dt45, ddof=1) * mf

# confidence interval for dt56
ci56 = np.mean(dt56) + pm1 * np.std(dt56, ddof=1) * mf

# confidence interval for dt67
ci67 = np.mean(dt67) + pm1 * np.std(dt67, ddof=1) * mf

# confidence interval for dt78
ci78 = np.mean(dt78) + pm1 * np.std(dt78, ddof=1) * mf

# confidence interval for dt89
ci89 = np.mean(dt89) + pm1 * np.std(dt89, ddof=1) * mf

print(ci12,ci23,ci34,ci45,ci56,ci67,ci78,ci89)
# %%
