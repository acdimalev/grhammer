from unittest import TestCase
from hypothesis import given
import hypothesis.strategies as st

from grhammer.parsers import ParseOk, ParseError
import grhammer.parsers as parsers

iterations = 256


def sorted_range_parser(a, b):
    if a > b:
        (a, b) = (b, a)
    return parsers.Range(a, b)


class TestParsers(TestCase):

    @given(
        st.one_of(
            st.builds(parsers.Literal, st.characters()),
            st.builds(sorted_range_parser, st.characters(), st.characters()),
            st.builds(parsers.Any),
        ),
        st.randoms(),
    )
    def test_generation_is_bounded_by_parsing(self, parser, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            result = parser.parse(parser.generate(entropy))
            self.assertIsInstance(result, ParseOk)
            self.assertEqual(result.remaining, '')
