import os

os.chdir( os.fspath("src/overlay") )
os.system( "py -3 Main.py" )