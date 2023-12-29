#!/usr/bin/env make

# Build
ACTIVATE_VENV := true
ENTRYPOINT := python3 -m entrypoint

## Create Python virtual environment
venv:
	$(eval ACTIVATE_VENV := . .venv/bin/activate)
	[ -d .venv ] || ( python3 -m venv .venv \
		&& $(ACTIVATE_VENV) \
		&& pip3 install --upgrade pip )

## Install Python requirements for running
requirements:
	( $(ACTIVATE_VENV) && pip3 install -r requirements.txt )


## Install Python requirements for running and testing
requirements-test: requirements
	( $(ACTIVATE_VENV) && pip3 install -r requirements-test.txt )


## Python lint and formatting checks
check-python:
	( $(ACTIVATE_VENV) && black --check entrypoint && pylint entrypoint )
.PHONY: check-python


run-streamlit-app:
	($(ACTIVATE_VENV) && streamlit run $(APP)/app.py)
.PHONY: run-streamlit-app
