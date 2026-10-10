# 🚀 Smart Traffic Analytics — Deployment Guide

This guide provides **4 distinct deployment methods**, ranging from immediate zero-cost cloud hosting to production Docker containers.

---

## 📌 Summary of Deployment Options

| Method | Target Use Case | Cost | Effort | Setup Time |
| :--- | :--- | :--- | :--- | :--- |
| **1. Streamlit Community Cloud** | Live Public URL for evaluators, GitHub sharing | **Free** | Minimal | ~3 minutes |
| **2. University LAN / Local Host** | In-person viva & live classroom presentation | **Free** | Zero | Instant |
| **3. Docker & Docker Compose** | Industry containerized standard | **Free** | Moderate | ~5 minutes |
| **4. Cloud VM (AWS / Render / GCP)** | Full-stack cloud server with Kafka broker | Free Tier / Paid | Advanced | ~15 minutes |

---

## 🌟 Method 1: Streamlit Community Cloud (Recommended)

Streamlit Community Cloud lets you host the dashboard directly from your GitHub repository for free with a public `.streamlit.app` link.

### Step 1: Push Code to GitHub
1. Create a new GitHub repository (e.g., `smart-traffic-analytics`).
2. In your terminal, initialize and push:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Smart Traffic Analytics project"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/smart-traffic-analytics.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud
1. Navigate to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
2. Click **"New app"**.
3. Select your repository: `<YOUR_USERNAME>/smart-traffic-analytics`.
4. Configure the fields:
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
   - **App URL:** (Optional custom subdomain, e.g., `smart-traffic-ai`)
5. Click **"Deploy!"**.
6. Within 2 minutes, your project is live with an SSL HTTPS link!

---

## 🏫 Method 2: Local & University LAN Demo (Best for Viva)

If you are presenting in a college lab without internet or wanting evaluators to test on their devices over the same Wi-Fi:

### Step 1: Start the Dashboard with Network Binding
```powershell
cd E:\smarttraffic
.\.venv\Scripts\streamlit.exe run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
```

### Step 2: Share Network URL
Streamlit will display:
```
Local URL:   http://localhost:8501
Network URL: http://192.168.x.x:8501
```
Anyone connected to the same Wi-Fi network (professors, judges) can open `http://<YOUR_IP>:8501` on their laptop or mobile phone!

---

## 🐳 Method 3: Containerized Deployment (Docker Compose)

Deploy the entire microservice stack (Zookeeper + Apache Kafka + Streamlit Dashboard) in isolated Docker containers.

### Prerequisites
- Install **Docker Desktop** (from [docker.com](https://www.docker.com/products/docker-desktop/)).

### Step 1: Build and Launch
In the project root directory:
```bash
docker compose up --build -d
```

### Step 2: Verify Running Containers
```bash
docker compose ps
```
You will see:
- `traffic-zookeeper` (port 2181)
- `traffic-kafka` (port 9092)
- `traffic-dashboard` (port 8501)

### Step 3: Access
Open `http://localhost:8501` in any browser.

### To stop:
```bash
docker compose down
```

---

## ☁️ Method 4: Deploying on Cloud VM (AWS EC2 / Ubuntu)

For a persistent 24/7 cloud server:

### Step 1: Launch an Ubuntu 22.04 LTS instance (e.g. AWS EC2 `t3.medium`).
Ensure security group inbound rules allow:
- Port `22` (SSH)
- Port `8501` (Dashboard)

### Step 2: Server Setup Script
```bash
# Update and install Java 17 + Python 3
sudo apt update && sudo apt install -y openjdk-17-jre-headless python3-pip git

# Clone repository
git clone https://github.com/<YOUR_USERNAME>/smart-traffic-analytics.git
cd smart-traffic-analytics

# Install dependencies
pip install -r requirements.txt

# Run background dashboard via systemd or nohup
nohup streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > dashboard.log 2>&1 &
```

Access via: `http://<EC2_PUBLIC_IP>:8501`.
