"""
Web-based OAuth2 login interface for Google, Microsoft, and X (Twitter)
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from auth.oauth_manager import OAuthManager

class AuthWebApp:
    """Web application for OAuth2 authentication"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
        self.oauth_manager = OAuthManager()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main page with login options"""
            return self.render_login_page()
        
        @self.app.route('/login/<provider>')
        def login(provider):
            """Initiate OAuth2 login for specific provider"""
            if not self.oauth_manager.is_configured(provider):
                return f"{provider.title()} OAuth not configured. Please check your .env file."
            
            redirect_uri = url_for('callback', provider=provider, _external=True)
            auth_url, state = self.oauth_manager.generate_auth_url(provider, redirect_uri)
            session['oauth_state'] = state
            return redirect(auth_url)
        
        @self.app.route('/callback/<provider>')
        def callback(provider):
            """Handle OAuth2 callback"""
            code = request.args.get('code')
            state = request.args.get('state')
            
            if not code or not state:
                return "Authorization failed. Missing code or state."
            
            try:
                # Exchange code for token
                redirect_uri = url_for('callback', provider=provider, _external=True)
                token_data = self.oauth_manager.exchange_code_for_token(
                    provider, code, state, redirect_uri
                )
                
                # Get user info
                access_token = token_data.get('access_token')
                user_info = self.oauth_manager.get_user_info(provider, access_token)
                
                # Store user session
                session['user'] = user_info
                session['access_token'] = access_token
                session['refresh_token'] = token_data.get('refresh_token')
                session['provider'] = provider
                session['login_time'] = datetime.now().isoformat()
                
                # Save user profile
                self.save_user_profile(user_info, provider, token_data)
                
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                return f"Authentication failed: {str(e)}"
        
        @self.app.route('/dashboard')
        def dashboard():
            """User dashboard after login"""
            if 'user' not in session:
                return redirect(url_for('index'))
            
            return self.render_dashboard()
        
        @self.app.route('/logout')
        def logout():
            """Logout user"""
            session.clear()
            return redirect(url_for('index'))
        
        @self.app.route('/api/user')
        def api_user():
            """API endpoint for current user info"""
            if 'user' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            return jsonify({
                'user': session['user'],
                'provider': session.get('provider'),
                'login_time': session.get('login_time')
            })
        
        @self.app.route('/api/personalized-data')
        def api_personalized_data():
            """API endpoint for personalized data based on user"""
            if 'user' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            provider = session.get('provider')
            user_data = self.get_personalized_data(provider, session['user'])
            
            return jsonify(user_data)
    
    def render_login_page(self):
        """Render the login page"""
        providers = {
            'google': {
                'name': 'Google',
                'color': '#4285F4',
                'icon': '🔍',
                'description': 'Sign in with your Google account'
            },
            'microsoft': {
                'name': 'Microsoft',
                'color': '#0078D4',
                'icon': '🪟',
                'description': 'Sign in with your Microsoft account'
            },
            'twitter': {
                'name': 'X (Twitter)',
                'color': '#1DA1F2',
                'icon': '🐦',
                'description': 'Sign in with your X/Twitter account'
            }
        }
        
        # Check which providers are configured
        configured_providers = {
            key: value for key, value in providers.items()
            if self.oauth_manager.is_configured(key)
        }
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Hub - OAuth Login</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #333;
                }}
                
                .login-container {{
                    background: white;
                    padding: 3rem;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 400px;
                    width: 90%;
                }}
                
                .logo {{
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }}
                
                h1 {{
                    color: #333;
                    margin-bottom: 0.5rem;
                }}
                
                .subtitle {{
                    color: #666;
                    margin-bottom: 2rem;
                }}
                
                .provider-buttons {{
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }}
                
                .provider-btn {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.75rem;
                    padding: 1rem 1.5rem;
                    border: none;
                    border-radius: 10px;
                    font-size: 1rem;
                    font-weight: 500;
                    cursor: pointer;
                    text-decoration: none;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                
                .provider-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                
                .google-btn {{
                    background: #4285F4;
                    color: white;
                }}
                
                .microsoft-btn {{
                    background: #0078D4;
                    color: white;
                }}
                
                .twitter-btn {{
                    background: #1DA1F2;
                    color: white;
                }}
                
                .warning {{
                    background: #fff3cd;
                    color: #856404;
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                    border-left: 4px solid #ffc107;
                }}
                
                .info {{
                    background: #d1ecf1;
                    color: #0c5460;
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                    border-left: 4px solid #17a2b8;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">🔐</div>
                <h1>Data Hub Login</h1>
                <p class="subtitle">Connect your accounts for personalized data</p>
                
                {''.join(f'''
                <div class="info">
                    <strong>{providers[p]['name']} OAuth</strong><br>
                    {providers[p]['description']}
                </div>
                <a href="/login/{p}" class="provider-btn {p}-btn">
                    <span>{providers[p]['icon']}</span>
                    <span>Continue with {providers[p]['name']}</span>
                </a>
                ''' for p in configured_providers)}
                
                {''.join(f'''
                <div class="warning">
                    <strong>{providers[p]['name']} not configured</strong><br>
                    Add {p.upper()}_CLIENT_ID and {p.upper()}_CLIENT_SECRET to .env
                </div>
                ''' for p in providers if p not in configured_providers)}
            </div>
        </body>
        </html>
        """
        return html
    
    def render_dashboard(self):
        """Render the user dashboard"""
        user = session['user']
        provider = session['provider']
        
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
                    padding: 1.5rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }}
                
                .user-card {{
                    background: white;
                    padding: 2rem;
                    border-radius: 15px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 2rem;
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                }}
                
                .user-avatar {{
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: #667eea;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    color: white;
                }}
                
                .user-info h2 {{
                    margin-bottom: 0.5rem;
                }}
                
                .user-info p {{
                    color: #666;
                }}
                
                .logout-btn {{
                    margin-left: auto;
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 5px;
                    cursor: pointer;
                    text-decoration: none;
                }}
                
                .data-section {{
                    background: white;
                    padding: 2rem;
                    border-radius: 15px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                .loading {{
                    text-align: center;
                    padding: 2rem;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Hub Dashboard</h1>
                <p>Welcome to your personalized data hub</p>
            </div>
            
            <div class="container">
                <div class="user-card">
                    <div class="user-avatar">
                        {user.get('name', 'User')[0].upper()}
                    </div>
                    <div class="user-info">
                        <h2>{user.get('name', 'Unknown User')}</h2>
                        <p>Connected via {provider.title()} • {user.get('email', 'No email')}</p>
                    </div>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
                
                <div class="data-section">
                    <h3>Your Personalized Data</h3>
                    <div id="personalized-data" class="loading">
                        Loading your personalized data...
                    </div>
                </div>
            </div>
            
            <script>
                // Load personalized data
                fetch('/api/personalized-data')
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('personalized-data').innerHTML = `
                            <pre>${{JSON.stringify(data, null, 2)}}</pre>
                        `;
                    }})
                    .catch(error => {{
                        document.getElementById('personalized-data').innerHTML = 
                            'Error loading data: ' + error.message;
                    }});
            </script>
        </body>
        </html>
        """
        return html
    
    def save_user_profile(self, user_info: dict, provider: str, token_data: dict):
        """Save user profile to file"""
        os.makedirs('data/users', exist_ok=True)
        
        user_profile = {
            'user_info': user_info,
            'provider': provider,
            'tokens': {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type')
            },
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        }
        
        user_id = user_info.get('id', 'unknown')
        filename = f'data/users/{provider}_{user_id}.json'
        
        with open(filename, 'w') as f:
            json.dump(user_profile, f, indent=2)
    
    def get_personalized_data(self, provider: str, user_info: dict) -> dict:
        """Get personalized data based on user profile"""
        # This would integrate with actual APIs using user tokens
        # For now, return sample personalized data
        
        user_id = user_info.get('id', 'unknown')
        user_name = user_info.get('name', 'User')
        
        return {
            'user_id': user_id,
            'user_name': user_name,
            'provider': provider,
            'personalized_feeds': {
                'microsoft': {
                    'azure_alerts': [],
                    'microsoft_teams_updates': [],
                    'outlook_integrations': []
                },
                'google': {
                    'gmail_alerts': [],
                    'google_workspace_updates': [],
                    'calendar_integrations': []
                },
                'twitter': {
                    'timeline_updates': [],
                    'mentions': [],
                    'trending_in_network': []
                }
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def run(self, host='0.0.0.0', port=5001, debug=False):
        """Run the authentication web app"""
        print(f"Starting authentication web app on http://localhost:{port}")
        self.app.run(host=host, port=port, debug=debug)

def create_auth_app():
    """Create and return the authentication app"""
    return AuthWebApp()
