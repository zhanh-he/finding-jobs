#!/usr/bin/env python3
"""Read-only official API snapshot; never changes canonical data or applies."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://api.smartrecruiters.com/v1/companies/Canva/postings'


def read(url):
    try:
        with urlopen(Request(url, headers={'User-Agent': 'finding-jobs-status-check/1.0'}), timeout=30) as response:
            return {'http_status': response.status, 'data': json.load(response)}
    except HTTPError as error:
        return {'http_status': error.code, 'access_note': 'No bypass; HTTP failure does not establish vacancy closure.'}
    except (URLError, TimeoutError, ValueError) as error:
        return {'http_status': None, 'access_note': type(error).__name__}


def snapshot():
    stamp = datetime.now(timezone.utc).isoformat()
    rows, pages, total = [], [], None
    for offset in range(0, 10000, 100):
        url = f'{BASE}?limit=100&offset={offset}'
        result = read(url)
        pages.append({'url': url, **result})
        if result['http_status'] != 200:
            break
        payload = result['data']
        total = payload.get('totalFound')
        batch = payload.get('content', [])
        rows.extend(batch)
        if not batch or (total is not None and len(rows) >= total):
            break
    ids = [str(row['id']) for row in rows]
    canonical = json.loads((ROOT / 'private/data/jobs.json').read_text())
    targets = {str(j['job_id']) for j in canonical['jobs'] if j.get('organization') == 'Canva' and j.get('job_id')}
    targets.update(alias for j in canonical['jobs'] if j.get('organization') == 'Canva' for alias in j.get('aliases', []) if alias.isdigit())
    details = {key: read(f'{BASE}/{key}') for key in sorted(targets)}
    complete = total is not None and len(rows) == total and len(set(ids)) == len(ids)
    report = {'checked_at': stamp, 'listing_total': total, 'rows': len(rows), 'unique_ids': len(set(ids)),
              'listing_complete_without_duplicate_ids': complete, 'pages': pages, 'target_details': details,
              'limitations': ['Public posting API only; targeted NeurIPS/ni recruitment may be absent.',
                              'No automatic canonical update, application, contact or deployment. Reconcile with official visible pages.']}
    directory = ROOT / '.local/canva_status_checks'
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (stamp.replace(':', '-') + '.json')
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'report': str(target.relative_to(ROOT)), 'rows': len(rows), 'complete': complete, 'canonical_changed': False}))
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(snapshot())
