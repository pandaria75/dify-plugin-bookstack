from __future__ import annotations

import unittest

from tools.page_inputs import normalize_tags


class NormalizeTagsTestCase(unittest.TestCase):
    def test_normalize_tags_returns_none_for_empty_values(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                self.assertIsNone(normalize_tags(value))

    def test_normalize_tags_preserves_single_string_as_single_tag(self):
        self.assertEqual(normalize_tags("  ops  "), ["ops"])

    def test_normalize_tags_normalizes_list_inputs(self):
        self.assertEqual(
            normalize_tags([" ops ", "", 7, None, "runbook", "   "]),
            ["ops", "7", "None", "runbook"],
        )

    def test_normalize_tags_returns_none_for_all_empty_list_items(self):
        self.assertIsNone(normalize_tags(["", "   "]))

    def test_normalize_tags_stringifies_scalar_non_list_values(self):
        self.assertEqual(normalize_tags(42), ["42"])


if __name__ == "__main__":
    unittest.main()
