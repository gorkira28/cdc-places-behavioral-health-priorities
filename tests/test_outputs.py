import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class OutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scores = pd.read_csv(ROOT / "data/processed/county_priority_scores.csv", dtype={"countyfips": str})
        cls.qa = json.loads((ROOT / "outputs/qa_report.json").read_text(encoding="utf-8"))

    def test_county_key_and_score(self):
        self.assertEqual(len(self.scores), self.scores["countyfips"].nunique())
        self.assertTrue(self.scores["priority_score"].between(0, 100).all())

    def test_source_validation(self):
        v = self.qa["validation"]
        self.assertEqual(v["rows"], v["unique_counties"])
        self.assertEqual(v["bad_fips"], 0)
        self.assertEqual(v["bad_depression"], 0)
        self.assertEqual(v["bad_mhlth"], 0)
        self.assertEqual(v["bad_access"], 0)
        self.assertEqual(v["complete_components"], len(self.scores))

    def test_artifacts_exist(self):
        required = [
            "data/processed/county_priority_scores.geojson",
            "data/processed/county_priority_scores.gpkg",
            "outputs/figures/national_priority_map.png",
            "outputs/figures/portfolio_preview.png",
            "outputs/tables/highest_priority_counties.csv",
        ]
        for rel in required:
            self.assertGreater((ROOT / rel).stat().st_size, 1000, rel)


if __name__ == "__main__":
    unittest.main()
