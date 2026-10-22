#!/usr/bin/env python3
"""Regression tests for source-backed state, null scores and preserved files."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from validate_registry import ROOT, WEIGHTS, validate_payload

SCHEMA = json.loads((ROOT / 'private/data/jobs.schema.json').read_text())


def fixture_job(jid='example', organization='Example'):
    scores = {key: {'value': None, 'weight': weight, 'evidence': ['source'], 'unknown_reason': 'Not evidenced'} for key, weight in WEIGHTS.items()}
    for key in ('research', 'academic'):
        scores[key].update(value=80, unknown_reason=None)
    return {
        'id': jid, 'record_type': 'vacancy', 'organization': organization, 'title': 'Audio researcher',
        'source_ids': ['source'], 'vacancy_status': 'open', 'verified_open': True,
        'public_fact_eligible': True, 'api_active': True if organization == 'Canva' else None,
        'aliases': [], 'artifacts': [], 'scores': scores, 'known_weight': 30, 'coverage_pct': 30,
        'provisional_overall': 80, 'career_fit_score': 80, 'career_fit_coverage_pct': 50,
        'seniority_level': 'Principal',
        'research_direction_fit': {'level': 'high', 'label': '方向较强', 'reason': 'Evidence'},
        'level_fit': {'level': 'low', 'label': '职级跨度', 'reason': 'Missing leadership'},
        'application_action': {'category': 'stretch', 'label': '低优先级冲刺', 'reason': 'Level gap'},
        'key_gaps': ['Leadership'], 'active_recommendation': {'grade': 'C', 'label': 'C — conditional'},
        'recommendation': 'C',
        'application_stage': 'unknown', 'requirements_official': [],
        'essential_requirements': [], 'preferred_requirements': [],
    }


def fixture_payload(jobs=None):
    return {'schema_version': '2.1', 'as_of': '2026-10-22', 'weights': copy.deepcopy(WEIGHTS),
            'sources': [{'id': 'source', 'title': 'Official employer'}], 'jobs': jobs or [fixture_job()]}


class RegistryDataContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = fixture_payload()
        self.archive_paths = []
        entries = []
        for suffix in ('docx', 'pdf'):
            relative = 'formal_doc/Submitted_CVResume/confirmed/resume.' + suffix
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(('immutable ' + suffix).encode())
            self.archive_paths.append(path)
            entries.append({'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        manifest = self.root / 'docs/submitted_archive_integrity.json'
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({'files': entries}))

    def tearDown(self):
        self.temp.cleanup()

    def validate(self, payload=None, *, files=False, baseline=False):
        return validate_payload(payload or self.payload, self.root, schema=SCHEMA, check_files=files, preserve_baseline=baseline)

    def assert_error(self, fragment, payload=None, **kwargs):
        result = self.validate(payload, **kwargs)
        self.assertEqual('failed', result['status'])
        self.assertTrue(any(fragment in error for error in result['errors']), result['errors'])

    def test_current_repository_canonical_and_files(self):
        result = validate_payload(json.loads((ROOT / 'private/data/jobs.json').read_text()), ROOT, schema=SCHEMA)
        self.assertEqual('passed', result['status'], result['errors'])
        self.assertEqual(2, result['submitted_originals_checked'])
        self.assertGreaterEqual(result['hashed_artifacts_checked'], 1)

    def test_valid_mixed_known_unknown_fixture(self):
        self.assertEqual('passed', self.validate(files=True)['status'])

    def test_schema_version_enforced(self):
        self.payload['schema_version'] = '2.0'
        self.assert_error('constant')

    def test_preserved_baseline_cannot_disappear(self):
        self.assert_error('preserved baseline IDs missing', baseline=True)

    def test_duplicate_canonical_id_rejected(self):
        self.payload['jobs'].append(copy.deepcopy(self.payload['jobs'][0]))
        self.assert_error('duplicate canonical ID')

    def test_unknown_source_reference_rejected(self):
        self.payload['jobs'][0]['source_ids'] = ['unregistered']
        self.assert_error('unregistered source')

    def test_nested_matrix_source_reference_rejected(self):
        self.payload['jobs'][0]['requirement_evidence_matrix'] = [{'source_ids': ['unregistered']}]
        self.assert_error('unregistered source')

    def test_api_inactive_is_not_open(self):
        self.payload['jobs'][0]['api_active'] = False
        self.assert_error('API inactive cannot be open')

    def test_canva_preferred_is_not_promoted_to_essential(self):
        job = fixture_job('canva-a', 'Canva')
        job['requirements_official'] = [
            {'id': 'Q01', 'category': 'core_expectation', 'requirement': 'Research experience', 'source_id': 'source'},
            {'id': 'N01', 'category': 'preferred', 'requirement': 'HCI background', 'source_id': 'source'},
        ]
        job['essential_requirements'] = ['Research experience', 'HCI background']
        self.assert_error('essential_requirements must correspond exactly', fixture_payload([job]))
        job['essential_requirements'] = ['Research experience']
        job['preferred_requirements'] = ['HCI background']
        self.assertEqual('passed', self.validate(fixture_payload([job]))['status'])

    def test_canva_no_record_is_not_proof_of_not_applied(self):
        job = fixture_job('canva-a', 'Canva')
        job['application_stage'] = 'not_applied'
        self.assert_error('application stage needs registered user evidence', fixture_payload([job]))
        job['application_stage'] = 'applied'
        self.assert_error('application stage needs registered user evidence', fixture_payload([job]))

    def test_canva_confirmed_application_requires_registered_user_source(self):
        job = fixture_job('canva-a', 'Canva')
        job.update(application_stage='applied', application_stage_evidence={'source_id': 'confirmed-application'})
        payload = fixture_payload([job])
        payload['sources'].append({'id': 'confirmed-application', 'kind': 'direct_user_confirmation'})
        self.assertEqual('passed', self.validate(payload)['status'])

    def test_canva_unknown_and_unconfirmed_are_preserved(self):
        job = fixture_job('canva-a', 'Canva')
        for stage in ('unknown', 'not_applied_unconfirmed'):
            job['application_stage'] = stage
            self.assertEqual('passed', self.validate(fixture_payload([job]))['status'])

    def test_watch_cannot_be_verified_open(self):
        self.payload['jobs'][0]['record_type'] = 'watch'
        self.assert_error('verified open requires an open vacancy')

    def test_duplicate_alias_between_records_rejected(self):
        one, two = fixture_job('a', 'Canva'), fixture_job('b', 'Canva')
        one['aliases'] = ['6000000001354300']
        two['aliases'] = ['https://jobs.smartrecruiters.com/Canva/6000000001354300-another-city/']
        self.assert_error('also belongs to', fixture_payload([one, two]))

    def test_alias_cannot_steal_another_canonical_id(self):
        one, two = fixture_job('a'), fixture_job('b')
        two['aliases'] = ['a']
        self.assert_error('also belongs to', fixture_payload([one, two]))

    def test_city_watch_mirrors_are_one_family(self):
        one, two = fixture_job('a', 'Canva'), fixture_job('b', 'Canva')
        for job, city in ((one, 'London'), (two, 'Sydney')):
            job.update(record_type='watch', vacancy_status='unknown', verified_open=False, api_active=None,
                       title='Research Engineer - Evaluations (' + city + ')')
        self.assert_error('city mirror repeats watch family', fixture_payload([one, two]))

    def test_unpublished_draft_cannot_be_downloadable(self):
        self.payload['jobs'][0].update(draft_material_status='local_draft_not_published', artifacts=[{'path': 'new_resume.pdf', 'type': 'resume', 'status': 'draft'}])
        self.assert_error('local unpublished draft cannot have published artifact links')

    def test_bad_artifact_hash_rejected(self):
        path = self.root / 'private/files/resume.txt'
        path.parent.mkdir(parents=True)
        path.write_text('real generated file')
        self.payload['jobs'][0]['artifacts'] = [{'path': 'files/resume.txt', 'type': 'resume', 'status': 'draft', 'sha256': '0' * 64}]
        self.assert_error('artifact SHA256 mismatch', files=True)

    def test_artifact_path_traversal_rejected(self):
        self.payload['jobs'][0]['artifacts'] = [{'path': '../outside.txt', 'type': 'resume', 'status': 'draft'}]
        self.assert_error('unsafe artifact path')

    def test_application_form_is_not_added_as_download(self):
        self.payload['jobs'][0]['artifacts'] = [{'path': 'application_form_CHRIS6.pdf', 'type': 'form', 'status': 'ready'}]
        self.assert_error('application form must not be a website artifact')

    def test_changed_submitted_archive_rejected(self):
        self.archive_paths[0].write_bytes(b'silently edited')
        self.assert_error('submitted archive SHA256 mismatch', files=True)

    def test_submitted_manifest_cannot_repeat_one_original(self):
        path = self.root / 'docs/submitted_archive_integrity.json'
        manifest = json.loads(path.read_text())
        manifest['files'][1] = copy.deepcopy(manifest['files'][0])
        path.write_text(json.dumps(manifest))
        self.assert_error('distinct DOCX and PDF originals', files=True)

    def test_zero_is_not_a_substitute_for_unknown_aggregate(self):
        job = self.payload['jobs'][0]
        for score in job['scores'].values():
            score.update(value=None, unknown_reason='Not evidenced')
        job.update(known_weight=0, coverage_pct=0, provisional_overall=0, career_fit_score=None, career_fit_coverage_pct=0)
        self.assert_error('unknown aggregate must remain null')

    def test_wrong_weighted_value_rejected(self):
        self.payload['jobs'][0]['provisional_overall'] = 90
        self.assert_error('provisional_overall: expected')

    def test_legacy_rounding_tolerance_is_bounded(self):
        self.payload['jobs'][0]['provisional_overall'] = 79.9
        self.assertEqual('passed', self.validate()['status'])
        self.payload['jobs'][0]['provisional_overall'] = 79.8
        self.assert_error('provisional_overall: expected')

    def test_numeric_score_cannot_claim_unknown(self):
        self.payload['jobs'][0]['scores']['research']['unknown_reason'] = 'Unknown; no midpoint'
        self.assert_error('numeric score contradicts unknown_reason')

    def test_boolean_is_not_a_numeric_score(self):
        self.payload['jobs'][0]['scores']['research']['value'] = True
        self.assert_error('expected number or null')

    def test_grade_and_label_must_agree(self):
        self.payload['jobs'][0]['active_recommendation']['label'] = 'B'
        self.assert_error('recommendation grade and label disagree')

    def test_country_history_unknown_remains_null(self):
        job = self.payload['jobs'][0]
        job.update(record_type='history', organization=None, vacancy_status='unknown', verified_open=False)
        self.assertEqual('passed', self.validate()['status'])

    def test_counts_are_derived_from_same_records(self):
        self.payload['counts'] = {'total_records': 103}
        self.assert_error('counts.total_records')


if __name__ == '__main__':
    unittest.main(verbosity=2)
