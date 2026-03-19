# OCI Network Explorer

Interactive network flow visualization for Oracle Cloud Infrastructure. Pulls real data from OCI and renders a diagram that shows how traffic flows — subnets, route tables, gateways, DRGs, peering, VPNs, and firewalls, all connected with directional flow edges.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- An OCI tenancy with API key access

### 1. Configure OCI Access

```bash
cp oci-config.example oci-config
```

Edit `oci-config` with your OCI credentials:

```ini
[DEFAULT]
user=ocid1.user.oc1..YOUR_USER_OCID
fingerprint=aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99
tenancy=ocid1.tenancy.oc1..YOUR_TENANCY_OCID
region=us-ashburn-1
key_file=/oci/key.pem
```

Place your OCI API signing key as `oci-key.pem` in the project root.

### 2. Start the App

```bash
cp .env.example .env
docker compose up -d
```

Or use the setup script:

```bash
./setup.sh
```

### 3. Sync Data from OCI

```bash
docker compose run --rm oci-sync sync.py --config-file /oci/config
```

To sync a specific compartment:

```bash
docker compose run --rm oci-sync sync.py --config-file /oci/config --compartment-id ocid1.compartment.oc1..xxxxx
```

### 4. Open the Explorer

Navigate to **http://localhost:3000**

## What You See

The diagram shows your OCI network as a flow visualization:

- **VCN** — large container with subnets nested inside
- **Subnets** — show CIDR, public/private status, and which route table controls them
- **Route Tables** — first-class nodes below the VCN, showing destination → target rules
- **Gateways** (IGW, NAT, SGW) — at the VCN boundary, connected via flow edges
- **DRG** — central connectivity hub with DRG route tables
- **Compartment** — wraps all resources in a boundary container

### Edges Show Traffic Flow

| Color | Traffic Type |
|-------|-------------|
| Green | Internet (via IGW) |
| Amber | NAT / FastConnect |
| Blue | DRG routing |
| Purple | Oracle Services (SGW) |
| Indigo | Peering (LPG / RPC) |
| Red | VPN / IPSec |
| Orange | Firewall-inspected |
| Gray | Subnet → Route Table link |

### Click Any Resource

Clicking a node:
- **Highlights the full traffic path** (subnet → route table → gateway)
- **Dims unrelated resources** to 15% opacity
- **Opens a detail panel** with: name, OCID, compartment, route rules, security list rules

### Security Overlay

Click the **Security** button in the toolbar to toggle security information on the detail panel.

## OCI Resources Supported

Networking, Routing, Security, Peering, VPN, FastConnect, Load Balancing, Firewalls, Public IPs — [full list in CLAUDE.md](CLAUDE.md).

## Architecture

| Service | Tech | Port |
|---------|------|------|
| Frontend | React, TypeScript, React Flow | 3000 |
| Backend | Python, FastAPI, SQLAlchemy | 8000 |
| Database | PostgreSQL 16 | 5432 |
| OCI Sync | Python, OCI SDK | CLI tool |

## Configuration

| File | Purpose |
|------|---------|
| `oci-config` | OCI API credentials (from `oci-config.example`) |
| `oci-key.pem` | OCI API signing key |
| `.env` | Database credentials (from `.env.example`) |

All credential files are gitignored.

## Stopping

```bash
docker compose down
```

To also remove the database:

```bash
docker compose down -v
```
