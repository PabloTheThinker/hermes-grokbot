import tempfile
import unittest
from pathlib import Path

from hermes_grokbot.drop import drop
from hermes_grokbot.protocol import inbox_path, sha256_bytes
from hermes_grokbot.pull import pull_local


class Protocol(unittest.TestCase):
    def test_reject_escape(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                inbox_path(Path(d), "../secret")

    def test_init_and_unchanged_hash(self):
        from hermes_grokbot.cli import main
        from hermes_grokbot.mailbox import init_mailbox

        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "box"
            init_mailbox(home)
            self.assertTrue((home / "seats" / "watch.md").is_file())
            dest = Path(d) / "out.txt"
            (home / "TO-HERMES.txt").write_text("ack\n")
            self.assertEqual(main(["pull", "--home", str(home), "--dest", str(dest), "--state-dir", d]), 0)
            self.assertEqual(main(["pull", "--home", str(home), "--dest", str(dest), "--state-dir", d]), 2)

        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "box"
            dest = Path(d) / "out.txt"
            path, digest = drop(home, "hello from hermes")
            self.assertTrue(path.is_file())
            self.assertEqual(digest, sha256_bytes(path.read_bytes()))
            # peer replies
            reply = home / "TO-HERMES.txt"
            reply.write_text("ack\n")
            got = pull_local(home, dest)
            self.assertIsNotNone(got)
            self.assertEqual(dest.read_text(), "ack\n")

    def test_install_plugin(self):
        from hermes_grokbot.install import install_plugin

        with tempfile.TemporaryDirectory() as d:
            dest = install_plugin(Path(d) / "hermes")
            self.assertTrue((dest / "adapter.py").is_file())
            self.assertTrue((dest / "plugin.yaml").is_file())

        from hermes_grokbot.drop import drop_ssh

        with self.assertRaises(ValueError):
            drop_ssh("nohost", ".", "x")


if __name__ == "__main__":
    unittest.main()
