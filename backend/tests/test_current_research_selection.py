from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from backend.app.services.imagineer_system import ImagineerSystem


class CurrentResearchSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = ImagineerSystem()
        self.now = datetime.now(timezone.utc)

    def _iso(self, delta: timedelta) -> str:
        return (self.now + delta).isoformat()

    def test_brain_current_cellular_work_replaces_older_wavevis(self) -> None:
        brain_at = self._iso(timedelta(days=-1))
        progress_event_at = self._iso(timedelta(days=-3))
        progress_source_at = self._iso(timedelta(hours=-2))
        wavevis_at = self._iso(timedelta(days=-5))

        selected = self.system._active_research_from_sources(
            brain_state={
                "ok": True,
                "json": {
                    "files": [
                        {
                            "name": "current-research-note.pdf",
                            "kind": "generated pdf",
                            "createdAt": brain_at,
                            "sourceText": (
                                "For the current pressure test, start every used cell at zero psi and the same "
                                "initial width before measuring the Cellular Soft Robots sample."
                            ),
                        }
                    ]
                },
            },
            progress_state={
                "ok": True,
                "json": {
                    "events": [
                        {
                            "created_at": self._iso(timedelta(hours=-1)),
                            "title": "Unrelated current app work",
                            "source_ids": ["unrelated_home"],
                        },
                        {
                            "created_at": progress_event_at,
                            "title": "Cellular Soft Robots manuscript restored",
                            "source_ids": ["paper_railway_state"],
                            "issue": "The active Cellular Soft Robots paper source needed restoration.",
                        },
                        {
                            "created_at": wavevis_at,
                            "title": "WaveVis reference-shape work",
                            "source_ids": ["wavevis_home"],
                            "issue": "Close the WaveVis X-cell reference match.",
                        },
                    ]
                },
            },
            progress_summary_state={
                "ok": True,
                "json": {
                    "latest": {
                        "sources": [
                            {
                                "id": "paper_railway_state",
                                "name": "paper Railway state",
                                "purpose": "Live Cellular Soft Robots manuscript state.",
                                "json": {"updatedAt": progress_source_at},
                            }
                        ]
                    }
                },
            },
        )

        self.assertEqual(selected["research_lane"], "cellular_soft_robots")
        self.assertEqual(selected["current_step"], "Lock the Cellular Soft Robots pressure-test protocol.")
        self.assertEqual(selected["event_created_at"], progress_source_at)
        self.assertEqual(selected["corroboration_count"], 3)
        self.assertIn("Brain current research note", selected["source"])
        self.assertIn("Progress research event", selected["source"])
        self.assertIn("Progress source paper_railway_state", selected["source"])

    def test_expired_wavevis_event_is_not_current(self) -> None:
        selected = self.system._active_research_from_sources(
            brain_state={"ok": True, "json": {"files": []}},
            progress_state={
                "ok": True,
                "json": {
                    "events": [
                        {
                            "created_at": self._iso(timedelta(days=-31)),
                            "title": "WaveVis X-cell reference work",
                            "source_ids": ["wavevis_home"],
                        }
                    ]
                },
            },
            progress_summary_state={"ok": True, "json": {"latest": {"sources": []}}},
        )

        self.assertEqual(selected, {})

    def test_brain_only_result_does_not_claim_progress_corroboration(self) -> None:
        selected = self.system._active_research_from_sources(
            brain_state={
                "ok": True,
                "json": {
                    "files": [
                        {
                            "name": "current-pressure-test.pdf",
                            "kind": "generated pdf",
                            "createdAt": self._iso(timedelta(hours=-1)),
                            "sourceText": (
                                "The current Cellular Soft Robots pressure test needs zero psi and a consistent "
                                "initial cell width."
                            ),
                        }
                    ]
                },
            },
            progress_state={"ok": False},
            progress_summary_state={"ok": False},
        )

        self.assertEqual(selected["corroboration_count"], 1)
        self.assertIn("Brain's newest", selected["why"])
        self.assertNotIn("Progress", selected["why"])


if __name__ == "__main__":
    unittest.main()
