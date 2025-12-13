# muskul.ai

Multi-platform fitness data aggregation and analytics platform.

## Architecture

- **Backend**: Rust (Axum framework) - High-performance REST API
- **Frontend**: React + TypeScript + Vite - Modern web interface
- **ETL**: Python - Data ingestion and transformation
- **AI Agent**: Python (FastAPI) - Intelligent data processing
- **Infrastructure**: Pulumi (TypeScript) - Azure cloud deployment

## Prerequisites

- Docker & Docker Compose
- Rust (latest stable)
- Node.js 20+
- Python 3.12+
- Azure CLI (for deployment)
- Pulumi CLI (for infrastructure)

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/antoniantonov/muskul.ai.git
   cd muskul.ai
   ```

2. **Start infrastructure services**
   ```bash
   docker-compose up -d
   ```

3. **Run backend**
   ```bash
   cd backend
   cargo run
   ```

4. **Run frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Run ETL**
   ```bash
   cd etl
   pip install -r requirements.txt
   python main.py
   ```

6. **Run AI Agent**
   ```bash
   cd ai-agent-service
   pip install -r requirements.txt
   python src/main.py
   ```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment with the following workflows:

### Workflows

- **Backend CI** (`.github/workflows/backend.yml`) - Rust tests, linting, Docker build
- **AI Agent CI** (`.github/workflows/ai-agent.yml`) - Python tests, linting, Docker build
- **ETL CI** (`.github/workflows/etl.yml`) - Python tests, linting, Docker build
- **Frontend CI** (`.github/workflows/frontend.yml`) - TypeScript tests, linting, accessibility, Lighthouse, Docker build
- **Infrastructure CD** (`.github/workflows/infra.yml`) - Pulumi preview and deployment

### Versioning

All Docker images use semantic versioning: `1.0.YYYYMMDD.buildnumber`

Examples:
- `1.0.20251123.42` - Build #42 on November 23, 2025
- `1.0.20251201.158` - Build #158 on December 1, 2025

### Required GitHub Secrets

Configure the following secrets in your GitHub repository settings (Settings → Secrets and variables → Actions):

#### Azure Container Registry (ACR)
- `ACR_LOGIN_SERVER` - Azure Container Registry URL (e.g., `muskulai.azurecr.io`)
- `ACR_USERNAME` - ACR service principal client ID
- `ACR_PASSWORD` - ACR service principal password/secret

**How to create ACR credentials:**
```bash
# Create a service principal with push access to ACR
az ad sp create-for-rbac \
  --name "muskul-ai-acr-push" \
  --role "AcrPush" \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.ContainerRegistry/registries/{acr-name}

# Output will contain clientId (username) and clientSecret (password)
```

#### Azure Deployment
- `AZURE_CREDENTIALS` - JSON object with Azure service principal credentials
  ```json
  {
    "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "clientSecret": "your-client-secret",
    "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
  ```

**How to create Azure credentials:**
```bash
# Create a service principal with Contributor access
az ad sp create-for-rbac \
  --name "muskul-ai-deployer" \
  --role Contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth

# Copy the JSON output to AZURE_CREDENTIALS secret
```

#### Pulumi
- `PULUMI_ACCESS_TOKEN` - Pulumi Cloud access token for state management

**How to get Pulumi token:**
1. Sign up at [Pulumi Cloud](https://app.pulumi.com/)
2. Go to Settings → Access Tokens
3. Create a new token with appropriate permissions
4. Copy the token to GitHub secret

#### Code Coverage
- `CODECOV_TOKEN` - Codecov upload token for coverage reports

**How to get Codecov token:**
1. Sign up at [Codecov](https://codecov.io/)
2. Add your GitHub repository
3. Copy the upload token from repository settings
4. Add to GitHub secret

### Deployment Strategy

- **Pull Requests**: Run tests, linting, and Pulumi preview
- **Push to `develop`**: Build and push Docker images with branch tag
- **Push to `main`**: Build and push Docker images with semantic version + `latest` tag, deploy infrastructure to dev/staging/prod

### Coverage Requirements

All services maintain 80% code coverage threshold:
- Backend: Rust (tarpaulin)
- Frontend: TypeScript (vitest)
- ETL: Python (pytest-cov)
- AI Agent: Python (pytest-cov)

## Project Structure

```
.
├── .github/workflows/      # GitHub Actions CI/CD workflows
├── ai-agent-service/       # AI Agent service (Python/FastAPI)
├── backend/                # Rust backend API
├── etl/                    # Python ETL jobs
├── frontend/               # React TypeScript frontend
├── infra/                  # Infrastructure as Code (Pulumi + observability)
├── docs/                   # Documentation
└── specs/                  # Feature specifications
```

## Development

### Running Tests

```bash
# Backend
cd backend && cargo test

# Frontend
cd frontend && npm test

# ETL
cd etl && pytest python/tests

# AI Agent
cd ai-agent-service && pytest
```

### Linting

```bash
# Backend
cd backend && cargo clippy

# Frontend
cd frontend && npm run lint

# ETL
cd etl && flake8 python && black python

# AI Agent
cd ai-agent-service && flake8 src && black src
```

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure all tests pass and coverage meets threshold
4. Submit a pull request

## License

Copyright © 2025 muskul.ai. All rights reserved.
