# miniDSP Tide16 Integration for Unfolded Circle Remote 3

[![GitHub release](https://img.shields.io/github/v/release/fattykidd/uc-minidsp-tide16?style=flat-square)](https://github.com/fattykidd/uc-minidsp-tide16/releases)
[![Docker Image Version](https://img.shields.io/docker/v/fattykidd/uc-minidsp-tide16?style=flat-square&logo=docker)](https://hub.docker.com/r/fattykidd/uc-minidsp-tide16)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

An official Unfolded Circle API integration driver that connects your **Unfolded Circle Remote 3** directly to a **miniDSP Tide16** audio processor over IP.

This driver exposes full control over input selection, volume, muting, preset switching, and status feedback straight to your Remote 3 interface and custom home automation workflows.

---

## Key Features

* **Bi-directional Status Sync:** Real-time updates for volume level, active input, mute state, and selected preset.
* **Input Switching:** Quick toggle across all supported Tide16 audio sources (Analog, Digital, HDMI, Streaming).
* **Preset Configuration:** Jump directly between your custom miniDSP presets/configurations.
* **Lightweight Containerization:** Pre-built Docker images optimized for minimal resource overhead (ARM64 & x86_64).
* **Auto-Discovery Ready:** Seamless integration with Unfolded Circle Web Configurator.

---

## Setup & Deployment

### Option 1: Docker Compose (Recommended)

Add the following service definition to your local `docker-compose.yml` stack:

```yaml
version: "3.8"

services:
  uc-minidsp-tide16:
    image: ghcr.io/fattykidd/uc-minidsp-tide16:latest
    container_name: uc-minidsp-tide16
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - TIDE16_IP=192.168.1.50   # Replace with your miniDSP Tide16 IP address
      - PORT=8080
      - LOG_LEVEL=INFO

```
### Option 2: Docker Cli
 ```bash
       docker run -d \
  --name uc-minidsp-tide16 \
  --restart unless-stopped \
  -p 8080:8080 \
  -e TIDE16_IP="192.168.1.50" \
  ghcr.io/fattykidd/uc-minidsp-tide16:latest

```
  Adding to Unfolded Circle Remote 3
1. Open your Unfolded Circle Web Configurator in your browser.

2. Navigate to Integrations -> Add Integration -> Driver URL / Custom Driver.

3. Enter your docker host IP and driver port:http://<YOUR_DOCKER_HOST_IP>:8080/driver.json
4. Follow the on-screen pairing steps to map your miniDSP entities to your UI pages and physical buttons.

