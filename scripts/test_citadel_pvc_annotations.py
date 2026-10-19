#!/usr/bin/env python3
"""Smoke test: shared PVC annotations merge user keys over resource-policy keep."""
import os
import re
import subprocess
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART = os.path.join(ROOT, "charts/citadel-monolith")
VALUES = os.path.join(CHART, "ci/pvc-annotations-values.yaml")


def render_pvcs() -> str:
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
            "templates/pvc.yaml",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc.stdout


def pvc_block(name: str, rendered: str) -> str:
    docs = re.split(r"\n---\n", rendered)
    for doc in docs:
        if re.search(rf"name: .*-{re.escape(name)}\s*$", doc, re.MULTILINE):
            return doc
    raise AssertionError(f"pvc for {name!r} not found")


class TestCitadelPvcAnnotations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = render_pvcs()

    def test_default_keeps_resource_policy_only(self):
        block = pvc_block("plain", self.rendered)
        self.assertIn('"helm.sh/resource-policy": "keep"', block)
        self.assertNotIn("helm.sh/hook", block)

    def test_user_annotations_keep_resource_policy(self):
        block = pvc_block("hooked", self.rendered)
        self.assertIn('"helm.sh/resource-policy": "keep"', block)
        self.assertIn('"helm.sh/hook": "pre-install"', block)
        self.assertIn('"helm.sh/hook-weight": "-5"', block)
        self.assertIn('"example.com/owner": "platform"', block)


if __name__ == "__main__":
    unittest.main()
