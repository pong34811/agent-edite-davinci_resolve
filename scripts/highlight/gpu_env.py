"""Make pip-installed CUDA DLLs (nvidia-cublas-cu12, nvidia-cudnn-cu12) visible to CTranslate2 on Windows."""
import os, pathlib, site, sys
def setup():
    roots=[pathlib.Path(p) for p in site.getsitepackages()]+[pathlib.Path(sys.prefix)/"Lib"/"site-packages"]
    dirs=[b for r in roots for b in (r/"nvidia").glob("*/bin")]
    dirs+=[r/"torch"/"lib" for r in roots if (r/"torch"/"lib"/"cublas64_12.dll").exists()]  # CUDA torch wheels ship cuBLAS/cuDNN too
    for b in dirs:
        os.add_dll_directory(str(b)); os.environ["PATH"]=str(b)+os.pathsep+os.environ["PATH"]
