import glob

def test_examples():
    exmple = glob.glob(".\examples\*.py")
    i=0
    for file in exmple:
        print(file)
        with open(file, 'r') as f:
            exec(f.read())
        i+=1
    assert i == 5
