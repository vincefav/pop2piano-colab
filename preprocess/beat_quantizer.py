import copy
import numpy as np
import note_seq

# Try to import optional dependencies
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available")

try:
    import scipy.interpolate as interp
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not available, using numpy fallback for interpolation")

try:
    import essentia
    import essentia.standard
    ESSENTIA_AVAILABLE = True
except ImportError:
    ESSENTIA_AVAILABLE = False
    print("Warning: essentia not available, using librosa fallback for rhythm extraction")

SAMPLERATE = 44100


def nearest_onset_offset_digitize(on, off, bins):
    intermediate = (bins[1:] + bins[:-1]) / 2
    on_idx = np.digitize(on, intermediate)
    off_idx = np.digitize(off, intermediate)
    off_idx[on_idx == off_idx] += 1
    # off_idx = np.clip(off_idx, a_min=0, a_max=len(bins) - 1)
    return on_idx, off_idx


def apply_sustain_pedal(pm):
    ns = note_seq.midi_to_note_sequence(pm)
    susns = note_seq.apply_sustain_control_changes(ns)
    suspm = note_seq.note_sequence_to_pretty_midi(susns)
    return suspm


def simple_interpolate(x, y, x_new):
    """Simple linear interpolation fallback when scipy is not available."""
    return np.interp(x_new, x, y)


def interpolate_beat_times(beat_times, steps_per_beat, extend=False):
    if SCIPY_AVAILABLE:
        beat_times_function = interp.interp1d(
            np.arange(beat_times.size),
            beat_times,
            bounds_error=False,
            fill_value="extrapolate",
        )
        if extend:
            beat_steps_8th = beat_times_function(
                np.linspace(0, beat_times.size, beat_times.size * steps_per_beat + 1)
            )
        else:
            beat_steps_8th = beat_times_function(
                np.linspace(0, beat_times.size - 1, beat_times.size * steps_per_beat - 1)
            )
    else:
        # Fallback using numpy interpolation
        x_old = np.arange(beat_times.size)
        if extend:
            x_new = np.linspace(0, beat_times.size, beat_times.size * steps_per_beat + 1)
        else:
            x_new = np.linspace(0, beat_times.size - 1, beat_times.size * steps_per_beat - 1)
        beat_steps_8th = simple_interpolate(x_old, beat_times, x_new)
    
    return beat_steps_8th


def midi_quantize_by_beats(
    sample, beat_times, steps_per_beat, ignore_sustain_pedal=False
):
    ns = note_seq.midi_file_to_note_sequence(sample.midi)
    if ignore_sustain_pedal:
        susns = ns
    else:
        susns = note_seq.apply_sustain_control_changes(ns)

    qns = copy.deepcopy(susns)

    notes = np.array([[n.start_time, n.end_time] for n in susns.notes])
    note_attributes = np.array([[n.pitch, n.velocity] for n in susns.notes])

    note_ons = np.array(notes[:, 0])
    note_offs = np.array(notes[:, 1])

    beat_steps_8th = interpolate_beat_times(beat_times, steps_per_beat, extend=False)

    on_idx, off_idx = nearest_onset_offset_digitize(note_ons, note_offs, beat_steps_8th)

    beat_steps_8th = interpolate_beat_times(beat_times, steps_per_beat, extend=True)

    discrete_notes = np.concatenate(
        (np.stack((on_idx, off_idx), axis=1), note_attributes), axis=1
    )

    def delete_duplicate_notes(dnotes):
        note_order = dnotes[:, 0] * 128 + dnotes[:, 2]
        dnotes = dnotes[note_order.argsort()]
        indices = []
        for i in range(1, len(dnotes)):
            if dnotes[i, 0] == dnotes[i - 1, 0] and dnotes[i, 2] == dnotes[i - 1, 2]:
                indices.append(i)
        dnotes = np.delete(dnotes, indices, axis=0)
        note_order = dnotes[:, 0] * 128 + dnotes[:, 1]
        dnotes = dnotes[note_order.argsort()]
        return dnotes

    discrete_notes = delete_duplicate_notes(discrete_notes)

    digitized_note_ons, digitized_note_offs = (
        beat_steps_8th[on_idx],
        beat_steps_8th[off_idx],
    )

    for i, note in enumerate(qns.notes):
        note.start_time = digitized_note_ons[i]
        note.end_time = digitized_note_offs[i]

    return qns, discrete_notes, beat_steps_8th


def extract_rhythm_librosa_fallback(song, y=None):
    """
    Fallback rhythm extraction using librosa when essentia is not available.
    Returns similar format to essentia's RhythmExtractor2013.
    """
    if not LIBROSA_AVAILABLE:
        raise ImportError("Neither essentia nor librosa is available for rhythm extraction")
    
    if y is None:
        y, sr = librosa.load(song, sr=SAMPLERATE)
    else:
        sr = SAMPLERATE
    
    # Use librosa's beat tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units='time')
    
    # Convert to format expected by the rest of the code
    bpm = float(tempo)
    beat_times = beat_frames
    confidence = 1.0  # librosa doesn't provide confidence, so we use 1.0
    estimates = [tempo]  # Single tempo estimate
    beat_intervals = np.diff(beat_times) if len(beat_times) > 1 else np.array([60.0/bpm])
    
    return bpm, beat_times, confidence, estimates, beat_intervals


def extract_rhythm_minimal_fallback(song, y=None):
    """
    Minimal fallback when neither essentia nor librosa is available.
    Creates a simple constant tempo beat grid.
    """
    if y is None:
        # We can't load audio without librosa, so create a dummy duration
        duration = 120.0  # 2 minutes default
    else:
        duration = len(y) / SAMPLERATE
    
    # Assume 120 BPM as default
    bpm = 120.0
    beat_interval = 60.0 / bpm
    beat_times = np.arange(0, duration, beat_interval)
    
    confidence = 0.5  # Low confidence since this is a guess
    estimates = [bpm]
    beat_intervals = np.full(len(beat_times)-1, beat_interval) if len(beat_times) > 1 else np.array([beat_interval])
    
    print(f"Warning: Using minimal fallback rhythm extraction (constant {bpm} BPM)")
    return bpm, beat_times, confidence, estimates, beat_intervals


def extract_rhythm(song, y=None):
    """
    Extract rhythm using essentia if available, otherwise fall back to librosa, 
    or minimal fallback if neither is available.
    """
    if ESSENTIA_AVAILABLE:
        if y is None and LIBROSA_AVAILABLE:
            y, sr = librosa.load(song, sr=SAMPLERATE)
        elif y is None:
            # Can't load without librosa, use minimal fallback
            return extract_rhythm_minimal_fallback(song, y)

        essentia_tracker = essentia.standard.RhythmExtractor2013(method="multifeature")
        (
            bpm,
            beat_times,
            confidence,
            estimates,
            essentia_beat_intervals,
        ) = essentia_tracker(y)
        return bpm, beat_times, confidence, estimates, essentia_beat_intervals
    elif LIBROSA_AVAILABLE:
        print("Using librosa fallback for rhythm extraction (essentia not available)")
        return extract_rhythm_librosa_fallback(song, y)
    else:
        print("Using minimal fallback for rhythm extraction (neither essentia nor librosa available)")
        return extract_rhythm_minimal_fallback(song, y)
