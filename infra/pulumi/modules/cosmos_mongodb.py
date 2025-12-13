"""
Azure Cosmos DB (MongoDB API) module
T030: Create Cosmos DB with MongoDB API, database, and collections
"""

import pulumi
import pulumi_azure_native as azure_native


def create_cosmos_mongodb(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> azure_native.documentdb.DatabaseAccount:
    """
    Create Azure Cosmos DB account with MongoDB API
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        DatabaseAccount: The created Cosmos DB account
    """
    
    # Cosmos DB account name (must be globally unique, lowercase, 3-44 chars)
    account_name = f"muskul-{environment}-cosmos"
    
    # Create Cosmos DB account with MongoDB API
    cosmos_account = azure_native.documentdb.DatabaseAccount(
        f"cosmos-{environment}",
        account_name=account_name,
        resource_group_name=resource_group_name,
        location=location,
        database_account_offer_type=azure_native.documentdb.DatabaseAccountOfferType.STANDARD,
        kind=azure_native.documentdb.DatabaseAccountKind.MONGO_DB,
        api_properties=azure_native.documentdb.ApiPropertiesArgs(
            server_version="4.2",
        ),
        consistency_policy=azure_native.documentdb.ConsistencyPolicyArgs(
            default_consistency_level=azure_native.documentdb.DefaultConsistencyLevel.SESSION,
        ),
        locations=[
            azure_native.documentdb.LocationArgs(
                location_name=location,
                failover_priority=0,
                is_zone_redundant=False,
            ),
        ],
        enable_automatic_failover=False,
        enable_multiple_write_locations=False,
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Create MongoDB database
    database = azure_native.documentdb.MongoDBResourceMongoDBDatabase(
        f"cosmos-db-{environment}",
        account_name=cosmos_account.name,
        resource_group_name=resource_group_name,
        database_name="muskul",
        resource=azure_native.documentdb.MongoDBDatabaseResourceArgs(
            id="muskul",
        ),
        options=azure_native.documentdb.CreateUpdateOptionsArgs(
            autoscale_settings=azure_native.documentdb.AutoscaleSettingsArgs(
                max_throughput=4000,
            ),
        ),
    )
    
    # Create collection: raw_activities
    raw_activities_collection = azure_native.documentdb.MongoDBResourceMongoDBCollection(
        f"raw-activities-collection-{environment}",
        account_name=cosmos_account.name,
        resource_group_name=resource_group_name,
        database_name=database.name,
        collection_name="raw_activities",
        resource=azure_native.documentdb.MongoDBCollectionResourceArgs(
            id="raw_activities",
            shard_key={
                "provider_user_id": "Hash",
            },
            indexes=[
                azure_native.documentdb.MongoIndexArgs(
                    key=azure_native.documentdb.MongoIndexKeysArgs(
                        keys=["_id"],
                    ),
                    options=azure_native.documentdb.MongoIndexOptionsArgs(
                        unique=True,
                    ),
                ),
                azure_native.documentdb.MongoIndexArgs(
                    key=azure_native.documentdb.MongoIndexKeysArgs(
                        keys=["provider_user_id", "provider_activity_id"],
                    ),
                    options=azure_native.documentdb.MongoIndexOptionsArgs(
                        unique=True,
                    ),
                ),
            ],
        ),
        options=azure_native.documentdb.CreateUpdateOptionsArgs(
            autoscale_settings=azure_native.documentdb.AutoscaleSettingsArgs(
                max_throughput=4000,
            ),
        ),
    )
    
    # Create collection: provider_sync_state
    provider_sync_state_collection = azure_native.documentdb.MongoDBResourceMongoDBCollection(
        f"provider-sync-state-collection-{environment}",
        account_name=cosmos_account.name,
        resource_group_name=resource_group_name,
        database_name=database.name,
        collection_name="provider_sync_state",
        resource=azure_native.documentdb.MongoDBCollectionResourceArgs(
            id="provider_sync_state",
            shard_key={
                "provider_user_id": "Hash",
            },
            indexes=[
                azure_native.documentdb.MongoIndexArgs(
                    key=azure_native.documentdb.MongoIndexKeysArgs(
                        keys=["_id"],
                    ),
                    options=azure_native.documentdb.MongoIndexOptionsArgs(
                        unique=True,
                    ),
                ),
                azure_native.documentdb.MongoIndexArgs(
                    key=azure_native.documentdb.MongoIndexKeysArgs(
                        keys=["provider_user_id", "provider"],
                    ),
                    options=azure_native.documentdb.MongoIndexOptionsArgs(
                        unique=True,
                    ),
                ),
            ],
        ),
        options=azure_native.documentdb.CreateUpdateOptionsArgs(
            autoscale_settings=azure_native.documentdb.AutoscaleSettingsArgs(
                max_throughput=4000,
            ),
        ),
    )
    
    # Export Cosmos DB details
    pulumi.export("cosmos_account_id", cosmos_account.id)
    pulumi.export("cosmos_account_name", cosmos_account.name)
    pulumi.export("cosmos_account_endpoint", cosmos_account.document_endpoint)
    pulumi.export("cosmos_database_name", database.name)
    pulumi.export("cosmos_raw_activities_collection", raw_activities_collection.name)
    pulumi.export("cosmos_provider_sync_state_collection", provider_sync_state_collection.name)
    
    # Export connection string (as secret)
    connection_strings = pulumi.Output.all(resource_group_name, cosmos_account.name).apply(
        lambda args: azure_native.documentdb.list_database_account_connection_strings(
            resource_group_name=args[0],
            account_name=args[1],
        )
    )
    primary_connection_string = connection_strings.apply(
        lambda cs: cs.connection_strings[0].connection_string if cs.connection_strings else ""
    )
    pulumi.export("cosmos_connection_string", pulumi.Output.secret(primary_connection_string))
    
    return cosmos_account
