import os
import tempfile
import unittest

from config_parser import config


class ConfigParserTests(unittest.TestCase):
    def _write_temp_conf(self, content: str) -> str:
        fd, path = tempfile.mkstemp(prefix="selector_conf_", suffix=".txt")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_ignores_selector_type(self):
        content = """
# comentario
SESSION_0_TYPE=selector
SESSION_0_TITLE=Selector
SESSION_0_SCREEN=1
SESSION_1_TYPE=2019
SESSION_1_TITLE=Linux
SESSION_1_SCREEN=2
""".strip()
        path = self._write_temp_conf(content)
        try:
            cfg = config(path)
            self.assertEqual(cfg.numeroSesiones, 1)
            self.assertEqual(cfg.sessionsList[0]["TYPE"], "2019")
        finally:
            os.remove(path)

    def test_sessions_limit_is_applied(self):
        content = """
SESSION_0_TYPE=2019
SESSION_0_TITLE=A
SESSION_0_SCREEN=1
SESSION_1_TYPE=2012
SESSION_1_TITLE=B
SESSION_1_SCREEN=2
SESSION_2_TYPE=nx
SESSION_2_TITLE=C
SESSION_2_SCREEN=3
""".strip()
        path = self._write_temp_conf(content)
        try:
            cfg = config(path, sessions_limit=2)
            self.assertEqual(cfg.numeroSesiones, 2)
            self.assertEqual([x["TYPE"] for x in cfg.sessionsList], ["2019", "2012"])
        finally:
            os.remove(path)

    def test_multi_digit_session_index_is_parsed(self):
        content = """
SESSION_10_TYPE=2019
SESSION_10_TITLE=Z
SESSION_10_SCREEN=7
""".strip()
        path = self._write_temp_conf(content)
        try:
            cfg = config(path)
            self.assertEqual(cfg.numeroSesiones, 1)
            self.assertEqual(cfg.sessionsList[0]["TYPE"], "2019")
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
