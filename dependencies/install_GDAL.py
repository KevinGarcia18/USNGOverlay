import platform
import os
import subprocess

ver = platform.architecture()[0]

if(ver == '32bit'):
    subprocess.call("pip install GDAL-2.2.4-cp36-cp36m-win32.whl")
else:
    subprocess.call("pip install GDAL-2.2.4-cp36-cp36m-win_amd64.whl")


