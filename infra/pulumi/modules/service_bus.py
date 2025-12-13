"""
Azure Service Bus module
T033: Create Service Bus namespace with queues for fitness data ingestion
"""

import pulumi
import pulumi_azure_native as azure_native


def create_service_bus(
    environment: str,
    resource_group_name: pulumi.Input[str],
    location: str,
) -> azure_native.servicebus.Namespace:
    """
    Create Azure Service Bus namespace with fitness data ingestion queue
    
    Args:
        environment: Environment name (dev, staging, prod)
        resource_group_name: Name of the resource group
        location: Azure region
    
    Returns:
        Namespace: The created Service Bus namespace
    """
    
    # Service Bus namespace name (must be globally unique)
    namespace_name = f"muskul-{environment}-sb"
    
    # Environment-specific SKU configuration
    # Basic: Dev (no topics, no duplicate detection, max 256 KB message size)
    # Standard: Staging/Prod (topics, duplicate detection, max 256 KB, auto-scaling)
    sku_config = {
        "dev": "Basic",
        "staging": "Standard",
        "prod": "Standard",
    }
    sku = sku_config.get(environment, "Basic")
    
    # Create Service Bus namespace
    namespace = azure_native.servicebus.Namespace(
        f"servicebus-{environment}",
        namespace_name=namespace_name,
        resource_group_name=resource_group_name,
        location=location,
        sku=azure_native.servicebus.SBSkuArgs(
            name=sku,
            tier=sku,
        ),
        tags={
            "Environment": environment,
            "Project": "muskul-ai",
            "ManagedBy": "Pulumi",
            "Purpose": "Message queue for fitness data",
        },
    )
    
    # Create queue for fitness data ingestion
    queue_name = "fitness-data-ingestion"
    
    # Queue configuration
    queue_config = {
        # Session support for ordered message processing
        "requires_session": True,
        # Dead letter queue for failed messages
        "dead_lettering_on_message_expiration": True,
        # Max delivery count before moving to dead letter queue
        "max_delivery_count": 10,
        # Message TTL: 14 days
        "default_message_time_to_live": "P14D",
        # Lock duration: 5 minutes
        "lock_duration": "PT5M",
        # Max queue size: 1 GB (dev), 5 GB (staging/prod)
        "max_size_in_megabytes": 1024 if environment == "dev" else 5120,
    }
    
    # Enable duplicate detection for Standard tier
    if sku == "Standard":
        queue_config["requires_duplicate_detection"] = True
        queue_config["duplicate_detection_history_time_window"] = "PT10M"  # 10 minutes
    
    # Create the queue
    queue = azure_native.servicebus.Queue(
        f"queue-fitness-data-{environment}",
        queue_name=queue_name,
        namespace_name=namespace.name,
        resource_group_name=resource_group_name,
        enable_batched_operations=True,
        enable_partitioning=True if sku == "Standard" else False,
        **queue_config,
    )
    
    # Create authorization rule for queue access
    queue_auth_rule = azure_native.servicebus.QueueAuthorizationRule(
        f"queue-auth-rule-{environment}",
        authorization_rule_name="SendListenAccess",
        queue_name=queue.name,
        namespace_name=namespace.name,
        resource_group_name=resource_group_name,
        rights=[
            azure_native.servicebus.AccessRights.SEND,
            azure_native.servicebus.AccessRights.LISTEN,
        ],
    )
    
    # Get connection strings
    connection_strings = pulumi.Output.all(
        resource_group_name,
        namespace.name,
        queue_auth_rule.name,
        queue.name,
    ).apply(
        lambda args: azure_native.servicebus.list_queue_keys(
            resource_group_name=args[0],
            namespace_name=args[1],
            authorization_rule_name=args[2],
            queue_name=args[3],
        )
    )
    
    # Export Service Bus details
    pulumi.export(f"servicebus_id_{environment}", namespace.id)
    pulumi.export(f"servicebus_name_{environment}", namespace.name)
    pulumi.export(f"servicebus_queue_name_{environment}", queue.name)
    pulumi.export(f"servicebus_connection_string_{environment}", pulumi.Output.secret(
        connection_strings.primary_connection_string
    ))
    pulumi.export(f"servicebus_primary_key_{environment}", pulumi.Output.secret(
        connection_strings.primary_key
    ))
    
    return namespace
