"""
Handles communicating with different stock APIs
"""


import pandas_datareader as pdd
import pandas as pd
from enum import Enum
from datetime import datetime, timedelta


MIN_READABLE_YEAR = 1971


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
    CUSTOM = 7

    @staticmethod
    def from_str(label):
        if label in ('YTD'):
            return StockTimeFrame.YTD
        elif label in ('1 Day'):
            return StockTimeFrame.DAY
        elif label in ('1 Week'):
            return StockTimeFrame.WEEK
        elif label in ('1 Year'):
            return StockTimeFrame.YEAR1
        elif label in ('3 Years'):
            return StockTimeFrame.YEAR3
        elif label in ('5 Years'):
            return StockTimeFrame.YEAR5
        elif label in ('Max'):
            return StockTimeFrame.MAX
        elif label in ('Custom'):
            raise NotImplementedError
        else:
            raise NotImplementedError

def get_available_time_frames():
    return ["YTD", "1 Day", "1 Week", "1 Year", "3 Years", "5 Years", "Max", "Custom"]

class StockDataHandling:
    """
    Stock data handling class
    """

    def __init__(self):
        pass

    def get_available_time_frames(self):
        return STOCK_TIME_FRAMES

    def convert_time_frame_to_datetime(self, time_frame):
        end_time = datetime.now()
        start_time = end_time

        if time_frame == StockTimeFrame.YTD:
            start_time = datetime(end_time.year, 1, 1)
        elif time_frame == StockTimeFrame.DAY:
            start_time = datetime(end_time.year, end_time.month, end_time.day)
        elif time_frame == StockTimeFrame.WEEK:
            start_time = end_time - timedelta(days=7)
        elif time_frame == StockTimeFrame.YEAR1:
            start_time = datetime(
                end_time.year - 1,
                end_time.month,
                end_time.day,
                end_time.hour,
                end_time.minute,
                end_time.second,
                end_time.microsecond,
                end_time.tzinfo,
            )
        elif time_frame == StockTimeFrame.YEAR3:
            start_time = datetime(
                end_time.year - 3,
                end_time.month,
                end_time.day,
                end_time.hour,
                end_time.minute,
                end_time.second,
                end_time.microsecond,
                end_time.tzinfo,
            )
        elif time_frame == StockTimeFrame.YEAR5:
            start_time = datetime(
                end_time.year - 5,
                end_time.month,
                end_time.day,
                end_time.hour,
                end_time.minute,
                end_time.second,
                end_time.microsecond,
                end_time.tzinfo,
            )
        elif time_frame == StockTimeFrame.MAX:
            start_time = datetime(MIN_READABLE_YEAR, 1, 1)

        return start_time, end_time

    def get_yahoo_stock(self, stock_ticker, time_frame):
        start_time, end_time = self.convert_time_frame_to_datetime(time_frame)
        try:
            data_df = pdd.DataReader(stock_ticker, "yahoo", start_time, end_time)
            return data_df
        except:
            print(f"Couldn't read '{stock_ticker}' stock data.")
            return pd.DataFrame()

    def normalize_stock_data(self, stock_data_df):
        normalized_stock_data_df = (
            stock_data_df - stock_data_df.mean()
        ) / stock_data_df.std()

        return normalized_stock_data_df


def get_stock_validity(stock):
    """
    returns True when stock name is valid, False otherwise.
    """
    return True
