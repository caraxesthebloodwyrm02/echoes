"""
NYE 2025 Trip Savings Calculator
Daily Routine for Funding Your Dream Journey

Calculate how much to save daily from today to fund your NYE 2025 roundtrip
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class SavingsRoutineCalculator:
    """
    Calculate daily savings needed for NYE 2025 trip
    Includes practical daily routines and money-saving strategies
    """

    def __init__(self):
        self.today = datetime.now()
        self.trip_start = datetime(2025, 12, 31)
        self.days_until_trip = (self.trip_start - self.today).days
        
        # Trip cost estimates (USD)
        self.trip_costs = {
            "Bangkok": {"flights": 400, "accommodation": 400, "meals": 200, "activities": 200, "misc": 200},
            "Bali": {"flights": 450, "accommodation": 450, "meals": 250, "activities": 250, "misc": 200},
            "Hanoi": {"flights": 300, "accommodation": 300, "meals": 150, "activities": 150, "misc": 150}
        }

    def calculate_total_cost(self, destination: str) -> float:
        """Calculate total trip cost for a destination"""
        if destination not in self.trip_costs:
            return 0
        return sum(self.trip_costs[destination].values())

    def calculate_daily_savings_needed(self, destination: str) -> Tuple[float, float]:
        """
        Calculate daily savings needed
        Returns: (daily_amount_usd, daily_amount_bdt)
        """
        total_cost = self.calculate_total_cost(destination)
        daily_usd = total_cost / self.days_until_trip
        daily_bdt = daily_usd * 110  # Approximate BDT/USD rate
        return daily_usd, daily_bdt

    def render_savings_summary(self) -> str:
        """Render savings summary for all destinations"""
        output = """
╔════════════════════════════════════════════════════════════════╗
║          NYE 2025 TRIP SAVINGS CALCULATOR                      ║
║          Fund Your Dream Journey Starting Today                ║
╚════════════════════════════════════════════════════════════════╝

"""
        output += f"Today's Date:        {self.today.strftime('%A, %B %d, %Y')}\n"
        output += f"Trip Start:          {self.trip_start.strftime('%A, %B %d, %Y')}\n"
        output += f"Days to Save:        {self.days_until_trip} days\n\n"

        output += "═" * 65 + "\n"
        output += "DESTINATION COMPARISON - DAILY SAVINGS REQUIRED\n"
        output += "═" * 65 + "\n\n"

        for destination in self.trip_costs.keys():
            total = self.calculate_total_cost(destination)
            daily_usd, daily_bdt = self.calculate_daily_savings_needed(destination)
            
            output += f"📍 {destination.upper()}\n"
            output += f"   Total Trip Cost:     ${total:,.2f} USD\n"
            output += f"   Daily Savings (USD): ${daily_usd:.2f}\n"
            output += f"   Daily Savings (BDT): ৳{daily_bdt:,.0f}\n"
            output += f"   Weekly Savings:      ${daily_usd * 7:.2f} USD\n"
            output += f"   Monthly Savings:     ${daily_usd * 30:.2f} USD\n\n"

        return output

    def generate_daily_routine(self, destination: str, daily_bdt: float) -> str:
        """Generate a practical daily savings routine"""
        output = f"""
╔════════════════════════════════════════════════════════════════╗
║     DAILY SAVINGS ROUTINE FOR {destination.upper()}                 
║     Target: ৳{daily_bdt:,.0f} per day                              
╚════════════════════════════════════════════════════════════════╝

MORNING ROUTINE (6:00 AM - 9:00 AM)
─────────────────────────────────────

1. MINDFUL AWAKENING (5 min)
   ✓ Set intention: "I'm saving for my NYE adventure"
   ✓ Visualize the destination (temples, beaches, streets)
   ✓ Mental commitment to today's savings goal

2. BREAKFAST OPTIMIZATION (30 min)
   ✓ Prepare home breakfast instead of eating out
   ✓ Savings: ৳150-200 (vs. ৳300-400 at café)
   ✓ Meal prep: Oatmeal, eggs, toast, tea
   → SAVINGS: ৳150-200

3. COMMUTE STRATEGY (30 min)
   ✓ Walk/cycle instead of rickshaw/taxi when possible
   ✓ Use public transport (bus) vs. private transport
   ✓ Savings: ৳50-100 daily
   → SAVINGS: ৳50-100

4. MORNING WORK SESSION (2 hours)
   ✓ Focus on high-income tasks (freelance, side gigs)
   ✓ Target: ৳300-500 additional income
   → INCOME BOOST: ৳300-500

MIDDAY ROUTINE (12:00 PM - 2:00 PM)
─────────────────────────────────────

5. LUNCH DISCIPLINE (1 hour)
   ✓ Pack lunch from home (rice, curry, vegetables)
   ✓ Avoid restaurant temptations
   ✓ Savings: ৳200-300 (vs. ৳400-600 outside)
   → SAVINGS: ৳200-300

6. SHOPPING AWARENESS (30 min)
   ✓ Avoid impulse purchases
   ✓ Use "24-hour rule" for non-essentials
   ✓ Redirect urge to spend → trip fund
   → SAVINGS: ৳100-200

7. SIDE INCOME OPPORTUNITY (1-2 hours)
   ✓ Freelance work (Upwork, Fiverr, local projects)
   ✓ Tutoring, content writing, design
   ✓ Target: ৳400-800 additional income
   → INCOME BOOST: ৳400-800

AFTERNOON ROUTINE (3:00 PM - 6:00 PM)
──────────────────────────────────────

8. ENTERTAINMENT SWAP (2 hours)
   ✓ Free activities: Parks, libraries, community events
   ✓ Skip paid entertainment (movies, cafés)
   ✓ Savings: ৳200-300
   → SAVINGS: ৳200-300

9. UTILITY OPTIMIZATION (30 min)
   ✓ Reduce electricity usage (AC, lights)
   ✓ Shorter showers, efficient water use
   ✓ Savings: ৳50-100
   → SAVINGS: ৳50-100

10. EVENING SNACK CONTROL (30 min)
    ✓ Prepare snacks at home (fruits, nuts, yogurt)
    ✓ Avoid street food and vending
    ✓ Savings: ৳100-150
    → SAVINGS: ৳100-150

EVENING ROUTINE (6:00 PM - 10:00 PM)
─────────────────────────────────────

11. DINNER EFFICIENCY (1 hour)
    ✓ Cook at home with family
    ✓ Batch cooking for next day
    ✓ Savings: ৳200-300
    → SAVINGS: ৳200-300

12. SIDE HUSTLE EVENING (1-2 hours)
    ✓ Online tutoring, freelance projects
    ✓ Content creation (YouTube, blogs)
    ✓ Target: ৳300-500 additional income
    → INCOME BOOST: ৳300-500

13. SAVINGS TRACKING (15 min)
    ✓ Log daily savings in spreadsheet
    ✓ Update trip fund balance
    ✓ Celebrate progress
    ✓ Visualize destination
    → ACCOUNTABILITY: Track & celebrate

14. MINDFUL REFLECTION (15 min)
    ✓ Journal about trip excitement
    ✓ Visualize NYE celebration
    ✓ Gratitude for savings progress
    ✓ Sleep well with purpose

NIGHT ROUTINE (10:00 PM - 11:00 PM)
────────────────────────────────────

15. BUDGET REVIEW (10 min)
    ✓ Quick check: Did I hit today's target?
    ✓ Plan tomorrow's strategy
    ✓ Adjust if needed

16. SLEEP OPTIMIZATION (50 min)
    ✓ No late-night snacking
    ✓ No impulse online shopping
    ✓ Prepare for next day's success

═══════════════════════════════════════════════════════════════════

DAILY SAVINGS BREAKDOWN
───────────────────────

Direct Savings (Reduced Spending):
  • Breakfast at home:        ৳150-200
  • Commute optimization:     ৳50-100
  • Lunch at home:            ৳200-300
  • Shopping discipline:      ৳100-200
  • Entertainment swap:       ৳200-300
  • Utilities optimization:   ৳50-100
  • Snack control:            ৳100-150
  • Dinner at home:           ৳200-300
  ────────────────────────────────────
  SUBTOTAL SAVINGS:           ৳1,050-1,650

Additional Income (Side Hustles):
  • Morning freelance:        ৳300-500
  • Midday projects:          ৳400-800
  • Evening tutoring:         ৳300-500
  ────────────────────────────────────
  SUBTOTAL INCOME:            ৳1,000-1,800

═══════════════════════════════════════════════════════════════════

TOTAL DAILY TARGET: ৳{daily_bdt:,.0f}

REALISTIC DAILY ACHIEVEMENT: ৳{daily_bdt * 0.8:,.0f} - ৳{daily_bdt * 1.2:,.0f}
(accounting for variations and unexpected expenses)

═══════════════════════════════════════════════════════════════════

WEEKLY MILESTONE CHECKLIST
──────────────────────────

Week 1:  ৳{daily_bdt * 7:,.0f} saved ✓
Week 2:  ৳{daily_bdt * 14:,.0f} saved ✓
Week 4:  ৳{daily_bdt * 28:,.0f} saved ✓
Month 1: ৳{daily_bdt * 30:,.0f} saved ✓

MONTHLY PROGRESS TRACKER
────────────────────────

October 2025:   ৳{daily_bdt * 31:,.0f} (31 days)
November 2025:  ৳{daily_bdt * 30:,.0f} (30 days)
December 2025:  ৳{daily_bdt * 31:,.0f} (31 days)

TOTAL BY NYE:   ৳{daily_bdt * self.days_until_trip:,.0f}

═══════════════════════════════════════════════════════════════════

PSYCHOLOGICAL STRATEGIES FOR SUCCESS
─────────────────────────────────────

1. VISUALIZATION
   ✓ Daily: Imagine yourself at the destination
   ✓ Feel the excitement, see the sights
   ✓ This strengthens commitment

2. ACCOUNTABILITY
   ✓ Share goal with friend/family
   ✓ Weekly check-ins
   ✓ Public commitment increases follow-through

3. REWARD SYSTEM
   ✓ Hit weekly target? Small reward (not money)
   ✓ Hit monthly target? Celebrate with family
   ✓ Positive reinforcement

4. OBSTACLE PLANNING
   ✓ Plan for unexpected expenses
   ✓ Build 10% buffer into savings
   ✓ Have backup income sources

5. COMMUNITY SUPPORT
   ✓ Find others saving for trips
   ✓ Share tips and encouragement
   ✓ Group accountability

═══════════════════════════════════════════════════════════════════

EMERGENCY FUND STRATEGY
───────────────────────

If you fall short:
  • Reduce trip duration (2 days instead of 3)
  • Choose budget destination (Hanoi vs. Bali)
  • Combine with travel rewards/credit card points
  • Negotiate group discounts
  • Travel during shoulder season (cheaper)

═══════════════════════════════════════════════════════════════════

FINAL MOTIVATION
────────────────

Remember: Every taka saved is a step closer to:
  ✓ Experiencing new cultures
  ✓ Creating unforgettable memories
  ✓ Celebrating NYE in a magical place
  ✓ Personal growth and adventure

You've got this! 🌍✈️🎉

═══════════════════════════════════════════════════════════════════
"""
        return output

    def generate_complete_savings_plan(self) -> str:
        """Generate complete savings plan for all destinations"""
        output = self.render_savings_summary()
        
        # Generate detailed routine for Bangkok (most popular)
        daily_usd, daily_bdt = self.calculate_daily_savings_needed("Bangkok")
        output += self.generate_daily_routine("Bangkok", daily_bdt)
        
        return output


def main():
    """Main execution"""
    calculator = SavingsRoutineCalculator()
    plan = calculator.generate_complete_savings_plan()
    print(plan)
    
    # Save to file
    with open("E:/Projects/Echoes/savings_routine_plan.txt", "w", encoding="utf-8") as f:
        f.write(plan)
    
    print("\n✓ Savings plan saved to: savings_routine_plan.txt\n")


if __name__ == "__main__":
    main()
