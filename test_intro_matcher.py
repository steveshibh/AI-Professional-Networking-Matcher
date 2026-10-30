import unittest
from intro_matcher import Profile, match_profiles, DEFAULT_PROFILES


class TestIntroMatcher(unittest.TestCase):
    def test_sample_backend_payments_query(self):
        query = "I need a backend engineer who has worked on payments"
        results = match_profiles(query)

        self.assertEqual(len(results), 3)
        # Mei has backend + engineer + payments -> highest score
        self.assertEqual(results[0][2].name, "Mei")
        self.assertIn("payments", results[0][1])

        names = [p.name for _, _, p in results]
        self.assertIn("Priya", names)
        self.assertIn("Wei", names)

    def test_empty_query(self):
        self.assertEqual(match_profiles(""), [])
        self.assertEqual(match_profiles("   "), [])

    def test_stopwords_only_query(self):
        self.assertEqual(match_profiles("I need someone who has worked with"), [])

    def test_zero_matches(self):
        self.assertEqual(match_profiles("Rust and blockchain"), [])

    def test_domain_synonym_expansion(self):
        # Wei has 'Stripe', which maps to 'payments'
        results = match_profiles("payments")
        matched_names = [p.name for _, _, p in results]
        self.assertIn("Wei", matched_names)
        self.assertIn("Priya", matched_names)
        self.assertIn("Mei", matched_names)

    def test_deterministic_tie_breaking(self):
        # Profiles with identical scores break ties by name alphabetically
        p1 = Profile("Bob", "Engineer", ["Python"], "City")
        p2 = Profile("Alice", "Engineer", ["Python"], "City")
        results = match_profiles("Engineer", profiles=[p1, p2])
        self.assertEqual(results[0][2].name, "Alice")
        self.assertEqual(results[1][2].name, "Bob")


if __name__ == "__main__":
    unittest.main()
