import numpy as np
from scipy.io import wavfile
from scipy.signal import resample
from scipy.interpolate import CubicSpline  # For soft-knee curve

# Tuned Params: Locked from prior teardowns
fs = 44100  # Sample rate
duration = 10  # Duration in seconds
runs = 3  # Iterative runs
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

# Evolved Lyrics Timestamps (unchanged for synchronization)
lyrics = [
    (2.0, "Reverberate in the silt of what was"),
    (4.5, "Fine enough to tear through fingers"),
    (6.8, "Gone but grinding still"),
    (9.0, "Haunting the static cracks, gold beneath"),
]


def soft_knee_compress(signal, threshold_db=-6, ratio=4, knee_width=3):
    """
    Apply soft-knee compression to preserve dynamics.
    - threshold_db: Compression start point in dB
    - ratio: Compression ratio (e.g., 4:1)
    - knee_width: Width of the soft knee in dB for smooth transition
    """
    # Convert to dB
    signal_db = 20 * np.log10(np.abs(signal) + 1e-10)
    threshold_linear = 10 ** (threshold_db / 20)

    # Define knee points for cubic spline
    knee_points = np.array(
        [
            [-knee_width / 2 + threshold_db, 0],
            [threshold_db, 0],
            [threshold_db + knee_width / 2, knee_width / 2 * (1 - 1 / ratio)],
        ]
    )
    spline_x = knee_points[:, 0]
    spline_y = knee_points[:, 1]
    compressor_curve = CubicSpline(spline_x, spline_y)

    # Apply gain reduction
    gain_reduction = np.zeros_like(signal_db)
    over_threshold = signal_db > threshold_db
    gain_reduction[over_threshold] = (
        compressor_curve(signal_db[over_threshold] - threshold_db) * 20 / np.log(10)
    )

    # Reconstruct compressed signal
    compressed_db = signal_db - gain_reduction
    compressed = np.sign(signal) * (10 ** (compressed_db / 20))
    return compressed / np.max(np.abs(compressed))  # Final normalization


for run in range(1, runs + 1):
    print(
        f"\n--- Run #{run}: {['Foundation', 'Teeth-Grind Humor', 'Maximum Nerve-Fray'][run-1]} ---"
    )

    # Warped vocal: Gut-grunt base, progressive vibrato
    freq_base = 110  # Hz
    vocal = np.sin(2 * np.pi * freq_base * t) * np.exp(-t / 2)
    vibrato_depth = [0.5, 0.8, 1.0][run - 1]
    vocal *= 1 + vibrato_depth * np.sin(2 * np.pi * 0.1 * t)

    # Pitch-shift: Progressive fray
    pitch_factor = [1.0, 0.98, 0.95][run - 1]
    vocal_resampled = resample(vocal, int(len(vocal) * pitch_factor))
    if len(vocal_resampled) < len(vocal):
        vocal_resampled = np.pad(
            vocal_resampled, (0, len(vocal) - len(vocal_resampled))
        )
    vocal = vocal_resampled[: len(vocal)]

    # Delays: Biting feedback
    delay_samples = int(0.3 * fs)
    feedback = 0.8
    delays = []
    for i in range(3):
        delayed = np.roll(vocal, i * delay_samples)
        delayed[: i * delay_samples] = 0
        delays.append(delayed * (feedback**i))

    reverbed = vocal + sum(delays)

    # Chaos: Gamma-distributed static
    chaos_factor = [2.5, 2.8, 3.0][run - 1]
    static = chaos_factor * np.random.gamma(2, 0.05, len(t))
    static = np.clip(
        static / np.max(static) if np.max(static) > 0 else static, -0.1, 0.1
    )
    reverbed += static

    # Apply Soft-Knee Compression (replaces hard clip)
    reverbed = soft_knee_compress(reverbed)

    # Lyrics Timestamps
    print("Lyrics drop at:")
    for time, line in lyrics:
        print(f"{time:.1f}s: {line}")

    # Progressive Insights
    insights = [
        "Low freq reveals hidden harmonics in the mud",
        "High feedback creates self-sustaining echo loops",
        "Chaos factor exposing the Glimpse's true character",
        "Glow plug distortion creating digital artifacts",
    ]
    print("\nTeardown Insights:")
    for i, insight in enumerate(insights[: run + 1], 1):
        print(f"{i}. {insight}")

    # Export WAV
    filename = f"sandstorm_run_{run:02d}.wav"
    wavfile.write(filename, fs, (reverbed * 32767).astype(np.int16))
    print(f"Etched: {filename} – {len(reverbed)/fs:.1f}s of refined dynamics.")

print(
    "\n🔧 Refinement Complete: Protocol operational, artifacts enhanced. Ready for next iteration."
)
