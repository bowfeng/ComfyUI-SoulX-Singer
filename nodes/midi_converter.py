"""ComfyUI nodes for MIDI <-> Meta conversion.

This module provides two nodes for bidirectional conversion between SoulX-Singer
metadata JSON format and MIDI files:
- MetaToMIDI: Converts SoulX-Singer metadata JSON to MIDI
- MIDIToMetaWithVocal: Converts MIDI to SoulX-Singer metadata with vocal file support
"""

import os
import sys
import json
import tempfile
import logging
from pathlib import Path
from typing import Tuple, Optional

# Add SoulX-Singer to path to access preprocessing tools
current_dir = Path(__file__).parent.parent
soulx_dir = current_dir / "SoulX-Singer"
if str(soulx_dir) not in sys.path:
    sys.path.insert(0, str(soulx_dir))

from preprocess.tools.midi_parser import midi2meta, meta2midi

# Initialize logger for this module
logger = logging.getLogger("SoulX-Singer")


class SoulXSingerMetaToMIDI:
    """Convert SoulX-Singer metadata JSON to MIDI file.

    This node converts SoulX-Singer's metadata JSON format (which contains
    F0 contours, phonemes, and timing information) to a standard MIDI file.
    This is useful for exporting synthesized singing results or for using
    MIDI files as input for other audio processing workflows.

    FIX: Added path quote stripping to handle Windows path inputs with quotes
    (e.g., "D:\path\to\file.json") which caused OSError on Windows.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "meta_file": ("STRING", {
                    "default": "",
                    "tooltip": "Path to SoulX-Singer metadata JSON file",
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("midi_file", "meta_file")
    FUNCTION = "convert"
    CATEGORY = "SoulX-Singer"
    DESCRIPTION = "Convert SoulX-Singer metadata JSON to MIDI file"

    def convert(
        self,
        meta_file: str,
    ) -> Tuple[str, str]:
        """Convert Meta to MIDI.

        Args:
            meta_file: Path to input SoulX-Singer metadata JSON file

        Returns:
            Tuple of (midi_file, meta_file) - MIDI file path and original meta file path

        Note:
            The MIDI file will be created in the same directory as the input JSON
            with the same filename but .mid extension.
        """
        # FIX: Remove quotes from paths if present to handle Windows path inputs
        # This prevents OSError: [WinError 123] on Windows when paths contain quotes
        meta_file = meta_file.strip('"').strip("'")

        # Use meta_file's directory and generate midi file with same name but .mid extension
        meta_path = Path(meta_file)
        midi_file = str(meta_path.with_suffix(".mid"))

        # Ensure output directory exists
        midi_dir = os.path.dirname(midi_file)
        if midi_dir:
            os.makedirs(midi_dir, exist_ok=True)

        # Convert Meta to MIDI using SoulX-Singer's internal function
        meta2midi(
            meta_path=meta_file,
            midi_path=midi_file,
        )

        return (midi_file, meta_file)


class SoulXSingerMIDIToMetaWithVocal:
    """Convert MIDI file to SoulX-Singer metadata JSON with automatic vocal file handling.

    This node converts MIDI files to SoulX-Singer's metadata JSON format. It requires
    an original vocal WAV file for F0 (fundamental frequency) extraction, which is
    essential for accurate singing voice synthesis.

    FIX: Added path quote stripping and vocal file auto-detection to handle common
    user input issues:
    1. Strips quotes from file paths to prevent Windows OSError
    2. Automatically searches for vocal.wav if not provided
    3. Provides clear error messages when vocal file is missing

    This is useful for preparing MIDI files for synthesis or for converting existing
    MIDI compositions to SoulX-Singer's format.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "midi_file": ("STRING", {
                    "default": "",
                    "tooltip": "Path to MIDI file",
                }),
                "vocal_file": ("STRING", {
                    "default": "",
                    "tooltip": "Path to original vocal WAV file (for F0 extraction). Can be left empty to auto-detect vocal.wav",
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("meta_file", "midi_file")
    FUNCTION = "convert"
    CATEGORY = "SoulX-Singer"
    DESCRIPTION = "Convert MIDI file to SoulX-Singer metadata JSON with automatic vocal file handling"

    def convert(
        self,
        midi_file: str,
        vocal_file: str,
    ) -> Tuple[str, str]:
        """Convert MIDI to Meta with vocal file.

        Args:
            midi_file: Path to input MIDI file
            vocal_file: Path to original vocal WAV file (optional, will search for vocal.wav if empty)

        Returns:
            Tuple of (meta_file, midi_file) - Meta file path and original MIDI file path

        Note:
            If vocal_file is not provided, the node will automatically search for a file
            named 'vocal.wav' in the same directory as the MIDI file. If not found,
            a ValueError will be raised with clear instructions.
        """
        # FIX: Remove quotes from paths if present to handle Windows path inputs
        # This prevents OSError: [WinError 123] on Windows when paths contain quotes
        midi_file = midi_file.strip('"').strip("'")
        vocal_file = vocal_file.strip('"').strip("'")

        # Use midi_file's directory and generate meta file with same name but .json extension
        midi_path = Path(midi_file)
        meta_file = str(midi_path.with_suffix(".json"))

        # Ensure output directory exists
        meta_dir = os.path.dirname(meta_file)
        if meta_dir:
            os.makedirs(meta_dir, exist_ok=True)

        # If vocal_file is empty, search for vocal.wav in the same directory
        if not vocal_file:
            midi_dir = midi_path.parent
            vocal_path = midi_dir / "vocal.wav"
            if vocal_path.exists():
                vocal_file = str(vocal_path)
                logger.info(f"Found vocal.wav in same directory: {vocal_path}")
            else:
                raise ValueError(
                    "vocal_file is required. Please provide the path to the vocal wav file, "
                    "or ensure 'vocal.wav' exists in the same directory as the MIDI file."
                )

        # Convert MIDI to Meta using SoulX-Singer's internal function
        midi2meta(
            midi_path=midi_file,
            meta_path=meta_file,
            vocal_file=vocal_file,
        )

        return (meta_file, midi_file)