"""
Loader for Agent Action Manifests.

Handles reading, parsing, and writing manifest files.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from pydantic import ValidationError

from .models import AgentActionManifest


#: Largest manifest file ``load_manifest`` reads (bytes). A larger file is refused before it is parsed.
MAX_MANIFEST_BYTES = 4 * 1024 * 1024


class ManifestLoadError(Exception):
    """Raised when a manifest cannot be loaded."""


def load_manifest(path: str | Path) -> AgentActionManifest:
    """Load and parse an AgentActionManifest from a JSON file.

    Raises:
        ManifestLoadError: if the file is not found, JSON is invalid, or the
            data does not conform to the AgentActionManifest schema.
    """
    path = Path(path)
    if not path.exists():
        raise ManifestLoadError(f"Manifest file not found: {path}")

    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_MANIFEST_BYTES + 1)
    except OSError as exc:
        raise ManifestLoadError(f"Could not read manifest file '{path}': {exc}") from exc
    if len(data) > MAX_MANIFEST_BYTES:
        raise ManifestLoadError(f"Manifest file '{path}' is larger than {MAX_MANIFEST_BYTES} bytes.")

    try:
        raw = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ManifestLoadError(f"Manifest file '{path}' is not valid UTF-8: {exc}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestLoadError(
            f"Invalid JSON in manifest file '{path}': {exc}"
        ) from exc
    except RecursionError as exc:
        raise ManifestLoadError(f"Manifest file '{path}' is nested too deeply to parse.") from exc

    return load_manifest_json(payload)


def load_manifest_json(payload: dict) -> AgentActionManifest:
    """Parse and validate an AgentActionManifest from a dict.

    Raises:
        ManifestLoadError: if the data does not conform to the AgentActionManifest schema.
    """
    try:
        return AgentActionManifest.model_validate(payload)
    except ValidationError as exc:
        raise ManifestLoadError(
            f"Manifest data failed schema validation:\n{exc}"
        ) from exc
    except RecursionError as exc:
        raise ManifestLoadError("Manifest data is nested too deeply to validate.") from exc


def dump_manifest(manifest: AgentActionManifest, path: str | Path) -> Path:
    """Serialize an AgentActionManifest to a JSON file.

    The document is encoded to UTF-8 before any file is opened, so text that cannot be encoded (for example an unpaired surrogate)
    raises ``ValueError`` and leaves an existing file untouched. The bytes are written to a temporary file in the same directory and
    moved over the target with ``os.replace``, so a reader never sees a partial file. A new file gets the usual umask-based mode; an
    existing file keeps its mode.

    Returns:
        The resolved Path that was written.
    """
    path = Path(path)
    data = manifest.model_dump(mode="json")
    try:
        encoded = (json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("Manifest contains text that cannot be encoded as UTF-8 (for example an unpaired surrogate).") from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        mode = os.stat(path).st_mode & 0o7777
    except FileNotFoundError:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return path
