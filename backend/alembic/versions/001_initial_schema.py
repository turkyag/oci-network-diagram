"""Initial schema with all OCI network resource tables.

Revision ID: 001
Revises:
Create Date: 2026-03-19
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topologies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # VCNs
    op.create_table(
        "vcns",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("cidr_blocks", sa.JSON(), nullable=True),
        sa.Column("dns_label", sa.String(255), server_default=""),
        sa.Column("compartment_id", sa.String(255), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vcns_topology_id", "vcns", ["topology_id"])
    op.create_index("ix_vcns_ocid", "vcns", ["ocid"])

    # Subnets
    op.create_table(
        "subnets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("cidr_block", sa.String(50), nullable=False),
        sa.Column("subnet_domain_name", sa.String(255), server_default=""),
        sa.Column("route_table_id", sa.String(255), server_default=""),
        sa.Column("security_list_ids", sa.JSON(), nullable=True),
        sa.Column("prohibit_public_ip_on_vnic", sa.Boolean(), server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subnets_topology_id", "subnets", ["topology_id"])
    op.create_index("ix_subnets_ocid", "subnets", ["ocid"])

    # Internet Gateways
    op.create_table(
        "internet_gateways",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_internet_gateways_topology_id", "internet_gateways", ["topology_id"])
    op.create_index("ix_internet_gateways_ocid", "internet_gateways", ["ocid"])

    # NAT Gateways
    op.create_table(
        "nat_gateways",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("public_ip", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_nat_gateways_topology_id", "nat_gateways", ["topology_id"])
    op.create_index("ix_nat_gateways_ocid", "nat_gateways", ["ocid"])

    # Service Gateways
    op.create_table(
        "service_gateways",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_gateways_topology_id", "service_gateways", ["topology_id"])
    op.create_index("ix_service_gateways_ocid", "service_gateways", ["ocid"])

    # DRGs
    op.create_table(
        "drgs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("compartment_id", sa.String(255), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_drgs_topology_id", "drgs", ["topology_id"])
    op.create_index("ix_drgs_ocid", "drgs", ["ocid"])

    # DRG Attachments
    op.create_table(
        "drg_attachments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("drg_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("network_type", sa.String(50), server_default=""),
        sa.Column("network_id", sa.String(255), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_drg_attachments_topology_id", "drg_attachments", ["topology_id"])
    op.create_index("ix_drg_attachments_ocid", "drg_attachments", ["ocid"])

    # DRG Route Tables
    op.create_table(
        "drg_route_tables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("drg_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("is_ecmp_enabled", sa.Boolean(), server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_drg_route_tables_topology_id", "drg_route_tables", ["topology_id"])
    op.create_index("ix_drg_route_tables_ocid", "drg_route_tables", ["ocid"])

    # DRG Route Rules
    op.create_table(
        "drg_route_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("drg_route_table_id", sa.String(255), nullable=False),
        sa.Column("destination", sa.String(255), nullable=False),
        sa.Column("destination_type", sa.String(50), nullable=False),
        sa.Column("next_hop_drg_attachment_id", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_drg_route_rules_topology_id", "drg_route_rules", ["topology_id"])

    # Remote Peering Connections
    op.create_table(
        "remote_peering_connections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("drg_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("peer_id", sa.String(255), server_default=""),
        sa.Column("peer_region", sa.String(100), server_default=""),
        sa.Column("peering_status", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_remote_peering_connections_topology_id", "remote_peering_connections", ["topology_id"])
    op.create_index("ix_remote_peering_connections_ocid", "remote_peering_connections", ["ocid"])

    # Local Peering Gateways
    op.create_table(
        "local_peering_gateways",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("peer_id", sa.String(255), server_default=""),
        sa.Column("peering_status", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_local_peering_gateways_topology_id", "local_peering_gateways", ["topology_id"])
    op.create_index("ix_local_peering_gateways_ocid", "local_peering_gateways", ["ocid"])

    # Route Tables
    op.create_table(
        "route_tables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_route_tables_topology_id", "route_tables", ["topology_id"])
    op.create_index("ix_route_tables_ocid", "route_tables", ["ocid"])

    # Route Rules
    op.create_table(
        "route_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("route_table_id", sa.String(255), nullable=False),
        sa.Column("destination", sa.String(255), nullable=False),
        sa.Column("destination_type", sa.String(50), nullable=False),
        sa.Column("network_entity_id", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_route_rules_topology_id", "route_rules", ["topology_id"])

    # Security Lists
    op.create_table(
        "security_lists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_security_lists_topology_id", "security_lists", ["topology_id"])
    op.create_index("ix_security_lists_ocid", "security_lists", ["ocid"])

    # Security Rules
    op.create_table(
        "security_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("security_list_id", sa.String(255), nullable=False),
        sa.Column("direction", sa.String(20), nullable=False),
        sa.Column("protocol", sa.String(10), nullable=False),
        sa.Column("source", sa.String(255), server_default=""),
        sa.Column("destination", sa.String(255), server_default=""),
        sa.Column("source_port_range_min", sa.Integer(), nullable=True),
        sa.Column("source_port_range_max", sa.Integer(), nullable=True),
        sa.Column("destination_port_range_min", sa.Integer(), nullable=True),
        sa.Column("destination_port_range_max", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_security_rules_topology_id", "security_rules", ["topology_id"])

    # Network Security Groups
    op.create_table(
        "network_security_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_network_security_groups_topology_id", "network_security_groups", ["topology_id"])
    op.create_index("ix_network_security_groups_ocid", "network_security_groups", ["ocid"])

    # NSG Rules
    op.create_table(
        "nsg_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("nsg_id", sa.String(255), nullable=False),
        sa.Column("direction", sa.String(20), nullable=False),
        sa.Column("protocol", sa.String(10), nullable=False),
        sa.Column("source", sa.String(255), server_default=""),
        sa.Column("destination", sa.String(255), server_default=""),
        sa.Column("source_type", sa.String(50), server_default=""),
        sa.Column("destination_type", sa.String(50), server_default=""),
        sa.Column("source_port_range_min", sa.Integer(), nullable=True),
        sa.Column("source_port_range_max", sa.Integer(), nullable=True),
        sa.Column("destination_port_range_min", sa.Integer(), nullable=True),
        sa.Column("destination_port_range_max", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_nsg_rules_topology_id", "nsg_rules", ["topology_id"])

    # Load Balancers
    op.create_table(
        "load_balancers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("ip_addresses", sa.JSON(), nullable=True),
        sa.Column("shape", sa.String(100), server_default=""),
        sa.Column("subnet_ids", sa.JSON(), nullable=True),
        sa.Column("is_private", sa.Boolean(), server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_load_balancers_topology_id", "load_balancers", ["topology_id"])
    op.create_index("ix_load_balancers_ocid", "load_balancers", ["ocid"])

    # Network Load Balancers
    op.create_table(
        "network_load_balancers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("ip_addresses", sa.JSON(), nullable=True),
        sa.Column("subnet_ids", sa.JSON(), nullable=True),
        sa.Column("is_private", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("is_preserve_source", sa.Boolean(), server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_network_load_balancers_topology_id", "network_load_balancers", ["topology_id"])
    op.create_index("ix_network_load_balancers_ocid", "network_load_balancers", ["ocid"])

    # IPSec Connections
    op.create_table(
        "ipsec_connections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("drg_id", sa.String(255), nullable=False),
        sa.Column("cpe_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("static_routes", sa.JSON(), nullable=True),
        sa.Column("cpe_local_identifier", sa.String(255), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ipsec_connections_topology_id", "ipsec_connections", ["topology_id"])
    op.create_index("ix_ipsec_connections_ocid", "ipsec_connections", ["ocid"])

    # CPEs
    op.create_table(
        "cpes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(50), server_default=""),
        sa.Column("cpe_device_shape_id", sa.String(255), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cpes_topology_id", "cpes", ["topology_id"])
    op.create_index("ix_cpes_ocid", "cpes", ["ocid"])

    # IPSec Tunnels
    op.create_table(
        "ipsec_tunnels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("ipsec_connection_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), server_default=""),
        sa.Column("vpn_ip", sa.String(50), server_default=""),
        sa.Column("cpe_ip", sa.String(50), server_default=""),
        sa.Column("routing", sa.String(50), server_default=""),
        sa.Column("bgp_info", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ipsec_tunnels_topology_id", "ipsec_tunnels", ["topology_id"])
    op.create_index("ix_ipsec_tunnels_ocid", "ipsec_tunnels", ["ocid"])

    # Network Firewalls
    op.create_table(
        "network_firewalls",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), server_default=""),
        sa.Column("subnet_id", sa.String(255), server_default=""),
        sa.Column("vcn_id", sa.String(255), server_default=""),
        sa.Column("policy_id", sa.String(255), server_default=""),
        sa.Column("ip_addresses", sa.JSON(), nullable=True),
        sa.Column("lifecycle_state", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_network_firewalls_topology_id", "network_firewalls", ["topology_id"])
    op.create_index("ix_network_firewalls_ocid", "network_firewalls", ["ocid"])

    # DHCP Options
    op.create_table(
        "dhcp_options",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("vcn_id", sa.String(255), server_default=""),
        sa.Column("display_name", sa.String(255), server_default=""),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dhcp_options_topology_id", "dhcp_options", ["topology_id"])
    op.create_index("ix_dhcp_options_ocid", "dhcp_options", ["ocid"])

    # Public IPs
    op.create_table(
        "public_ips",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), server_default=""),
        sa.Column("ip_address", sa.String(50), server_default=""),
        sa.Column("lifetime", sa.String(50), server_default=""),
        sa.Column("assigned_entity_id", sa.String(255), server_default=""),
        sa.Column("assigned_entity_type", sa.String(100), server_default=""),
        sa.Column("compartment_id", sa.String(255), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_public_ips_topology_id", "public_ips", ["topology_id"])
    op.create_index("ix_public_ips_ocid", "public_ips", ["ocid"])

    # Cross Connects
    op.create_table(
        "cross_connects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), server_default=""),
        sa.Column("compartment_id", sa.String(255), server_default=""),
        sa.Column("location_name", sa.String(255), server_default=""),
        sa.Column("port_speed_shape_name", sa.String(100), server_default=""),
        sa.Column("cross_connect_group_id", sa.String(255), server_default=""),
        sa.Column("lifecycle_state", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cross_connects_topology_id", "cross_connects", ["topology_id"])
    op.create_index("ix_cross_connects_ocid", "cross_connects", ["ocid"])

    # Virtual Circuits
    op.create_table(
        "virtual_circuits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), server_default=""),
        sa.Column("compartment_id", sa.String(255), server_default=""),
        sa.Column("type", sa.String(50), server_default=""),
        sa.Column("bandwidth_shape_name", sa.String(100), server_default=""),
        sa.Column("bgp_session_state", sa.String(50), server_default=""),
        sa.Column("gateway_id", sa.String(255), server_default=""),
        sa.Column("provider_name", sa.String(255), server_default=""),
        sa.Column("region", sa.String(100), server_default=""),
        sa.Column("lifecycle_state", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_virtual_circuits_topology_id", "virtual_circuits", ["topology_id"])
    op.create_index("ix_virtual_circuits_ocid", "virtual_circuits", ["ocid"])

    # DRG Route Distributions
    op.create_table(
        "drg_route_distributions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topology_id", sa.Integer(), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("drg_id", sa.String(255), server_default=""),
        sa.Column("display_name", sa.String(255), server_default=""),
        sa.Column("distribution_type", sa.String(50), server_default=""),
        sa.ForeignKeyConstraint(["topology_id"], ["topologies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_drg_route_distributions_topology_id", "drg_route_distributions", ["topology_id"])
    op.create_index("ix_drg_route_distributions_ocid", "drg_route_distributions", ["ocid"])


def downgrade() -> None:
    tables = [
        "drg_route_distributions", "virtual_circuits", "cross_connects",
        "public_ips", "dhcp_options", "network_firewalls",
        "ipsec_tunnels", "cpes", "ipsec_connections",
        "network_load_balancers", "load_balancers",
        "nsg_rules", "network_security_groups",
        "security_rules", "security_lists",
        "route_rules", "route_tables",
        "local_peering_gateways", "remote_peering_connections",
        "drg_route_rules", "drg_route_tables",
        "drg_attachments", "drgs",
        "service_gateways", "nat_gateways", "internet_gateways",
        "subnets", "vcns", "topologies",
    ]
    for table in tables:
        op.drop_table(table)
