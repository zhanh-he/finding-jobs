import unittest
from public_projection import public_projection


class PublicBoundary(unittest.TestCase):
    def test_candidate_fields_cannot_leak_through_projection(self):
        canonical = {'schema_version': '2.1', 'as_of': '2026-10-22', 'jobs': [{
            'id': 'one', 'record_type': 'vacancy', 'title': 'Job', 'official_url': 'https://example.com',
            'public_fact_eligible': True, 'candidate_evidence_refs': ['SECRET'], 'contacts': ['SECRET'],
            'visa': {'SECRET': True}, 'application_stage': 'interview', 'artifacts': [{'path': 'SECRET'}],
            'research_direction_fit': {'reason': 'SECRET'}, 'level_fit': {'reason': 'SECRET'},
            'key_gaps': ['SECRET'], 'requirement_evidence_matrix': ['SECRET'], 'application_history_refs': ['SECRET']}]}
        result = public_projection(canonical)
        self.assertNotIn('SECRET', str(result))
        self.assertEqual(result['jobs'][0]['application_stage'], 'unknown')
        self.assertEqual(result['jobs'][0]['artifacts'], [])

    def test_opt_in_never_includes_history_or_default_rows(self):
        data = {'schema_version': '2.1', 'as_of': '2026-10-22', 'jobs': [
            {'id': 'a', 'record_type': 'history', 'public_fact_eligible': True},
            {'id': 'b', 'record_type': 'vacancy'}]}
        self.assertEqual(public_projection(data)['jobs'], [])


if __name__ == '__main__':
    unittest.main()
