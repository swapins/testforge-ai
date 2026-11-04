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
    assert payload['test_cases'][0]['scenario_type'] == 'positive'
    assert payload['test_cases'][0]['review_status'] == 'draft'
    assert payload['test_cases'][0]['objective']
    assert payload['test_cases'][0]['acceptance_criteria'] == []
    assert {case['scenario_type'] for case in payload['test_cases']} == {
        'positive', 'negative', 'boundary', 'business-rule'
    }


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
    assert result.test_cases[0].review_status == 'draft'


def test_acceptance_criteria_are_traced_to_generated_cases():
    response = client.post('/generate', json={
        'requirement_id': 'AUTH-002',
        'description': 'Users must receive a clear lockout message after failed logins.',
        'acceptance_criteria': [
            'The message is shown after the fifth failed attempt.',
            'The account cannot authenticate during the lockout period.',
        ],
    })
    assert response.status_code == 200
    case = response.json()['test_cases'][0]
    assert case['requirement_id'] == 'AUTH-002'
    assert case['acceptance_criteria'] == [
        'The message is shown after the fifth failed attempt.',
        'The account cannot authenticate during the lockout period.',
    ]
    assert case['assumptions']


def test_review_status_is_constrained_and_cases_are_never_executable():
    invalid = client.post('/generate', json={
        'requirement_id': 'AUTH-003',
        'description': 'Users must be able to sign out safely.',
        'review_status': 'approved',
    })
    assert invalid.status_code == 200
    payload = invalid.json()
    assert payload['test_cases'][0]['review_status'] == 'draft'
    assert payload['executable'] is False

    from app.schemas import TestCase
    try:
        TestCase(
            id='AUTH-003-TC001', requirement_id='AUTH-003', title='x',
            scenario_type='positive', objective='x', steps=['x'],
            expected_result='x', origin='deterministic-baseline',
            review_status='pending',
        )
    except Exception as error:
        assert 'review_status' in str(error)
    else:
        raise AssertionError('Unknown review states must be rejected.')


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
