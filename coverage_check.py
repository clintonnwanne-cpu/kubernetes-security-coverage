"""Offline synthetic coverage reconciliation. No Kubernetes/cloud access."""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone


def instant(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timestamps require a timezone')
    return dt.astimezone(timezone.utc)


def analyze(data, now, max_age_hours=24):
    if max_age_hours <= 0:
        raise ValueError('max_age_hours must be positive')
    now = instant(now)
    nodes = data['nodes']
    ids = [n['id'] for n in nodes]
    if any(not isinstance(x, str) or not x.strip() for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('node IDs must be nonempty and unique')
    observations = {}
    for obs in data['observations']:
        observations.setdefault(obs['node_id'], []).append(obs)
    rows = []
    for node in nodes:
        node_id = node['id']
        evidence = observations.get(node_id, [])
        if node.get('supported') is False:
            status, reason = 'unsupported', 'control not supported; remains in denominator'
        elif node.get('supported') is not True:
            status, reason = 'unknown', 'support status absent or invalid'
        elif not evidence:
            status, reason = 'missing', 'no observation'
        else:
            try:
                dated = [(instant(o['observed_at']), o) for o in evidence]
                latest = max(t for t, _ in dated)
                newest = [o for t, o in dated if t == latest]
                age = (now - latest).total_seconds() / 3600
                if age < 0:
                    status, reason = 'unknown', 'future observation'
                elif len({str(o.get('healthy')) for o in newest}) != 1:
                    status, reason = 'unknown', 'conflicting latest observations'
                elif age > max_age_hours:
                    status, reason = 'stale', 'latest observation exceeds freshness window'
                elif newest[0].get('healthy') is True:
                    status, reason = 'covered', 'fresh healthy synthetic observation'
                elif newest[0].get('healthy') is False:
                    status, reason = 'missing', 'sensor reports unhealthy'
                else:
                    status, reason = 'unknown', 'invalid health value'
            except (ValueError, KeyError, TypeError, AttributeError):
                status, reason = 'unknown', 'malformed observation timestamp'
        rows.append({'node_id': node_id, 'status': status, 'reason': reason})
    counts = dict(Counter(r['status'] for r in rows))
    complete = data.get('inventory_complete') is True
    known_percent = round(100 * counts.get('covered', 0) / len(nodes), 2) if nodes else None
    return {'evaluated_at': now.isoformat(), 'inventory_complete': complete,
            'known_nodes': len(nodes), 'counts': counts,
            'known_inventory_coverage_percent': known_percent,
            'fleet_coverage_percent': known_percent if complete and nodes else None,
            'orphan_observation_ids': sorted(set(observations) - set(ids)),
            'rows': sorted(rows, key=lambda r: r['node_id']),
            'limitation': 'Input completeness is asserted by the caller, not independently verified. Sensor health is not proof of enforcement.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input'); p.add_argument('--now', required=True)
    p.add_argument('--max-age-hours', type=float, default=24)
    a = p.parse_args()
    try:
        with open(a.input) as f: data = json.load(f)
        print(json.dumps(analyze(data, a.now, a.max_age_hours), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as e:
        p.exit(2, f'Invalid input: {e}\n')

if __name__ == '__main__': main()
