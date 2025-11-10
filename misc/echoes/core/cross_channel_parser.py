"""
Cross-Channel Signal Parsing with Smooth Flow and Balanced Sine
===============================================================

Implements parameterized signal processing across multiple channels/modalities
with smooth flow transitions and balanced sine wave processing for coherent
multimodal signal integration.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from scipy import signal
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignalParameters:
    """Parameters for signal processing across channels."""

    amplitude: float = 1.0
    frequency: float = 1.0
    phase: float = 0.0
    damping: float = 0.1
    noise_level: float = 0.05
    sampling_rate: int = 1000
    window_size: int = 256


@dataclass
class ChannelFlow:
    """Represents a signal flow in a processing channel."""

    channel_id: str
    modality: str
    signal_data: np.ndarray
    parameters: SignalParameters
    flow_state: Dict[str, Any]


class BalancedSineProcessor:
    """
    Processes signals using balanced sine wave transformations
    for coherent multimodal integration.
    """

    def __init__(self, base_frequency: float = 1.0, balance_factor: float = 0.5):
        self.base_frequency = base_frequency
        self.balance_factor = balance_factor  # 0-1, controls sine wave balance

    def generate_balanced_sine(
        self, time_points: np.ndarray, params: SignalParameters
    ) -> np.ndarray:
        """
        Generate a balanced sine wave with controlled harmonics.

        The balance factor controls the mix between fundamental and harmonic frequencies,
        creating smoother signal transitions.
        """
        # Fundamental frequency component
        fundamental = params.amplitude * np.sin(
            2 * np.pi * params.frequency * time_points + params.phase
        )

        # Harmonic components for richness
        harmonic1 = (params.amplitude * 0.3) * np.sin(
            2 * np.pi * (params.frequency * 2) * time_points + params.phase
        )
        harmonic2 = (params.amplitude * 0.1) * np.sin(
            2 * np.pi * (params.frequency * 3) * time_points + params.phase
        )

        # Balanced combination
        balanced_signal = self.balance_factor * fundamental + (
            1 - self.balance_factor
        ) * (harmonic1 + harmonic2)

        # Apply damping
        damping_envelope = np.exp(-params.damping * time_points)
        balanced_signal *= damping_envelope

        # Add controlled noise
        if params.noise_level > 0:
            noise = np.random.normal(0, params.noise_level, len(time_points))
            balanced_signal += noise

        return balanced_signal

    def smooth_flow_transition(
        self, signal1: np.ndarray, signal2: np.ndarray, transition_points: int = 100
    ) -> np.ndarray:
        """
        Create smooth transition between two signals using balanced sine modulation.
        """
        if len(signal1) == 0 or len(signal2) == 0:
            return np.concatenate([signal1, signal2])

        # Create smooth transition window using balanced sine
        transition_window = np.linspace(0, np.pi, transition_points)
        sine_weights = (np.sin(transition_window) + 1) / 2  # 0 to 1

        # Apply smooth transition
        transition_region = (1 - sine_weights) * signal1[
            -transition_points:
        ] + sine_weights * signal2[:transition_points]

        # Combine signals with smooth flow
        result = np.concatenate(
            [
                (
                    signal1[:-transition_points]
                    if len(signal1) > transition_points
                    else signal1
                ),
                transition_region,
                (
                    signal2[transition_points:]
                    if len(signal2) > transition_points
                    else signal2
                ),
            ]
        )

        return result


class CrossChannelParser:
    """
    Parameterized parser for processing signals across multiple channels/modalities
    with smooth flow and balanced sine integration.
    """

    def __init__(self):
        self.channels: Dict[str, ChannelFlow] = {}
        self.sine_processor = BalancedSineProcessor()
        self.flow_history: List[Dict[str, Any]] = []

    def add_channel(
        self, channel_id: str, modality: str, initial_data: np.ndarray = None
    ) -> ChannelFlow:
        """
        Add a new processing channel for a specific modality.
        """
        if initial_data is None:
            initial_data = np.array([])

        channel = ChannelFlow(
            channel_id=channel_id,
            modality=modality,
            signal_data=initial_data,
            parameters=SignalParameters(),
            flow_state={"active": True, "phase": 0.0, "energy": 0.0},
        )

        self.channels[channel_id] = channel
        logger.info(f"Added channel {channel_id} for modality {modality}")

        return channel

    def update_channel_parameters(self, channel_id: str, **param_updates) -> bool:
        """
        Update signal processing parameters for a channel.
        """
        if channel_id not in self.channels:
            logger.warning(f"Channel {channel_id} not found")
            return False

        channel = self.channels[channel_id]
        params = channel.parameters

        # Update parameters dynamically
        for param, value in param_updates.items():
            if hasattr(params, param):
                setattr(params, param, value)
                logger.debug(f"Updated {channel_id} {param} to {value}")

        return True

    def process_channel_signal(
        self, channel_id: str, new_data: np.ndarray, smooth_transition: bool = True
    ) -> np.ndarray:
        """
        Process new signal data for a channel with smooth flow integration.
        """
        if channel_id not in self.channels:
            logger.error(f"Channel {channel_id} not found")
            return new_data

        channel = self.channels[channel_id]

        # Generate time points for balanced sine processing
        time_points = np.linspace(
            0, len(new_data) / channel.parameters.sampling_rate, len(new_data)
        )

        # Apply balanced sine transformation
        processed_signal = self.sine_processor.generate_balanced_sine(
            time_points, channel.parameters
        )

        # Modulate with input data
        if len(new_data) > 0:
            # Normalize signals for coherent mixing
            if np.max(np.abs(new_data)) > 0:
                new_data_norm = new_data / np.max(np.abs(new_data))
            else:
                new_data_norm = new_data

            if np.max(np.abs(processed_signal)) > 0:
                processed_signal_norm = processed_signal / np.max(
                    np.abs(processed_signal)
                )
            else:
                processed_signal_norm = processed_signal

            # Balanced combination
            processed_signal = (
                self.sine_processor.balance_factor * new_data_norm
                + (1 - self.sine_processor.balance_factor) * processed_signal_norm
            )

        # Apply smooth flow transition if requested
        if smooth_transition and len(channel.signal_data) > 0:
            combined_signal = self.sine_processor.smooth_flow_transition(
                channel.signal_data, processed_signal
            )
        else:
            combined_signal = np.concatenate([channel.signal_data, processed_signal])

        # Update channel state
        channel.signal_data = combined_signal
        channel.flow_state["energy"] = np.mean(np.abs(combined_signal))
        channel.flow_state["phase"] += 0.1  # Incremental phase advance

        # Record flow event
        self._record_flow_event(
            channel_id,
            "signal_processed",
            {
                "data_points": len(new_data),
                "energy_level": channel.flow_state["energy"],
                "smooth_transition": smooth_transition,
            },
        )

        return combined_signal

    def cross_channel_fusion(
        self, channel_ids: List[str], fusion_method: str = "balanced_sine"
    ) -> np.ndarray:
        """
        Fuse signals from multiple channels using parameterized processing.
        """
        if not channel_ids:
            return np.array([])

        # Get signals from specified channels
        signals = []
        for channel_id in channel_ids:
            if channel_id in self.channels:
                signals.append(self.channels[channel_id].signal_data)

        if not signals:
            return np.array([])

        if fusion_method == "balanced_sine":
            return self._balanced_sine_fusion(signals)
        elif fusion_method == "phase_aligned":
            return self._phase_aligned_fusion(signals)
        elif fusion_method == "energy_weighted":
            return self._energy_weighted_fusion(signals)
        else:
            # Default to simple averaging
            return np.mean(signals, axis=0)

    def _balanced_sine_fusion(self, signals: List[np.ndarray]) -> np.ndarray:
        """Fuse signals using balanced sine wave modulation."""
        if len(signals) == 1:
            return signals[0]

        # Find maximum length for alignment
        max_len = max(len(s) for s in signals)

        # Pad signals to same length
        padded_signals = []
        for signal in signals:
            if len(signal) < max_len:
                padding = np.zeros(max_len - len(signal))
                padded_signals.append(np.concatenate([signal, padding]))
            else:
                padded_signals.append(signal)

        # Create balanced sine modulation for each signal
        time_points = np.linspace(0, max_len / 1000, max_len)
        modulations = []

        for i, signal in enumerate(padded_signals):
            # Different phase for each channel to create rich fusion
            phase_offset = (2 * np.pi * i) / len(signals)
            modulation = self.sine_processor.generate_balanced_sine(
                time_points,
                SignalParameters(frequency=1.0, phase=phase_offset, amplitude=0.5),
            )
            modulations.append(modulation)

        # Apply modulations and combine
        fused_signal = np.zeros(max_len)
        for signal, modulation in zip(padded_signals, modulations):
            fused_signal += signal * (modulation + 1)  # Ensure positive modulation

        # Normalize
        if np.max(np.abs(fused_signal)) > 0:
            fused_signal /= np.max(np.abs(fused_signal))

        return fused_signal

    def _phase_aligned_fusion(self, signals: List[np.ndarray]) -> np.ndarray:
        """Fuse signals with phase alignment for coherent integration."""
        if len(signals) == 1:
            return signals[0]

        # Align phases using cross-correlation
        aligned_signals = []

        # Use first signal as reference
        reference = signals[0]
        aligned_signals.append(reference)

        for signal in signals[1:]:
            # Compute cross-correlation for alignment
            correlation = signal.correlate(reference, signal, mode="full")
            max_corr_idx = np.argmax(np.abs(correlation))

            # Calculate lag
            lag = max_corr_idx - (len(reference) - 1)

            # Shift signal to align
            if lag > 0:
                aligned = np.concatenate([signal[lag:], np.zeros(lag)])
            elif lag < 0:
                aligned = np.concatenate([np.zeros(-lag), signal[:lag]])
            else:
                aligned = signal

            aligned_signals.append(aligned)

        # Combine aligned signals
        return np.mean(aligned_signals, axis=0)

    def _energy_weighted_fusion(self, signals: List[np.ndarray]) -> np.ndarray:
        """Fuse signals weighted by their energy levels."""
        if len(signals) == 1:
            return signals[0]

        # Calculate energy weights
        energies = [np.sum(signal**2) for signal in signals]
        total_energy = sum(energies)

        if total_energy == 0:
            return np.mean(signals, axis=0)

        weights = [energy / total_energy for energy in energies]

        # Find maximum length
        max_len = max(len(s) for s in signals)

        # Pad signals and apply weights
        weighted_signals = []
        for signal, weight in zip(signals, weights):
            if len(signal) < max_len:
                padded = np.concatenate([signal, np.zeros(max_len - len(signal))])
            else:
                padded = signal
            weighted_signals.append(padded * weight)

        return np.sum(weighted_signals, axis=0)

    def get_channel_status(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for a channel."""
        if channel_id not in self.channels:
            return None

        channel = self.channels[channel_id]
        return {
            "channel_id": channel_id,
            "modality": channel.modality,
            "signal_length": len(channel.signal_data),
            "energy_level": channel.flow_state.get("energy", 0.0),
            "phase": channel.flow_state.get("phase", 0.0),
            "parameters": {
                "amplitude": channel.parameters.amplitude,
                "frequency": channel.parameters.frequency,
                "phase": channel.parameters.phase,
                "damping": channel.parameters.damping,
                "noise_level": channel.parameters.noise_level,
            },
        }

    def get_flow_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent flow processing history."""
        return self.flow_history[-limit:] if self.flow_history else []

    def _record_flow_event(
        self, channel_id: str, event_type: str, details: Dict[str, Any]
    ):
        """Record a flow processing event."""
        event = {
            "timestamp": np.datetime64("now"),
            "channel_id": channel_id,
            "event_type": event_type,
            "details": details,
        }
        self.flow_history.append(event)

        # Keep history manageable
        if len(self.flow_history) > 1000:
            self.flow_history = self.flow_history[-500:]
