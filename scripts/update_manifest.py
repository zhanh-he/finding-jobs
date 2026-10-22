"""Refresh inspectable website file hashes after building (no deploy assertion)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'private/data/jobs.json').read_text())
files = sorted(p for folder in ('private', 'public-safe') for p in (ROOT / folder).rglob('*') if p.is_file())
manifest = {
    'schema_version': '2.1', 'updated_date': data['as_of'],
    'site_url': 'https://zhanh-he.github.io/finding-jobs/private/index.html?view=canva',
    'research_as_of': data['as_of'], 'records': len(data['jobs']),
    'specific_vacancies': data['counts']['record_types']['vacancy'],
    'retained_deep_packs': 4, 'new_deep_packs': 3,
    'published_material_artifacts': sum(len(j.get('artifacts') or []) for j in data['jobs']),
    'new_canva_materials_published': False, 'progress_storage': 'browser_local_only',
    'raw_mail_and_original_cv_sources_included': False,
    'deployment_evidence': 'GitHub Actions github-pages environment; a commit is not proof of deployment.',
    'files': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
}
(ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'manifest_files': len(files), 'records': len(data['jobs'])}))
