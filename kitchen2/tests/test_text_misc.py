# -*- coding: utf-8 -*-
#
import unittest

try:
    import chardet
except ImportError:
    chardet = None

from kitchen.text import misc
from kitchen.text.exceptions import ControlCharError
from kitchen.text.converters import to_unicode

import base_classes

class TestTextMisc(unittest.TestCase, base_classes.UnicodeTestData):
    def test_guess_encoding_no_chardet(self):
        # Test that unicode strings are not allowed
        self.assertRaises(TypeError, misc.guess_encoding, self.u_spanish)

        self.assertTrue(misc.guess_encoding(self.utf8_spanish, disable_chardet=True) == 'utf-8')
        self.assertTrue(misc.guess_encoding(self.latin1_spanish, disable_chardet=True) == 'latin-1')
        self.assertTrue(misc.guess_encoding(self.utf8_japanese, disable_chardet=True) == 'utf-8')
        self.assertTrue(misc.guess_encoding(self.euc_jp_japanese, disable_chardet=True) == 'latin-1')

    def test_guess_encoding_with_chardet(self):
        # We go this slightly roundabout way because multiple encodings can
        # output the same byte sequence.  What we're really interested in is
        # if we can get the original unicode string without knowing the
        # converters beforehand
        self.assertTrue(to_unicode(self.utf8_spanish,
            misc.guess_encoding(self.utf8_spanish)) == self.u_spanish)
        self.assertTrue(to_unicode(self.latin1_spanish,
            misc.guess_encoding(self.latin1_spanish)) == self.u_spanish)
        self.assertTrue(to_unicode(self.utf8_japanese,
            misc.guess_encoding(self.utf8_japanese)) == self.u_japanese)

    def test_guess_encoding_with_chardet_installed(self):
        if chardet:
            self.assertTrue(to_unicode(self.euc_jp_japanese,
                misc.guess_encoding(self.euc_jp_japanese)) == self.u_japanese)
        else:
            self.skipTest('chardet not installed, euc_jp will not be guessed correctly')

    def test_guess_encoding_with_chardet_uninstalled(self):
        if chardet:
            self.skipTest('chardet installed, euc_jp will not be mangled')
        else:
            self.assertTrue(to_unicode(self.euc_jp_japanese,
                misc.guess_encoding(self.euc_jp_japanese)) ==
                self.u_mangled_euc_jp_as_latin1)

    def test_str_eq(self):
        # str vs str:
        self.assertTrue(misc.str_eq(self.euc_jp_japanese, self.euc_jp_japanese) == True)
        self.assertTrue(misc.str_eq(self.utf8_japanese, self.utf8_japanese) == True)
        self.assertTrue(misc.str_eq(self.b_ascii, self.b_ascii) == True)
        self.assertTrue(misc.str_eq(self.euc_jp_japanese, self.latin1_spanish) == False)
        self.assertTrue(misc.str_eq(self.utf8_japanese, self.euc_jp_japanese) == False)
        self.assertTrue(misc.str_eq(self.b_ascii, self.b_ascii[:-2]) == False)

        # unicode vs unicode:
        self.assertTrue(misc.str_eq(self.u_japanese, self.u_japanese) == True)
        self.assertTrue(misc.str_eq(self.u_ascii, self.u_ascii) == True)
        self.assertTrue(misc.str_eq(self.u_japanese, self.u_spanish) == False)
        self.assertTrue(misc.str_eq(self.u_ascii, self.u_ascii[:-2]) == False)

        # unicode vs str with default utf-8 conversion:
        self.assertTrue(misc.str_eq(self.u_japanese, self.utf8_japanese) == True)
        self.assertTrue(misc.str_eq(self.u_ascii, self.b_ascii) == True)
        self.assertTrue(misc.str_eq(self.u_japanese, self.euc_jp_japanese) == False)
        self.assertTrue(misc.str_eq(self.u_ascii, self.b_ascii[:-2]) == False)

        # unicode vs str with explicit encodings:
        self.assertTrue(misc.str_eq(self.u_japanese, self.euc_jp_japanese, encoding='euc_jp') == True)
        self.assertTrue(misc.str_eq(self.u_japanese, self.utf8_japanese, encoding='utf8') == True)
        self.assertTrue(misc.str_eq(self.u_ascii, self.b_ascii, encoding='latin1') == True)
        self.assertTrue(misc.str_eq(self.u_japanese, self.euc_jp_japanese, encoding='latin1') == False)
        self.assertTrue(misc.str_eq(self.u_japanese, self.utf8_japanese, encoding='euc_jp') == False)
        self.assertTrue(misc.str_eq(self.u_japanese, self.utf8_japanese, encoding='euc_jp') == False)
        self.assertTrue(misc.str_eq(self.u_ascii, self.b_ascii[:-2], encoding='latin1') == False)

        # str vs unicode (reverse parameter order of unicode vs str)
        self.assertTrue(misc.str_eq(self.utf8_japanese, self.u_japanese) == True)
        self.assertTrue(misc.str_eq(self.b_ascii, self.u_ascii) == True)
        self.assertTrue(misc.str_eq(self.euc_jp_japanese, self.u_japanese) == False)
        self.assertTrue(misc.str_eq(self.b_ascii, self.u_ascii[:-2]) == False)

        self.assertTrue(misc.str_eq(self.euc_jp_japanese, self.u_japanese, encoding='euc_jp') == True)
        self.assertTrue(misc.str_eq(self.utf8_japanese, self.u_japanese, encoding='utf8') == True)
        self.assertTrue(misc.str_eq(self.b_ascii, self.u_ascii, encoding='latin1') == True)
        self.assertTrue(misc.str_eq(self.euc_jp_japanese, self.u_japanese, encoding='latin1') == False)
        self.assertTrue(misc.str_eq(self.utf8_japanese, self.u_japanese, encoding='euc_jp') == False)
        self.assertTrue(misc.str_eq(self.utf8_japanese, self.u_japanese, encoding='euc_jp') == False)
        self.assertTrue(misc.str_eq(self.b_ascii, self.u_ascii[:-2], encoding='latin1') == False)


    def test_process_control_chars(self):
        self.assertRaises(TypeError, misc.process_control_chars, 'byte string')
        self.assertRaises(ControlCharError, misc.process_control_chars,
                *[self.u_ascii_chars], **{'strategy': 'strict'})
        self.assertTrue(misc.process_control_chars(self.u_ascii_chars,
            strategy='ignore') == self.u_ascii_no_ctrl)
        self.assertTrue(misc.process_control_chars(self.u_ascii_chars,
            strategy='replace') == self.u_ascii_ctrl_replace)

    def test_html_entities_unescape(self):
        self.assertRaises(TypeError, misc.html_entities_unescape, 'byte string')
        self.assertTrue(misc.html_entities_unescape(self.u_entity_escape) == self.u_entity)
        self.assertTrue(misc.html_entities_unescape(u'<tag>%s</tag>'
            % self.u_entity_escape) == self.u_entity)
        self.assertTrue(misc.html_entities_unescape(u'a&#1234567890;b') == u'a&#1234567890;b')
        self.assertTrue(misc.html_entities_unescape(u'a&#xfffd;b') == u'a\ufffdb')
        self.assertTrue(misc.html_entities_unescape(u'a&#65533;b') == u'a\ufffdb')

    def test_byte_string_valid_xml(self):
        self.assertTrue(misc.byte_string_valid_xml(u'unicode string') == False)

        self.assertTrue(misc.byte_string_valid_xml(self.utf8_japanese))
        self.assertTrue(misc.byte_string_valid_xml(self.euc_jp_japanese, 'euc_jp'))

        self.assertTrue(misc.byte_string_valid_xml(self.utf8_japanese, 'euc_jp') == False)
        self.assertTrue(misc.byte_string_valid_xml(self.euc_jp_japanese, 'utf8') == False)

        self.assertTrue(misc.byte_string_valid_xml(self.utf8_ascii_chars) == False)

    def test_byte_string_valid_encoding(self):
        '''Test that a byte sequence is validated'''
        self.assertTrue(misc.byte_string_valid_encoding(self.utf8_japanese) == True)
        self.assertTrue(misc.byte_string_valid_encoding(self.euc_jp_japanese, encoding='euc_jp') == True)

    def test_byte_string_invalid_encoding(self):
        '''Test that we return False with non-encoded chars'''
        self.assertTrue(misc.byte_string_valid_encoding('\xff') == False)
        self.assertTrue(misc.byte_string_valid_encoding(self.euc_jp_japanese) == False)

class TestIsStringTypes(unittest.TestCase):
    def test_isbasestring(self):
        self.assertTrue(misc.isbasestring('abc'))
        self.assertTrue(misc.isbasestring(u'abc'))
        self.assertFalse(misc.isbasestring(5))

    def test_isbytestring(self):
        self.assertTrue(misc.isbytestring('abc'))
        self.assertFalse(misc.isbytestring(u'abc'))
        self.assertFalse(misc.isbytestring(5))

    def test_isunicodestring(self):
        self.assertFalse(misc.isunicodestring('abc'))
        self.assertTrue(misc.isunicodestring(u'abc'))
        self.assertFalse(misc.isunicodestring(5))
