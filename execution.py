from higgsboom.MarketData.CSecurityMarketDataUtils import *

secUtils = CSecurityMarketDataUtils('Z:/StockData')
fundTAQ = secUtils.FundTAQDataFrame('588090.SH', '20201117')
print(fundTAQ
      )
fundTAQ.to_csv('.\\fundtest.csv')
