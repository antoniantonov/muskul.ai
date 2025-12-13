.PHONY: help build run test clean dev check lint fmt doc

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the project in release mode
	cargo build --release

dev: ## Run the project in development mode with hot reload
	cargo watch -x run

run: ## Run the project
	cargo run

test: ## Run all tests
	cargo test

test-verbose: ## Run tests with verbose output
	cargo test -- --nocapture

check: ## Check the project for errors without building
	cargo check

lint: ## Run clippy linter
	cargo clippy -- -D warnings

fmt: ## Format code using rustfmt
	cargo fmt

fmt-check: ## Check code formatting
	cargo fmt -- --check

clean: ## Clean build artifacts
	cargo clean

doc: ## Generate and open documentation
	cargo doc --open --no-deps

install-tools: ## Install development tools
	cargo install cargo-watch
	cargo install cargo-audit

audit: ## Run security audit
	cargo audit

.DEFAULT_GOAL := help
