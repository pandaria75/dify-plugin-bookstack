from __future__ import annotations

import unittest

from tools.page_inputs import normalize_tags


class NormalizeTagsTestCase(unittest.TestCase):
    def test_normalize_tags_returns_none_for_empty_values(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                self.assertIsNone(normalize_tags(value))

    def test_normalize_tags_preserves_single_string_as_single_tag(self):
        self.assertEqual(normalize_tags("  ops  "), [{"name": "ops", "value": ""}])

    def test_normalize_tags_normalizes_name_value_string_inputs(self):
        self.assertEqual(
            normalize_tags(" env : production "),
            [{"name": "env", "value": "production"}],
        )

    def test_normalize_tags_normalizes_structured_dict_inputs(self):
        self.assertEqual(
            normalize_tags([
                {"name": " env ", "value": " production "},
                {"name": "owner", "value": None},
                {"name": "status"},
                {"name": "   ", "value": "skip"},
            ]),
            [
                {"name": "env", "value": "production"},
                {"name": "owner", "value": ""},
                {"name": "status", "value": ""},
            ],
        )

    def test_normalize_tags_normalizes_mixed_list_inputs_in_order(self):
        self.assertEqual(
            normalize_tags([" ops ", "env:prod", {"name": "owner", "value": "team-a"}, "", "   "]),
            [
                {"name": "ops", "value": ""},
                {"name": "env", "value": "prod"},
                {"name": "owner", "value": "team-a"},
            ],
        )

    def test_normalize_tags_returns_none_for_all_empty_list_items(self):
        self.assertIsNone(normalize_tags(["", "   "]))

    def test_normalize_tags_keeps_empty_value_after_separator(self):
        self.assertEqual(normalize_tags("env:   "), [{"name": "env", "value": ""}])

    def test_normalize_tags_stringifies_scalar_non_list_values(self):
        self.assertEqual(normalize_tags(42), [{"name": "42", "value": ""}])


if __name__ == "__main__":
    unittest.main()
