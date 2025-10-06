"""
Web Dashboard - Flask-based web interface for the Data Hub
"""

import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

logger = logging.getLogger(__name__)

class Dashboard:
    """Web dashboard for displaying data hub information"""
    
    def __init__(self, data_hub):
        self.app = Flask(__name__)
        CORS(self.app)
        self.data_hub = data_hub
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return self.render_dashboard()
        
        @self.app.route('/api/data')
        def api_data():
            """API endpoint for current data"""
            try:
                data = self.data_hub.get_latest_data()
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/summary')
        def api_summary():
            """API endpoint for data summary"""
            try:
                summary = self.data_hub.aggregator.get_data_summary()
                return jsonify(summary)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts')
        def api_alerts():
            """API endpoint for alerts"""
            try:
                alerts = self.data_hub.aggregator.get_alerts_summary()
                return jsonify(alerts)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/refresh')
        def api_refresh():
            """API endpoint to trigger data refresh"""
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                data = loop.run_until_complete(self.data_hub.fetch_all_ecosystems())
                loop.close()
                return jsonify({'status': 'success', 'timestamp': datetime.now().isoformat()})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health')
        def api_health():
            """API endpoint for health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
    
    def render_dashboard(self):
        """Render the main dashboard HTML"""
        try:
            latest_data = self.data_hub.get_latest_data()
            summary = self.data_hub.aggregator.get_data_summary()
            alerts = self.data_hub.aggregator.get_alerts_summary()
            
            return self.generate_html_dashboard(latest_data, summary, alerts)
        except Exception as e:
            logger.error(f"Error rendering dashboard: {str(e)}")
            return f"<h1>Error: {str(e)}</h1>"
    
    def generate_html_dashboard(self, data, summary, alerts):
        """Generate HTML dashboard"""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Hub Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f5f5f5;
                    color: #333;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                }}
                
                .header p {{
                    opacity: 0.9;
                    font-size: 1.1rem;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }}
                
                .stat-card {{
                    background: white;
                    padding: 1.5rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                
                .stat-card h3 {{
                    color: #667eea;
                    font-size: 2rem;
                    margin-bottom: 0.5rem;
                }}
                
                .stat-card p {{
                    color: #666;
                    font-size: 0.9rem;
                }}
                
                .section {{
                    background: white;
                    margin-bottom: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                
                .section-header {{
                    background: #f8f9fa;
                    padding: 1rem 1.5rem;
                    border-bottom: 1px solid #e9ecef;
                }}
                
                .section-header h2 {{
                    color: #333;
                    font-size: 1.5rem;
                }}
                
                .section-content {{
                    padding: 1.5rem;
                }}
                
                .health-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 0.5rem;
                }}
                
                .health-healthy {{ background: #28a745; }}
                .health-warning {{ background: #ffc107; }}
                .health-error {{ background: #dc3545; }}
                
                .alert {{
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-radius: 5px;
                    border-left: 4px solid;
                }}
                
                .alert-high {{
                    background: #f8d7da;
                    border-color: #dc3545;
                    color: #721c24;
                }}
                
                .alert-medium {{
                    background: #fff3cd;
                    border-color: #ffc107;
                    color: #856404;
                }}
                
                .refresh-btn {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 1rem;
                    transition: background 0.3s;
                }}
                
                .refresh-btn:hover {{
                    background: #5a6fd8;
                }}
                
                .loading {{
                    text-align: center;
                    padding: 2rem;
                    color: #666;
                }}
                
                .service-list {{
                    list-style: none;
                }}
                
                .service-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.75rem 0;
                    border-bottom: 1px solid #eee;
                }}
                
                .service-item:last-child {{
                    border-bottom: none;
                }}
                
                .article-list {{
                    list-style: none;
                }}
                
                .article-item {{
                    margin-bottom: 1rem;
                    padding: 1rem;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }}
                
                .article-item h4 {{
                    margin-bottom: 0.5rem;
                    color: #333;
                }}
                
                .article-item p {{
                    color: #666;
                    font-size: 0.9rem;
                    margin-bottom: 0.5rem;
                }}
                
                .article-item a {{
                    color: #667eea;
                    text-decoration: none;
                }}
                
                .article-item a:hover {{
                    text-decoration: underline;
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 1rem;
                    }}
                    
                    .header h1 {{
                        font-size: 2rem;
                    }}
                    
                    .stats-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Data Hub Dashboard</h1>
                <p>Real-time insights from Microsoft, Google, and X ecosystems</p>
            </div>
            
            <div class="container">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{summary.get('total_services', 0)}</h3>
                        <p>Total Services Monitored</p>
                    </div>
                    <div class="stat-card">
                        <h3>{summary.get('healthy_services', 0)}</h3>
                        <p>Healthy Services</p>
                    </div>
                    <div class="stat-card">
                        <h3>{summary.get('total_articles', 0)}</h3>
                        <p>Recent Articles</p>
                    </div>
                    <div class="stat-card">
                        <h3>{summary.get('total_trending_topics', 0)}</h3>
                        <p>Trending Topics</p>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <h2>🔄 Quick Actions</h2>
                    </div>
                    <div class="section-content">
                        <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
                        <span id="refresh-status"></span>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <h2>🚨 Alerts</h2>
                    </div>
                    <div class="section-content">
                        {self.render_alerts(alerts)}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <h2>📊 Ecosystem Health</h2>
                    </div>
                    <div class="section-content">
                        {self.render_health_status(data)}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <h2>📰 Latest Articles</h2>
                    </div>
                    <div class="section-content">
                        {self.render_articles(data)}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <h2>🔥 Trending Topics</h2>
                    </div>
                    <div class="section-content">
                        {self.render_trending_topics(data)}
                    </div>
                </div>
            </div>
            
            <script>
                function refreshData() {{
                    const statusEl = document.getElementById('refresh-status');
                    statusEl.textContent = 'Refreshing...';
                    
                    fetch('/api/refresh')
                        .then(response => response.json())
                        .then(data => {{
                            if (data.status === 'success') {{
                                statusEl.textContent = 'Data refreshed successfully!';
                                setTimeout(() => {{
                                    location.reload();
                                }}, 1000);
                            }} else {{
                                statusEl.textContent = 'Error: ' + data.error;
                            }}
                        }})
                        .catch(error => {{
                            statusEl.textContent = 'Error: ' + error.message;
                        }});
                }}
                
                // Auto-refresh every 5 minutes
                setInterval(() => {{
                    fetch('/api/data')
                        .then(response => response.json())
                        .then(data => {{
                            // Update UI with new data
                            console.log('Data updated:', new Date());
                        }});
                }}, 300000);
            </script>
        </body>
        </html>
        """
        return html
    
    def render_alerts(self, alerts):
        """Render alerts section"""
        if alerts.get('total_alerts', 0) == 0:
            return '<p>No active alerts</p>'
        
        html = ""
        for alert in alerts.get('latest_alerts', [])[:3]:
            severity_class = f"alert-{alert.get('severity', 'medium')}"
            html += f"""
            <div class="{severity_class}">
                <strong>{alert.get('type', 'Alert').replace('_', ' ').title()}:</strong>
                {alert.get('message', '')}
                <br><small>{alert.get('timestamp', '')}</small>
            </div>
            """
        return html
    
    def render_health_status(self, data):
        """Render health status section"""
        health_status = {}
        
        # Extract health status from data
        for ecosystem in ['microsoft', 'google', 'x']:
            if ecosystem in data:
                # Determine health based on available data
                health_status[ecosystem] = 'healthy'  # Default
        
        html = "<ul class='service-list'>"
        for ecosystem, status in health_status.items():
            indicator_class = f"health-{status}"
            html += f"""
            <li class="service-item">
                <span>
                    <span class="health-indicator {indicator_class}"></span>
                    {ecosystem.title()}
                </span>
                <span>{status.title()}</span>
            </li>
            """
        html += "</ul>"
        return html
    
    def render_articles(self, data):
        """Render articles section"""
        articles = []
        
        # Collect articles from all ecosystems
        for ecosystem in ['microsoft', 'google', 'x']:
            if ecosystem in data:
                eco_data = data[ecosystem]
                if isinstance(eco_data, dict):
                    # Extract articles based on ecosystem structure
                    pass
        
        if not articles:
            return '<p>No recent articles found</p>'
        
        html = "<ul class='article-list'>"
        for article in articles[:5]:
            html += f"""
            <li class="article-item">
                <h4>{article.get('title', 'No title')}</h4>
                <p>{article.get('summary', '')[:150]}...</p>
                <a href="{article.get('link', '#')}" target="_blank">Read more →</a>
            </li>
            """
        html += "</ul>"
        return html
    
    def render_trending_topics(self, data):
        """Render trending topics section"""
        topics = []
        
        # Extract trending topics from X/Twitter
        if 'x' in data and isinstance(data['x'], dict):
            x_data = data['x']
            if 'trending_topics' in x_data and isinstance(x_data['trending_topics'], dict):
                topics = x_data['trending_topics'].get('trending_topics', [])
        
        if not topics:
            return '<p>No trending topics found</p>'
        
        html = "<ul class='service-list'>"
        for topic in topics[:10]:
            topic_name = topic.get('hashtag', topic.get('topic', 'Unknown'))
            html += f"""
            <li class="service-item">
                <span>{topic_name}</span>
                <span>#{topic.get('rank', '')}</span>
            </li>
            """
        html += "</ul>"
        return html
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard"""
        logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def create_dashboard(data_hub, port=5000):
    """Create and run the dashboard"""
    dashboard = Dashboard(data_hub)
    dashboard.run(port=port)
