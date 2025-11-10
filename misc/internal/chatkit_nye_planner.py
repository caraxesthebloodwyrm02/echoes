"""
ChatKit.World - NYE 2025 Roundtrip Journey Planner
Art Nouveau Aesthetic: Flowing lines, organic shapes, floral motifs, soft elegance

A beautiful travel planning interface for NYE 2025 (Dec 31) → Jan 2, 2026 roundtrip
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from core.config import TravelStyle, DEFAULTS
from core.display_utils import PALETTE, safe_symbol
from core.exporter import export_text, export_json


@dataclass
class Destination:
    """Destination with Art Nouveau styling"""

    name: str
    country: str
    description: str
    vibe: str  # Art Nouveau aesthetic descriptor
    estimated_cost_usd: float
    flight_hours: int
    highlights: List[str]


class NYEJourneyPlanner:
    """
    Art Nouveau-inspired NYE 2025 journey planner
    Flowing, organic interface with decorative elegance
    """

    def __init__(
        self,
        departure_city: str = DEFAULTS["origin"],
        travel_style: TravelStyle = DEFAULTS["travel_style"],
        departure_date: Optional[datetime] = None,
        return_date: Optional[datetime] = None,
        use_unicode: bool = True,
    ):
        self.departure_city = departure_city
        self.travel_style = travel_style
        self.use_unicode = use_unicode
        self.departure_date = departure_date or datetime.fromisoformat(
            DEFAULTS["date_start"]
        )  # NYE
        self.return_date = return_date or datetime.fromisoformat(
            DEFAULTS["date_end"]
        )  # Jan 2
        self.trip_duration = (self.return_date - self.departure_date).days
        self.destinations = self._initialize_destinations()

    def _sym(self, symbol: str) -> str:
        """Return symbol or fallback '*' if Unicode disabled for this instance."""
        return symbol if self.use_unicode else "*"

    def _initialize_destinations(self) -> List[Destination]:
        """Initialize curated destinations with Art Nouveau descriptions"""
        destinations = [
            Destination(
                name="Bangkok, Thailand",
                country="Thailand",
                description="Ornate temples with golden spires, flowing Chao Phraya River, silk markets",
                vibe="Ornate & Mystical",
                estimated_cost_usd=1200,
                flight_hours=4,
                highlights=[
                    "Grand Palace (Art Nouveau-inspired Thai architecture)",
                    "Wat Arun (flowing riverside temple)",
                    "Floating markets (organic, natural beauty)",
                    "NYE celebrations at Silom district",
                ],
            ),
            Destination(
                name="Bali, Indonesia",
                country="Indonesia",
                description="Terraced rice paddies, ancient temples, tropical gardens with flowing water features",
                vibe="Serene & Botanical",
                estimated_cost_usd=1400,
                flight_hours=5,
                highlights=[
                    "Tegallalang Rice Terraces (organic curves)",
                    "Ubud Palace & Arts District",
                    "Tanah Lot Temple (flowing ocean backdrop)",
                    "NYE beach celebrations",
                ],
            ),
            Destination(
                name="Hanoi, Vietnam",
                country="Vietnam",
                description="Ancient architecture, Hoan Kiem Lake reflections, French colonial elegance",
                vibe="Historic & Refined",
                estimated_cost_usd=950,
                flight_hours=2.5,
                highlights=[
                    "Old Quarter (winding, organic streets)",
                    "Hoan Kiem Lake (serene reflections)",
                    "Temple of Literature (classical elegance)",
                    "NYE street celebrations & water puppetry",
                ],
            ),
        ]

        # Filter by travel style
        return self._filter_by_travel_style(destinations)

    def _filter_by_travel_style(
        self, destinations: List[Destination]
    ) -> List[Destination]:
        """Filter destinations based on travel style"""
        if self.travel_style == TravelStyle.BUDGET:
            # Sort by cost, prioritize cheaper options
            return sorted(destinations, key=lambda d: d.estimated_cost_usd)
        elif self.travel_style == TravelStyle.LUXURY:
            # Adjust costs upward for luxury experiences
            for dest in destinations:
                dest.estimated_cost_usd *= 1.5
            return sorted(
                destinations, key=lambda d: d.estimated_cost_usd, reverse=True
            )
        else:  # COMFORT
            return destinations

    def render_header(self) -> str:
        """Render Art Nouveau-style header with floral motifs"""
        palette = PALETTE
        header = f"""
{palette['accent']}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     {self._sym('✿')} ChatKit.World - NYE 2025 Journey Planner {self._sym('✿')}            ║
    ║                                                               ║
    ║     Flowing Lines • Organic Elegance • Decorative Beauty     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{palette['reset']}
        """
        return header

    def render_trip_details(self) -> str:
        """Render trip details with elegant formatting"""
        palette = PALETTE
        details = f"""
{palette['title']}
    ⟡ JOURNEY DETAILS ⟡
{palette['reset']}
    Departure:  {self.departure_date.strftime('%A, %B %d, %Y')} (NYE)
    Return:     {self.return_date.strftime('%A, %B %d, %Y')}
    Duration:   {self.trip_duration} days of elegant escape
    
{palette['text']}
    "Travel is the only thing you buy that makes you richer" {self._sym('✿')}
{palette['reset']}
        """
        return details

    def render_destination_card(self, dest: Destination, index: int) -> str:
        """Render individual destination with Art Nouveau styling"""
        palette = PALETTE
        card = f"""
{palette['accent']}
    ╭─ Option {index + 1}: {dest.name.upper()} {dest.vibe} ─╮
{palette['reset']}
{palette['title']}
    Country:        {dest.country}
    Flight Time:    {dest.flight_hours} hours from {self.departure_city}
    Est. Cost:      ${dest.estimated_cost_usd:,.0f} USD
    
    {self._sym('✿')} Aesthetic: {dest.description}
    
    {self._sym('✿')} Highlights:
{palette['reset']}
        """
        for highlight in dest.highlights:
            card += f"        • {highlight}\n"

        card += f"{palette['accent']}    ╰────────────────────────────────────────────────╯{palette['reset']}\n"
        return card

    def render_top_3_options(self) -> str:
        """Render the top 3 curated destination options"""
        palette = PALETTE
        output = self.render_header()
        output += self.render_trip_details()
        output += f"\n{palette['accent']}{self._sym('✿')} ─ CURATED DESTINATIONS FOR YOUR NYE ESCAPE ─ {self._sym('✿')}{palette['reset']}\n"

        for i, dest in enumerate(self.destinations[:3]):
            output += self.render_destination_card(dest, i)

        return output

    def calculate_daily_itinerary(self, destination: Destination) -> Dict:
        """Generate a 3-day NYE itinerary"""
        itinerary = {
            "destination": destination.name,
            "days": [
                {
                    "date": "Dec 31, 2025 (NYE)",
                    "theme": "Arrival & Evening Celebration",
                    "activities": [
                        "Arrive at destination (morning/afternoon)",
                        "Check into accommodation",
                        "Explore local evening markets/streets",
                        "NYE celebration (fireworks, street parties, cultural events)",
                        "Late night dining & celebration",
                    ],
                    "estimated_cost": "$150-200",
                },
                {
                    "date": "Jan 1, 2026 (Day 1)",
                    "theme": "Cultural Immersion",
                    "activities": [
                        "Morning: Rest & recovery",
                        "Midday: Visit primary cultural landmark",
                        "Afternoon: Local market exploration",
                        "Evening: Traditional cuisine dining",
                        "Night: Relaxation & reflection",
                    ],
                    "estimated_cost": "$100-150",
                },
                {
                    "date": "Jan 2, 2026 (Return)",
                    "theme": "Final Moments & Departure",
                    "activities": [
                        "Morning: Sunrise at scenic location",
                        "Late morning: Last-minute shopping/souvenirs",
                        "Afternoon: Depart for airport",
                        "Evening: Arrive home with memories",
                    ],
                    "estimated_cost": "$50-100",
                },
            ],
        }
        return itinerary

    def render_itinerary(self, destination: Destination) -> str:
        """Render the 3-day itinerary with Art Nouveau styling"""
        palette = PALETTE
        itinerary = self.calculate_daily_itinerary(destination)

        output = f"\n{palette['accent']}{self._sym('✿')} ─ {destination.name.upper()} ITINERARY ─ {self._sym('✿')}{palette['reset']}\n"

        for day in itinerary["days"]:
            output += f"\n{palette['title']}⟡ {day['date']} | {day['theme']}{palette['reset']}\n"
            for activity in day["activities"]:
                output += f"   {self._sym('✿')} {activity}\n"
            output += f"   {palette['text']}Estimated: {day['estimated_cost']}{palette['reset']}\n"

        return output

    def generate_full_plan(self) -> str:
        """Generate complete travel plan"""
        output = self.render_top_3_options()

        # Add sample itinerary for first destination
        output += self.render_itinerary(self.destinations[0])

        palette = PALETTE
        output += f"\n{palette['accent']}{self._sym('✿')} ─ QUICK SELECTION GUIDE ─ {self._sym('✿')}{palette['reset']}\n"
        output += """
    1. Bangkok (Thailand)
       → Best for: Urban energy, temples, nightlife
       → Budget: ~$1,200 USD
       → Vibe: Ornate & Mystical
    
    2. Bali (Indonesia)
       → Best for: Beach relaxation, nature, culture
       → Budget: ~$1,400 USD
       → Vibe: Serene & Botanical
    
    3. Hanoi (Vietnam)
       → Best for: History, authenticity, affordability
       → Budget: ~$950 USD
       → Vibe: Historic & Refined
        """

        return output

    def export_to_json(self, filename: str = "nye_journey_plan.json") -> str:
        """Export plan to JSON format for integration with other tools"""
        plan_data = {
            "trip_metadata": {
                "departure_date": self.departure_date.isoformat(),
                "return_date": self.return_date.isoformat(),
                "duration_days": self.trip_duration,
                "departure_city": self.departure_city,
                "travel_style": self.travel_style.value,
            },
            "destinations": [
                {
                    "name": dest.name,
                    "country": dest.country,
                    "description": dest.description,
                    "vibe": dest.vibe,
                    "estimated_cost_usd": dest.estimated_cost_usd,
                    "flight_hours": dest.flight_hours,
                    "highlights": dest.highlights,
                }
                for dest in self.destinations
            ],
        }

        export_json(plan_data, filename)

        return filename

    def export_to_html(self, filename: str = "nye_journey_plan.html") -> str:
        """Export plan to HTML with Art Nouveau styling"""
        html_content = (
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYE 2025 Journey Planner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #f5e6d3 0%, #e8d4c0 100%);
            color: #5a4a42;
            line-height: 1.8;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 50px;
            border-bottom: 3px solid #8b4513;
            padding-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            color: #8b4513;
            margin-bottom: 10px;
            font-style: italic;
        }
        
        .subtitle {
            color: #daa520;
            font-size: 1.2em;
            letter-spacing: 2px;
        }
        
        .trip-info {
            background: rgba(255, 228, 225, 0.7);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #daa520;
        }
        
        .destinations {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .destination-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-top: 4px solid #daa520;
            transition: transform 0.3s ease;
        }
        
        .destination-card:hover {
            transform: translateY(-5px);
        }
        
        .destination-card h3 {
            color: #8b4513;
            margin-bottom: 10px;
            font-size: 1.5em;
        }
        
        .vibe {
            color: #daa520;
            font-style: italic;
            margin-bottom: 15px;
        }
        
        .cost {
            font-size: 1.3em;
            color: #8b4513;
            font-weight: bold;
            margin: 15px 0;
        }
        
        .highlights {
            list-style: none;
            margin-top: 15px;
        }
        
        .highlights li {
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .highlights li:before {
            content: "✿";
            position: absolute;
            left: 0;
            color: #daa520;
        }
        
        footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #8b4513;
            color: #8b4513;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>NYE 2025 Journey Planner</h1>
            <p class="subtitle">Flowing Lines • Organic Elegance • Decorative Beauty</p>
        </header>
        
        <div class="trip-info">
            <p><strong>Departure:</strong> """
            + self.departure_date.strftime("%A, %B %d, %Y")
            + """</p>
            <p><strong>Return:</strong> """
            + self.return_date.strftime("%A, %B %d, %Y")
            + """</p>
            <p><strong>Duration:</strong> """
            + str(self.trip_duration)
            + """ days</p>
            <p><strong>Travel Style:</strong> """
            + self.travel_style.value.capitalize()
            + """</p>
        </div>
        
        <div class="destinations">
"""
        )

        for dest in self.destinations:
            html_content += f"""
            <div class="destination-card">
                <h3>{dest.name}</h3>
                <p class="vibe">{dest.vibe}</p>
                <p>{dest.description}</p>
                <div class="cost">${dest.estimated_cost_usd:,.0f} USD</div>
                <p><strong>Flight Time:</strong> {dest.flight_hours} hours from {self.departure_city}</p>
                <ul class="highlights">
"""
            for highlight in dest.highlights:
                html_content += f"                    <li>{highlight}</li>\n"

            html_content += """
                </ul>
            </div>
"""

        html_content += (
            """
        </div>
        
        <footer>
            <p>Plan generated on """
            + datetime.now().strftime("%B %d, %Y at %I:%M %p")
            + """</p>
            <p>"Travel is the only thing you buy that makes you richer"</p>
        </footer>
    </div>
</body>
</html>
"""
        )

        export_text(html_content, filename)

        return filename


def interactive_main():
    """Interactive CLI with destination selection"""
    print("\n" + "=" * 65)
    print("Welcome to ChatKit.World - NYE 2025 Journey Planner")
    print("=" * 65 + "\n")

    # Get user preferences
    print("Let's customize your journey!\n")

    departure_city = (
        input("Where are you departing from? (default: Dhaka): ").strip() or "Dhaka"
    )

    print("\nTravel Style:")
    print("  1. Budget (most affordable)")
    print("  2. Comfort (balanced)")
    print("  3. Luxury (premium experience)")
    style_choice = input("Choose your travel style (1-3, default: 2): ").strip() or "2"

    travel_styles = {
        "1": TravelStyle.BUDGET,
        "2": TravelStyle.COMFORT,
        "3": TravelStyle.LUXURY,
    }
    travel_style = travel_styles.get(style_choice, TravelStyle.COMFORT)

    use_unicode = (
        input("\nUse decorative symbols? (y/n, default: y): ").strip().lower() != "n"
    )

    # Create planner
    planner = NYEJourneyPlanner(
        departure_city=departure_city,
        travel_style=travel_style,
        use_unicode=use_unicode,
    )

    # Display options
    print("\n" + planner.render_top_3_options())

    # Destination selection
    print("\nWhich destination interests you?")
    for i, dest in enumerate(planner.destinations, 1):
        print(f"  {i}. {dest.name} (${dest.estimated_cost_usd:,.0f})")

    choice = input("\nEnter the number of your choice (1-3): ").strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(planner.destinations):
            selected = planner.destinations[idx]
            print("\n" + planner.render_itinerary(selected))
        else:
            print("Invalid selection. Showing first destination.")
            print("\n" + planner.render_itinerary(planner.destinations[0]))
    except ValueError:
        print("Invalid input. Showing first destination.")
        print("\n" + planner.render_itinerary(planner.destinations[0]))

    # Export options
    print("\n" + "=" * 65)
    print("Export your plan:")
    print("=" * 65)

    txt_file = "nye_journey_plan.txt"
    json_file = "nye_journey_plan.json"
    html_file = "nye_journey_plan.html"

    export_text(planner.generate_full_plan(), txt_file)
    print(f"✓ Text plan saved to: {txt_file}")

    planner.export_to_json(json_file)
    print(f"✓ JSON plan saved to: {json_file}")

    planner.export_to_html(html_file)
    print(f"✓ HTML plan saved to: {html_file}")

    print("\n" + "=" * 65)
    print("Your journey awaits! Safe travels!")
    print("=" * 65 + "\n")


def main():
    """Main execution"""
    planner = NYEJourneyPlanner()
    plan = planner.generate_full_plan()
    print(plan)

    # Save to multiple formats
    export_text(plan, "E:/Projects/Echoes/nye_journey_plan.txt")

    planner.export_to_json("E:/Projects/Echoes/nye_journey_plan.json")
    planner.export_to_html("E:/Projects/Echoes/nye_journey_plan.html")

    print("\n✿ Plans saved to: nye_journey_plan.txt, .json, and .html ✿\n")


if __name__ == "__main__":
    import sys

    # Run interactive mode if --interactive flag is provided
    if "--interactive" in sys.argv:
        interactive_main()
    else:
        main()
