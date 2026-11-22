from pathlib import Path
import tempfile
import unittest

from scripts.consolida_diario import consolida


class ConsolidaDiarioTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.branch = "docs/processo-pr"
        self.fragment = self.root / "docs/diario/docs/processo-pr.md"
        self.fragment.parent.mkdir(parents=True)
        self.state = self.root / "docs/stato-progetto.md"
        self.original = "# Stato\n\n## Vecchia voce\n\nEvidenze precedenti.\n"
        self.entry = "## 22 novembre 2026 — Verifica\n\nRisultato con accento: già fatto."
        self.state.write_text(self.original, encoding="utf-8")
        self.fragment.write_text(self.entry + "\n", encoding="utf-8")

    def test_prepend_and_remove_only_selected_fragment(self):
        other = self.fragment.with_name("altra-pr.md")
        other.touch()
        self.assertTrue(consolida(self.root, self.branch))
        self.assertEqual(self.state.read_text(encoding="utf-8"),
                         "# Stato\n\n" + self.entry + "\n\n" + self.original[9:])
        self.assertFalse(self.fragment.exists())
        self.assertTrue(other.exists())
        self.assertFalse(consolida(self.root, self.branch))

    def test_retry_after_diary_replaced(self):
        consolidated = "# Stato\n\n" + self.entry + "\n\n## Voce precedente\n"
        self.state.write_text(consolidated, encoding="utf-8")
        self.assertTrue(consolida(self.root, self.branch))
        self.assertEqual(self.state.read_text(encoding="utf-8"), consolidated)
        self.assertFalse(self.fragment.exists())

    def test_too_many_lines_leave_both_files_intact(self):
        oversized = self.entry + "\n" + "riga\n" * 6
        self.fragment.write_text(oversized, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "massimo 8"):
            consolida(self.root, self.branch)
        self.assertEqual(self.state.read_text(encoding="utf-8"), self.original)
        self.assertEqual(self.fragment.read_text(encoding="utf-8"), oversized)

    def test_reject_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "Nome del ramo"):
            consolida(self.root, "../stato-progetto")
