import numpy as np
import pandas as pd



date = '20201116'
etfNumber = '588000'

data = np.genfromtxt('.\\tradelist\\' + etfNumber[0:6] + '\\' + 'fm288etfd' + date + '001.txt', dtype=str,delimiter= 'no way u can delim')

i = 0
data = np.row_stack(data)
del_list = []

cp = float(str(data[1]).split('|')[18])

while i < data.shape[0]:
    if data[i, 0][1] != ' ':
        del_list.append(i)

    i += 1

        # get the array of 300etf before formatting, which contains only 1 row with all the information inside.
data = np.delete(data, del_list, axis=0)

        # get the array of trade list by loops
index = 1
dtarr = np.array([data[0, :][0].split('|')])
while index < data.shape[0]:
    lst = data[index, :]
    lst = np.array([lst[0].split('|')])
    dtarr = np.concatenate((dtarr, lst))
    index += 1
dtarr = dtarr[:,2:]
print(dtarr)
        # format the stock number with .SZ or .SH at the end
i2 = 0
while i2 < data.shape[0]:
    if dtarr[i2, 0][0] == '6' or dtarr[i2, 0][0] == '9':

        dtarr[i2, 0] = dtarr[i2, 0].strip() + ".SH"
    elif dtarr[i2, 0][0] == '3' or dtarr[i2, 0][0] == '0':
        dtarr[i2, 0] = dtarr[i2, 0].strip() + ".SZ"
    i2 += 1

print(dtarr.shape[0])