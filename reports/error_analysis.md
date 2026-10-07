# Qualitative retrieval error analysis

Examples are selected directly from held-out test rankings. Scores are raw method scores; methods without an observed example are explicitly marked as unavailable.

Validation-selected fusion weights: lexical=0.0, semantic=0.8, structure=0.2.

## CodeInsight succeeds; semantic misses top 5

### Example 1: click / `click::src.click.core.Context.to_info_dict`

- Query: Gather information that could be useful for a tool generating user-facing documentation. This traverses the entire CLI structure. .. code-block:: python with Context(cli) as ctx: info = ctx. () .. versionadded:: 8.0
- Expected: `click::src.click.core.Context.to_info_dict` (`src/click/core.py`), rank positions: {"BM25": 458, "CodeInsight": 4, "Lexical": 395, "Semantic": 14, "Semantic + AST": 1, "Semantic + Calls": 14, "Semantic + Dependencies": 14, "Semantic + Inheritance": 14, "Semantic + Multi-Structure": 1, "Structure-only": 15}
- Expected unit structure: kind=method; parent=Context; calls=['to_info_dict']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=[]
- Expected component scores: lexical=0.0000, semantic=0.4258, structure=0.1899.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.core.Parameter._check_name_is_usable` | 20.8393 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.shell_completion.ShellComplete` | 18.4804 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| BM25 | `click::src.click.types.BoolParamType` | 18.2316 | `src/click/types.py` | imports: __future__, abc, click.shell_completion, collections.abc |
| BM25 | `click::src.click.core.Context.invoke` | 17.3369 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core._check_nested_chain` | 16.9050 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.exceptions.NoArgsIsHelpError.__init__` | 0.3002 | `src/click/exceptions.py` | same unit kind; imports: __future__, collections.abc, gettext, globals |
| Lexical | `click::src.click.testing.CliRunner.get_default_prog_name` | 0.2845 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, contextlib, os |
| Lexical | `click::src.click.shell_completion.ShellComplete.__init__` | 0.2672 | `src/click/shell_completion.py` | same unit kind; imports: __future__, collections.abc, gettext, os |
| Lexical | `click::src.click.core.Group.resolve_command` | 0.2561 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.types.Choice.normalize_choice` | 0.2501 | `src/click/types.py` | same unit kind; imports: __future__, abc, click.shell_completion, collections.abc |
| Semantic | `click::src.click.shell_completion._resolve_context` | 0.5232 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Semantic | `click::src.click.core.Group.to_info_dict` | 0.4942 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.to_info_dict` | 0.4846 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.decorators.custom_version_option` | 0.4655 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic | `click::src.click.core.Parameter.get_help_spec` | 0.4542 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.abort` | 0.1899 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.find_object` | 0.1899 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._close_with_exception_info` | 0.1899 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.get_parameter_source` | 0.1899 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._default_map_has` | 0.1899 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.to_info_dict` | 0.5926 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context._make_sub_context` | 0.5916 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.get_usage` | 0.5555 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.get_help` | 0.5501 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.__init__` | 0.5501 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.shell_completion._resolve_context` | 0.2616 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Semantic + Calls | `click::src.click.core.Group.to_info_dict` | 0.2471 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.to_info_dict` | 0.2423 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.decorators.custom_version_option` | 0.2328 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Calls | `click::src.click.core.Parameter.get_help_spec` | 0.2271 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.shell_completion._resolve_context` | 0.2616 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Semantic + Dependencies | `click::src.click.core.Group.to_info_dict` | 0.2471 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.to_info_dict` | 0.2423 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.decorators.custom_version_option` | 0.2328 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Dependencies | `click::src.click.core.Parameter.get_help_spec` | 0.2271 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.shell_completion._resolve_context` | 0.2616 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Semantic + Inheritance | `click::src.click.core.Group.to_info_dict` | 0.2471 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.to_info_dict` | 0.2423 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.decorators.custom_version_option` | 0.2328 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Inheritance | `click::src.click.core.Parameter.get_help_spec` | 0.2271 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.to_info_dict` | 0.3078 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context._make_sub_context` | 0.3068 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.get_usage` | 0.2707 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.get_help` | 0.2653 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.__init__` | 0.2653 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.shell_completion._resolve_context` | 0.4186 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| CodeInsight | `click::src.click.core.Group.to_info_dict` | 0.3953 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.to_info_dict` | 0.3877 | `src/click/core.py` | same file; same module; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.to_info_dict` | 0.3786 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: to_info_dict; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context._make_sub_context` | 0.3770 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 2: click / `click::src.click.core.Context.close`

- Query: Invoke all callbacks registered with :meth:`call_on_close`, and exit all context managers entered with :meth:`with_resource`.
- Expected: `click::src.click.core.Context.close` (`src/click/core.py`), rank positions: {"BM25": 533, "CodeInsight": 3, "Lexical": 510, "Semantic": 7, "Semantic + AST": 3, "Semantic + Calls": 20, "Semantic + Dependencies": 7, "Semantic + Inheritance": 7, "Semantic + Multi-Structure": 4, "Structure-only": 20}
- Expected unit structure: kind=method; parent=Context; calls=['_close_with_exception_info']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=[]
- Expected component scores: lexical=0.0000, semantic=0.3777, structure=0.1739.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.core.Group.invoke` | 11.5163 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click._termui_impl.ProgressBar.__iter__` | 9.9855 | `src/click/_termui_impl.py` | same unit kind; imports: __future__, collections.abc, contextlib, exceptions |
| BM25 | `click::src.click.core.Command.main` | 9.8130 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.decorators.help_option` | 9.4973 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| BM25 | `click::src.click.decorators.custom_version_option` | 9.1649 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Lexical | `click::src.click.core.Context.with_resource` | 0.2385 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Context.exit` | 0.1756 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Context.invoke` | 0.1642 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Context.invoke` | 0.1411 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Command.invoke` | 0.1393 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context.with_resource` | 0.5614 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context.call_on_close` | 0.5221 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.decorators.pass_context` | 0.4170 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic | `click::src.click.globals.get_current_context` | 0.3821 | `src/click/globals.py` | imports: __future__, typing |
| Semantic | `click::src.click.globals.get_current_context` | 0.3821 | `src/click/globals.py` | imports: __future__, typing |
| Structure-only | `click::src.click.core.Context.exit` | 0.2833 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.forward` | 0.2723 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.abort` | 0.1739 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.find_object` | 0.1739 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._close_with_exception_info` | 0.1739 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.with_resource` | 0.6286 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.call_on_close` | 0.6089 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.close` | 0.5367 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _close_with_exception_info; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context._close_with_exception_info` | 0.5335 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context._make_sub_context` | 0.5305 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Context.exit` | 0.3751 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.main` | 0.3673 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Context.forward` | 0.3337 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.decorators.pass_meta_key` | 0.3227 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Calls | `click::src.click.decorators.make_pass_decorator` | 0.3209 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Dependencies | `click::src.click.core.Context.with_resource` | 0.2807 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context.call_on_close` | 0.2611 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.decorators.pass_context` | 0.2085 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Dependencies | `click::src.click.globals.get_current_context` | 0.1911 | `src/click/globals.py` | imports: __future__, typing |
| Semantic + Dependencies | `click::src.click.globals.get_current_context` | 0.1911 | `src/click/globals.py` | imports: __future__, typing |
| Semantic + Inheritance | `click::src.click.core.Context.with_resource` | 0.2807 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context.call_on_close` | 0.2611 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.decorators.pass_context` | 0.2085 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Inheritance | `click::src.click.globals.get_current_context` | 0.1911 | `src/click/globals.py` | imports: __future__, typing |
| Semantic + Inheritance | `click::src.click.globals.get_current_context` | 0.1911 | `src/click/globals.py` | imports: __future__, typing |
| Semantic + Multi-Structure | `click::src.click.core.Context.with_resource` | 0.3677 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.call_on_close` | 0.3480 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.exit` | 0.2980 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.close` | 0.2758 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _close_with_exception_info; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.forward` | 0.2731 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.with_resource` | 0.4839 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.call_on_close` | 0.4525 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.close` | 0.3369 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _close_with_exception_info; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.decorators.pass_context` | 0.3336 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| CodeInsight | `click::src.click.core.Context._close_with_exception_info` | 0.3318 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 3: click / `click::src.click.core.Context.get_usage`

- Query: Helper method to get formatted usage string for the current context and command.
- Expected: `click::src.click.core.Context.get_usage` (`src/click/core.py`), rank positions: {"BM25": 109, "CodeInsight": 5, "Lexical": 14, "Semantic": 6, "Semantic + AST": 4, "Semantic + Calls": 8, "Semantic + Dependencies": 6, "Semantic + Inheritance": 6, "Semantic + Multi-Structure": 5, "Structure-only": 16}
- Expected unit structure: kind=method; parent=Context; calls=['get_usage']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=[]
- Expected component scores: lexical=0.2488, semantic=0.5311, structure=0.1887.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.types.BoolParamType` | 14.0897 | `src/click/types.py` | imports: __future__, abc, click.shell_completion, collections.abc |
| BM25 | `click::src.click.core.ParameterSource` | 13.3274 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Group.command` | 12.2712 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core._check_nested_chain` | 11.6448 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core._complete_visible_commands` | 10.7305 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core._BaseCommand` | 0.4265 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.decorators.command` | 0.4042 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Lexical | `click::src.click.core.Context._make_sub_context` | 0.4028 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.decorators.command` | 0.3735 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Lexical | `click::src.click.core.Group.command` | 0.3569 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.get_usage` | 0.6604 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.get_help` | 0.6405 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.format_usage` | 0.6318 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.format_help` | 0.5545 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context` | 0.5312 | `src/click/core.py` | same file; same module; calls: get_usage; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.abort` | 0.1887 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.find_object` | 0.1887 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._close_with_exception_info` | 0.1887 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.get_parameter_source` | 0.1887 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._default_map_has` | 0.1887 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.get_usage` | 0.6651 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.get_help` | 0.6551 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.format_usage` | 0.6508 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.get_usage` | 0.6429 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: get_usage; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.format_help` | 0.6121 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.get_usage` | 0.3302 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.get_help` | 0.3202 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.format_usage` | 0.3159 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Group.command` | 0.2933 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.format_help` | 0.2773 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.get_usage` | 0.3302 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.get_help` | 0.3202 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.format_usage` | 0.3159 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.format_help` | 0.2773 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context` | 0.2656 | `src/click/core.py` | same file; same module; calls: get_usage; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.get_usage` | 0.3302 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.get_help` | 0.3202 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.format_usage` | 0.3159 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.format_help` | 0.2773 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context` | 0.2656 | `src/click/core.py` | same file; same module; calls: get_usage; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Command.get_usage` | 0.4139 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Command.get_help` | 0.4039 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Command.format_usage` | 0.3996 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Command.format_help` | 0.3610 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.get_usage` | 0.3599 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: get_usage; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.get_usage` | 0.5618 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.get_help` | 0.5459 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.format_usage` | 0.5390 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.format_help` | 0.4771 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.get_usage` | 0.4626 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: get_usage; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.

## Semantic succeeds; CodeInsight misses top 5

### Example 1: click / `click::src.click._compat._FixupStream`

- Query: The new io interface needs more from streams than streams traditionally implement. As such, this fix-up code is necessary in some circumstances. The forcing of readable and writable flags are there because some tools put badly patched objects on sys (one such offender are certain version of jupyter notebook).
- Expected: `click::src.click._compat._FixupStream` (`src/click/_compat.py`), rank positions: {"BM25": 35, "CodeInsight": 6, "Lexical": 35, "Semantic": 5, "Semantic + AST": 5, "Semantic + Calls": 6, "Semantic + Dependencies": 7, "Semantic + Inheritance": 10, "Semantic + Multi-Structure": 9, "Structure-only": 55}
- Expected unit structure: kind=class; parent=None; calls=['cast', 'f', 'getattr', 'read', 'seek', 'tell', 'write', 'x']; imports=['__future__', '_winconsole', 'codecs', 'collections.abc', 'errno', 'io', 'locale', 'os']; bases=[]
- Expected component scores: lexical=0.0497, semantic=0.4681, structure=0.0405.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.types.BoolParamType` | 20.1594 | `src/click/types.py` | same unit kind; imports: __future__, collections.abc, os, sys |
| BM25 | `click::src.click.__init__.__getattr__` | 17.4570 | `src/click/__init__.py` | imports: __future__, types |
| BM25 | `click::src.click.core.Command.get_params` | 17.0945 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| BM25 | `click::src.click._compat.open_stream` | 17.0836 | `src/click/_compat.py` | same file; same module; calls: cast, getattr; imports: __future__, _winconsole, codecs, collections.abc |
| BM25 | `click::src.click.testing.CliRunner.__init__` | 16.6664 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Lexical | `click::src.click.types.Path.to_info_dict` | 0.2264 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.types.PathInfoDict` | 0.1682 | `src/click/types.py` | same unit kind; imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.testing.CliRunner.isolation` | 0.1459 | `src/click/testing.py` | calls: cast, read, write; imports: __future__, collections.abc, io, os |
| Lexical | `click::src.click.types.Path.__init__` | 0.1376 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.exceptions.Exit.__init__` | 0.1344 | `src/click/exceptions.py` | imports: __future__, collections.abc, typing |
| Semantic | `click::src.click._compat._is_jupyter_kernel_output` | 0.5642 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic | `click::src.click._compat._FixupStream.__init__` | 0.5172 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic | `click::src.click._compat._NonClosingTextIOWrapper.__init__` | 0.5134 | `src/click/_compat.py` | same file; same module; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic | `click::src.click.testing.StreamMixer` | 0.4920 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Semantic | `click::src.click._compat._FixupStream` | 0.4681 | `src/click/_compat.py` | same file; same module; same unit kind; calls: cast, f, getattr, read; imports: __future__, _winconsole, codecs, collections.abc |
| Structure-only | `click::src.click._compat._NonClosingTextIOWrapper` | 0.2905 | `src/click/_compat.py` | same file; same module; same unit kind; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Structure-only | `click::src.click.testing._NamedTextIOWrapper` | 0.2799 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Structure-only | `click::src.click.testing.BytesIOCopy` | 0.2799 | `src/click/testing.py` | same unit kind; calls: write; imports: __future__, collections.abc, io, os |
| Structure-only | `click::src.click._winconsole._WindowsConsoleRawIOBase` | 0.1946 | `src/click/_winconsole.py` | same unit kind; imports: __future__, collections.abc, io, sys |
| Structure-only | `click::src.click.types.File` | 0.1827 | `src/click/types.py` | same unit kind; calls: cast; imports: __future__, collections.abc, os, sys |
| Semantic + AST | `click::src.click._compat._is_jupyter_kernel_output` | 0.2821 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + AST | `click::src.click._compat._FixupStream.__init__` | 0.2586 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + AST | `click::src.click._compat._NonClosingTextIOWrapper.__init__` | 0.2567 | `src/click/_compat.py` | same file; same module; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + AST | `click::src.click.testing.StreamMixer` | 0.2460 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Semantic + AST | `click::src.click._compat._FixupStream` | 0.2340 | `src/click/_compat.py` | same file; same module; same unit kind; calls: cast, f, getattr, read; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Calls | `click::src.click._compat._is_jupyter_kernel_output` | 0.2821 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Calls | `click::src.click.__init__.__getattr__` | 0.2734 | `src/click/__init__.py` | imports: __future__, types |
| Semantic + Calls | `click::src.click._compat._FixupStream.__init__` | 0.2586 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Calls | `click::src.click._compat._NonClosingTextIOWrapper.__init__` | 0.2567 | `src/click/_compat.py` | same file; same module; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Calls | `click::src.click.testing.StreamMixer` | 0.2460 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Semantic + Dependencies | `click::src.click._compat._is_jupyter_kernel_output` | 0.3631 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Dependencies | `click::src.click._compat._FixupStream.__init__` | 0.3397 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Dependencies | `click::src.click._compat._NonClosingTextIOWrapper.__init__` | 0.3377 | `src/click/_compat.py` | same file; same module; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Dependencies | `click::src.click._winconsole._WindowsConsoleReader.readinto` | 0.3241 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + Dependencies | `click::src.click._winconsole.ConsoleStream.__init__` | 0.3212 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + Inheritance | `click::src.click._compat._NonClosingTextIOWrapper` | 0.7141 | `src/click/_compat.py` | same file; same module; same unit kind; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Inheritance | `click::src.click.testing.BytesIOCopy` | 0.6946 | `src/click/testing.py` | same unit kind; calls: write; imports: __future__, collections.abc, io, os |
| Semantic + Inheritance | `click::src.click.testing._NamedTextIOWrapper` | 0.6388 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Semantic + Inheritance | `click::src.click.types.File` | 0.5051 | `src/click/types.py` | same unit kind; calls: cast; imports: __future__, collections.abc, os, sys |
| Semantic + Inheritance | `click::src.click._winconsole._WindowsConsoleRawIOBase` | 0.4154 | `src/click/_winconsole.py` | same unit kind; imports: __future__, collections.abc, io, sys |
| Semantic + Multi-Structure | `click::src.click._compat._NonClosingTextIOWrapper` | 0.3594 | `src/click/_compat.py` | same file; same module; same unit kind; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Multi-Structure | `click::src.click.testing.BytesIOCopy` | 0.3346 | `src/click/testing.py` | same unit kind; calls: write; imports: __future__, collections.abc, io, os |
| Semantic + Multi-Structure | `click::src.click._compat._is_jupyter_kernel_output` | 0.3024 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Multi-Structure | `click::src.click._compat._FixupStream.__init__` | 0.2789 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Multi-Structure | `click::src.click.testing._NamedTextIOWrapper` | 0.2787 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| CodeInsight | `click::src.click._compat._is_jupyter_kernel_output` | 0.4594 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| CodeInsight | `click::src.click._compat._FixupStream.__init__` | 0.4219 | `src/click/_compat.py` | same file; same module; imports: __future__, _winconsole, codecs, collections.abc |
| CodeInsight | `click::src.click._compat._NonClosingTextIOWrapper.__init__` | 0.4188 | `src/click/_compat.py` | same file; same module; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| CodeInsight | `click::src.click._compat._NonClosingTextIOWrapper` | 0.4007 | `src/click/_compat.py` | same file; same module; same unit kind; calls: cast; imports: __future__, _winconsole, codecs, collections.abc |
| CodeInsight | `click::src.click.testing.StreamMixer` | 0.3995 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 2: click / `click::src.click._termui_impl._PagerWriter`

- Query: Wrap a pager's output to strip ANSI styling when colors are disabled. The wrapped is owned by the pager strategy that produced it, so this wrapper never closes it: ``_pipepager`` closes its pipe to signal EOF to the pager process, ``_tempfilepager`` closes and removes its temporary file, and ``_nullpager`` leaves an external such as ``sys.stdout`` untouched. The `` `` attribute lets :func:`click.echo` detect that ANSI stripping is handled here, so it doesn't strip a second time (see :func:`._compat.should_strip_ansi`).
- Expected: `click::src.click._termui_impl._PagerWriter` (`src/click/_termui_impl.py`), rank positions: {"BM25": 399, "CodeInsight": 6, "Lexical": 317, "Semantic": 5, "Semantic + AST": 10, "Semantic + Calls": 21, "Semantic + Dependencies": 4, "Semantic + Inheritance": 5, "Semantic + Multi-Structure": 6, "Structure-only": 310}
- Expected unit structure: kind=class; parent=None; calls=['flush', 'getattr', 'strip_ansi', 'write']; imports=['__future__', '_compat', 'collections.abc', 'contextlib', 'exceptions', 'gettext', 'io', 'math']; bases=[]
- Expected component scores: lexical=0.0000, semantic=0.5124, structure=0.0395.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click._termui_impl._pager_contextmanager` | 34.2027 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| BM25 | `click::src.click.types.BoolParamType` | 30.8754 | `src/click/types.py` | same unit kind; imports: __future__, _compat, collections.abc, exceptions |
| BM25 | `click::src.click.termui._readline_prompt` | 29.6531 | `src/click/termui.py` | calls: strip_ansi; imports: __future__, _compat, collections.abc, contextlib |
| BM25 | `click::src.click.core._check_nested_chain` | 28.2317 | `src/click/core.py` | imports: __future__, collections.abc, contextlib, exceptions |
| BM25 | `click::src.click.testing.CliRunner.isolation` | 27.7310 | `src/click/testing.py` | calls: flush, write; imports: __future__, _compat, collections.abc, contextlib |
| Lexical | `click::src.click.types.FuncParamType.__init__` | 0.2253 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Lexical | `click::src.click.utils._PacifyFlushWrapper.__init__` | 0.2151 | `src/click/utils.py` | imports: __future__, _compat, collections.abc, exceptions |
| Lexical | `click::src.click.types.FuncParamType.to_info_dict` | 0.2104 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Lexical | `click::src.click.utils._safecall` | 0.1922 | `src/click/utils.py` | imports: __future__, _compat, collections.abc, exceptions |
| Lexical | `click::src.click.types.FuncParamType` | 0.1868 | `src/click/types.py` | same unit kind; imports: __future__, _compat, collections.abc, exceptions |
| Semantic | `click::src.click._termui_impl.get_pager_file` | 0.5873 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click._compat.should_strip_ansi` | 0.5647 | `src/click/_compat.py` | imports: __future__, collections.abc, io, os |
| Semantic | `click::src.click._termui_impl._tempfilepager` | 0.5375 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click._termui_impl._pager_contextmanager` | 0.5160 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click._termui_impl._PagerWriter` | 0.5124 | `src/click/_termui_impl.py` | same file; same module; same unit kind; calls: flush, getattr, strip_ansi, write; imports: __future__, _compat, collections.abc, contextlib |
| Structure-only | `click::src.click.types.File.to_info_dict` | 0.1952 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Structure-only | `click::src.click.types.File.convert` | 0.1952 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Structure-only | `click::src.click.types.File.resolve_lazy_flag` | 0.1952 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Structure-only | `click::src.click.types.File.__init__` | 0.1952 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Structure-only | `click::src.click.types.File.shell_complete` | 0.1952 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + AST | `click::src.click.types.File.convert` | 0.4565 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + AST | `click::src.click.types.File.__init__` | 0.4377 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + AST | `click::src.click.types.File.resolve_lazy_flag` | 0.4037 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + AST | `click::src.click.types.File.to_info_dict` | 0.3905 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + AST | `click::src.click.types.File.shell_complete` | 0.3838 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + Calls | `click::src.click.termui._readline_prompt` | 0.5405 | `src/click/termui.py` | calls: strip_ansi; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Calls | `click::src.click.core._echo_aborted` | 0.3708 | `src/click/core.py` | imports: __future__, collections.abc, contextlib, exceptions |
| Semantic + Calls | `click::src.click.utils._safecall` | 0.3692 | `src/click/utils.py` | imports: __future__, _compat, collections.abc, exceptions |
| Semantic + Calls | `click::src.click.core.Command.get_short_help_str` | 0.3571 | `src/click/core.py` | imports: __future__, collections.abc, contextlib, exceptions |
| Semantic + Calls | `click::src.click.termui.clear` | 0.3378 | `src/click/termui.py` | imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl.get_pager_file` | 0.3725 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl._tempfilepager` | 0.3476 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl._pager_contextmanager` | 0.3369 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl._PagerWriter` | 0.3351 | `src/click/_termui_impl.py` | same file; same module; same unit kind; calls: flush, getattr, strip_ansi, write; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl._nullpager` | 0.3274 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._termui_impl.get_pager_file` | 0.2936 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._compat.should_strip_ansi` | 0.2824 | `src/click/_compat.py` | imports: __future__, collections.abc, io, os |
| Semantic + Inheritance | `click::src.click._termui_impl._tempfilepager` | 0.2687 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._termui_impl._pager_contextmanager` | 0.2580 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._termui_impl._PagerWriter` | 0.2562 | `src/click/_termui_impl.py` | same file; same module; same unit kind; calls: flush, getattr, strip_ansi, write; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click.termui._readline_prompt` | 0.3288 | `src/click/termui.py` | calls: strip_ansi; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click._termui_impl.get_pager_file` | 0.3134 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click._compat.should_strip_ansi` | 0.2930 | `src/click/_compat.py` | imports: __future__, collections.abc, io, os |
| Semantic + Multi-Structure | `click::src.click._termui_impl._tempfilepager` | 0.2885 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click._termui_impl._pager_contextmanager` | 0.2777 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click._termui_impl.get_pager_file` | 0.4777 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click._compat.should_strip_ansi` | 0.4560 | `src/click/_compat.py` | imports: __future__, collections.abc, io, os |
| CodeInsight | `click::src.click._termui_impl._tempfilepager` | 0.4379 | `src/click/_termui_impl.py` | same file; same module; calls: flush; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click.termui._readline_prompt` | 0.4280 | `src/click/termui.py` | calls: strip_ansi; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click._termui_impl._pager_contextmanager` | 0.4207 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 3: click / `click::src.click.core.Group.format_commands`

- Query: Extra format methods for multi methods that adds all the commands after the options.
- Expected: `click::src.click.core.Group.format_commands` (`src/click/core.py`), rank positions: {"BM25": 2, "CodeInsight": 6, "Lexical": 2, "Semantic": 5, "Semantic + AST": 5, "Semantic + Calls": 70, "Semantic + Dependencies": 5, "Semantic + Inheritance": 5, "Semantic + Multi-Structure": 20, "Structure-only": 571}
- Expected unit structure: kind=method; parent=Group; calls=['_', 'append', 'get_command', 'get_short_help_str', 'len', 'list_commands', 'max', 'section']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=[]
- Expected component scores: lexical=0.2195, semantic=0.4860, structure=0.0000.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.core._complete_visible_commands` | 12.9665 | `src/click/core.py` | same file; same module; calls: get_command, list_commands; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Group.format_commands` | 11.2958 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _, append, get_command, get_short_help_str; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Option.get_help_record` | 10.7765 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.types.DateTime.convert` | 10.3515 | `src/click/types.py` | same unit kind; calls: len; imports: __future__, abc, click.shell_completion, collections.abc |
| BM25 | `click::src.click.core._check_nested_chain` | 10.1820 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Option.get_help_record` | 0.2591 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Group.format_commands` | 0.2195 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _, append, get_command, get_short_help_str; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Group.__init__` | 0.2103 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.types.DateTime.convert` | 0.1961 | `src/click/types.py` | same unit kind; calls: len; imports: __future__, abc, click.shell_completion, collections.abc |
| Lexical | `click::src.click.core.Group.to_info_dict` | 0.1934 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: get_command, list_commands; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Group.format_options` | 0.5912 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.format_options` | 0.5542 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append, section, write_dl; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context` | 0.5374 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.format_help` | 0.5312 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Group.format_commands` | 0.4860 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _, append, get_command, get_short_help_str; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.types._NumberParamTypeBase.convert` | 0.2500 | `src/click/types.py` | same unit kind; calls: _; imports: __future__, abc, click.shell_completion, collections.abc |
| Structure-only | `click::src.click.exceptions.BadParameter.format_message` | 0.2500 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Structure-only | `click::src.click._winconsole._WindowsConsoleWriter._get_error_message` | 0.2500 | `src/click/_winconsole.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, sys |
| Structure-only | `click::src.click.exceptions.MissingParameter.__str__` | 0.2500 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Structure-only | `click::src.click.exceptions.FileError.format_message` | 0.2500 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + AST | `click::src.click.core.Group.format_options` | 0.2956 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.format_options` | 0.2771 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append, section, write_dl; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context` | 0.2687 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.format_help` | 0.2656 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Group.format_commands` | 0.2430 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _, append, get_command, get_short_help_str; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.exceptions.MissingParameter.format_message` | 0.6552 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + Calls | `click::src.click.exceptions.BadParameter.format_message` | 0.6265 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + Calls | `click::src.click.exceptions.MissingParameter.__str__` | 0.6186 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + Calls | `click::src.click.exceptions.FileError.format_message` | 0.6137 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + Calls | `click::src.click.types._NumberParamTypeBase.convert` | 0.5833 | `src/click/types.py` | same unit kind; calls: _; imports: __future__, abc, click.shell_completion, collections.abc |
| Semantic + Dependencies | `click::src.click.core.Group.format_options` | 0.2956 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.format_options` | 0.2771 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append, section, write_dl; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context` | 0.2687 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.format_help` | 0.2656 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Group.format_commands` | 0.2430 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _, append, get_command, get_short_help_str; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Group.format_options` | 0.2956 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.format_options` | 0.2771 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append, section, write_dl; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context` | 0.2687 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.format_help` | 0.2656 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Group.format_commands` | 0.2430 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: _, append, get_command, get_short_help_str; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Group.format_options` | 0.2956 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Option.get_help_record` | 0.2939 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.exceptions.MissingParameter.format_message` | 0.2802 | `src/click/exceptions.py` | same unit kind; calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + Multi-Structure | `click::src.click.exceptions.NoSuchOption` | 0.2775 | `src/click/exceptions.py` | calls: _; imports: __future__, collections.abc, gettext, globals |
| Semantic + Multi-Structure | `click::src.click.core.Command.format_options` | 0.2771 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append, section, write_dl; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Group.format_options` | 0.4730 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.format_options` | 0.4434 | `src/click/core.py` | same file; same module; same unit kind; calls: _, append, section, write_dl; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context` | 0.4299 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.format_help` | 0.4249 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command` | 0.3939 | `src/click/core.py` | same file; same module; calls: _, append, get_short_help_str, len; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.

## Lexical misses top 5; structure-only succeeds

### Example 1: click / `click::src.click.core.ParameterSource`

- Query: This is an :class:`~enum. ` that indicates the source of a parameter's value. Use :meth:`click.Context.get_parameter_source` to get the source for a parameter by name. Members are ordered from most explicit to least explicit source. This allows comparison to check if a value was explicitly provided: .. code-block:: python source = ctx.get_parameter_source("port") if source < click. . : ... # value was explicitly set .. versionchanged:: 8.3.3 Use :class:`~enum. ` and reorder members from most to least explicit. Supports comparison operators. .. versionchanged:: 8.0 Use :class:`~enum.Enum` and drop the ``validate`` method. .. versionchanged:: 8.0 Added the `` `` value.
- Expected: `click::src.click.core.ParameterSource` (`src/click/core.py`), rank positions: {"BM25": 1, "CodeInsight": 1, "Lexical": 6, "Semantic": 1, "Semantic + AST": 1, "Semantic + Calls": 6, "Semantic + Dependencies": 2, "Semantic + Inheritance": 2, "Semantic + Multi-Structure": 1, "Structure-only": 2}
- Expected unit structure: kind=class; parent=None; calls=['auto']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=['enum.IntEnum']
- Expected component scores: lexical=0.2942, semantic=0.5814, structure=0.2405.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.core.ParameterSource` | 59.2392 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| BM25 | `click::src.click.types.BoolParamType` | 38.5329 | `src/click/types.py` | same unit kind; imports: __future__, abc, click.shell_completion, collections.abc |
| BM25 | `click::src.click.core.Parameter` | 36.5225 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Command.get_params` | 34.6847 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Parameter._check_name_is_usable` | 27.7881 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.shell_completion.BashComplete.source` | 0.4456 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Lexical | `click::src.click.core.Context.set_parameter_source` | 0.4002 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.shell_completion.ShellComplete.source` | 0.3665 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Lexical | `click::src.click.core.Option.consume_value` | 0.3334 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Parameter.handle_parse_result` | 0.3262 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.ParameterSource` | 0.5814 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| Semantic | `click::src.click.core.Parameter.consume_value` | 0.5010 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Parameter.handle_parse_result` | 0.4947 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.decorators.custom_version_option` | 0.4752 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic | `click::src.click.core.Parameter.resolve_envvar_value` | 0.4741 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click._utils.Sentinel` | 0.3631 | `src/click/_utils.py` | same unit kind; imports: __future__, enum, typing |
| Structure-only | `click::src.click.core.ParameterSource` | 0.2405 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| Structure-only | `click::src.click.core.Parameter.handle_parse_result` | 0.1927 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Command.shell_complete` | 0.1760 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Parameter` | 0.1597 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.ParameterSource` | 0.3867 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| Semantic + AST | `click::src.click.core.Context.get_parameter_source` | 0.3175 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.exceptions.NoSuchCommand` | 0.3128 | `src/click/exceptions.py` | same unit kind; imports: __future__, collections.abc, gettext, globals |
| Semantic + AST | `click::src.click._utils.Sentinel` | 0.3087 | `src/click/_utils.py` | same unit kind; imports: __future__, enum, typing |
| Semantic + AST | `click::src.click.core.Command` | 0.3063 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.shell_completion._is_incomplete_argument` | 0.5236 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Semantic + Calls | `click::src.click.core.Parameter.handle_parse_result` | 0.5031 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.shell_complete` | 0.3954 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Parameter` | 0.3139 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command` | 0.2917 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click._utils.Sentinel` | 0.4294 | `src/click/_utils.py` | same unit kind; imports: __future__, enum, typing |
| Semantic + Dependencies | `click::src.click.core.ParameterSource` | 0.4046 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| Semantic + Dependencies | `click::src.click._utils.Sentinel.__reduce_ex__` | 0.3793 | `src/click/_utils.py` | imports: __future__, enum, typing |
| Semantic + Dependencies | `click::src.click.core.Parameter.consume_value` | 0.3644 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Parameter.handle_parse_result` | 0.3613 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click._utils.Sentinel` | 0.6263 | `src/click/_utils.py` | same unit kind; imports: __future__, enum, typing |
| Semantic + Inheritance | `click::src.click.core.ParameterSource` | 0.5619 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| Semantic + Inheritance | `click::src.click.core.Parameter.consume_value` | 0.2505 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Parameter.handle_parse_result` | 0.2474 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.decorators.custom_version_option` | 0.2376 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Multi-Structure | `click::src.click.core.ParameterSource` | 0.4110 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| Semantic + Multi-Structure | `click::src.click._utils.Sentinel` | 0.3943 | `src/click/_utils.py` | same unit kind; imports: __future__, enum, typing |
| Semantic + Multi-Structure | `click::src.click.core.Parameter.handle_parse_result` | 0.3437 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.shell_completion._is_incomplete_argument` | 0.2986 | `src/click/shell_completion.py` | imports: __future__, collections.abc, gettext, os |
| Semantic + Multi-Structure | `click::src.click.core.Parameter` | 0.2843 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.ParameterSource` | 0.5132 | `src/click/core.py` | same file; same module; same unit kind; calls: auto; imports: __future__, _utils, abc, click.shell_completion; bases: enum.IntEnum |
| CodeInsight | `click::src.click.core.Parameter.handle_parse_result` | 0.4343 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Parameter.consume_value` | 0.4137 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click._utils.Sentinel` | 0.4130 | `src/click/_utils.py` | same unit kind; imports: __future__, enum, typing |
| CodeInsight | `click::src.click.core.Parameter.resolve_envvar_value` | 0.3923 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 2: click / `click::src.click.core.Context._make_sub_context`

- Query: Create a new context of the same type as this context, but for a new . :meta private:
- Expected: `click::src.click.core.Context._make_sub_context` (`src/click/core.py`), rank positions: {"BM25": 36, "CodeInsight": 1, "Lexical": 47, "Semantic": 2, "Semantic + AST": 1, "Semantic + Calls": 1, "Semantic + Dependencies": 2, "Semantic + Inheritance": 2, "Semantic + Multi-Structure": 1, "Structure-only": 1}
- Expected unit structure: kind=method; parent=Context; calls=['type']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=[]
- Expected component scores: lexical=0.0846, semantic=0.4945, structure=0.2848.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.decorators.pass_meta_key` | 14.3586 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| BM25 | `click::src.click.types.BoolParamType` | 13.6229 | `src/click/types.py` | imports: __future__, abc, click.shell_completion, collections.abc |
| BM25 | `click::src.click.core.ParameterSource` | 13.0140 | `src/click/core.py` | same file; same module; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Command.get_params` | 12.9503 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Parameter` | 11.9669 | `src/click/core.py` | same file; same module; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Context.meta` | 0.2599 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.globals.get_current_context` | 0.2194 | `src/click/globals.py` | imports: __future__, typing |
| Lexical | `click::src.click.globals.get_current_context` | 0.2091 | `src/click/globals.py` | imports: __future__, typing |
| Lexical | `click::src.click.core.Parameter.get_default` | 0.1805 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Parameter.add_to_parser` | 0.1757 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.make_context` | 0.5077 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context._make_sub_context` | 0.4945 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Parameter.make_metavar` | 0.4911 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.decorators.pass_context` | 0.4531 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic | `click::src.click.core.Argument.get_help_spec` | 0.4502 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._make_sub_context` | 0.2848 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.abort` | 0.2238 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.find_object` | 0.2238 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context._close_with_exception_info` | 0.2238 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.get_parameter_source` | 0.2238 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context._make_sub_context` | 0.6949 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.with_resource` | 0.6453 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.invoke` | 0.6002 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.meta` | 0.5952 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.__enter__` | 0.5946 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Context._make_sub_context` | 0.3693 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.make_context` | 0.2538 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Parameter.make_metavar` | 0.2455 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.types._NumberRangeBase.__repr__` | 0.2380 | `src/click/types.py` | same unit kind; calls: type; imports: __future__, abc, click.shell_completion, collections.abc |
| Semantic + Calls | `click::src.click.decorators.pass_context` | 0.2266 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Dependencies | `click::src.click.core.Command.make_context` | 0.2538 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context._make_sub_context` | 0.2473 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Parameter.make_metavar` | 0.2455 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.decorators.pass_context` | 0.2266 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Dependencies | `click::src.click.core.Argument.get_help_spec` | 0.2251 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.make_context` | 0.2538 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context._make_sub_context` | 0.2473 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Parameter.make_metavar` | 0.2455 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.decorators.pass_context` | 0.2266 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| Semantic + Inheritance | `click::src.click.core.Argument.get_help_spec` | 0.2251 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context._make_sub_context` | 0.3897 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.with_resource` | 0.3096 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.meta` | 0.2911 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.invoke` | 0.2644 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.__enter__` | 0.2589 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context._make_sub_context` | 0.4526 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: type; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.make_context` | 0.4062 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Parameter.make_metavar` | 0.3929 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.decorators.pass_context` | 0.3625 | `src/click/decorators.py` | imports: __future__, functools, gettext, globals |
| CodeInsight | `click::src.click.core.Context.with_resource` | 0.3611 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 3: click / `click::src.click.core.Context.forward`

- Query: Similar to :meth:`invoke` but fills in default keyword arguments from the current context if the other command expects it. This cannot invoke callbacks directly, only other commands. .. versionchanged:: 8.0 All `` `` are tracked in :attr:`params` so they will be passed if `` `` is called at multiple levels.
- Expected: `click::src.click.core.Context.forward` (`src/click/core.py`), rank positions: {"BM25": 17, "CodeInsight": 5, "Lexical": 10, "Semantic": 5, "Semantic + AST": 4, "Semantic + Calls": 1, "Semantic + Dependencies": 5, "Semantic + Inheritance": 5, "Semantic + Multi-Structure": 1, "Structure-only": 1}
- Expected unit structure: kind=method; parent=Context; calls=['TypeError', 'invoke', 'isinstance']; imports=['__future__', '_utils', 'abc', 'click.shell_completion', 'collections', 'collections.abc', 'contextlib', 'decorators']; bases=[]
- Expected component scores: lexical=0.1876, semantic=0.5073, structure=0.2648.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.types.BoolParamType` | 31.8817 | `src/click/types.py` | calls: isinstance; imports: __future__, abc, click.shell_completion, collections.abc |
| BM25 | `click::src.click.parser.__getattr__` | 31.8567 | `src/click/parser.py` | imports: __future__, _utils, collections, collections.abc |
| BM25 | `click::src.click.__init__.__getattr__` | 26.9102 | `src/click/__init__.py` | imports: __future__, decorators, exceptions, formatting |
| BM25 | `click::src.click.core.Parameter` | 26.4776 | `src/click/core.py` | same file; same module; calls: isinstance; imports: __future__, _utils, abc, click.shell_completion |
| BM25 | `click::src.click.core.Command.get_params` | 26.4142 | `src/click/core.py` | same file; same module; same unit kind; calls: isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Context.invoke` | 0.2582 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Group.to_info_dict` | 0.2317 | `src/click/core.py` | same file; same module; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Group` | 0.2130 | `src/click/core.py` | same file; same module; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Context.invoke` | 0.2109 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Lexical | `click::src.click.core.Command.invoke` | 0.2065 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context.invoke` | 0.5768 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context.invoke` | 0.5768 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context.invoke` | 0.5768 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Command.invoke` | 0.5330 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic | `click::src.click.core.Context.forward` | 0.5073 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Context.forward` | 0.2648 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Command.invoke` | 0.2157 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.core.Command.main` | 0.1791 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Structure-only | `click::src.click.decorators.pass_meta_key` | 0.1415 | `src/click/decorators.py` | calls: invoke; imports: __future__, functools, gettext, globals |
| Structure-only | `click::src.click.core.Context.abort` | 0.1171 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.invoke` | 0.5227 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.invoke` | 0.4922 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.invoke` | 0.4922 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Context.forward` | 0.4879 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + AST | `click::src.click.core.Command.invoke` | 0.4725 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Context.forward` | 0.5491 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Command.invoke` | 0.4919 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.core.Group.invoke` | 0.4779 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Calls | `click::src.click.decorators.pass_meta_key` | 0.4771 | `src/click/decorators.py` | calls: invoke; imports: __future__, functools, gettext, globals |
| Semantic + Calls | `click::src.click.decorators.make_pass_decorator` | 0.4346 | `src/click/decorators.py` | calls: invoke; imports: __future__, functools, gettext, globals |
| Semantic + Dependencies | `click::src.click.core.Context.invoke` | 0.2884 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context.invoke` | 0.2884 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context.invoke` | 0.2884 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Command.invoke` | 0.2665 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Dependencies | `click::src.click.core.Context.forward` | 0.2537 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context.invoke` | 0.2884 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context.invoke` | 0.2884 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context.invoke` | 0.2884 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Command.invoke` | 0.2665 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Inheritance | `click::src.click.core.Context.forward` | 0.2537 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.forward` | 0.3861 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Command.invoke` | 0.3744 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.invoke` | 0.3470 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.invoke` | 0.3394 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| Semantic + Multi-Structure | `click::src.click.core.Context.invoke` | 0.3394 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.invoke` | 0.4849 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, isinstance; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.invoke` | 0.4818 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.invoke` | 0.4818 | `src/click/core.py` | same file; same module; same parent; same unit kind; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Command.invoke` | 0.4696 | `src/click/core.py` | same file; same module; same unit kind; calls: invoke; imports: __future__, _utils, abc, click.shell_completion |
| CodeInsight | `click::src.click.core.Context.forward` | 0.4588 | `src/click/core.py` | same file; same module; same parent; same unit kind; calls: TypeError, invoke, isinstance; imports: __future__, _utils, abc, click.shell_completion |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.

## All evaluated methods miss top 5

### Example 1: click / `click::src.click._compat._is_compatible_text_stream`

- Query: Check if a 's and attributes are compatible with the desired values.
- Expected: `click::src.click._compat._is_compatible_text_stream` (`src/click/_compat.py`), rank positions: {"BM25": 160, "CodeInsight": 21, "Lexical": 208, "Semantic": 18, "Semantic + AST": 18, "Semantic + Calls": 22, "Semantic + Dependencies": 18, "Semantic + Inheritance": 18, "Semantic + Multi-Structure": 21, "Structure-only": 203}
- Expected unit structure: kind=function; parent=None; calls=['_is_compat_stream_attr']; imports=['__future__', '_winconsole', 'codecs', 'collections.abc', 'errno', 'io', 'locale', 'os']; bases=[]
- Expected component scores: lexical=0.0000, semantic=0.2324, structure=0.0000.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click.types.BoolParamType` | 14.6783 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| BM25 | `click::src.click.core.ParameterSource` | 14.4507 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| BM25 | `click::src.click.types.Tuple.convert` | 12.8390 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| BM25 | `click::src.click.core.Command.get_params` | 11.4558 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| BM25 | `click::src.click._compat.open_stream` | 10.4621 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Lexical | `click::src.click.types.Tuple.convert` | 0.0764 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.types.BoolParamType` | 0.0712 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.types.Choice.get_missing_message` | 0.0669 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.types.Choice.get_invalid_choice_message` | 0.0488 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Lexical | `click::src.click.types.Choice.get_metavar` | 0.0461 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic | `click::src.click.core.Parameter.value_is_missing` | 0.3661 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic | `click::src.click.types.CompositeParamType` | 0.3318 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic | `click::src.click.types.BoolParamType.convert` | 0.3111 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic | `click::src.click.core.Option._infer_flag_kind` | 0.3061 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic | `click::src.click.types.Choice.convert` | 0.2922 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Structure-only | `click::src.click.types.Choice.get_missing_message` | 0.0790 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Structure-only | `click::src.click.types.Choice.get_invalid_choice_message` | 0.0476 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Structure-only | `click::src.click.types.Choice.get_metavar` | 0.0392 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Structure-only | `click::src.click.types.Choice` | 0.0267 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Structure-only | `click::src.click.core.Context.abort` | 0.0000 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + AST | `click::src.click.core.Parameter.value_is_missing` | 0.1830 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + AST | `click::src.click.types.CompositeParamType` | 0.1659 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + AST | `click::src.click.types.BoolParamType.convert` | 0.1555 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + AST | `click::src.click.core.Option._infer_flag_kind` | 0.1531 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + AST | `click::src.click.types.Choice.convert` | 0.1461 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Calls | `click::src.click.types.Choice.get_missing_message` | 0.2718 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Calls | `click::src.click.types.Choice.get_invalid_choice_message` | 0.2100 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Calls | `click::src.click.core.Parameter.value_is_missing` | 0.1830 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + Calls | `click::src.click.types.Choice.get_metavar` | 0.1734 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Calls | `click::src.click.types.Choice` | 0.1678 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Dependencies | `click::src.click.core.Parameter.value_is_missing` | 0.1830 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + Dependencies | `click::src.click.types.CompositeParamType` | 0.1659 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Dependencies | `click::src.click.types.BoolParamType.convert` | 0.1555 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Dependencies | `click::src.click.core.Option._infer_flag_kind` | 0.1531 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + Dependencies | `click::src.click.types.Choice.convert` | 0.1461 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Inheritance | `click::src.click.core.Parameter.value_is_missing` | 0.1830 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + Inheritance | `click::src.click.types.CompositeParamType` | 0.1659 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Inheritance | `click::src.click.types.BoolParamType.convert` | 0.1555 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Inheritance | `click::src.click.core.Option._infer_flag_kind` | 0.1531 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + Inheritance | `click::src.click.types.Choice.convert` | 0.1461 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Multi-Structure | `click::src.click.core.Parameter.value_is_missing` | 0.1830 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Semantic + Multi-Structure | `click::src.click.types.CompositeParamType` | 0.1659 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Multi-Structure | `click::src.click.types.BoolParamType.convert` | 0.1555 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Multi-Structure | `click::src.click.types.Choice.get_missing_message` | 0.1533 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Semantic + Multi-Structure | `click::src.click.core.Option._infer_flag_kind` | 0.1531 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| CodeInsight | `click::src.click.core.Parameter.value_is_missing` | 0.2929 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| CodeInsight | `click::src.click.types.CompositeParamType` | 0.2654 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| CodeInsight | `click::src.click.types.BoolParamType.convert` | 0.2489 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| CodeInsight | `click::src.click.core.Option._infer_flag_kind` | 0.2449 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| CodeInsight | `click::src.click.types.Choice.convert` | 0.2338 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 2: click / `click::src.click._compat._wrap_io_open`

- Query: Handles not passing `` `` and `` `` in binary .
- Expected: `click::src.click._compat._wrap_io_open` (`src/click/_compat.py`), rank positions: {"BM25": 181, "CodeInsight": 44, "Lexical": 355, "Semantic": 44, "Semantic + AST": 44, "Semantic + Calls": 44, "Semantic + Dependencies": 44, "Semantic + Inheritance": 44, "Semantic + Multi-Structure": 44, "Structure-only": 352}
- Expected unit structure: kind=function; parent=None; calls=['open']; imports=['__future__', '_winconsole', 'codecs', 'collections.abc', 'errno', 'io', 'locale', 'os']; bases=[]
- Expected component scores: lexical=0.0000, semantic=0.2667, structure=0.0000.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click._compat.open_stream` | 10.2472 | `src/click/_compat.py` | same file; same module; same unit kind; calls: open; imports: __future__, _winconsole, codecs, collections.abc |
| BM25 | `click::src.click._compat.get_binary_stderr` | 7.8850 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| BM25 | `click::src.click._compat.get_binary_stdout` | 7.8850 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| BM25 | `click::src.click._compat.get_binary_stdin` | 7.8850 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| BM25 | `click::src.click.core.Context._default_map_has` | 7.2222 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Lexical | `click::src.click._compat.get_binary_stdout` | 0.1632 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Lexical | `click::src.click._compat.get_binary_stdin` | 0.1594 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Lexical | `click::src.click._compat.get_binary_stderr` | 0.1351 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Lexical | `click::src.click._compat.open_stream` | 0.1198 | `src/click/_compat.py` | same file; same module; same unit kind; calls: open; imports: __future__, _winconsole, codecs, collections.abc |
| Lexical | `click::src.click.testing.make_input_stream` | 0.0548 | `src/click/testing.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Semantic | `click::src.click._compat.get_binary_stdin` | 0.3969 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.3738 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic | `click::src.click.testing.CliRunner.__init__` | 0.3446 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic | `click::src.click._compat.get_binary_stdout` | 0.3440 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic | `click::src.click.testing.CliRunner` | 0.3419 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Structure-only | `click::src.click.core.Context.abort` | 0.0000 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Structure-only | `click::src.click.types.Path.coerce_path_result` | 0.0000 | `src/click/types.py` | imports: __future__, collections.abc, os, sys |
| Structure-only | `click::src.click.core.Parameter.spec` | 0.0000 | `src/click/core.py` | imports: __future__, collections.abc, errno, os |
| Structure-only | `click::src.click.exceptions.BadParameter` | 0.0000 | `src/click/exceptions.py` | imports: __future__, collections.abc, typing |
| Structure-only | `click::src.click.testing.Result` | 0.0000 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + AST | `click::src.click._compat.get_binary_stdin` | 0.1984 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + AST | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.1869 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + AST | `click::src.click.testing.CliRunner.__init__` | 0.1723 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + AST | `click::src.click._compat.get_binary_stdout` | 0.1720 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + AST | `click::src.click.testing.CliRunner` | 0.1709 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Calls | `click::src.click._compat.get_binary_stdin` | 0.1984 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Calls | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.1869 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + Calls | `click::src.click.testing.CliRunner.__init__` | 0.1723 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Calls | `click::src.click._compat.get_binary_stdout` | 0.1720 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Calls | `click::src.click.testing.CliRunner` | 0.1709 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Dependencies | `click::src.click._compat.get_binary_stdin` | 0.1984 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Dependencies | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.1869 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + Dependencies | `click::src.click.testing.CliRunner.__init__` | 0.1723 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Dependencies | `click::src.click._compat.get_binary_stdout` | 0.1720 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Dependencies | `click::src.click.testing.CliRunner` | 0.1709 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Inheritance | `click::src.click._compat.get_binary_stdin` | 0.1984 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Inheritance | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.1869 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + Inheritance | `click::src.click.testing.CliRunner.__init__` | 0.1723 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Inheritance | `click::src.click._compat.get_binary_stdout` | 0.1720 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Inheritance | `click::src.click.testing.CliRunner` | 0.1709 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Multi-Structure | `click::src.click._compat.get_binary_stdin` | 0.1984 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Multi-Structure | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.1869 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| Semantic + Multi-Structure | `click::src.click.testing.CliRunner.__init__` | 0.1723 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| Semantic + Multi-Structure | `click::src.click._compat.get_binary_stdout` | 0.1720 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| Semantic + Multi-Structure | `click::src.click.testing.CliRunner` | 0.1709 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| CodeInsight | `click::src.click._compat.get_binary_stdin` | 0.3175 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| CodeInsight | `click::src.click._winconsole._WindowsConsoleRawIOBase.__init__` | 0.2990 | `src/click/_winconsole.py` | imports: __future__, collections.abc, io, sys |
| CodeInsight | `click::src.click.testing.CliRunner.__init__` | 0.2757 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |
| CodeInsight | `click::src.click._compat.get_binary_stdout` | 0.2752 | `src/click/_compat.py` | same file; same module; same unit kind; imports: __future__, _winconsole, codecs, collections.abc |
| CodeInsight | `click::src.click.testing.CliRunner` | 0.2735 | `src/click/testing.py` | imports: __future__, collections.abc, io, os |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
### Example 3: click / `click::src.click._termui_impl._pager_contextmanager`

- Query: Decide what method to use for paging through text.
- Expected: `click::src.click._termui_impl._pager_contextmanager` (`src/click/_termui_impl.py`), rank positions: {"BM25": 431, "CodeInsight": 7, "Lexical": 390, "Semantic": 7, "Semantic + AST": 44, "Semantic + Calls": 7, "Semantic + Dependencies": 7, "Semantic + Inheritance": 7, "Semantic + Multi-Structure": 8, "Structure-only": 531}
- Expected unit structure: kind=function; parent=None; calls=['StringIO', '_default_text_stdout', '_nullpager', '_pipepager', '_resolve_pager_command', '_tempfilepager', 'get', 'isatty']; imports=['__future__', '_compat', 'collections.abc', 'contextlib', 'exceptions', 'gettext', 'io', 'math']; bases=[]
- Expected component scores: lexical=0.0000, semantic=0.2896, structure=0.0000.

| Method | Top-5 candidate | Score | File | Structural overlap vs expected |
|---|---|---:|---|---|
| BM25 | `click::src.click._termui_impl.ProgressBar.generator` | 9.1212 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| BM25 | `click::src.click._termui_impl.ProgressBar.__iter__` | 9.0757 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| BM25 | `click::src.click._textwrap.TextWrapper.indent_only` | 7.3149 | `src/click/_textwrap.py` | imports: __future__, _compat, collections.abc, contextlib |
| BM25 | `click::src.click.formatting.wrap_text` | 7.2729 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| BM25 | `click::src.click._compat.get_binary_stderr` | 6.8326 | `src/click/_compat.py` | same unit kind; imports: __future__, collections.abc, io, os |
| Lexical | `click::src.click.core.Command.get_short_help_str` | 0.4871 | `src/click/core.py` | imports: __future__, collections.abc, contextlib, exceptions |
| Lexical | `click::src.click.termui.unstyle` | 0.4851 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Lexical | `click::src.click._termui_impl._PagerWriter.write` | 0.4383 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| Lexical | `click::src.click.core.Command.format_help_text` | 0.3932 | `src/click/core.py` | imports: __future__, collections.abc, contextlib, exceptions |
| Lexical | `click::src.click._textwrap._truncate_visible` | 0.3768 | `src/click/_textwrap.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click.termui.echo_via_pager` | 0.3778 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click._termui_impl._nullpager` | 0.3236 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click.formatting.wrap_text` | 0.3230 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click._termui_impl._resolve_pager_command` | 0.3226 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic | `click::src.click._termui_impl.get_pager_file` | 0.3115 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Structure-only | `click::src.click.types._NumberParamTypeBase.convert` | 0.0471 | `src/click/types.py` | imports: __future__, _compat, collections.abc, exceptions |
| Structure-only | `click::src.click._termui_impl.ProgressBar.__enter__` | 0.0471 | `src/click/_termui_impl.py` | same file; same module; imports: __future__, _compat, collections.abc, contextlib |
| Structure-only | `click::src.click.parser._Argument.process` | 0.0471 | `src/click/parser.py` | imports: __future__, collections.abc, exceptions, gettext |
| Structure-only | `click::src.click.testing.BytesIOCopy.write` | 0.0471 | `src/click/testing.py` | imports: __future__, _compat, collections.abc, contextlib |
| Structure-only | `click::src.click.testing.EchoingStdin.__repr__` | 0.0471 | `src/click/testing.py` | imports: __future__, _compat, collections.abc, contextlib |
| Semantic + AST | `click::src.click.formatting.HelpFormatter.write_paragraph` | 0.2219 | `src/click/formatting.py` | imports: __future__, _compat, collections.abc, contextlib |
| Semantic + AST | `click::src.click._textwrap.TextWrapper._handle_long_word` | 0.2054 | `src/click/_textwrap.py` | imports: __future__, _compat, collections.abc, contextlib |
| Semantic + AST | `click::src.click.formatting.HelpFormatter.write_text` | 0.2044 | `src/click/formatting.py` | imports: __future__, _compat, collections.abc, contextlib |
| Semantic + AST | `click::src.click.formatting.HelpFormatter.write_usage` | 0.2025 | `src/click/formatting.py` | imports: __future__, _compat, collections.abc, contextlib |
| Semantic + AST | `click::src.click.core.Group.format_commands` | 0.1980 | `src/click/core.py` | imports: __future__, collections.abc, contextlib, exceptions |
| Semantic + Calls | `click::src.click.termui.echo_via_pager` | 0.1889 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Calls | `click::src.click._termui_impl._nullpager` | 0.1618 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Calls | `click::src.click.formatting.wrap_text` | 0.1615 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Calls | `click::src.click._termui_impl._resolve_pager_command` | 0.1613 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Calls | `click::src.click._termui_impl.get_pager_file` | 0.1557 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click.termui.echo_via_pager` | 0.1889 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl._nullpager` | 0.1618 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click.formatting.wrap_text` | 0.1615 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl._resolve_pager_command` | 0.1613 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Dependencies | `click::src.click._termui_impl.get_pager_file` | 0.1557 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click.termui.echo_via_pager` | 0.1889 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._termui_impl._nullpager` | 0.1618 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click.formatting.wrap_text` | 0.1615 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._termui_impl._resolve_pager_command` | 0.1613 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Inheritance | `click::src.click._termui_impl.get_pager_file` | 0.1557 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click.termui.echo_via_pager` | 0.1889 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click._termui_impl._nullpager` | 0.1618 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click.formatting.wrap_text` | 0.1615 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click._termui_impl._resolve_pager_command` | 0.1613 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| Semantic + Multi-Structure | `click::src.click._termui_impl.get_pager_file` | 0.1557 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click.termui.echo_via_pager` | 0.3022 | `src/click/termui.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click._termui_impl._nullpager` | 0.2589 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click.formatting.wrap_text` | 0.2584 | `src/click/formatting.py` | same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click._termui_impl._resolve_pager_command` | 0.2581 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |
| CodeInsight | `click::src.click._termui_impl.get_pager_file` | 0.2492 | `src/click/_termui_impl.py` | same file; same module; same unit kind; imports: __future__, _compat, collections.abc, contextlib |

Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence.
