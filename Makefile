PYTHON ?= python3

.PHONY: check check-secrets

check:
	@$(PYTHON) -B -m unittest discover -s tests -q
	@$(PYTHON) -B scripts/repo_checks.py

check-secrets:
	@$(PYTHON) -B scripts/check_secrets.py
