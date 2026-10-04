PYTHON ?= python3

.PHONY: check check-secrets examples demo

check:
	@$(PYTHON) -B -m unittest discover -s tests -q
	@$(PYTHON) -B scripts/repo_checks.py
	@$(PYTHON) -B scripts/run_examples.py --check

check-secrets:
	@$(PYTHON) -B scripts/check_secrets.py

examples:
	@$(PYTHON) -B scripts/run_examples.py

demo: examples
	@$(PYTHON) -B scripts/serve_demo.py
