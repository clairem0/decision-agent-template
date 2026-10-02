"""Small local JSON, atomic-write and writer-lock helpers; no network calls."""
import contextlib
import json
import os
from pathlib import Path
import tempfile


class Hold(ValueError):
    """Stop a mutation until its input or local state can be checked."""


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      parse_constant=lambda _: (_ for _ in ()).throw(Hold('Nonfinite JSON value.')))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, indent=2).encode('utf-8')


def atomic_write(path, data):
    path = Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextlib.contextmanager
def writer_lock(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    lock = root / '.writer.lock'
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise Hold('Another writer or interrupted writer holds .writer.lock in this review folder. Confirm no process is active before removing it.') from None
    try:
        try:
            os.write(descriptor, str(os.getpid()).encode())
        finally:
            os.close(descriptor)
        yield
    finally:
        lock.unlink(missing_ok=True)
