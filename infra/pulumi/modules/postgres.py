"""
Azure Database for PostgreSQL Flexible Server module
T031: Create PostgreSQL Flexible Server with database, firewall rules, and extensions
"""

import pulumi
import pulumi_azure_native as azure_native


def create_postgres(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> azure_native.dbforpostgresql.Server:
    """
    Create Azure Database for PostgreSQL Flexible Server
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        Server: The created PostgreSQL Flexible Server
    """
    
    # Server name (must be globally unique)
    server_name = f"muskul-{environment}-postgres"
    
    # Environment-specific SKU configuration
    sku_map = {
        "dev": {
            "name": "Standard_B1ms",
            "tier": "Burstable",
        },
        "staging": {
            "name": "Standard_D2s_v3",
            "tier": "GeneralPurpose",
        },
        "prod": {
            "name": "Standard_D4s_v3",
            "tier": "GeneralPurpose",
        },
    }
    sku_config = sku_map.get(environment, sku_map["dev"])
    
    # Storage size in MB (32 GB for dev, 128 GB for staging/prod)
    storage_size_gb = 32 if environment == "dev" else 128
    
    # Get admin password from config (or use a default for dev)
    config = pulumi.Config()
    admin_password = config.get_secret("postgres_admin_password") or pulumi.Output.secret("ChangeMe123!")
    
    # Create PostgreSQL Flexible Server
    postgres_server = azure_native.dbforpostgresql.Server(
        f"postgres-{environment}",
        server_name=server_name,
        resource_group_name=resource_group_name,
        location=location,
        sku=azure_native.dbforpostgresql.SkuArgs(
            name=sku_config["name"],
            tier=sku_config["tier"],
        ),
        storage=azure_native.dbforpostgresql.StorageArgs(
            storage_size_gb=storage_size_gb,
        ),
        version=azure_native.dbforpostgresql.ServerVersion.SERVER_VERSION_14,
        administrator_login="muskul_admin",
        administrator_login_password=admin_password,
        high_availability=azure_native.dbforpostgresql.HighAvailabilityArgs(
            mode=azure_native.dbforpostgresql.HighAvailabilityMode.DISABLED,
        ),
        backup=azure_native.dbforpostgresql.BackupArgs(
            backup_retention_days=7,
            geo_redundant_backup=azure_native.dbforpostgresql.GeoRedundantBackupEnum.DISABLED,
        ),
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Create database
    database = azure_native.dbforpostgresql.Database(
        f"postgres-db-{environment}",
        database_name="muskul",
        server_name=postgres_server.name,
        resource_group_name=resource_group_name,
        charset="UTF8",
        collation="en_US.utf8",
    )
    
    # Create firewall rule to allow Azure services
    azure_services_firewall = azure_native.dbforpostgresql.FirewallRule(
        f"postgres-fw-azure-{environment}",
        firewall_rule_name="AllowAzureServices",
        server_name=postgres_server.name,
        resource_group_name=resource_group_name,
        start_ip_address="0.0.0.0",
        end_ip_address="0.0.0.0",
    )
    
    # For dev environment, allow all IPs (for development access)
    if environment == "dev":
        dev_firewall = azure_native.dbforpostgresql.FirewallRule(
            f"postgres-fw-dev-{environment}",
            firewall_rule_name="AllowAllIPs",
            server_name=postgres_server.name,
            resource_group_name=resource_group_name,
            start_ip_address="0.0.0.0",
            end_ip_address="255.255.255.255",
        )
    
    # Enable uuid-ossp extension
    uuid_extension = azure_native.dbforpostgresql.Configuration(
        f"postgres-ext-uuid-{environment}",
        configuration_name="azure.extensions",
        server_name=postgres_server.name,
        resource_group_name=resource_group_name,
        value="uuid-ossp",
        source="user-override",
    )
    
    # Export PostgreSQL details
    pulumi.export("postgres_server_id", postgres_server.id)
    pulumi.export("postgres_server_name", postgres_server.name)
    pulumi.export("postgres_server_fqdn", postgres_server.fully_qualified_domain_name)
    pulumi.export("postgres_database_name", database.name)
    pulumi.export("postgres_admin_username", "muskul_admin")
    
    # Export connection string (as secret)
    connection_string = pulumi.Output.all(
        postgres_server.fully_qualified_domain_name,
        database.name,
        admin_password
    ).apply(
        lambda args: f"postgresql://muskul_admin:{args[2]}@{args[0]}:5432/{args[1]}?sslmode=require"
    )
    pulumi.export("postgres_connection_string", pulumi.Output.secret(connection_string))
    
    return postgres_server
