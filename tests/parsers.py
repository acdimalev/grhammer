from unittest import TestCase
from hypothesis import given, assume
from hypothesis.strategies import *

from grhammer.parsers import *
from grhammer.strategies import *

iterations = 32


def parsers_are_good(entropy, some_parsers):
    try:
        for parser in some_parsers:
            parser.generate(entropy, None)
    except GenerationException:
        return False
    return True


class TestParsers(TestCase):

    @given(
        entropys(),
        parsers(),
    )
    def test_generation_is_bounded_by_parsing(self, entropy, parser):
        assume(parsers_are_good(entropy, [parser]))
        for _ in range(iterations):
            # FIXME: Calculate statistics of bogus test pass.
            try:
                result = parser.parse(parser.generate(entropy, None), None)
                self.assertIsInstance(result, ParseOk)
                self.assertEqual(0, len(result.remaining))
            except GenerationException:
                pass

    @given(
        entropys(),
        one_of(
            just(OneOf),
        ),
        parsers_by_depth(4),
        parsers_by_depth(4),
        parsers_by_depth(4),
    )
    def test_associativity(self, entropy, Parser, a, b, c):
        assume(parsers_are_good(entropy, [a, b, c]))
        left = Parser([Parser([a, b]), c])
        right = Parser([a, Parser([b, c])])
        flat = Parser([a, b, c])
        for _ in range(iterations):
            # FIXME: Calculate statistics of bogus test pass.
            try:
                document = flat.generate(entropy, None)
                reference = tuple(flat.parse(document, None))
                self.assertEqual(reference, tuple(left.parse(document, None)))
                self.assertEqual(reference, tuple(right.parse(document, None)))
            except GenerationException:
                pass

    @given(
        entropys(),
        bad_parsers(),
    )
    def test_bad_parsers_cannot_generate_documents(self, entropy, parser):
        for _ in range(iterations):
            with self.assertRaises(Exception):
                parser.generate(entropy, None)
