# -*- coding: utf-8 -*-
#
import unittest

from kitchen.text.exceptions import ControlCharError

from kitchen.text import display

import base_classes

class TestDisplay(base_classes.UnicodeTestData, unittest.TestCase):

    def test_internal_interval_bisearch(self):
        '''Test that we can find things in an interval table'''
        table = ((0, 3), (5, 7), (9, 10))
        self.assertTrue(display._interval_bisearch(0, table))
        self.assertTrue(display._interval_bisearch(1, table))
        self.assertTrue(display._interval_bisearch(2, table))
        self.assertTrue(display._interval_bisearch(3, table))
        self.assertTrue(display._interval_bisearch(5, table))
        self.assertTrue(display._interval_bisearch(6, table))
        self.assertTrue(display._interval_bisearch(7, table))
        self.assertTrue(display._interval_bisearch(9, table))
        self.assertTrue(display._interval_bisearch(10, table))
        self.assertFalse(display._interval_bisearch(-1, table))
        self.assertFalse(display._interval_bisearch(4, table))
        self.assertFalse(display._interval_bisearch(8, table))
        self.assertFalse(display._interval_bisearch(11, table))

    def test_internal_generate_combining_table(self):
        '''Test that the combining table we generate is equal to or a subseet of what's in the current table

        If we assert it can mean one of two things:

        1. The code is broken
        2. The table we have is out of date.
        '''
        old_table = display._COMBINING
        new_table = display._generate_combining_table()
        for interval in new_table:
            if interval[0] == interval[1]:
                self.assertTrue(display._interval_bisearch(interval[0], old_table))
            else:
                for codepoint in xrange(interval[0], interval[1] + 1):
                    self.assertTrue(display._interval_bisearch(interval[0], old_table))

    def test_internal_ucp_width(self):
        '''Test that ucp_width returns proper width for characters'''
        for codepoint in xrange(0, 0xFFFFF + 1):
            if codepoint < 32 or (codepoint < 0xa0 and codepoint >= 0x7f):
                # With strict on, we should raise an error
                self.assertRaises(ControlCharError, display._ucp_width, codepoint, 'strict')

                if codepoint in (0x08, 0x1b, 0x7f, 0x94):
                    # Backspace, delete, clear delete remove one char
                    self.assertEqual(display._ucp_width(codepoint), -1)
                else:
                    # Everything else returns 0
                    self.assertEqual(display._ucp_width(codepoint), 0)
            elif display._interval_bisearch(codepoint, display._COMBINING):
                # Combining character
                self.assertEqual(display._ucp_width(codepoint), 0)
            elif (codepoint >= 0x1100 and
                    (codepoint <= 0x115f or                     # Hangul Jamo init. consonants
                        codepoint == 0x2329 or codepoint == 0x232a or
                        (codepoint >= 0x2e80 and codepoint <= 0xa4cf and
                            codepoint != 0x303f) or                   # CJK ... Yi
                        (codepoint >= 0xac00 and codepoint <= 0xd7a3) or # Hangul Syllables
                        (codepoint >= 0xf900 and codepoint <= 0xfaff) or # CJK Compatibility Ideographs
                        (codepoint >= 0xfe10 and codepoint <= 0xfe19) or # Vertical forms
                        (codepoint >= 0xfe30 and codepoint <= 0xfe6f) or # CJK Compatibility Forms
                        (codepoint >= 0xff00 and codepoint <= 0xff60) or # Fullwidth Forms
                        (codepoint >= 0xffe0 and codepoint <= 0xffe6) or
                        (codepoint >= 0x20000 and codepoint <= 0x2fffd) or
                        (codepoint >= 0x30000 and codepoint <= 0x3fffd))):
                self.assertEqual(display._ucp_width(codepoint), 2)
            else:
                self.assertEqual(display._ucp_width(codepoint), 1)

    def test_textual_width(self):
        '''Test that we find the proper number of spaces that a utf8 string will consume'''
        self.assertEqual(display.textual_width(self.u_japanese), 31)
        self.assertEqual(display.textual_width(self.u_spanish), 50)
        self.assertEqual(display.textual_width(self.u_mixed), 23)

    def test_textual_width_chop(self):
        '''utf8_width_chop with byte strings'''
        self.assertEqual(display.textual_width_chop(self.u_mixed, 1000), self.u_mixed)
        self.assertEqual(display.textual_width_chop(self.u_mixed, 23), self.u_mixed)
        self.assertEqual(display.textual_width_chop(self.u_mixed, 22), self.u_mixed[:-1])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 19), self.u_mixed[:-4])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 1), u'')
        self.assertEqual(display.textual_width_chop(self.u_mixed, 2), self.u_mixed[0])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 3), self.u_mixed[:2])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 4), self.u_mixed[:3])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 5), self.u_mixed[:4])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 6), self.u_mixed[:5])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 7), self.u_mixed[:5])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 8), self.u_mixed[:6])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 9), self.u_mixed[:7])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 10), self.u_mixed[:8])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 11), self.u_mixed[:9])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 12), self.u_mixed[:10])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 13), self.u_mixed[:10])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 14), self.u_mixed[:11])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 15), self.u_mixed[:12])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 16), self.u_mixed[:13])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 17), self.u_mixed[:14])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 18), self.u_mixed[:15])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 19), self.u_mixed[:15])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 20), self.u_mixed[:16])
        self.assertEqual(display.textual_width_chop(self.u_mixed, 21), self.u_mixed[:17])

    def test_textual_width_fill(self):
        '''Pad a utf8 string'''
        self.assertEqual(display.textual_width_fill(self.u_mixed, 1), self.u_mixed)
        self.assertEqual(display.textual_width_fill(self.u_mixed, 25), self.u_mixed + u'  ')
        self.assertEqual(display.textual_width_fill(self.u_mixed, 25, left=False), u'  ' + self.u_mixed)
        self.assertEqual(display.textual_width_fill(self.u_mixed, 25, chop=18), self.u_mixed[:-4] + u'       ')
        self.assertEqual(display.textual_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.u_spanish), self.u_spanish + self.u_mixed[:-4] + self.u_spanish + u'       ')
        self.assertEqual(display.textual_width_fill(self.u_mixed, 25, chop=18), self.u_mixed[:-4] + u'       ')
        self.assertEqual(display.textual_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.u_spanish), self.u_spanish + self.u_mixed[:-4] + self.u_spanish + u'       ')

    def test_internal_textual_width_le(self):
        test_data = ''.join([self.u_mixed, self.u_spanish])
        tw = display.textual_width(test_data)
        self.assertEqual(display._textual_width_le(68, self.u_mixed, self.u_spanish), (tw <= 68))
        self.assertEqual(display._textual_width_le(69, self.u_mixed, self.u_spanish), (tw <= 69))
        self.assertEqual(display._textual_width_le(137, self.u_mixed, self.u_spanish), (tw <= 137))
        self.assertEqual(display._textual_width_le(138, self.u_mixed, self.u_spanish), (tw <= 138))
        self.assertEqual(display._textual_width_le(78, self.u_mixed, self.u_spanish), (tw <= 78))
        self.assertEqual(display._textual_width_le(79, self.u_mixed, self.u_spanish), (tw <= 79))

    def test_wrap(self):
        '''Test that text wrapping works'''
        self.assertEqual(display.wrap(self.u_mixed), [self.u_mixed])
        self.assertEqual(display.wrap(self.u_paragraph), self.u_paragraph_out)
        self.assertEqual(display.wrap(self.utf8_paragraph), self.u_paragraph_out)
        self.assertEqual(display.wrap(self.u_mixed_para), self.u_mixed_para_out)
        self.assertEqual(display.wrap(self.u_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----'),
            self.u_mixed_para_57_initial_subsequent_out)

    def test_fill(self):
        self.assertEqual(display.fill(self.u_paragraph), u'\n'.join(self.u_paragraph_out))
        self.assertEqual(display.fill(self.utf8_paragraph), u'\n'.join(self.u_paragraph_out))
        self.assertEqual(display.fill(self.u_mixed_para), u'\n'.join(self.u_mixed_para_out))
        self.assertEqual(display.fill(self.u_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----'),
            u'\n'.join(self.u_mixed_para_57_initial_subsequent_out))

    def test_byte_string_textual_width_fill(self):
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 1), self.utf8_mixed)
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 25), self.utf8_mixed + '  ')
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 25, left=False), '  ' + self.utf8_mixed)
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18), self.u_mixed[:-4].encode('utf8') + '       ')
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18, prefix=self.utf8_spanish, suffix=self.utf8_spanish), self.utf8_spanish + self.u_mixed[:-4].encode('utf8') + self.utf8_spanish + '       ')
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18), self.u_mixed[:-4].encode('utf8') + '       ')
        self.assertEqual(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18, prefix=self.utf8_spanish, suffix=self.utf8_spanish), self.utf8_spanish + self.u_mixed[:-4].encode('utf8') + self.utf8_spanish + '       ')
