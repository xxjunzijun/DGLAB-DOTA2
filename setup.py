import os
abspath = os.path.dirname(os.path.abspath(__file__))
testPath = os.path.join(abspath, "requirements.txt")

os.system(f"pip install -r {testPath}")
input("press any key to exit...")
