from hypothesis.strategies import *

from .parsers import *


# primitive parsers

def primitive_parsers():
    return one_of(
        literal_parsers(),
        range_parsers(),
        any_parsers(),
    )

def literal_parsers():
    return builds(Literal, characters())

def range_parsers():
    return builds(
        lambda a, b: Range(a, b) if a <= b else Range(b, a),
        characters(), characters(),
    )

def any_parsers():
    return builds(Any)


# combinatorial parsers

def combinatorial_parsers(children):
    return one_of(
        one_of_parsers(children),
        optional_parsers(children),
        many_parsers(children),
        sequence_parsers(children),
        less_parsers(children),
    )

def one_of_parsers(children):
    return builds(OneOf, lists(children, min_size=1))

def optional_parsers(children):
    return builds(Optional, children)

def many_parsers(children):
    return builds(Many, children)

def sequence_parsers(children):
    return builds(Sequence, lists(children, min_size=1))

def less_parsers(children):
    return builds(Less, children, children)


# categories of parsers

def parsers():
    x = one_of(
        primitive_parsers(),
        combinatorial_parsers(deferred(lambda: x)),
    )
    return x

def parsers_by_depth(n):
    if 1 == n:
        return primitive_parsers()
    else:
        previous_parsers = parsers_by_depth(n - 1)
        return one_of(
            previous_parsers,
            combinatorial_parsers(previous_parsers),
        )

def bad_parsers():
    """Parsers that cannot match any document."""
    return one_of(
        just(Sequence([Many(Any()), Literal('0')])),
        just(Less(Literal('0'), Literal('0'))),
    )


# support strategies

def entropys():
    def from_random(random):
        def entropy(n_bits):
            return n_bits and random.getrandbits(n_bits)
        return entropy
    return randoms().map(from_random)
