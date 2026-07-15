"""Make the skill's scripts/ importable (import tts, markers, phonemes, backends.*)."""
import os
import sys

_SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "ttsCN", "scripts",
)
sys.path.insert(0, _SCRIPTS)
