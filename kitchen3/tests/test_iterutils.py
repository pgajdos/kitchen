# -*- coding: utf-8 -*-
#
import unittest

from kitchen import iterutils

class TestIterutils(unittest.TestCase):
    iterable_data = (
            [0, 1, 2],
            [],
            (0, 1, 2),
            tuple(),
            set([0, 1, 2]),
            set(),
            dict(a=1, b=2),
            dict(),
            [None],
            [False],
            [0],
            range(0, 3),
            iter([1, 2, 3]),
            )
    non_iterable_data = (
            None,
            False,
            True,
            0,
            1.1,
            )

    def test_isiterable(self):
        for item in self.iterable_data:
            self.assertTrue(iterutils.isiterable(item) == True)

        for item in self.non_iterable_data:
            self.assertTrue(iterutils.isiterable(item) == False)

        # strings
        self.assertTrue(iterutils.isiterable(b'a', include_string=True) == True)
        self.assertTrue(iterutils.isiterable(b'a', include_string=False) == False)
        self.assertTrue(iterutils.isiterable(b'a') == False)
        self.assertTrue(iterutils.isiterable('a', include_string=True) == True)
        self.assertTrue(iterutils.isiterable('a', include_string=False) == False)
        self.assertTrue(iterutils.isiterable('a') == False)

    def test_iterate(self):
        iterutils.iterate(None)
        for item in self.non_iterable_data:
            self.assertTrue(list(iterutils.iterate(item)) == [item])

        for item in self.iterable_data[:-1]:
            self.assertTrue(list(iterutils.iterate(item)) == list(item))

        # iter() is exhausted after use so we have to test separately
        self.assertTrue(list(iterutils.iterate(iter([1, 2, 3]))) == [1, 2, 3])

        # strings
        self.assertTrue(list(iterutils.iterate(b'abc')) == [b'abc'])
        self.assertEqual(list(iterutils.iterate(b'abc', include_string=True)), [ord(b'a'), ord(b'b'), ord(b'c')])
        self.assertTrue(list(iterutils.iterate('abc')) == ['abc'])
        self.assertTrue(list(iterutils.iterate('abc', include_string=True)) == ['a', 'b', 'c'])
