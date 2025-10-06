#!/usr/bin/env python3
"""
Master Hub - Complete orchestrator for all services
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Import all services
from research.ai_service import AIService
from finance.finance_service import FinanceService
from entertainment.media_service import MediaService
from insights.social_service import SocialService

class MasterHub:
    """Master orchestrator for all services"""
    
    def __init__(self):
        self.services = {
            'ai': AIService(),
            'finance': FinanceService(),
            'media': MediaService(),
            'social': SocialService()
        }
        self.accounts = {
            'google': 'irfankabir02@gmail.com',
            'microsoft': 'irfankabirprince@outlook.com',
            'spotify': 'irfankabir02@gmail.com'
        }
        self.setup_directories()
    
    def setup_directories(self):
        """Setup directory structure"""
        directories = [
            'data/ai',
            'data/finance',
            'data/media',
            'data/social',
            'data/dashboards',
            'data/secrets',
            'data/commerce',
            'data/music',
            'data/notifications'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def fetch_all_services(self) -> Dict[str, Any]:
        """Fetch data from all services"""
        return {
            'ai': self.services['ai'].get_ai_dashboard(),
            'finance': self.services['finance'].get_finance_dashboard(),
            'media': self.services['media'].get_media_dashboard(),
            'social': self.services['social'].get_social_dashboard(),
            'accounts': self.accounts,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }
    
    def generate_master_dashboard(self) -> str:
        """Generate comprehensive master dashboard"""
        data = self.fetch_all_services()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Master Hub - All Services Dashboard</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f0f0f; color: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); padding: 2rem; text-align: center; }}
                .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
                .service-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; }}
                .service-card {{ background: linear-gradient(145deg, #1a1a1a, #2a2a2a); border-radius: 15px; padding: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
                .service-header {{ display: flex; align-items: center; margin-bottom: 1.5rem; }}
                .service-icon {{ font-size: 2rem; margin-right: 1rem; }}
                .metric-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
                .metric {{ background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; text-align: center; }}
                .metric h3 {{ color: #667eea; font-size: 1.8rem; margin-bottom: 0.5rem; }}
                .notification {{ background: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; padding: 1rem; margin: 1rem 0; }}
                .accounts {{ background: rgba(40, 167, 69, 0.1); padding: 1rem; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Master Hub Dashboard</h1>
                <p>All Services • All Accounts • One Dashboard</p>
                <p>Generated: {data['timestamp']}</p>
            </div>
            
            <div class="container">
                <div class="accounts">
                    <h3>Connected Accounts</h3>
                    <p><strong>Google:</strong> {data['accounts']['google']}</p>
                    <p><strong>Microsoft:</strong> {data['accounts']['microsoft']}</p>
                    <p><strong>Spotify:</strong> {data['accounts']['spotify']}</p>
                </div>
                
                <div class="service-grid">
                    <!-- AI Service -->
                    <div class="service-card">
                        <div class="service-header">
                            <span class="service-icon">🤖</span>
                            <h2>AI Services</h2>
                        </div>
                        <div class="metric-grid">
                            <div class="metric">
                                <h3>{len(data['ai']['local_ai']['ollama']['models'])}</h3>
                                <p>Ollama Models</p>
                            </div>
                            <div class="metric">
                                <h3>{data['ai']['usage_stats']['total_queries']}</h3>
                                <p>Total Queries</p>
                            </div>
                        </div>
                        <div class="notification">
                            <strong>Latest:</strong> Groq API active with {data['ai']['usage_stats']['api_queries']} queries
                        </div>
                    </div>
                    
                    <!-- Finance Service -->
                    <div class="service-card">
                        <div class="service-header">
                            <span class="service-icon">💰</span>
                            <h2>Finance</h2>
                        </div>
                        <div class="metric-grid">
                            <div class="metric">
                                <h3>${data['finance']['personal_finance']['total_assets']:,.0f}</h3>
                                <p>Total Assets</p>
                            </div>
                            <div class="metric">
                                <h3>{data['finance']['commerce']['revenue']:,}</h3>
                                <p>Commerce Revenue</p>
                            </div>
                        </div>
                        <div class="notification">
                            <strong>Alert:</strong> AAPL target price reached
                        </div>
                    </div>
                    
                    <!-- Media Service -->
                    <div class="service-card">
                        <div class="service-header">
                            <span class="service-icon">🎵</span>
                            <h2>Media</h2>
                        </div>
                        <div class="metric-grid">
                            <div class="metric">
                                <h3>${data['media']['total_monetization']['monthly_total']}</h3>
                                <p>Monthly Revenue</p>
                            </div>
                            <div class="metric">
                                <h3>{data['media']['youtube']['channel_stats']['subscribers']:,}</h3>
                                <p>YouTube Subscribers</p>
                            </div>
                        </div>
                        <div class="notification">
                            <strong>Insight:</strong> New role model song added
                        </div>
                    </div>
                    
                    <!-- Social Service -->
                    <div class="service-card">
                        <div class="service-header">
                            <span class="service-icon">👥</span>
                            <h2>Social</h2>
                        </div>
                        <div class="metric-grid">
                            <div class="metric">
                                <h3>{data['social']['user_driven_insights']['sentiment_analysis']['confidence']*100:.0f}%</h3>
                                <p>Sentiment Accuracy</p>
                            </div>
                            <div class="metric">
                                <h3>{data['social']['engagement_summary']['total_interactions']:,}</h3>
                                <p>Total Interactions</p>
                            </div>
                        </div>
                        <div class="notification">
                            <strong>Trending:</strong> AI adoption insights from Reddit
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        os.makedirs('data/dashboards', exist_ok=True)
        with open('data/dashboards/master_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        return html
    
    def run_cli(self):
        """Run CLI interface"""
        print("=" * 80)
        print("    MASTER HUB v2.0")
        print("    Complete Service Orchestrator")
        print("=" * 80)
        
        data = self.fetch_all_services()
        
        print("\nServices Overview:")
        print(f"  AI Services: {len(data['ai']['local_ai']['ollama']['models'])} models active")
        print(f"  Finance: ${data['finance']['personal_finance']['total_assets']:,.0f} total assets")
        print(f"  Media: ${data['media']['total_monetization']['monthly_total']} monthly revenue")
        print(f"  Social: {data['social']['engagement_summary']['total_interactions']:,} interactions")
        
        print(f"\nDashboard generated: data/dashboards/master_dashboard.html")
        print(f"Full data saved: data/master_data.json")
        
        print("\nMaster Hub is ready!")
        print("   Use individual services or run unified_hub.py for web interface")
{{ ... }}

        # Save full data
        with open('data/master_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main function"""
    hub = MasterHub()
    hub.run_cli()

if __name__ == "__main__":
    main()
