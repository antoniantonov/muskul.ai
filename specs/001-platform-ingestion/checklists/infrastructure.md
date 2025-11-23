# Infrastructure (Pulumi/Azure) Quality Checklist

**Agent**: `@pulumi` | **Scope**: `infra/**/*.py`, `.github/workflows/*-deploy.yml`

This checklist ensures all Infrastructure as Code (IaC) and CI/CD configurations meet production-grade quality standards before marking tasks complete.

---

## Code Quality

- [ ] **Linting**: All code passes `ruff check .` with zero errors/warnings
- [ ] **Formatting**: All code passes `black --check .` with no changes needed
- [ ] **Type Hints**: All Pulumi resources have type hints
- [ ] **Resource Naming**: All resources follow Azure naming conventions (lowercase, hyphens, service prefix)
  - Example: `muskul-backend-prod-app`, `muskul-db-prod-pg`, `muskul-kv-prod`
- [ ] **Code Organization**: Resources organized by service/environment in separate files
- [ ] **No Hardcoded Values**: All environment-specific values in Pulumi config or variables
- [ ] **Comments**: Complex resource configurations have explanatory comments

---

## Infrastructure as Code Best Practices

- [ ] **Idempotent Resources**: Resources can be re-applied without side effects
- [ ] **Stack Configurations**: Separate stacks for dev, staging, production environments
- [ ] **State Management**: Pulumi state managed in Pulumi Cloud or Azure Blob Storage
- [ ] **Import Existing Resources**: Existing Azure resources imported (not recreated)
- [ ] **Resource Dependencies**: Explicit dependencies declared with `pulumi.DependsOn()`
- [ ] **Output Exports**: Important values exported (app URLs, connection strings, resource IDs)
- [ ] **Secrets Management**: Sensitive values marked as secrets with `pulumi.secret()`
- [ ] **Resource Tagging**: All resources tagged with metadata (see below)

---

## Resource Tagging

All Azure resources MUST be tagged with:
- [ ] **environment**: `dev`, `staging`, `production`
- [ ] **project**: `muskul-ai`
- [ ] **managed-by**: `pulumi`
- [ ] **cost-center**: (if applicable) for cost allocation
- [ ] **owner**: Team or individual responsible for resource
- [ ] **created-date**: ISO 8601 date when resource was created

Example:
```python
tags={
    "environment": "production",
    "project": "muskul-ai",
    "managed-by": "pulumi",
    "owner": "platform-team",
    "created-date": "2025-11-23"
}
```

---

## Security

- [ ] **Managed Identities**: All services use managed identities (no service principals with passwords)
- [ ] **Key Vault Integration**: Secrets stored in Azure Key Vault (not environment variables)
- [ ] **Private Endpoints**: Databases use private endpoints (not public IPs)
- [ ] **Network Security Groups (NSG)**: NSG rules configured (allow only necessary ports)
- [ ] **RBAC Assignments**: Role-Based Access Control configured (least privilege principle)
  - Service → Key Vault: `Key Vault Secrets User` role
  - Service → Database: `Contributor` role (or custom role)
- [ ] **HTTPS Only**: All endpoints require HTTPS (TLS 1.2+)
- [ ] **Disable Public Access**: Databases have public access disabled (require private endpoint or VPN)
- [ ] **Firewall Rules**: Only necessary IP ranges whitelisted

---

## Cost Optimization

- [ ] **Environment-Specific Sizing**: Resources sized appropriately per environment
  - **Dev**: Basic SKU (e.g., B1 App Service, Basic PostgreSQL)
  - **Staging**: Standard SKU (e.g., S1 App Service, General Purpose PostgreSQL)
  - **Production**: Premium SKU with autoscaling (e.g., P1v2 App Service, Business Critical PostgreSQL)
- [ ] **Autoscaling Configured**: Production services have autoscaling rules
  - Scale up when CPU >70% or memory >80%
  - Scale down when CPU <30% for 10 minutes
  - Min instances: 2 (production), 1 (dev/staging)
  - Max instances: 10 (production), 3 (staging)
- [ ] **Reserved Instances**: (If applicable) Long-running resources use reserved instances (1-3 year commitment)
- [ ] **Spot Instances**: (If applicable) Non-critical workloads use spot instances
- [ ] **Storage Tiers**: Use appropriate storage tiers (hot/cool/archive for blobs)
- [ ] **Cost Alerts**: Cost alerts configured (alert when spending >80% of budget)

---

## CI/CD (GitHub Actions)

- [ ] **OIDC Authentication**: GitHub Actions use OIDC (no stored credentials)
  - Azure federated credentials configured for GitHub repository
  - Workflow uses `azure/login@v1` with OIDC
- [ ] **Preview on PR**: Pull requests trigger Pulumi preview
  - PR comment shows resource changes (create, update, delete)
  - Preview requires approval before merge
- [ ] **Manual Approval for Production**: Production deployments require manual approval
  - GitHub environment protection rules configured
  - Required reviewers: 1+ team members
- [ ] **Smoke Tests**: Post-deployment smoke tests run
  - Health check endpoints (`/health`, `/ready`)
  - Critical API endpoints (OAuth2, dashboard)
  - Database connectivity
- [ ] **Rollback Plan**: Rollback procedure documented
  - Use `pulumi stack select <previous-version>` and `pulumi up`
  - Database migrations have DOWN scripts
- [ ] **Deployment Notifications**: Notifications sent to Slack/Teams on deployment success/failure
- [ ] **Environment Secrets**: GitHub Actions secrets configured per environment

---

## Azure-Specific Resources

### Container Apps
- [ ] **Container Image**: Container image built and pushed to Azure Container Registry (ACR)
- [ ] **Health Probes**: Liveness and readiness probes configured
- [ ] **Environment Variables**: Config loaded from environment variables
- [ ] **Secrets**: Sensitive config loaded from Key Vault references
- [ ] **Resource Limits**: CPU and memory limits set (e.g., 0.5 CPU, 1GB memory)
- [ ] **Ingress**: Ingress configured with HTTPS (external or internal)
- [ ] **Scaling Rules**: HTTP scaling or custom metrics scaling configured

### Azure Database for PostgreSQL
- [ ] **SKU**: Appropriate tier selected (Basic for dev, General Purpose for prod)
- [ ] **Version**: PostgreSQL 16+ used
- [ ] **Backup Retention**: Backups retained for 7-35 days (30 days for production)
- [ ] **High Availability**: Zone-redundant HA enabled for production
- [ ] **Storage Autogrow**: Storage autogrow enabled
- [ ] **Firewall Rules**: Only application subnet/VNet allowed
- [ ] **SSL Enforcement**: SSL enforcement enabled (require TLS 1.2+)

### Cosmos DB (MongoDB API)
- [ ] **API**: MongoDB API selected (not SQL or Cassandra)
- [ ] **Consistency Level**: Appropriate consistency level (Session for most cases)
- [ ] **Throughput**: Autoscale throughput configured (400-4000 RU/s)
- [ ] **Backup Policy**: Continuous backup enabled (point-in-time restore)
- [ ] **Multi-Region**: (If applicable) Multi-region replication configured
- [ ] **Network Rules**: Only application subnet/VNet allowed

### Azure Key Vault
- [ ] **SKU**: Standard SKU for dev, Premium SKU for production (HSM-backed keys)
- [ ] **Access Policies**: RBAC model enabled (not access policies)
- [ ] **Soft Delete**: Soft delete enabled (90-day retention)
- [ ] **Purge Protection**: Purge protection enabled (production only)
- [ ] **Network Rules**: Private endpoint configured (no public access)
- [ ] **Audit Logging**: Diagnostic settings configured (logs to Log Analytics)

### Application Insights
- [ ] **Workspace-Based**: Application Insights uses Log Analytics workspace
- [ ] **Sampling**: Adaptive sampling configured (10% for requests, 100% for failures)
- [ ] **Retention**: Data retained for 90 days (production)
- [ ] **Alerts**: Alerts configured for anomalies, failures, performance degradation
- [ ] **Availability Tests**: Availability tests (ping tests) configured for critical endpoints

---

## Monitoring & Observability

- [ ] **Diagnostic Settings**: All resources have diagnostic settings enabled
  - Logs sent to Log Analytics workspace
  - Metrics sent to Azure Monitor
- [ ] **Log Analytics Workspace**: Shared workspace for all services
- [ ] **Azure Monitor Alerts**: Alerts configured for SLO violations
  - High error rate, high latency, resource exhaustion
- [ ] **Action Groups**: Action groups configured (email, SMS, webhook)
- [ ] **Dashboards**: Azure dashboards created for platform overview
- [ ] **Runbooks**: Runbooks linked to alerts (troubleshooting steps)

---

## Deployment Validation

- [ ] **Pulumi Preview**: `pulumi preview` shows expected changes (no surprises)
- [ ] **Dependency Graph**: `pulumi stack graph` shows correct resource dependencies
- [ ] **No Dangling Resources**: Old/unused resources cleaned up (use `pulumi stack export` to audit)
- [ ] **Resource Locks**: (Production only) Critical resources have delete locks
- [ ] **Compliance**: Resources comply with Azure policies (no policy violations)

---

## Documentation

- [ ] **README**: `infra/README.md` documents:
  - How to set up Pulumi CLI
  - How to authenticate to Azure
  - How to create new stack (environment)
  - How to deploy changes
  - How to troubleshoot common issues
- [ ] **Architecture Diagram**: Architecture diagram shows all resources and relationships
- [ ] **Runbooks**: Runbooks for deployment, rollback, disaster recovery
- [ ] **Cost Estimates**: Estimated monthly cost per environment documented

---

## Task Completion Validation

Before marking an infrastructure task as `[X]` complete:

1. ✅ Run `black . && ruff check .` - all pass
2. ✅ Run `pulumi preview` - shows expected changes, no errors
3. ✅ Verify resource naming - follows Azure conventions
4. ✅ Verify resource tagging - all required tags present
5. ✅ Check security - managed identities, Key Vault, private endpoints, RBAC configured
6. ✅ Check cost optimization - appropriate SKUs, autoscaling, cost alerts
7. ✅ Verify CI/CD - OIDC auth, preview on PR, manual approval for prod, smoke tests
8. ✅ Run smoke tests - health checks pass, critical endpoints respond
9. ✅ Verify all checklist items above are complete for the specific task

---

**Agent Reference**: `.github/agents/pulumi.agent.md`  
**Last Updated**: 2025-11-23
