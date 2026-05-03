AWK ?= awk
FRONTEND_DIR ?= $(if $(wildcard package.json),.,frontend)
FRONTEND_MAKEFILE := $(lastword $(MAKEFILE_LIST))

.PHONY: frontend-help \
        frontend-install frontend-dev frontend-build frontend-lint \
        frontend-format-check frontend-format frontend-type-check \
        frontend-test frontend-test-watch frontend-test-coverage frontend-test-e2e

ifneq ($(wildcard package.json),)
.DEFAULT_GOAL := help
.PHONY: help
help: frontend-help
endif

frontend-help:
	@powershell -NoProfile -Command "$$files = @('$(FRONTEND_MAKEFILE)'); $$awk = Get-Command '$(AWK)' -ErrorAction SilentlyContinue; if ($$awk) { & $$awk.Source 'BEGIN { FS = "":.*##""; print ""Available frontend commands:"" } /^frontend-[a-zA-Z0-9_-]+:.*##/ { gsub(/^[ \t]+|[ \t]+$$/, """", $$2); printf ""  %-30s %s\n"", $$1, $$2 }' $$files } else { 'Available frontend commands:'; foreach ($$file in $$files) { Get-Content $$file | Where-Object { $$_ -match '^frontend-[a-zA-Z0-9_-]+:.*##' } | ForEach-Object { $$parts = $$_ -split ':.*##', 2; '  {0,-30} {1}' -f $$parts[0].Trim(), $$parts[1].Trim() } } }"

## -- Frontend ----------------------------------------------------------------

frontend-install: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm install

frontend-dev: ## Start the Next.js development server (port 3000)
	cd $(FRONTEND_DIR) && npm run dev

frontend-build: ## Build the frontend for production
	cd $(FRONTEND_DIR) && npm run build

frontend-lint: ## Lint the frontend with ESLint
	cd $(FRONTEND_DIR) && npm run lint

frontend-format-check: ## Check frontend formatting with Prettier
	cd $(FRONTEND_DIR) && npm run format-check

frontend-format: ## Auto-fix frontend formatting with Prettier
	cd $(FRONTEND_DIR) && npm run format

frontend-type-check: ## Run TypeScript type checking for the frontend
	cd $(FRONTEND_DIR) && npm run type-check

frontend-test: ## Run frontend unit and integration tests
	cd $(FRONTEND_DIR) && npm run test

frontend-test-watch: ## Run frontend unit and integration tests in watch mode
	cd $(FRONTEND_DIR) && npm run test:watch

frontend-test-coverage: ## Run frontend unit and integration tests with coverage
	cd $(FRONTEND_DIR) && npm run test:coverage

frontend-test-e2e: ## Run frontend end-to-end tests
	cd $(FRONTEND_DIR) && npm run test:e2e
