#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This program reads in an input argument (which is expected to be
a positive integer) and write some text to a file with name
dummy_*.txt where * is the input argument 


"""

import sys 
import os
import numpy as np 
import random
#
# Reproduce result
#
# save random state
# import pickle
# rand_state = random.getstate()
# pickle.dump( rand_state, open( "simulation_currernt_state.p", "wb" ) )

# access saved random state
# rand_state = pickle.load( open( "simulation_current_state.p", "rb" ) )
# random.setstate(rand_state)

def sim_mmm_func(mode,m,n0,t_limit,inter=[],service=[],time_end=None,lamb=None,a2l=None,a2u=None,p0=None,alpha0=None,beta0=None,eta0=None,alpha1=None,eta1=None,mu=None):
    #
    #For transient part removal
    traces_0 = []
    traces_1 = []
    #
    #initilising record of jobs
    record = []
    response_time_cumulative_0 = 0
    response_time_cumulative_1 = 0 
    num_customers_served_0 = 0
    num_customers_served_1 = 0

    # Initialising the arrival event 
    if mode == 'random':
        #
        #for testing of probability of sending job to 1/0
        job_numbers = 0
        job_sent_to_0 = 0
        #
        next_arrival_time = random.expovariate(lamb) * random.uniform(a2l,a2u)
        sent = random.choices([0,1],[p0,1-p0])
        sent = sent[0]
        u = random.random()
        #initialising according to PDF
        if sent:
            tmp = u * (alpha1**(-eta1))
            service_time_next_arrival = (eta1/tmp) ** (1/(eta1+1))
        else:
            tmp = u*(alpha0**(-eta0) - beta0**(-eta0))
            service_time_next_arrival = (eta0/tmp) ** (1/(eta0+1))
            job_sent_to_0 = job_sent_to_0 + 1
        #
        #for testing of probability of sending job to 1/0
        job_numbers = job_numbers + 1
        #
    else: #trace mode
        next_arrival_time = inter[0]
        service_time_next_arrival = service[0][0]
        sent = service[0][1]
        trace_index = 1
    
    # Initialise the departure event to empty
    next_departure_time = np.empty((m,))
    next_departure_time[:] = np.inf

    # Intialise the master clock 
    master_clock = 0 
    
    # Intialise servers status
    server_busy = np.full((m,), False, dtype=bool)
    
    # Initialise arrival_time_next_departure
    arrival_time_next_departure = np.zeros((m,))

    #initialise if the job is marked as reprocessed and its corresponding service time
    reprocessed = np.full((m,), False, dtype=bool)
    service_time_reprocessed = np.zeros((m,))

    # Initialise queues for group 0 and group 1 respectively
    queue0 = []
    queue1 = []
    queue1_reprocess = []
    queue0_length = 0
    queue1_length = 0
    
    if mode == 'random':
        # Start iteration until the end of simulation time
        while master_clock < time_end:
 
            first_departure_time = np.min(next_departure_time)
            first_departure_server = np.argmin(next_departure_time)

            if next_arrival_time < first_departure_time:
                next_event_time = next_arrival_time
                next_event_type = 'arrival' 
            else:
                next_event_time = first_departure_time
                next_event_type = 'departure'
            
            #update master clock
            master_clock = next_event_time

            if next_event_type == 'arrival': # an arrival

                if sent == 0: 
                    if np.all(server_busy[:n0]): # if all 0 servers are busy
                        # add customer to queue and increment queue length
                        queue0.append([next_arrival_time, service_time_next_arrival])
                        queue0_length = queue0_length + 1        
                    else: # some servers are idle 
                        # Send the customer to any available server
                        idle_server = np.min(np.where(~server_busy[:n0]))

                        #check if the service time is over the time limit for group 0
                        if service_time_next_arrival > t_limit:
                            #job will be killed after limit time 
                            next_departure_time[idle_server] = next_arrival_time + t_limit
                            arrival_time_next_departure[idle_server] = next_arrival_time

                            #record the service time to be futhur processed by group 1 later
                            service_time_reprocessed[idle_server] = service_time_next_arrival
                        else:
                            next_departure_time[idle_server] = next_arrival_time + service_time_next_arrival
                            arrival_time_next_departure[idle_server] = next_arrival_time

                        #set the coresponding server to busy
                        server_busy[idle_server] = True        
                else: # sent to group 1 
                    if np.all(server_busy[n0:]): # if all 1 servers are busy
                        # add customer to queue and increment queue length
                        queue1.append([next_arrival_time, service_time_next_arrival])
                        queue1_length = queue1_length + 1

                        #add a indicator meaning this job is not a reprocessed job when retriving from queue
                        queue1_reprocess.append(False)        
                    else: # some servers are idle 
                        # Send the customer to any available server
                        idle_server = np.min(np.where(~server_busy[n0:])) + n0

                        #update next departure time and arrival time and server status
                        next_departure_time[idle_server] = next_arrival_time + service_time_next_arrival
                        arrival_time_next_departure[idle_server] = (next_arrival_time)

                        server_busy[idle_server] = True

                # generate a new job and schedule its arrival 
                next_arrival_time = master_clock + random.expovariate(lamb) * random.uniform(a2l,a2u)
                sent = random.choices([0,1],[p0,1-p0])
                sent = sent[0]
                u = random.random()
                if sent:
                    tmp = u * (alpha1**(-eta1))
                    service_time_next_arrival = (eta1/tmp) ** (1/(eta1+1))
                else:
                    tmp = u*(alpha0**(-eta0) - beta0**(-eta0))
                    service_time_next_arrival = (eta0/tmp) ** (1/(eta0+1))
                    job_sent_to_0 = job_sent_to_0 + 1
                job_numbers = job_numbers + 1
    
            else: # a departure 
                # 
                # Update the variables:
                # 1) response_time_cumulative for corresponding group
                # 2) num_customers_served for corresponding group
                #
                #default negetive value indicate job departured from group0 will be reprocessed
                arrive_record = -1

                if first_departure_server < n0: # departuring from group 0 server(s)

                    if service_time_reprocessed[first_departure_server]: # departuring job is a killed job

                        if np.all(server_busy[n0:]): #if all group 1 servers are busy
                            #add killed job to queue
                            queue1.append([arrival_time_next_departure[first_departure_server],service_time_reprocessed[first_departure_server]])
                            queue1_length = queue1_length + 1
                            #add indicator as this is a reprocessed job in queue
                            queue1_reprocess.append(True)
                        else:
                            #add killed job to idle group 1 server 
                            idle_server = np.min(np.where(~server_busy[n0:])) + n0
                            #update departure time, arrival time, server status and mark as reprocessed job
                            next_departure_time[idle_server] = master_clock + service_time_reprocessed[first_departure_server]
                            arrival_time_next_departure[idle_server] = arrival_time_next_departure[first_departure_server]
                            server_busy[idle_server] = True
                            reprocessed[idle_server] = True
                        
                        #reset reprocessed job as default 
                        service_time_reprocessed[first_departure_server] = 0.0

                    else: # departuring job is a completed from gourp 0
                        #
                        # Store response time for transient removal
                        traces_0. append(master_clock - arrival_time_next_departure[first_departure_server])
                        #
                        #update the reletive variables related to mrt of group 0
                        response_time_cumulative_0 = response_time_cumulative_0 + \
                                                master_clock - \
                                                arrival_time_next_departure[first_departure_server]
                        num_customers_served_0 = num_customers_served_0 + 1
                        job_group = '0'
                        departure_record = master_clock
                        arrive_record = arrival_time_next_departure[first_departure_server]

                    #start waiting job in queue if there is any
                    if queue0_length:
                        first_job_in_the_buffer = queue0.pop(0)
                        queue0_length = queue0_length - 1
                        
                        arrival_time_next_departure[first_departure_server] = first_job_in_the_buffer[0]

                        #update variables accordingly, check if service time is over time limit for group 0
                        if first_job_in_the_buffer[1] > t_limit:
                            next_departure_time[first_departure_server] = master_clock + t_limit
                            service_time_reprocessed[first_departure_server] = first_job_in_the_buffer[1]
                        else:
                            next_departure_time[first_departure_server] = \
                                master_clock + first_job_in_the_buffer[1]
                    
                    else: # queue empty
                        next_departure_time[first_departure_server] = np.inf
                        server_busy[first_departure_server] = False

                else:# departuring from group 1 server(s)
                    if reprocessed[first_departure_server] == False: #if job is not reprocessed job
                        #
                        # Store response time for transient removal
                        traces_1. append(master_clock - arrival_time_next_departure[first_departure_server])
                        #
                        response_time_cumulative_1 = response_time_cumulative_1 + \
                                                master_clock - \
                                                arrival_time_next_departure[first_departure_server]
                        num_customers_served_1 = num_customers_served_1 + 1
                        job_group = '1'
                        departure_record = master_clock
                        arrive_record = arrival_time_next_departure[first_departure_server]

                    else: #departuring job is reprocessed job
                        
                        #change reprocessed mark to default
                        reprocessed[first_departure_server] = False

                        #update r0 job information
                        job_group = 'r0'
                        departure_record = master_clock
                        arrive_record = arrival_time_next_departure[first_departure_server]
                    

                    if queue1_length: # assign job if there is any in queue1
                        
                        first_job_in_the_buffer = queue1.pop(0)
                        recycle = queue1_reprocess.pop(0)
                        queue1_length = queue1_length - 1
                        
                        next_departure_time[first_departure_server] = \
                            master_clock + first_job_in_the_buffer[1]
                        arrival_time_next_departure[first_departure_server] = first_job_in_the_buffer[0]
                        if recycle:
                            reprocessed[first_departure_server] = True
                    else: # queue empty
                        next_departure_time[first_departure_server] = np.inf
                        server_busy[first_departure_server] = False

                if arrive_record > 0: # if deparuring job is not about to be reprocessed : departuing from the system
                    record.append([arrive_record,departure_record,job_group])
                    
    else:
        # Start iteration until last job departure from the system
        while trace_index < len(inter) or np.any(server_busy):
 
            first_departure_time = np.min(next_departure_time)
            first_departure_server = np.argmin(next_departure_time)

            if next_arrival_time < first_departure_time:
                next_event_time = next_arrival_time
                next_event_type = 'arrival' 
            else:
                next_event_time = first_departure_time
                next_event_type = 'departure'

            #update master clock
            master_clock = next_event_time

            if next_event_type == 'arrival': # an arrival

                if sent == 0: 
                    if np.all(server_busy[:n0]): # if all 0 servers are busy
                        # add customer to queue and increment queue length
                        queue0.append([next_arrival_time, service_time_next_arrival])
                        queue0_length = queue0_length + 1        
                    else: # some servers are idle
                        # Send the customer to any available server 
                        idle_server = np.min(np.where(~server_busy[:n0]))

                        if service_time_next_arrival > t_limit:
                            #job will be killed after limit time 
                            next_departure_time[idle_server] = next_arrival_time + t_limit
                            arrival_time_next_departure[idle_server] = next_arrival_time

                            #record the service time to be futhur processed by group 1 later
                            service_time_reprocessed[idle_server] = service_time_next_arrival
                        else:
                            
                            next_departure_time[idle_server] = next_arrival_time + service_time_next_arrival
                            arrival_time_next_departure[idle_server] = next_arrival_time

                        #set the coresponding server to busy
                        server_busy[idle_server] = True

                else:# sent to group 1 
                    if np.all(server_busy[n0:]): # if all 1 servers are busy
                        # add customer to queue and increment queue length
                        queue1.append([next_arrival_time, service_time_next_arrival])
                        queue1_length = queue1_length + 1

                        #add a indicator meaning this job is not a reprocessed job when retriving from queue        
                        queue1_reprocess.append(False)
                    else: # some servers are idle 
                        # Send the customer to any available server
                        idle_server = np.min(np.where(~server_busy[n0:])) + n0

                        #update next departure time and arrival time and server status
                        next_departure_time[idle_server] = next_arrival_time + service_time_next_arrival
                        arrival_time_next_departure[idle_server] = next_arrival_time
        
                        server_busy[idle_server] = True

                # generate a new job and schedule its arrival
                if trace_index < len(inter):
                    next_arrival_time = master_clock + inter[trace_index]
                    sent = service[trace_index][1]
                    service_time_next_arrival = service[trace_index][0]
                    trace_index = trace_index + 1
                else:
                    #no more arrival job to be acessed, set next arrival to infinity
                    next_arrival_time = np.inf

    
            else: # a departure
                # 
                # Update the variables:
                # 1) response_time_cumulative for corresponding group
                # 2) num_customers_served for corresponding group
                # 
                #default negetive value indicate job departured from group0 will be reprocessed
                arrive_record = -1

                if first_departure_server < n0: # departuring from group 0 server(s)

                    if service_time_reprocessed[first_departure_server]: # departuring job is a killed job

                        if np.all(server_busy[n0:]): #if all group 1 servers are busy
                            #add killed job to queue
                            queue1.append([arrival_time_next_departure[first_departure_server],service_time_reprocessed[first_departure_server]])
                            #add indicator as this is a reprocessed job in queue
                            queue1_reprocess.append(True)
                            queue1_length = queue1_length + 1 
                        else:
                            #add killed job to idle group 1 server 
                            idle_server = np.min(np.where(~server_busy[n0:])) + n0
                            next_departure_time[idle_server] = master_clock + service_time_reprocessed[first_departure_server]
                            arrival_time_next_departure[idle_server] = arrival_time_next_departure[first_departure_server]
                            server_busy[idle_server] = True
                            reprocessed[idle_server] = True

                        #reset reprocessed job as default  
                        service_time_reprocessed[first_departure_server] = 0.0
                    else: # departuring job is a completed job from group 0
                        #update the reletive variables related to mrt of group 0
                        response_time_cumulative_0 = response_time_cumulative_0 + \
                                                master_clock - \
                                                arrival_time_next_departure[first_departure_server]
                        num_customers_served_0 = num_customers_served_0 + 1
                        job_group = '0'
                        departure_record = master_clock
                        arrive_record = arrival_time_next_departure[first_departure_server]

                    #start waiting job in queue if there is any
                    if queue0_length:
                        first_job_in_the_buffer = queue0.pop(0)
                        queue0_length = queue0_length - 1

                        #update variables accordingly, check if service time is over time limit for group 0
                        arrival_time_next_departure[first_departure_server] = first_job_in_the_buffer[0]
                        if first_job_in_the_buffer[1] > t_limit:
                            next_departure_time[first_departure_server] = master_clock + t_limit
                            service_time_reprocessed[first_departure_server] = first_job_in_the_buffer[1]
                        else:
                            next_departure_time[first_departure_server] = \
                                master_clock + first_job_in_the_buffer[1]
                            
                
                    else: # queue empty
                        next_departure_time[first_departure_server] = np.inf
                        server_busy[first_departure_server] = False
                else: # departuring from group 1 server(s)
                    if reprocessed[first_departure_server] == False: #if job is not reprocessed job
                        
                        response_time_cumulative_1 = response_time_cumulative_1 + \
                                                master_clock - \
                                                arrival_time_next_departure[first_departure_server]
                        num_customers_served_1 = num_customers_served_1 + 1

                        job_group = '1'
                        departure_record = master_clock
                        arrive_record = arrival_time_next_departure[first_departure_server]
                    else:#departuring job is reprocessed job

                        #change reprocessed mark to default
                        reprocessed[first_departure_server] = False

                        #update r0 job information
                        job_group = 'r0'
                        departure_record = master_clock
                        arrive_record = arrival_time_next_departure[first_departure_server]
                    

                    if queue1_length: # assign job if there is any in queue1

                        first_job_in_the_buffer = queue1.pop(0)
                        recycle = queue1_reprocess.pop(0)
                        queue1_length = queue1_length - 1
                        
                        next_departure_time[first_departure_server] = \
                            master_clock + first_job_in_the_buffer[1]
                        arrival_time_next_departure[first_departure_server] = first_job_in_the_buffer[0]
                        if recycle:
                            reprocessed[first_departure_server] = True
                    else: # queue empty
                        next_departure_time[first_departure_server] = np.inf
                        server_busy[first_departure_server] = False

                if arrive_record > 0: # if deparuring job is not about to be reprocessed : departuing from the system
                    record.append([arrive_record,departure_record,job_group])

    mean_response_time_0 = response_time_cumulative_0/num_customers_served_0

    mean_response_time_1 = response_time_cumulative_1/num_customers_served_1
    
    mean_result = [mean_response_time_0, mean_response_time_1]
    #
    #test if the probability aligh with given parameter p0
    #print(f'p0 = {p0}, and the actual percentage in this run is {job_sent_to_0/job_numbers}')
    #

    #
    #For the design Probelm
    #
    # w0 = 0.83
    # w1 = 0.059
    # print(mean_response_time_0 * w0 + mean_response_time_1 * w1)
    #
    return mean_result, record, traces_0, traces_1


def main(s):

    cur_path = os.path.dirname(__file__)

    mode_file = 'mode_{}.txt'.format(s)
    rel_path = 'config/{}'.format(mode_file)

    mode_path = os.path.join(cur_path,rel_path)
    with open(mode_path) as file:
        mode = file.readline().strip()

    para_file = 'para_{}.txt'.format(s)
    rel_path = 'config/{}'.format(para_file)
    para_path = os.path.join(cur_path,rel_path)
    with open(para_path) as file:
        n = int(file.readline().strip())
        n0 = int(file.readline().strip())
        T_limit = float(file.readline().strip())
        if mode == 'random':
            time_end = int(file.readline().strip())

    inter_file = 'interarrival_{}.txt'.format(s)
    rel_path = 'config/{}'.format(inter_file)
    inter_path = os.path.join(cur_path,rel_path)
    with open(inter_path) as file:
        if mode == 'random':
            lamb, a2l, a2u = file.readline().strip().split()
            lamb = float(lamb)
            a2l = float(a2l)
            a2u = float(a2u)
        else:
            inter_arrival_time = []
            for line in file.readlines():
                inter_arrival_time.append(float(line.strip()))

    service_file = 'service_{}.txt'.format(s)
    rel_path = 'config/{}'.format(service_file)
    service_path = os.path.join(cur_path,rel_path)
    with open(service_path) as file:
        if mode == 'random':
            p0 = float(file.readline().strip())
            alpha0, beta0, eta0 = file.readline().strip().split()
            alpha1, eta1 = file.readline().strip().split()

            alpha0 = float(alpha0)
            alpha1 = float(alpha1)
            beta0 = float(beta0)
            eta0 = float(eta0)
            eta1 = float(eta1)
        else:
            service_time_and_group = []
            for line in file.readlines():
                (a,b) = line.strip().split()
                a = float(a)
                b= float(b)
                service_time_and_group.append((a,b))
    
    if mode == 'random':
        result1, result2, traces_0, traces_1 = sim_mmm_func(mode,n,n0,T_limit,time_end=time_end,lamb=lamb,a2l=a2l,a2u=a2u,p0=p0,alpha0=alpha0,beta0=beta0,eta0=eta0,alpha1=alpha1,eta1=eta1)
    else:
        result1, result2, traces_0, traces_1 = sim_mmm_func(mode,n,n0,T_limit,inter=inter_arrival_time,service=service_time_and_group)

    

    out_folder = 'output'
    mrt_file = os.path.join(out_folder,'mrt_'+s+'.txt')
    dep_file = os.path.join(out_folder,'dep_'+s+'.txt')
    #
    #For transient removal
    # traces_0_file = os.path.join(out_folder,'traces_0_'+s+'_1.txt')
    # traces_1_file = os.path.join(out_folder,'traces_1_'+s+'_1.txt')
    # with open(traces_0_file,'w') as file:
    #     for trace in traces_0:
    #         file.writelines(str('{:.4f}'.format(trace))+'\n')
    # with open(traces_1_file,'w') as file:
    #     for trace in traces_1:
    #         file.writelines(str('{:.4f}'.format(trace))+'\n') 
    #
    
    with open(mrt_file,'w') as file:
        file.writelines(str('{:.4f}'.format(result1[0]))+' ' +str('{:.4f}'.format(result1[1]))) 
    with open(dep_file,'w') as file:
        for record in result2:
            file.writelines(str('{:.4f}'.format(record[0]))+' '+str('{:.4f}'.format(record[1]))+ ' '+str(record[2])+'\n') 
    

if __name__ == "__main__":
   main(sys.argv[1])
