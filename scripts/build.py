"""Validate and produce a portable, dependency-free static site."""
import shutil
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.pipeline import read,validate_catalog
root=Path(__file__).resolve().parents[1]
validate_catalog(read(root/'data/catalog.json',{}))
dist=root/'dist'
if dist.exists():shutil.rmtree(dist)
shutil.copytree(root/'src',dist)
shutil.copytree(root/'data',dist/'data',ignore=shutil.ignore_patterns('evaluation.json','language-evaluation.json','*.tmp','.staging'))
(dist/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n  Content-Security-Policy: default-src \'self\'; script-src \'self\'; style-src \'self\'; img-src \'self\' data:; connect-src \'self\'; object-src \'none\'; base-uri \'self\'; form-action \'none\'\n/data/*\n  Cache-Control: public, max-age=300, must-revalidate\n')
print('Built dist/ — static files, no runtime services required')
