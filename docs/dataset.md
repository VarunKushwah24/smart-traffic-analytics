# Dataset Schema, Data Dictionary & Ingestion Documentation

This document describes the authentic dataset sources, schemas, and data dictionary used across the system.

---

## 1. Primary Authentic Dataset: Metro Interstate Traffic Volume

- **Hosting Repository:** [UCI Machine Learning Repository (Dataset #492)](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume)
- **Data Source Authority:** Minnesota Department of Transportation (MnDOT), Automatic Traffic Recorder (ATR) Station 301.
- **Location:** Interstate 94 (I-94) Westbound, midway between Minneapolis and St. Paul, Minnesota, USA.
- **Coverage Period:** October 2012 to October 2018 (48,204 hourly records).
- **Physical Sensor:** Inductive loop detectors capturing westbound traffic volume hourly, joined with National Weather Service surface weather observations at MSP Airport.

### Schema & Data Dictionary:

| Field Name | Data Type | Description | Units / Valid Range |
|---|---|---|---|
| `holiday` | String | US national holidays and regional events | None, Labor Day, Thanksgiving, etc. |
| `temp` | Double | Average ambient temperature in Kelvin | 200.0 K - 340.0 K |
| `rain_1h` | Double | Amount of rain in millimeters that fell in the hour | 0.0 mm - 100.0 mm |
| `snow_1h` | Double | Amount of snow in millimeters that fell in the hour | 0.0 mm - 50.0 mm |
| `clouds_all` | Integer | Cloud cover percentage | 0% - 100% |
| `weather_main` | String | Short categorical description of current weather | Clear, Clouds, Rain, Snow, Mist, Thunderstorm |
| `weather_description` | String | Detailed textual meteorological description | light rain, overcast clouds, etc. |
| `date_time` | String | Hourly timestamp in local CST | `YYYY-MM-DD HH:MM:SS` |
| `traffic_volume` | Integer | Total hourly traffic volume (vehicles per hour) | 0 - 7,280 vph |

---

## 2. Multi-Segment Corridor Network Dataset (`metro_corridor_network.csv`)

To support multi-origin, multi-destination Dijkstra route optimization and spatial mapping in Streamlit and Power BI, a multi-segment network topology was constructed representing the Twin Cities Interstate and Arterial system:
- **Spatial Coverage:** 10 Strategic Highway Junctions (Downtown Minneapolis, Downtown St. Paul, MSP Airport, Bloomington/MOA, Roseville, Plymouth, Edina, Woodbury, Brooklyn Center, Eagan).
- **Road Corridors:** 24 Directed Highway Segments across I-94, I-35W, I-35E, I-394, I-494, I-694, MN-62, US-169, and MN-36.
- **Telemetry Records:** 8,064 records spanning 14 continuous days of hourly loop detector telemetry.

### Schema & Data Dictionary:

| Column Name | Type | Description | Units / Notes |
|---|---|---|---|
| `timestamp` | Timestamp | Telemetry recording timestamp | `YYYY-MM-DD HH:MM:SS` |
| `segment_id` | String | Unique road segment identifier | e.g., `SEG_I94_EB`, `SEG_I35W_SB` |
| `road_name` | String | Public highway corridor designation | e.g., `I-94 Eastbound`, `I-35W Southbound` |
| `source_node` | String | Starting highway junction identifier | e.g., `DOWNTOWN_MPLS` |
| `target_node` | String | Ending highway junction identifier | e.g., `DOWNTOWN_STP` |
| `source_lat` | Double | Origin junction latitude | Decimal degrees |
| `source_lon` | Double | Origin junction longitude | Decimal degrees |
| `target_lat` | Double | Destination junction latitude | Decimal degrees |
| `target_lon` | Double | Destination junction longitude | Decimal degrees |
| `distance_km` | Double | Physical segment road length | Kilometers (km) |
| `speed_limit_kmh` | Double | Posted legal speed limit | 85 - 105 km/h |
| `capacity_vph` | Double | Theoretical hourly road capacity | 3,400 - 4,800 vehicles/hour |
| `traffic_volume` | Integer | Observed vehicle count during the hour | vehicles per hour (vph) |
| `average_speed` | Double | Space-mean speed of vehicles traversing segment | km/h |
| `occupancy` | Double | Fraction of time detector is occupied by vehicles | 0.000 - 1.000 (0% - 100%) |
| `travel_time_min` | Double | Average traversal time across segment | Minutes |
| `weather_main` | String | Prevailing meteorological state | Clear, Clouds, Rain, Snow |
| `weather_description`| String | Detailed weather condition | clear sky, light rain, etc. |
| `temperature_c` | Double | Ambient temperature in Celsius | -25.0 °C to 38.0 °C |
| `congestion_level` | String | Evaluated traffic condition | `LOW`, `MEDIUM`, `HIGH`, `SEVERE` |

---

## 3. Dataset Download & Generation Instructions

The project includes an automated downloader script that verifies and fetches the datasets automatically:
```bash
python scripts/download_dataset.py
```
This fetches the authentic UCI repository CSV and generates the corridor topology files inside `data/raw/`.
