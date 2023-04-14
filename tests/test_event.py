from utils.event import Event


def test_event():
    a = Event[str]()
    s_l = []

    def add(s: str):
        s_l.append(s)

    a += add
    a.invoke("1")
    assert s_l[0] == "1"
    a -= add
    a.invoke("2")
    assert len(s_l) == 1
