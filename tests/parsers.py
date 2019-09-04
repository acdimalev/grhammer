from unittest import TestCase
from hypothesis import given, assume
import hypothesis.strategies as st

from grhammer.parsers import ParseOk, ParseError
import grhammer.parsers as parsers

iterations = 32


# primitive parsers

parser_literals = lambda: st.builds(parsers.Literal, st.characters())
parser_ranges = lambda: st.builds(
    lambda a, b: parsers.Range(a, b) if a <= b else parsers.Range(b, a),
    st.characters(), st.characters(),
)
parser_any = lambda: st.builds(parsers.Any)


# combinatorial parsers

parser_one_of = lambda children: st.builds(
    parsers.OneOf, st.lists(children, 1),
)
parser_optional = lambda children: st.builds(
    parsers.Optional, children,
)
parser_many = lambda children: st.builds(
    parsers.Many, children,
)
parser_sequence = lambda children: st.builds(
    parsers.Sequence, st.lists(children, 1),
)
parser_less = lambda children: st.builds(
    parsers.Less, children, children,
)


# parsers by category

parser_primitives = lambda: st.one_of(
    parser_literals(),
    parser_ranges(),
    parser_any(),
)
parser_combinators = lambda children: st.one_of(
    parser_one_of(children),
    parser_optional(children),
    parser_many(children),
    parser_sequence(children),
    parser_less(children),
)
st_parsers = lambda: st.one_of(
    parser_primitives(),
    parser_combinators(st.deferred(lambda: st_parsers())),
)


# parsers by depth

parsers_by_depth = lambda n: (
    parser_primitives()
) if n == 1 else (
    st.one_of(
        parsers_by_depth(n - 1),
        parser_combinators(parsers_by_depth(n - 1)),
    )
)


# special-purpose parsers

# parsers that cannot match any document
bad_parsers = lambda: st.one_of(
    st.just(parsers.Sequence([parsers.Many(parsers.Any()), parsers.Literal('0')])),
)


def parsers_are_good(entropy, some_parsers):
    try:
        for parser in some_parsers:
            parser.generate(entropy)
    except parsers.GenerationException:
        return False
    return True


class TestParsers(TestCase):

    @given(
        st_parsers(),
        st.randoms(),
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
            except parsers.GenerationException:
                pass

    @given(
        st.one_of(
            st.just(parsers.OneOf),
        ),
        parsers_by_depth(4),
        parsers_by_depth(4),
        parsers_by_depth(4),
        st.randoms(),
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
            except parsers.GenerationException:
                pass


    @given(
        bad_parsers(),
        st.randoms(),
    )
    def test_bad_parsers_cannot_generate_documents(self, parser, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            with self.assertRaises(Exception):
                parser.generate(entropy)
