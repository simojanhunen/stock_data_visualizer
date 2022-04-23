"""
Handles communicating with different stock APIs
"""


import pandas_datareader as pdd
import pandas as pd
from enum import Enum


class StockTimeFrame(Enum):
    """
    Available stock time frames
    """

    YTD = 0
    DAY = 1
    WEEK = 2
    YEAR1 = 3
    YEAR3 = 4
    YEAR5 = 5
    MAX = 6

    def get_dates(self):
        """
        Returns end and start date for the chosen enumeration, e.g.,
            return (start_date, end_date)
        """
        raise NotImplementedError()


class StockDataHandling:
    """
    Stock data handling class
    """

    def __init__(self):
        pass

    def get_available_time_frames(self):
        return STOCK_TIME_FRAMES

    def get_yahoo_stock(self, stock_ticker, time_frame):
        if time_frame == StockTimeFrame.YTD:
            return pdd.DataReader(stock_ticker, "yahoo", "2022-01-01", "2022-04-23")
        elif time_frame == StockTimeFrame.DAY:
            raise NotImplementedError()
        elif time_frame == StockTimeFrame.WEEK:
            raise NotImplementedError()
        elif time_frame == StockTimeFrame.YEAR1:
            raise NotImplementedError()
        elif time_frame == StockTimeFrame.YEAR3:
            raise NotImplementedError()
        elif time_frame == StockTimeFrame.YEAR5:
            raise NotImplementedError()
        elif time_frame == StockTimeFrame.MAX:
            raise NotImplementedError()

    def normalize_stock_data(stock_data_df):
        normalized_stock_data_df = (
            stock_data_df - stock_data_df.mean()
        ) / stock_data_df.std()

        return normalized_stock_data_df
