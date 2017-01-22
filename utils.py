from collections import OrderedDict
from functools import partial
from os import path
import os
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy.random as nr
import time

NUDGE = .005


class Timer(object):

    def __init__(self, start=True):
        self.end_time = None
        if start:
            self.start()
        else:
            self.st_time = None

    def start(self):
        self.st_time = time.perf_counter()

    def end(self):
        self.end_time = time.perf_counter()
        return self.time

    @property
    def time(self):
        return self.end_time - self.st_time


get_dtypes = lambda df, tp='category': df.columns[df.dtypes == tp]


def mod_cols(df, f=None, cols=None):
    df = df.copy()
    if cols is None:
        cols = get_dtypes(df, object)

    for c in cols:
        df[c] = f(df[c].copy())
    return df


def add_nulls(s, size=100):
    rand_ixs = nr.choice(s.index, size=size, replace=False)
    s.loc[rand_ixs] = None
    return s


def get_obj_type(df, as_str=True):
    """Get type of first non-null element in first column
    with object dtype. With `as_str` convert to arg for
    `fastparquet.write`'s `object_encoding` param.
    """
    [obj_col, *_] = get_dtypes(df, object)
    s = df[obj_col]
    nonull_val = s[s == s].values[0]
    if as_str:
        return enc_dct[type(nonull_val)]
    return type(nonull_val)


enc_dct = {str: 'utf8', bytes: 'bytes'}


# Plotting stuff
def s2df(ss):
    return DataFrame(OrderedDict([(s.name, s) for s in ss]))


def label(x, y, txt):
    x, y, txt = df = s2df([x, y, txt])
    ax = plt.gca()
    for i, row in df.iterrows():
        ax.text(row[x] + NUDGE, row[y] + NUDGE, str(row[txt]))


def scatter(x=None, y=None, s=None, sz_fact=30):
    plt.scatter(x, y, s=s * sz_fact, alpha=.25)
    plt.xlabel(x)
    plt.ylabel(y)
    # plt.legend()


def plot_scatter(x, y, size, lab=None, ax=None, sz_fact=30, color=None):
    # print('size={}\t lab={}\t ax={}\t sz_fact={}\t color={}\t'.format(size, lab, ax, sz_fact, color))
    scatter(x=x, y=y, s=size, sz_fact=sz_fact)
    # scatter_df(res, x=x, y=y, size=s)
    label(x, y, lab)


# def outlier_val(s, nsd=2.5):
#     s = s.dropna()
#     m = s.mean()
#     sd = s.std()
#     return m + nsd * sd


# def trim_outliers(df, cs=[], nsd=2.5):
#     for c in cs:
#         s = df[c]
#         v = outlier_val(s, nsd=nsd)
#         df = df[s <= v]
#     return df


def part(f, *a, **kw):
    wrapper = partial(f, *a, **kw)
    wrapper.__module__ = '__main__'
    return wrapper


def getsize(fn):
    if not path.isdir(fn):
        return path.getsize(fn)
    return sum(path.getsize(path.join(dirpath, fn_))
               for dirpath, _, fns in os.walk(fn)
               for fn_ in fns)
