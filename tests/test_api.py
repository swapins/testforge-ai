import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.generators import GenerationError, HuggingFaceGenerator
from app.schemas import Requirement

client = TestClient(app)


def test_health():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['mode'] == 'draft-only'


def test_submit_requirement():
    response = client.post('/requirements', json={
        'requirement_id': 'AUTH-001',
        'description': 'Users must be temporarily locked after five failed logins.'
    })
    assert response.status_code == 201
    assert response.json()['status'] == 'received'
    assert response.json()['requirement']['requirement_id'] == 'AUTH-001'


def test_generate_is_review_first():
    res = client.post('/generate', json={
        'requirement_id': 'AUTH-001',
        'description': 'Users must be temporarily locked after five failed logins.'
    })
    assert res.status_code == 200
    payload = res.json()
    assert payload['executable'] is False
    assert payload['generation_mode'] == 'deterministic-baseline'
    assert payload['test_cases'][0]['review_required'] is True
    assert payload['test_cases'][0]['origin'] == 'deterministic-baseline'
    assert payload['test_cases'][0]['requirement_id'] == 'AUTH-001'


def test_rejects_empty_requirement():
    assert client.post('/generate', json={'requirement_id': 'X', 'description': 'short'}).status_code == 422


def test_huggingface_requires_model_id(monkeypatch):
    monkeypatch.setenv('TESTFORGE_GENERATOR', 'huggingface')
    monkeypatch.delenv('TESTFORGE_MODEL_ID', raising=False)
    response = client.post('/generate', json={
        'requirement_id': 'AUTH-001',
        'description': 'Users must be temporarily locked after five failed logins.'
    })
    assert response.status_code == 502
    assert 'TESTFORGE_MODEL_ID' in response.json()['detail']


def test_huggingface_output_remains_review_required(monkeypatch):
    class FakeInferenceClient:
        def __init__(self, **_kwargs):
            pass

        def text_generation(self, *_args, **_kwargs):
            return (
                '{"test_cases":[{"title":"Check lockout",'
                '"steps":["Enter an invalid password"],'
                '"expected_result":"The account is locked"}]}'
            )

    monkeypatch.setitem(
        sys.modules,
        'huggingface_hub',
        SimpleNamespace(InferenceClient=FakeInferenceClient),
    )
    result = HuggingFaceGenerator('test-model').generate(Requirement(
        requirement_id='AUTH-001',
        description='Users must be locked after five failed login attempts.',
    ))
    assert result.executable is False
    assert result.test_cases[0].review_required is True
    assert result.test_cases[0].origin == 'huggingface-inference'


def test_huggingface_rejects_malformed_output(monkeypatch):
    class FakeInferenceClient:
        def __init__(self, **_kwargs):
            pass

        def text_generation(self, *_args, **_kwargs):
            return 'not a JSON draft'

    monkeypatch.setitem(
        sys.modules,
        'huggingface_hub',
        SimpleNamespace(InferenceClient=FakeInferenceClient),
    )
    requirement = Requirement(
        requirement_id='AUTH-001',
        description='Users must be locked after five failed login attempts.',
    )
    try:
        HuggingFaceGenerator('test-model').generate(requirement)
    except GenerationError as error:
        assert 'does not match the draft schema' in str(error)
    else:
        raise AssertionError('Malformed model output should not be accepted.')
