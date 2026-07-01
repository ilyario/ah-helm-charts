#!/usr/bin/env python3
"""Smoke test: application updateStrategy renders correct Deployment strategy."""
import os
import re
import subprocess
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART = os.path.join(ROOT, "charts/citadel-monolith")
VALUES = os.path.join(CHART, "ci/update-strategy-values.yaml")


def render_deployments() -> str:
    proc = subprocess.run(
        [
            "helm",
            "template",
            "t",
            CHART,
            "-f",
            VALUES,
            "--namespace",
            "app-test",
            "--show-only",
            "templates/deployment.yaml",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc.stdout


def deployment_block(name: str, rendered: str) -> str:
    docs = re.split(r"\n---\n", rendered)
    for doc in docs:
        if re.search(rf"name: .*-{re.escape(name)}\s*$", doc, re.MULTILINE):
            return doc
    raise AssertionError(f"deployment for {name!r} not found")


class TestCitadelUpdateStrategy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = render_deployments()

    def test_recreate_strategy(self):
        block = deployment_block("recreate-app", self.rendered)
        self.assertIn("type: Recreate", block)
        self.assertNotIn("rollingUpdate:", block)

    def test_rolling_update_strategy(self):
        block = deployment_block("rolling-app", self.rendered)
        self.assertIn("type: RollingUpdate", block)
        self.assertIn("maxUnavailable: 0", block)
        self.assertIn("maxSurge: 1", block)

    def test_default_omits_strategy(self):
        proc = subprocess.run(
            [
                "helm",
                "template",
                "t",
                CHART,
                "-f",
                os.path.join(CHART, "ci/hpa-values.yaml"),
                "--namespace",
                "app-test",
                "--show-only",
                "templates/deployment.yaml",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertNotIn("strategy:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
