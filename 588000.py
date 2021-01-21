import math
import datetime
import multiprocessing as mp
import numpy as np
import pandas as pd
from higgsboom.MarketData.CSecurityMarketDataUtils import *
import matplotlib.pyplot as plt


class DT:
    # set the dir of fund&security.
    secUtils = CSecurityMarketDataUtils('Z:/StockData')

    etfNumber = '588000.SH'
    date = '20200102'
    tradelist = np.zeros((1, 1))
    cash_component = 0
    #store data in memory
    etfArray = np.zeros((0,0))
    etfdf = pd.DataFrame
    rtarr = []

    # will set the etf number, date and the etf trade list of the day.
    def __init__(self, etfNumber, date):
        self.etfNumber = etfNumber
        self.date = date


        #DT.get_return_array(self)

    # this function will update trade list to the current date.
    def get_trade_list(self):
        date = self.date
        etfNumber = self.etfNumber

        data = np.genfromtxt('.\\tradelist\\' + etfNumber[0:6] + '\\' + 'fm288etfd' + date + '001.txt', dtype=str,
                             delimiter='no way u can delim')

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
        dtarr = dtarr[:, 2:]

        # format the stock number with .SZ or .SH at the end
        i2 = 0
        while i2 < data.shape[0]:
            if dtarr[i2, 0][0] == '6' or dtarr[i2, 0][0] == '9':

                dtarr[i2, 0] = dtarr[i2, 0].strip() + ".SH"
            elif dtarr[i2, 0][0] == '3' or dtarr[i2, 0][0] == '0':
                dtarr[i2, 0] = dtarr[i2, 0].strip() + ".SZ"
            i2 += 1
        self.tradelist = dtarr
        self.cash_component = cp






    # get the fund taq of the trading time horizon
    def get_etf_TAQ_array(self):
        fundTAQ = self.secUtils.FundTAQDataFrame(self.etfNumber, self.date)
        fundArray = np.array(fundTAQ)
        fundArray = fundArray[fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')] < '14:57:00.000']
        fundArray = fundArray[fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')] > '09:30:00.000']
        self.etfArray = fundArray

        self.etf_i_b10 = fundTAQ.columns.values.tolist().index('BuyVolume10')
        self.etf_i_b1 = fundTAQ.columns.values.tolist().index('BuyVolume01')
        self.etf_i_bp10 = fundTAQ.columns.values.tolist().index('BuyPrice10')
        self.etf_i_bp1 = fundTAQ.columns.values.tolist().index('BuyPrice01')

        self.etf_i_s10 = fundTAQ.columns.values.tolist().index('SellVolume10')
        self.etf_i_s1 = fundTAQ.columns.values.tolist().index('SellVolume01')
        self.etf_i_sp10 = fundTAQ.columns.values.tolist().index('SellPrice10')
        self.etf_i_sp1 = fundTAQ.columns.values.tolist().index('SellPrice01')

        rtarr = np.zeros((fundArray.shape[0],8))
        rtarr = np.concatenate((np.row_stack(fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')]),rtarr),axis = 1)

        stktdarr = np.zeros((fundArray.shape[0],4))
        stktdarr = np.concatenate((np.row_stack(fundArray[:, fundTAQ.columns.values.tolist().index('TradingTime')]),stktdarr),axis = 1)
        stktdarr[:,2] = 1
        stktdarr[:,4] = 1
        setattr(DT,'rtarr',rtarr)
        setattr(DT,'stktdarr',stktdarr)



    def get_discount_etf(self):
        fundtaq = self.etfArray
        i_s10 = self.etf_i_s10
        i_s1 = self.etf_i_s1

        i_sp1 = self.etf_i_sp1
        dcetf = np.zeros((fundtaq.shape[0],1))
        fundtaq = np.concatenate((fundtaq,dcetf),axis = 1 )
        for index in range(fundtaq.shape[0]):
            ttshare = 2600000
            current_share = 0
            ttcost = 0
            i = 0
            # return only the row at trade time

            sum_vol = fundtaq[index, i_s10:i_s1 + 1].sum()
            # check if there is enough shares to trade
            if ttshare > sum_vol:
                print('cant buy' + self.etfNumber )
                fundtaq[index, -1] = 0
            else:
                while i < 10:
                    if float(fundtaq[index, i_s1 - i]) < ttshare - current_share:
                        current_share += float(fundtaq[index, i_s1 - i])
                        ttcost += float(fundtaq[index, i_s1 - i]) * float(fundtaq[index, i_sp1 - i])
                        i += 1
                    else:
                        ttcost += float(ttshare - current_share) * float(fundtaq[index, i_sp1 - i])
                        current_share += ttshare - current_share
                        i = 10
                fundtaq[index, -1] = ttcost

        self.rtarr[:, 2] = fundtaq[:, -1]

    def get_premium_etf(self):
        fundTAQ = self.etfdf
        fundtaq = self.etfArray
        i_b10 = self.etf_i_b10
        i_b1 = self.etf_i_b1
        i_bp10 = self.etf_i_bp10
        i_bp1 = self.etf_i_bp1
        dcetf = np.zeros((fundtaq.shape[0], 1))
        fundtaq = np.concatenate((fundtaq, dcetf), axis=1)
        for index in range(fundtaq.shape[0]):
            ttshare = 2600000
            current_share = 0
            ttreturn = 0
            i = 0

            sum_vol = fundtaq[index, i_b1:i_b10 + 1].sum()
            # check if there is enough shares to trade
            if ttshare > sum_vol:
                print('cant sell' + self.etfNumber)
                fundtaq[index, -1] = 0
            else:
                while i < 10:
                    if float(fundtaq[index, i_b1 + i]) < ttshare - current_share:
                        current_share += float(fundtaq[index, i_b1 + i])
                        ttreturn += float(fundtaq[index, i_b1 + i]) * float(fundtaq[index, i_bp1 + i])
                        i += 1
                    else:
                        ttreturn += float(ttshare - current_share) * float(fundtaq[index, i_bp1 + i])
                        current_share += ttshare - current_share
                        i = 10
                fundtaq[index, -1] = ttreturn


        self.rtarr[:, 1] = fundtaq[:, -1]

    def get_IOPV(self,tradelist, rtarr):

        stockNumber = tradelist[0]

        namearr = stockNumber + 'arr'
        print(namearr)
        stockTAQ = self.secUtils.StockTAQDataFrame(stockNumber, self.date)
        stockArr = np.array(stockTAQ)
        ttindex = stockTAQ.columns.values.tolist().index('TradingTime')

        stockArr = stockArr[stockArr[:, ttindex] <= '14:57:00.000']
        stockArr = stockArr[stockArr[:, ttindex] >= '09:30:00.000']

        adjstockArr = np.zeros((rtarr.shape[0], ttindex))
        adjstockArr = np.concatenate((adjstockArr, np.row_stack(rtarr[:, 0])), axis=1)
        colnum = int(stockArr.shape[1] - adjstockArr.shape[1])
        new0 = np.zeros((rtarr.shape[0], colnum))
        adjstockArr = np.concatenate(
            (adjstockArr, new0), axis=1)

        stkindex = 0
        etfindex = 0
        # make the stkarr same size as etfarr
        while etfindex < rtarr.shape[0]:
            while stkindex < stockArr.shape[0] and stockArr[stkindex, ttindex] <= adjstockArr[etfindex, ttindex]:
                adj_time = adjstockArr[etfindex, ttindex]
                adjstockArr[etfindex, :] = stockArr[stkindex, :]
                adjstockArr[etfindex, ttindex] = adj_time
                stkindex += 1
            if stkindex < stockArr.shape[0] and stockArr[stkindex, ttindex] > adjstockArr[etfindex, ttindex]:
                adj_time = adjstockArr[etfindex, ttindex]
                adjstockArr[etfindex, :] = stockArr[stkindex - 1, :]
                adjstockArr[etfindex, ttindex] = adj_time

            if stkindex == stockArr.shape[0]:
                adj_time = adjstockArr[etfindex, ttindex]
                adjstockArr[etfindex, :] = stockArr[stkindex - 1, :]
                adjstockArr[etfindex, ttindex] = adj_time
            etfindex += 1

        i_s10 = stockTAQ.columns.values.tolist().index('SellVolume10')
        i_s1 = stockTAQ.columns.values.tolist().index('SellVolume01')
        i_sp10 = stockTAQ.columns.values.tolist().index('SellPrice10')
        i_sp1 = stockTAQ.columns.values.tolist().index('SellPrice01')

        i_b10 = stockTAQ.columns.values.tolist().index('BuyVolume10')
        i_b1 = stockTAQ.columns.values.tolist().index('BuyVolume01')
        i_bp10 = stockTAQ.columns.values.tolist().index('BuyPrice10')
        i_bp1 = stockTAQ.columns.values.tolist().index('BuyPrice01')
        stkarr = np.concatenate((np.row_stack(rtarr[:, 0]), adjstockArr[:, i_s10:i_s1 + 1]), axis=1)
        stkarr = np.concatenate((stkarr, adjstockArr[:, i_sp10:i_sp1 + 1]), axis=1)
        stkarr = np.concatenate((stkarr, adjstockArr[:, i_b1:i_b10 + 1]), axis=1)
        stkarr = np.concatenate((stkarr, adjstockArr[:, i_bp1:i_bp10 + 1]), axis=1)

        # end of get stock array

        # get pr iopv
        stockcost = stkarr[:,0]
        stockcost = np.concatenate((np.row_stack(stockcost),np.row_stack(stockcost),np.row_stack(stockcost)),axis = 1)
        stockcost[:,1] = 0
        stockcost[:,2] = 1
        if float(tradelist[3].strip()) == 2 or float(tradelist[ 3].strip()) == 4:
            stockcost[:, 1] = stockcost[:, 1].astype(np.float) + float(tradelist[ 5].strip())
        else:
            stktaq = stkarr
            quant = float((tradelist[2].strip()))

            # -4 current amt -3 total amt -2 stock cost -1 can trade or not
            stktaq = np.concatenate((stktaq, np.zeros((stktaq.shape[0], 4))), axis=1)

            stktaq[:, -3] = stktaq[:, 1:11].astype(np.float).sum(axis=1)
            # change the index to 0 if cant trade
            cant_trade = stktaq[stktaq[:, -3].astype(np.float) < quant]
            cant_trade[:, -1] = 0
            stktaq[stktaq[:, -3].astype(np.float) < quant] = cant_trade
            # find the time tick that can trade
            can_trade = stktaq[stktaq[:, -3].astype(np.float) >= quant]
            can_trade[:, -1] = 1
            index = 0
            while index < 10:
                col1 = can_trade[:, 10 - index]
                col2 = -can_trade[:, -4].astype(np.float) + quant
                minrow = np.array([col1, col2]).transpose()
                minrow = minrow.astype(np.float).min(axis=1)
                can_trade[:, -4] = can_trade[:, -4].astype(np.float) + minrow
                can_trade[:, -2] = can_trade[:, -2].astype(np.float) + can_trade[:, 20 - index].astype(
                    np.float) * minrow
                index += 1
            stktaq[stktaq[:, -3].astype(np.float) >= quant] = can_trade
            stockcost[:, 1] = stockcost[:, 1].astype(np.float) + stktaq[:, -2].astype(np.float)
            stockcost[:, 2] = stockcost[:, 2].astype(np.float) * stktaq[:, -1].astype(np.float)

        # get dc iopv

        stockrev = stkarr[:, 0]
        stockrev = np.concatenate((np.row_stack(stockrev), np.row_stack(stockrev), np.row_stack(stockrev)), axis=1)
        stockrev[:, 1] = 0
        stockrev[:, 2] = 1
        if float(tradelist[3].strip()) == 2 or float(tradelist[3].strip()) == 4:
            stockrev[:, 1] = stockrev[:, 1].astype(np.float) + float(tradelist[5].strip())
        else:
            quant = float((tradelist[2].strip()))
            stocktaq = stkarr

            # return on the row at trade time
            stocktaq = np.concatenate((stocktaq, np.zeros((stocktaq.shape[0], 4))), axis=1)

            stocktaq[:, -3] = stocktaq[:, 21:31].astype(np.float).sum(axis=1)
            cant_trade = stocktaq[stocktaq[:, -3].astype(np.float) < quant]
            cant_trade[:, -1] = 0
            stocktaq[stocktaq[:, -3].astype(np.float) < quant] = cant_trade
            can_trade = stocktaq[stocktaq[:, -3].astype(np.float) >= quant]
            can_trade[:, -1] = 1
            index = 0
            while index < 10:
                col1 = can_trade[:, 21 + index]
                col2 = -can_trade[:, -4].astype(np.float) + quant
                minrow = np.array([col1, col2]).transpose()
                minrow = minrow.astype(np.float).min(axis=1)
                can_trade[:, -4] = can_trade[:, -4].astype(np.float) + minrow
                can_trade[:, -2] = can_trade[:, -2].astype(np.float) + can_trade[:, 31 + index].astype(
                    np.float) * minrow
                index += 1

            stocktaq[stocktaq[:, -3].astype(np.float) >= quant] = can_trade
            stockrev[:, 1] = stockrev[:, 1].astype(np.float) + stocktaq[:, -2].astype(np.float)
            stockrev[:, 2] = stockrev[:, 2].astype(np.float) * stocktaq[:, -1].astype(np.float)

        iopvarr = np.concatenate((stockcost[:,0:3],stockrev[:,1:3]),axis = 1)

        return iopvarr





if __name__ == '__main__':
    maxrate = []
    firstrate = []

    tdPeriodList = TradingDays(startDate='20201116', endDate='20210120')
    for i in tdPeriodList:
        print(i)
        dTypes = ['TAQ']
        i = i.replace("-", "")
        a = DT('588000.SH', i)
        a.get_trade_list()
        a.get_etf_TAQ_array()
        a.get_premium_etf()
        a.get_discount_etf()


        if __name__ == '__main__':

            rtarr = a.rtarr

            tradelist = a.tradelist

            pool = mp.Pool(mp.cpu_count())
            # stklist = pool.starmap(a.get_stock_TAQ_array, [(td,rtarr) for td in tradelist[:,0]])
            # print("stkfinish")

            iopv_list = pool.starmap(a.get_IOPV, [(td, rtarr) for td in tradelist])
            print('finish')

            iopv = iopv_list[0]
            index = 1
            while index < tradelist.shape[0]:

                iopv[:, 1] = iopv[:, 1].astype(np.float) + iopv_list[index][:,1].astype(np.float)
                iopv[:, 2] = iopv[:, 2].astype(np.float) * iopv_list[index][:,2].astype(np.float)
                iopv[:, 3] = iopv[:, 3].astype(np.float) + iopv_list[index][:, 3].astype(np.float)
                iopv[:, 4] = iopv[:, 4].astype(np.float) * iopv_list[index][:, 4].astype(np.float)

                index += 1
            iopv[:, 1] = iopv[:, 1].astype(np.float) + a.cash_component
            iopv[:, 3] = iopv[:, 3].astype(np.float) + a.cash_component
            del iopv_list

            # get iopv into rtarr

            rtarr[:, 3] = iopv[:, 1].astype(np.float) * iopv[:, 2].astype(np.float)
            rtarr[:, 4] = iopv[:, 3].astype(np.float) * iopv[:, 4].astype(np.float)

            # get pr rate

            rtarr_pr = rtarr[rtarr[:, 1].astype(np.float) * rtarr[:, 3].astype(np.float) > 0]
            rtarr_pr[:,5] = (rtarr_pr[:, 1].astype(np.float) - rtarr_pr[:, 3].astype(np.float) - 0.00012 * (
                    rtarr_pr[:, 1].astype(np.float) + rtarr_pr[:, 3].astype(np.float))) / rtarr_pr[:, 3].astype(
                np.float)
            # update the premium row in rtarr
            rtarr[rtarr[:, 1].astype(np.float) * rtarr[:, 3].astype(np.float) > 0][:,5] = rtarr_pr[:,5]


            # get dc rate

            rtarr_dc = rtarr[rtarr[:, 2].astype(np.float) * rtarr[:, 4].astype(np.float) > 0]
            rtarr_dc[:, 6] = (rtarr_dc[:, 4].astype(np.float) - rtarr_dc[:, 2].astype(np.float) - 0.00012 * (
                    rtarr_dc[:, 2].astype(np.float) + rtarr_dc[:, 4].astype(np.float)) - 0.001 * rtarr_dc[:,
                                                                                                 2].astype(
                np.float)) / rtarr_dc[:, 2].astype(np.float)
            # update the discount rate in rtarr
            rtarr[rtarr[:, 2].astype(np.float) * rtarr[:, 4].astype(np.float) > 0] = rtarr_dc


            # get max rate

            rtarr[:,7] = rtarr[:,[5,6]].astype(np.float).max(axis = 1)

            rtarr[rtarr[:, 7].astype(np.float) < 0.0][:,7] = 0.0

            daymax = rtarr[:, 7].astype(np.float).max()

            if rtarr[rtarr[:, 7].astype(np.float) > 0.0][:, 7].shape[0] == 0:
                dayfirst = 0.0
            else:
                dayfirst = rtarr[rtarr[:, 7].astype(np.float) > 0.0][:, 7][0]

            maxrate.append(daymax)
            firstrate.append(dayfirst)



            # pr_iopv = pool.starmap(a.get_premium_IOPV, [(td, stk) for td in tradelist for stk in stklist])


