"""Protect public assets and contract after directory migration."""
import json
from pathlib import Path
from .test_api import client


def test_shared_data_and_static_paths(client):
    for url in ('/', '/ai-stream.js', '/assets/factory-hero.png', '/api/snapshot'):
        assert client.get(url).status_code == 200, url
    assert len(client.get('/api/snapshot').json()['orders']) == 120
    for url in ('/.env', '/backend/.env', '/app/main.py', '/data/orders.csv', '/data/raw/source.xlsx', '/data/dialogs.xlsx'):
        assert client.get(url).status_code == 404, url


def test_export_matches_runtime(client):
    schema = client.get('/openapi.json').json()
    assert schema['servers'][0]['url'] == 'http://127.0.0.1:8000'
    assert 'text/event-stream' in schema['paths']['/api/v1/workflow/chat/stream']['post']['responses']['200']['content']
    exported = Path(__file__).resolve().parents[2] / 'docs' / 'openapi.json'
    assert schema == json.loads(exported.read_text(encoding='utf-8'))


def test_every_deployment_ships_the_discovery_engine():
    """app/discovery.py imports simulation.briefing. The Docker image and the cloud-function ZIP must both carry it, and the
    engine must stay standard-library only so it needs no extra dependency in either."""
    import ast
    root = Path(__file__).resolve().parents[2]
    engine = ('__init__.py', 'briefing.py', 'prediction.py', 'workdays.py')
    assert 'COPY simulation/__init__.py simulation/briefing.py simulation/prediction.py simulation/workdays.py ./simulation/' in (root / 'Dockerfile').read_text()
    assert f"ENGINE = {engine!r}" in (root / 'deploy/cloud-function/package.py').read_text()
    allowed = {'__future__', 'argparse', 'csv', 'json', 'math', 'collections', 'datetime', 'pathlib', 'statistics'}
    for name in engine:
        tree = ast.parse((root / 'simulation' / name).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert {a.name.split('.')[0] for a in node.names} <= allowed, (name, ast.dump(node))
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module.split('.')[0] in allowed, (name, node.module)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in ('prediction', 'workdays'), (name, node.module)
