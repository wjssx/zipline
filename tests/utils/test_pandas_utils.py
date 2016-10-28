"""
Tests for zipline/utils/pandas_utils.py
"""
import numpy as np
import pandas as pd

from zipline.testing import parameter_space, ZiplineTestCase
from zipline.testing.predicates import assert_equal
from zipline.utils.pandas_utils import (
    ensure_keys,
    nearest_unequal_elements,
)


class TestNearestUnequalElements(ZiplineTestCase):

    @parameter_space(tz=['UTC', 'US/Eastern'], __fail_fast=True)
    def test_nearest_unequal_elements(self, tz):

        dts = pd.to_datetime(
            ['2014-01-01', '2014-01-05', '2014-01-06', '2014-01-09'],
        ).tz_localize(tz)

        t = lambda s: None if s is None else pd.Timestamp(s, tz=tz)

        for dt, before, after in (('2013-12-30', None, '2014-01-01'),
                                  ('2013-12-31', None, '2014-01-01'),
                                  ('2014-01-01', None, '2014-01-05'),
                                  ('2014-01-02', '2014-01-01', '2014-01-05'),
                                  ('2014-01-03', '2014-01-01', '2014-01-05'),
                                  ('2014-01-04', '2014-01-01', '2014-01-05'),
                                  ('2014-01-05', '2014-01-01', '2014-01-06'),
                                  ('2014-01-06', '2014-01-05', '2014-01-09'),
                                  ('2014-01-07', '2014-01-06', '2014-01-09'),
                                  ('2014-01-08', '2014-01-06', '2014-01-09'),
                                  ('2014-01-09', '2014-01-06', None),
                                  ('2014-01-10', '2014-01-09', None),
                                  ('2014-01-11', '2014-01-09', None)):
            computed = nearest_unequal_elements(dts, t(dt))
            expected = (t(before), t(after))
            self.assertEqual(computed, expected)

    @parameter_space(tz=['UTC', 'US/Eastern'], __fail_fast=True)
    def test_nearest_unequal_elements_short_dts(self, tz):

        # Length 1.
        dts = pd.to_datetime(['2014-01-01']).tz_localize(tz)
        t = lambda s: None if s is None else pd.Timestamp(s, tz=tz)

        for dt, before, after in (('2013-12-31', None, '2014-01-01'),
                                  ('2014-01-01', None, None),
                                  ('2014-01-02', '2014-01-01', None)):
            computed = nearest_unequal_elements(dts, t(dt))
            expected = (t(before), t(after))
            self.assertEqual(computed, expected)

        # Length 0
        dts = pd.to_datetime([]).tz_localize(tz)
        for dt, before, after in (('2013-12-31', None, None),
                                  ('2014-01-01', None, None),
                                  ('2014-01-02', None, None)):
            computed = nearest_unequal_elements(dts, t(dt))
            expected = (t(before), t(after))
            self.assertEqual(computed, expected)

    def test_nearest_unequal_bad_input(self):
        with self.assertRaises(ValueError) as e:
            nearest_unequal_elements(
                pd.to_datetime(['2014', '2014']),
                pd.Timestamp('2014'),
            )

        self.assertEqual(str(e.exception), 'dts must be unique')

        with self.assertRaises(ValueError) as e:
            nearest_unequal_elements(
                pd.to_datetime(['2014', '2013']),
                pd.Timestamp('2014'),
            )

        self.assertEqual(
            str(e.exception),
            'dts must be sorted in increasing order',
        )

    @parameter_space(default_value=[1000.0, 0.0, 1.0])
    def test_ensure_keys(self, default_value):
        s = pd.Series({'a': 1, 'b': 2, 'c': 3})
        result = ensure_keys(s, ['z', 'a', 'd', 'c'], default_value)

        assert_equal(
            result,
            pd.Series({
                'a': 1.0,
                'b': 2.0,
                'c': 3.0,
                'd': default_value,
                'z': default_value,
            })
        )
