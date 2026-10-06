# Environment Report

## Machine summary

- OS: Windows 11 Home (Build 26200)
- CPU: Intel64 Family 6 Model 186 Stepping 3, 1 physical processor reported, approx. 1.3 GHz nominal clock
- RAM: 16 GB total, approximately 1.55 GB available at inspection time
- GPU: no CUDA-capable GPU detected in the active Python environment
- Disk: standard local workstation storage; not fully enumerated in this environment report
- Python: Python 3.12.10 via `py -3.12`
- Git: 2.55.0.windows.2
- Package manager: `pip` 25.0.1
- Internet access: confirmed reachable to public HTTPS endpoints such as Hugging Face and GitHub

## Scientific stack

- NumPy 1.26.4
- Pandas 2.2.2
- SciPy 1.17.1
- scikit-learn 1.5.1
- NetworkX 3.3
- Sentence-Transformers 3.2.1
- PyTorch 2.14.1
- Transformers 4.45.0

## Resource limitations

- Memory is constrained for large-scale full-repository training and large embedding pipelines.
- No CUDA device is available, so GPU acceleration is not available for deep learning.
- The dataset size should remain moderate and repository-scope focused to stay within memory and time budgets.

## Recommended experiment scale

- Keep the benchmark to a small set of public Python repositories (for example 2-5 moderate-size repos and a sampled subset of files).
- Prefer repository-level retrieval tasks over full language-model fine-tuning.
- Use lightweight embeddings and classical ML rankers to keep experiments reproducible and stable.
- Run 1-3 ablation studies with a small, fixed number of repositories to protect time and hardware constraints.
