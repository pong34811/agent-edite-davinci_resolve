"""Make pip-installed CUDA DLLs (nvidia-cublas-cu12, nvidia-cudnn-cu12) visible to CTranslate2 on Windows."""
import os, pathlib, site, sys
def setup():
    roots=[pathlib.Path(p) for p in site.getsitepackages()]+[pathlib.Path(sys.prefix)/"Lib"/"site-packages"]
    for r in roots:
        for b in (r/"nvidia").glob("*/bin"):
            os.add_dll_directory(str(b)); os.environ["PATH"]=str(b)+os.pathsep+os.environ["PATH"]
