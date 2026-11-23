"""Sposta una singola voce di diario nel commit di integrazione."""

import argparse
import os
from pathlib import Path
import re
import tempfile


def consolida(root: Path, branch: str) -> bool:
    """Restituisce False se il frammento è già assente."""
    if not all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", part)
               for part in branch.split("/")):
        raise ValueError("Nome del ramo non valido")

    docs = root / "docs"
    diario = docs / "diario"
    frammento = diario / f"{branch}.md"
    if diario.resolve() not in frammento.resolve().parents or frammento.is_symlink():
        raise ValueError("Il frammento deve essere un file sotto docs/diario")
    try:
        righe = frammento.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return False
    if (not 1 <= len(righe) <= 8
            or not re.fullmatch(r"## .+ — .+", righe[0])
            or any(riga.startswith(("# ", "## ")) for riga in righe[1:])):
        raise ValueError("Il frammento deve avere una sola voce di massimo 8 righe")

    stato = docs / "stato-progetto.md"
    titolo, _, voci = stato.read_text(encoding="utf-8").partition("\n")
    if not titolo.startswith("# "):
        raise ValueError("Titolo del diario mancante")
    voce = "\n".join(righe).rstrip()
    esistenti = voci.lstrip("\n")
    # Un nuovo tentativo dopo la sostituzione del diario non duplica la voce.
    if not (esistenti.rstrip() == voce or esistenti.startswith(voce + "\n\n")):
        nuovo = f"{titolo}\n\n{voce}\n"
        if esistenti:
            nuovo += "\n" + esistenti
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=docs, delete=False
        ) as file:
            temporaneo = Path(file.name)
            try:
                file.write(nuovo)
                file.close()
                temporaneo.chmod(stato.stat().st_mode & 0o777)
                os.replace(temporaneo, stato)
            finally:
                temporaneo.unlink(missing_ok=True)
    frammento.unlink()
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("branch", help="Nome completo del ramo della PR")
    args = parser.parse_args()
    try:
        spostato = consolida(Path(__file__).resolve().parents[1], args.branch)
    except (ValueError, OSError) as errore:
        parser.exit(1, f"{errore}\n")
    if not spostato:
        parser.exit(1, "Frammento assente: controllare il nome del ramo o il diario già consolidato.\n")


if __name__ == "__main__":
    main()
