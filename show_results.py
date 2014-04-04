import os
import numpy as np
import matplotlib.pyplot as plt

pwd='/media/Big Daddy/New_Documents/python/python_projects/trading/results'
os.chdir(pwd)
all_files = os.listdir('./')
short_updates = [i for i in all_files if 'short' in i]

with open('all_results.csv','w') as outF:
    results = []
    for i in short_updates:
        with open(i,'r') as f:
            for line in f:
                results.append([float(i) for i in line.strip().split(',')])
                outF.write(line)

results = np.array(results)
#     1  2    3      4      5        6       7
#   (ma,md,smooth,percent,riseTol,lossTol, profit)
mas = list(set(results[:,1]))
mds = list(set(results[:,2]))
smooths = list(set(results[:,3]))
percents = list(set(results[:,4]))
riseTols = list(set(results[:,5]))
lossTols = list(set(results[:,6]))
mas.sort()
mds.sort()
smooths.sort()
percents.sort()
riseTols.sort()
lossTols.sort()

#plot profit as function of each pair of 
fig = plt.figure()
ax1 =fig.add_subplot(111) 

fixedValue1 = riseTols[0]
fixedValue2 = lossTols[0]
fixedValue3 = percents[0]
fixedValue4 = smooths[0]

colors = dict()
colors[20] = 'b'
colors[60] = 'r'
colors[100] = 'g'
colors[200] = 'm'


for s in smooths:
    for p in percents:
        for m in mas:
            profitLine = [i[7] for i in results[results[:,2].argsort()] if i[1]==m and fixedValue1 == i[5] and fixedValue2 == i[6] and p == i[4] and s == i[3]]
            xLine = [i[2] for i in results[results[:,2].argsort()] if i[1]==m and fixedValue1 == i[5] and fixedValue2 == i[6] and p == i[4] and s == i[3]]
            ax1.plot(xLine,profitLine, colors[m],linewidth=percents.index(p)**2+1)
    
fig.show()

mas.index(200)
