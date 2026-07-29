import shutil
import os

files_to_archive = [
    'python/observer/program.py',
    'python/observer/program_resolver.py',
    'python/observer/cross_repo_program_resolver.py',
    'python/observer/initiative.py',
    'python/observer/workstream.py',
    'python/observer/initiative_resolver.py',
    'python/observer/workstream_resolver.py'
]

for f in files_to_archive:
    if os.path.exists(f):
        dest = f.replace('python/observer/', 'archive/experimental/')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy(f, dest)
        print(f'Archived: {f} -> {dest}')
    else:
        print(f'Not found: {f}')

print('Archivization complete')