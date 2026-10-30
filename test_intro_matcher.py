import unittest
from intro_matcher import match, format_match, Match, Profile


class TestIntroMatcher(unittest.TestCase):
    def test_sample_backend_payments_query(self):
        query = "I need a backend engineer who has worked on payments"
        results = match(query)

        self.assertEqual(len(results), 3)
        self.assertIsInstance(results[0], Match)
        # Mei has backend (2.5) + engineer (2.5) + payment (3.0) = 8.0
        self.assertEqual(results[0].profile.name, "Mei")
        self.assertAlmostEqual(results[0].score, 8.0)
        self.assertIn("payment", results[0].hits)

        names = [m.profile.name for m in results]
        self.assertIn("Priya", names)
        self.assertIn("Wei", names)

    def test_plural_and_stemming(self):
        # Querying singular 'payment' matches profiles with 'payments'
        res_singular = match("payment")
        res_plural = match("payments")
        names_singular = [m.profile.name for m in res_singular]
        names_plural = [m.profile.name for m in res_plural]
        self.assertEqual(names_singular, names_plural)

    def test_domain_synonym_expansion(self):
        # Wei has 'Stripe', mapping to 'payments' -> 'payment'
        results = match("payments")
        names = [m.profile.name for m in results]
        self.assertIn("Wei", names)

    def test_empty_and_whitespace_query(self):
        self.assertEqual(match(""), [])
        self.assertEqual(match("   "), [])

    def test_invalid_top_k(self):
        self.assertEqual(match("engineer", top_k=0), [])
        self.assertEqual(match("engineer", top_k=-1), [])

    def test_stopwords_only(self):
        self.assertEqual(match("I need someone who has worked with"), [])

    def test_zero_matches(self):
        self.assertEqual(match("Rust and blockchain"), [])

    def test_formatting(self):
        results = match("designer")
        self.assertTrue(len(results) > 0)
        formatted = format_match(results[0])
        self.assertTrue(formatted.startswith("Daniel (Score: 2.5"))


if __name__ == "__main__":
    unittest.main()
