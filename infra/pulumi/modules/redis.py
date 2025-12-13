"""
Azure Cache for Redis module
T032: Create Redis cache with environment-specific SKU and configuration
"""

import pulumi
import pulumi_azure_native as azure_native


def create_redis_cache(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> azure_native.cache.Redis:
    """
    Create Azure Cache for Redis with environment-specific configuration
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        Redis: The created Redis cache instance
    """
    
    # Redis cache name (must be globally unique, lowercase alphanumeric and hyphens)
    redis_name = f"muskul-{environment}-redis"
    
    # Environment-specific SKU configuration
    # Basic: Dev (no SLA, no replication)
    # Standard: Staging (replication, 99.9% SLA)
    # Premium: Production (replication, clustering, persistence, 99.95% SLA)
    sku_config = {
        "dev": {
            "name": "Basic",
            "family": "C",
            "capacity": 0,  # 250 MB
        },
        "staging": {
            "name": "Standard",
            "family": "C",
            "capacity": 1,  # 1 GB
        },
        "prod": {
            "name": "Premium",
            "family": "P",
            "capacity": 1,  # 6 GB
        },
    }
    sku = sku_config.get(environment, sku_config["dev"])
    
    # Redis configuration
    redis_config = {
        "maxmemory-policy": "allkeys-lru",  # Evict least recently used keys
        "maxmemory-reserved": "50" if environment == "dev" else "125",  # MB reserved for non-cache ops
    }
    
    # Additional config for Premium
    if environment == "prod":
        redis_config["rdb-backup-enabled"] = "true"
        redis_config["rdb-backup-frequency"] = "60"  # 60 minutes
        redis_config["rdb-storage-connection-string"] = ""  # To be set with storage account
    
    # Create Redis cache
    redis_cache = azure_native.cache.Redis(
        f"redis-{environment}",
        name=redis_name,
        resource_group_name=resource_group_name,
        location=location,
        sku=azure_native.cache.SkuArgs(
            name=sku["name"],
            family=sku["family"],
            capacity=sku["capacity"],
        ),
        enable_non_ssl_port=False,  # Enforce SSL
        minimum_tls_version="1.2",
        public_network_access="Enabled",  # Set to "Disabled" if using VNet
        redis_configuration=redis_config,
        redis_version="6",  # Redis 6.x
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
            "Purpose": "Session and cache storage",
        },
    )
    
    # Get Redis keys
    redis_keys = pulumi.Output.all(resource_group_name, redis_name).apply(
        lambda args: azure_native.cache.list_redis_keys(
            resource_group_name=args[0],
            name=args[1],
        )
    )
    
    # Export Redis details
    pulumi.export(f"redis_id_{environment}", redis_cache.id)
    pulumi.export(f"redis_name_{environment}", redis_cache.name)
    pulumi.export(f"redis_host_{environment}", redis_cache.host_name)
    pulumi.export(f"redis_ssl_port_{environment}", redis_cache.ssl_port)
    pulumi.export(f"redis_primary_key_{environment}", pulumi.Output.secret(
        redis_keys.primary_key
    ))
    pulumi.export(f"redis_connection_string_{environment}", pulumi.Output.secret(
        pulumi.Output.all(redis_cache.host_name, redis_cache.ssl_port, redis_keys.primary_key).apply(
            lambda args: f"{args[0]}:{args[1]},password={args[2]},ssl=True,abortConnect=False"
        )
    ))
    
    return redis_cache
