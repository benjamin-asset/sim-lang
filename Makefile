setup:
	dephell deps convert --from=pyproject.toml --to=setup.py
	poetry export -f requirements.txt -o requirements.txt --without-hashes --dev
