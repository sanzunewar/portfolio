"""Custom static files storage.

Subclasses WhiteNoise's manifest storage but sets manifest_strict = False so
that a missing manifest entry (e.g. during tests, before collectstatic runs)
falls back to the plain filename instead of raising. Production still gets
hashed, cache-busted filenames after collectstatic.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
