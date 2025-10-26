from spica.config import tau_task_for_domain


def test_tau_task_env_domain_override(monkeypatch):
    monkeypatch.setenv("SPICA_TAU_TASK", "0.08")
    monkeypatch.setenv("SPICA_TAU_TASK__QA_RAG", "0.12")
    assert abs(tau_task_for_domain("qa.rag") - 0.12) < 1e-9
    assert abs(tau_task_for_domain("other.domain") - 0.08) < 1e-9

