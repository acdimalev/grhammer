from unittest import TestCase
from hypothesis import given
import hypothesis.strategies as st

import grhammer.rng as rng

iterations = 256


class TestRNG(TestCase):

    @given(
        st.integers(min_value=0, max_value=1024),
    )
    def test_entropy_range(self, n_bits):
        x = rng.entropy(n_bits)
        self.assertIsInstance(x, int)
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, 2 ** n_bits)

    @given(
        st.integers(min_value=1),
        st.randoms(),
    )
    def test_roll_range(self, n, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            x = rng.roll(entropy, n)
            self.assertIsInstance(x, int)
            self.assertGreaterEqual(x, 0)
            self.assertLess(x, n)

    @given(
        st.integers(),
        st.integers(),
        st.randoms(),
    )
    def test_in_range_range(self, a, b, random):
        entropy = lambda k: k and random.getrandbits(k)
        if a > b:
            (a, b) = (b, a)
        for _ in range(iterations):
            x = rng.in_range(entropy, a, b)
            self.assertIsInstance(x, int)
            self.assertGreaterEqual(x, a)
            self.assertLessEqual(x, b)

    @given(
        st.lists(st.one_of(
            st.booleans(),
            st.integers(),
            st.floats(),
            st.text(),
        ), min_size=1),
        st.randoms(),
    )
    def test_one_of_range(self, options, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            x = rng.one_of(entropy, options)
            self.assertIn(x, options)

    @given(
        st.randoms(),
    )
    def test_maybe_range(self, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            x = rng.maybe(entropy)
            self.assertIn(x, [False, True])

    @given(
        st.randoms(),
    )
    def test_scale_range(self, random):
        entropy = lambda k: k and random.getrandbits(k)
        for _ in range(iterations):
            x = rng.maybe(entropy)
            self.assertIsInstance(x, int)
            self.assertGreaterEqual(x, 0)
