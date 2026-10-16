#!/usr/bin/env python3
"""Reverse-apply the modele-social/règles hunks of a git diff onto a COPY of the AFTER tree -> BEFORE tree.
usage: python3 -I work/scripts/make_before_tree.py DIFF_PATCH AFTER_ROOT OUT_ROOT [--all]
  AFTER_ROOT = dir containing modele-social/ (e.g. inputs/rules/G1_xxx); OUT_ROOT/modele-social is (re)created.
  --all also reverses non-règles files under modele-social/ (package.json, CHANGELOG...).
Prints a JSON summary: per diff file status, hunk reports, sha256 before/after, files differing between the trees.
Handles git-quoted paths with octal escapes ("r\303\250gles"). Context lines are verified before reversing.
"""
import sys, os, re, json, shutil, hashlib

def unquote_git_path(p):
    if p.startswith('"') and p.endswith('"'):
        inner = p[1:-1]; out = bytearray(); i = 0
        while i < len(inner):
            c = inner[i]
            if c == '\\':
                nxt = inner[i+1]
                if nxt in '01234567':
                    out.extend(bytes([int(inner[i+1:i+4], 8)])); i += 4; continue
                out.extend({'n':'\n','t':'\t'}.get(nxt, nxt).encode()); i += 2; continue
            out.extend(c.encode('utf-8')); i += 1
        p = out.decode('utf-8')
    return p

def parse_diff(text):
    files = []; cur = None; lines = text.split('\n'); i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('diff --git '):
            cur = {'hunks': []}; files.append(cur)
        elif ln.startswith('--- ') and cur is not None:
            cur['old'] = unquote_git_path(ln[4:].strip())
        elif ln.startswith('+++ ') and cur is not None:
            cur['new'] = unquote_git_path(ln[4:].strip())
        elif ln.startswith('@@') and cur is not None:
            m = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', ln)
            h = {'old_start': int(m.group(1)), 'old_len': int(m.group(2) or 1),
                 'new_start': int(m.group(3)), 'new_len': int(m.group(4) or 1), 'lines': []}
            cur['hunks'].append(h); i += 1
            rem_old, rem_new = h['old_len'], h['new_len']
            while i < len(lines) and (rem_old > 0 or rem_new > 0):
                l = lines[i]
                if l.startswith('\\'): i += 1; continue
                tag = l[0] if l else ' '; body = l[1:] if l else ''
                if tag == ' ': rem_old -= 1; rem_new -= 1
                elif tag == '-': rem_old -= 1
                elif tag == '+': rem_new -= 1
                else: break
                h['lines'].append((tag, body)); i += 1
            continue
        i += 1
    return files

def reverse_apply(path, hunks):
    content = open(path, encoding='utf-8').read()
    nl = content.endswith('\n'); lines = content.split('\n')
    if nl: lines = lines[:-1]
    report = []
    for h in sorted(hunks, key=lambda h: -h['new_start']):
        exp_after = [b for t, b in h['lines'] if t in ' +']
        exp_before = [b for t, b in h['lines'] if t in ' -']
        s = h['new_start'] - 1; actual = lines[s:s+len(exp_after)]
        if actual != exp_after:
            report.append({'hunk_new_start': h['new_start'], 'status': 'CONTEXT_MISMATCH', 'actual': actual, 'expected': exp_after}); continue
        lines[s:s+len(exp_after)] = exp_before
        report.append({'hunk_new_start': h['new_start'], 'status': 'REVERSED',
                       'lines_added_by_commit': [b for t, b in h['lines'] if t == '+'],
                       'lines_removed_by_commit': [b for t, b in h['lines'] if t == '-']})
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + ('\n' if nl else ''))
    return report

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def tree_hashes(root):
    return {os.path.relpath(os.path.join(dp, f), root): sha(os.path.join(dp, f))
            for dp, _, fn in os.walk(root) for f in fn}

def main():
    diff_path, after_root, out_root = sys.argv[1:4]; only_regles = '--all' not in sys.argv
    src, dst = os.path.join(after_root, 'modele-social'), os.path.join(out_root, 'modele-social')
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    files = parse_diff(open(diff_path, encoding='utf-8').read())
    summary = {'diff': diff_path, 'after_root': after_root, 'out_root': out_root, 'files': []}
    for fd in files:
        newp = fd.get('new', ''); oldp = fd.get('old', '')
        rel = (newp[2:] if newp.startswith('b/') else newp)
        if rel == '/dev/null': rel = oldp[2:] if oldp.startswith('a/') else oldp
        e = {'path': rel, 'hunks': len(fd['hunks'])}
        if not rel.startswith('modele-social/'): e['status'] = 'SKIPPED_NOT_IN_MODELE_SOCIAL'
        elif only_regles and not rel.startswith('modele-social/règles/'): e['status'] = 'SKIPPED_NOT_RULES'
        else:
            target = os.path.join(out_root, rel)
            if oldp.endswith('/dev/null'):
                os.remove(target); e['status'] = 'FILE_ADDED_BY_COMMIT_REMOVED_IN_BEFORE'
            elif newp.endswith('/dev/null') or not os.path.exists(target):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                before = [b for h in fd['hunks'] for t, b in h['lines'] if t in ' -']
                open(target, 'w', encoding='utf-8').write('\n'.join(before) + '\n'); e['status'] = 'FILE_DELETED_BY_COMMIT_RESTORED'
            else:
                e['sha_after'] = sha(os.path.join(after_root, rel))
                e['hunk_report'] = reverse_apply(target, fd['hunks']); e['sha_before'] = sha(target)
                e['status'] = 'OK' if all(r['status'] == 'REVERSED' for r in e['hunk_report']) else 'PARTIAL'
        summary['files'].append(e)
    ha, hb = tree_hashes(src), tree_hashes(dst)
    summary['files_differing_between_trees'] = sorted(k for k in set(ha) | set(hb) if ha.get(k) != hb.get(k))
    summary['n_files_after'], summary['n_files_before'] = len(ha), len(hb)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
main()
