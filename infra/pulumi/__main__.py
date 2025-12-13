"""
Muskul.ai Azure Infrastructure
Main Pulumi program entry point - T039
Orchestrates all Azure resources in dependency order
"""

import pulumi
import pulumi_azure_native as azure_native

# Import all infrastructure modules
from modules.resource_group import create_resource_group
from modules.app_insights import create_application_insights
from modules.vnet import create_virtual_network
from modules.storage import create_storage
from modules.container_registry import create_container_registry
from modules.postgres import create_postgres
from modules.redis import create_redis_cache
from modules.cosmos_mongodb import create_cosmos_mongodb
from modules.service_bus import create_service_bus
from modules.container_apps_environment import create_container_apps_environment
from modules.container_app_backend import create_backend_container_app
from modules.container_app_etl import create_etl_container_app
from modules.container_app_ai_agent import create_ai_agent_container_app

# Get configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
location = config.get("azure-native:location") or "eastus"

pulumi.log.info(f"Deploying muskul-platform infrastructure for environment: {environment}")

# Step 1: Create Resource Group (foundation)
resource_group = create_resource_group(environment, location)

# Step 2: Create Monitoring Infrastructure (needed for Container Apps)
monitoring = create_application_insights(
    environment,
    resource_group.name,
    location,
)

# Step 3: Create Virtual Network with subnets and NSG
network = create_virtual_network(
    environment,
    resource_group.name,
    location,
)

# Step 4: Create Storage Account
storage = create_storage(
    environment,
    resource_group.name,
    location,
)

# Step 5: Create Container Registry
registry = create_container_registry(
    environment,
    resource_group.name,
    location,
)

# Step 6: Create Databases (can be parallel)
postgres = create_postgres(
    environment,
    resource_group.name,
    location,
)

redis = create_redis_cache(
    environment,
    resource_group.name,
    location,
)

cosmos = create_cosmos_mongodb(
    environment,
    resource_group.name,
    location,
)

# Step 7: Create Service Bus
service_bus = create_service_bus(
    environment,
    resource_group.name,
    location,
)

# Step 8: Create Container Apps Environment (depends on monitoring)
container_apps_env = create_container_apps_environment(
    environment,
    resource_group.name,
    location,
    monitoring["workspace"].customer_id,
    monitoring["workspace_shared_keys"].apply(lambda keys: keys.primary_shared_key),
)

# Step 9: Create Container Apps (depend on environment and other services)

# Build connection strings
postgres_connection_string = pulumi.Output.all(
    postgres.fully_qualified_domain_name,
    config.require_secret("postgres_admin_password")
).apply(
    lambda args: f"postgresql://muskul_admin:{args[1]}@{args[0]}:5432/muskuldb?sslmode=require"
)

redis_keys = pulumi.Output.all(resource_group.name, redis.name).apply(
    lambda args: azure_native.cache.list_redis_keys(
        resource_group_name=args[0],
        name=args[1],
    )
)

redis_connection_string = pulumi.Output.all(
    redis.host_name,
    redis.ssl_port,
    redis_keys
).apply(
    lambda args: f"{args[0]}:{args[1]},password={args[2].primary_key},ssl=True,abortConnect=False"
)

cosmos_keys = pulumi.Output.all(resource_group.name, cosmos.name).apply(
    lambda args: azure_native.documentdb.list_database_account_keys(
        resource_group_name=args[0],
        account_name=args[1],
    )
)

cosmos_connection_string = pulumi.Output.all(
    cosmos.name,
    cosmos_keys
).apply(
    lambda args: f"mongodb://{args[0]}:{args[1].primary_master_key}@{args[0]}.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@{args[0]}@"
)

storage_keys = pulumi.Output.all(resource_group.name, storage.name).apply(
    lambda args: azure_native.storage.list_storage_account_keys(
        resource_group_name=args[0],
        account_name=args[1],
    )
)

storage_connection_string = pulumi.Output.all(
    storage.name,
    storage_keys
).apply(
    lambda args: f"DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1].keys[0].value};EndpointSuffix=core.windows.net"
)

servicebus_keys = pulumi.Output.all(
    resource_group.name,
    service_bus.name
).apply(
    lambda args: azure_native.servicebus.list_namespace_keys(
        resource_group_name=args[0],
        namespace_name=args[1],
        authorization_rule_name="RootManageSharedAccessKey",
    )
)

servicebus_connection_string = servicebus_keys.apply(
    lambda keys: keys.primary_connection_string
)

# Get ACR credentials for dev/staging
if environment in ["dev", "staging"]:
    acr_credentials = pulumi.Output.all(resource_group.name, registry.name).apply(
        lambda args: azure_native.containerregistry.list_registry_credentials(
            resource_group_name=args[0],
            registry_name=args[1],
        )
    )
    acr_username = acr_credentials.username
    acr_password = acr_credentials.apply(
        lambda creds: creds.passwords[0].value if creds.passwords else ""
    )
else:
    acr_username = None
    acr_password = None

backend_app = create_backend_container_app(
    environment,
    resource_group.name,
    location,
    container_apps_env.id,
    registry.login_server,
    acr_username,
    acr_password,
    postgres_connection_string,
    redis_connection_string,
    cosmos_connection_string,
    storage_connection_string,
)

etl_app = create_etl_container_app(
    environment,
    resource_group.name,
    location,
    container_apps_env.id,
    registry.login_server,
    acr_username,
    acr_password,
    postgres_connection_string,
    cosmos_connection_string,
    storage_connection_string,
    servicebus_connection_string,
)

ai_agent_app = create_ai_agent_container_app(
    environment,
    resource_group.name,
    location,
    container_apps_env.id,
    registry.login_server,
    acr_username,
    acr_password,
    config.require_secret("openai_api_key") if config.get_secret("openai_api_key") else pulumi.Output.secret(""),
    config.get("openai_endpoint") or "https://api.openai.com/v1",
    postgres_connection_string,
    redis_connection_string,
)

# Export all critical outputs
pulumi.export("environment", environment)
pulumi.export("location", location)

# Resource Group
pulumi.export("resource_group_id", resource_group.id)
pulumi.export("resource_group_name", resource_group.name)

# Network
pulumi.export("vnet_id", network["vnet"].id)
pulumi.export("vnet_name", network["vnet"].name)

# Container Registry
pulumi.export("acr_login_server", registry.login_server)
pulumi.export("acr_name", registry.name)

# Backend URL (primary application endpoint)
pulumi.export("backend_url", backend_app.apply(
    lambda app: f"https://{app.configuration.ingress.fqdn}" if app.configuration.ingress else None
))

# ETL URL
pulumi.export("etl_url", etl_app.apply(
    lambda app: f"https://{app.configuration.ingress.fqdn}" if app.configuration.ingress else None
))

# AI Agent URL
pulumi.export("ai_agent_url", ai_agent_app.apply(
    lambda app: f"https://{app.configuration.ingress.fqdn}" if app.configuration.ingress else None
))

# Database connection strings
pulumi.export("postgres_connection_string", pulumi.Output.secret(postgres_connection_string))
pulumi.export("redis_connection_string", pulumi.Output.secret(redis_connection_string))
pulumi.export("cosmos_connection_string", pulumi.Output.secret(cosmos_connection_string))
pulumi.export("service_bus_connection_string", pulumi.Output.secret(servicebus_connection_string))
pulumi.export("storage_connection_string", pulumi.Output.secret(storage_connection_string))

# Application Insights
pulumi.export("app_insights_connection_string", pulumi.Output.secret(
    monitoring["app_insights"].connection_string
))
pulumi.export("app_insights_instrumentation_key", pulumi.Output.secret(
    monitoring["app_insights"].instrumentation_key
))

# Summary
pulumi.export("deployment_summary", pulumi.Output.all(
    backend_app, registry.login_server
).apply(
    lambda args: {
        "status": "deployed",
        "backend_fqdn": args[0].configuration.ingress.fqdn if args[0].configuration.ingress else "N/A",
        "container_registry": args[1],
        "next_steps": [
            f"1. Build and push images: docker build -t {args[1]}/backend:latest ./backend && docker push {args[1]}/backend:latest",
            "2. Update container apps with new image versions",
            "3. Configure custom domains (optional)",
            "4. Set up CI/CD pipelines",
        ]
    }
))
