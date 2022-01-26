import glob


def test_examples():
    example = glob.glob("./apps/example*.py")
    i = 0
    for file in example:
        print(file)
        with open(file, "r") as f:
            exec(f.read(), globals())
        i += 1
    assert i == 6
