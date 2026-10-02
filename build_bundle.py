"""Build only explicitly listed public files; never copy a working folder."""
import hashlib
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parent


def public_files():
    names = (ROOT / 'PUBLIC_FILES.txt').read_text().splitlines()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate manifest entries')
    for name in names:
        relative = PurePosixPath(name)
        if not name or relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe manifest path')
        if relative.parts[0] in {'local','private','data','runs','reports','.git','.codex','.claude','.agents'} or name == '.env':
            raise ValueError('Private location in manifest')
        path = ROOT / name
        if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_file():
            raise ValueError('Missing file or symlink in manifest: '+name)
        yield name, path


def audit(files):
    # Broad patterns supplement a manual content review; they do not prove absence of all personal data.
    patterns = [r'/(?:Users|home)/[A-Za-z0-9_.-]+/', r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
                r'\bsk-(?:or-v1-)?[A-Za-z0-9]{20,}', r'\b[A-Za-z0-9._%+-]+@(?:gmail|outlook|icloud)\.com\b']
    for name, path in files:
        content = path.read_text(encoding='utf-8')
        if any(re.search(pattern, content) for pattern in patterns):
            raise ValueError('Possible private content in '+name+'; review before packaging')


def main():
    files = list(public_files()); audit(files)
    output = ROOT / 'local' / 'distribution'; output.mkdir(parents=True, exist_ok=True)
    archive = output / 'decision-agent-starter.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name, path in files:
            bundle.write(path, 'decision-agent-starter/'+name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output/'SHA256SUMS.txt').write_text(digest+'  '+archive.name+'\n')
    print(f'{len(files)} explicitly listed files; pattern audit passed.')
    print(archive)
    print('SHA256 '+digest)


if __name__ == '__main__':
    main()
