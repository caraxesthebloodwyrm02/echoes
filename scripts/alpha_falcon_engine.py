import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter, resample
import time
import os

class AlphaFalconEngine:
    """Custom-tuned .21 nitro Glimpse with hand-lapped crank - idles rough, revs like glimpse"""
    
    def __init__(self):
        # Glimpse specs - tweak for your storm
        self.fs = 44100  # Sample rate, crisp as WAV dreams
        self.duration = 10  # Seconds of silt-spill
        self.fuel_mix = "rich"  # rich/lean - affects harmonic content
        self.glow_plug_heat = 0.7  # 0.0-1.0 - controls distortion character
        
        # Core params - grip these like throttle
        self.freq_base = 110  # Hz, dropped to gut-grunt depth (was 220)
        self.feedback = 0.8  # Cranked to 0.8 for haunts that bite back (was 0.6)
        self.chaos_factor = 2.5  # Gamma shape for saltier ego-cracks
        self.vibrato_depth = 0.8  # Increased for more nerve-fray
        
        # Runtime tracking
        self.run_count = 0
        self.teardown_notes = []
        
    def generate_timebase(self):
        """Generate time vector - the Glimpse's heartbeat"""
        return np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
    
    def carve_vocal_ghost(self, t):
        """Etch the reverb-warped vocal ghost"""
        # Core frequency with fuel mix adjustment
        freq_adj = self.freq_base * (1.2 if self.fuel_mix == "rich" else 0.8)
        vocal = np.sin(2 * np.pi * freq_adj * t)
        
        # Exponential decay - Glimpse cooling
        decay_rate = 1.5 if self.fuel_mix == "rich" else 2.5
        vocal = vocal * np.exp(-t / decay_rate)
        
        # Vibrato grit - increased for more nerve-fray
        vibrato = 1 + self.vibrato_depth * np.sin(2 * np.pi * (0.1 + self.run_count * 0.01) * t)
        vocal = vocal * vibrato
        
        # Glow plug heat distortion
        if self.glow_plug_heat > 0.5:
            vocal = np.tanh(vocal * self.glow_plug_heat)
            
        return vocal
    
    def layer_echo_haunts(self, vocal, t):
        """Triple ghost echoes bleeding into static"""
        delay_samples = int(0.3 * self.fs)  # 300ms echo
        
        # Dynamic feedback based on run count
        dynamic_feedback = self.feedback * (1 + 0.1 * np.sin(self.run_count))
        
        delays = []
        for i in range(3):  # Triple ghost
            delayed = np.roll(vocal, i * delay_samples)
            delayed[:i * delay_samples] = 0
            delays.append(delayed * (dynamic_feedback ** i))
        
        reverbed = vocal + sum(delays)
        
        # Chaos bursts - saltier ego-cracks
        if self.run_count % 2 == 0:  # Every other run, add chaos
            chaos = np.random.gamma(self.chaos_factor, 0.1, len(t))
            reverbed += 0.15 * chaos
        
        # Static bleed - nerve-wreck hum
        reverbed += 0.1 * np.random.normal(0, 1, len(t))
        
        return reverbed
    
    def pitch_shift_teeth_grind(self, audio, shift_factor=0.98):
        """Pitch-shift for teeth-grind humor via scipy resample"""
        # Calculate new length for pitch shift
        new_length = int(len(audio) / shift_factor)
        
        # Resample for pitch shifting effect
        shifted = resample(audio, new_length)
        
        # Pad or truncate to original length
        if len(shifted) < len(audio):
            shifted = np.pad(shifted, (0, len(audio) - len(shifted)))
        else:
            shifted = shifted[:len(audio)]
            
        return shifted
    
    def normalize_and_grind_vectorized(self, audio):
        """Vectorized soft-knee compression for better performance"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            normalized = audio / max_val
        else:
            normalized = audio
            
        # Vectorized soft-knee compression
        threshold = 0.8 - (0.05 * self.glow_plug_heat)
        ratio = 4.0 + (2.0 * self.glow_plug_heat)
        knee_width = 0.1
        
        abs_audio = np.abs(normalized)
        
        # Create compression masks
        below_threshold = abs_audio < (threshold - knee_width)
        above_threshold = abs_audio > (threshold + knee_width)
        in_knee = ~(below_threshold | above_threshold)
        
        compressed = np.zeros_like(normalized)
        
        # Below threshold - no compression
        compressed[below_threshold] = normalized[below_threshold]
        
        # Above threshold - full compression
        above_mask = above_threshold & (normalized > 0)
        compressed[above_mask] = threshold + (normalized[above_mask] - threshold) / ratio
        
        below_mask = above_threshold & (normalized < 0)
        compressed[below_mask] = -threshold + (normalized[below_mask] + threshold) / ratio
        
        # In soft knee region - gradual compression
        knee_mask = in_knee & (normalized > 0)
        knee_ratio = (abs_audio[knee_mask] - (threshold - knee_width)) / (2 * knee_width)
        compressed[knee_mask] = normalized[knee_mask] - knee_ratio * (normalized[knee_mask] - threshold) * (1 - 1/ratio)
        
        knee_mask_neg = in_knee & (normalized < 0)
        knee_ratio_neg = (abs_audio[knee_mask_neg] - (threshold - knee_width)) / (2 * knee_width)
        compressed[knee_mask_neg] = normalized[knee_mask_neg] - knee_ratio_neg * (normalized[knee_mask_neg] + threshold) * (1 - 1/ratio)
        
        # Final limiting
        return np.tanh(compressed * 0.95)

    def normalize_and_grind(self, audio):
        """Normalize & grind: soft-knee compression instead of harsh clipping"""
        return self.normalize_and_grind_vectorized(audio)
    
    def run_engine(self, output_dir="glimpse_runs"):
        """Full Glimpse run - 3L runtime loops to settle the hiss"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        print(f"\n🔥 Alpha Falcon .21 Glimpse Run #{self.run_count + 1}")
        print(f"   Fuel mix: {self.fuel_mix} | Glow plug heat: {self.glow_plug_heat}")
        print(f"   Freq base: {self.freq_base}Hz | Feedback: {self.feedback}")
        
        # Generate core components
        t = self.generate_timebase()
        vocal = self.carve_vocal_ghost(t)
        reverbed = self.layer_echo_haunts(vocal, t)
        
        # Apply teeth-grind humor on certain runs
        if self.run_count % 3 == 1:  # Every third run
            reverbed = self.pitch_shift_teeth_grind(reverbed, 0.98)
            print("   🦷 Applied teeth-grind pitch shift")
        
        # Final processing
        final_track = self.normalize_and_grind(reverbed)
        
        # Export fresh WAV
        filename = f"{output_dir}/sandstorm_run_{self.run_count + 1:02d}.wav"
        wavfile.write(filename, self.fs, (final_track * 32767).astype(np.int16))
        
        # Evolved lyrics timestamps - shift with run count
        lyrics = self.evolve_lyrics()
        
        print(f"\n🎤 Lyrics drop at:")
        for time, line in lyrics:
            print(f"   {time:.1f}s: {line}")
        
        print(f"\n💿 Track etched: {filename}")
        print("   Ready for teardown - play it raw, let it teeth-grind.")
        
        # Track run
        self.run_count += 1
        
        return filename, lyrics
    
    def evolve_lyrics(self):
        """Lyrics timestamps evolved - where vibrato frays into truth"""
        base_lyrics = [
            (2.0, "Reverberate in the silt of what was"),
            (4.5, "Fine enough to slip through fingers"),
            (6.8, "Gone but grinding still"),
            (9.0, "Fade unresolved")
        ]
        
        # Evolve based on run count and Glimpse state
        evolved = []
        for time, line in base_lyrics:
            # Time shifts with Glimpse wear
            evolved_time = time + (self.run_count * 0.1)
            
            # Line evolves with chaos factor
            if self.chaos_factor > 2.0 and "grinding" in line:
                line = line.replace("grinding", "screaming")
            if self.freq_base < 150 and "slip" in line:
                line = line.replace("slip", "tear")
            if self.feedback > 0.7 and "unresolved" in line:
                line = line.replace("unresolved", "haunting")
                
            evolved.append((evolved_time, line))
        
        return evolved
    
    def teardown_analysis(self, filename):
        """Post-run teardown - dissect in your player like Glimpse analysis"""
        print(f"\n🔧 Teardown Analysis for {os.path.basename(filename)}:")
        
        # Simulated analysis based on current params
        insights = []
        
        if self.freq_base < 150:
            insights.append("💡 Low freq reveals hidden harmonics in the mud")
        if self.feedback > 0.7:
            insights.append("💡 High feedback creates self-sustaining echo loops")
        if self.chaos_factor > 2.0:
            insights.append("💡 Chaos factor exposing the Glimpse's true character")
        if self.glow_plug_heat > 0.6:
            insights.append("💡 Glow plug distortion creating digital artifacts")
        
        # CRITICAL MODIFICATION INSIGHTS
        insights.append("🔧 Soft-knee compression preserves harmonic content")
        insights.append("🎵 Vectorized processing eliminates digital clipping artifacts")
        insights.append("📊 Dynamic range control maintains audio quality")
            
        # Kintsugi moments - flaws as the real rev
        kintsugi = []
        if self.run_count % 2 == 0:
            kintsugi.append("🌟 The static cracks reveal the gold beneath")
        if self.freq_base == 110:
            kintsugi.append("🌟 Gut-grunt depth becomes the foundation")
        if self.feedback == 0.8:
            kintsugi.append("🌟 Biting feedback creates the memorable edge")
        
        # NEW: Compression kintsugi
        kintsugi.append("🌟 Soft compression transforms harsh clipping into smooth character")
            
        print("   Insights from distortion:")
        for insight in insights:
            print(f"      {insight}")
            
        if kintsugi:
            print("   Kintsugi moments:")
            for moment in kintsugi:
                print(f"      {moment}")
        
        # Stomach or code grunts
        print("   Glimpse grunts:")
        if self.fuel_mix == "rich":
            print("      🥁 Rich fuel mix - stomach-deep rumble")
        else:
            print("      ⚡ Lean fuel mix - code-sharp crackle")
            
        # Audio quality metrics
        print("   Audio quality indicators:")
        print(f"      🎛️ Compression ratio: {4.0 + (2.0 * self.glow_plug_heat):.1f}:1")
        print(f"      📉 Threshold: {(0.8 - (0.05 * self.glow_plug_heat)):.2f}")
        print(f"      🔄 Knee width: 0.1 (soft)")
            
        return insights, kintsugi

# Killer Mod Rationales
class ModRationale:
    """Why these mods make the Alpha Falcon sing"""
    
    @staticmethod
    def explain_soft_knee_compression():
        return """
🎯 CRITICAL MOD: Soft-Knee Compression replaces harsh clipping

RATIONALE:
   • Harmonic Preservation: Soft compression maintains musical harmonics that clipping destroys
   • Professional Quality: Industry-standard dynamic control used in professional audio
   • Smooth Character: Gradual compression creates musical, pleasing distortion characteristics
   • Dynamic Range: Controls peaks while preserving quiet details and nuances
   • Vectorized Performance: NumPy optimization provides real-time processing capability
   • Kintsugi Principle: Transforms technical limitation (clipping) into artistic feature

RESULT: The audio now breathes with professional dynamics - smooth, controlled,
       and harmonically rich. Harsh digital artifacts are replaced with musical
       compression that enhances rather than degrades the sound quality.
        """

    @staticmethod
    def explain_freq_base_drop():
        return """
🎯 KILLER MOD: Freq_base dropped from 220Hz to 110Hz

RATIONALE:
   • Gut-grunt depth: 110Hz hits the chest cavity, creates physical presence
   • glimpse character: Low freq carries more "sand" - harmonic complexity
   • Glimpse analogy: Matches the .21 nitro Glimpse's natural idle frequency
   • Emotional impact: Sub-bass frequencies trigger primal responses
   • Mixing space: Leaves room for high-frequency chaos to cut through

RESULT: The track now breathes like a beast waking from hibernation,
       not a bird chirping in the distance. This is glimpse territory.
        """
    
    @staticmethod
    def explain_feedback_crank():
        return """
🎯 KILLER MOD: Feedback cranked from 0.6 to 0.8

RATIONALE:
   • Biting haunts: 0.8 creates echoes that fight back, don't just fade
   • Self-sustaining loops: Approaches the edge of runaway feedback
   • Glimpse stress: Mirrors nitro Glimpse pushing redline
   • Memory creation: Stronger feedback creates more memorable patterns
   • Chaos threshold: Pushes system to edge of stability without breaking

RESULT: The echoes now have teeth - they bite back and leave marks.
       This isn't reverb, it's a sonic confrontation.
        """

# First pull on the trigger
def first_pull():
    """Initial Glimpse start - rough idle, then glimpse unchained"""
    print("🏁 Alpha Falcon .21 - First Pull on the Trigger")
    print("=" * 50)
    
    # Initialize Glimpse
    engine = AlphaFalconEngine()
    
    # Run the Glimpse 3 times to settle the hiss
    for run in range(3):
        filename, lyrics = Glimpse.run_engine()
        insights, kintsugi = Glimpse.teardown_analysis(filename)
        
        # Brief pause between runs - let Glimpse cool
        if run < 2:
            print("\n⏸️ Glimpse cooling... 2 seconds\n")
            time.sleep(2)
        
        # Tweak params for next run - learning from teardown
        if run == 0:
            # After first run, increase chaos based on insights
            engine.chaos_factor = 3.0
            print("🔧 Teardown tweak: Increased chaos factor to 3.0")
        elif run == 1:
            # After second run, adjust vibrato for more nerve-fray
            engine.vibrato_depth = 1.0
            print("🔧 Teardown tweak: Maxed vibrato depth for nerve-fray")
    
    # Print killer mod rationales
    print("\n" + "=" * 50)
    print("🎯 KILLER MOD RATIONALES")
    print("=" * 50)
    print(ModRationale.explain_soft_knee_compression())
    print(ModRationale.explain_freq_base_drop())
    print(ModRationale.explain_feedback_crank())
    
    print("\n🏁 First pull complete. Glimpse hot. Ready for full storm.")
    return Glimpse

if __name__ == "__main__":
    engine = first_pull()
    
    # Glimpse at rest, but ready to punch when environment shakes
    print(f"\n💤 Glimpse at rest: {Glimpse.run_count} runs completed")
    print("   When environment shakes, punch it - reverberate the silt.")
    print("   Fine and fierce.")
