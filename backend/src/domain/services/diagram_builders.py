from __future__ import annotations

from src.domain.entities.topology import Topology
from src.domain.services.route_analyzer import AnalysisResult

ZONE_EXT_Y, ZONE_BND_Y, ZONE_DRG_Y, ZONE_VCN_Y = -250, -100, 0, 180
VCN_W, VCN_GAP, VCN_X0 = 700, 200, 150
SUB_X, SUB_Y0, SUB_W, SUB_H, SUB_GAP = 30, 60, 640, 50, 15
VCN_HDR, VCN_PAD = 55, 20

FLOW_COLORS = {"IGW": "#22c55e", "NAT": "#f59e0b", "DRG": "#3b82f6",
                "SGW": "#8b5cf6", "LPG": "#6366f1"}


_COMP_MAP: dict[str, dict] = {}

def _set_comp_map(topo) -> None:
    """Initialize compartment name lookup from topology metadata."""
    global _COMP_MAP
    _COMP_MAP = {}
    if topo.metadata_json and isinstance(topo.metadata_json, dict):
        _COMP_MAP = topo.metadata_json.get("compartment_map", {})

def _comp_name(comp_id: str) -> str:
    if not comp_id:
        return ""
    meta = _COMP_MAP.get(comp_id, {})
    if meta.get("name"):
        return meta["name"]
    if ".tenancy." in comp_id:
        return "Root (Tenancy)"
    return comp_id


def edge(eid, src, tgt, label, stroke, animated=False, dashed=False,
         bidirectional=False, arrow="target"):
    """Build a React Flow edge dict.
    arrow: "target" (→), "source" (←), "both" (↔), "none"
    """
    e = {"id": eid, "source": src, "target": tgt, "label": label,
         "animated": animated, "style": {"stroke": stroke, "strokeWidth": 1.5}}
    if dashed:
        e["style"]["strokeDasharray"] = "6 4"
    marker = {"type": "arrowclosed", "color": stroke, "width": 12, "height": 12}
    if bidirectional or arrow == "both":
        e["markerEnd"] = marker
        e["markerStart"] = {**marker, "orient": "auto-start-reverse"}
    elif arrow == "target":
        e["markerEnd"] = marker
    elif arrow == "source":
        e["markerStart"] = marker
    return e


def _cx(vp):
    if not vp:
        return VCN_X0 + VCN_W // 2
    xs = [p["x"] for p in vp.values()]
    rs = [p["x"] + p["width"] for p in vp.values()]
    return int((min(xs) + max(rs)) / 2)


def build_vcns(topo, nodes):
    # Build NSG lookup for VCN-level NSG data
    nsg_by_id = {n.ocid: n for n in topo.network_security_groups}
    nsgr_by_nsg: dict[str, list] = {}
    for r in topo.nsg_rules:
        nsgr_by_nsg.setdefault(r.nsg_id, []).append(r)

    pos = {}
    x = VCN_X0
    for v in topo.vcns:
        sc = sum(1 for s in topo.subnets if s.vcn_id == v.ocid)
        h = VCN_HDR + max(1, sc) * (SUB_H + SUB_GAP) + VCN_PAD
        nodes.append({"id": v.ocid, "type": "vcn",
            "position": {"x": x, "y": ZONE_VCN_Y},
            "data": {"label": v.display_name, "resource_id": v.ocid, "resource_type": "vcn",
                     "properties": {"cidr_blocks": v.cidr_blocks, "dns_label": v.dns_label,
                         "compartment_id": v.compartment_id, "compartment_name": _comp_name(v.compartment_id),
                         "network_security_groups": [
                             {"ocid": nsg.ocid, "display_name": nsg.display_name,
                              "rules": [{"direction": r.direction, "protocol": r.protocol,
                                         "source": r.source, "destination": r.destination,
                                         "source_type": r.source_type, "destination_type": r.destination_type,
                                         "description": r.description}
                                        for r in nsgr_by_nsg.get(nsg.ocid, [])]}
                             for nsg in topo.network_security_groups if nsg.vcn_id == v.ocid
                         ]}},
            "style": {"width": VCN_W, "height": h}})
        pos[v.ocid] = {"x": x, "y": ZONE_VCN_Y, "width": VCN_W, "height": h}
        x += VCN_W + VCN_GAP
    return pos


def build_subnets(topo, nodes, vp, analysis):
    rt_names = {rt.ocid: rt.display_name for rt in topo.route_tables}
    sl_names = {sl.ocid: sl.display_name for sl in topo.security_lists}
    vcn_comps = {v.ocid: v.compartment_id for v in topo.vcns}

    # Build security list + rules lookups
    sl_by_id = {sl.ocid: sl for sl in topo.security_lists}
    sr_by_list: dict[str, list] = {}
    for r in topo.security_rules:
        sr_by_list.setdefault(r.security_list_id, []).append(r)

    by_vcn: dict[str, list] = {}
    for s in topo.subnets:
        by_vcn.setdefault(s.vcn_id, []).append(s)
    for vid, subs in by_vcn.items():
        if vid not in vp:
            continue
        vcn_compartment = vcn_comps.get(vid, "")
        for i, s in enumerate(subs):
            y = SUB_Y0 + i * (SUB_H + SUB_GAP)
            security_data = [
                {
                    "ocid": sl.ocid,
                    "display_name": sl.display_name,
                    "rules": [
                        {"direction": r.direction, "protocol": r.protocol,
                         "source": r.source, "destination": r.destination,
                         "destination_port_range_min": r.destination_port_range_min,
                         "destination_port_range_max": r.destination_port_range_max,
                         "description": r.description}
                        for r in sr_by_list.get(sl.ocid, [])
                    ]
                }
                for sid in s.security_list_ids
                if (sl := sl_by_id.get(sid))
            ]
            nodes.append({"id": s.ocid, "type": "subnet",
                "position": {"x": SUB_X, "y": y}, "parentId": vid, "extent": "parent",
                "data": {"label": s.display_name, "resource_id": s.ocid, "resource_type": "subnet",
                    "properties": {"cidr_block": s.cidr_block,
                        "is_public": not s.prohibit_public_ip_on_vnic,
                        "compartment_id": vcn_compartment,
                        "compartment_name": _comp_name(vcn_compartment),
                        "route_table_name": rt_names.get(s.route_table_id, ""),
                        "route_table_id": s.route_table_id,
                        "security_list_names": [sl_names.get(sid, sid) for sid in s.security_list_ids],
                        "security_lists": security_data}},
                "style": {"width": SUB_W, "height": SUB_H}})


# ── External ───────────────────────────────────────────────────────

def build_externals(topo, nodes, vp):
    """Position external nodes aligned above their corresponding gateways/connectivity."""
    # Find average x of gateways per type to align external nodes above them
    gw_xs: dict[str, list[int]] = {"internet": [], "oracle": [], "onprem": [], "region": []}
    for n in nodes:
        rt = n["data"].get("resource_type", "")
        if rt == "internet_gateway" or rt == "nat_gateway":
            gw_xs["internet"].append(n["position"]["x"])
        elif rt == "service_gateway":
            gw_xs["oracle"].append(n["position"]["x"])
        elif rt in ("cpe", "ipsec_connection"):
            gw_xs["onprem"].append(n["position"]["x"])
        elif rt == "rpc":
            gw_xs["region"].append(n["position"]["x"])

    cx = _cx(vp)
    fallback_x = VCN_X0
    used_xs: list[int] = []

    def _pick_x(xs_list: list[int]) -> int:
        nonlocal fallback_x
        if xs_list:
            return int(sum(xs_list) / len(xs_list))
        x = fallback_x
        while x in used_xs:
            x += 250
        fallback_x = x + 250
        return x

    def _add(nid, label, rtype, xs_list):
        x = _pick_x(xs_list)
        used_xs.append(x)
        nodes.append({"id": nid, "type": "external",
            "position": {"x": x, "y": ZONE_EXT_Y},
            "data": {"label": label, "resource_type": rtype, "resource_id": nid}})

    if topo.service_gateways:
        _add("external-oracle-services", "Oracle Services", "oracle_services", gw_xs["oracle"])
    if topo.cpes or topo.ipsec_connections:
        _add("external-on-premises", "On-Premises", "on_premises", gw_xs["onprem"])
    if topo.remote_peering_connections:
        _add("external-other-region", "Other Region", "other_region", gw_xs["region"])


# ── Gateways ───────────────────────────────────────────────────────

def build_gateways(topo, nodes, edges, vp, analysis=None):
    vcn_comps = {v.ocid: v.compartment_id for v in topo.vcns}
    gw_route_rules = analysis.gateway_to_route_rules if analysis else {}

    items: list[tuple] = []
    for g in topo.internet_gateways:
        items.append((g.ocid, g.vcn_id, g.display_name, "internet_gateway",
                       {"gateway_type": "internet_gateway", "is_enabled": g.is_enabled}))
    for g in topo.nat_gateways:
        items.append((g.ocid, g.vcn_id, g.display_name, "nat_gateway",
                       {"gateway_type": "nat_gateway", "is_enabled": True, "public_ip": g.public_ip}))
    for g in topo.service_gateways:
        items.append((g.ocid, g.vcn_id, g.display_name, "service_gateway",
                       {"gateway_type": "service_gateway", "is_enabled": True}))
    by_vcn: dict[str, list] = {}
    for it in items:
        by_vcn.setdefault(it[1], []).append(it)
    for vid, gws in by_vcn.items():
        p = vp.get(vid)
        if not p:
            continue
        span = max(1, len(gws))
        for i, (gid, _, label, gtype, props) in enumerate(gws):
            props["compartment_id"] = vcn_comps.get(vid, "")
            props["compartment_name"] = _comp_name(vcn_comps.get(vid, ""))
            props["used_by_routes"] = gw_route_rules.get(gid, [])
            gx = p["x"] + int((i + 0.5) * p["width"] / span)
            nodes.append({"id": gid, "type": "gateway",
                "position": {"x": gx, "y": ZONE_BND_Y},
                "data": {"label": label, "resource_type": gtype, "resource_id": gid, "properties": props}})


# ── DRG + DRG route tables ────────────────────────────────────────

def build_drgs(topo, nodes, edges, vp, analysis):
    if not topo.drgs:
        return

    # Build lookup maps for attachment targets
    ipsec_map = {c.ocid: c for c in topo.ipsec_connections}
    rpc_map = {r.ocid: r for r in topo.remote_peering_connections}
    vc_map = {v.ocid: v for v in topo.virtual_circuits}
    node_ids = {n["id"] for n in nodes}

    ATT_COLORS = {"VCN": "#3b82f6", "IPSEC_TUNNEL": "#ef4444",
                  "REMOTE_PEERING_CONNECTION": "#7c3aed", "VIRTUAL_CIRCUIT": "#f59e0b"}
    ATT_LABELS = {"VCN": "VCN Attach", "IPSEC_TUNNEL": "IPSec Attach",
                  "REMOTE_PEERING_CONNECTION": "RPC Attach", "VIRTUAL_CIRCUIT": "FC Attach"}

    cx = _cx(vp)
    for i, drg in enumerate(topo.drgs):
        atts = [a for a in topo.drg_attachments if a.drg_id == drg.ocid]
        rpcs = [r for r in topo.remote_peering_connections if r.drg_id == drg.ocid]
        dists = [d for d in topo.drg_route_distributions if d.drg_id == drg.ocid]
        dx = cx - 60 + i * 250
        nodes.append({"id": drg.ocid, "type": "drg",
            "position": {"x": dx, "y": ZONE_DRG_Y},
            "data": {"label": drg.display_name, "resource_id": drg.ocid, "resource_type": "drg",
                "properties": {"compartment_id": drg.compartment_id,
                    "compartment_name": _comp_name(drg.compartment_id),
                    "attachment_count": len(atts), "rpc_count": len(rpcs),
                    "attachments": [{"name": a.display_name, "type": a.network_type,
                                     "network_id": a.network_id} for a in atts],
                    "route_distributions": [{"name": d.display_name, "type": d.distribution_type} for d in dists],
                    "drg_route_tables": [
                        {"ocid": drt.ocid, "display_name": drt.display_name, "is_ecmp_enabled": drt.is_ecmp_enabled,
                         "rules": [{"destination": r.destination, "destination_type": r.destination_type,
                                    "next_hop_drg_attachment_id": r.next_hop_drg_attachment_id}
                                   for r in topo.drg_route_rules if r.drg_route_table_id == drt.ocid]}
                        for drt in topo.drg_route_tables if drt.drg_id == drg.ocid
                    ]}}})

        # DRG attachment edges — all types
        for a in atts:
            color = ATT_COLORS.get(a.network_type, "#3b82f6")
            label = f"{ATT_LABELS.get(a.network_type, a.network_type)}"
            if a.network_type == "VCN" and a.network_id in vp:
                edges.append(edge(a.ocid, drg.ocid, a.network_id, label, color, animated=True, bidirectional=True))
            elif a.network_type == "IPSEC_TUNNEL" and a.network_id in ipsec_map:
                # Link to IPSec node if it exists
                target = a.network_id if a.network_id in node_ids else drg.ocid
                if target != drg.ocid:
                    edges.append(edge(a.ocid, drg.ocid, target, label, color, animated=True))
            elif a.network_type == "REMOTE_PEERING_CONNECTION":
                # Link to RPC node (will be created below)
                edges.append(edge(a.ocid, drg.ocid, a.network_id, label, color, animated=True))
            elif a.network_type == "VIRTUAL_CIRCUIT":
                target = a.network_id if a.network_id in node_ids else drg.ocid
                if target != drg.ocid:
                    edges.append(edge(a.ocid, drg.ocid, target, label, color, animated=True))

        # RPC nodes + edge to DRG
        rpc_offset = 0
        for rpc in rpcs:
            nodes.append({"id": rpc.ocid, "type": "connectivity",
                "position": {"x": dx + 200 + rpc_offset, "y": ZONE_DRG_Y - 50},
                "data": {"label": rpc.display_name, "resource_id": rpc.ocid,
                    "resource_type": "rpc",
                    "properties": {"peer_id": rpc.peer_id, "peer_region": rpc.peer_region,
                                   "peering_status": rpc.peering_status, "drg_id": rpc.drg_id}}})
            edges.append(edge(f"edge-rpc-drg-{rpc.ocid}", rpc.ocid, drg.ocid,
                              f"RPC ({rpc.peer_region or 'peer'})", "#7c3aed", animated=True))
            rpc_offset += 180

    # RPC-to-RPC peering edges (cross-DRG or cross-region)
    rpc_seen: set[tuple[str, str]] = set()
    all_rpcs = {r.ocid: r for r in topo.remote_peering_connections}
    for rpc in topo.remote_peering_connections:
        if not rpc.peer_id or rpc.peer_id not in all_rpcs:
            continue
        pair = tuple(sorted([rpc.ocid, rpc.peer_id]))
        if pair in rpc_seen:
            continue
        rpc_seen.add(pair)
        edges.append(edge(f"edge-rpc-peer-{pair[0]}-{pair[1]}", pair[0], pair[1],
                          "RPC Peering", "#7c3aed", animated=True, dashed=True, bidirectional=True))
    # DRG route table nodes — linked to their parent DRG
    cx2 = _cx(vp)
    att_map = {a.ocid: a for a in topo.drg_attachments}
    for idx, df in enumerate(analysis.drg_flows):
        drt = next((rt for rt in topo.drg_route_tables if rt.ocid == df.route_table_ocid), None)
        if not drt:
            continue
        ecmp = drt.is_ecmp_enabled
        dx = cx2 + 200 + idx * 180
        nodes.append({"id": df.route_table_ocid, "type": "drgRouteTable",
            "position": {"x": dx, "y": ZONE_DRG_Y + 10},
            "data": {"label": df.route_table_name, "resource_id": df.route_table_ocid,
                "resource_type": "drg_route_table",
                "properties": {"rule_count": len(df.rules), "is_ecmp_enabled": ecmp,
                    "drg_name": df.drg_name, "rules": df.rules}}})
        # Edge: DRG → DRG Route Table
        edges.append(edge(f"edge-drg-drt-{df.route_table_ocid}",
                          df.drg_ocid, df.route_table_ocid, "", "#3b82f6"))
        # Edges: DRG Route Table → next-hop attachment targets (VCNs)
        for rule in df.rules:
            nhop = rule.get("next_hop_drg_attachment_id", "")
            if not nhop:
                continue
            att = att_map.get(nhop)
            target_id = att.network_id if att and att.network_id in vp else nhop
            dest = rule.get("destination", "")
            edges.append(edge(f"edge-drt-hop-{df.route_table_ocid}-{nhop}-{dest}",
                              df.route_table_ocid, target_id, dest, "#3b82f6", dashed=True))


# ── Route Tables ───────────────────────────────────────────────────

def build_load_balancers(topo, nodes, edges, vp):
    """Build LB/NLB nodes to the right of their VCN, with edges to VCN."""
    subnet_to_vcn = {s.ocid: s.vcn_id for s in topo.subnets}
    vcn_lb_count: dict[str, int] = {}

    def _place(lb_ocid, lb_name, subnet_ids, rtype, props):
        vcn_id = next((subnet_to_vcn[s] for s in subnet_ids if s in subnet_to_vcn), None)
        pos = vp.get(vcn_id) if vcn_id else None
        if not pos:
            return
        count = vcn_lb_count.get(vcn_id, 0)
        vcn_lb_count[vcn_id] = count + 1
        lx = pos["x"] + pos["width"] + 120
        ly = pos["y"] + count * 90
        nodes.append({"id": lb_ocid, "type": "loadBalancer",
            "position": {"x": lx, "y": ly},
            "data": {"label": lb_name, "resource_id": lb_ocid, "resource_type": rtype,
                "properties": props}})
        edges.append(edge(f"edge-lb-{lb_ocid}", lb_ocid, vcn_id, rtype.replace("_", " ").title(), "#ec4899", animated=True))

    for lb in topo.load_balancers:
        _place(lb.ocid, lb.display_name, lb.subnet_ids, "load_balancer",
               {"shape": lb.shape, "is_private": lb.is_private, "ip_addresses": lb.ip_addresses, "subnet_ids": lb.subnet_ids})
    for nlb in topo.network_load_balancers:
        _place(nlb.ocid, nlb.display_name, nlb.subnet_ids, "network_load_balancer",
               {"is_private": nlb.is_private, "ip_addresses": nlb.ip_addresses, "subnet_ids": nlb.subnet_ids})


def build_compartments(topo, nodes, vp):
    """Build compartment container nodes using real names from metadata.
    Each compartment with resources gets its own boundary box.
    Uses topology.metadata_json.compartment_map for display names."""

    # Get compartment name map from metadata
    comp_map = {}
    if topo.metadata_json and isinstance(topo.metadata_json, dict):
        comp_map = topo.metadata_json.get("compartment_map", {})

    # Collect compartment IDs that have resources
    comp_ids: set[str] = set()
    for v in topo.vcns:
        if v.compartment_id:
            comp_ids.add(v.compartment_id)
    for d in topo.drgs:
        if d.compartment_id:
            comp_ids.add(d.compartment_id)

    if not comp_ids:
        return {}

    # Map each non-external, non-child node to its compartment
    # VCNs and DRGs have compartment_id. Other nodes inherit from their VCN.
    vcn_comp = {v.ocid: v.compartment_id for v in topo.vcns}
    node_to_comp: dict[str, str] = {}
    for n in nodes:
        if n["type"] in ("external", "compartment") or n.get("parentId"):
            continue
        # Try to find compartment from properties or VCN parent
        props = n.get("data", {}).get("properties", {})
        cid = props.get("compartment_id", "")
        if not cid:
            # Inherit from first comp_id as fallback
            cid = next(iter(comp_ids), "")
        if cid:
            node_to_comp[n["id"]] = cid

    WIDTH_EST = {
        "vcn": lambda n: n.get("style", {}).get("width", 700),
        "drg": lambda _: 200,
        "drgRouteTable": lambda n: max(220, len(n["data"].get("label", "")) * 6 + 60),
        "routeTable": lambda n: max(180, len(n["data"].get("label", "")) * 6 + 60),
        "gateway": lambda _: 160, "loadBalancer": lambda _: 180,
        "connectivity": lambda _: 180, "firewall": lambda _: 180, "lpg": lambda _: 170,
    }

    # Group nodes by compartment
    comp_nodes: dict[str, list[dict]] = {cid: [] for cid in comp_ids}
    for n in nodes:
        nid = n["id"]
        if nid in node_to_comp:
            cid = node_to_comp[nid]
            if cid in comp_nodes:
                est = WIDTH_EST.get(n["type"], lambda _: 140)
                w = n.get("style", {}).get("width", est(n))
                h = n.get("style", {}).get("height", 60)
                comp_nodes[cid].append({
                    "x": n["position"]["x"], "y": n["position"]["y"],
                    "width": w, "height": h,
                })

    PAD_X, PAD_TOP, PAD_BOTTOM = 50, 60, 40
    compartment_positions = {}

    for comp_id in comp_ids:
        positioned = comp_nodes.get(comp_id, [])
        if not positioned:
            continue

        min_x = min(p["x"] for p in positioned) - PAD_X
        min_y = min(p["y"] for p in positioned) - PAD_TOP
        max_x = max(p["x"] + p["width"] for p in positioned) + PAD_X
        max_y = max(p["y"] + p["height"] for p in positioned) + PAD_BOTTOM

        comp_w = max_x - min_x
        comp_h = max_y - min_y

        # Get real name from metadata, fall back to OCID-derived name
        meta = comp_map.get(comp_id, {})
        comp_name = meta.get("name", "")
        if not comp_name:
            if ".tenancy." in comp_id:
                comp_name = "Root (Tenancy)"
            else:
                comp_name = comp_id

        node_id = f"compartment-{comp_id[-12:]}"
        nodes.insert(0, {
            "id": node_id,
            "type": "compartment",
            "position": {"x": min_x, "y": min_y},
            "data": {
                "label": comp_name,
                "resource_type": "compartment",
                "resource_id": comp_id,
                "properties": {"compartment_id": comp_id, "compartment_name": comp_name}
            },
            "style": {"width": comp_w, "height": comp_h, "zIndex": -1},
            "selectable": True,
            "draggable": False,
        })
        compartment_positions[comp_id] = {"x": min_x, "y": min_y, "width": comp_w, "height": comp_h}

    return compartment_positions


def build_route_tables(topo, nodes, edges, vp, analysis, emap):
    vcn_comps = {v.ocid: v.compartment_id for v in topo.vcns}
    by_vcn: dict[str, list] = {}
    for rt in topo.route_tables:
        by_vcn.setdefault(rt.vcn_id, []).append(rt)
    for vid, rts in by_vcn.items():
        p = vp.get(vid)
        if not p:
            continue
        # Filter out route tables that have no rules AND no subnets referencing them
        active_rts = [rt for rt in rts
                      if analysis.route_table_to_subnets.get(rt.ocid)
                      or any(f.route_table_ocid == rt.ocid and f.rules for f in analysis.flows)]
        if not active_rts:
            continue
        bot_y = p["y"] + p["height"] + 60
        span = max(1, len(active_rts))
        for idx, rt in enumerate(active_rts):
            flow = next((f for f in analysis.flows if f.route_table_ocid == rt.ocid), None)
            resolved = [{"destination": r.destination, "destination_type": r.destination_type,
                          "target_name": r.target_name, "target_type": r.target_type}
                         for r in flow.rules] if flow else []
            subnets_using = [
                next((s.display_name for s in topo.subnets if s.ocid == socid), socid)
                for socid in analysis.route_table_to_subnets.get(rt.ocid, [])
            ]
            rx = p["x"] + int((idx + 0.5) * p["width"] / span)
            nodes.append({"id": rt.ocid, "type": "routeTable",
                "position": {"x": rx, "y": bot_y},
                "data": {"label": rt.display_name, "resource_id": rt.ocid, "resource_type": "route_table",
                    "properties": {"rule_count": len(resolved), "rules": resolved,
                        "compartment_id": vcn_comps.get(vid, ""),
                        "compartment_name": _comp_name(vcn_comps.get(vid, "")),
                        "subnets_using": subnets_using}}})
            for socid in analysis.route_table_to_subnets.get(rt.ocid, []):
                edges.append(edge(f"edge-sub-rt-{socid}-{rt.ocid}", socid, rt.ocid, "", "#64748b"))
            if not flow:
                continue
            for r in flow.rules:
                if r.target_type == "UNKNOWN":
                    continue
                c = FLOW_COLORS.get(r.target_type, "#64748b")
                edges.append(edge(f"edge-rt-gw-{rt.ocid}-{r.target_ocid}-{r.destination}",
                                  rt.ocid, r.target_ocid, r.destination, c, dashed=True))
