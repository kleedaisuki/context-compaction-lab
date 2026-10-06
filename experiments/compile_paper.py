"""Export the standalone acmart manuscript with an already installed TeX engine.

Use the Codex LaTeX editor for interactive editing. This exporter is a local
fallback and creates the deliverable PDF after three citation/float passes;
it never installs a TeX toolchain. Intermediate objects and logs stay in .cache.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    """Compile the maintained source and copy only a verified PDF to paper/."""
    root = Path(__file__).resolve().parents[1]
    compiler = shutil.which("pdflatex")
    if compiler is None:
        raise SystemExit("Use the native LaTeX editor or an already installed pdflatex.")
    source = root / "paper/manuscript.tex"
    output = root / ".cache/paper/tex"
    output.mkdir(parents=True, exist_ok=True)
    command = [
        compiler,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output}",
        str(source),
    ]
    for index in range(1, 4):
        result = subprocess.run(
            command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        (output.parent / f"compile-pass{index}.log").write_text(
            result.stdout + result.stderr, encoding="utf-8"
        )
        if result.returncode:
            raise SystemExit(f"Compilation failed; inspect .cache/paper/compile-pass{index}.log")
    log = (output / "manuscript.log").read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?:Citation|Reference).*undefined|There were undefined", log):
        raise SystemExit("Resolve manuscript citation/reference diagnostics before export.")
    generated = output / "manuscript.pdf"
    if not generated.is_file() or generated.stat().st_size < 10000:
        raise SystemExit("The compiler did not produce a plausible complete PDF.")
    shutil.copyfile(generated, root / "paper/manuscript.pdf")
    print("Exported paper/manuscript.pdf from the standalone acmart source.")


if __name__ == "__main__":
    main()
