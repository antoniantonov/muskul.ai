"""
Azure Resource Group module
T027: Create resource group with name, tags, and exports
"""

import pulumi
import pulumi_azure_native as azure_native


def create_resource_group(environment: str, location: str) -> azure_native.resources.ResourceGroup:
    """
    Create Azure Resource Group for the muskul.ai platform
    
    Args:
        environment: Environment name (dev, staging, prod)
        location: Azure region (e.g., eastus, westus2)
    
    Returns:
        ResourceGroup: The created resource group
    """
    
    # Define common tags
    tags = {
        "Environment": environment,
        "Project": "muskul-ai",
        "ManagedBy": "Pulumi",
        "Purpose": "fitness-data-platform",
    }
    
    # Create resource group with naming convention
    resource_group_name = f"muskul-{environment}-rg"
    
    resource_group = azure_native.resources.ResourceGroup(
        resource_group_name,
        resource_group_name=resource_group_name,
        location=location,
        tags=tags,
    )
    
    # Export resource group details
    pulumi.export("resource_group_id", resource_group.id)
    pulumi.export("resource_group_name", resource_group.name)
    pulumi.export("resource_group_location", resource_group.location)
    
    return resource_group
