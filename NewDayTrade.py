import numpy as np
import pandas as pd
from higgsboom.MarketData.CSecurityMarketDataUtils import *
import matplotlib.pyplot as plt

class DT:
    etfNumber = '510050.SH'
    date = '20200423'
    tradelist = np.zeros((1, 1))
    cash_component = 0

    # will set the etf number, date and the etf trade list of the day.
    def __init__(self, etfNumber, date):
        self.etfNumber = etfNumber
        self.date = date
        DT.get_trade_list(self)
        DT.get_etf_TAQ_array(self)
        DT.get_stock_TAQ_array(self)
        DT.get_return_array(self)

    # this function will update trade list to the current date.
    def get_trade_list(self):
        date = self.date
        etfNumber = self.etfNumber

        data = np.array(
            np.genfromtxt('.\\tradelist\\' + etfNumber[0:6] + '\\' + '510300' + date + '.TXT', dtype=str, delimiter='|',
                          usecols=np.arange(0, 7),
                          skip_header=14, skip_footer=1))

        i = 0
        while i < data.shape[0]:
            if data[i, 0][0] == '6' or data[i, 0][0] == '9':

                data[i, 0] = data[i, 0] + ".SH"
            elif data[i, 0][0] == '3' or data[i, 0][0] == '0':
                data[i, 0] = data[i, 0] + ".SZ"

            i += 1
        cp = np.array(
            np.genfromtxt('.\\tradelist\\' + etfNumber[0:6] + '\\' + '510300' + date + '.TXT', dtype=str,skip_header=7, skip_footer=301))
        cp = float(str(cp[0]).replace('EstimateCashComponent=',''))
        self.tradelist = data
        self.cash_component = cp

    # set the dir of fund&security.
    secUtils = CSecurityMarketDataUtils('Z:/StockData', 'GTALocalData')

    #store data in memory
    etfArray = np.zeros((0,0))
    etfdf = secUtils.FundTAQDataFrame(etfNumber, date)

    # get the fund taq of the trading time horizon
    def get_etf_TAQ_array(self):
        fundTAQ = self.secUtils.FundTAQDataFrame(self.etfNumber, self.date)
        fundArray = np.array(fundTAQ)
        fundArray = fundArray[fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')] < '15:00:00.000']
        fundArray = fundArray[fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')] > '09:30:00.000']
        self.etfArray = fundArray
        rtarr = np.zeros((fundArray.shape[0],7))
        rtarr = np.concatenate((fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')],rtarr),axis = 1)
        setattr(adjDayTrade,'rtarr',rtarr)


    # get the stock taq of the trading time horizon
    def get_stock_TAQ_array(self):
        tradelist = self.tradelist
        for i in tradelist[:,0]:
            namedf = i+'df'
            namearr = i+'arr'
            stockTAQ = self.secUtils.StockTAQDataFrame(i, self.date)
            stockArr = np.array(stockTAQ)
            stockArr = stockArr[stockArr[:, stockTAQ.columns.values.tolist().index('TradingTime')] < '15:00:00.000']
            stockArr = stockArr[stockArr[:, stockTAQ.columns.values.tolist().index('TradingTime')] >= '09:30:00.000']
            setattr(adjDayTrade, namedf, stockTAQ)
            setattr(adjDayTrade, namearr, stockArr)

    # will return 0 if there is not enough stock/etf to trade, else will return total return, counted as 900000shares
    def get_discount_etf(self, tradetime):
        fundTAQ = self.etfdf
        fundtaq = self.etfArray
        ttshare = 900000
        current_share = 0
        ttcost = 0
        i = 0
        # return only the row at trade time
        fundtaq = fundtaq[fundtaq[:, fundTAQ.columns.values.tolist().index('TradingTime')] == tradetime]
        i_s10 = fundTAQ.columns.values.tolist().index('SellVolume10')
        i_s1 = fundTAQ.columns.values.tolist().index('SellVolume01')
        i_sp10 = fundTAQ.columns.values.tolist().index('SellPrice10')
        i_sp1 = fundTAQ.columns.values.tolist().index('SellPrice01')
        sum_vol = fundtaq[0, i_s10:i_s1 + 1].sum()
        # check if there is enough shares to trade
        if ttshare > sum_vol:
            print('cant buy' + self.etfNumber)
            return ttcost
        while i < 10:
            if float(fundtaq[0,i_s1 - i]) < ttshare - current_share:
                current_share += float(fundtaq[0,i_s1 - i])
                ttcost += float(fundtaq[0,i_s1 - i]) * float(fundtaq[0,i_sp1 - i])
                i += 1
            else:
                ttcost += float(ttshare - current_share) * float(fundtaq[0,i_sp1 - i])
                current_share += ttshare - current_share
                i = 10
        #print(ttcost)
        return ttcost

    def get_premium_etf(self, tradetime):
        fundTAQ = self.etfdf
        fundtaq = self.etfArray
        ttshare = 900000
        current_share = 0
        ttreturn = 0
        i = 0

        fundtaq = fundtaq[fundtaq[:, fundTAQ.columns.values.tolist().index('TradingTime')] == tradetime]

        i_b10 = fundTAQ.columns.values.tolist().index('BuyVolume10')
        i_b1 = fundTAQ.columns.values.tolist().index('BuyVolume01')
        i_bp10 = fundTAQ.columns.values.tolist().index('BuyPrice10')
        i_bp1 = fundTAQ.columns.values.tolist().index('BuyPrice01')
        sum_vol = fundtaq[0, i_b1:i_b10 + 1].sum()

        # check if there is enough shares to trade
        if ttshare > sum_vol:
            print('cant sell ' + self.etfNumber)
            return ttreturn
        while i < 10:
            if float(fundtaq[0,i_b1 + i]) < ttshare - current_share:
                current_share += float(fundtaq[0,i_b1 + i])

                ttreturn += float(fundtaq[0,i_b1 + i]) * float(fundtaq[0,i_bp1 + i])
                i += 1
            else:
                ttreturn += float(ttshare - current_share) * float(fundtaq[0,i_bp1 + i])

                current_share += ttshare - current_share

                i = 10

        return ttreturn

    # this function helps calculate the premium stock cost, returns the cost of buying a single stock
    def get_stock_buy_cost(self,stockNumber,tradetime,quant):
        stockTAQ = getattr(adjDayTrade,stockNumber+'df')
        stocktaq = getattr(adjDayTrade,stockNumber+'arr')
        ttshare = quant
        current_share = 0
        ttcost = 0
        i = 0
        # return on the row at trade time
        stocktaq = stocktaq[stocktaq[:, stockTAQ.columns.values.tolist().index('TradingTime')] <= tradetime]
        stocktaq = stocktaq[-1, :]

        # get crucial index
        i_s10 = stockTAQ.columns.values.tolist().index('SellVolume10')
        i_s1 = stockTAQ.columns.values.tolist().index('SellVolume01')
        i_sp10 = stockTAQ.columns.values.tolist().index('SellPrice10')
        i_sp1 = stockTAQ.columns.values.tolist().index('SellPrice01')

        sum_vol = stocktaq[i_s10:i_s1 + 1].sum()
        if ttshare > sum_vol:
            print('cant buy' + stockNumber)
            return ttcost
        while i < 10:
            if float(stocktaq[i_s1 - i]) < ttshare - current_share:
                current_share += float(stocktaq[i_s1 - i])
                ttcost += float(stocktaq[i_s1 - i]) * float(stocktaq[i_sp1 - i])
                i += 1
            else:
                ttcost += float(ttshare - current_share) * float(stocktaq[i_sp1 - i])
                current_share += ttshare - current_share
                i = 10
        return ttcost


    # will return 0 if  there is not enough stock/etf to trade
    def get_premium_IOPV(self, tradetime):
        tradelist = self.tradelist
        i = 0
        ttcost = 0
        while i < float(tradelist.shape[0]):
            if float(tradelist[i,3]) == 2:
                ttcost += float(tradelist[i,5])
                i += 1
            elif float(tradelist[i,3]) == 4:
                ttcost += float(tradelist[i,5])
                i += 1
            else:
                stockNumber = str(tradelist[i, 0])
                stockQuant = float((tradelist[i, 2]))
                stockcst = self.get_stock_buy_cost(stockNumber,tradetime,stockQuant)
                if stockcst == 0:
                    return float(0)
                ttcost += stockcst
                i += 1
        ttcost += self.cash_component
        #print(ttcost)

        return ttcost

    def get_stock_sell_return(self,stockNumber,tradetime,quant):
        stockTAQ = getattr(adjDayTrade,stockNumber+'df')
        stocktaq = getattr(adjDayTrade,stockNumber +'arr')
        ttshare = quant
        current_share = 0
        ttreturn = 0
        i = 0
        # return on the row at trade time
        stocktaq = stocktaq[stocktaq[:, stockTAQ.columns.values.tolist().index('TradingTime')] <= tradetime]
        stocktaq = stocktaq[-1, :]


        # get crucial index
        i_b10 = stockTAQ.columns.values.tolist().index('BuyVolume10')
        i_b1 = stockTAQ.columns.values.tolist().index('BuyVolume01')
        i_bp10 = stockTAQ.columns.values.tolist().index('BuyPrice10')
        i_bp1 = stockTAQ.columns.values.tolist().index('BuyPrice01')

        sum_vol = stocktaq[i_b1:i_b10 + 1].sum()
        if ttshare > sum_vol:
            print('cant sell' + stockNumber)
            return ttreturn
        while i < 10:
            if float(stocktaq[i_b1 - i]) < ttshare - current_share:
                current_share += float(stocktaq[i_b1 + i])
                ttreturn += float(stocktaq[i_b1 + i]) * float(stocktaq[i_bp1 + i])
                i += 1
            else:
                ttreturn += float(ttshare - current_share) * float(stocktaq[i_bp1 + i])
                current_share += ttshare - current_share
                i = 10
        return ttreturn


    def get_discount_IOPV(self, tradetime):
        tradelist = self.tradelist
        i = 0
        ttreturn = 0
        while i < float(tradelist.shape[0]):
            if float(tradelist[i, 3]) == 2:
                ttreturn += float(tradelist[i, 5])
                i += 1
            elif float(tradelist[i, 3]) == 4:
                ttreturn += float(tradelist[i, 5])
                i += 1
            else:
                stockNumber = str(tradelist[i, 0])
                stockQuant = float((tradelist[i, 2]))
                stockreturn = self.get_stock_sell_return(stockNumber, tradetime, stockQuant)
                if stockreturn == 0:
                    return float(0)
                ttreturn += stockreturn
                i += 1
        ttreturn += self.cash_component
        #print(ttreturn)
        return ttreturn

a = adjDayTrade(etfNumber, '20200102')



