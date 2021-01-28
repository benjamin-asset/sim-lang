import executor


def test_execute():
    executor.execute('print(1 + 2)', 1, 2, 3)
    assert True

