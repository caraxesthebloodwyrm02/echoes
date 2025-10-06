# 🚀 Data Hub - Multi-Ecosystem Data Aggregator

A comprehensive data aggregation system that fetches and displays real-time information from Microsoft, Google, and X (Twitter) ecosystems.

## 🌟 Features

- **Multi-Ecosystem Support**: Aggregates data from Microsoft, Google, and X ecosystems
- **Real-time Data**: Fetches latest news, service status, trending topics, and updates
- **Web Dashboard**: Beautiful, responsive web interface for data visualization
- **Automated Scheduling**: Configurable data fetching intervals
- **Health Monitoring**: Tracks service status and generates alerts
- **API Endpoints**: RESTful API for programmatic access
- **Extensible Architecture**: Easy to add new data sources

## 🏗️ Architecture

```
data_hub/
├── data_hub.py              # Main entry point
├── fetchers/                # Ecosystem-specific fetchers
│   ├── microsoft_fetcher.py # Microsoft ecosystem data
│   ├── google_fetcher.py    # Google ecosystem data
│   └── x_fetcher.py         # X/Twitter ecosystem data
├── aggregator/              # Data processing and aggregation
│   ├── data_aggregator.py   # Main aggregation logic
│   └── scheduler.py         # Automated scheduling
├── web/                     # Web dashboard
│   └── dashboard.py         # Flask web interface
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

### 3. Run the Data Hub

```bash
python data_hub.py
```

The dashboard will be available at `http://localhost:5000`

## 📊 Data Sources

### Microsoft Ecosystem
- **Azure Service Status**: Real-time Azure service health
- **Microsoft Blog**: Latest Microsoft news and announcements
- **GitHub Microsoft**: Popular Microsoft repositories
- **Office 365 Status**: Office 365 service status
- **Microsoft Releases**: Latest product releases and updates

### Google Ecosystem
- **Google Cloud Status**: GCP service health monitoring
- **Google Blog**: Latest Google news and updates
- **Android Updates**: Android developer news and releases
- **Google Workspace**: Workspace service status
- **Google API Releases**: Latest API updates and features

### X (Twitter) Ecosystem
- **Trending Topics**: Real-time trending hashtags and topics
- **Twitter News**: Latest Twitter/X platform updates
- **Platform Updates**: X.com news and feature announcements
- **Popular Hashtags**: Technology and trending hashtags
- **Twitter Spaces**: Popular Twitter Spaces (when API available)

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Twitter API (Optional - for enhanced features)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret

# Google API (Optional)
GOOGLE_API_KEY=your_google_api_key

# Azure Configuration (Optional)
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret

# Data Hub Settings
FETCH_INTERVAL_MINUTES=60
DASHBOARD_PORT=5000
LOG_LEVEL=INFO
```

### Configuration Options

- **FETCH_INTERVAL_MINUTES**: How often to fetch new data (default: 60)
- **DASHBOARD_PORT**: Web dashboard port (default: 5000)
- **LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR)
- **DATA_RETENTION_DAYS**: How long to keep data files (default: 30)

## 🌐 Web Dashboard

The web dashboard provides:

- **Real-time Statistics**: Service counts, health status, article counts
- **Health Monitoring**: Visual indicators for service status
- **Latest Articles**: Recent news and updates from all ecosystems
- **Trending Topics**: Current trending hashtags and topics
- **Alerts**: System alerts and notifications
- **Auto-refresh**: Automatic data updates every 5 minutes

### Dashboard Features

- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Automatic data refresh
- **Interactive Elements**: Manual refresh button
- **Visual Indicators**: Color-coded health status
- **Searchable Content**: Easy navigation and filtering

## 🔌 API Endpoints

### RESTful API

- `GET /` - Main dashboard
- `GET /api/data` - Current aggregated data
- `GET /api/summary` - Data summary and statistics
- `GET /api/alerts` - Current system alerts
- `GET /api/refresh` - Trigger manual data refresh
- `GET /api/health` - System health check

### Example API Usage

```bash
# Get current data
curl http://localhost:5000/api/data

# Get data summary
curl http://localhost:5000/api/summary

# Trigger refresh
curl http://localhost:5000/api/refresh
```

## 📈 Data Format

### Aggregated Data Structure

```json
{
  "summary": {
    "total_services": 45,
    "healthy_services": 42,
    "total_articles": 25,
    "total_trending_topics": 15
  },
  "health_status": {
    "microsoft": "healthy",
    "google": "healthy",
    "x": "healthy"
  },
  "trending_topics": [...],
  "recent_articles": [...],
  "service_status": {...},
  "alerts": [...],
  "statistics": {...}
}
```

## 🔄 Automation

### Scheduled Fetching

The system supports multiple scheduling options:

```python
from aggregator.scheduler import DataScheduler

# Setup scheduler
scheduler = DataScheduler(data_hub)
scheduler.schedule_hourly_fetch()
scheduler.schedule_daily_fetch("09:00")
scheduler.schedule_custom_interval(30)  # minutes
scheduler.start_scheduler()
```

### Manual Fetching

```python
import asyncio
from data_hub import DataHub

async def main():
    hub = DataHub()
    data = await hub.fetch_all_ecosystems()
    print(data)

asyncio.run(main())
```

## 🔍 Monitoring and Logging

### Log Files

- **data_hub.log**: Main application logs
- **Console output**: Real-time logging

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

## 🛠️ Development

### Adding New Data Sources

1. Create a new fetcher in `fetchers/`
2. Add configuration in `config.py`
3. Update the aggregator in `aggregator/data_aggregator.py`
4. Add dashboard display in `web/dashboard.py`

### Extending the Dashboard

The dashboard uses Flask and can be easily extended:

```python
# Add new route
@app.route('/api/custom')
def custom_endpoint():
    return jsonify({'custom': 'data'})

# Add new page
@app.route('/custom')
def custom_page():
    return render_template('custom.html')
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Rate Limits**: Increase fetch intervals in configuration
3. **Port Conflicts**: Change DASHBOARD_PORT in .env
4. **Missing Data**: Check API keys and internet connectivity

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python data_hub.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in data_hub.log
- Open an issue on GitHub

---

**Built with ❤️ for the developer community**
