import io, tempfile, unittest
from contextlib import redirect_stdout, redirect_stderr
from renegade.playground import main
class PlaygroundTests(unittest.TestCase):
 def test_default_and_inline(self):
  output=io.StringIO()
  with redirect_stdout(output): self.assertEqual(main([]), 0)
  text=output.getvalue(); self.assertIn("INPUT", text); self.assertIn("SUMMARY", text)
  with redirect_stdout(io.StringIO()): self.assertEqual(main(["--grid", "[[1,0],[0,1]]"]), 0)
 def test_file_and_errors(self):
  with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
   handle.write("[[1]]"); handle.flush()
   with redirect_stdout(io.StringIO()): self.assertEqual(main(["--file", handle.name]), 0)
  error=io.StringIO()
  with redirect_stderr(error): self.assertEqual(main(["--grid", "bad"]), 2)
  self.assertIn("error:", error.getvalue())
