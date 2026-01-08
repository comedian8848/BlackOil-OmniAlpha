import pandas as pd
from multiprocessing import Pool
from datas import *
import os
import traceback
import time

class Alphas(object):
    def __init__(self, df_data):
        pass

    @classmethod
    def calc_alpha(cls, path, func, data):
        try:
            t1 = time.time()
            res = func(data)
            res.to_csv(path)
            t2 = time.time()
            print(f"Factory {os.path.splitext(os.path.basename(path))[0]} time {t2-t1}")
        except Exception as e:
            print(f"generate {path} error!!!")
            # traceback.print_exc()

    @classmethod
    def get_stocks_data(cls, year, list_assets, benchmark):
        yer = int(year)
        start_time = f'{yer-1}-01-01'
        end_time = f'{yer+1}-01-01'

        data_path = 'datas'
        df_all = pd.DataFrame()

        # 获取基准数据（如沪深300指数）
        df_benchmark = cls.get_benchmark(year, benchmark)
        benchmark_open = df_benchmark.set_index('date')['open']
        benchmark_close = df_benchmark.set_index('date')['close']

        # 读取股票数据
        for asset in list_assets:
            try:
                file_path = f'{data_path}/{asset}.csv'
                if not os.path.exists(file_path):
                    continue
                
                df = pd.read_csv(file_path)
                df = df[(df['date'] >= start_time) & (df['date'] <= end_time)]
                df['asset'] = asset
                
                # 关联基准指数数据
                df = df.set_index('date')
                df['benchmark_open'] = benchmark_open
                df['benchmark_close'] = benchmark_close
                df = df.reset_index()
                
                df_all = pd.concat([df_all, df], ignore_index=True)
            except Exception as e:
                print(f"Error loading {asset}: {e}")
                continue

        if df_all.empty:
            raise ValueError("No stock data loaded!")

        # 重命名列以匹配因子计算需要
        df_all = df_all.rename(columns={
            "交易日期": "date",
            "股票代码": "code",
            "开盘价": "open",
            "收盘价": "close",
            "最高价": "high",
            "最低价": "low",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "pctChg",
            "换手率": "turnover"})
        
        # 计算平均成交价 vwap
        df_all['vwap'] = df_all['amount'] / (df_all['volume'] * 100)
        df_all['turnover'] = df_all['turnover'] / 100

        # 返回计算因子需要的列
        df_all = df_all.reset_index(drop=True)
        df_all = df_all[['asset', 'date', "open", "close", "high", "low", "volume", "amount", 'vwap', "pctChg", 'turnover', 'benchmark_open', 'benchmark_close']]
        df_all = df_all[df_all['asset'].notnull()]
        
        return df_all.pivot(index='date', columns='asset')

    @classmethod
    def get_benchmark(cls, year, code):
        yer = int(year)
        start_time = f'{yer-1}-01-01'
        end_time = f'{yer+1}-01-01'

        data_path = 'index'
        df = pd.read_csv(f'{data_path}/{code}.csv')
        return df[(df['date'] >= start_time) & (df['date'] <= end_time)]

    @classmethod
    def get_alpha_methods(cls, self):
        return (list(filter(lambda m: m.startswith("alpha") and callable(getattr(self, m)),
                            dir(self))))

    @classmethod
    def generate_alpha_single(cls, alpha_name, year, list_assets, benchmark, need_save=False):
        # 获取计算因子所需股票数据
        stock_data = cls.get_stocks_data(year, list_assets, benchmark)

        # 实例化因子计算的对象
        stock = cls(stock_data)

        factor = getattr(cls, alpha_name)
        if factor is None:
            print('alpha name is error!!!')
            return None
        
        alpha_data = factor(stock)

        if need_save:
            path = f'alphas/{cls.__name__}/{year}'
            if not os.path.isdir(path):
                os.makedirs(path)
            alpha_data.to_csv(f'{path}/{alpha_name}.csv')

        return alpha_data

    @classmethod
    def generate_alphas(cls, year, list_assets, benchmark):
        t1 = time.time()
        # 获取计算因子所需股票数据
        stock_data = cls.get_stocks_data(year, list_assets, benchmark)

        # 实例化因子计算的对象
        stock = cls(stock_data)
        
        # 因子计算结果的保存路径
        path = f'alphas/{cls.__name__}/{year}'

        # 创建保存路径
        if not os.path.isdir(path):
            os.makedirs(path)

        # 创建线程池
        count = os.cpu_count()
        pool = Pool(count)

        # 获取所有因子计算的方法
        methods = cls.get_alpha_methods(cls)

        # 在线程池中计算所有alpha
        for m in methods:
            factor = getattr(cls, m)
            try:
                pool.apply_async(cls.calc_alpha, (f'{path}/{m}.csv', factor, stock))
            except Exception as e:
                traceback.print_exc()

        pool.close()
        pool.join()
        t2 = time.time()
        print(f"Total time {t2-t1}")
