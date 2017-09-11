def hello(i):
    i +=1
    return i

def test_hello():
    assert hello(2) == 3