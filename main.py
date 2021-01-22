import pandas as pd
import numpy as np
from higgsboom.FuncUtils.DateTime import *



tdPeriodList = TradingDays(startDate='20200101', endDate='20201231')
list = []
for i in tdPeriodList:
    i = i.replace('-','')
    element = 'https://www.huatai-pb.com/etf-web/etf/download?filePath=512510'+i+'.TXT'
    list.append(element)
listarr = np.array(list)
listarr = np.row_stack(listarr)

print(listarr
      )
a = pd.DataFrame(listarr)

a.to_csv(r'.\test.csv', index = False)




