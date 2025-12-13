"""
Azure Container App for ETL Service
T036: Create Container App for ETL with Service Bus queue trigger and high scaling
"""

import pulumi
import pulumi_azure_native as azure_native
from typing import Optional


def create_etl_container_app(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
    managed_environment_id: pulumi.Input[str],
    acr_login_server: pulumi.Input[str],
    acr_username: Optional[pulumi.Input[str]],
    acr_password: Optional[pulumi.Input[str]],
    database_url: pulumi.Input[str],
    cosmos_connection_string: pulumi.Input[str],
    storage_connection_string: pulumi.Input[str],
    servicebus_connection_string: pulumi.Input[str],
) -> azure_native.app.ContainerApp:
    """
    Create Container App for ETL service with event-driven scaling
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
        managed_environment_id: Container Apps environment ID
        acr_login_server: ACR login server URL
        acr_username: ACR username (if admin enabled)
        acr_password: ACR password (if admin enabled)
        database_url: PostgreSQL connection string
        cosmos_connection_string: Cosmos DB connection string
        storage_connection_string: Storage account connection string
        servicebus_connection_string: Service Bus connection string
    
    Returns:
        ContainerApp: The created ETL container app
    """
    
    # Container app name
    app_name = f"muskul-{environment}-etl"
    
    # Image configuration
    image_name = f"{acr_login_server}/muskul-etl:latest"
    
    # Environment-specific resource configuration
    # ETL needs to scale aggressively based on queue depth
    resource_config = {
        "dev": {"cpu": 0.5, "memory": "1Gi", "min_replicas": 0, "max_replicas": 5},
        "staging": {"cpu": 0.75, "memory": "1.5Gi", "min_replicas": 0, "max_replicas": 8},
        "prod": {"cpu": 1.0, "memory": "2Gi", "min_replicas": 1, "max_replicas": 10},
    }
    config = resource_config.get(environment, resource_config["dev"])
    
    # Environment variables for the ETL
    env_vars = [
        azure_native.app.EnvironmentVarArgs(
            name="ENVIRONMENT",
            value=environment,
        ),
        azure_native.app.EnvironmentVarArgs(
            name="DATABASE_URL",
            secret_ref="database-url",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="COSMOS_CONNECTION_STRING",
            secret_ref="cosmos-connection-string",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="STORAGE_CONNECTION_STRING",
            secret_ref="storage-connection-string",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="SERVICEBUS_CONNECTION_STRING",
            secret_ref="servicebus-connection-string",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="SERVICEBUS_QUEUE_NAME",
            value="fitness-data-ingestion",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="LOG_LEVEL",
            value="INFO",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="BATCH_SIZE",
            value="100",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="MAX_CONCURRENT_SESSIONS",
            value="10",
        ),
    ]
    
    # Secrets for sensitive data
    secrets = [
        azure_native.app.SecretArgs(
            name="database-url",
            value=database_url,
        ),
        azure_native.app.SecretArgs(
            name="cosmos-connection-string",
            value=cosmos_connection_string,
        ),
        azure_native.app.SecretArgs(
            name="storage-connection-string",
            value=storage_connection_string,
        ),
        azure_native.app.SecretArgs(
            name="servicebus-connection-string",
            value=servicebus_connection_string,
        ),
    ]
    
    # Add ACR credentials if provided
    if acr_password:
        secrets.append(
            azure_native.app.SecretArgs(
                name="acr-password",
                value=acr_password,
            )
        )
    
    # Registry configuration
    registries = []
    if acr_username and acr_password:
        registries = [
            azure_native.app.RegistryCredentialsArgs(
                server=acr_login_server,
                username=acr_username,
                password_secret_ref="acr-password",
            )
        ]
    
    # Create Container App
    container_app = azure_native.app.ContainerApp(
        f"etl-app-{environment}",
        container_app_name=app_name,
        resource_group_name=resource_group_name,
        location=location,
        managed_environment_id=managed_environment_id,
        configuration=azure_native.app.ConfigurationArgs(
            # ETL typically doesn't need ingress (queue-driven)
            # But we expose a health endpoint for monitoring
            ingress=azure_native.app.IngressArgs(
                external=False,  # Internal only
                target_port=8080,
                transport="http",
                allow_insecure=False,
                traffic=[
                    azure_native.app.TrafficWeightArgs(
                        latest_revision=True,
                        weight=100,
                    )
                ],
            ),
            secrets=secrets,
            registries=registries if registries else None,
            dapr=None,
        ),
        template=azure_native.app.TemplateArgs(
            containers=[
                azure_native.app.ContainerArgs(
                    name="etl",
                    image=image_name,
                    env=env_vars,
                    resources=azure_native.app.ContainerResourcesArgs(
                        cpu=config["cpu"],
                        memory=config["memory"],
                    ),
                    probes=[
                        # Liveness probe
                        azure_native.app.ContainerAppProbeArgs(
                            type="Liveness",
                            http_get=azure_native.app.ContainerAppProbeHttpGetArgs(
                                path="/health",
                                port=8080,
                            ),
                            initial_delay_seconds=20,
                            period_seconds=30,
                            timeout_seconds=5,
                            failure_threshold=3,
                        ),
                        # Readiness probe
                        azure_native.app.ContainerAppProbeArgs(
                            type="Readiness",
                            http_get=azure_native.app.ContainerAppProbeHttpGetArgs(
                                path="/health",
                                port=8080,
                            ),
                            initial_delay_seconds=10,
                            period_seconds=10,
                            timeout_seconds=3,
                            failure_threshold=3,
                        ),
                    ],
                )
            ],
            scale=azure_native.app.ScaleArgs(
                min_replicas=config["min_replicas"],
                max_replicas=config["max_replicas"],
                rules=[
                    # Service Bus queue scaling rule (primary trigger)
                    azure_native.app.ScaleRuleArgs(
                        name="servicebus-queue-scaling",
                        azure_queue=azure_native.app.QueueScaleRuleArgs(
                            queue_name="fitness-data-ingestion",
                            queue_length=10,  # Scale when queue has 10+ messages per replica
                            auth=[
                                azure_native.app.ScaleRuleAuthArgs(
                                    secret_ref="servicebus-connection-string",
                                    trigger_parameter="connection",
                                )
                            ],
                        ),
                    ),
                    # CPU scaling rule (backup)
                    azure_native.app.ScaleRuleArgs(
                        name="cpu-scaling",
                        custom=azure_native.app.CustomScaleRuleArgs(
                            type="cpu",
                            metadata={
                                "type": "Utilization",
                                "value": "75",
                            },
                        ),
                    ),
                    # Memory scaling rule (backup)
                    azure_native.app.ScaleRuleArgs(
                        name="memory-scaling",
                        custom=azure_native.app.CustomScaleRuleArgs(
                            type="memory",
                            metadata={
                                "type": "Utilization",
                                "value": "80",
                            },
                        ),
                    ),
                ],
            ),
        ),
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
            "Service": "etl",
        },
    )
    
    # Export ETL app details
    pulumi.export(f"etl_app_id_{environment}", container_app.id)
    pulumi.export(f"etl_app_name_{environment}", container_app.name)
    pulumi.export(f"etl_app_fqdn_{environment}", container_app.configuration.apply(
        lambda c: c.ingress.fqdn if c and c.ingress else None
    ))
    
    return container_app
