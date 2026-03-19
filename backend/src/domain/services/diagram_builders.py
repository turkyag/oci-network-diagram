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


def build_vcns(topo, nodes, comp_positions):
    # Build NSG lookup for VCN-level NSG data
    nsg_by_id = {n.ocid: n for n in topo.network_security_groups}
    nsgr_by_nsg: dict[str, list] = {}
    for r in topo.nsg_rules:
        nsgr_by_nsg.setdefault(r.nsg_id, []).append(r)

    pos = {}  # ABSOLUTE positions for edge routing

    # Group VCNs by compartment for relative positioning
    by_comp: dict[str, list] = {}
    no_comp: list = []
    for v in topo.vcns:
        if v.compartment_id and v.compartment_id in comp_positions:
            by_comp.setdefault(v.compartment_id, []).append(v)
        else:
            no_comp.append(v)

    for comp_id, vcns in by_comp.items():
        cp = comp_positions[comp_id]
        rel_x = 60  # relative X inside compartment (padding from left)

        for v in vcns:
            sc = sum(1 for s in topo.subnets if s.vcn_id == v.ocid)
            h = VCN_HDR + max(1, sc) * (SUB_H + SUB_GAP) + VCN_PAD

            node = {"id": v.ocid, "type": "vcn",
                "position": {"x": rel_x, "y": 200},  # RELATIVE to compartment
                "parentId": cp["node_id"],
                "extent": "parent",
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
                "style": {"width": VCN_W, "height": h}}
            nodes.append(node)

            # Store ABSOLUTE position for edge routing
            abs_x = cp["x"] + rel_x
            abs_y = cp["y"] + 200
            pos[v.ocid] = {"x": abs_x, "y": abs_y, "width": VCN_W, "height": h}

            rel_x += VCN_W + VCN_GAP

    # VCNs without a compartment — position absolute
    abs_x = VCN_X0
    for v in no_comp:
        sc = sum(1 for s in topo.subnets if s.vcn_id == v.ocid)
        h = VCN_HDR + max(1, sc) * (SUB_H + SUB_GAP) + VCN_PAD
        nodes.append({"id": v.ocid, "type": "vcn",
            "position": {"x": abs_x, "y": ZONE_VCN_Y},
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
        pos[v.ocid] = {"x": abs_x, "y": ZONE_VCN_Y, "width": VCN_W, "height": h}
        abs_x += VCN_W + VCN_GAP

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

def build_gateways(topo, nodes, edges, vp, analysis=None, comp_positions=None):
    if comp_positions is None:
        comp_positions = {}
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
        comp_id = vcn_comps.get(vid, "")
        cp = comp_positions.get(comp_id) if comp_id else None
        span = max(1, len(gws))
        for i, (gid, _, label, gtype, props) in enumerate(gws):
            props["compartment_id"] = comp_id
            props["compartment_name"] = _comp_name(comp_id)
            props["used_by_routes"] = gw_route_rules.get(gid, [])
            # Absolute position for edge routing
            gx_abs = p["x"] + int((i + 0.5) * p["width"] / span)
            if cp:
                # Position relative to compartment
                gx_rel = gx_abs - cp["x"]
                gy_rel = ZONE_BND_Y - cp["y"]
                # Clamp: gateways go above VCNs, ensure they stay inside compartment
                gy_rel = max(30, gy_rel)
                nodes.append({"id": gid, "type": "gateway",
                    "position": {"x": gx_rel, "y": gy_rel},
                    "parentId": cp["node_id"],
                    "extent": "parent",
                    "data": {"label": label, "resource_type": gtype, "resource_id": gid, "properties": props}})
            else:
                nodes.append({"id": gid, "type": "gateway",
                    "position": {"x": gx_abs, "y": ZONE_BND_Y},
                    "data": {"label": label, "resource_type": gtype, "resource_id": gid, "properties": props}})


# ── DRG + DRG route tables ────────────────────────────────────────

def build_drgs(topo, nodes, edges, vp, analysis, comp_positions=None):
    if comp_positions is None:
        comp_positions = {}
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

    # Position each DRG above its attached VCN (not globally centered)
    for i, drg in enumerate(topo.drgs):
        atts = [a for a in topo.drg_attachments if a.drg_id == drg.ocid]
        rpcs = [r for r in topo.remote_peering_connections if r.drg_id == drg.ocid]
        dists = [d for d in topo.drg_route_distributions if d.drg_id == drg.ocid]
        # Find the VCN this DRG is attached to and position above it
        attached_vcn_ids = [a.network_id for a in atts if a.network_type == "VCN" and a.network_id in vp]
        if attached_vcn_ids:
            vcn_pos = vp[attached_vcn_ids[0]]
            dx = vcn_pos["x"] + vcn_pos["width"] // 2 - 60
        else:
            dx = _cx(vp) + i * 250

        cp = comp_positions.get(drg.compartment_id) if drg.compartment_id else None

        drg_data = {"label": drg.display_name, "resource_id": drg.ocid, "resource_type": "drg",
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
                    ]}}

        if cp:
            # Position relative to compartment
            rel_x = dx - cp["x"]
            rel_y = max(30, ZONE_DRG_Y - cp["y"])
            nodes.append({"id": drg.ocid, "type": "drg",
                "position": {"x": rel_x, "y": rel_y},
                "parentId": cp["node_id"],
                "extent": "parent",
                "data": drg_data})
        else:
            nodes.append({"id": drg.ocid, "type": "drg",
                "position": {"x": dx, "y": ZONE_DRG_Y},
                "data": drg_data})

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
    # DRG route table nodes — positioned near their parent DRG
    att_map = {a.ocid: a for a in topo.drg_attachments}
    # Build lookup: DRG ID → compartment info for parentId
    drg_comp_map = {d.ocid: d.compartment_id for d in topo.drgs}
    # Find DRG node positions (these are relative if inside a compartment)
    drg_node_pos = {}
    drg_parent_id = {}
    for n in nodes:
        if n["type"] == "drg":
            drg_node_pos[n["id"]] = n["position"]
            drg_parent_id[n["id"]] = n.get("parentId")
    drg_drt_count: dict[str, int] = {}
    for idx, df in enumerate(analysis.drg_flows):
        drt = next((rt for rt in topo.drg_route_tables if rt.ocid == df.route_table_ocid), None)
        if not drt:
            continue
        ecmp = drt.is_ecmp_enabled
        # Position next to parent DRG
        drg_pos = drg_node_pos.get(df.drg_ocid, {"x": 500, "y": ZONE_DRG_Y})
        drt_idx = drg_drt_count.get(df.drg_ocid, 0)
        drg_drt_count[df.drg_ocid] = drt_idx + 1
        drt_x = drg_pos["x"] + 200 + drt_idx * 200
        drt_y = drg_pos["y"] + 10

        # If parent DRG is inside a compartment, DRG route table goes in same compartment
        parent_comp_node_id = drg_parent_id.get(df.drg_ocid)
        drt_node = {"id": df.route_table_ocid, "type": "drgRouteTable",
            "position": {"x": drt_x, "y": drt_y},
            "data": {"label": df.route_table_name, "resource_id": df.route_table_ocid,
                "resource_type": "drg_route_table",
                "properties": {"rule_count": len(df.rules), "is_ecmp_enabled": ecmp,
                    "drg_name": df.drg_name, "rules": df.rules}}}
        if parent_comp_node_id:
            drt_node["parentId"] = parent_comp_node_id
            drt_node["extent"] = "parent"
        nodes.append(drt_node)
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


def build_compartments(topo):
    """Build compartment container nodes. Must run BEFORE other builders.
    Returns (nodes, comp_positions) where comp_positions maps comp_id to
    {node_id, x, y, width, height} for child positioning."""

    comp_map = {}
    if topo.metadata_json and isinstance(topo.metadata_json, dict):
        comp_map = topo.metadata_json.get("compartment_map", {})

    # Group VCNs by compartment
    comp_vcns: dict[str, list] = {}
    for v in topo.vcns:
        if v.compartment_id:
            comp_vcns.setdefault(v.compartment_id, []).append(v)

    # Also note DRGs per compartment
    comp_drgs: dict[str, list] = {}
    for d in topo.drgs:
        if d.compartment_id:
            comp_drgs.setdefault(d.compartment_id, []).append(d)

    # All compartments that have resources
    all_comp_ids = set(comp_vcns.keys()) | set(comp_drgs.keys())

    nodes = []
    comp_positions = {}  # comp_id -> {node_id, x, y, width, height}

    x_offset = 100
    COMP_PAD = 80  # padding inside compartment

    for comp_id in sorted(all_comp_ids):  # sorted for deterministic layout
        meta = comp_map.get(comp_id, {})
        comp_name = meta.get("name", "")
        if not comp_name:
            comp_name = "Root (Tenancy)" if ".tenancy." in comp_id else comp_id

        vcns = comp_vcns.get(comp_id, [])
        drgs = comp_drgs.get(comp_id, [])

        # Estimate compartment size based on content
        vcn_count = len(vcns)
        max_subnet_count = max(
            (sum(1 for s in topo.subnets if s.vcn_id == v.ocid) for v in vcns),
            default=1,
        )

        # Width: enough for VCNs side by side + padding
        comp_w = max(800, vcn_count * (VCN_W + VCN_GAP) + COMP_PAD * 2)

        # Height: VCN header area + VCN body + route tables + DRG area + padding
        vcn_h = VCN_HDR + max(1, max_subnet_count) * (SUB_H + SUB_GAP) + VCN_PAD
        comp_h = vcn_h + 350  # room for gateways above, route tables below, DRG area

        node_id = f"compartment-{comp_id[-12:]}"

        nodes.append({
            "id": node_id,
            "type": "compartment",
            "position": {"x": x_offset, "y": 50},
            "data": {
                "label": comp_name,
                "resource_type": "compartment",
                "resource_id": comp_id,
                "properties": {"compartment_id": comp_id, "compartment_name": comp_name},
            },
            "style": {"width": comp_w, "height": comp_h},
        })

        comp_positions[comp_id] = {
            "node_id": node_id,
            "x": x_offset,
            "y": 50,
            "width": comp_w,
            "height": comp_h,
        }

        x_offset += comp_w + 100  # gap between compartments

    return nodes, comp_positions


def build_route_tables(topo, nodes, edges, vp, analysis, emap, comp_positions=None):
    if comp_positions is None:
        comp_positions = {}
    vcn_comps = {v.ocid: v.compartment_id for v in topo.vcns}
    by_vcn: dict[str, list] = {}
    for rt in topo.route_tables:
        by_vcn.setdefault(rt.vcn_id, []).append(rt)
    for vid, rts in by_vcn.items():
        p = vp.get(vid)
        if not p:
            continue
        comp_id = vcn_comps.get(vid, "")
        cp = comp_positions.get(comp_id) if comp_id else None
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
            rx_abs = p["x"] + int((idx + 0.5) * p["width"] / span)

            rt_node = {"id": rt.ocid, "type": "routeTable",
                "data": {"label": rt.display_name, "resource_id": rt.ocid, "resource_type": "route_table",
                    "properties": {"rule_count": len(resolved), "rules": resolved,
                        "compartment_id": comp_id,
                        "compartment_name": _comp_name(comp_id),
                        "subnets_using": subnets_using}}}

            if cp:
                # Position relative to compartment
                rt_node["position"] = {"x": rx_abs - cp["x"], "y": bot_y - cp["y"]}
                rt_node["parentId"] = cp["node_id"]
                rt_node["extent"] = "parent"
            else:
                rt_node["position"] = {"x": rx_abs, "y": bot_y}

            nodes.append(rt_node)
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
