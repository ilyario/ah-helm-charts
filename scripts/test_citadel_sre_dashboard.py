#!/usr/bin/env python3
"""Smoke test: SRE dashboard JSON is valid and has expected structure."""
import json
import os
import subprocess
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(
    ROOT,
    "charts/citadel-monolith/files/grafana-dashboards/citadel-sre.json",
)


class TestCitadelSreDashboard(unittest.TestCase):
    def test_json_file_exists_and_parses(self):
        self.assertTrue(os.path.isfile(JSON_PATH), JSON_PATH)
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("uid"), "citadel-sre-release")
        self.assertIn("panels", data)
        self.assertGreater(len(data["panels"]), 3)
        names = {v.get("name") for v in data.get("templating", {}).get("list", [])}
        self.assertIn("namespace", names)
        self.assertIn("ingress_controller_namespace", names)

    def test_helm_renders_configmap_with_dashboard(self):
        proc = subprocess.run(
            [
                "helm",
                "template",
                "t",
                os.path.join(ROOT, "charts/citadel-monolith"),
                "-f",
                os.path.join(
                    ROOT,
                    "charts/citadel-monolith/ci/sre-dashboard-values.yaml",
                ),
                "--namespace",
                "app-test",
                "--show-only",
                "templates/grafana-dashboard-configmap.yaml",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            self.fail(proc.stderr or proc.stdout)
        self.assertIn("kind: ConfigMap", proc.stdout)
        self.assertIn("citadel-sre.json:", proc.stdout)
        self.assertIn("citadel-sre-release", proc.stdout)


if __name__ == "__main__":
    unittest.main()
