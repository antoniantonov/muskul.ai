"""
Azure Virtual Network module
T037: Create VNet with subnets and NSG for container apps and databases
"""

import pulumi
import pulumi_azure_native as azure_native
from typing import Dict


def create_virtual_network(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> Dict[str, any]:
    """
    Create Azure Virtual Network with subnets and Network Security Group
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        Dict containing VNet, subnets, and NSG resources
    """
    
    # VNet name
    vnet_name = f"muskul-{environment}-vnet"
    
    # NSG name
    nsg_name = f"muskul-{environment}-nsg"
    
    # Address spaces by environment
    address_spaces = {
        "dev": "10.0.0.0/16",
        "staging": "10.1.0.0/16",
        "prod": "10.2.0.0/16",
    }
    base_address = address_spaces.get(environment, "10.0.0.0/16")
    
    # Subnet configurations
    subnet_configs = {
        "container-apps-subnet": f"{base_address.rsplit('.', 2)[0]}.1.0/24",
        "postgres-subnet": f"{base_address.rsplit('.', 2)[0]}.2.0/24",
        "redis-subnet": f"{base_address.rsplit('.', 2)[0]}.3.0/24",
    }
    
    # Create Network Security Group
    nsg = azure_native.network.NetworkSecurityGroup(
        f"nsg-{environment}",
        network_security_group_name=nsg_name,
        resource_group_name=resource_group_name,
        location=location,
        security_rules=[
            # Allow HTTP inbound
            azure_native.network.SecurityRuleArgs(
                name="AllowHttpInbound",
                priority=100,
                direction=azure_native.network.SecurityRuleDirection.INBOUND,
                access=azure_native.network.SecurityRuleAccess.ALLOW,
                protocol=azure_native.network.SecurityRuleProtocol.TCP,
                source_port_range="*",
                destination_port_range="80",
                source_address_prefix="*",
                destination_address_prefix="*",
                description="Allow HTTP traffic",
            ),
            # Allow HTTPS inbound
            azure_native.network.SecurityRuleArgs(
                name="AllowHttpsInbound",
                priority=110,
                direction=azure_native.network.SecurityRuleDirection.INBOUND,
                access=azure_native.network.SecurityRuleAccess.ALLOW,
                protocol=azure_native.network.SecurityRuleProtocol.TCP,
                source_port_range="*",
                destination_port_range="443",
                source_address_prefix="*",
                destination_address_prefix="*",
                description="Allow HTTPS traffic",
            ),
            # Allow AMQP for Service Bus
            azure_native.network.SecurityRuleArgs(
                name="AllowAmqpInbound",
                priority=120,
                direction=azure_native.network.SecurityRuleDirection.INBOUND,
                access=azure_native.network.SecurityRuleAccess.ALLOW,
                protocol=azure_native.network.SecurityRuleProtocol.TCP,
                source_port_range="*",
                destination_port_range="5671-5672",
                source_address_prefix="VirtualNetwork",
                destination_address_prefix="*",
                description="Allow AMQP traffic for Service Bus",
            ),
            # Allow PostgreSQL internal traffic
            azure_native.network.SecurityRuleArgs(
                name="AllowPostgresInternal",
                priority=130,
                direction=azure_native.network.SecurityRuleDirection.INBOUND,
                access=azure_native.network.SecurityRuleAccess.ALLOW,
                protocol=azure_native.network.SecurityRuleProtocol.TCP,
                source_port_range="*",
                destination_port_range="5432",
                source_address_prefix="VirtualNetwork",
                destination_address_prefix="VirtualNetwork",
                description="Allow PostgreSQL traffic within VNet",
            ),
            # Allow Redis internal traffic
            azure_native.network.SecurityRuleArgs(
                name="AllowRedisInternal",
                priority=140,
                direction=azure_native.network.SecurityRuleDirection.INBOUND,
                access=azure_native.network.SecurityRuleAccess.ALLOW,
                protocol=azure_native.network.SecurityRuleProtocol.TCP,
                source_port_range="*",
                destination_port_range="6379-6380",
                source_address_prefix="VirtualNetwork",
                destination_address_prefix="VirtualNetwork",
                description="Allow Redis traffic within VNet",
            ),
        ],
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Create Virtual Network
    vnet = azure_native.network.VirtualNetwork(
        f"vnet-{environment}",
        virtual_network_name=vnet_name,
        resource_group_name=resource_group_name,
        location=location,
        address_space=azure_native.network.AddressSpaceArgs(
            address_prefixes=[base_address],
        ),
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Create subnets
    subnets = {}
    for subnet_name, address_prefix in subnet_configs.items():
        subnet = azure_native.network.Subnet(
            f"subnet-{subnet_name}-{environment}",
            subnet_name=subnet_name,
            resource_group_name=resource_group_name,
            virtual_network_name=vnet.name,
            address_prefix=address_prefix,
            network_security_group=azure_native.network.NetworkSecurityGroupArgs(
                id=nsg.id,
            ),
            # Enable service endpoints for databases
            service_endpoints=[
                azure_native.network.ServiceEndpointPropertiesFormatArgs(
                    service="Microsoft.Sql",
                ),
                azure_native.network.ServiceEndpointPropertiesFormatArgs(
                    service="Microsoft.Storage",
                ),
            ] if "postgres" in subnet_name or "redis" in subnet_name else None,
            # Delegation for Container Apps subnet
            delegations=[
                azure_native.network.DelegationArgs(
                    name="Microsoft.App.environments",
                    service_name="Microsoft.App/environments",
                )
            ] if subnet_name == "container-apps-subnet" else None,
        )
        subnets[subnet_name] = subnet
    
    # Export VNet details
    pulumi.export("vnet_id", vnet.id)
    pulumi.export("vnet_name", vnet.name)
    pulumi.export("vnet_address_space", base_address)
    pulumi.export("nsg_id", nsg.id)
    pulumi.export("nsg_name", nsg.name)
    
    # Export subnet IDs
    for subnet_name, subnet in subnets.items():
        pulumi.export(f"subnet_{subnet_name}_id", subnet.id)
        pulumi.export(f"subnet_{subnet_name}_address", subnet_configs[subnet_name])
    
    return {
        "vnet": vnet,
        "nsg": nsg,
        "subnets": subnets,
    }
