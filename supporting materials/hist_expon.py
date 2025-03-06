#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np 
import matplotlib.pyplot as plt
import random 

#from test 5
alpha0 = 1.4
alpha1 = 3.2
eta0 = 3.4
eta1 = 3.7
beta0 = 4.1
sent = 0 # or 1 in test for group 1 servers

# Generate 10,000 random service times according to PDF
n = 10000
num = 0
x = []
while num < n :
    u = random.random()
    if sent:
        tmp = u * (alpha1**(-eta1))
        service_time_next_arrival = (eta1/tmp) ** (1/(eta1+1))
    else:
        tmp = u*(alpha0**(-eta0) - beta0**(-eta0))
        service_time_next_arrival = (eta0/tmp) ** (1/(eta0+1))

    x.append(service_time_next_arrival)

    num = num+1

x = np.array(x)

# To check the numbers are really exponentially distributed
# Plot an histogram of the number 
nb = 50 # Number of bins in histogram 
freq, bin_edges = np.histogram(x, bins = nb, range=(0,np.max(x)))

# Lower and upper limits of the bins
bin_lower = bin_edges[:-1]
bin_upper = bin_edges[1:]


bin_center = (bin_lower+bin_upper)/2
bin_width = bin_edges[1]-bin_edges[0]

plt.bar(bin_center,freq,width=bin_width)
plt.title('Histogram of 10^4 exponentially distributed generated service time')
plt.savefig('hist_expon.png')



