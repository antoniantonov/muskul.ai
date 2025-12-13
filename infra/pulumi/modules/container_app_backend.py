"""
Azure Container App for Backend Service
T034: Create Container App for Rust backend with auto-scaling
"""

import pulumi
import pulumi_azure_native as azure_native
from typing import Dict, Optional


def create_backend_container_app(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
    managed_environment_id: pulumi.Input[str],
    acr_login_server: pulumi.Input[str],
    acr_username: Optional[pulumi.Input[str]],
    acr_password: Optional[pulumi.Input[str]],
    database_url: pulumi.Input[str],
    redis_connection_string: pulumi.Input[str],
    cosmos_connection_string: pulumi.Input[str],
    storage_connection_string: pulumi.Input[str],
) -> azure_native.app.ContainerApp:
    """
    Create Container App for backend service
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
        managed_environment_id: Container Apps environment ID
        acr_login_server: ACR login server URL
        acr_username: ACR username (if admin enabled)
        acr_password: ACR password (if admin enabled)
        database_url: PostgreSQL connection string
        redis_connection_string: Redis connection string
        cosmos_connection_string: Cosmos DB connection string
        storage_connection_string: Storage account connection string
    
    Returns:
        ContainerApp: The created backend container app
    """
    
    # Container app name
    app_name = f"muskul-{environment}-backend"
    
    # Image configuration
    image_name = f"{acr_login_server}/muskul-backend:latest"
    
    # Environment-specific resource configuration
    resource_config = {
        "dev": {"cpu": 0.5, "memory": "1Gi", "min_replicas": 1, "max_replicas": 2},
        "staging": {"cpu": 0.75, "memory": "1.5Gi", "min_replicas": 1, "max_replicas": 5},
        "prod": {"cpu": 1.0, "memory": "2Gi", "min_replicas": 2, "max_replicas": 5},
    }
    config = resource_config.get(environment, resource_config["dev"])
    
    # Environment variables for the backend
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
            name="REDIS_URL",
            secret_ref="redis-url",
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
            name="RUST_LOG",
            value="info",
        ),
        azure_native.app.EnvironmentVarArgs(
            name="SERVER_PORT",
            value="8080",
        ),
    ]
    
    # Secrets for sensitive data
    secrets = [
        azure_native.app.SecretArgs(
            name="database-url",
            value=database_url,
        ),
        azure_native.app.SecretArgs(
            name="redis-url",
            value=redis_connection_string,
        ),
        azure_native.app.SecretArgs(
            name="cosmos-connection-string",
            value=cosmos_connection_string,
        ),
        azure_native.app.SecretArgs(
            name="storage-connection-string",
            value=storage_connection_string,
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
        f"backend-app-{environment}",
        container_app_name=app_name,
        resource_group_name=resource_group_name,
        location=location,
        managed_environment_id=managed_environment_id,
        configuration=azure_native.app.ConfigurationArgs(
            ingress=azure_native.app.IngressArgs(
                external=True,
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
            dapr=None,  # Dapr disabled for backend
        ),
        template=azure_native.app.TemplateArgs(
            containers=[
                azure_native.app.ContainerArgs(
                    name="backend",
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
                            initial_delay_seconds=10,
                            period_seconds=30,
                            timeout_seconds=5,
                            failure_threshold=3,
                        ),
                        # Readiness probe
                        azure_native.app.ContainerAppProbeArgs(
                            type="Readiness",
                            http_get=azure_native.app.ContainerAppProbeHttpGetArgs(
                                path="/health/ready",
                                port=8080,
                            ),
                            initial_delay_seconds=5,
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
                    # HTTP scaling rule
                    azure_native.app.ScaleRuleArgs(
                        name="http-scaling",
                        http=azure_native.app.HttpScaleRuleArgs(
                            metadata={
                                "concurrentRequests": "50",
                            },
                        ),
                    ),
                    # CPU scaling rule
                    azure_native.app.ScaleRuleArgs(
                        name="cpu-scaling",
                        custom=azure_native.app.CustomScaleRuleArgs(
                            type="cpu",
                            metadata={
                                "type": "Utilization",
                                "value": "70",
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
            "Service": "backend",
        },
    )
    
    # Export backend app details
    pulumi.export(f"backend_app_id_{environment}", container_app.id)
    pulumi.export(f"backend_app_name_{environment}", container_app.name)
    pulumi.export(f"backend_app_fqdn_{environment}", container_app.configuration.apply(
        lambda c: c.ingress.fqdn if c and c.ingress else None
    ))
    pulumi.export(f"backend_app_url_{environment}", container_app.configuration.apply(
        lambda c: f"https://{c.ingress.fqdn}" if c and c.ingress and c.ingress.fqdn else None
    ))
    
    return container_app
