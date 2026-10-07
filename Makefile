.PHONY: test bench demo mcp clean

PYTHON ?= python3

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

bench:
	$(PYTHON) benchmarks/bench_matrix.py

demo:
	$(PYTHON) -m apex_fde_matrix demo

sovereign-demo:
	$(PYTHON) examples/paperclip_hermes_nim_demo.py

mcp:
	$(PYTHON) -m apex_fde_matrix mcp

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info
