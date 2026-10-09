AirSense 🌬️A full-stack, ML-powered environmental monitoring platform for real-time air quality tracking, 24-hour pollutant forecasting, and spatial regulatory compliance.AirSense bridges the gap between raw meteorological data and actionable environmental insights. By seamlessly aggregating high-frequency timeseries data and geospatial enforcement records, the platform empowers citizens, health officials, and policymakers with predictive analytics and real-time visualization to mitigate localized air pollution effectively.✨ Key Features & Functionality🌍 Real-Time Environmental MonitoringInteractive Spatial Mapping: Renders active metropolitan monitoring stations (Delhi, Mumbai, Bengaluru, Chennai, Kolkata) with live pollutant indexing using Leaflet and React.Granular Pollutant Tracking: Captures and visualizes comprehensive 6-pollutant grid data (PM2.5, PM10, $\text{NO}_2$, $\text{SO}_2$, $\text{CO}$, $\text{O}_3$) updated hourly.🧠 Predictive Analytics24-Hour ML Forecasting: Utilizes an XGBoost model executing recursive roll-forward predictions based on autoregressive lag features ($t-1 \dots t-24$) to project tomorrow's air quality trends.Rolling Sub-Index Calculations: Automatically computes official CPCB (Central Pollution Control Board) sub-indices using in-memory 16-hour rolling averages.⚖️ Regulatory & Compliance TrackingSpatial Enforcement Alerts: Leverages PostGIS to cross-reference geographical coordinates with localized environmental regulatory actions (e.g., NGT, DPCC directives).Automated Data Backfilling: Robust Python ingestion pipelines capable of seamlessly hydrating TimescaleDB with 180-day historical data windows (21,600+ records) to train models on the fly.🛠️ Tech Stack & ArchitectureComponentTechnologyRationaleFrontendReact, Vite, Tailwind CSSVite provides ultra-fast HMR for development, while Tailwind ensures rapid, responsive UI composition for data-dense dashboards.Backend APIPython, FastAPI, UvicornFastAPI delivers high-performance asynchronous endpoint handling and automatic OpenAPI documentation validation.DatabaseTimescaleDB (PostgreSQL)Optimized specifically for high-frequency time-series telemetry and rolling aggregation queries.Spatial EnginePostGISEnables advanced geographic queries to tie pollutant data directly to spatial compliance zones.Machine LearningXGBoost, PandasProvides highly efficient gradient-boosted decision trees perfect for structured, tabular time-series forecasting.System Architecture FlowPlaintext[ External APIs (Open-Meteo / AQI) ]
           │
           ▼
[ Python Ingestion Pipeline (Cron/Sched) ] ─── (Transform & Rollups) ──┐
           │                                                           │
           ▼                                                           ▼
[ TimescaleDB (Time-Series Data) ] <───> [ PostGIS (Spatial Compliance) ]
           │
           ▼
[ FastAPI Backend (Data Access & XGBoost Inference Engine) ]
           │
           ▼
[ React / Vite Frontend (Interactive Maps & Recharts Visualizations) ]
⚙️ Prerequisites & Installation⚠️ Hackathon/Evaluation Note: Due to strict time constraints during development, the core application components (Backend and Frontend) are currently configured to run locally while the database is containerized. A complete multi-container Docker deployment architecture is planned for the immediate roadmap prior to public release.1. System RequirementsDocker Desktop (running and healthy)Python 3.10+Node.js 18+ & npmGit2. Clone & Configure EnvironmentsBashgit clone https://github.com/yourusername/AirSense.git
cd AirSense
Create the .env file based on the provided template:Bashcp .env.example .env
.env.example Format:Code snippet# Database Configuration
POSTGRES_DB=airquality_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secure_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
TZ=Asia/Kolkata
3. Spin Up the DatabaseBashdocker compose up -d timescaledb
4. Run the Data Ingestion PipelinesPopulate the database with historical data and compliance records:Bash# Seed 180 days of timeseries data for 5 major stations
python ingestion/pipeline.py 

# Seed spatial regulatory actions
python ingestion/seed_compliance.py
5. Launch the FastAPI BackendOpen a new terminal session in the project root:Bashpip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
6. Launch the React FrontendOpen another terminal session:Bashcd frontend
npm install
npm run dev
Navigate to http://localhost:5173 to interact with the platform.🚦 Usage & API DocumentationInteracting with the UIStation Selection: Click any geographic marker on the Leaflet map to set the active station context.Forecast Analysis: Scroll to the "24-Hour AQI Forecast" card to view the XGBoost projection curve for the selected city.Compliance Audit: View the bottom right panel for localized spatial regulatory infractions based on the selected region.Core API EndpointsGET /api/stationsRetrieves all active monitoring stations with their geographic coordinates.JSON[
  {
    "station_id": "bengaluru",
    "name": "Bengaluru Urban Monitoring Station",
    "lat": 12.9716,
    "lon": 77.5946
  },
  ...
]
GET /api/forecast?station_id={id}Executes the XGBoost inference engine to return 24 hours of predicted AQI data.Request: curl -s "[http://127.0.0.1:8000/api/forecast?station_id=chennai](http://127.0.0.1:8000/api/forecast?station_id=chennai)"Response:JSON{
  "station_id": "chennai",
  "forecast": [
    {"timestamp": "2026-10-10T01:00:00", "predicted_aqi": 62.4},
    {"timestamp": "2026-10-10T02:00:00", "predicted_aqi": 64.1}
  ]
}
🧠 Challenges Faced & Lessons LearnedMassive Docker Build Bottlenecks: Initially, installing ML dependencies (like XGBoost and FastAPI) pulled heavily unoptimized NVIDIA CUDA packages, resulting in 2GB+ image layers and 45-minute build times. Solution: We explicitly migrated the requirements.txt targets to CPU-only wheels for local inference, dropping the download footprint to ~200MB and cutting build time to under 3 minutes.Time-Series Feature Starvation: The XGBoost forecasting service relies on a continuous rolling window (24–48 hours) to generate autoregressive lag features. Early iterations failed silently with "Insufficient historical data" because of un-synced NULL values in the base aqi column. Solution: We engineered a resilient SQL COALESCE pipeline to sync calculated aqi_cpcb metrics with raw aqi columns, ensuring feature generation never starved the model.Spatial and Temporal Aggregation: Combining standard relational data with both heavy time-series aggregations (TimescaleDB) and geographic boundaries (PostGIS) created heavy initial query loads. Solution: We implemented composite B-Tree indexing on (time DESC, station_id) to ensure sub-millisecond retrieval of the latest monitoring payload.🔮 Future RoadmapShort-Term (Next 30 Days)Full Containerization: Complete the docker-compose.yml to package the React frontend and FastAPI backend into isolated, production-ready containers.CI/CD Integration: Implement GitHub Actions for automated unit testing (PyTest) and linting.Long-Term (Q1-Q2 Next Year)Public Cloud Deployment: Migrate the full-stack architecture to AWS/GCP for public consumption.Hardware Edge Integration: Transition from weather-API ingestion to direct WebSocket streaming from physical, low-cost IoT particulate matter sensors.Mobile Port: Wrap the frontend interface in React Native for accessible, on-the-go citizen monitoring.