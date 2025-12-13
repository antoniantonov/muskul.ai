# Muskul.ai Pulumi Infrastructure

Complete Azure infrastructure as code for the muskul.ai fitness data platform using Pulumi and Python.

## Architecture Overview

This infrastructure deploys a complete multi-tier application stack on Azure:

### Core Components

- **Resource Group**: Logical container for all resources
- **Virtual Network**: Isolated network with dedicated subnets
  - Container Apps subnet (with delegation)
  - PostgreSQL subnet (with service endpoints)
  - Redis subnet (with service endpoints)
- **Network Security Group**: HTTP/HTTPS/AMQP/database traffic rules
- **Container Registry**: Private Docker image repository
- **Log Analytics + Application Insights**: Comprehensive monitoring and logging

### Compute Layer

- **Container Apps Environment**: Managed Kubernetes environment
- **Backend Container App**: Rust API service (main application)
- **ETL Container App**: Python data processing pipeline
- **AI Agent Container App**: Python AI/ML service

### Data Layer

- **PostgreSQL Flexible Server**: Primary relational database
- **Redis Cache**: Session storage and caching
- **Cosmos DB (MongoDB API)**: Document storage for AI/ML data
- **Azure Storage**: Blob storage for raw data files

### Messaging

- **Service Bus**: Message queue for async processing and inter-service communication

## Prerequisites

### Required Tools

```bash
# Install Pulumi CLI
curl -fsSL https://get.pulumi.com | sh

# Install Azure CLI
brew install azure-cli  # macOS
# or use: https://docs.microsoft.com/cli/azure/install-azure-cli

# Install Python 3.8+
python3 --version

# Install dependencies
cd infra/pulumi
pip install -r requirements.txt
```

### Azure Authentication

```bash
# Login to Azure
az login

# Set default subscription (if you have multiple)
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Verify authentication
az account show
```

## Getting Started

### 1. Initialize Pulumi Backend

Choose between Pulumi Cloud (recommended) or local/self-hosted backend:

#### Option A: Pulumi Cloud (Recommended)

```bash
# Login to Pulumi Cloud (free for individuals)
pulumi login

# Creates account at https://app.pulumi.com if needed
```

#### Option B: Local Backend

```bash
# Use local file system
pulumi login --local

# Or use Azure Blob Storage
pulumi login azblob://muskulpulumistate
```

### 2. Create a New Stack

A stack represents an isolated environment (dev, staging, prod):

```bash
cd infra/pulumi

# Create development stack
pulumi stack init dev

# Or staging
pulumi stack init staging

# Or production
pulumi stack init prod
```

### 3. Configure Stack

Set required configuration values for your stack:

```bash
# Set Azure region
pulumi config set azure-native:location eastus

# Set environment name (should match stack name)
pulumi config set environment dev

# Set database admin password (stored encrypted)
pulumi config set --secret postgres_admin_password "YourSecurePassword123!"

# Optional: Configure specific resource settings
pulumi config set postgres_sku_name "B_Standard_B1ms"  # Basic tier for dev
pulumi config set redis_sku_name "Basic"               # Basic tier for dev
```

#### Configuration by Environment

**Development:**
```bash
pulumi stack select dev
pulumi config set environment dev
pulumi config set azure-native:location eastus
pulumi config set --secret postgres_admin_password "DevPassword123!"
```

**Staging:**
```bash
pulumi stack select staging
pulumi config set environment staging
pulumi config set azure-native:location westus2
pulumi config set --secret postgres_admin_password "StagingPassword123!"
pulumi config set postgres_sku_name "GP_Standard_D2s_v3"  # General Purpose
```

**Production:**
```bash
pulumi stack select prod
pulumi config set environment prod
pulumi config set azure-native:location eastus2
pulumi config set --secret postgres_admin_password "ProdPassword123!"
pulumi config set postgres_sku_name "GP_Standard_D4s_v3"  # Higher tier
pulumi config set redis_sku_name "Premium"                 # Premium tier
```

### 4. Preview Changes

Preview what will be created before deploying:

```bash
# Dry-run to see planned changes
pulumi preview

# Save preview to file
pulumi preview --json > preview.json
```

### 5. Deploy Infrastructure

Deploy all resources to Azure:

```bash
# Deploy with automatic approval
pulumi up --yes

# Deploy with manual confirmation
pulumi up

# Deploy specific resources only (advanced)
pulumi up --target urn:pulumi:dev::muskul-platform::azure-native:resources:ResourceGroup::muskul-dev-rg
```

Deployment typically takes 10-15 minutes for a full stack.

## Working with Stacks

### List Available Stacks

```bash
pulumi stack ls
```

### Switch Between Stacks

```bash
# Switch to staging
pulumi stack select staging

# Switch to production
pulumi stack select prod
```

### View Stack Outputs

After deployment, view exported values:

```bash
# View all outputs
pulumi stack output

# Get specific output
pulumi stack output backend_url
pulumi stack output acr_login_server

# Get secret outputs (decrypted)
pulumi stack output --show-secrets postgres_connection_string
```

### View Stack State

```bash
# Show current stack resources
pulumi stack

# Export stack state to JSON
pulumi stack export > stack-state.json

# Import stack state from JSON
pulumi stack import < stack-state.json
```

## Post-Deployment Steps

### 1. Build and Push Container Images

```bash
# Get ACR login server
ACR_SERVER=$(pulumi stack output acr_login_server)

# Login to ACR
az acr login --name ${ACR_SERVER%%.*}

# Build and push backend
docker build -t $ACR_SERVER/backend:latest ./backend
docker push $ACR_SERVER/backend:latest

# Build and push ETL
docker build -t $ACR_SERVER/etl:latest ./etl
docker push $ACR_SERVER/etl:latest

# Build and push AI agent
docker build -t $ACR_SERVER/ai-agent:latest ./ai-agent-service
docker push $ACR_SERVER/ai-agent:latest
```

### 2. Update Container Apps

After pushing images, update the container apps:

```bash
# Backend app will auto-update if configured with revisionMode: "Single"
# Or manually trigger revision:
pulumi up --yes
```

### 3. Initialize Database Schema

```bash
# Get connection strings
POSTGRES_CONN=$(pulumi stack output --show-secrets postgres_connection_string)

# Run migrations (adjust based on your migration tool)
cd backend
DATABASE_URL=$POSTGRES_CONN cargo run --bin migrate
```

### 4. Verify Deployment

```bash
# Get backend URL
BACKEND_URL=$(pulumi stack output backend_url)

# Test health endpoint
curl $BACKEND_URL/health

# Test API
curl $BACKEND_URL/api/v1/activities
```

## Updating Infrastructure

### Update Specific Resources

```bash
# Make changes to modules/postgres.py or other modules
vim modules/postgres.py

# Preview changes
pulumi preview

# Apply changes
pulumi up
```

### Refresh State

Sync Pulumi state with actual Azure resources:

```bash
pulumi refresh
```

## Destroying Infrastructure

### Destroy Entire Stack

```bash
# Preview what will be deleted
pulumi destroy --preview

# Destroy with confirmation
pulumi destroy

# Destroy without confirmation (dangerous!)
pulumi destroy --yes
```

### Remove Stack

After destroying resources, remove the stack configuration:

```bash
pulumi stack rm dev
```

## Troubleshooting

### Common Issues

**Authentication Errors:**
```bash
# Re-authenticate with Azure
az login
az account show

# Verify Pulumi is authenticated
pulumi whoami
```

**State Conflicts:**
```bash
# Cancel ongoing operations
pulumi cancel

# Refresh state from Azure
pulumi refresh
```

**Resource Already Exists:**
```bash
# Import existing resource into Pulumi state
pulumi import azure-native:resources:ResourceGroup muskul-dev-rg /subscriptions/SUBSCRIPTION_ID/resourceGroups/muskul-dev-rg
```

**Networking Issues:**
```bash
# Check NSG rules
az network nsg rule list --resource-group muskul-dev-rg --nsg-name muskul-dev-nsg

# Check subnet configuration
az network vnet subnet list --resource-group muskul-dev-rg --vnet-name muskul-dev-vnet
```

### Debugging

Enable detailed logging:

```bash
# Verbose output
pulumi up --verbose

# Debug level logging
pulumi up --logtostderr --logflow -v=9 2> pulumi.log
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
    paths:
      - 'infra/pulumi/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: pulumi/actions@v4
        with:
          command: up
          stack-name: prod
          work-dir: infra/pulumi
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          ARM_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Module Reference

### modules/resource_group.py (T027)
Creates Azure Resource Group with tags and naming convention.

### modules/container_registry.py (T028)
Creates ACR with environment-specific SKU and admin/managed identity auth.

### modules/storage.py (T029)
Creates Storage Account with blob containers and lifecycle policies.

### modules/postgres.py (T030)
Creates PostgreSQL Flexible Server with firewall rules and high availability options.

### modules/redis.py (T031)
Creates Redis Cache with SSL and data persistence configuration.

### modules/cosmos_mongodb.py (T032)
Creates Cosmos DB with MongoDB API for document storage.

### modules/service_bus.py (T033)
Creates Service Bus namespace with queues and topics.

### modules/container_apps_environment.py (T034)
Creates Container Apps Environment with Log Analytics integration.

### modules/container_app_backend.py (T035)
Deploys Rust backend API as Container App with scaling rules.

### modules/container_app_etl.py (T036)
Deploys Python ETL pipeline as Container App.

### modules/vnet.py (T037)
Creates Virtual Network with subnets and NSG rules.

### modules/app_insights.py (T038)
Creates Application Insights and Log Analytics workspace.

### __main__.py (T039)
Orchestrates all modules in dependency order and exports outputs.

## Cost Optimization

### Development Environment

- Use Basic/Free tiers where available
- Schedule auto-shutdown for non-business hours
- Use single replicas for container apps
- Shorter retention periods (30 days)

### Production Environment

- Use appropriate tiers based on load
- Enable auto-scaling
- Implement geo-redundancy
- Configure backup policies
- Use reserved capacity for predictable workloads

### Cost Monitoring

```bash
# View estimated costs
az consumption usage list

# Set up budget alerts in Azure Portal
```

## Security Best Practices

1. **Secrets Management**: All sensitive values stored encrypted in Pulumi config
2. **Network Isolation**: Resources deployed in VNet with NSG rules
3. **Identity Management**: Use Managed Identities for production
4. **SSL/TLS**: Enforced for all data in transit
5. **Firewall Rules**: Restrict database access to specific subnets
6. **RBAC**: Apply least-privilege access principles

## Support

- **Pulumi Documentation**: https://www.pulumi.com/docs/
- **Azure Documentation**: https://docs.microsoft.com/azure/
- **Project Issues**: https://github.com/antoniantonov/muskul.ai/issues

## License

See main project LICENSE file.
