#!/usr/bin/env python3
"""Recompute the CBP CROSS statistics quoted in MARKET_DISCOVERY.md.

Input: cbp_rulings_data.csv from https://github.com/justinmoonjeli/CROSSFetch
(open-source scrape of the CBP Customs Rulings Online Search System, 216,164
rulings to 2025-03-13). Columns: id, rulingNumber, subject, categories,
rulingDate, isUsmca, isNafta, collection, relatedRulings, modifiedBy, modifies,
revokedBy, revokes, tariffs.

Definitions used throughout the report:
- "prior" ruling on a line = a ruling on the same 6- or 10-digit line with a
  strictly earlier rulingDate; per ruling, the maximum count across its codes.
- A 6-digit line is the first six digits of any cited code. A 10-digit line is
  the first ten digits of a code cited at ten digits; chapter 98 and 99 measure
  codes are cited at eight digits (1,356 of 1,363 such citations in 2023-24) and
  therefore fall out of the 10-digit statistics but stay in the 6-digit ones.
- Denominators for the 10-digit statistics are rulings carrying at least one
  10-digit code (3,073 of the 3,247 coded 2023-24 rulings); the same figures on
  the all-coded denominator are 5 points lower (93.9% -> 88.9%; 71.5% -> 67.6%).
- Concentration and singleton statistics exclude chapters 98 and 99 explicitly
  and count one mention per ruling per line.
- "superseding ruling" = a ruling whose modifies or revokes field is non-empty.
- same-day co-citation cluster = rulings sharing (rulingDate, cited ruling);
  this is a batch-filing proxy, not a measure of interpretive recurrence.
Run: python3 cross_recomputation.py path/to/cbp_rulings_data.csv
"""
import csv, collections, re, statistics, sys, bisect
from datetime import date
csv.field_size_limit(10**9)
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8', errors='replace')))
print('rows', len(rows))
def codes(s): return [re.sub(r'\D', '', c.strip()) for c in s.split(',') if c.strip()]
by = {r['rulingNumber'].strip(): r for r in rows}
yr = collections.Counter(); hq = collections.Counter()
for r in rows:
    y = r['rulingDate'][:4]; yr[y] += 1
    if r['collection'].strip().lower() == 'hq': hq[y] += 1
for y in ('2017', '2021', '2022', '2023', '2024'): print(y, 'all', yr[y], 'HQ', hq[y])
mr = sum(1 for r in rows if r['modifiedBy'].strip() or r['revokedBy'].strip())
print('ever modified or revoked', mr, '%.2f%%' % (100 * mr / len(rows)))
sup = [r for r in rows if r['modifies'].strip() or r['revokes'].strip()]
print('superseding rulings', len(sup), 'HQ share %.1f%%' % (100 * sum(1 for r in sup if r['collection'].strip().lower() == 'hq') / len(sup)))
c = collections.Counter(r['rulingDate'][:4] for r in sup if r['collection'].strip().lower() == 'hq')
print('HQ superseding by year', {y: c[y] for y in ('2020', '2021', '2022', '2023', '2024')})
lags = []
for r in sup:
    for t in (r['modifies'] + ',' + r['revokes']).split(','):
        t = t.strip()
        if t in by and by[t]['rulingDate'][:4].isdigit() and r['rulingDate'][:4].isdigit():
            lags.append((date.fromisoformat(r['rulingDate'][:10]) - date.fromisoformat(by[t]['rulingDate'][:10])).days / 365.25)
print('supersession lag n', len(lags), 'median years %.2f' % statistics.median(lags))
r2 = [r for r in rows if r['rulingDate'][:4] in ('2023', '2024')]
print('2023-24 rulings', len(r2), 'HQ', sum(1 for r in r2 if r['collection'].strip().lower() == 'hq'), 'protest in subject', sum(1 for r in r2 if 'protest' in r['subject'].lower()))
print('no code %.1f%%' % (100 * sum(1 for r in r2 if not codes(r['tariffs'])) / len(r2)))
print('origin in subject %.1f%%' % (100 * sum(1 for r in r2 if 'origin' in r['subject'].lower()) / len(r2)))
print('set or kit in subject %.1f%%' % (100 * sum(1 for r in r2 if re.search(r'\b(set|sets|kit|kits)\b', r['subject'].lower())) / len(r2)))
print('chapter 99 cited %.1f%%' % (100 * sum(1 for r in r2 if any(c.startswith('99') for c in codes(r['tariffs']))) / len(r2)))
r17 = [r for r in rows if r['rulingDate'][:4] == '2017']
print('2017 chapter 99 cited %.1f%%' % (100 * sum(1 for r in r17 if any(c.startswith('99') for c in codes(r['tariffs']))) / len(r17)))
print('cites a related ruling %.1f%%' % (100 * sum(1 for r in r2 if r['relatedRulings'].strip()) / len(r2)))
first10 = collections.defaultdict(list); first6 = collections.defaultdict(list)
for r in rows:
    d = r['rulingDate'][:10]
    for cc in set(codes(r['tariffs'])):
        if len(cc) >= 10: first10[cc[:10]].append(d)
        if len(cc) >= 6: first6[cc[:6]].append(d)
for k in first10: first10[k].sort()
for k in first6: first6[k].sort()
p10 = p6 = n = ten = 0; priors = []
for r in r2:
    cs = set(codes(r['tariffs']))
    c10 = [cc[:10] for cc in cs if len(cc) >= 10]; c6 = [cc[:6] for cc in cs if len(cc) >= 6]
    if not c6: continue
    n += 1; d = r['rulingDate'][:10]
    if any(bisect.bisect_left(first6[cc], d) > 0 for cc in c6): p6 += 1
    if c10:
        m = max(bisect.bisect_left(first10[cc], d) for cc in c10)
        if m > 0: p10 += 1
        priors.append(m)
        if m >= 10: ten += 1
print('coded 2023-24', n, 'prior 6-digit %.1f%%' % (100 * p6 / n), 'prior 10-digit %.1f%% of %d with a 10-digit code' % (100 * p10 / len(priors), len(priors)), 'median priors on the 10-digit line', statistics.median(priors), 'ten or more priors %.1f%%' % (100 * ten / len(priors)))
l6 = collections.Counter(); l10 = collections.Counter()
for r in r2:
    cs = [cc for cc in codes(r['tariffs']) if len(cc) >= 6 and cc[:2] not in ('98', '99')]
    for cc in set(cc[:6] for cc in cs): l6[cc] += 1
    for cc in set(cc[:10] for cc in cs if len(cc) >= 10): l10[cc] += 1
tot = sum(l6.values()); cum = 0; k = 0
for cc, v in l6.most_common():
    cum += v; k += 1
    if cum >= tot / 2: break
print('excluding chapters 98 and 99: 6-digit lines', len(l6), 'mentions (one per ruling per line)', tot, 'lines covering half', k, '| 10-digit lines', len(l10), 'singleton lines %.1f%%' % (100 * sum(1 for v in l10.values() if v == 1) / len(l10)))
g = collections.Counter()
for r in r2:
    for t in r['relatedRulings'].split(','):
        t = t.strip()
        if t: g[(r['rulingDate'][:10], t)] += 1
print('same-day (date, cited ruling) groups >=2:', sum(1 for v in g.values() if v >= 2), 'rulings', sum(v for v in g.values() if v >= 2), '| >=3:', sum(1 for v in g.values() if v >= 3), 'rulings', sum(v for v in g.values() if v >= 3), 'of', len(r2))
