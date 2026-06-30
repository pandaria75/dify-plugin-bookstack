from __future__ import annotations

import unittest

from tools.resource_inputs import (
    normalize_optional_integer,
    normalize_optional_integer_list,
    normalize_optional_string,
    normalize_optional_tags,
    normalize_required_string,
)


class ResourceInputsTestCase(unittest.TestCase):
    def test_normalize_required_string_trims_value(self):
        self.assertEqual(normalize_required_string("  Shelf Name  ", "name"), "Shelf Name")

    def test_normalize_required_string_rejects_empty_values(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "name is required"):
                    normalize_required_string(value, "name")

    def test_normalize_optional_string_returns_none_for_empty_values(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                self.assertIsNone(normalize_optional_string(value))

    def test_normalize_optional_string_trims_non_empty_values(self):
        self.assertEqual(normalize_optional_string("  summary  "), "summary")

    def test_normalize_optional_integer_accepts_numeric_values(self):
        self.assertEqual(normalize_optional_integer(" 7 ", "priority"), 7)
        self.assertEqual(normalize_optional_integer(3, "priority"), 3)

    def test_normalize_optional_integer_returns_none_for_empty_values(self):
        self.assertIsNone(normalize_optional_integer(None, "priority"))
        self.assertIsNone(normalize_optional_integer("", "priority"))
        self.assertIsNone(normalize_optional_integer("  ", "priority"))

    def test_normalize_optional_integer_rejects_invalid_values(self):
        with self.assertRaisesRegex(ValueError, "priority must be an integer"):
            normalize_optional_integer("high", "priority")

    def test_normalize_optional_integer_list_accepts_scalar_or_list_inputs(self):
        self.assertEqual(normalize_optional_integer_list(" 12 ", "books"), [12])
        self.assertEqual(normalize_optional_integer_list([" 4 ", 7, "", None, "10"], "books"), [4, 7, 10])

    def test_normalize_optional_integer_list_returns_none_for_empty_inputs(self):
        self.assertIsNone(normalize_optional_integer_list(None, "books"))
        self.assertIsNone(normalize_optional_integer_list("", "books"))
        self.assertIsNone(normalize_optional_integer_list([" ", None], "books"))

    def test_normalize_optional_integer_list_rejects_invalid_entries(self):
        with self.assertRaisesRegex(ValueError, "books entries must be integers"):
            normalize_optional_integer_list(["4", "abc"], "books")

    def test_normalize_optional_tags_reuses_existing_tag_normalization(self):
        self.assertEqual(
            normalize_optional_tags([" ops ", {"name": "env", "value": " prod "}]),
            [
                {"name": "ops", "value": ""},
                {"name": "env", "value": "prod"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
