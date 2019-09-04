from unittest import TestCase
from hypothesis import given, assume
from hypothesis.strategies import *

from grhammer.parsers import *
from grhammer.strategies import *

iterations = 32


def parsers_are_good(entropy, some_parsers):
    try:
        for parser in some_parsers:
            parser.generate(entropy)
    except GenerationException:
        return False
    return True


class TestParsers(TestCase):

    @given(
        parsers(),
        randoms(),
    )
    def test_generation_is_bounded_by_parsing(self, parser, random):
        entropy = lambda k: k and random.getrandbits(k)
        assume(parsers_are_good(entropy, [parser]))
        for _ in range(iterations):
            # FIXME: Calculate statistics of bogus test pass.
            try:
                result = parser.parse(parser.generate(entropy))
                self.assertIsInstance(result, ParseOk)
                self.assertEqual(0, len(result.remaining))
            except GenerationException:
                pass

    @given(
        one_of(
            just(OneOf),
        ),
        parsers_by_depth(4),
        parsers_by_depth(4),
        parsers_by_depth(4),
        randoms(),
    )
    def test_associativity(self, Parser, a, b, c, random):
        entropy = lambda k: k and random.getrandbits(k)
        assume(parsers_are_good(entropy, [a, b, c]))
        left = Parser([Parser([a, b]), c])
        right = Parser([a, Parser([b, c])])
        flat = Parser([a, b, c])
        # FIXME: This is a lot of work for a single test cycle.
        for _ in range(iterations):
            # FIXME: Calculate statistics of bogus test pass.
            try:
                document = flat.generate(entropy)
                reference = tuple(flat.parse(document))
                self.assertEqual(reference, tuple(left.parse(document)))
                self.assertEqual(reference, tuple(right.parse(document)))
            except GenerationException:
                pass


    @given(
        bad_parsers(),
        randoms(),
    )
    def test_bad_parsers_cannot_generate_documents(self, parser, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            with self.assertRaises(Exception):
                parser.generate(entropy)
