import numpy as np
import pandas as pd
from numba import njit
from datetime import datetime
import pytest
from itertools import product

from vectorbt.generic import nb
from vectorbt.records.drawdowns import Drawdowns

day_dt = np.timedelta64(86400000000000)

df = pd.DataFrame({
    'a': [1, 2, 3, 4, np.nan],
    'b': [np.nan, 4, 3, 2, 1],
    'c': [1, 2, np.nan, 2, 1]
}, index=pd.DatetimeIndex([
    datetime(2018, 1, 1),
    datetime(2018, 1, 2),
    datetime(2018, 1, 3),
    datetime(2018, 1, 4),
    datetime(2018, 1, 5)
]))

@njit
def pd_nanmean_nb(x):
    return np.nanmean(x)

@njit
def nanmean_nb(col, i, x):
    return np.nanmean(x)

@njit
def nanmean_matrix_nb(i, x):
    return np.nanmean(x)


# ############# accessors.py ############# #


class TestAccessors:
    def test_split_into_ranges(self):
        pd.testing.assert_frame_equal(
            df['a'].vbt.split_into_ranges(n=2),
            pd.DataFrame(
                np.array([
                    [1., 4.],
                    [2., np.nan]
                ]),
                index=pd.RangeIndex(start=0, stop=2, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-04'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-02', '2018-01-05'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        pd.testing.assert_frame_equal(
            df['a'].vbt.split_into_ranges(range_len=2),
            pd.DataFrame(
                np.array([
                    [1., 2., 3., 4.],
                    [2., 3., 4., np.nan]
                ]),
                index=pd.RangeIndex(start=0, stop=2, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        pd.testing.assert_frame_equal(
            df['a'].vbt.split_into_ranges(range_len=2, n=3),
            pd.DataFrame(
                np.array([
                    [1., 3., 4.],
                    [2., 4., np.nan]
                ]),
                index=pd.RangeIndex(start=0, stop=2, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-03', '2018-01-04'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-02', '2018-01-04', '2018-01-05'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        pd.testing.assert_frame_equal(
            df['a'].vbt.split_into_ranges(range_len=3, n=2),
            pd.DataFrame(
                np.array([
                    [1., 3.],
                    [2., 4.],
                    [3., np.nan]
                ]),
                index=pd.RangeIndex(start=0, stop=3, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-03'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-03', '2018-01-05'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        pd.testing.assert_frame_equal(
            df.vbt.split_into_ranges(n=2),
            pd.DataFrame(
                np.array([
                    [1., 4., np.nan, 2., 1., 2.],
                    [2., np.nan, 4., 1., 2., 1.]
                ]),
                index=pd.RangeIndex(start=0, stop=2, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.Index(['a', 'a', 'b', 'b', 'c', 'c'], dtype='object'),
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-04', '2018-01-01', '2018-01-04', '2018-01-01', '2018-01-04'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-02', '2018-01-05', '2018-01-02', '2018-01-05', '2018-01-02', '2018-01-05'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        pd.testing.assert_frame_equal(
            df.vbt.split_into_ranges(start_idxs=[0, 1], end_idxs=[3, 4]),
            pd.DataFrame(
                np.array([
                    [1., 2., np.nan, 4., 1., 2.],
                    [2., 3., 4., 3., 2., np.nan],
                    [3., 4., 3., 2., np.nan, 2.]
                ]),
                index=pd.RangeIndex(start=0, stop=3, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.Index(['a', 'a', 'b', 'b', 'c', 'c'], dtype='object'),
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-02', '2018-01-01', '2018-01-02', '2018-01-01', '2018-01-02'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-03', '2018-01-04', '2018-01-03', '2018-01-04', '2018-01-03', '2018-01-04'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        pd.testing.assert_frame_equal(
            df.vbt.split_into_ranges(start_idxs=df.index[[0, 1]], end_idxs=df.index[[2, 3]]),
            pd.DataFrame(
                np.array([
                    [1., 2., np.nan, 4., 1., 2.],
                    [2., 3., 4., 3., 2., np.nan],
                    [3., 4., 3., 2., np.nan, 2.]
                ]),
                index=pd.RangeIndex(start=0, stop=3, step=1),
                columns=pd.MultiIndex.from_arrays([
                    pd.Index(['a', 'a', 'b', 'b', 'c', 'c'], dtype='object'),
                    pd.DatetimeIndex([
                        '2018-01-01', '2018-01-02', '2018-01-01', '2018-01-02', '2018-01-01', '2018-01-02'
                    ], dtype='datetime64[ns]', name='range_start', freq=None),
                    pd.DatetimeIndex([
                        '2018-01-03', '2018-01-04', '2018-01-03', '2018-01-04', '2018-01-03', '2018-01-04'
                    ], dtype='datetime64[ns]', name='range_end', freq=None)
                ])
            )
        )
        with pytest.raises(Exception) as e_info:
            df.vbt.split_into_ranges()
        with pytest.raises(Exception) as e_info:
            df.vbt.split_into_ranges(start_idxs=[0, 1])
        with pytest.raises(Exception) as e_info:
            df.vbt.split_into_ranges(end_idxs=[2, 4])
        with pytest.raises(Exception) as e_info:
            df.vbt.split_into_ranges(start_idxs=[0, 1], end_idxs=[2, 4])

    @pytest.mark.parametrize(
        "test_value",
        [-1, 0., np.nan],
    )
    def test_fillna(self, test_value):
        pd.testing.assert_series_equal(df['a'].vbt.fillna(test_value), df['a'].fillna(test_value))
        pd.testing.assert_frame_equal(df.vbt.fillna(test_value), df.fillna(test_value))

    @pytest.mark.parametrize(
        "test_n",
        [1, 2, 3, 4, 5],
    )
    def test_fshift(self, test_n):
        pd.testing.assert_series_equal(df['a'].vbt.fshift(test_n), df['a'].shift(test_n))
        np.testing.assert_array_equal(
            df['a'].vbt.fshift(test_n).values,
            nb.fshift_1d_nb(df['a'].values, test_n)
        )
        pd.testing.assert_frame_equal(df.vbt.fshift(test_n), df.shift(test_n))

    def test_diff(self):
        pd.testing.assert_series_equal(df['a'].vbt.diff(), df['a'].diff())
        np.testing.assert_array_equal(df['a'].vbt.diff().values, nb.diff_1d_nb(df['a'].values))
        pd.testing.assert_frame_equal(df.vbt.diff(), df.diff())

    def test_pct_change(self):
        pd.testing.assert_series_equal(df['a'].vbt.pct_change(), df['a'].pct_change(fill_method=None))
        np.testing.assert_array_equal(df['a'].vbt.pct_change().values, nb.pct_change_1d_nb(df['a'].values))
        pd.testing.assert_frame_equal(df.vbt.pct_change(), df.pct_change(fill_method=None))

    def test_ffill(self):
        pd.testing.assert_series_equal(df['a'].vbt.ffill(), df['a'].ffill())
        pd.testing.assert_frame_equal(df.vbt.ffill(), df.ffill())

    def test_product(self):
        pd.testing.assert_series_equal(df['a'].vbt.product(), df['a'].product())
        pd.testing.assert_frame_equal(df.vbt.product(), df.product())

    def test_product(self):
        assert df['a'].vbt.product() == df['a'].product()
        np.testing.assert_array_equal(df.vbt.product(), df.product())

    def test_cumsum(self):
        pd.testing.assert_series_equal(df['a'].vbt.cumsum(), df['a'].cumsum())
        pd.testing.assert_frame_equal(df.vbt.cumsum(), df.cumsum())

    def test_cumprod(self):
        pd.testing.assert_series_equal(df['a'].vbt.cumprod(), df['a'].cumprod())
        pd.testing.assert_frame_equal(df.vbt.cumprod(), df.cumprod())

    @pytest.mark.parametrize(
        "test_window,test_minp",
        list(product([1, 2, 3, 4, 5], [1, None]))
    )
    def test_rolling_min(self, test_window, test_minp):
        if test_minp is None:
            test_minp = test_window
        pd.testing.assert_series_equal(
            df['a'].vbt.rolling_min(test_window, minp=test_minp),
            df['a'].rolling(test_window, min_periods=test_minp).min()
        )
        pd.testing.assert_frame_equal(
            df.vbt.rolling_min(test_window, minp=test_minp),
            df.rolling(test_window, min_periods=test_minp).min()
        )

    @pytest.mark.parametrize(
        "test_window,test_minp",
        list(product([1, 2, 3, 4, 5], [1, None]))
    )
    def test_rolling_max(self, test_window, test_minp):
        if test_minp is None:
            test_minp = test_window
        pd.testing.assert_series_equal(
            df['a'].vbt.rolling_max(test_window, minp=test_minp),
            df['a'].rolling(test_window, min_periods=test_minp).max()
        )
        pd.testing.assert_frame_equal(
            df.vbt.rolling_max(test_window, minp=test_minp),
            df.rolling(test_window, min_periods=test_minp).max()
        )

    @pytest.mark.parametrize(
        "test_window,test_minp",
        list(product([1, 2, 3, 4, 5], [1, None]))
    )
    def test_rolling_mean(self, test_window, test_minp):
        if test_minp is None:
            test_minp = test_window
        pd.testing.assert_series_equal(
            df['a'].vbt.rolling_mean(test_window, minp=test_minp),
            df['a'].rolling(test_window, min_periods=test_minp).mean()
        )
        pd.testing.assert_frame_equal(
            df.vbt.rolling_mean(test_window, minp=test_minp),
            df.rolling(test_window, min_periods=test_minp).mean()
        )

    @pytest.mark.parametrize(
        "test_window,test_minp,test_ddof",
        list(product([1, 2, 3, 4, 5], [1, None], [0, 1]))
    )
    def test_rolling_std(self, test_window, test_minp, test_ddof):
        if test_minp is None:
            test_minp = test_window
        pd.testing.assert_series_equal(
            df['a'].vbt.rolling_std(test_window, minp=test_minp, ddof=test_ddof),
            df['a'].rolling(test_window, min_periods=test_minp).std(ddof=test_ddof)
        )
        pd.testing.assert_frame_equal(
            df.vbt.rolling_std(test_window, minp=test_minp, ddof=test_ddof),
            df.rolling(test_window, min_periods=test_minp).std(ddof=test_ddof)
        )

    @pytest.mark.parametrize(
        "test_window,test_minp,test_adjust",
        list(product([1, 2, 3, 4, 5], [1, None], [False, True]))
    )
    def test_ewm_mean(self, test_window, test_minp, test_adjust):
        if test_minp is None:
            test_minp = test_window
        pd.testing.assert_series_equal(
            df['a'].vbt.ewm_mean(test_window, minp=test_minp, adjust=test_adjust),
            df['a'].ewm(span=test_window, min_periods=test_minp, adjust=test_adjust).mean()
        )
        pd.testing.assert_frame_equal(
            df.vbt.ewm_mean(test_window, minp=test_minp, adjust=test_adjust),
            df.ewm(span=test_window, min_periods=test_minp, adjust=test_adjust).mean()
        )

    @pytest.mark.parametrize(
        "test_window,test_minp,test_adjust,test_ddof",
        list(product([1, 2, 3, 4, 5], [1, None], [False, True], [0, 1]))
    )
    def test_ewm_std(self, test_window, test_minp, test_adjust, test_ddof):
        if test_minp is None:
            test_minp = test_window
        pd.testing.assert_series_equal(
            df['a'].vbt.ewm_std(test_window, minp=test_minp, adjust=test_adjust, ddof=test_ddof),
            df['a'].ewm(span=test_window, min_periods=test_minp, adjust=test_adjust).std(ddof=test_ddof)
        )
        pd.testing.assert_frame_equal(
            df.vbt.ewm_std(test_window, minp=test_minp, adjust=test_adjust, ddof=test_ddof),
            df.ewm(span=test_window, min_periods=test_minp, adjust=test_adjust).std(ddof=test_ddof)
        )

    def test_expanding_min(self):
        pd.testing.assert_series_equal(df['a'].vbt.expanding_min(), df['a'].expanding().min())
        pd.testing.assert_frame_equal(df.vbt.expanding_min(), df.expanding().min())

    def test_expanding_max(self):
        pd.testing.assert_series_equal(df['a'].vbt.expanding_max(), df['a'].expanding().max())
        pd.testing.assert_frame_equal(df.vbt.expanding_max(), df.expanding().max())

    def test_expanding_mean(self):
        pd.testing.assert_series_equal(df['a'].vbt.expanding_mean(), df['a'].expanding().mean())
        pd.testing.assert_frame_equal(df.vbt.expanding_mean(), df.expanding().mean())

    @pytest.mark.parametrize(
        "test_ddof",
        [0, 1]
    )
    def test_expanding_std(self, test_ddof):
        pd.testing.assert_series_equal(
            df['a'].vbt.expanding_std(ddof=test_ddof),
            df['a'].expanding().std(ddof=test_ddof)
        )
        pd.testing.assert_frame_equal(
            df.vbt.expanding_std(ddof=test_ddof),
            df.expanding().std(ddof=test_ddof)
        )

    @pytest.mark.parametrize(
        "test_window",
        [1, 2, 3, 4, 5],
    )
    def test_rolling_apply(self, test_window):
        pd.testing.assert_series_equal(
            df['a'].rolling(test_window, min_periods=1).apply(pd_nanmean_nb, raw=True),
            df['a'].vbt.rolling_apply(test_window, nanmean_nb)
        )
        pd.testing.assert_frame_equal(
            df.rolling(test_window, min_periods=1).apply(pd_nanmean_nb, raw=True),
            df.vbt.rolling_apply(test_window, nanmean_nb)
        )

    def test_rolling_apply_on_matrix(self):
        pd.testing.assert_frame_equal(
            df.vbt.rolling_apply(3, nanmean_matrix_nb, on_matrix=True),
            pd.DataFrame(
                np.array([
                    [1., 1., 1.],
                    [2., 2., 2.],
                    [2.28571429, 2.28571429, 2.28571429],
                    [2.75, 2.75, 2.75],
                    [2.28571429, 2.28571429, 2.28571429]
                ]),
                index=df.index,
                columns=df.columns
            )
        )

    def test_expanding_apply(self):
        pd.testing.assert_series_equal(
            df['a'].expanding(min_periods=1).apply(pd_nanmean_nb, raw=True),
            df['a'].vbt.expanding_apply(nanmean_nb)
        )
        pd.testing.assert_frame_equal(
            df.expanding(min_periods=1).apply(pd_nanmean_nb, raw=True),
            df.vbt.expanding_apply(nanmean_nb)
        )

    def test_expanding_apply_on_matrix(self):
        pd.testing.assert_frame_equal(
            df.vbt.expanding_apply(nanmean_matrix_nb, on_matrix=True),
            pd.DataFrame(
                np.array([
                    [1., 1., 1.],
                    [2., 2., 2.],
                    [2.28571429, 2.28571429, 2.28571429],
                    [2.4, 2.4, 2.4],
                    [2.16666667, 2.16666667, 2.16666667]
                ]),
                index=df.index,
                columns=df.columns
            )
        )

    def test_groupby_apply(self):
        pd.testing.assert_series_equal(
            df['a'].groupby(np.asarray([1, 1, 2, 2, 3])).apply(lambda x: pd_nanmean_nb(x.values)),
            df['a'].vbt.groupby_apply(np.asarray([1, 1, 2, 2, 3]), nanmean_nb)
        )
        pd.testing.assert_frame_equal(
            df.groupby(np.asarray([1, 1, 2, 2, 3])).agg({
                'a': lambda x: pd_nanmean_nb(x.values),
                'b': lambda x: pd_nanmean_nb(x.values),
                'c': lambda x: pd_nanmean_nb(x.values)
            }),  # any clean way to do column-wise grouping in pandas?
            df.vbt.groupby_apply(np.asarray([1, 1, 2, 2, 3]), nanmean_nb)
        )

    def test_groupby_apply_on_matrix(self):
        pd.testing.assert_frame_equal(
            df.vbt.groupby_apply(np.asarray([1, 1, 2, 2, 3]), nanmean_matrix_nb, on_matrix=True),
            pd.DataFrame(
                np.array([
                    [2., 2., 2.],
                    [2.8, 2.8, 2.8],
                    [1., 1., 1.]
                ]),
                index=pd.Int64Index([1, 2, 3], dtype='int64'),
                columns=df.columns
            )
        )

    @pytest.mark.parametrize(
        "test_freq",
        ['1h', '3d', '1w'],
    )
    def test_resample_apply(self, test_freq):
        pd.testing.assert_series_equal(
            df['a'].resample(test_freq).apply(lambda x: pd_nanmean_nb(x.values)),
            df['a'].vbt.resample_apply(test_freq, nanmean_nb)
        )
        pd.testing.assert_frame_equal(
            df.resample(test_freq).apply(lambda x: pd_nanmean_nb(x.values)),
            df.vbt.resample_apply(test_freq, nanmean_nb)
        )

    def test_resample_apply_on_matrix(self):
        pd.testing.assert_frame_equal(
            df.vbt.resample_apply('3d', nanmean_matrix_nb, on_matrix=True),
            pd.DataFrame(
                np.array([
                    [2.28571429, 2.28571429, 2.28571429],
                    [2., 2., 2.]
                ]),
                index=pd.DatetimeIndex(['2018-01-01', '2018-01-04'], dtype='datetime64[ns]', freq='3D'),
                columns=df.columns
            )
        )

    def test_applymap(self):
        @njit
        def mult_nb(col, i, x):
            return x * 2

        pd.testing.assert_series_equal(
            df['a'].map(lambda x: x * 2),
            df['a'].vbt.applymap(mult_nb)
        )
        pd.testing.assert_frame_equal(
            df.applymap(lambda x: x * 2),
            df.vbt.applymap(mult_nb)
        )

    def test_filter(self):
        @njit
        def greater_nb(col, i, x):
            return x > 2

        pd.testing.assert_series_equal(
            df['a'].map(lambda x: x if x > 2 else np.nan),
            df['a'].vbt.filter(greater_nb)
        )
        pd.testing.assert_frame_equal(
            df.applymap(lambda x: x if x > 2 else np.nan),
            df.vbt.filter(greater_nb)
        )

    def test_apply_and_reduce(self):
        @njit
        def every_nth_nb(col, a, n):
            return a[::n]

        @njit
        def sum_nb(col, a, n):
            return np.nansum(a)

        assert df['a'].iloc[::2].sum() == df['a'].vbt.apply_and_reduce(every_nth_nb, sum_nb, 2)
        pd.testing.assert_series_equal(
            df.iloc[::2].sum(),
            df.vbt.apply_and_reduce(every_nth_nb, sum_nb, 2)
        )
        pd.testing.assert_series_equal(
            df.iloc[::2].sum() * day_dt,
            df.vbt.apply_and_reduce(every_nth_nb, sum_nb, 2, time_units=True)
        )

    def test_reduce(self):
        @njit
        def sum_nb(col, a):
            return np.nansum(a)

        assert df['a'].sum() == df['a'].vbt.reduce(sum_nb)
        pd.testing.assert_series_equal(
            df.sum(),
            df.vbt.reduce(sum_nb)
        )
        pd.testing.assert_series_equal(
            df.sum() * day_dt,
            df.vbt.reduce(sum_nb, time_units=True)
        )

    def test_reduce_to_array(self):
        @njit
        def min_and_max_nb(col, a):
            result = np.empty(2)
            result[0] = np.nanmin(a)
            result[1] = np.nanmax(a)
            return result

        result = df.apply(lambda x: np.asarray([np.min(x), np.max(x)]), axis=0)
        pd.testing.assert_series_equal(
            result['a'],
            df['a'].vbt.reduce_to_array(min_and_max_nb)
        )
        result.index = pd.Index(['min', 'max'])
        pd.testing.assert_series_equal(
            result['a'],
            df['a'].vbt.reduce_to_array(min_and_max_nb, index=['min', 'max'])
        )
        pd.testing.assert_frame_equal(
            result,
            df.vbt.reduce_to_array(min_and_max_nb, index=['min', 'max'])
        )
        pd.testing.assert_frame_equal(
            result * day_dt,
            df.vbt.reduce_to_array(min_and_max_nb, index=['min', 'max'], time_units=True)
        )

    @pytest.mark.parametrize(
        "test_func,test_func_nb",
        [
            (lambda x, **kwargs: x.min(**kwargs), nb.nanmin_nb),
            (lambda x, **kwargs: x.max(**kwargs), nb.nanmax_nb),
            (lambda x, **kwargs: x.mean(**kwargs), nb.nanmean_nb),
            (lambda x, **kwargs: x.median(**kwargs), nb.nanmedian_nb),
            (lambda x, **kwargs: x.std(**kwargs, ddof=0), nb.nanstd_nb),
            (lambda x, **kwargs: x.count(**kwargs), nb.nancnt_nb),
            (lambda x, **kwargs: x.sum(**kwargs), nb.nansum_nb)
        ],
    )
    def test_funcs(self, test_func, test_func_nb):
        # numeric
        assert test_func(df['a']) == test_func(df['a'].vbt)
        pd.testing.assert_series_equal(
            test_func(df),
            test_func(df.vbt)
        )
        np.testing.assert_array_equal(test_func(df).values, test_func_nb(df.values))
        pd.testing.assert_series_equal(
            test_func(df) * day_dt,
            test_func(df.vbt, time_units=True)
        )
        # boolean
        bool_ts = df == df
        assert test_func(bool_ts['a']) == test_func(bool_ts['a'].vbt)
        pd.testing.assert_series_equal(
            test_func(bool_ts),
            test_func(bool_ts.vbt)
        )
        pd.testing.assert_series_equal(
            test_func(bool_ts) * day_dt,
            test_func(bool_ts.vbt, time_units=True)
        )

    @pytest.mark.parametrize(
        "test_func",
        [
            lambda x, **kwargs: x.idxmin(**kwargs),
            lambda x, **kwargs: x.idxmax(**kwargs)
        ],
    )
    def test_arg_funcs(self, test_func):
        assert test_func(df['a']) == test_func(df['a'].vbt)
        pd.testing.assert_series_equal(
            test_func(df),
            test_func(df.vbt)
        )

    def test_describe(self):
        pd.testing.assert_series_equal(
            df['a'].describe(),
            df['a'].vbt.describe()
        )
        pd.testing.assert_frame_equal(
            df.describe(percentiles=None),
            df.vbt.describe(percentiles=None)
        )
        pd.testing.assert_frame_equal(
            df.describe(percentiles=[]),
            df.vbt.describe(percentiles=[])
        )
        pd.testing.assert_frame_equal(
            df.describe(percentiles=np.arange(0, 1, 0.1)),
            df.vbt.describe(percentiles=np.arange(0, 1, 0.1))
        )

    def test_drawdown(self):
        pd.testing.assert_series_equal(
            df['a'] / df['a'].expanding().max() - 1,
            df['a'].vbt.drawdown()
        )
        pd.testing.assert_frame_equal(
            df / df.expanding().max() - 1,
            df.vbt.drawdown()
        )

    def test_drawdowns(self):
        assert type(df['a'].vbt.drawdowns) is Drawdowns
        assert df['a'].vbt.drawdowns.wrapper.freq == df['a'].vbt.freq
        assert df['a'].vbt.drawdowns.wrapper.ndim == df['a'].ndim
        assert df.vbt.drawdowns.wrapper.ndim == df.ndim
