from tools.queue_runner import QueueRunner


def test_queue_runner_priority_and_results():
    order = []
    r = QueueRunner()

    def j(name):
        return lambda: order.append(name)

    r.submit("low", j("low"), priority=1)
    r.submit("high", j("high"), priority=10)
    r.run(budget_s=5.0)

    # higher priority should execute first
    assert order == ["high", "low"]
    assert r.completed == ["high", "low"]
    assert r.failed == []

