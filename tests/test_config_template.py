import os
import tempfile
import unittest

from oceano2python.cli.config_template import build_template, interactive_review_split_entries


class ConfigTemplateTests(unittest.TestCase):
    def test_ctd_template_contains_header_regexes(self):
        template = build_template(["data/CTD/cnv/dfr29001.cnv"], "CTD")

        self.assertIn("[ctd]", template)
        self.assertIn("[ctd.header]", template)
        self.assertIn("endHeader = '^[*]END[*]'", template)
        self.assertIn("DATETIME = 'System", template)
        self.assertIn("LATITUDE = 'NMEA", template)
        self.assertIn("LONGITUDE = 'NMEA", template)
        self.assertIn("[ctd.split]", template)

    def test_casino_template_contains_format_section(self):
        template = build_template(
            ["data/CASINO/20230305_101030_20230305_235900_AutoSave24h_piratafr33.csv"],
            "CASINO",
        )

        self.assertIn('[casino.header]', template)
        self.assertIn("isData = 'ACQAUTO'", template)
        self.assertIn("[casino.format]", template)
        self.assertIn("DATE = '(\\d+)-(\\d+)-(\\d+)'", template)
        self.assertIn("TIME = '(\\d+):(\\d+):(\\d+)'", template)
        self.assertIn("LATITUDE = '([NSEW])", template)
        self.assertIn("LONGITUDE = '([NSEW])", template)

    def test_cli_can_write_output_file(self):
        template = build_template(["data/LADCP/fr29001.lad"], "LADCP")
        self.assertIn("[ladcp]", template)
        self.assertIn("[ladcp.split]", template)

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".toml") as handle:
            handle.write(template)
            temp_path = handle.name

        try:
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)
        finally:
            os.unlink(temp_path)

    def test_interactive_review_can_accept_and_add_mappings(self):
        prompts = iter(["SSTP", "96 SSPS", ""])
        messages = []

        reviewed = interactive_review_split_entries(
            assignments=[("RELH", 58)],
            review_items=[{"index": 94, "label": "SBE21 Temp (deg C)", "suggestions": ["TEMP", "TE01", "SSTP"]}],
            known_codes={"RELH", "TEMP", "TE01", "SSTP", "SSPS"},
            input_fn=lambda _prompt: next(prompts),
            output_fn=messages.append,
        )

        self.assertEqual(reviewed, [("RELH", 58), ("SSTP", 94), ("SSPS", 96)])
        self.assertTrue(any("Interactive split review" in message for message in messages))

    def test_build_template_interactive_uses_selected_mapping(self):
        def fake_input(prompt):
            if "Column 47" in prompt:
                return "SSTP"
            return ""

        template = build_template(
            ["data/CASINO/20230305_101030_20230305_235900_AutoSave24h_piratafr33.csv"],
            "CASINO",
            interactive=True,
            input_fn=fake_input,
            output_fn=lambda _message: None,
        )

        self.assertIn("\tSSTP = 47", template)


if __name__ == "__main__":
    unittest.main()
