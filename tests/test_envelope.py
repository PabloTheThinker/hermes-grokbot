import tempfile
import unittest
from pathlib import Path

from hermes_grokbot.cli import main
from hermes_grokbot.envelope import Envelope, parse
from hermes_grokbot.mailbox import assign, init_mailbox


class EnvelopeTests(unittest.TestCase):
    def test_roundtrip(self):
        e = Envelope(body="watch three shops", to="watch", kind="order", sender="hermes", id="abc123abc123")
        got = parse(e.render())
        self.assertEqual(got.body, "watch three shops")
        self.assertEqual(got.to, "watch")
        self.assertEqual(got.kind, "order")

    def test_plain_text_is_chief_order(self):
        got = parse("just a line")
        self.assertEqual(got.body, "just a line")
        self.assertEqual(got.to, "chief")

    def test_assign_writes_outbox(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "box"
            path = assign(home, "recon", "three public shops, file only")
            self.assertTrue(path.is_file())
            self.assertTrue((home / "seats" / "recon.md").is_file())
            self.assertIn("recon", path.read_text())

    def test_doctor_runs(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "box"
            init_mailbox(home)
            self.assertIn(main(["doctor", "--home", str(home)]), (0, 1))

    def test_enable_merges(self):
        from hermes_grokbot.enable import enable_in_config

        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("pyyaml")
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "config.yaml"
            cfg.write_text("plugins:\n  enabled:\n  - irc-platform\ngateway:\n  platforms: {}\n")
            self.assertEqual(enable_in_config(cfg), "enabled")
            text = cfg.read_text()
            self.assertIn("irc-platform", text)
            self.assertIn("grokbot", text)


if __name__ == "__main__":
    unittest.main()
