import unittest
from intro_matcher import match


class TestIntroMatcher(unittest.TestCase):
    def test_sample_query(self):
        results = match("I need a backend engineer who has worked on payments")
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].startswith("Mei"))
        self.assertTrue(any("Priya" in r for r in results))
        self.assertTrue(any("Wei" in r for r in results))

    def test_empty_query(self):
        self.assertEqual(match(""), [])
        self.assertEqual(match("   "), [])

    def test_stopwords_only(self):
        self.assertEqual(match("I need someone who has worked with"), [])

    def test_zero_matches(self):
        self.assertEqual(match("Rust and blockchain"), [])

    def test_domain_synonym_expansion(self):
        # Wei has 'Stripe', mapping to 'payments'
        results = match("payments")
        names = [r.split()[0] for r in results]
        self.assertIn("Wei", names)


if __name__ == "__main__":
    unittest.main()
