"""This module contains a variety of functions for extracting random values from
a source of entropy.  These functions are particularly useful for generating
random documents and random assortments of parsers.

The source of entropy for each of these functions is expected to be a function
that, when provided with a positive integer, returns an integer produced from
that number or random bits.

A reference implementation of entropy is also provided here.
"""


import math, random


def entropy(n_bits):
    """A reference source of entropy."""
    return n_bits and random.getrandbits(n_bits)


def roll(entropy, n):
    """From 0 to n - 1."""

    # Minimum bit depth to cover the full range.
    # Note that more bits would be more fair.
    bit_depth = math.ceil(math.log2(n))

    x = entropy(bit_depth)

    # Scale from total range to desired range.
    # Numbers with higher odds will be evenly distributed.
    return math.floor(x * n / 2 ** bit_depth)


def in_range(entropy, first, last):
    """From first to last."""
    return first + roll(entropy, last - first + 1)


def one_of(entropy, options):
    """One of a set of options."""

    # Coerce to list; could be an iterator or set.
    options = list(options)

    return options[roll(entropy, len(options))]


def maybe(entropy):
    """True or False."""
    return one_of(entropy, [False, True])


def scale(entropy):
    """From 0 to positive infinity."""

    # Double scale with each successive 1.
    bit_depth = 0
    while entropy(1):
        bit_depth += 1

    # Return a random number within the scale.
    return 2 ** bit_depth + entropy(bit_depth) - 1
