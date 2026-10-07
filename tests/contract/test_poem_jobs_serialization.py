from dataclasses import replace

import pytest
from pydantic import ValidationError

from application.ports.poem_jobs import PoemJob
from bootstrap.settings import PoemJobsConfig, Secrets, Settings
from contracts.poem import CanLamRo
from entrypoints.api.routers.poem_jobs import public_job


def test_default_job_config_is_validated_and_not_shared():
    first = Settings(secrets=Secrets(_env_file=None))
    second = Settings(secrets=Secrets(_env_file=None))
    assert first.poem_jobs == PoemJobsConfig.model_validate({})
    first.poem_jobs.active_limit = 5
    assert second.poem_jobs.active_limit == 2


def test_public_job_parses_stored_result_and_rejects_invalid_status():
    result = CanLamRo(ca=1, cau_hoi="What topic?", ly_do="Missing topic", trace_id="test")
    job = PoemJob(
        job_id="job-test",
        tenant_id="private-tenant",
        status="completed",
        created_at=1,
        updated_at=2,
        deadline=300,
        payload={"session_id": "conversation-test"},
        result=result.model_dump(mode="json"),
    )
    response = public_job(job)
    assert isinstance(response.result, CanLamRo)
    assert response.result == result
    assert response.conversation_id == "conversation-test"
    assert "tenant_id" not in response.model_dump()
    with pytest.raises(ValidationError):
        public_job(replace(job, status="invalid-status"))


def test_public_job_rejects_invalid_stored_result():
    job = PoemJob(
        job_id="job-test",
        tenant_id="tenant-test",
        status="completed",
        created_at=1,
        updated_at=2,
        deadline=300,
        payload={},
        result={"unrecognized": "result"},
    )
    with pytest.raises(ValidationError):
        public_job(job)
