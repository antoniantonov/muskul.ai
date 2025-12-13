"""
Azure Container Apps Environment module
Shared environment for all Container Apps
"""

import pulumi
import pulumi_azure_native as azure_native


def create_container_apps_environment(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
    log_analytics_workspace_id: pulumi.Input[str],
    log_analytics_workspace_key: pulumi.Input[str],
) -> azure_native.app.ManagedEnvironment:
    """
    Create Azure Container Apps Environment for hosting container apps
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
        log_analytics_workspace_id: Log Analytics workspace ID for logs
        log_analytics_workspace_key: Log Analytics workspace shared key
    
    Returns:
        ManagedEnvironment: The created Container Apps environment
    """
    
    # Container Apps environment name
    env_name = f"muskul-{environment}-cae"
    
    # Create Container Apps environment
    managed_env = azure_native.app.ManagedEnvironment(
        f"container-apps-env-{environment}",
        environment_name=env_name,
        resource_group_name=resource_group_name,
        location=location,
        app_logs_configuration=azure_native.app.AppLogsConfigurationArgs(
            destination="log-analytics",
            log_analytics_configuration=azure_native.app.LogAnalyticsConfigurationArgs(
                customer_id=log_analytics_workspace_id,
                shared_key=log_analytics_workspace_key,
            ),
        ),
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Export environment details
    pulumi.export(f"container_apps_env_id_{environment}", managed_env.id)
    pulumi.export(f"container_apps_env_name_{environment}", managed_env.name)
    pulumi.export(f"container_apps_env_default_domain_{environment}", managed_env.default_domain)
    
    return managed_env
