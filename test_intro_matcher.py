"""
test_intro_matcher.py
=====================
Unit Test Suite – AI Professional Networking Matcher
-----------------------------------------------------
Tests the core matching logic, normalisation pipeline, edge-case handling,
and output formatting of `intro_matcher.py`.

Run with:
    python3 -m unittest -v test_intro_matcher.py

All test cases are grouped in a single TestCase class so they share setUp
state and can be run as a suite or individually.
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import unittest

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
from intro_matcher import match, format_match, Match, Profile


# ===========================================================================
# TEST SUITE
# ===========================================================================

class TestIntroMatcher(unittest.TestCase):
    """
    Comprehensive tests for intro_matcher.py covering:
      - Happy-path multi-field matching
      - Text normalisation (stemming / plurals)
      - Domain synonym expansion
      - Edge cases: empty input, invalid top_k, stopword-only queries,
        zero-match queries
      - Output formatter
    """

    # -----------------------------------------------------------------------
    # TEST 1 – Happy path: a realistic user query
    # -----------------------------------------------------------------------
    def test_sample_backend_payments_query(self):
        """
        Verifies the canonical demo query returns the expected top-3 matches
        in the correct order with accurate scores and hit tokens.

        Score breakdown for top result (Mei):
          "backend"  → title match  → 2.5
          "engineer" → title match  → 2.5
          "payment"  → skill match  → 3.0
          Total = 8.0
        """
        query = "I need a backend engineer who has worked on payments"
        results = match(query)

        # Should return exactly 3 profiles (default top_k)
        self.assertEqual(len(results), 3)

        # Every result must be a Match instance
        self.assertIsInstance(results[0], Match)

        # Mei is the best match (score 8.0 – hits all three relevant fields)
        self.assertEqual(results[0].profile.name, "Mei")
        self.assertAlmostEqual(results[0].score, 8.0)

        # "payment" (stemmed from "payments") must appear in Mei's hit tokens
        self.assertIn("payment", results[0].hits)

        # Priya and Wei should also appear in the top 3 (both score 5.5)
        names = [m.profile.name for m in results]
        self.assertIn("Priya", names)
        self.assertIn("Wei", names)

    # -----------------------------------------------------------------------
    # TEST 2 – Normalisation: singular and plural queries must yield the same results
    # -----------------------------------------------------------------------
    def test_plural_and_stemming(self):
        """
        Confirms that the naïve stemmer in _norm() makes "payment" and
        "payments" interchangeable, so users get consistent results regardless
        of how they phrase a query.
        """
        # Both singular and plural forms of the token should produce
        # identical ranked result lists
        res_singular = match("payment")
        res_plural   = match("payments")

        names_singular = [m.profile.name for m in res_singular]
        names_plural   = [m.profile.name for m in res_plural]

        self.assertEqual(names_singular, names_plural)

    # -----------------------------------------------------------------------
    # TEST 3 – Synonym / alias expansion
    # -----------------------------------------------------------------------
    def test_domain_synonym_expansion(self):
        """
        Verifies ALIASES mapping: Wei lists "Stripe" as a skill, which is
        aliased to "payments". A query for "payments" must therefore surface Wei.

        This validates that company/tool names expand to their domain concepts.
        """
        results = match("payments")
        names = [m.profile.name for m in results]

        # Wei uses Stripe (→ "payments" after alias expansion) so must appear
        self.assertIn("Wei", names)

    # -----------------------------------------------------------------------
    # TEST 4 – Edge case: empty and whitespace-only queries
    # -----------------------------------------------------------------------
    def test_empty_and_whitespace_query(self):
        """
        An empty string or a string of only whitespace produces no tokens
        after tokenisation, so match() must return an empty list rather than
        raising an error or returning all profiles.
        """
        self.assertEqual(match(""),    [])   # completely empty
        self.assertEqual(match("   "), [])   # whitespace only

    # -----------------------------------------------------------------------
    # TEST 5 – Edge case: non-positive top_k
    # -----------------------------------------------------------------------
    def test_invalid_top_k(self):
        """
        top_k controls the maximum result count.  Values of 0 or negative are
        invalid and must immediately return [] without scoring any profiles.
        """
        self.assertEqual(match("engineer", top_k=0),  [])  # zero → no results
        self.assertEqual(match("engineer", top_k=-1), [])  # negative → no results

    # -----------------------------------------------------------------------
    # TEST 6 – Edge case: query consisting entirely of stopwords
    # -----------------------------------------------------------------------
    def test_stopwords_only(self):
        """
        After stopword filtering, a query such as "I need someone who has
        worked with" reduces to zero meaningful tokens, so match() must
        return [] rather than matching every profile.
        """
        self.assertEqual(match("I need someone who has worked with"), [])

    # -----------------------------------------------------------------------
    # TEST 7 – Edge case: query with no matching profiles
    # -----------------------------------------------------------------------
    def test_zero_matches(self):
        """
        A query on skills/topics not represented in any profile must return []
        rather than a partial or incorrect list.
        """
        # Neither "rust" nor "blockchain" appear in any profile
        self.assertEqual(match("Rust and blockchain"), [])

    # -----------------------------------------------------------------------
    # TEST 8 – Output formatter
    # -----------------------------------------------------------------------
    def test_formatting(self):
        """
        format_match() must produce a human-readable string that:
          - starts with the matched person's name
          - includes the rounded score
          - follows the documented template format

        Uses "designer" to reliably surface Daniel as the top (and only) match.
        """
        results = match("designer")

        # Sanity: at least one result to format
        self.assertTrue(len(results) > 0)

        formatted = format_match(results[0])

        # Daniel is the only designer; output should start with his name and score
        self.assertTrue(formatted.startswith("Daniel (Score: 2.5"))


# ===========================================================================
# SCRIPT ENTRY POINT
# Allows running tests directly: python3 test_intro_matcher.py
# ===========================================================================

if __name__ == "__main__":
    unittest.main()
