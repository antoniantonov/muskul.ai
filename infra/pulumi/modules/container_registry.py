"""
Azure Container Registry module
T028: Create ACR with environment-specific configuration
"""

import pulumi
import pulumi_azure_native as azure_native
from typing import Dict


def create_container_registry(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> azure_native.containerregistry.Registry:
    """
    Create Azure Container Registry with environment-specific settings
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        Registry: The created container registry
    """
    
    # Registry name (must be globally unique, alphanumeric only)
    registry_name = f"muskul{environment}acr"
    
    # Environment-specific SKU configuration
    sku_map = {
        "dev": "Basic",
        "staging": "Standard",
        "prod": "Standard",
    }
    sku = sku_map.get(environment, "Basic")
    
    # Admin user enabled for dev/staging, disabled for prod (use managed identity)
    admin_enabled = environment in ["dev", "staging"]
    
    # Identity configuration (managed identity for prod)
    identity = None
    if environment == "prod":
        identity = azure_native.containerregistry.IdentityPropertiesArgs(
            type=azure_native.containerregistry.ResourceIdentityType.SYSTEM_ASSIGNED,
        )
    
    # Create container registry
    registry = azure_native.containerregistry.Registry(
        f"acr-{environment}",
        registry_name=registry_name,
        resource_group_name=resource_group_name,
        location=location,
        sku=azure_native.containerregistry.SkuArgs(
            name=sku,
        ),
        admin_user_enabled=admin_enabled,
        identity=identity,
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Export registry details
    pulumi.export("acr_id", registry.id)
    pulumi.export("acr_name", registry.name)
    pulumi.export("acr_login_server", registry.login_server)
    
    if admin_enabled:
        # Export admin credentials for dev/staging
        credentials = pulumi.Output.all(resource_group_name, registry_name).apply(
            lambda args: azure_native.containerregistry.list_registry_credentials(
                resource_group_name=args[0],
                registry_name=args[1],
            )
        )
        pulumi.export("acr_admin_username", credentials.username)
        pulumi.export("acr_admin_password", pulumi.Output.secret(
            credentials.passwords[0].value if credentials.passwords else ""
        ))
    
    if environment == "prod":
        pulumi.export("acr_principal_id", registry.identity.apply(
            lambda i: i.principal_id if i else None
        ))
    
    return registry
