"""
Azure Storage Account module
T029: Create storage account with containers and lifecycle policies
"""

import pulumi
import pulumi_azure_native as azure_native


def create_storage(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> azure_native.storage.StorageAccount:
    """
    Create Azure Storage Account with blob containers and lifecycle management
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        StorageAccount: The created storage account
    """
    
    # Storage account name (must be globally unique, lowercase alphanumeric, 3-24 chars)
    storage_account_name = f"muskul{environment}storage"[:24]
    
    # Create storage account
    storage_account = azure_native.storage.StorageAccount(
        f"storage-{environment}",
        account_name=storage_account_name,
        resource_group_name=resource_group_name,
        location=location,
        sku=azure_native.storage.SkuArgs(
            name=azure_native.storage.SkuName.STANDARD_LRS,
        ),
        kind=azure_native.storage.Kind.STORAGE_V2,
        enable_https_traffic_only=True,
        minimum_tls_version=azure_native.storage.MinimumTlsVersion.TLS1_2,
        allow_blob_public_access=False,
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
        },
    )
    
    # Create blob container for fitness files
    fitness_files_container = azure_native.storage.BlobContainer(
        f"fitness-files-{environment}",
        container_name="fitness-files",
        account_name=storage_account.name,
        resource_group_name=resource_group_name,
        public_access=azure_native.storage.PublicAccess.NONE,
    )
    
    # Create blob container for ETL temporary files
    etl_temp_container = azure_native.storage.BlobContainer(
        f"etl-temp-{environment}",
        container_name="etl-temp",
        account_name=storage_account.name,
        resource_group_name=resource_group_name,
        public_access=azure_native.storage.PublicAccess.NONE,
    )
    
    # Create lifecycle management policy (delete blobs after 90 days)
    lifecycle_policy = azure_native.storage.ManagementPolicy(
        f"lifecycle-policy-{environment}",
        account_name=storage_account.name,
        resource_group_name=resource_group_name,
        management_policy_name="default",
        policy=azure_native.storage.ManagementPolicySchemaArgs(
            rules=[
                azure_native.storage.ManagementPolicyRuleArgs(
                    name="delete-old-blobs",
                    enabled=True,
                    type=azure_native.storage.RuleType.LIFECYCLE,
                    definition=azure_native.storage.ManagementPolicyDefinitionArgs(
                        actions=azure_native.storage.ManagementPolicyActionArgs(
                            base_blob=azure_native.storage.ManagementPolicyBaseBlobArgs(
                                delete=azure_native.storage.DateAfterModificationArgs(
                                    days_after_modification_greater_than=90,
                                ),
                            ),
                        ),
                        filters=azure_native.storage.ManagementPolicyFilterArgs(
                            blob_types=["blockBlob"],
                            prefix_match=["fitness-files/", "etl-temp/"],
                        ),
                    ),
                ),
            ],
        ),
    )
    
    # Export storage account details
    pulumi.export("storage_account_id", storage_account.id)
    pulumi.export("storage_account_name", storage_account.name)
    pulumi.export("storage_account_primary_endpoints", storage_account.primary_endpoints)
    pulumi.export("fitness_files_container_name", fitness_files_container.name)
    pulumi.export("etl_temp_container_name", etl_temp_container.name)
    
    # Export connection string (as secret)
    storage_keys = pulumi.Output.all(resource_group_name, storage_account.name).apply(
        lambda args: azure_native.storage.list_storage_account_keys(
            resource_group_name=args[0],
            account_name=args[1],
        )
    )
    primary_key = storage_keys.apply(lambda keys: keys.keys[0].value)
    connection_string = pulumi.Output.all(storage_account.name, primary_key).apply(
        lambda args: f"DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1]};EndpointSuffix=core.windows.net"
    )
    pulumi.export("storage_connection_string", pulumi.Output.secret(connection_string))
    
    return storage_account
