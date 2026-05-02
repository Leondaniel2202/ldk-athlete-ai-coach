include backend/Makefile
include frontend/Makefile

.DEFAULT_GOAL := all
AWK ?= awk

.PHONY: all frontend backend help \
        install test lint format-check type-check

all: frontend backend

frontend:
	$(MAKE) -C frontend

backend:
	$(MAKE) -C backend

help: ## Show this help message
	@powershell -NoProfile -Command "$$files = @('$(MAKEFILE_LIST)' -split ' '); $$awk = Get-Command '$(AWK)' -ErrorAction SilentlyContinue; if ($$awk) { & $$awk.Source 'BEGIN { FS = "":.*##""; print ""Available root commands:"" } /^[a-zA-Z0-9_-]+:.*##/ { gsub(/^[ \t]+|[ \t]+$$/, """", $$2); printf ""  %-30s %s\n"", $$1, $$2 }' $$files } else { 'Available root commands:'; foreach ($$file in $$files) { Get-Content $$file | Where-Object { $$_ -match '^[a-zA-Z0-9_-]+:.*##' } | ForEach-Object { $$parts = $$_ -split ':.*##', 2; '  {0,-30} {1}' -f $$parts[0].Trim(), $$parts[1].Trim() } } }"
