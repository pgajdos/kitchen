# -*- coding: utf-8 -*-
#

import unittest

import io
import sys
import warnings

try:
    import chardet
except:
    chardet = None

from kitchen.text import converters
from kitchen.text.exceptions import XmlEncodeError

import base_classes

class UnicodeNoStr(object):
    def __unicode__(self):
        return 'El veloz murciélago saltó sobre el perro perezoso.'

class StrNoUnicode(object):
    def __str__(self):
        return 'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

class StrReturnsUnicode(object):
    def __str__(self):
        return 'El veloz murciélago saltó sobre el perro perezoso.'

class UnicodeReturnsStr(object):
    def __unicode__(self):
        return 'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

class UnicodeStrCrossed(object):
    def __unicode__(self):
        return 'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

    def __str__(self):
        return 'El veloz murciélago saltó sobre el perro perezoso.'

class ReprUnicode(object):
    def __repr__(self):
        return 'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'

class TestConverters(unittest.TestCase, base_classes.UnicodeTestData):
    def test_to_unicode(self):
        '''Test to_unicode when the user gives good values'''
        self.assertEqual(converters.to_unicode(self.u_japanese, encoding='latin1'), self.u_japanese)

        self.assertEqual(converters.to_unicode(self.utf8_spanish), self.u_spanish)
        self.assertEqual(converters.to_unicode(self.utf8_japanese), self.u_japanese)

        self.assertEqual(converters.to_unicode(self.latin1_spanish, encoding='latin1'), self.u_spanish)
        self.assertEqual(converters.to_unicode(self.euc_jp_japanese, encoding='euc_jp'), self.u_japanese)

        self.assertRaises(TypeError, converters.to_unicode, *[5], **{'nonstring': 'foo'})

    def test_to_unicode_errors(self):
        self.assertEqual(converters.to_unicode(self.latin1_spanish), self.u_mangled_spanish_latin1_as_utf8)
        self.assertEqual(converters.to_unicode(self.latin1_spanish, errors='ignore'), self.u_spanish_ignore)
        self.assertRaises(UnicodeDecodeError, converters.to_unicode,
                *[self.latin1_spanish], **{'errors': 'strict'})

    def test_to_unicode_nonstring(self):
        self.assertEqual(converters.to_unicode(5), '5')
        self.assertEqual(converters.to_unicode(5, nonstring='empty'), '')
        self.assertEqual(converters.to_unicode(5, nonstring='passthru'), 5)
        self.assertEqual(converters.to_unicode(5, nonstring='simplerepr'), '5')
        self.assertEqual(converters.to_unicode(5, nonstring='repr'), '5')
        self.assertRaises(TypeError, converters.to_unicode, *[5], **{'nonstring': 'strict'})

        obj_repr = converters.to_unicode(object, nonstring='simplerepr')
        self.assertEqual(obj_repr, "<class 'object'>")
        self.assertTrue(isinstance(obj_repr, str))

    def test_to_unicode_nonstring_with_objects_that_have__unicode__and__str__(self):
        '''Test that to_unicode handles objects that have  __unicode__ and  __str__ methods'''
        if sys.version_info < (3, 0):
            # None of these apply on python3 because python3 does not use __unicode__
            # and it enforces __str__ returning str
            self.assertEqual(converters.to_unicode(UnicodeNoStr(), nonstring='simplerepr'), self.u_spanish)
            self.assertEqual(converters.to_unicode(StrNoUnicode(), nonstring='simplerepr'), self.u_spanish)
            self.assertEqual(converters.to_unicode(UnicodeReturnsStr(), nonstring='simplerepr'), self.u_spanish)

        self.assertEqual(converters.to_unicode(StrReturnsUnicode(), nonstring='simplerepr'), self.u_spanish)
        self.assertEqual(converters.to_unicode(UnicodeStrCrossed(), nonstring='simplerepr'), self.u_spanish)

    def test_to_bytes(self):
        '''Test to_bytes when the user gives good values'''
        self.assertEqual(converters.to_bytes(self.utf8_japanese, encoding='latin1'), self.utf8_japanese)

        self.assertEqual(converters.to_bytes(self.u_spanish), self.utf8_spanish)
        self.assertEqual(converters.to_bytes(self.u_japanese), self.utf8_japanese)

        self.assertEqual(converters.to_bytes(self.u_spanish, encoding='latin1'), self.latin1_spanish)
        self.assertEqual(converters.to_bytes(self.u_japanese, encoding='euc_jp'), self.euc_jp_japanese)

    def test_to_bytes_errors(self):
        self.assertEqual(converters.to_bytes(self.u_mixed, encoding='latin1'),
                self.latin1_mixed_replace)
        self.assertEqual(converters.to_bytes(self.u_mixed, encoding='latin',
            errors='ignore'), self.latin1_mixed_ignore)
        self.assertRaises(UnicodeEncodeError, converters.to_bytes,
            *[self.u_mixed], **{'errors': 'strict', 'encoding': 'latin1'})

    def _check_repr_bytes(self, repr_string, obj_name):
        self.assertTrue(isinstance(repr_string, bytes))
        match = self.repr_re.match(repr_string)
        self.assertNotEqual(match, None)
        self.assertEqual(match.groups()[0], obj_name)

    def test_to_bytes_nonstring(self):
        self.assertEqual(converters.to_bytes(5), b'5')
        self.assertEqual(converters.to_bytes(5, nonstring='empty'), b'')
        self.assertEqual(converters.to_bytes(5, nonstring='passthru'), 5)
        self.assertEqual(converters.to_bytes(5, nonstring='simplerepr'), b'5')
        self.assertEqual(converters.to_bytes(5, nonstring='repr'), b'5')

        # Raise a TypeError if the msg is nonstring and we're set to strict
        self.assertRaises(TypeError, converters.to_bytes, *[5], **{'nonstring': 'strict'})
        # Raise a TypeError if given an invalid nonstring arg
        self.assertRaises(TypeError, converters.to_bytes, *[5], **{'nonstring': 'INVALID'})

        obj_repr = converters.to_bytes(object, nonstring='simplerepr')
        self.assertEqual(obj_repr, b"<class 'object'>")
        self.assertTrue(isinstance(obj_repr, bytes))

    def test_to_bytes_nonstring_with_objects_that_have__unicode__and__str__(self):
        if sys.version_info < (3, 0):
            # This object's _str__ returns a utf8 encoded object
            self.assertEqual(converters.to_bytes(StrNoUnicode(), nonstring='simplerepr'), self.utf8_spanish)
        # No __str__ method so this returns repr
        string = converters.to_bytes(UnicodeNoStr(), nonstring='simplerepr')
        self._check_repr_bytes(string, b'UnicodeNoStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        self.assertEqual(converters.to_bytes(StrReturnsUnicode(), nonstring='simplerepr'), self.utf8_spanish)
        # Unless we explicitly ask for something different
        self.assertEqual(converters.to_bytes(StrReturnsUnicode(),
            nonstring='simplerepr', encoding='latin1'), self.latin1_spanish)

        # This object has no __str__ so it returns repr
        string = converters.to_bytes(UnicodeReturnsStr(), nonstring='simplerepr')
        self._check_repr_bytes(string, b'UnicodeReturnsStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        self.assertEqual(converters.to_bytes(UnicodeStrCrossed(), nonstring='simplerepr'), self.utf8_spanish)

        # This object's __repr__ returns unicode which to_bytes converts to utf8
        self.assertEqual(converters.to_bytes(ReprUnicode(), nonstring='simplerepr'),
                'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))
        self.assertEqual(converters.to_bytes(ReprUnicode(), nonstring='repr'),
                'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))

    def test_unicode_to_xml(self):
        self.assertEqual(converters.unicode_to_xml(None), b'')
        self.assertRaises(XmlEncodeError, converters.unicode_to_xml, *[b'byte string'])
        self.assertRaises(ValueError, converters.unicode_to_xml, *['string'], **{'control_chars': 'foo'})
        self.assertRaises(XmlEncodeError, converters.unicode_to_xml,
                *['string\u0002'], **{'control_chars': 'strict'})
        self.assertEqual(converters.unicode_to_xml(self.u_entity), self.utf8_entity_escape)
        self.assertEqual(converters.unicode_to_xml(self.u_entity, attrib=True), self.utf8_attrib_escape)
        self.assertEqual(converters.unicode_to_xml(self.u_entity, encoding='ascii'), self.ascii_entity_escape)
        self.assertEqual(converters.unicode_to_xml(self.u_entity, encoding='ascii', attrib=True), self.ascii_attrib_escape)

    def test_xml_to_unicode(self):
        self.assertEqual(converters.xml_to_unicode(self.utf8_entity_escape, 'utf8', 'replace'), self.u_entity)
        self.assertEqual(converters.xml_to_unicode(self.utf8_attrib_escape, 'utf8', 'replace'), self.u_entity)
        self.assertEqual(converters.xml_to_unicode(self.ascii_entity_escape, 'ascii', 'replace'), self.u_entity)
        self.assertEqual(converters.xml_to_unicode(self.ascii_attrib_escape, 'ascii', 'replace'), self.u_entity)

    def test_xml_to_byte_string(self):
        self.assertEqual(converters.xml_to_byte_string(self.utf8_entity_escape, 'utf8', 'replace'), self.u_entity.encode('utf8'))
        self.assertEqual(converters.xml_to_byte_string(self.utf8_attrib_escape, 'utf8', 'replace'), self.u_entity.encode('utf8'))
        self.assertEqual(converters.xml_to_byte_string(self.ascii_entity_escape, 'ascii', 'replace'), self.u_entity.encode('utf8'))
        self.assertEqual(converters.xml_to_byte_string(self.ascii_attrib_escape, 'ascii', 'replace'), self.u_entity.encode('utf8'))

        self.assertEqual(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='euc_jp', errors='replace'),
            self.u_entity.encode('euc_jp', 'replace'))
        self.assertEqual(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='latin1', errors='replace'),
            self.u_entity.encode('latin1', 'replace'))
        self.assertEqual(converters.xml_to_byte_string(self.ascii_attrib_escape,
            output_encoding='euc_jp', errors='replace'),
            self.u_entity.encode('euc_jp', 'replace'))
        self.assertEqual(converters.xml_to_byte_string(self.ascii_attrib_escape,
            output_encoding='latin1', errors='replace'),
            self.u_entity.encode('latin1', 'replace'))

    def test_byte_string_to_xml(self):
        self.assertRaises(XmlEncodeError, converters.byte_string_to_xml, *['test'])
        self.assertEqual(converters.byte_string_to_xml(self.utf8_entity), self.utf8_entity_escape)
        self.assertEqual(converters.byte_string_to_xml(self.utf8_entity, attrib=True), self.utf8_attrib_escape)

    def test_bytes_to_xml(self):
        self.assertEqual(converters.bytes_to_xml(self.b_byte_chars), self.b_byte_encoded)

    def test_xml_to_bytes(self):
        self.assertEqual(converters.xml_to_bytes(self.b_byte_encoded), self.b_byte_chars)

    def test_guess_encoding_to_xml(self):
        self.assertEqual(converters.guess_encoding_to_xml(self.u_entity), self.utf8_entity_escape)
        self.assertEqual(converters.guess_encoding_to_xml(self.utf8_spanish), self.utf8_spanish)
        self.assertEqual(converters.guess_encoding_to_xml(self.latin1_spanish), self.utf8_spanish)
        self.assertEqual(converters.guess_encoding_to_xml(self.utf8_japanese), self.utf8_japanese)

    def test_guess_encoding_to_xml_euc_japanese(self):
        if chardet:
            self.assertEqual(converters.guess_encoding_to_xml(self.euc_jp_japanese),
                    self.utf8_japanese)
        else:
            self.skipTest('chardet not installed, euc_japanese won\'t be detected')

    def test_guess_encoding_to_xml_euc_japanese_mangled(self):
        if chardet:
            self.skipTest('chardet installed, euc_japanese won\'t be mangled')
        else:
            self.assertEqual(converters.guess_encoding_to_xml(self.euc_jp_japanese),
                    self.utf8_mangled_euc_jp_as_latin1)

class TestGetWriter(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.io = io.BytesIO()

    def test_utf8_writer(self):
        writer = converters.getwriter('utf-8')
        io = writer(self.io)
        io.write(self.u_japanese + '\n')
        io.seek(0)
        result = io.read().strip()
        self.assertEqual(result, self.utf8_japanese)

        io.seek(0)
        io.truncate(0)
        io.write(self.euc_jp_japanese + b'\n')
        io.seek(0)
        result = io.read().strip()
        self.assertEqual(result, self.euc_jp_japanese)

        io.seek(0)
        io.truncate(0)
        io.write(self.utf8_japanese + b'\n')
        io.seek(0)
        result = io.read().strip()
        self.assertEqual(result, self.utf8_japanese)

    def test_error_handlers(self):
        '''Test setting alternate error handlers'''
        writer = converters.getwriter('latin1')
        io = writer(self.io, errors='strict')
        self.assertRaises(UnicodeEncodeError, io.write, self.u_japanese)


class TestExceptionConverters(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.exceptions = {}
        tests = {'u_jpn': self.u_japanese,
                'u_spanish': self.u_spanish,
                'utf8_jpn': self.utf8_japanese,
                'utf8_spanish': self.utf8_spanish,
                'euc_jpn': self.euc_jp_japanese,
                'latin1_spanish': self.latin1_spanish}
        for test in tests.items():
            try:
                raise Exception(test[1])
            except Exception as xxx_todo_changeme:
                self.exceptions[test[0]] = xxx_todo_changeme
                pass

    def test_exception_to_unicode_with_unicode(self):
        self.assertEqual(converters.exception_to_unicode(self.exceptions['u_jpn']), self.u_japanese)
        self.assertEqual(converters.exception_to_unicode(self.exceptions['u_spanish']), self.u_spanish)

    def test_exception_to_unicode_with_bytes(self):
        self.assertEqual(converters.exception_to_unicode(self.exceptions['utf8_jpn']), self.u_japanese)
        self.assertEqual(converters.exception_to_unicode(self.exceptions['utf8_spanish']), self.u_spanish)
        # Mangled latin1/utf8 conversion but no tracebacks
        self.assertEqual(converters.exception_to_unicode(self.exceptions['latin1_spanish']), self.u_mangled_spanish_latin1_as_utf8)
        # Mangled euc_jp/utf8 conversion but no tracebacks
        self.assertEqual(converters.exception_to_unicode(self.exceptions['euc_jpn']), self.u_mangled_euc_jp_as_utf8)

    def test_exception_to_unicode_custom(self):
        # If given custom functions, then we should not mangle
        c = [lambda e: converters.to_unicode(e.args[0], encoding='euc_jp'),
                lambda e: converters.to_unicode(e, encoding='euc_jp')]
        self.assertEqual(converters.exception_to_unicode(self.exceptions['euc_jpn'],
            converters=c), self.u_japanese)
        c.extend(converters.EXCEPTION_CONVERTERS)
        self.assertEqual(converters.exception_to_unicode(self.exceptions['euc_jpn'],
            converters=c), self.u_japanese)

        c = [lambda e: converters.to_unicode(e.args[0], encoding='latin1'),
                lambda e: converters.to_unicode(e, encoding='latin1')]
        self.assertEqual(converters.exception_to_unicode(self.exceptions['latin1_spanish'],
            converters=c),  self.u_spanish)
        c.extend(converters.EXCEPTION_CONVERTERS)
        self.assertEqual(converters.exception_to_unicode(self.exceptions['latin1_spanish'],
            converters=c),  self.u_spanish)

    def test_exception_to_bytes_with_unicode(self):
        self.assertEqual(converters.exception_to_bytes(self.exceptions['u_jpn']), self.utf8_japanese)
        self.assertEqual(converters.exception_to_bytes(self.exceptions['u_spanish']), self.utf8_spanish)

    def test_exception_to_bytes_with_bytes(self):
        self.assertEqual(converters.exception_to_bytes(self.exceptions['utf8_jpn']), self.utf8_japanese)
        self.assertEqual(converters.exception_to_bytes(self.exceptions['utf8_spanish']), self.utf8_spanish)
        self.assertEqual(converters.exception_to_bytes(self.exceptions['latin1_spanish']), self.latin1_spanish)
        self.assertEqual(converters.exception_to_bytes(self.exceptions['euc_jpn']), self.euc_jp_japanese)

    def test_exception_to_bytes_custom(self):
        # If given custom functions, then we should not mangle
        c = [lambda e: converters.to_bytes(e.args[0], encoding='euc_jp'),
                lambda e: converters.to_bytes(e, encoding='euc_jp')]
        self.assertEqual(converters.exception_to_bytes(self.exceptions['euc_jpn'],
            converters=c), self.euc_jp_japanese)
        c.extend(converters.EXCEPTION_CONVERTERS)
        self.assertEqual(converters.exception_to_bytes(self.exceptions['euc_jpn'],
            converters=c), self.euc_jp_japanese)

        c = [lambda e: converters.to_bytes(e.args[0], encoding='latin1'),
                lambda e: converters.to_bytes(e, encoding='latin1')]
        self.assertEqual(converters.exception_to_bytes(self.exceptions['latin1_spanish'],
            converters=c),  self.latin1_spanish)
        c.extend(converters.EXCEPTION_CONVERTERS)
        self.assertEqual(converters.exception_to_bytes(self.exceptions['latin1_spanish'],
            converters=c),  self.latin1_spanish)


class TestDeprecatedConverters(TestConverters):
    def setUp(self):
        warnings.simplefilter('ignore', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def test_to_xml(self):
        self.assertEqual(converters.to_xml(self.u_entity), self.utf8_entity_escape)
        self.assertEqual(converters.to_xml(self.utf8_spanish), self.utf8_spanish)
        self.assertEqual(converters.to_xml(self.latin1_spanish), self.utf8_spanish)
        self.assertEqual(converters.to_xml(self.utf8_japanese), self.utf8_japanese)

    def test_to_utf8(self):
        self.assertEqual(converters.to_utf8(self.u_japanese), self.utf8_japanese)
        self.assertEqual(converters.to_utf8(self.utf8_spanish), self.utf8_spanish)

    def test_to_str(self):
        self.assertEqual(converters.to_str(self.u_japanese), self.utf8_japanese)
        self.assertEqual(converters.to_str(self.utf8_spanish), self.utf8_spanish)
        self.assertEqual(converters.to_str(object), b"<class 'object'>")

    def test_non_string(self):
        '''Test deprecated non_string parameter'''
        # unicode
        self.assertRaises(TypeError, converters.to_unicode, *[5], **{'non_string': 'foo'})
        self.assertEqual(converters.to_unicode(5, non_string='empty'), '')
        self.assertEqual(converters.to_unicode(5, non_string='passthru'), 5)
        self.assertEqual(converters.to_unicode(5, non_string='simplerepr'), '5')
        self.assertEqual(converters.to_unicode(5, non_string='repr'), '5')
        self.assertRaises(TypeError, converters.to_unicode, *[5], **{'non_string': 'strict'})

        self.assertEqual(converters.to_unicode(StrReturnsUnicode(), non_string='simplerepr'), self.u_spanish)
        self.assertEqual(converters.to_unicode(UnicodeStrCrossed(), non_string='simplerepr'), self.u_spanish)
        if sys.version_info < (3, 0):
            # Not applicable on python3
            self.assertEqual(converters.to_unicode(UnicodeNoStr(), non_string='simplerepr'), self.u_spanish)
            self.assertEqual(converters.to_unicode(StrNoUnicode(), non_string='simplerepr'), self.u_spanish)
            self.assertEqual(converters.to_unicode(UnicodeReturnsStr(), non_string='simplerepr'), self.u_spanish)

        obj_repr = converters.to_unicode(object, non_string='simplerepr')
        self.assertEqual(obj_repr, "<class 'object'>")
        self.assertTrue(isinstance(obj_repr, str))

        # Bytes
        self.assertEqual(converters.to_bytes(5), b'5')
        self.assertEqual(converters.to_bytes(5, non_string='empty'), b'')
        self.assertEqual(converters.to_bytes(5, non_string='passthru'), 5)
        self.assertEqual(converters.to_bytes(5, non_string='simplerepr'), b'5')
        self.assertEqual(converters.to_bytes(5, non_string='repr'), b'5')

        # Raise a TypeError if the msg is non_string and we're set to strict
        self.assertRaises(TypeError, converters.to_bytes, *[5], **{'non_string': 'strict'})
        # Raise a TypeError if given an invalid non_string arg
        self.assertRaises(TypeError, converters.to_bytes, *[5], **{'non_string': 'INVALID'})

        # No __str__ method so this returns repr
        string = converters.to_bytes(UnicodeNoStr(), non_string='simplerepr')
        self._check_repr_bytes(string, b'UnicodeNoStr')

        if sys.version_info < (3, 0):
            # Not applicable on python3
            # This object's _str__ returns a utf8 encoded object
            self.assertEqual(converters.to_bytes(StrNoUnicode(), non_string='simplerepr'), self.utf8_spanish)

        # This object's __str__ returns unicode which to_bytes converts to utf8
        self.assertEqual(converters.to_bytes(StrReturnsUnicode(), non_string='simplerepr'), self.utf8_spanish)
        # Unless we explicitly ask for something different
        self.assertEqual(converters.to_bytes(StrReturnsUnicode(),
            non_string='simplerepr', encoding='latin1'), self.latin1_spanish)

        # This object has no __str__ so it returns repr
        string = converters.to_bytes(UnicodeReturnsStr(), non_string='simplerepr')
        self._check_repr_bytes(string, b'UnicodeReturnsStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        self.assertEqual(converters.to_bytes(UnicodeStrCrossed(), non_string='simplerepr'), self.utf8_spanish)

        # This object's __repr__ returns unicode which to_bytes converts to utf8
        self.assertEqual(converters.to_bytes(ReprUnicode(), non_string='simplerepr'),
                'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))
        self.assertEqual(converters.to_bytes(ReprUnicode(), non_string='repr'),
                'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))

        obj_repr = converters.to_bytes(object, non_string='simplerepr')
        self.assertEqual(obj_repr, b"<class 'object'>")
        self.assertTrue(isinstance(obj_repr, bytes))
