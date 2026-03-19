#!/usr/bin/env python3
"""
OCI Network Sync — Pulls real network data from OCI

Connects to Oracle Cloud Infrastructure using your API config,
fetches all network resources, and sends them to the backend API.

Usage:
    python sync.py [--api-url http://backend:8000] [--compartment-id ocid1.compartment...]
                   [--config-file /oci/config] [--profile DEFAULT]
                   [--name "My Network"]
"""
from __future__ import annotations

import argparse
import sys
import time

import httpx
import oci


# ---------------------------------------------------------------------------
# OCI data fetching
# ---------------------------------------------------------------------------

def _discover_compartments(config: dict, tenancy_id: str, root_compartment_id: str) -> tuple[list[str], dict[str, dict]]:
    """Recursively list all compartments. Returns (list of IDs, map of ID → {name, parent_id})."""
    identity = oci.identity.IdentityClient(config)

    # Root compartment (tenancy)
    comp_map: dict[str, dict] = {}
    try:
        tenancy = identity.get_tenancy(tenancy_id).data
        root_name = tenancy.name or "Tenancy"
    except Exception:
        root_name = "Root"
    comp_map[root_compartment_id] = {"name": root_name, "parent_id": ""}

    all_ids = [root_compartment_id]

    try:
        compartments = _list_all(
            identity.list_compartments, root_compartment_id,
            compartment_id_in_subtree=True,
            access_level="ACCESSIBLE",
        )
        for c in compartments:
            if getattr(c, "lifecycle_state", "") == "ACTIVE":
                all_ids.append(c.id)
                comp_map[c.id] = {
                    "name": c.name or c.id[-8:],
                    "parent_id": c.compartment_id or root_compartment_id,
                }
                print(f"    {c.name} ({c.id[-12:]}...)")
    except oci.exceptions.ServiceError as e:
        print(f"  Warning: Could not list sub-compartments: {e.message[:80]}")

    return all_ids, comp_map


def fetch_oci_network_data(config: dict, compartment_id: str) -> dict:
    """Fetch all network resources from OCI across all sub-compartments."""
    tenancy_id = config.get("tenancy", compartment_id)

    # Discover all compartments (root + children recursively)
    print("  Discovering compartments...")
    compartment_ids, comp_map = _discover_compartments(config, tenancy_id, compartment_id)
    print(f"  Found {len(compartment_ids)} compartment(s)")

    vn_client = oci.core.VirtualNetworkClient(config)
    lb_client = oci.load_balancer.LoadBalancerClient(config)
    nlb_client = oci.network_load_balancer.NetworkLoadBalancerClient(config)

    payload = _empty_payload()

    # Fetch VCNs across ALL compartments
    print("  Fetching VCNs...")
    vcns = []
    for cid in compartment_ids:
        vcns.extend(_list_all(vn_client.list_vcns, cid))
    for v in vcns:
        payload["vcns"].append(_vcn(v))

    vcn_ids = [v.id for v in vcns]

    # Build VCN → compartment map for VCN-scoped queries
    vcn_comp = {v.id: v.compartment_id for v in vcns}

    print("  Fetching Subnets...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for s in _list_all(vn_client.list_subnets, cid, vcn_id=vcn_id):
            payload["subnets"].append(_subnet(s))

    print("  Fetching Internet Gateways...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for g in _list_all(vn_client.list_internet_gateways, cid, vcn_id=vcn_id):
            payload["internet_gateways"].append(_igw(g))

    print("  Fetching NAT Gateways...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for g in _list_all(vn_client.list_nat_gateways, cid, vcn_id=vcn_id):
            payload["nat_gateways"].append(_nat(g))

    print("  Fetching Service Gateways...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for g in _list_all(vn_client.list_service_gateways, cid, vcn_id=vcn_id):
            payload["service_gateways"].append(_sgw(g))

    print("  Fetching DRGs...")
    drgs = []
    for cid in compartment_ids:
        drgs.extend(_list_all(vn_client.list_drgs, cid))
    for d in drgs:
        payload["drgs"].append(_drg(d))

    drg_ids = [d.id for d in drgs]

    print("  Fetching DRG Attachments...")
    for cid in compartment_ids:
        for drg_id in drg_ids:
            for a in _list_all(vn_client.list_drg_attachments, cid, drg_id=drg_id):
                payload["drg_attachments"].append(_drg_attachment(a))

    print("  Fetching DRG Route Tables...")
    for drg_id in drg_ids:
        for t in _list_all(vn_client.list_drg_route_tables, drg_id):
            payload["drg_route_tables"].append(_drg_route_table(t))
            # Fetch rules for each route table
            try:
                rules = _list_all(vn_client.list_drg_route_rules, t.id)
                for r in rules:
                    payload["drg_route_rules"].append(_drg_route_rule(t.id, r))
            except oci.exceptions.ServiceError:
                pass

    print("  Fetching Remote Peering Connections...")
    for cid in compartment_ids:
        for drg_id in drg_ids:
            try:
                rpcs = _list_all(vn_client.list_remote_peering_connections, cid, drg_id=drg_id)
                for r in rpcs:
                    payload["remote_peering_connections"].append(_rpc(r))
            except oci.exceptions.ServiceError:
                pass

    print("  Fetching Local Peering Gateways...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        try:
            lpgs = _list_all(vn_client.list_local_peering_gateways, cid, vcn_id=vcn_id)
            for l in lpgs:
                payload["local_peering_gateways"].append(_lpg(l))
        except oci.exceptions.ServiceError:
            pass

    print("  Fetching Route Tables...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for rt in _list_all(vn_client.list_route_tables, cid, vcn_id=vcn_id):
            payload["route_tables"].append(_route_table(rt))
            for rule in (rt.route_rules or []):
                payload["route_rules"].append(_route_rule(rt.id, rule))

    print("  Fetching Security Lists...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for sl in _list_all(vn_client.list_security_lists, cid, vcn_id=vcn_id):
            payload["security_lists"].append(_security_list(sl))
            for rule in (sl.ingress_security_rules or []):
                payload["security_rules"].append(_security_rule(sl.id, "INGRESS", rule))
            for rule in (sl.egress_security_rules or []):
                payload["security_rules"].append(_security_rule(sl.id, "EGRESS", rule))

    print("  Fetching Network Security Groups...")
    for cid in compartment_ids:
        for vcn_id in vcn_ids:
            try:
                for nsg in _list_all(vn_client.list_network_security_groups, compartment_id=cid, vcn_id=vcn_id):
                    payload["network_security_groups"].append(_nsg(nsg))
                    try:
                        nsg_rules = _list_all(vn_client.list_network_security_group_security_rules, nsg.id)
                        for r in nsg_rules:
                            payload["nsg_rules"].append(_nsg_rule(nsg.id, r))
                    except oci.exceptions.ServiceError:
                        pass
            except oci.exceptions.ServiceError:
                pass

    print("  Fetching Load Balancers...")
    for cid in compartment_ids:
        try:
            for lb in _list_all(lb_client.list_load_balancers, compartment_id=cid):
                payload["load_balancers"].append(_lb(lb))
        except oci.exceptions.ServiceError:
            pass

    print("  Fetching Network Load Balancers...")
    for cid in compartment_ids:
        try:
            for nlb in _list_all(nlb_client.list_network_load_balancers, compartment_id=cid):
                payload["network_load_balancers"].append(_nlb(nlb))
        except oci.exceptions.ServiceError:
            pass

    print("  Fetching IPSec Connections...")
    for cid in compartment_ids:
        for drg_id in drg_ids:
            try:
                conns = _list_all(vn_client.list_ip_sec_connections, cid, drg_id=drg_id)
                for c in conns:
                    payload["ipsec_connections"].append(_ipsec(c))
                    try:
                        tunnels = _list_all(vn_client.list_ip_sec_connection_tunnels, c.id)
                        for t in tunnels:
                            payload["ipsec_tunnels"].append(_ipsec_tunnel(c.id, t))
                    except oci.exceptions.ServiceError:
                        pass
            except oci.exceptions.ServiceError:
                pass

    print("  Fetching CPEs...")
    for cid in compartment_ids:
        try:
            for cpe in _list_all(vn_client.list_cpes, cid):
                payload["cpes"].append(_cpe(cpe))
        except oci.exceptions.ServiceError:
            pass

    print("  Fetching DHCP Options...")
    for vcn_id in vcn_ids:
        cid = vcn_comp.get(vcn_id, compartment_id)
        for dh in _list_all(vn_client.list_dhcp_options, cid, vcn_id=vcn_id):
            payload["dhcp_options"].append(dict(
                ocid=dh.id, vcn_id=dh.vcn_id or "", display_name=dh.display_name or "",
                options=[{"type": getattr(o, "type", ""), "server_type": getattr(o, "server_type", "")} for o in (dh.options or [])],
            ))

    # Build subnet→VCN map for firewall resolution
    subnet_vcn = {s["ocid"]: s["vcn_id"] for s in payload["subnets"] if s.get("vcn_id")}

    print("  Fetching Network Firewalls...")
    try:
        nfw_mod = __import__("oci.network_firewall", fromlist=["NetworkFirewallClient"])
        nfw_client = nfw_mod.NetworkFirewallClient(config)
        for cid in compartment_ids:
            for nf in _list_all(nfw_client.list_network_firewalls, compartment_id=cid):
                fw_subnet_id = getattr(nf, "subnet_id", "") or ""
                payload["network_firewalls"].append(dict(
                    ocid=nf.id, display_name=nf.display_name or "",
                    subnet_id=fw_subnet_id,
                    vcn_id=subnet_vcn.get(fw_subnet_id, ""),
                    policy_id=getattr(nf, "network_firewall_policy_id", "") or "",
                    ip_addresses=[ip for ip in (getattr(nf, "ipv4_address", None) and [nf.ipv4_address] or [])],
                    lifecycle_state=getattr(nf, "lifecycle_state", "") or "",
                ))
    except Exception as e:
        print(f"    Skipped (not available or no permissions): {e}")

    print("  Fetching Public IPs...")
    for cid in compartment_ids:
        try:
            for pip in _list_all(vn_client.list_public_ips, scope="REGION", compartment_id=cid):
                payload["public_ips"].append(dict(
                    ocid=pip.id, display_name=pip.display_name or "",
                    ip_address=pip.ip_address or "",
                    lifetime=pip.lifetime or "",
                    assigned_entity_id=pip.assigned_entity_id or "",
                    assigned_entity_type=pip.assigned_entity_type or "",
                    compartment_id=pip.compartment_id or "",
                ))
        except oci.exceptions.ServiceError:
            pass

    print("  Fetching Cross-Connects...")
    for cid in compartment_ids:
      try:
        for cc in _list_all(vn_client.list_cross_connects, cid):
            payload["cross_connects"].append(dict(
                ocid=cc.id, display_name=cc.display_name or "",
                compartment_id=cc.compartment_id or "",
                location_name=getattr(cc, "location_name", "") or "",
                port_speed_shape_name=getattr(cc, "port_speed_shape_name", "") or "",
                cross_connect_group_id=getattr(cc, "cross_connect_group_id", "") or "",
                lifecycle_state=getattr(cc, "lifecycle_state", "") or "",
            ))
      except oci.exceptions.ServiceError:
        pass

    print("  Fetching Virtual Circuits...")
    for cid in compartment_ids:
      try:
        for vc in _list_all(vn_client.list_virtual_circuits, cid):
            payload["virtual_circuits"].append(dict(
                ocid=vc.id, display_name=vc.display_name or "",
                compartment_id=vc.compartment_id or "",
                type=getattr(vc, "type", "") or "",
                bandwidth_shape_name=getattr(vc, "bandwidth_shape_name", "") or "",
                bgp_session_state=getattr(vc, "bgp_session_state", "") or "",
                gateway_id=getattr(vc, "gateway_id", "") or "",
                provider_name=getattr(vc, "provider_name", "") or "",
                region=getattr(vc, "region", "") or "",
                lifecycle_state=getattr(vc, "lifecycle_state", "") or "",
            ))
      except oci.exceptions.ServiceError:
        pass

    print("  Fetching DRG Route Distributions...")
    for drg_id in drg_ids:
        try:
            for rd in _list_all(vn_client.list_drg_route_distributions, drg_id):
                payload["drg_route_distributions"].append(dict(
                    ocid=rd.id, drg_id=rd.drg_id or "", display_name=rd.display_name or "",
                    distribution_type=rd.distribution_type or "",
                ))
        except oci.exceptions.ServiceError:
            pass

    # Include compartment metadata for the diagram
    payload["_compartment_map"] = comp_map

    return payload


# ---------------------------------------------------------------------------
# OCI pagination helper
# ---------------------------------------------------------------------------

def _extract_items(data):
    """Extract list items from OCI response data (handles both list and collection objects)."""
    if isinstance(data, list):
        return data
    if hasattr(data, "items"):
        return data.items
    return [data]


def _list_all(list_fn, *args, **kwargs):
    """Call an OCI list function and handle pagination."""
    items = []
    try:
        response = list_fn(*args, **kwargs)
        items.extend(_extract_items(response.data))
        while response.has_next_page:
            response = list_fn(*args, page=response.next_page, **kwargs)
            items.extend(_extract_items(response.data))
    except oci.exceptions.ServiceError as e:
        if e.status in (404, 400):
            return items
        raise
    except AttributeError:
        pass
    return items


# ---------------------------------------------------------------------------
# Resource mappers — OCI SDK objects → import payload dicts
# ---------------------------------------------------------------------------

def _vcn(v) -> dict:
    return dict(
        ocid=v.id, display_name=v.display_name or "",
        cidr_blocks=v.cidr_blocks or (v.cidr_block and [v.cidr_block]) or [],
        dns_label=v.dns_label or "", compartment_id=v.compartment_id or "",
    )

def _subnet(s) -> dict:
    return dict(
        ocid=s.id, vcn_id=s.vcn_id or "", display_name=s.display_name or "",
        cidr_block=s.cidr_block or "",
        subnet_domain_name=s.subnet_domain_name or "",
        route_table_id=s.route_table_id or "",
        security_list_ids=s.security_list_ids or [],
        prohibit_public_ip_on_vnic=getattr(s, 'prohibit_public_ip_on_vnic', True) if hasattr(s, 'prohibit_public_ip_on_vnic') else True,
    )

def _igw(g) -> dict:
    return dict(
        ocid=g.id, vcn_id=g.vcn_id or "", display_name=g.display_name or "",
        is_enabled=g.is_enabled if g.is_enabled is not None else True,
    )

def _nat(g) -> dict:
    return dict(
        ocid=g.id, vcn_id=g.vcn_id or "", display_name=g.display_name or "",
        public_ip=g.nat_ip or "",
    )

def _sgw(g) -> dict:
    services = []
    if g.services:
        services = [s.service_name for s in g.services]
    return dict(
        ocid=g.id, vcn_id=g.vcn_id or "", display_name=g.display_name or "",
        services=services,
    )

def _drg(d) -> dict:
    return dict(
        ocid=d.id, display_name=d.display_name or "",
        compartment_id=d.compartment_id or "",
    )

def _drg_attachment(a) -> dict:
    net_type = ""
    net_id = ""
    if a.network_details:
        net_type = a.network_details.type or ""
        net_id = a.network_details.id or ""
    return dict(
        ocid=a.id, drg_id=a.drg_id or "", display_name=a.display_name or "",
        network_type=net_type, network_id=net_id,
    )

def _drg_route_table(t) -> dict:
    return dict(
        ocid=t.id, drg_id=t.drg_id or "", display_name=t.display_name or "",
        is_ecmp_enabled=t.is_ecmp_enabled or False,
    )

def _drg_route_rule(table_id: str, r) -> dict:
    return dict(
        drg_route_table_id=table_id,
        destination=r.destination or "",
        destination_type=r.destination_type or "",
        next_hop_drg_attachment_id=r.next_hop_drg_attachment_id or "",
    )

def _rpc(r) -> dict:
    return dict(
        ocid=r.id, drg_id=r.drg_id or "", display_name=r.display_name or "",
        peer_id=r.peer_id or "", peer_region=r.peer_region_name or "",
        peering_status=r.peering_status or "",
    )

def _lpg(l) -> dict:
    return dict(
        ocid=l.id, vcn_id=l.vcn_id or "", display_name=l.display_name or "",
        peer_id=l.peer_id or "", peering_status=l.peering_status or "",
    )

def _route_table(rt) -> dict:
    return dict(
        ocid=rt.id, vcn_id=rt.vcn_id or "", display_name=rt.display_name or "",
    )

def _route_rule(rt_id: str, r) -> dict:
    return dict(
        route_table_id=rt_id,
        destination=r.destination or "",
        destination_type=r.destination_type or "",
        network_entity_id=r.network_entity_id or "",
        description=r.description or "",
    )

def _security_list(sl) -> dict:
    return dict(
        ocid=sl.id, vcn_id=sl.vcn_id or "", display_name=sl.display_name or "",
    )

def _security_rule(sl_id: str, direction: str, r) -> dict:
    src = ""
    dst = ""
    dp_min = None
    dp_max = None
    sp_min = None
    sp_max = None

    if direction == "INGRESS":
        src = r.source or ""
    else:
        dst = r.destination or ""

    proto = r.protocol or "all"
    desc = r.description or ""

    # TCP/UDP port ranges
    if hasattr(r, "tcp_options") and r.tcp_options:
        if r.tcp_options.destination_port_range:
            dp_min = r.tcp_options.destination_port_range.min
            dp_max = r.tcp_options.destination_port_range.max
        if r.tcp_options.source_port_range:
            sp_min = r.tcp_options.source_port_range.min
            sp_max = r.tcp_options.source_port_range.max
    if hasattr(r, "udp_options") and r.udp_options:
        if r.udp_options.destination_port_range:
            dp_min = r.udp_options.destination_port_range.min
            dp_max = r.udp_options.destination_port_range.max
        if r.udp_options.source_port_range:
            sp_min = r.udp_options.source_port_range.min
            sp_max = r.udp_options.source_port_range.max

    return dict(
        security_list_id=sl_id, direction=direction, protocol=proto,
        source=src, destination=dst,
        source_port_range_min=sp_min, source_port_range_max=sp_max,
        destination_port_range_min=dp_min, destination_port_range_max=dp_max,
        description=desc,
    )

def _nsg(n) -> dict:
    return dict(
        ocid=n.id, vcn_id=n.vcn_id or "", display_name=n.display_name or "",
    )

def _nsg_rule(nsg_id: str, r) -> dict:
    dp_min = None
    dp_max = None
    sp_min = None
    sp_max = None

    if hasattr(r, "tcp_options") and r.tcp_options:
        if r.tcp_options.destination_port_range:
            dp_min = r.tcp_options.destination_port_range.min
            dp_max = r.tcp_options.destination_port_range.max
        if r.tcp_options.source_port_range:
            sp_min = r.tcp_options.source_port_range.min
            sp_max = r.tcp_options.source_port_range.max
    if hasattr(r, "udp_options") and r.udp_options:
        if r.udp_options.destination_port_range:
            dp_min = r.udp_options.destination_port_range.min
            dp_max = r.udp_options.destination_port_range.max
        if r.udp_options.source_port_range:
            sp_min = r.udp_options.source_port_range.min
            sp_max = r.udp_options.source_port_range.max

    return dict(
        nsg_id=nsg_id, direction=r.direction or "",
        protocol=r.protocol or "all",
        source=r.source or "", destination=r.destination or "",
        source_type=r.source_type or "", destination_type=r.destination_type or "",
        source_port_range_min=sp_min, source_port_range_max=sp_max,
        destination_port_range_min=dp_min, destination_port_range_max=dp_max,
        description=r.description or "",
    )

def _lb(lb) -> dict:
    ips = []
    if lb.ip_addresses:
        ips = [ip.ip_address for ip in lb.ip_addresses if ip.ip_address]
    return dict(
        ocid=lb.id, display_name=lb.display_name or "",
        ip_addresses=ips, shape=lb.shape_name or "",
        subnet_ids=lb.subnet_ids or [], is_private=lb.is_private or False,
    )

def _nlb(nlb) -> dict:
    ips = []
    if hasattr(nlb, "ip_addresses") and nlb.ip_addresses:
        for ip in nlb.ip_addresses:
            addr = ip.ip_address if hasattr(ip, "ip_address") else str(ip)
            if addr:
                ips.append(addr)
    subnet_ids = []
    if hasattr(nlb, "subnet_id") and nlb.subnet_id:
        subnet_ids = [nlb.subnet_id]
    return dict(
        ocid=nlb.id, display_name=nlb.display_name or "",
        ip_addresses=ips, subnet_ids=subnet_ids,
        is_private=getattr(nlb, "is_private", False) or False,
        is_preserve_source=getattr(nlb, "is_preserve_source_destination", False) or False,
    )

def _ipsec(c) -> dict:
    return dict(
        ocid=c.id, drg_id=c.drg_id or "", cpe_id=c.cpe_id or "",
        display_name=c.display_name or "",
        static_routes=c.static_routes or [],
        cpe_local_identifier=c.cpe_local_identifier or "",
    )

def _ipsec_tunnel(conn_id: str, t) -> dict:
    bgp = {}
    if t.bgp_session_info:
        bgp = {
            "oracle_bgp_asn": getattr(t.bgp_session_info, "oracle_bgp_asn", None),
            "customer_bgp_asn": getattr(t.bgp_session_info, "customer_bgp_asn", None),
            "bgp_state": getattr(t.bgp_session_info, "bgp_state", None),
        }
    return dict(
        ocid=t.id, ipsec_connection_id=conn_id,
        display_name=t.display_name or "",
        status=t.status or "", vpn_ip=t.vpn_ip or "", cpe_ip=t.cpe_ip or "",
        routing=t.routing or "", bgp_info=bgp,
    )

def _cpe(c) -> dict:
    return dict(
        ocid=c.id, display_name=c.display_name or "",
        ip_address=c.ip_address or "",
        cpe_device_shape_id=c.cpe_device_shape_id or "",
    )


def _empty_payload() -> dict:
    return {
        "vcns": [], "subnets": [], "internet_gateways": [], "nat_gateways": [],
        "service_gateways": [], "drgs": [], "drg_attachments": [], "drg_route_tables": [],
        "drg_route_rules": [], "remote_peering_connections": [], "local_peering_gateways": [],
        "route_tables": [], "route_rules": [], "security_lists": [], "security_rules": [],
        "network_security_groups": [], "nsg_rules": [], "load_balancers": [],
        "network_load_balancers": [], "ipsec_connections": [], "cpes": [], "ipsec_tunnels": [],
        "network_firewalls": [], "dhcp_options": [], "public_ips": [],
        "cross_connects": [], "virtual_circuits": [], "drg_route_distributions": [],
    }


# ---------------------------------------------------------------------------
# API interaction
# ---------------------------------------------------------------------------

def create_topology(client: httpx.Client, api_url: str, name: str, description: str) -> int:
    resp = client.post(f"{api_url}/api/topologies", json={"name": name, "description": description})
    resp.raise_for_status()
    return resp.json()["id"]


def import_data(client: httpx.Client, api_url: str, topology_id: int, payload: dict) -> None:
    resp = client.post(f"{api_url}/api/topologies/{topology_id}/import", json=payload)
    resp.raise_for_status()


def wait_for_backend(api_url: str, max_retries: int = 30, delay: float = 2.0) -> None:
    for attempt in range(max_retries):
        try:
            resp = httpx.get(f"{api_url}/api/topologies", timeout=5.0)
            if resp.status_code < 500:
                return
        except httpx.ConnectError:
            pass
        print(f"  Waiting for backend... (attempt {attempt + 1}/{max_retries})")
        time.sleep(delay)
    print("ERROR: Backend did not become ready in time.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real OCI network data and import into the diagram tool")
    parser.add_argument("--api-url", default="http://backend:8000", help="Backend API URL")
    parser.add_argument("--config-file", default="/oci/config", help="OCI config file path")
    parser.add_argument("--profile", default="DEFAULT", help="OCI config profile name")
    parser.add_argument("--compartment-id", default="", help="Compartment OCID (defaults to tenancy root)")
    parser.add_argument("--name", default="", help="Topology name (defaults to region name)")
    parser.add_argument("--wait", action="store_true", default=True, help="Wait for backend")
    args = parser.parse_args()

    api_url = args.api_url.rstrip("/")

    print("OCI Network Diagram - Data Fetcher")
    print(f"  Config:  {args.config_file} [{args.profile}]")
    print(f"  API URL: {api_url}")
    print()

    # Load OCI config
    try:
        config = oci.config.from_file(args.config_file, args.profile)
    except Exception as e:
        print(f"ERROR: Failed to load OCI config from {args.config_file}: {e}")
        sys.exit(1)

    oci.config.validate_config(config)
    region = config.get("region", "unknown")
    compartment_id = args.compartment_id or config.get("tenancy", "")

    print(f"  Region:      {region}")
    print(f"  Tenancy:     {config.get('tenancy', 'N/A')}")
    print(f"  Compartment: {compartment_id}")
    print()

    if args.wait:
        wait_for_backend(api_url)

    # Fetch real data from OCI
    print("Fetching network resources from OCI...")
    payload = fetch_oci_network_data(config, compartment_id)

    # Print summary
    print()
    print("Fetched resources:")
    total = 0
    for key, items in payload.items():
        if items:
            label = key.replace("_", " ").title()
            print(f"  {label}: {len(items)}")
            total += len(items)
    print(f"  Total: {total}")
    print()

    if total == 0:
        print("No network resources found in this compartment.")
        print("Check your compartment ID or try a different one.")
        sys.exit(0)

    # Send to API
    topo_name = args.name or f"oci-{region}"
    with httpx.Client(timeout=30.0) as client:
        print(f"Creating topology '{topo_name}'...")
        topology_id = create_topology(client, api_url, topo_name, f"OCI {region}")
        print(f"  Topology ID: {topology_id}")

        print("Importing resources...")
        import_data(client, api_url, topology_id, payload)
        print("  Import complete!")

    print()
    print(f"Done! Topology '{topo_name}' created with {total} resources.")


if __name__ == "__main__":
    main()
