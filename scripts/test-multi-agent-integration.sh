#!/bin/bash
#
# Multi-Agent Test Execution Script
# Purpose: Automated validation of multi-agent routing and quality gates
# Date: 2025-11-23
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result counters
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASS_COUNT++))
}

log_fail() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAIL_COUNT++))
}

log_skip() {
    echo -e "${YELLOW}[⏭ SKIP]${NC} $1"
    ((SKIP_COUNT++))
}

log_header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_header "Checking Prerequisites"
    
    local all_ok=true
    
    # Check for required directories
    if [ ! -d "backend" ]; then
        log_fail "backend/ directory not found"
        all_ok=false
    else
        log_success "backend/ directory exists"
    fi
    
    if [ ! -d "frontend" ]; then
        log_fail "frontend/ directory not found"
        all_ok=false
    else
        log_success "frontend/ directory exists"
    fi
    
    if [ ! -d "etl" ]; then
        log_fail "etl/ directory not found"
        all_ok=false
    else
        log_success "etl/ directory exists"
    fi
    
    if [ ! -d "infra" ]; then
        log_fail "infra/ directory not found"
        all_ok=false
    else
        log_success "infra/ directory exists"
    fi
    
    # Check for Rust toolchain
    if ! command -v cargo &> /dev/null; then
        log_fail "cargo (Rust) not found in PATH"
        all_ok=false
    else
        log_success "cargo (Rust) found: $(cargo --version)"
    fi
    
    # Check for Node.js
    if ! command -v npm &> /dev/null; then
        log_fail "npm (Node.js) not found in PATH"
        all_ok=false
    else
        log_success "npm (Node.js) found: $(npm --version)"
    fi
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        log_fail "python3 not found in PATH"
        all_ok=false
    else
        log_success "python3 found: $(python3 --version)"
    fi
    
    if [ "$all_ok" = false ]; then
        echo ""
        log_fail "Prerequisites not met. Please initialize project structure and install dependencies."
        exit 1
    fi
    
    echo ""
    log_success "All prerequisites met"
}

# Test Case 1: Rust Backend Agent
test_rust_agent() {
    log_header "Test Case 1: Rust Backend Agent (@rust)"
    
    # Check if Rust backend is initialized
    if [ ! -f "backend/Cargo.toml" ]; then
        log_skip "T057: backend/Cargo.toml not found (project not initialized)"
        return
    fi
    
    # Test T057: Database connection pool
    log_info "Testing T057: Database connection pool"
    if [ -f "backend/src/config/database.rs" ]; then
        log_success "T057: backend/src/config/database.rs exists"
        
        # Check for tests
        if [ -f "backend/tests/config/database_test.rs" ] || grep -q "mod database" backend/tests/**/*.rs 2>/dev/null; then
            log_success "T057: Tests exist for database connection pool"
        else
            log_fail "T057: No tests found for database connection pool"
        fi
    else
        log_skip "T057: backend/src/config/database.rs not implemented yet"
    fi
    
    # Run Rust quality checks
    log_info "Running Rust quality checks..."
    
    cd backend
    
    # cargo fmt check
    if cargo fmt -- --check &> /dev/null; then
        log_success "Rust: cargo fmt --check passed"
    else
        log_fail "Rust: cargo fmt --check failed"
    fi
    
    # cargo clippy
    if cargo clippy -- -D warnings &> /dev/null; then
        log_success "Rust: cargo clippy passed"
    else
        log_fail "Rust: cargo clippy failed (warnings present)"
    fi
    
    # cargo test
    if cargo test &> /dev/null; then
        log_success "Rust: cargo test passed"
    else
        log_fail "Rust: cargo test failed"
    fi
    
    # cargo audit (security)
    if command -v cargo-audit &> /dev/null; then
        if cargo audit &> /dev/null; then
            log_success "Rust: cargo audit passed (no known CVEs)"
        else
            log_fail "Rust: cargo audit failed (CVEs detected)"
        fi
    else
        log_skip "Rust: cargo-audit not installed"
    fi
    
    # Coverage check (if tarpaulin installed)
    if command -v cargo-tarpaulin &> /dev/null; then
        coverage=$(cargo tarpaulin --output-format Json 2>/dev/null | jq '.coverage' || echo "0")
        if (( $(echo "$coverage >= 80" | bc -l) )); then
            log_success "Rust: Test coverage ${coverage}% (≥80% required)"
        else
            log_fail "Rust: Test coverage ${coverage}% (<80% required)"
        fi
    else
        log_skip "Rust: cargo-tarpaulin not installed"
    fi
    
    cd ..
}

# Test Case 2: TypeScript Frontend Agent
test_typescript_agent() {
    log_header "Test Case 2: TypeScript Frontend Agent (@typescript)"
    
    # Check if frontend is initialized
    if [ ! -f "frontend/package.json" ]; then
        log_skip "T080: frontend/package.json not found (project not initialized)"
        return
    fi
    
    # Test T080: Provider connection UI
    log_info "Testing T080: Provider connection UI"
    if [ -f "frontend/src/pages/connect-provider-page.tsx" ]; then
        log_success "T080: frontend/src/pages/connect-provider-page.tsx exists"
        
        # Check for tests
        if [ -f "frontend/src/pages/__tests__/connect-provider-page.test.tsx" ]; then
            log_success "T080: Tests exist for provider connection page"
        else
            log_fail "T080: No tests found for provider connection page"
        fi
    else
        log_skip "T080: frontend/src/pages/connect-provider-page.tsx not implemented yet"
    fi
    
    # Run TypeScript quality checks
    log_info "Running TypeScript quality checks..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing npm dependencies..."
        npm install &> /dev/null
    fi
    
    # npm run lint (ESLint)
    if npm run lint &> /dev/null; then
        log_success "TypeScript: ESLint passed"
    else
        log_fail "TypeScript: ESLint failed"
    fi
    
    # npm run type-check (TypeScript strict)
    if npm run type-check &> /dev/null; then
        log_success "TypeScript: Type checking passed (strict mode)"
    else
        log_fail "TypeScript: Type checking failed"
    fi
    
    # npm test (Vitest)
    if npm test -- --run &> /dev/null; then
        log_success "TypeScript: Tests passed (Vitest)"
    else
        log_fail "TypeScript: Tests failed"
    fi
    
    # Coverage check
    if npm run coverage &> /dev/null; then
        coverage=$(cat coverage/coverage-summary.json | jq '.total.lines.pct' || echo "0")
        if (( $(echo "$coverage >= 80" | bc -l) )); then
            log_success "TypeScript: Test coverage ${coverage}% (≥80% required)"
        else
            log_fail "TypeScript: Test coverage ${coverage}% (<80% required)"
        fi
    else
        log_skip "TypeScript: Coverage not configured"
    fi
    
    # Accessibility check (axe-core)
    if command -v axe &> /dev/null; then
        if npm run axe &> /dev/null; then
            log_success "TypeScript: Accessibility audit passed (axe-core)"
        else
            log_fail "TypeScript: Accessibility violations detected (axe-core)"
        fi
    else
        log_skip "TypeScript: axe-core not installed"
    fi
    
    cd ..
}

# Test Case 3: Python ETL Agent
test_python_agent() {
    log_header "Test Case 3: Python ETL Agent (@python)"
    
    # Check if Python ETL is initialized
    if [ ! -f "etl/requirements.txt" ]; then
        log_skip "T116: etl/requirements.txt not found (project not initialized)"
        return
    fi
    
    # Test T116: ETL subscriber
    log_info "Testing T116: Service Bus subscriber for ETL"
    if [ -f "etl/python/jobs/etl_subscriber.py" ]; then
        log_success "T116: etl/python/jobs/etl_subscriber.py exists"
        
        # Check for tests
        if [ -f "etl/python/tests/test_etl_subscriber.py" ]; then
            log_success "T116: Tests exist for ETL subscriber"
        else
            log_fail "T116: No tests found for ETL subscriber"
        fi
    else
        log_skip "T116: etl/python/jobs/etl_subscriber.py not implemented yet"
    fi
    
    # Run Python quality checks
    log_info "Running Python quality checks..."
    
    cd etl
    
    # Create venv if needed
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt &> /dev/null
    else
        source venv/bin/activate
    fi
    
    # black (formatting)
    if black --check . &> /dev/null; then
        log_success "Python: black formatting passed"
    else
        log_fail "Python: black formatting failed"
    fi
    
    # ruff (linting)
    if ruff check . &> /dev/null; then
        log_success "Python: ruff linting passed"
    else
        log_fail "Python: ruff linting failed"
    fi
    
    # mypy (type checking)
    if mypy --strict . &> /dev/null; then
        log_success "Python: mypy type checking passed (strict)"
    else
        log_fail "Python: mypy type checking failed"
    fi
    
    # pytest (tests)
    if pytest &> /dev/null; then
        log_success "Python: pytest passed"
    else
        log_fail "Python: pytest failed"
    fi
    
    # Coverage check
    if pytest --cov &> /dev/null; then
        coverage=$(pytest --cov --cov-report=json &> /dev/null && cat coverage.json | jq '.totals.percent_covered' || echo "0")
        if (( $(echo "$coverage >= 80" | bc -l) )); then
            log_success "Python: Test coverage ${coverage}% (≥80% required)"
        else
            log_fail "Python: Test coverage ${coverage}% (<80% required)"
        fi
    else
        log_skip "Python: Coverage not configured"
    fi
    
    deactivate
    cd ..
}

# Test Case 4: PostgreSQL Agent
test_pg_agent() {
    log_header "Test Case 4: PostgreSQL Agent (@pg)"
    
    # Check if migrations exist
    if [ ! -d "backend/migrations" ]; then
        log_skip "T041: backend/migrations/ not found (migrations not created)"
        return
    fi
    
    # Test T041: Users table migration
    log_info "Testing T041: Create migration 001_create_users_table.sql"
    if [ -f "backend/migrations/001_create_users_table.sql" ]; then
        log_success "T041: backend/migrations/001_create_users_table.sql exists"
        
        # Check for reversible migration (UP and DOWN)
        if grep -q "CREATE TABLE" backend/migrations/001_create_users_table.sql && \
           grep -q "DROP TABLE" backend/migrations/001_create_users_table.sql; then
            log_success "T041: Migration is reversible (UP and DOWN present)"
        else
            log_fail "T041: Migration not reversible (missing DOWN script)"
        fi
        
        # Check for constraints
        if grep -q "NOT NULL\|UNIQUE\|PRIMARY KEY\|FOREIGN KEY" backend/migrations/001_create_users_table.sql; then
            log_success "T041: Migration has proper constraints"
        else
            log_fail "T041: Migration missing constraints"
        fi
        
        # Check for indexes
        if grep -q "CREATE INDEX" backend/migrations/001_create_users_table.sql; then
            log_success "T041: Migration creates indexes"
        else
            log_fail "T041: Migration missing indexes"
        fi
    else
        log_skip "T041: backend/migrations/001_create_users_table.sql not implemented yet"
    fi
}

# Test Case 5: MongoDB Agent
test_mongo_agent() {
    log_header "Test Case 5: MongoDB Agent (@mongo)"
    
    # Check if MongoDB init scripts exist
    if [ ! -d "infra/mongodb" ]; then
        log_skip "T048: infra/mongodb/ not found"
        return
    fi
    
    # Test T048: raw_activities collection
    log_info "Testing T048: MongoDB initialization script for raw_activities"
    if [ -f "infra/mongodb/init.js" ]; then
        log_success "T048: infra/mongodb/init.js exists"
        
        # Check for collection creation
        if grep -q "db.createCollection.*raw_activities" infra/mongodb/init.js; then
            log_success "T048: raw_activities collection defined"
        else
            log_fail "T048: raw_activities collection not found in init script"
        fi
        
        # Check for indexes
        if grep -q "createIndex" infra/mongodb/init.js; then
            log_success "T048: Indexes defined in init script"
        else
            log_fail "T048: No indexes found in init script"
        fi
        
        # Check for schema validation
        if grep -q "validator" infra/mongodb/init.js; then
            log_success "T048: Schema validation rules defined"
        else
            log_fail "T048: Schema validation rules missing"
        fi
    else
        log_skip "T048: infra/mongodb/init.js not implemented yet"
    fi
}

# Test Case 6: Observability Agent
test_ot_agent() {
    log_header "Test Case 6: Observability Agent (@ot)"
    
    # Test T062: OpenTelemetry tracing
    log_info "Testing T062: OpenTelemetry tracing middleware"
    if [ -f "backend/src/middleware/tracing.rs" ]; then
        log_success "T062: backend/src/middleware/tracing.rs exists"
        
        # Check for OpenTelemetry imports
        if grep -q "opentelemetry\|tracing" backend/src/middleware/tracing.rs; then
            log_success "T062: OpenTelemetry/tracing imports present"
        else
            log_fail "T062: OpenTelemetry/tracing imports missing"
        fi
        
        # Check for span creation
        if grep -q "span\|trace" backend/src/middleware/tracing.rs; then
            log_success "T062: Span/trace logic present"
        else
            log_fail "T062: Span/trace logic missing"
        fi
    else
        log_skip "T062: backend/src/middleware/tracing.rs not implemented yet"
    fi
    
    # Test T014: Grafana dashboards
    log_info "Testing T014: Grafana dashboards config"
    if [ -d "infra/grafana/dashboards" ] && [ "$(ls -A infra/grafana/dashboards)" ]; then
        log_success "T014: Grafana dashboards directory exists and not empty"
        
        # Count dashboard JSON files
        dashboard_count=$(find infra/grafana/dashboards -name "*.json" | wc -l)
        if [ "$dashboard_count" -gt 0 ]; then
            log_success "T014: Found $dashboard_count Grafana dashboard(s)"
        else
            log_fail "T014: No Grafana dashboards found"
        fi
    else
        log_skip "T014: infra/grafana/dashboards/ not created yet"
    fi
}

# Test Case 7: Infrastructure Agent
test_pulumi_agent() {
    log_header "Test Case 7: Infrastructure Agent (@pulumi)"
    
    # Check if Pulumi is initialized
    if [ ! -f "infra/pulumi/Pulumi.yaml" ]; then
        log_skip "T027: infra/pulumi/Pulumi.yaml not found (Pulumi not initialized)"
        return
    fi
    
    # Test T027: Resource group module
    log_info "Testing T027: Azure resource group module"
    if [ -f "infra/pulumi/modules/resource_group.py" ]; then
        log_success "T027: infra/pulumi/modules/resource_group.py exists"
        
        # Check for resource naming conventions
        if grep -q "rg-\|resource_group" infra/pulumi/modules/resource_group.py; then
            log_success "T027: Azure naming conventions followed"
        else
            log_fail "T027: Azure naming conventions not followed"
        fi
        
        # Check for resource tags
        if grep -q "tags" infra/pulumi/modules/resource_group.py; then
            log_success "T027: Resource tagging present"
        else
            log_fail "T027: Resource tagging missing"
        fi
    else
        log_skip "T027: infra/pulumi/modules/resource_group.py not implemented yet"
    fi
    
    # Run Pulumi quality checks
    log_info "Running Pulumi quality checks..."
    
    cd infra/pulumi
    
    # ruff (linting)
    if ruff check . &> /dev/null; then
        log_success "Pulumi: ruff linting passed"
    else
        log_fail "Pulumi: ruff linting failed"
    fi
    
    # black (formatting)
    if black --check . &> /dev/null; then
        log_success "Pulumi: black formatting passed"
    else
        log_fail "Pulumi: black formatting failed"
    fi
    
    # pulumi preview (dry run)
    if command -v pulumi &> /dev/null; then
        if pulumi preview &> /dev/null; then
            log_success "Pulumi: pulumi preview passed (no errors)"
        else
            log_fail "Pulumi: pulumi preview failed"
        fi
    else
        log_skip "Pulumi: pulumi CLI not installed"
    fi
    
    cd ../..
}

# Generate test report
generate_report() {
    log_header "Test Execution Summary"
    
    local total=$((PASS_COUNT + FAIL_COUNT + SKIP_COUNT))
    local pass_pct=$(awk "BEGIN {printf \"%.1f\", ($PASS_COUNT / $total) * 100}")
    
    echo -e "${GREEN}✓ PASSED: $PASS_COUNT${NC}"
    echo -e "${RED}✗ FAILED: $FAIL_COUNT${NC}"
    echo -e "${YELLOW}⏭ SKIPPED: $SKIP_COUNT${NC}"
    echo -e "TOTAL: $total"
    echo ""
    echo -e "Success Rate: ${pass_pct}%"
    echo ""
    
    if [ "$FAIL_COUNT" -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ ALL TESTS PASSED - MULTI-AGENT SYSTEM OPERATIONAL     ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE               ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Multi-Agent Integration - Automated Test Execution         ║${NC}"
    echo -e "${BLUE}║  Date: $(date +"%Y-%m-%d %H:%M:%S")                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_prerequisites
    
    test_rust_agent
    test_typescript_agent
    test_python_agent
    test_pg_agent
    test_mongo_agent
    test_ot_agent
    test_pulumi_agent
    
    generate_report
}

# Run main
main "$@"
