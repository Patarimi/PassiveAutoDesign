from glob import glob

def test_examples():
    exmple = glob("../examples/*.py")
    for file in exmple:
        execfile(file)
        print(file)
