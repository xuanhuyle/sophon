"""Fetch pinned public inputs and reproduce the upstream dbt project locally."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request

import duckdb

COMMIT = 'b79ecaefb12ae4a7e42314a3a2cee9645d401791'
REPOSITORY = 'https://github.com/bISTP/nyc-taxi-databricks-dbt.git'
INPUTS = {
    'yellow_tripdata_2025-01.parquet': 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet',
    'green_tripdata_2025-01.parquet': 'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-01.parquet',
    'yellow_dictionary.pdf': 'https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf',
    'trip_records.html': 'https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page',
    'congestion_program.html': 'https://portal.311.nyc.gov/article/?kanumber=KA-03612',
    'databricks_decimal.html': 'https://docs.databricks.com/aws/en/sql/language-manual/data-types/decimal-type',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def verify_raw_inputs(database, root):
    receipts = {}
    with duckdb.connect(str(database), read_only=True) as con:
        con.execute("SET memory_limit='512MB'")
        for service in ('yellow', 'green'):
            stored_sql = f'SELECT count(*), sum(hash(t)), bit_xor(hash(t)) FROM bronze.{service}_tripdata_raw t'
            source_sql = 'SELECT count(*), sum(hash(t)), bit_xor(hash(t)) FROM read_parquet(?) t'
            stored = con.execute(stored_sql).fetchone()
            original = con.execute(source_sql, [str(root / f'{service}_tripdata_2025-01.parquet')]).fetchone()
            receipts[service] = {'stored_sql': stored_sql, 'source_sql': source_sql,
                                 'columns': ['rows', 'row_hash_sum', 'row_hash_xor'],
                                 'stored': stored, 'source': original, 'equal': stored == original}
            if stored != original:
                raise RuntimeError('Raw input differs after preparation: ' + service)
    return receipts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-checkout', type=Path)
    args = parser.parse_args()
    root = Path('viability/runs/public_nyc').resolve()
    root.mkdir(parents=True, exist_ok=True)
    evidence = Path('viability/public_nyc/evidence')
    evidence.mkdir(parents=True, exist_ok=True)
    project = root / 'project'
    if project.exists():
        raise RuntimeError('Refusing to overwrite an existing prepared project')
    source = args.source_checkout
    if source is None:
        source = root / 'upstream'
        source.mkdir()
        for command in ([ 'git', 'init'], ['git', 'remote', 'add', 'origin', REPOSITORY],
                        ['git', 'fetch', '--depth', '1', 'origin', COMMIT],
                        ['git', 'checkout', '--detach', 'FETCH_HEAD']):
            subprocess.run(command, cwd=source, check=True, capture_output=True)
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    if actual != COMMIT:
        raise RuntimeError('Wrong upstream commit')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True).strip():
        raise RuntimeError('Upstream checkout is modified')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=source).decode().split('\0')
    inventory = {f: sha(source / f) for f in tracked if f}
    provenance = {'repository': REPOSITORY, 'commit': actual, 'upstream_files': inventory,
                  'protocol_sha256': sha('viability/public_nyc/PROTOCOL.md'),
                  'inputs': {}, 'engine': 'DuckDB ' + duckdb.__version__,
                  'live_databricks': False,
                  'adaptations': ['Local DuckDB profile instead of Databricks connection.',
                                  'January only; both services loaded; yellow-only rule audit.',
                                  'Full refresh with is_test_run=false.',
                                  'Upstream model SQL, YAML and macros remain unchanged.']}
    for name, url in INPUTS.items():
        path = root / name
        if not path.exists():
            request = urllib.request.Request(url, headers={'User-Agent': 'Sophon-public-research/0.1'})
            with urllib.request.urlopen(request, timeout=60) as response, path.open('wb') as f:
                shutil.copyfileobj(response, f)
        provenance['inputs'][name] = {'url': url, 'bytes': path.stat().st_size, 'sha256': sha(path)}
        print('INPUT', name, path.stat().st_size, flush=True)
    shutil.copytree(source, project, ignore=shutil.ignore_patterns('.git', 'assets'))
    # Keep active database/WAL writes on native local disk. The managed workspace
    # exhibited stale WAL replay during the first run; finalized files are copied.
    database = Path(tempfile.mkdtemp(prefix='sophon-public-nyc-')) / 'prod.duckdb'
    with duckdb.connect(str(database)) as con:
        con.execute("SET memory_limit='512MB'")
        con.execute('SET threads=2')
        con.execute('CREATE SCHEMA bronze')
        for service in ('yellow', 'green'):
            con.execute(f'CREATE TABLE bronze.{service}_tripdata_raw AS SELECT * FROM read_parquet(?)',
                        [str(root / f'{service}_tripdata_2025-01.parquet')])
        con.execute('CHECKPOINT')
    profile = {'default': {'target': 'dev', 'outputs': {'dev': {
        'type': 'duckdb', 'path': str(database), 'schema': 'silver', 'threads': 2,
        'settings': {'memory_limit': '512MB', 'threads': 2},
    }}}}
    (project / 'profiles.yml').write_text(json.dumps(profile, indent=2))
    dbt = Path(sys.executable).parent / 'dbt'
    commands = [ [str(dbt), 'deps', '--profiles-dir', str(project)],
                 [str(dbt), 'build', '--full-refresh', '--vars', '{"is_test_run": false}',
                  '--profiles-dir', str(project)] ]
    provenance['commands'] = []
    for index, command in enumerate(commands):
        log = evidence / f'dbt_{index}.log'
        with log.open('w') as f:
            result = subprocess.run(command, cwd=project, stdout=f, stderr=subprocess.STDOUT)
        provenance['commands'].append({'argv': command, 'returncode': result.returncode,
                                       'log': str(log)})
        (evidence / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
        print('DBT', index, result.returncode, str(log), flush=True)
        if result.returncode:
            raise RuntimeError('dbt command failed; inspect the recorded log')
    unchanged = {f: sha(project / f) == expected for f, expected in inventory.items()
                 if (project / f).is_file()}
    provenance['copied_upstream_files_unchanged'] = unchanged
    provenance['adaptations'].append('Native temporary database storage; copied after dbt closes.')
    provenance['raw_input_verification'] = verify_raw_inputs(database, root)
    if Path(str(database) + '.wal').exists():
        raise RuntimeError('Database still has an active WAL; refusing to copy it')
    shutil.copy2(database, root / 'prod.duckdb')
    (evidence / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    if not all(unchanged.values()):
        raise RuntimeError('Upstream files changed during local preparation')


if __name__ == '__main__':
    main()
