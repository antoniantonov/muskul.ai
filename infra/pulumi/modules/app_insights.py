"""
Azure Application Insights module
T038: Create Application Insights with Log Analytics workspace
"""

import pulumi
import pulumi_azure_native as azure_native
from typing import Dict


def create_application_insights(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> Dict[str, any]:
    """
    Create Azure Application Insights with Log Analytics workspace
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        Dict containing Application Insights and Log Analytics workspace
    """
    
    # Log Analytics workspace name
    workspace_name = f"muskul-{environment}-logs"
    
    # Application Insights name
    app_insights_name = f"muskul-{environment}-ai"
    
    # Retention days by environment
    retention_days = {
        "dev": 30,
        "staging": 60,
        "prod": 90,
    }
    retention = retention_days.get(environment, 30)
    
    # Create Log Analytics Workspace
    workspace = azure_native.operationalinsights.Workspace(
        f"log-analytics-{environment}",
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        location=location,
        sku=azure_native.operationalinsights.WorkspaceSkuArgs(
            name="PerGB2018",
        ),
        retention_in_days=retention,
        public_network_access_for_ingestion="Enabled",
        public_network_access_for_query="Enabled",
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Get workspace shared keys for Container Apps environment
    workspace_shared_keys = pulumi.Output.all(
        resource_group_name, workspace.name
    ).apply(
        lambda args: azure_native.operationalinsights.get_shared_keys(
            resource_group_name=args[0],
            workspace_name=args[1],
        )
    )
    
    # Create Application Insights
    app_insights = azure_native.insights.Component(
        f"app-insights-{environment}",
        resource_name=app_insights_name,
        resource_group_name=resource_group_name,
        location=location,
        kind="web",
        application_type="web",
        workspace_resource_id=workspace.id,
        ingestion_mode="LogAnalytics",
        public_network_access_for_ingestion="Enabled",
        public_network_access_for_query="Enabled",
        retention_in_days=retention,
        sampling_percentage=100.0 if environment == "dev" else 10.0,
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Export Log Analytics details
    pulumi.export("log_analytics_workspace_id", workspace.id)
    pulumi.export("log_analytics_workspace_name", workspace.name)
    pulumi.export("log_analytics_customer_id", workspace.customer_id)
    pulumi.export("log_analytics_workspace_key", pulumi.Output.secret(
        workspace_shared_keys.apply(lambda keys: keys.primary_shared_key)
    ))
    
    # Export Application Insights details
    pulumi.export("app_insights_id", app_insights.id)
    pulumi.export("app_insights_name", app_insights.name)
    pulumi.export("app_insights_instrumentation_key", pulumi.Output.secret(
        app_insights.instrumentation_key
    ))
    pulumi.export("app_insights_connection_string", pulumi.Output.secret(
        app_insights.connection_string
    ))
    pulumi.export("app_insights_app_id", app_insights.app_id)
    
    return {
        "workspace": workspace,
        "workspace_shared_keys": workspace_shared_keys,
        "app_insights": app_insights,
    }
