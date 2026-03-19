# OCI Network Flow Explorer

## What This Is

A network flow visualization tool for Oracle Cloud Infrastructure. It pulls real network data from OCI via the OCI SDK and renders an interactive diagram that answers: **"What is connected to what, and how does traffic flow?"**

This is a **read-only explorer** — not a designer or editor. Deploy it, sync OCI data with the `oci-sync` tool, and explore your network topology visually.

## How It Works

1. **oci-sync** tool connects to OCI using your API key, fetches all network resources, pushes to the database
2. **Backend** (FastAPI) serves the data, computes route analysis + diagram layout
3. **Frontend** (React + React Flow) renders the interactive network flow diagram

## Quick Start

```bash
# 1. Clone and configure
cp oci-config.example oci-config   # Edit with your OCI credentials
cp .env.example .env               # Edit DB password if needed
# Place your OCI API signing key as: oci-key.pem

# 2. Start
./setup.sh
# Or manually:
docker compose up -d

# 3. Sync data from OCI
docker compose run --rm oci-sync sync.py --config-file /oci/config

# 4. Open http://localhost:3000
```

## Architecture

```
oci-sync/       → Python CLI: connects to OCI SDK, fetches resources, pushes to API
backend/        → FastAPI + SQLAlchemy: REST API, route analysis engine, diagram layout
frontend/       → React + @xyflow/react: interactive network flow diagram
docker-compose  → PostgreSQL + Backend + Frontend + OCI Sync (tools profile)
```

**Design:** Domain-Driven Design. Entities are dataclasses, repos are ABCs, infrastructure is SQLAlchemy async.

## Diagram Layout (OKIT-inspired, flow-oriented)

The diagram uses a 5-zone vertical layout:

| Zone | Y | What |
|------|---|------|
| External | -250 | On-Prem, Oracle Services, Other Region |
| Boundary | -100 | IGW, NAT, SGW, IPSec, FastConnect |
| DRG Hub | 0 | DRG + DRG Route Tables |
| VCN | 180 | VCN container with subnets nested inside |
| Route Tables | below VCN | Route tables as first-class nodes |

Everything wrapped in a **Compartment** container.

## Core Design Rules

1. **Route tables are first-class visible objects** — not hidden. Each subnet visually connects to its route table, which connects to target gateways.
2. **Traffic flow is shown via edges**: Subnet → Route Table → Gateway (dashed, color-coded by type)
3. **DRG is the central connectivity hub** — large, prominent node with DRG route tables nearby
4. **Security is a toggleable overlay** — default shows topology and routing only
5. **Click highlighting**: Click any resource → entire traffic path highlights, everything else dims
6. **Detail panel** shows full context: name, OCID, compartment, route rules, security lists with rules, DRG attachments
7. **Compartment names** shown instead of OCIDs everywhere
8. **Public/Private subnets** correctly identified and color-coded

## Edge Colors (Traffic Type)

| Color | Meaning |
|-------|---------|
| Green (#22c55e) | Internet traffic (via IGW) |
| Amber (#f59e0b) | NAT / FastConnect |
| Blue (#3b82f6) | DRG routing |
| Purple (#8b5cf6) | Oracle Services (SGW) |
| Indigo (#6366f1) | Peering (LPG/RPC) |
| Red (#ef4444) | VPN / IPSec |
| Orange (#f97316) | Firewall |
| Gray (#64748b) | Subnet → Route Table link |

## OCI Resources Supported

**Networking:** VCN, Subnet (with public/private detection), IGW, NAT GW, Service GW, DHCP Options
**Routing:** Route Table, Route Rule, DRG, DRG Attachment (all types), DRG Route Table, DRG Route Rule, DRG Route Distribution
**Security:** Security List + Rules, NSG + Rules, Network Firewall
**Peering:** LPG, RPC
**VPN:** IPSec Connection + Tunnels, CPE
**FastConnect:** Cross-Connect, Virtual Circuit
**Load Balancing:** Load Balancer, Network Load Balancer
**Other:** Public IP, Compartment

## Route Analysis Engine

The backend includes a route analyzer that:
- Resolves each subnet's route table → target gateway chain
- Detects **blackhole routes** (target doesn't exist)
- Detects **missing route tables** (subnet references non-existent RT)
- Detects **overlapping CIDRs** within a VCN
- Flags subnets with **no default route**
- Results shown as warnings banner on the diagram

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/topologies` | List synced topologies |
| GET | `/api/topologies/{id}` | Full topology detail |
| GET | `/api/topologies/{id}/diagram` | React Flow nodes + edges + warnings |
| GET | `/api/topologies/{id}/analysis` | Route flows + warnings + relationship maps |
| POST | `/api/topologies` | Create (used by oci-sync) |
| POST | `/api/topologies/{id}/import` | Import resource data (used by oci-sync) |
| DELETE | `/api/topologies/{id}` | Delete |
| GET | `/health` | Health check |

## File Structure

```
backend/src/
├── domain/entities/       # Dataclass entities (28 types)
├── domain/services/       # DiagramService, RouteAnalyzer, diagram_builders
├── application/           # Use cases, DTOs
├── infrastructure/        # SQLAlchemy models, repository, DB connection
└── presentation/          # FastAPI routes

frontend/src/
├── components/nodes/      # 10 React Flow node types
├── components/            # Sidebar, DiagramCanvas, DetailPanel, Legend, etc.
├── hooks/                 # useTopology, useFlowHighlight, useZoomLevel
└── services/              # API client

oci-sync/
└── sync.py               # OCI SDK data puller
```

## Configuration

- `oci-config` — OCI SDK config file (from `oci-config.example`)
- `oci-key.pem` — OCI API signing key
- `.env` — Database credentials (from `.env.example`)
- All config files are gitignored. Only examples are committed.
