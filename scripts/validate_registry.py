#!/usr/bin/env python3
"""Validate the canonical registry and file contracts using only Python stdlib.

The JSON Schema uses a deliberately small, executed subset of draft 2020-12.
Semantic checks cover constraints that JSON Schema alone cannot express: source
foreign keys, inactive API results, aliases, weighted nulls and immutable files.
This command reads files; --report is the only optional output mutation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = {'research': 20, 'technical': 20, 'academic': 10, 'engineering': 10,
           'location_lifestyle': 25, 'salary_development': 10, 'interview_competitiveness': 5}
CAREER = ('research', 'technical', 'academic', 'engineering')
ROUNDING_TOLERANCE = 0.11  # Preserved Cambridge 82.1 versus 82.1429 is intentional.


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def schema_errors(value, schema, document=None, path='$'):
    """Execute all schema keywords used in jobs.schema.json, without a dependency."""
    document = document or schema
    errors = []
    if '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/'):
            return [f'{path}: unsupported external schema reference {ref}']
        target = document
        for key in ref[2:].split('/'):
            target = target[key.replace('~1', '/').replace('~0', '~')]
        return schema_errors(value, target, document, path)
    types = schema.get('type', [])
    types = [types] if isinstance(types, str) else types
    predicates = {
        'null': lambda v: v is None, 'object': lambda v: isinstance(v, dict),
        'array': lambda v: isinstance(v, list), 'string': lambda v: isinstance(v, str),
        'boolean': lambda v: isinstance(v, bool), 'number': is_number,
        'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
    }
    if types and not any(predicates[t](value) for t in types):
        return [f'{path}: expected {" or ".join(types)}, got {type(value).__name__}']
    if 'const' in schema and value != schema['const']:
        errors.append(f'{path}: expected constant {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: value is outside permitted enum')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{path}.{key}: required field missing')
        properties = schema.get('properties', {})
        for key, item in value.items():
            if key in properties:
                errors += schema_errors(item, properties[key], document, f'{path}.{key}')
            elif schema.get('additionalProperties') is False:
                errors.append(f'{path}.{key}: unrecognized field')
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{path}: too few array items')
        if schema.get('uniqueItems'):
            serialized = [json.dumps(v, sort_keys=True, ensure_ascii=False) for v in value]
            if len(set(serialized)) != len(serialized):
                errors.append(f'{path}: duplicate array item')
        for i, item in enumerate(value):
            if 'items' in schema:
                errors += schema_errors(item, schema['items'], document, f'{path}[{i}]')
    elif isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            errors.append(f'{path}: string is too short')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            errors.append(f'{path}: string does not match required pattern')
    elif is_number(value):
        if value < schema.get('minimum', -math.inf) or value > schema.get('maximum', math.inf):
            errors.append(f'{path}: number outside permitted range')
    return errors


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def local_target(root, value):
    if not isinstance(value, str) or not value or '\\' in value or urlparse(value).scheme:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts:
        return None
    target = (root / value).resolve()
    return target if target.is_relative_to(root.resolve()) else None


def identifier(value):
    value = str(value).strip().lower().rstrip('/')
    posting = re.search(r'(?<!\d)(6000000\d{9})(?!\d)', value)
    return 'canva-posting:' + posting.group(1) if posting else value


def validate_payload(payload, root=ROOT, *, schema=None, check_files=True, preserve_baseline=True):
    root = Path(root)
    if schema is None:
        schema = json.loads((root / 'private/data/jobs.schema.json').read_text())
    errors = schema_errors(payload, schema)
    warnings = []
    jobs = payload.get('jobs', []) if isinstance(payload, dict) else []
    sources = payload.get('sources', []) if isinstance(payload, dict) else []
    if not isinstance(jobs, list) or not isinstance(sources, list):
        return {'status': 'failed', 'errors': errors, 'warnings': warnings}
    ids = [j.get('id') for j in jobs if isinstance(j, dict)]
    if len(set(ids)) != len(ids):
        errors.append('jobs: duplicate canonical ID')
    source_ids = [s.get('id') for s in sources if isinstance(s, dict)]
    if len(set(source_ids)) != len(source_ids):
        errors.append('sources: duplicate source ID')
    known_sources = set(source_ids)
    source_lookup = {source.get('id'): source for source in sources if isinstance(source, dict)}
    if preserve_baseline:
        missing = set(schema.get('x-preserved-record-ids', [])) - set(ids)
        if missing:
            errors.append('jobs: preserved baseline IDs missing: ' + ', '.join(sorted(missing)))

    def references(value, label):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'source_ids' and isinstance(item, list):
                    for sid in item:
                        if sid not in known_sources:
                            errors.append(f'{label}.source_ids: unregistered source {sid!r}')
                references(item, label + '.' + key)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                references(item, f'{label}[{i}]')

    ownership = {}
    watch_families = {}
    artifact_count = 0
    hashed_artifacts = 0

    def claim(value, owner):
        key = identifier(value)
        previous = ownership.get(key)
        if previous is not None and previous != owner:
            errors.append(f'{owner}: alias/posting {value!r} also belongs to {previous}')
        ownership[key] = owner

    def close(actual, expected, label, *, allow_absent=False):
        if allow_absent and actual is None:
            return
        if expected is None:
            if actual is not None:
                errors.append(f'{label}: unknown aggregate must remain null')
        elif not is_number(actual) or abs(actual - expected) > ROUNDING_TOLERANCE:
            errors.append(f'{label}: expected {expected:.6f}, got {actual!r}')

    for job in jobs:
        if not isinstance(job, dict):
            continue
        jid = str(job.get('id', '<missing>'))
        references(job, jid)
        claim(jid, jid)
        for alias in job.get('aliases') or []:
            claim(alias, jid)
        is_canva = str(job.get('organization', '')).lower() == 'canva'
        if is_canva:
            for field in ('official_url', 'information_url'):
                url = job.get(field)
                if url and re.search(r'(?<!\d)6000000\d{9}(?!\d)', url):
                    claim(url, jid)
            for field in ('seniority_level', 'research_direction_fit', 'level_fit', 'application_action', 'key_gaps', 'api_active', 'aliases'):
                if field not in job:
                    errors.append(f'{jid}: Canva field {field} is missing')
            if job.get('record_type') == 'vacancy' and not isinstance(job.get('api_active'), bool):
                errors.append(f'{jid}: formal Canva vacancy needs explicit API active boolean')
            official_requirements = job.get('requirements_official')
            if not isinstance(official_requirements, list):
                errors.append(f'{jid}: Canva requirements_official must be an explicit list')
            else:
                for field, category in [('essential_requirements', 'core_expectation'), ('preferred_requirements', 'preferred')]:
                    expected = [item.get('requirement') for item in official_requirements if isinstance(item, dict) and item.get('category') == category]
                    actual = job.get(field)
                    if not isinstance(actual, list) or Counter(actual) != Counter(expected):
                        errors.append(f'{jid}: {field} must correspond exactly to requirements_official category {category}')
                for item in official_requirements:
                    if isinstance(item, dict) and item.get('source_id') not in known_sources:
                        errors.append(f'{jid}: official requirement has unregistered source {item.get("source_id")!r}')
            user_evidence_kinds = {'direct_user_confirmation', 'user_confirmed_application', 'application_receipt'}
            application_refs = list(job.get('source_ids') or []) + list(job.get('application_history_refs') or [])
            stage_evidence = job.get('application_stage_evidence')
            if isinstance(stage_evidence, str):
                application_refs.append(stage_evidence)
            elif isinstance(stage_evidence, list):
                application_refs.extend(stage_evidence)
            elif isinstance(stage_evidence, dict):
                application_refs.extend(stage_evidence.get('source_ids') or [])
                if stage_evidence.get('source_id'):
                    application_refs.append(stage_evidence['source_id'])
            for event in job.get('application_events') or []:
                if isinstance(event, dict) and event.get('source_id'):
                    application_refs.append(event['source_id'])
            has_user_evidence = any(isinstance(ref, str) and source_lookup.get(ref, {}).get('kind') in user_evidence_kinds for ref in application_refs)
            if job.get('application_stage') not in ('unknown', 'not_applied_unconfirmed') and not has_user_evidence:
                errors.append(f'{jid}: Canva application stage needs registered user evidence; no record does not prove not_applied')
            if job.get('record_type') == 'watch':
                title = re.sub(r'\b(london|sydney)\b', '', str(job.get('title', '')).lower())
                family = re.sub(r'[^\w]+', '', title)
                if family in watch_families and not job.get('distinct_role_rationale'):
                    errors.append(f'{jid}: city mirror repeats watch family {watch_families[family]}')
                watch_families[family] = jid
        if job.get('api_active') is False and (job.get('vacancy_status') == 'open' or job.get('verified_open') is True):
            errors.append(f'{jid}: API inactive cannot be open or verified open')
        if job.get('verified_open') is True and (job.get('record_type') != 'vacancy' or job.get('vacancy_status') != 'open'):
            errors.append(f'{jid}: verified open requires an open vacancy record')
        if job.get('draft_material_status') == 'local_draft_not_published' and job.get('artifacts'):
            errors.append(f'{jid}: local unpublished draft cannot have published artifact links')
        if is_canva and job.get('draft_material_status') == 'local_draft_not_published' and job.get('artifacts') != []:
            errors.append(f'{jid}: Canva local draft artifacts must be []')

        current = job.get('active_recommendation') or {}
        grade = current.get('grade')
        label = current.get('label')
        if grade in ('A', 'B', 'C', 'D'):
            label_grade = re.match(r'^\s*([A-D])(?:\b|[（(])', str(label or ''))
            if label_grade and label_grade.group(1) != grade:
                errors.append(f'{jid}: recommendation grade and label disagree')
            if job.get('recommendation') not in (None, grade):
                errors.append(f'{jid}: recommendation fields disagree')

        scores = job.get('scores') or {}
        known_weight = weighted = career_weight = career_weighted = 0
        valid_scores = isinstance(scores, dict)
        for key, expected_weight in WEIGHTS.items():
            value = scores.get(key) if isinstance(scores, dict) else None
            if not isinstance(value, dict):
                valid_scores = False
                continue
            if value.get('weight') != expected_weight:
                errors.append(f'{jid}.scores.{key}: wrong dimension weight')
            number = value.get('value')
            if number is None:
                if not value.get('unknown_reason'):
                    warnings.append(f'{jid}.scores.{key}: null score has no specific unknown_reason')
            elif is_number(number):
                if value.get('unknown_reason'):
                    errors.append(f'{jid}.scores.{key}: numeric score contradicts unknown_reason')
                known_weight += expected_weight
                weighted += expected_weight * number
                if key in CAREER:
                    career_weight += expected_weight
                    career_weighted += expected_weight * number
            else:
                valid_scores = False
            for sid in value.get('evidence') or []:
                if sid not in known_sources:
                    errors.append(f'{jid}.scores.{key}: unregistered source {sid!r}')
        if valid_scores:
            close(job.get('known_weight'), known_weight, jid + '.known_weight')
            close(job.get('coverage_pct'), known_weight, jid + '.coverage_pct')
            overall = weighted / known_weight if known_weight else None
            close(job.get('provisional_overall'), overall, jid + '.provisional_overall')
            close(job.get('computed_provisional_overall'), overall, jid + '.computed_provisional_overall', allow_absent=True)
            close(job.get('career_fit_score'), career_weighted / career_weight if career_weight else None, jid + '.career_fit_score')
            close(job.get('career_fit_coverage_pct'), career_weight / 60 * 100, jid + '.career_fit_coverage_pct')

        for artifact in job.get('artifacts') or []:
            if not isinstance(artifact, dict):
                continue
            artifact_count += 1
            path = artifact.get('path')
            if re.search(r'application_form|chris6', PurePosixPath(path or '').name, re.I):
                errors.append(f'{jid}: application form must not be a website artifact')
            target = local_target(root / 'private', path)
            if target is None:
                errors.append(f'{jid}: unsafe artifact path {path!r}')
            elif check_files:
                if not target.is_file() or target.stat().st_size == 0:
                    errors.append(f'{jid}: artifact missing or empty: {path}')
                elif artifact.get('sha256'):
                    hashed_artifacts += 1
                    if sha256(target) != artifact['sha256'].lower():
                        errors.append(f'{jid}: artifact SHA256 mismatch: {path}')
            if check_files and target is not None and target.is_file() and artifact.get('bytes') is not None and target.stat().st_size != artifact['bytes']:
                errors.append(f'{jid}: artifact byte count mismatch: {path}')

    archive_count = 0
    if check_files:
        manifest_path = root / 'docs/submitted_archive_integrity.json'
        if not manifest_path.is_file():
            errors.append('submitted archive integrity manifest missing')
        else:
            manifest = json.loads(manifest_path.read_text())
            archives = manifest.get('files', [])
            if len(archives) != 2:
                errors.append('submitted archive manifest must identify both original DOCX/PDF files')
            archive_paths = [entry.get('path', '') for entry in archives]
            if len(set(archive_paths)) != len(archive_paths) or {Path(path).suffix.lower() for path in archive_paths} != {'.docx', '.pdf'}:
                errors.append('submitted archive manifest needs distinct DOCX and PDF originals')
            for entry in archives:
                path = entry.get('path', '')
                target = local_target(root, path)
                if not path.startswith('formal_doc/Submitted_CVResume/') or target is None:
                    errors.append('submitted archive path is outside immutable archive')
                elif not target.is_file():
                    errors.append('submitted archive missing: ' + path)
                elif sha256(target) != entry.get('sha256'):
                    errors.append('submitted archive SHA256 mismatch: ' + path)
                else:
                    archive_count += 1

    record_types = dict(Counter(j.get('record_type') for j in jobs if isinstance(j, dict)))
    vacancy_status = {key: sum(j.get('record_type') == 'vacancy' and j.get('vacancy_status') == key for j in jobs if isinstance(j, dict)) for key in ('open', 'closed', 'unknown', 'upcoming')}
    verified_open = sum(j.get('verified_open') is True for j in jobs if isinstance(j, dict))
    counts = payload.get('counts') or {}
    for key, expected in [('total_records', len(jobs)), ('record_types', record_types), ('vacancy_status', vacancy_status), ('verified_open', verified_open)]:
        if key in counts and counts[key] != expected:
            errors.append(f'counts.{key}: disagrees with canonical jobs')
    return {'status': 'passed' if not errors else 'failed', 'records': len(jobs), 'record_types': record_types,
            'vacancy_status': vacancy_status, 'verified_open': verified_open, 'sources': len(sources),
            'artifact_references': artifact_count, 'hashed_artifacts_checked': hashed_artifacts,
            'submitted_originals_checked': archive_count, 'errors': errors, 'warnings': warnings,
            'limitations': ['Vacancy status remains a source-backed snapshot, not an HTTP response inference.',
                            'Existing rounds may omit computed_provisional_overall; when present it is checked.',
                            'Legacy one-decimal scores use an absolute rounding tolerance of 0.11.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'private/data/jobs.json')
    parser.add_argument('--schema', type=Path, default=ROOT / 'private/data/jobs.schema.json')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--skip-files', action='store_true', help='For data-only inspection; full CI must not use this flag.')
    args = parser.parse_args()
    try:
        payload = json.loads(args.data.read_text())
        schema = json.loads(args.schema.read_text())
        result = validate_payload(payload, schema=schema, check_files=not args.skip_files)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {'status': 'failed', 'errors': [str(error)], 'warnings': []}
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output)
    print(output, end='')
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
