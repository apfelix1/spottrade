from higgsboom.MarketData.CSecurityMarketDataUtils import *

secUtils = CSecurityMarketDataUtils('Z:/StockData')
df = secUtils.FundTAQDataFrame('515580.SH', '20200714')
df.to_csv('.\\test.csv')
print(secUtils.FundTAQDataFrame('515580.SH', '20200714'))
