# -*- coding: utf-8 -*-
#
import unittest

from kitchen.pycompat24.sets import add_builtin_set
add_builtin_set()

from kitchen import collections

class TestStrictDictGetSet(unittest.TestCase):
    def test_strict_dict_get_set(self):
        '''Test getting and setting items in StrictDict'''
        d = collections.StrictDict()
        d['a'] = 1
        d[b'a'] = 2
        self.assertNotEqual(d['a'], d[b'a'])
        self.assertEqual(len(d), 2)

        d['\xf1'] = 1
        d[b'\xf1'] = 2
        d['\xf1'.encode('utf-8')] = 3
        self.assertEqual(d['\xf1'], 1)
        self.assertEqual(d[b'\xf1'], 2)
        self.assertEqual(d['\xf1'.encode('utf-8')], 3)
        self.assertEqual(len(d), 5)

class TestStrictDict(unittest.TestCase):
    def setUp(self):
        self.d = collections.StrictDict()
        self.d['a'] = 1
        self.d[b'a'] = 2
        self.d['\xf1'] = 1
        self.d[b'\xf1'] = 2
        self.d['\xf1'.encode('utf-8')] = 3
        self.keys = ['a', b'a', '\xf1', b'\xf1', '\xf1'.encode('utf-8')]

    def tearDown(self):
        del(self.d)

    def _compare_lists(self, list1, list2, debug=False):
        '''We have a mixture of bytes and unicode so we have to compare these
            lists manually and inefficiently
        '''
        def _compare_lists_helper(compare_to, dupes, idx, length):
            if i not in compare_to:
                return False
            for n in range(1, length + 1):
                if i not in dupes[n][idx]:
                    dupes[n][idx].add(i)
                    return True
        if len(list1) != len(list2):
            return False

        list1_dupes = dict([(i, (set(), set(), set())) for i in range(1, len(list1)+1)])
        list2_dupes = dict([(i, (set(), set(), set())) for i in range(1, len(list1)+1)])

        list1_u = [l for l in list1 if isinstance(l, str)]
        list1_b = [l for l in list1 if isinstance(l, bytes)]
        list1_o = [l for l in list1 if not (isinstance(l, (str, bytes)))]

        list2_u = [l for l in list2 if isinstance(l, str)]
        list2_b = [l for l in list2 if isinstance(l, bytes)]
        list2_o = [l for l in list2 if not (isinstance(l, (str, bytes)))]

        for i in list1:
            if isinstance(i, str):
                if not _compare_lists_helper(list2_u, list1_dupes, 0, len(list1)):
                    return False
            elif isinstance(i, bytes):
                if not _compare_lists_helper(list2_b, list1_dupes, 1, len(list1)):
                    return False
            else:
                if not _compare_lists_helper(list2_o, list1_dupes, 2, len(list1)):
                    return False

        if list1_dupes[2][0] or list1_dupes[2][1] or list1_dupes[2][2]:
            for i in list2:
                if isinstance(i, str):
                    if not _compare_lists_helper(list1_u, list2_dupes, 0, len(list1)):
                        return False
                elif isinstance(i, bytes):
                    if not _compare_lists_helper(list1_b, list2_dupes, 1, len(list1)):
                        return False
                else:
                    if not _compare_lists_helper(list1_o, list2_dupes, 2, len(list1)):
                        return False

            for i in range(2, len(list1)+1):
                for n in list1_dupes[i]:
                    if n not in list2_dupes[i]:
                        return False

        return True

    def test__compare_list(self):
        '''*sigh* this test support function is so complex we need to test it'''
        self.assertTrue(self._compare_lists(['a', 'b', 'c'], ['c', 'a', 'b']))
        self.assertTrue(not self._compare_lists(['b', 'c'], ['c', 'a', 'b']))
        self.assertTrue(not self._compare_lists([b'a', 'b'], ['a', 'b']))
        self.assertTrue(not self._compare_lists(['a', b'b'], [b'a', 'b']))
        self.assertTrue(self._compare_lists(['a', 'b', 1], ['a', 1, 'b']))
        self.assertTrue(self._compare_lists([b'a', b'b'], [b'a', b'b']))
        self.assertTrue(self._compare_lists([b'a', 'b'], [b'a', 'b']))
        self.assertTrue(not self._compare_lists([b'a', 'b'], [b'a', b'b']))
        self.assertTrue(self._compare_lists([b'a', 'b', 'b', 'c', b'a'], [b'a', b'a', 'b', 'c', 'b']))
        self.assertTrue(not self._compare_lists([b'a', 'b', 'b', 'c', 'a'], [b'a', b'a', 'b', 'c', 'b']))
        self.assertTrue(not self._compare_lists([b'a', 'b', 'b', 'c', b'a'], [b'a', 'b', 'b', 'c', 'b']))

    def test_strict_dict_len(self):
        '''StrictDict len'''
        self.assertEqual(len(self.d), 5)

    def test_strict_dict_del(self):
        '''StrictDict del'''
        self.assertEqual(len(self.d), 5)
        del(self.d['\xf1'])
        self.assertRaises(KeyError, self.d.__getitem__, '\xf1')
        self.assertEqual(len(self.d), 4)

    def test_strict_dict_iter(self):
        '''StrictDict iteration'''
        keys = []
        for k in self.d:
            keys.append(k)
        self.assertTrue(self._compare_lists(keys, self.keys),
                msg='keys != self.key: %s != %s' % (keys, self.keys))

        keys = []
        for k in self.d.keys():
            keys.append(k)
        self.assertTrue(self._compare_lists(keys, self.keys),
                msg='keys != self.key: %s != %s' % (keys, self.keys))

        keys = [k for k in self.d]
        self.assertTrue(self._compare_lists(keys, self.keys),
                msg='keys != self.key: %s != %s' % (keys, self.keys))

        keys = []
        for k in list(self.d.keys()):
            keys.append(k)
        self.assertTrue(self._compare_lists(keys, self.keys),
                msg='keys != self.key: %s != %s' % (keys, self.keys))

    def test_strict_dict_contains(self):
        '''StrictDict contains function'''
        self.assertTrue(b'b' not in self.d)
        self.assertTrue('b' not in self.d)
        self.assertTrue(b'\xf1' in self.d)
        self.assertTrue('\xf1' in self.d)
        self.assertTrue(b'a' in self.d)
        self.assertTrue('a' in self.d)

        del(self.d['\xf1'])
        self.assertTrue('\xf1' not in self.d)
        self.assertTrue(b'\xf1' in self.d)

        del(self.d[b'a'])
        self.assertTrue('a' in self.d)
        self.assertTrue(b'a' not in self.d)
