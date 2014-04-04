import matplotlib.pyplot as plt
import pickle
import numpy as np
from common import *
from observer import *
from overlord import *
import os

# read in price data
price_data = loadData('data/btc_usd_btce.txt')

x = dict()

# open up every daily_percent* file and add it in.
results_dir = [result for result in os.listdir('results/')  if 'daily_percent' in result]
for result in results_dir:
    with open('results/'+result,'rb') as f:
        while True:
            try:
                tmp = pickle.load(f)
                x = dict(x.items() + tmp.items())
            except EOFError:
                print 'Done Loading results/%s' % result
                break
        
x_list = []
action_list = []
for key in x.keys():
    x_list.append(x[key][0])
    action_list.append(x[key][1])
    
timeFrame=min([len(i) for i in x_list])
square_x = [i[0:timeFrame] for i in x_list]
square_action = [i[0:timeFrame] for i in action_list]
truncated_time = price_data[1,0:timeFrame]
truncated_price = price_data[0,0:timeFrame]

x_array = np.array(square_x)
action_array = np.array(square_action)

bestMethod = []
movingStrategy = []
changePoints = []
changeTimes = []
reducedMaxes = []

absolute_max = []
inertial_max = [(0,-1)]

orders = []
actions = []
inertia = 1.05
curMethod = -9999
current_max_method_index = -1

'''
Goal is to move through follow-up time and find 3 quantities.
1. the ABSOLUTE maximum profit at each time point, what strategy that used
2. a generally best method that resists switching methds at each time point

'''
for i in range(timeFrame):

    if current_max_method_index != -1 and action_array[current_max_method_index,i] != 0:
        orders.append(truncated_price[i])
        actions.append(action_array[current_max_method_index,i])
    
    # max VALUEat current time
    current_max_value=max(x_array[:,i])
    
    # INDEX strategy that maximuzes
    current_max_method_index=np.where(x_array[:,i]==current_max_value)[0][0]
    current_max_method = x.keys()[current_max_method_index]
    # add max value
    absolute_max.append((current_max_value,current_max_method_index))


    # if current best method is significantly better than last method
    if i == 0 or current_max_value > inertia * inertial_max[-1][0] :
        inertial_max.append((current_max_value,current_max_method_index))
    # otherwise keep using old method
    else:
        inertial_max.append((x_array[inertial_max[-1][1],i],inertial_max[-1][1]))
        

lastOrder = 0
profit_percent=1
for i in range(len(orders)):
    if actions[i] == lastOrder: pass
    else:
        print profit_percent
        profit_percent = profit_percent* orders[i]**actions[i]
        lastOrder = actions[i]
        


    

absolute_array = np.array(absolute_max)
inertial_array = np.array(inertial_max)

plt.plot(inertial_array[:,0])
plt.plot(absolute_array[:,0])
plt.show()





'''
    # check if same method as last time    
    if curMethod == x_max[i][1]:   pass
    else:
        # indeces of changes
        changePoints.append(i)
        # times of changes
        changeTimes.append(truncated_time[i])
        # reduced list
        reducedMaxes.append(curBest)
        
        # update new current method
        curMethod = x.keys()[curBest]
'''

'''
curX = -9999
changePoints = []
changeTimes = []
reducedMaxes = []
for i in range(timeFrame):
    # if still the same -- skip
    if curX == bestMethod[i]:    pass
    else:
        changePoints.append(i)
        changeTimes.append(truncated_time[i])
        reducedMaxes.append(curX)
        curX = bestMethod[i]
plt.plot(truncated_time,x_max)
plt.vlines(changeTimes,0,1.1*max(x_max),'g',linewidth=1)
plt.show()
'''