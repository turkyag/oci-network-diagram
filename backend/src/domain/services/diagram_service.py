from __future__ import annotations

from dataclasses import asdict

from src.domain.entities.topology import Topology
from src.domain.services.route_analyzer import RouteAnalyzer
from src.domain.services.diagram_builders import (
    edge, build_vcns, build_subnets, build_externals, build_gateways,
    build_drgs, build_route_tables, build_load_balancers, build_compartments,
    ZONE_EXT_Y, ZONE_BND_Y, ZONE_DRG_Y,
)


class DiagramService:
    """Converts a Topology into a 5-zone flow-aware React Flow diagram."""

    def __init__(self) -> None:
        self._analyzer = RouteAnalyzer()

    def generate(self, topology: Topology) -> dict:
        analysis = self._analyzer.analyze(topology)
        emap = self._analyzer._build_entity_map(topology)
        nodes: list[dict] = []
        edges: list[dict] = []

        vp = build_vcns(topology, nodes)
        build_subnets(topology, nodes, vp, analysis)
        build_gateways(topology, nodes, edges, vp, analysis)
        build_drgs(topology, nodes, edges, vp, analysis)
        build_route_tables(topology, nodes, edges, vp, analysis, emap)
        build_load_balancers(topology, nodes, edges, vp)
        self._build_lpgs(topology, nodes, edges, vp)
        self._build_connectivity(topology, nodes, edges, vp)
        self._build_firewalls(topology, nodes, edges, vp)
        # Build externals AFTER gateways/connectivity so they align above them
        build_externals(topology, nodes, vp)
        self._build_external_edges(topology, nodes, edges)
        # Build compartments LAST — they wrap VCNs as background containers
        build_compartments(topology, nodes, vp)

        return {
            "nodes": nodes,
            "edges": edges,
            "warnings": [asdict(w) for w in analysis.warnings],
        }

    # ── LPG nodes ──────────────────────────────────────────────────────

    def _build_lpgs(self, topo, nodes, edges, vp):
        lpg_map = {l.ocid: l for l in topo.local_peering_gateways}
        seen: set[tuple[str, str]] = set()
        for lpg in topo.local_peering_gateways:
            p = vp.get(lpg.vcn_id)
            if not p:
                continue
            nodes.append({"id": lpg.ocid, "type": "lpg",
                "position": {"x": p["x"] + p["width"] + 30, "y": p["y"] + 40},
                "data": {"label": lpg.display_name, "resource_id": lpg.ocid,
                    "resource_type": "lpg",
                    "properties": {"peer_id": lpg.peer_id, "peering_status": lpg.peering_status}}})
            if not lpg.peer_id or lpg.peer_id not in lpg_map:
                continue
            pair = tuple(sorted([lpg.ocid, lpg.peer_id]))
            if pair in seen:
                continue
            seen.add(pair)
            edges.append(edge(f"edge-lpg-{pair[0]}-{pair[1]}", pair[0], pair[1],
                              "LPG Peering", "#6366f1", animated=True, bidirectional=True))

    # ── Connectivity (CPE, IPSec, CrossConnect, VirtualCircuit) ────────

    def _build_connectivity(self, topo, nodes, edges, vp):
        bx = min((p["x"] for p in vp.values()), default=150)
        ext_ids = {n["id"] for n in nodes if n["type"] == "external"}

        for i, cpe in enumerate(topo.cpes):
            nodes.append({"id": cpe.ocid, "type": "connectivity",
                "position": {"x": bx + i * 200, "y": ZONE_EXT_Y},
                "data": {"label": cpe.display_name, "resource_id": cpe.ocid,
                    "resource_type": "cpe", "properties": {"ip_address": cpe.ip_address}}})

        for i, ipsec in enumerate(topo.ipsec_connections):
            tunnels = [t for t in topo.ipsec_tunnels if t.ipsec_connection_id == ipsec.ocid]
            nodes.append({"id": ipsec.ocid, "type": "connectivity",
                "position": {"x": bx + i * 200 + 100, "y": ZONE_BND_Y},
                "data": {"label": ipsec.display_name, "resource_id": ipsec.ocid,
                    "resource_type": "ipsec_connection",
                    "properties": {"static_routes": ipsec.static_routes,
                        "tunnels": [{"name": t.display_name, "status": t.status, "vpn_ip": t.vpn_ip, "cpe_ip": t.cpe_ip, "routing": t.routing} for t in tunnels],
                        "tunnel_count": len(tunnels)}}})
            edges.append(edge(f"edge-ipsec-drg-{ipsec.ocid}", ipsec.ocid, ipsec.drg_id, "IPSec", "#ef4444", animated=True, bidirectional=True))
            if ipsec.cpe_id:
                edges.append(edge(f"edge-ipsec-cpe-{ipsec.ocid}", ipsec.ocid, ipsec.cpe_id, "CPE", "#ef4444", animated=True, bidirectional=True))
            if "external-on-premises" in ext_ids:
                edges.append(edge(f"edge-ipsec-onprem-{ipsec.ocid}", ipsec.ocid, "external-on-premises", "", "#ef4444", animated=True))

        rx = max((p["x"] + p["width"] for p in vp.values()), default=850) + 200
        for i, cc in enumerate(topo.cross_connects):
            nodes.append({"id": cc.ocid, "type": "connectivity",
                "position": {"x": rx + i * 200, "y": ZONE_BND_Y},
                "data": {"label": cc.display_name, "resource_id": cc.ocid,
                    "resource_type": "cross_connect",
                    "properties": {"location_name": cc.location_name, "lifecycle_state": cc.lifecycle_state}}})

        drg_ids = {d.ocid for d in topo.drgs}
        for i, vc in enumerate(topo.virtual_circuits):
            nodes.append({"id": vc.ocid, "type": "connectivity",
                "position": {"x": rx + i * 200, "y": ZONE_BND_Y + 60},
                "data": {"label": vc.display_name, "resource_id": vc.ocid,
                    "resource_type": "virtual_circuit",
                    "properties": {"bandwidth_shape_name": vc.bandwidth_shape_name,
                        "lifecycle_state": vc.lifecycle_state, "gateway_id": vc.gateway_id}}})
            # Link virtual circuit to its DRG if gateway_id points to one
            if vc.gateway_id and vc.gateway_id in drg_ids:
                edges.append(edge(f"edge-vc-drg-{vc.ocid}", vc.ocid, vc.gateway_id,
                                  "FastConnect", "#f59e0b", animated=True))

    # ── Firewall nodes ─────────────────────────────────────────────────

    def _build_firewalls(self, topo, nodes, edges, vp):
        for idx, fw in enumerate(topo.network_firewalls):
            p = vp.get(fw.vcn_id)
            if not p:
                continue
            nodes.append({"id": fw.ocid, "type": "firewall",
                "position": {"x": p["x"] + idx * 180, "y": p["y"] + p["height"] - 40},
                "data": {"label": fw.display_name, "resource_id": fw.ocid,
                    "resource_type": "network_firewall",
                    "properties": {"subnet_id": fw.subnet_id, "policy_id": fw.policy_id}}})
            edges.append(edge(f"edge-fw-{fw.ocid}", fw.ocid, fw.vcn_id, fw.display_name, "#f97316"))

    # ── External edges (gateway -> external) ───────────────────────────

    def _build_external_edges(self, topo, nodes, edges):
        ext_ids = {n["id"] for n in nodes if n["type"] == "external"}
        for gw in topo.service_gateways:
            if "external-oracle-services" in ext_ids:
                edges.append(edge(f"edge-gw-ext-{gw.ocid}", gw.ocid, "external-oracle-services", "SGW", "#8b5cf6"))
        for rpc in topo.remote_peering_connections:
            if "external-other-region" in ext_ids:
                edges.append(edge(f"edge-rpc-ext-{rpc.ocid}", rpc.ocid, "external-other-region", "RPC", "#7c3aed"))
