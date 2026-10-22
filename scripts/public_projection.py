"""Explicit public-facts projection of the single canonical registry.

Do not add candidate fields here. Generated JSON/CSV are never independent inputs.
"""
from copy import deepcopy

PUBLIC_FIELDS = '''id record_type organization title team country city locations is_london
official_url information_url application_url application_channel application_instructions
channel_verified_at channel_checked_at channel_verification_status
posted_date deadline_original deadline_date deadline_time deadline_timezone deadline_iso
deadline_precision deadline_conflict planning_deadline vacancy_status verified_open
status_reason status_checked_at verified_at jd_completeness salary_min salary_max
salary_currency salary_period salary_gross_or_net salary_original salary_source_ids
contract_type contract_duration start_date hours remote_policy attendance_frequency
responsibilities essential_requirements preferred_requirements job_type direction
recruitment_channel ai_application_policy ai_policy_evidence seniority_level api_active
aliases related_closed_ids deduplication_note source_urls'''.split()


def public_projection(canonical):
    jobs, sources = [], []
    for row in canonical['jobs']:
        if not row.get('public_fact_eligible') or row['record_type'] == 'history':
            continue
        job = {k: deepcopy(row[k]) for k in PUBLIC_FIELDS if k in row}
        sid = 'public-' + row['id']
        job.update(source_ids=[sid], source_confidence={'level': 'high' if row.get('verified_open') else 'medium', 'reason': 'Public source and dated status; no candidate evidence.'},
                   application_stage='unknown', recommendation='Watchlist' if row['record_type'] == 'watch' else None,
                   active_recommendation=None, artifacts=[], deep_review_status='public_facts_only',
                   next_action='核对官方状态与地点；本视图不包含个人匹配或申请记录。')
        sources.append({'id': sid, 'title': row['title'], 'url': row.get('official_url'),
                        'verified_at': row.get('verified_at'), 'evidence': 'Public employer/conference source only; unknown activity remains unknown.',
                        'additional_urls': row.get('source_urls', [])})
        jobs.append(job)
    return {'schema_version': canonical['schema_version'], 'as_of': canonical['as_of'],
            'sources': sources, 'privacy': 'Generated public job-facts allowlist; no candidate assessments, application history, immigration analysis or materials.', 'jobs': jobs}
