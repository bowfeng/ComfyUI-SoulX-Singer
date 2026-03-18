"""ComfyUI nodes for SoulX-Singer."""

from .model_loader import SoulXSingerModelLoader
from .simple_synthesizer import SoulXSingerSimple
from .advanced_synthesizer import SoulXSingerAdvanced
from .midi_converter import SoulXSingerMetaToMIDI, SoulXSingerMIDIToMetaWithVocal

__all__ = ['SoulXSingerModelLoader', 'SoulXSingerSimple', 'SoulXSingerAdvanced', 'SoulXSingerMetaToMIDI', 'SoulXSingerMIDIToMetaWithVocal']
