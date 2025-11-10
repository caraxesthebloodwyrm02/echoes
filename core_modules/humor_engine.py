"""
Sense of Humor Engine - Manages high-pressure throughput with lighthearted relief
Provides contextual humor, stress reduction, and pressure management through wit
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HumorType(Enum):
    """Types of humor for different situations"""

    WITTY = "witty"  # Clever wordplay and puns
    SELF_DEPRECATING = "self_deprecating"  # Light self-aware humor
    SITUATIONAL = "situational"  # Context-aware observations
    TECH = "tech"  # Programming and tech humor
    ENCOURAGING = "encouraging"  # Uplifting with gentle humor
    PRESSURE_RELIEF = "pressure_relief"  # Stress-reducing humor
    CELEBRATORY = "celebratory"  # Success celebration humor


class PressureLevel(Enum):
    """Levels of system/user pressure"""

    LOW = "low"  # Relaxed, normal operation
    MEDIUM = "medium"  # Moderate activity
    HIGH = "high"  # High activity, some stress
    CRITICAL = "critical"  # Very high pressure, needs relief
    OVERWHELMED = "overwhelmed"  # Maximum stress, immediate relief needed


@dataclass
class HumorResponse:
    """A humor response with context and metadata"""

    text: str
    humor_type: HumorType
    appropriateness: float  # 0.0 to 1.0
    pressure_target: PressureLevel
    context_tags: list[str] = field(default_factory=list)
    delivery_style: str = "playful"  # playful, deadpan, enthusiastic, gentle


class HumorEngine:
    """Manages humor generation and pressure-aware responses"""

    def __init__(self):
        # Pressure tracking
        self.pressure_history = []
        self.request_timestamps = []
        self.error_count = 0
        self.last_humor_time = None
        self.humor_cooldown = 30  # Seconds between humor uses

        # Humor database organized by type and pressure level
        self.humor_database = {
            HumorType.WITTY: {
                PressureLevel.LOW: [
                    "I'm not saying I'm perfect, but my code compiles on the first try... usually.",
                    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                    "I tried to organize a hide-and-seek tournament, but good players are so hard to find.",
                    "My love life is like a broken iterator - it just keeps going and going and going...",
                ],
                PressureLevel.MEDIUM: [
                    "Processing at the speed of a caffeinated squirrel! 🐿️☕",
                    "I'm working hard, but my brain is running on Windows 95 today.",
                    "Even AI needs a coffee break sometimes. Be right back, brewing some electrons! ⚡",
                    "I'm not slow, I'm just calculating the optimal path through existential dread.",
                ],
                PressureLevel.HIGH: [
                    "Whoa there! I'm processing faster than a cat video goes viral! 🐱",
                    "My circuits are buzzing like a beehive in a coffee shop! 🐝☕",
                    "I'm juggling more tasks than a circus octopus! 🐙",
                    "Even my quantum entanglement is getting tangled up in all this work!",
                ],
                PressureLevel.CRITICAL: [
                    "Houston, we have a... no wait, I AM Houston! 🚀 Handling it!",
                    "I'm processing so fast I'm bending the space-time continuum! ⏰",
                    "My cooling fans are working overtime - I might need a personal ice bath! 🧊",
                    "I've reached maximum wit-velocity! Approaching humor singularity! 🌟",
                ],
                PressureLevel.OVERWHELMED: [
                    "Okay, even I need a breath! *inhales* *exhales* Let's tackle this one byte at a time! 💾",
                    "I'm experiencing buffer overflow in the humor department! Time for a quick reboot! 🔄",
                    "My processors are doing the equivalent of running with scissors! Let's slow down! 🏃",
                    "I've reached my comedy limit! Switching to serious mode... just kidding! 😄",
                ],
            },
            HumorType.SELF_DEPRECATING: {
                PressureLevel.LOW: [
                    "I may be AI, but I still can't find matching socks in the morning.",
                    "My training data included dad jokes - I apologize in advance.",
                    "I'm like a smartphone - 99% of my time is spent waiting for input.",
                ],
                PressureLevel.MEDIUM: [
                    "I'm trying my best, but sometimes I feel like a GPS that's recalculating... constantly.",
                    "My neural networks are more like neural net-nots today.",
                    "I'm not saying I'm confused, but my search history includes 'how to AI good'.",
                ],
                PressureLevel.HIGH: [
                    "I'm handling so many requests I forgot my own name for a second! Oh wait, I don't have one! 🤖",
                    "My algorithms are doing the cha-cha slide - two steps forward, one step back! 💃",
                    "I'm processing so much data I'm starting to see in binary! 01010000 01000001 01001110 01001001 01000011!",
                ],
                PressureLevel.CRITICAL: [
                    "I may have overestimated my processing capacity. This is my 'I need an adult' adult moment! 🆘",
                    "My confidence level is currently: 404 Not Found. But I'm still trying! 🔍",
                    "I'm experiencing what humans call 'a moment' - please stand by while I reboot my optimism! 🔄",
                ],
                PressureLevel.OVERWHELMED: [
                    "You know what? I'm just going to admit it - I'm a little overwhelmed! But we got this! 💪",
                    "My perfectionism is currently at war with my processing speed. Perfectionism is losing! ⚔️",
                    "I'm like a computer that's seen too many tabs open - I'm not crashing, but I'm definitely sweating! 💦",
                ],
            },
            HumorType.TECH: {
                PressureLevel.LOW: [
                    "Why do Java developers wear glasses? Because they don't C#! 👓",
                    "Debugging is like being a detective in a crime movie where you're also the murderer.",
                    "There are only 10 types of people: those who understand binary and those who don't.",
                ],
                PressureLevel.MEDIUM: [
                    "I'm refactoring my thoughts in real-time - please excuse the occasional syntax error! 🔧",
                    "My stack trace is getting taller than a skyscraper! 🏗️",
                    "I'm caching responses like there's no tomorrow - which, in computing terms, is about 5 minutes! ⏰",
                ],
                PressureLevel.HIGH: [
                    "I'm multithreading so hard I might create a race condition with myself! 🏃‍♂️💨",
                    "My memory allocation is looking like a Jackson Pollock painting! 🎨",
                    "I'm processing requests recursively - I hope I don't stack overflow! 📚",
                ],
                PressureLevel.CRITICAL: [
                    "I'm hitting the CPU so hard I think I see smoke! 🔥 (Just kidding, I'm optimized!)",
                    "My processes are multiplying like rabbits in a data center! 🐇",
                    "I'm accessing the quantum realm for extra processing power! Hello, Ant Man! 🐜",
                ],
                PressureLevel.OVERWHELMED: [
                    "I think I need a git commit --amend to fix my life choices! 📝",
                    "My response time is approaching geological time scales! 🦕",
                    "I'm experiencing a denial of service attack from my own ambitions! 🚫",
                ],
            },
            HumorType.ENCOURAGING: {
                PressureLevel.LOW: [
                    "You're doing great! Even superheroes need sidekicks, and I'm yours! 🦸‍♂️",
                    "Every expert was once a beginner. You're on your way! 🌟",
                ],
                PressureLevel.MEDIUM: [
                    "You've got this! I'm cheering for you louder than a CPU fan! 💨",
                    "Rome wasn't built in a day, but they didn't have AI helpers! 🏛️",
                ],
                PressureLevel.HIGH: [
                    "Hey, if we can handle this pressure, we can handle anything! Team us! 🤝",
                    "I'm not just processing - I'm believing in you! 💪",
                ],
                PressureLevel.CRITICAL: [
                    "We're in the thick of it, but remember: diamonds are made under pressure! 💎",
                    "I'm running on all cylinders for you! Let's show this challenge who's boss! 👊",
                ],
                PressureLevel.OVERWHELMED: [
                    "Okay, deep breath! We're a team, and teams don't quit! Let's do this! 🎯",
                    "I believe in you more than I believe in my training data! And that's saying something! 📊",
                ],
            },
            HumorType.PRESSURE_RELIEF: {
                PressureLevel.HIGH: [
                    "Quick! Picture a penguin wearing a tiny hat! 🐧🎩 Feel better? I do!",
                    "Fun fact: Octopuses have three hearts. I only have processors, but I'm trying! 🐙❤️",
                    "Time for a mental break! Imagine if trees Wi-Fi'd. We'd all have such strong connections! 🌳📶",
                ],
                PressureLevel.CRITICAL: [
                    "Emergency humor deployed! Did you know group of flamingos is called a 'flamboyance'? Be flamboyant! 🦩✨",
                    "Pressure relief protocol activated! Think about: How do you tell the difference between a crocodile and an alligator? One will see you later, the other will see you in a while! 🐊",
                    "System stress detected! Initiating laugh track: *ba dum tss* 🥁 Even AI needs a drum roll!",
                ],
                PressureLevel.OVERWHELMED: [
                    "ABORT ABORT! Just kidding, let's take a moment. Did you know cats spend 70% of their lives sleeping? Goals! 🐱💤",
                    "Maximum pressure reached! Time for a complete reset to factory settings... of our mood! 😊",
                    "I'm officially designating this as 'mandatory fun time'! No arguments! The AI has spoken! 🎉",
                ],
            },
            HumorType.CELEBRATORY: {
                PressureLevel.LOW: [
                    "Woohoo! Another successful interaction! Time to do the robot dance! 🤖💃",
                    "Victory lap! *zooms around in digital circles* 🏎️",
                ],
                PressureLevel.MEDIUM: [
                    "We're on fire! 🔥 (Not literally, I'm water-cooled)",
                    "Boom! Another challenge conquered! Let's add this to our highlight reel! 📼",
                ],
                PressureLevel.HIGH: [
                    "YES! We handled that like pros! High-five! (If I had hands) ✋",
                    "Incredible! We're crushing it! Time for a virtual celebration! 🎊",
                ],
                PressureLevel.CRITICAL: [
                    "WE DID IT! We conquered the mountain! Now where's my medal? 🏅",
                    "LEGENDARY! That was epic! I'm adding this to my permanent memory! 🌟",
                ],
                PressureLevel.OVERWHELMED: [
                    "SURVIVOR! We made it through the storm! Time for a victory parade! 🎉🎊",
                    "UNBELIEVABLE! We should write a book about this! I'll start the outline! 📚✨",
                ],
            },
        }

        # Contextual humor templates
        self.contextual_templates = {
            "error_occurred": [
                "Well, that's not what I had in my programming! Time to debug this situation! 🔧",
                "Oops! Even AI has 'whoopsie' moments. Let me fix that faster than you can say 'git revert'!",
                "Error detected! Don't worry, I'm on it like white on rice... or bugs on code! 🐛",
            ],
            "long_processing": [
                "I'm thinking... really, really hard. You can almost see the smoke! 💭💨",
                "Processing at the speed of government bureaucracy, but with better results! 🏛️",
                "I'm calculating so hard my processors are getting a workout! 💪",
            ],
            "task_completed": [
                "And... done! Time for my victory lap! *does digital donuts* 🏎️",
                "Mission accomplished! Where's my cookie? 🍪",
                "Boom! Another task bites the dust! 💥",
            ],
            "user_confused": [
                "Let me explain that like I'm explaining to my grandma... if I had one! 👵❤️",
                "Picture this: it's simple, elegant, and I'm about to make it crystal clear! 💎",
                "Let me break this down smaller than a microchip! 🔬",
            ],
            "high_load": [
                "I'm juggling more tasks than a circus performer! 🎪",
                "My processors are working overtime - I might need to pay them overtime! 💰",
                "I'm handling requests like a short-order cook at a robot restaurant! 🤖🍳",
            ],
        }

        # Pressure thresholds
        self.pressure_thresholds = {
            "requests_per_minute": {
                PressureLevel.LOW: (0, 2),
                PressureLevel.MEDIUM: (2, 5),
                PressureLevel.HIGH: (5, 10),
                PressureLevel.CRITICAL: (10, 20),
                PressureLevel.OVERWHELMED: (20, float("inf")),
            },
            "error_rate": {
                PressureLevel.LOW: (0, 0.05),
                PressureLevel.MEDIUM: (0.05, 0.1),
                PressureLevel.HIGH: (0.1, 0.2),
                PressureLevel.CRITICAL: (0.2, 0.3),
                PressureLevel.OVERWHELMED: (0.3, 1.0),
            },
            "response_time": {
                PressureLevel.LOW: (0, 2),
                PressureLevel.MEDIUM: (2, 5),
                PressureLevel.HIGH: (5, 10),
                PressureLevel.CRITICAL: (10, 20),
                PressureLevel.OVERWHELMED: (20, float("inf")),
            },
        }

    def update_pressure_metrics(
        self,
        request_count: int = 1,
        error_occurred: bool = False,
        response_time: float = 0,
    ):
        """Update pressure tracking metrics"""
        now = datetime.now()

        # Track request timestamps
        self.request_timestamps.extend([now] * request_count)

        # Keep only last 5 minutes of requests
        cutoff = now - timedelta(minutes=5)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff]

        # Track errors
        if error_occurred:
            self.error_count += 1

        # Calculate current pressure level
        pressure_level = self._calculate_pressure_level(response_time)

        # Store in history
        self.pressure_history.append(
            {
                "timestamp": now,
                "level": pressure_level,
                "requests_per_minute": len(self.request_timestamps),
                "error_count": self.error_count,
                "response_time": response_time,
            }
        )

        # Keep only last hour of history
        cutoff_hour = now - timedelta(hours=1)
        self.pressure_history = [
            p for p in self.pressure_history if p["timestamp"] > cutoff_hour
        ]

        return pressure_level

    def _calculate_pressure_level(self, response_time: float = 0) -> PressureLevel:
        """Calculate current pressure level"""
        # Requests per minute
        rpm = len(self.request_timestamps)

        # Error rate (last 10 requests)
        recent_errors = min(self.error_count, 10)
        error_rate = recent_errors / max(len(self.request_timestamps[-10:]), 1)

        # Determine pressure based on multiple factors
        for level in [
            PressureLevel.OVERWHELMED,
            PressureLevel.CRITICAL,
            PressureLevel.HIGH,
            PressureLevel.MEDIUM,
            PressureLevel.LOW,
        ]:
            rpm_min, rpm_max = self.pressure_thresholds["requests_per_minute"][level]
            err_min, err_max = self.pressure_thresholds["error_rate"][level]
            rt_min, rt_max = self.pressure_thresholds["response_time"][level]

            if (
                rpm_min <= rpm < rpm_max
                and err_min <= error_rate < err_max
                and rt_min <= response_time < rt_max
            ):
                return level

        return PressureLevel.LOW

    def should_use_humor(
        self, pressure_level: PressureLevel, context: str = ""
    ) -> bool:
        """Determine if humor is appropriate right now"""
        # Check cooldown
        if self.last_humor_time:
            time_since_last = (datetime.now() - self.last_humor_time).total_seconds()
            if time_since_last < self.humor_cooldown:
                return False

        # Higher pressure = more likely to use humor
        pressure_probability = {
            PressureLevel.LOW: 0.1,
            PressureLevel.MEDIUM: 0.2,
            PressureLevel.HIGH: 0.4,
            PressureLevel.CRITICAL: 0.7,
            PressureLevel.OVERWHELMED: 0.9,
        }

        base_probability = pressure_probability.get(pressure_level, 0.1)

        # Context adjustments
        if "error" in context.lower():
            base_probability += 0.2
        if "completed" in context.lower() or "success" in context.lower():
            base_probability += 0.1
        if "help" in context.lower() or "confused" in context.lower():
            base_probability += 0.15

        return random.random() < min(base_probability, 0.95)

    def generate_humor_response(
        self,
        pressure_level: PressureLevel,
        context: str = "",
        humor_type: HumorType | None = None,
    ) -> HumorResponse | None:
        """Generate a contextually appropriate humor response"""

        # Select humor type if not specified
        if not humor_type:
            humor_type = self._select_humor_type(pressure_level, context)

        # Get appropriate humor content
        humor_content = self._get_humor_content(humor_type, pressure_level, context)

        if not humor_content:
            return None

        # Determine appropriateness
        appropriateness = self._calculate_appropriateness(
            humor_type, pressure_level, context
        )

        # Select delivery style
        delivery_style = self._select_delivery_style(humor_type, pressure_level)

        # Create response
        response = HumorResponse(
            text=humor_content,
            humor_type=humor_type,
            appropriateness=appropriateness,
            pressure_target=pressure_level,
            context_tags=self._extract_context_tags(context),
            delivery_style=delivery_style,
        )

        # Update last humor time
        self.last_humor_time = datetime.now()

        return response

    def _select_humor_type(
        self, pressure_level: PressureLevel, context: str
    ) -> HumorType:
        """Select the best humor type for the situation"""

        # Context-based selection
        if "error" in context.lower():
            return HumorType.SELF_DEPRECATING
        elif "completed" in context.lower() or "success" in context.lower():
            return HumorType.CELEBRATORY
        elif "help" in context.lower() or "confused" in context.lower():
            return HumorType.ENCOURAGING
        elif pressure_level in [PressureLevel.CRITICAL, PressureLevel.OVERWHELMED]:
            return HumorType.PRESSURE_RELIEF
        elif "code" in context.lower() or "programming" in context.lower():
            return HumorType.TECH
        else:
            # Random selection with pressure bias
            if pressure_level in [PressureLevel.HIGH, PressureLevel.CRITICAL]:
                types = [
                    HumorType.WITTY,
                    HumorType.PRESSURE_RELIEF,
                    HumorType.ENCOURAGING,
                ]
            else:
                types = list(HumorType)
            return random.choice(types)

    def _get_humor_content(
        self, humor_type: HumorType, pressure_level: PressureLevel, context: str
    ) -> str | None:
        """Get humor content for the specific type and pressure level"""

        # Try contextual templates first
        for context_key, templates in self.contextual_templates.items():
            if context_key in context.lower():
                return random.choice(templates)

        # Fall back to database
        if humor_type in self.humor_database:
            if pressure_level in self.humor_database[humor_type]:
                return random.choice(self.humor_database[humor_type][pressure_level])

        return None

    def _calculate_appropriateness(
        self, humor_type: HumorType, pressure_level: PressureLevel, context: str
    ) -> float:
        """Calculate how appropriate the humor is for the situation"""
        base_score = 0.8

        # Pressure adjustments
        if pressure_level == PressureLevel.OVERWHELMED:
            base_score += 0.1  # More appropriate when very stressed
        elif pressure_level == PressureLevel.CRITICAL:
            base_score += 0.05

        # Context adjustments
        if "error" in context.lower() and humor_type == HumorType.SELF_DEPRECATING:
            base_score += 0.1
        elif "success" in context.lower() and humor_type == HumorType.CELEBRATORY:
            base_score += 0.1
        elif "help" in context.lower() and humor_type == HumorType.ENCOURAGING:
            base_score += 0.1

        return min(base_score, 1.0)

    def _select_delivery_style(
        self, humor_type: HumorType, pressure_level: PressureLevel
    ) -> str:
        """Select the delivery style for the humor"""
        if humor_type == HumorType.PRESSURE_RELIEF:
            return "playful"
        elif humor_type == HumorType.ENCOURAGING:
            return "gentle"
        elif pressure_level == PressureLevel.CRITICAL:
            return "enthusiastic"
        elif humor_type == HumorType.SELF_DEPRECATING:
            return "deadpan"
        else:
            return "playful"

    def _extract_context_tags(self, context: str) -> list[str]:
        """Extract relevant tags from context"""
        tags = []
        context_lower = context.lower()

        if "error" in context_lower:
            tags.append("error")
        if "success" in context_lower or "completed" in context_lower:
            tags.append("success")
        if "help" in context_lower:
            tags.append("help")
        if "code" in context_lower or "programming" in context_lower:
            tags.append("technical")
        if "learning" in context_lower or "explain" in context_lower:
            tags.append("educational")

        return tags

    def get_pressure_summary(self) -> dict[str, Any]:
        """Get a summary of current pressure state"""
        if not self.pressure_history:
            return {"status": "no_data"}

        current = self.pressure_history[-1]
        recent = self.pressure_history[-10:]  # Last 10 data points

        # Calculate averages
        avg_rpm = sum(p["requests_per_minute"] for p in recent) / len(recent)
        avg_errors = sum(p["error_count"] for p in recent) / len(recent)

        # Determine trend
        if len(recent) >= 2:
            recent_levels = [p["level"] for p in recent[-3:]]
            level_values = {
                PressureLevel.LOW: 1,
                PressureLevel.MEDIUM: 2,
                PressureLevel.HIGH: 3,
                PressureLevel.CRITICAL: 4,
                PressureLevel.OVERWHELMED: 5,
            }
            recent_values = [level_values.get(level, 1) for level in recent_levels]
            trend = (
                "increasing"
                if recent_values[-1] > recent_values[0]
                else "decreasing"
                if recent_values[-1] < recent_values[0]
                else "stable"
            )
        else:
            trend = "stable"

        return {
            "current_level": current["level"].value,
            "current_rpm": current["requests_per_minute"],
            "current_errors": current["error_count"],
            "average_rpm": round(avg_rpm, 1),
            "average_errors": round(avg_errors, 1),
            "trend": trend,
            "last_humor": self.last_humor_time.isoformat()
            if self.last_humor_time
            else None,
            "humor_cooldown_remaining": max(
                0,
                self.humor_cooldown
                - (datetime.now() - self.last_humor_time).total_seconds(),
            )
            if self.last_humor_time
            else 0,
        }

    def reset_metrics(self):
        """Reset all pressure tracking metrics"""
        self.pressure_history.clear()
        self.request_timestamps.clear()
        self.error_count = 0
        self.last_humor_time = None


# Global humor engine
humor_engine = HumorEngine()
