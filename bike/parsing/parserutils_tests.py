# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""
Utilities to help with parsing python sourcecode
"""

from textwrap import dedent
from protest.assertions import *
from parserutils import *

class maskEscapedQuotesTests:
    'Masks any escaped quotes with "*" to make it easier to parse strings'
    def masks_escaped_quotes(self):
        src = '\" \\\\\\\" \' \\\\\\\\\"  \'  \''
        assert_equal('" **** \' ****"  \'  \'',maskEscapedQuotes(src))

class maskPythonKeywordsInStringsAndCommentsTests:
    'python keywords showing up in strings and comments can make speedy parsing problematic. This function masks them out'
    def capitializes_any_python_keywords_in_strings(self):
        src = '\"\"\"class try while\"\"\" class2 try2 while2'
        assert_equal('"""CLASS TRY WHILE""" class2 try2 while2',maskPythonKeywordsInStringsAndComments(src))
        assert_equal('"""CLASS TRY WHILE""" class2 try2 while2',maskPythonKeywordsInStringsAndComments(src))
        src = "\'\'\' def if for \'\'\' def2 if2 for2'"
        assert_equal("\'\'\' DEF IF FOR \'\'\' def2 if2 for2'",maskPythonKeywordsInStringsAndComments(src))


class splitLogicalLinesTests:
    r"""A 'logical line' is a line which may span multiple physical lines in the python source,
    e.g. with a "\\" character seperating them, or open brackets."""

    def handles_explicitly_continued_line_with_comment(self):
        physicallines = dedent("""
        z = a + b + \  # comment
        c + d
        pass
        """)
        assert_equal(['\n','z = a + b + \\  # comment\nc + d\n', 'pass\n'],
                     splitLogicalLines(physicallines))

    def handles_line_continued_due_to_open_brackets(self):
        physicallines = dedent("""
        z = a + b + (
        c + d)
        pass
        """)
        assert_equal(['\n', 'z = a + b + (\nc + d)\n', 'pass\n'],
                     splitLogicalLines(physicallines))
                         

    def handles_lines_continued_over_nested_open_braces_and_brackets(self):
        physicallines = dedent("""
        z = a + b + ( c + [d
        + e]
        + f)   # comment
        pass
        """)

        assert_equal(['\n', 'z = a + b + ( c + [d\n+ e]\n+ f)   # comment\n', 'pass\n'],
                     splitLogicalLines(physicallines))

    def handles_multiline_strings(self):
        physicallines = dedent("""
        ''' this is an mlc
        so is this
        '''
        pass
        """)
        assert_equal(['\n', "''' this is an mlc\nso is this\n'''\n", 'pass\n'],
                     splitLogicalLines(physicallines))


class makeLineParseableTests:
    '''
    Takes a snippet of python code taken out of context, and auguments it with noops and whitespace to make it parsable by the python compiler module.

    The linchpin of the BicycleRepairMan fast parsing technique: grep the code to locate an interesting string, then just parse that.
    '''

    def handles_a_dangling_if_statement(self):
        src = "if foo:"
        assert_equal("if foo: pass",makeLineParseable(src))

    def handles_a_dangling_try_statement(self):
        src = "try :"
        assert_equal("try : pass\nexcept: pass",makeLineParseable(src))

    def handles_a_try_statement_with_code_inlined(self):
        src = "try : a = 1"
        assert_equal(("try : a = 1\nexcept: pass"),makeLineParseable(src))

    def handles_a_dangling_except_statement(self):
        src = "except :"
        assert_equal(("try: pass\nexcept : pass"),makeLineParseable(src))

    def handles_a_dangling_finally_statement(self):
        src = "finally:"
        assert_equal(("try: pass\nfinally: pass"),makeLineParseable(src))

    def handles_an_else_statement(self):
        src = "else :"
        assert_equal(("if 0: pass\nelse : pass"),makeLineParseable(src))

    def handles_an_elif_statement(self):
        src = "elif foo:"
        assert_equal(("if 0: pass\nelif foo: pass"),makeLineParseable(src))

