# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-07-09T21:08:09.452Z
> Files: 502 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.agent-config.toml` (~14 tok)
- `.DS_Store` (~2731 tok)
- `.gitignore` — Git ignore rules (~42 tok)
- `CLAUDE.md` — OpenWolf (~66 tok)
- `GEMINI.md` (~9 tok)
- `local.env` (~42 tok)
- `README.md` — Project documentation (~697 tok)
- `requirements.txt` — Python dependencies (~96 tok)
- `test_config.py` — Test file (~735 tok)
- `token_cache.json` (~495 tok)
- `upcloud.code-workspace` (~12 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## .github/

- `copilot-instructions.md` (~136 tok)

## .github/workflows/

- `dev-to-trunk.yml` — CI: Dev to Trunk Auto-PR (~983 tok)
- `pr-to-prod.yml` — CI: 'upcloud to production' (~195 tok)

## archive/

- `test_paths.py` — URL configuration (~371 tok)

## upcloud/

- `__init__.py` (~58 tok)
- `.DS_Store` (~1639 tok)
- `config.py` — Config: get_access_token, get_new_token, refresh_access_token, raise_exception + 1 more (~922 tok)
- `onedrive_client.py` — URL configuration (~2939 tok)
- `server.py` — API: GET (1 endpoints) (~353 tok)
- `upcloud.py` — main, check_and_upload (~532 tok)
- `utils.py` — get_files_to_upload (~44 tok)

## venv/

- `.DS_Store` (~1639 tok)
- `.gitignore` — Git ignore rules (~19 tok)
- `pyvenv.cfg` (~90 tok)

## venv/bin/

- `activate` — This file must be used with "source bin/activate" *from bash* (~571 tok)
- `activate.csh` — This file must be used with "source bin/activate.csh" *from csh*. (~254 tok)
- `activate.fish` — This file must be used with "source <venv>/bin/activate.fish" *from fish* (~595 tok)
- `Activate.ps1` — Declares from (~2409 tok)
- `dotenv` — -*- coding: utf-8 -*- (~74 tok)
- `fastapi` — -*- coding: utf-8 -*- (~73 tok)
- `normalizer` — -*- coding: utf-8 -*- (~79 tok)
- `pip` — -*- coding: utf-8 -*- (~76 tok)
- `pip3` — -*- coding: utf-8 -*- (~76 tok)
- `pip3.13` — -*- coding: utf-8 -*- (~76 tok)
- `tqdm` — -*- coding: utf-8 -*- (~72 tok)
- `uvicorn` — -*- coding: utf-8 -*- (~73 tok)

## venv/lib/

- `.DS_Store` (~1640 tok)

## venv/lib/python3.13/

- `.DS_Store` (~1640 tok)

## venv/lib/python3.13/site-packages/

- `typing_extensions.py` — _Sentinel: final, done, done, IntVar + 10 more (~38415 tok)

## venv/lib/python3.13/site-packages/Deprecated-1.2.15.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE.rst` (~271 tok)
- `METADATA` — Declares or (~1475 tok)
- `RECORD` (~239 tok)
- `top_level.txt` (~3 tok)
- `WHEEL` (~30 tok)

## venv/lib/python3.13/site-packages/annotated_types-0.7.0.dist-info/

- `INSTALLER` (~2 tok)
- `METADATA` — Declares MyClass (~4013 tok)
- `RECORD` (~214 tok)
- `WHEEL` (~24 tok)

## venv/lib/python3.13/site-packages/annotated_types-0.7.0.dist-info/licenses/

- `LICENSE` — Project license (~289 tok)

## venv/lib/python3.13/site-packages/annotated_types/

- `__init__.py` — Declares from (~3949 tok)
- `py.typed` (~0 tok)
- `test_cases.py` — Test file (~1834 tok)

## venv/lib/python3.13/site-packages/anyio-4.6.2.post1.dist-info/

- `entry_points.txt` (~10 tok)
- `INSTALLER` (~2 tok)
- `LICENSE` — Project license (~288 tok)
- `METADATA` (~1252 tok)
- `RECORD` (~1486 tok)
- `top_level.txt` (~2 tok)
- `WHEEL` (~25 tok)

## venv/lib/python3.13/site-packages/anyio/

- `__init__.py` — Declares as (~1233 tok)
- `from_thread.py` — _BlockingAsyncContextManager: run, run_sync, run_async_cm, started + 11 more (~4994 tok)
- `lowlevel.py` — View: get, get, get (~1192 tok)
- `py.typed` (~0 tok)
- `pytest_plugin.py` — extract_backend_and_options, get_runner, pytest_configure, pytest_fixture_setup + 7 more (~1918 tok)
- `to_process.py` — from: run_sync, send_raw_command, current_default_process_limiter, process_worker (~2735 tok)
- `to_thread.py` — run_sync, current_default_thread_limiter (~685 tok)

## venv/lib/python3.13/site-packages/anyio/_backends/

- `__init__.py` (~0 tok)
- `_asyncio.py` — from: close, get_loop, run, find_root_task + 2 more (~26142 tok)
- `_trio.py` — from: cancel, deadline, deadline, cancel_called + 25 more (~11518 tok)

## venv/lib/python3.13/site-packages/anyio/_core/

- `__init__.py` (~0 tok)
- `_eventloop.py` — threadlocals: run, sleep, sleep_forever, sleep_until + 5 more (~1341 tok)
- `_exceptions.py` — BrokenResourceError: iterate_exceptions (~709 tok)
- `_fileio.py` — from: wrapped, aclose, read, read1 + 39 more (~5989 tok)
- `_resources.py` — aclose_forcefully (~125 tok)
- `_signals.py` — open_signal_receiver (~259 tok)
- `_sockets.py` — URL configuration (~6940 tok)
- `_streams.py` — Declares create_memory_object_stream (~516 tok)
- `_subprocesses.py` — run_process, drain_stream, open_process (~2218 tok)
- `_synchronization.py` — from: set, is_set, wait, statistics + 28 more (~5749 tok)
- `_tasks.py` — _IgnoredTaskStatus: started, cancel, deadline, deadline + 8 more (~1362 tok)
- `_testing.py` — TaskInfo: has_pending_cancellation, get_current_task, get_running_tasks, wait_all_tasks_blocked (~606 tok)
- `_typedattr.py` — TypedAttributeSet: typed_attribute, extra_attributes, extra, extra + 1 more (~717 tok)

## venv/lib/python3.13/site-packages/anyio/abc/

- `__init__.py` (~766 tok)
- `_eventloop.py` — AsyncBackend: run, current_token, current_time, cancelled_exception_class + 36 more (~2749 tok)
- `_resources.py` — AsyncResource: aclose (~224 tok)
- `_sockets.py` — _NullAsyncContextManager: extra_attributes, send_fds, receive_fds, accept + 3 more (~1790 tok)
- `_streams.py` — UnreliableObjectReceiveStream: receive, send, send_eof, receive + 3 more (~1886 tok)
- `_subprocesses.py` — Process: wait, terminate, kill, send_signal + 5 more (~591 tok)
- `_tasks.py` — TaskStatus: started, started, started, start_soon + 1 more (~781 tok)
- `_testing.py` — TestRunner: run_asyncgen_fixture, run_fixture, run_test (~521 tok)

## venv/lib/python3.13/site-packages/anyio/streams/

- `__init__.py` (~0 tok)
- `buffered.py` — BufferedByteReceiveStream: aclose, buffer, extra_attributes, receive + 2 more (~1286 tok)
- `file.py` — URL configuration (~1253 tok)
- `memory.py` — MemoryObjectStreamStatistics: statistics, receive_nowait, receive, clone + 9 more (~3015 tok)
- `stapled.py` — from: receive, send, send_eof, aclose + 9 more (~1230 tok)
- `text.py` — TextReceiveStream: receive, aclose, extra_attributes, send + 7 more (~1456 tok)
- `tls.py` — from: wrap, unwrap, aclose, receive + 6 more (~3641 tok)

## venv/lib/python3.13/site-packages/certifi-2024.8.30.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE` — Project license (~264 tok)
- `METADATA` (~593 tok)
- `RECORD` (~271 tok)
- `top_level.txt` (~2 tok)
- `WHEEL` (~25 tok)

## venv/lib/python3.13/site-packages/certifi/

- `__init__.py` (~27 tok)
- `__main__.py` (~70 tok)
- `cacert.pem` — Issuer: CN=GlobalSign Root CA O=GlobalSign nv-sa OU=Root CA (~79848 tok)
- `core.py` — URL patterns: 3 routes (~1265 tok)
- `py.typed` (~0 tok)

## venv/lib/python3.13/site-packages/cffi-1.17.1.dist-info/

- `entry_points.txt` (~19 tok)
- `INSTALLER` (~2 tok)
- `LICENSE` — Project license (~346 tok)
- `METADATA` (~409 tok)
- `RECORD` (~847 tok)
- `top_level.txt` (~5 tok)
- `WHEEL` (~30 tok)

## venv/lib/python3.13/site-packages/cffi/

- `__init__.py` (~147 tok)
- `_cffi_errors.h` — ifndef CFFI_MESSAGEBOX (~1117 tok)
- `_cffi_include.h` — *******  CPython-specific section  ********* (~4302 tok)
- `_embedding.h` — ** Support code for embedding **** (~5368 tok)
- `_imp_emulation.py` — get_suffixes, find_module, load_dynamic (~846 tok)
- `_shimmed_dist_utils.py` (~638 tok)
- `api.py` — FFI: cdef, are, embedding_api, dlopen + 8 more (~12049 tok)
- `backend_ctypes.py` — CTypesType: cmp, set_ffi, load_library, new_void_type + 1 more (~12130 tok)
- `cffi_opcode.py` — CffiOp: as_c_expr, as_python_bytes, format_four_bytes (~1638 tok)
- `commontypes.py` — resolve_common_type, win_common_types (~802 tok)
- `cparser.py` — specifier: source, replace, replace, replace_keeping_newlines + 2 more (~12797 tok)
- `error.py` — Declares FFIError (~251 tok)
- `ffiplatform.py` — URL configuration (~1024 tok)
- `lock.py` — allocate_lock: acquire (~214 tok)
- `model.py` — type qualifiers (~6228 tok)
- `parse_c_type.h` — Declares char (~1708 tok)
- `pkgconfig.py` — pkg-config, https://www.freedesktop.org/wiki/Software/pkg-config/ integration for cffi (~1250 tok)
- `recompiler.py` — GlobalExpr: as_c_expr, as_python_expr, as_c_expr, as_python_expr + 12 more (~18677 tok)
- `setuptools_ext.py` — URL configuration (~2535 tok)
- `vengine_cpy.py` — DEPRECATED: implementation for ffi.verify() (~12501 tok)
- `vengine_gen.py` — DEPRECATED: implementation for ffi.verify() (~7697 tok)
- `verifier.py` — DEPRECATED: implementation for ffi.verify() (~3195 tok)

## venv/lib/python3.13/site-packages/charset_normalizer-3.4.0.dist-info/

- `entry_points.txt` (~17 tok)
- `INSTALLER` (~2 tok)
- `LICENSE` — Project license (~286 tok)
- `METADATA` (~9088 tok)
- `RECORD` (~736 tok)
- `top_level.txt` (~5 tok)
- `WHEEL` (~30 tok)

## venv/lib/python3.13/site-packages/charset_normalizer/

- `__init__.py` — -*- coding: utf-8 -*- (~427 tok)
- `__main__.py` (~21 tok)
- `api.py` — from_bytes (~6446 tok)
- `cd.py` — encoding_unicode_range, unicode_range_languages, encoding_languages, mb_encoding_languages + 7 more (~3588 tok)
- `constant.py` — -*- coding: utf-8 -*- (~11200 tok)
- `legacy.py` — TODO: remove this check when dropping Python 3.7 support (~665 tok)
- `md.py` — MessDetectorPlugin: eligible, feed, reset, ratio + 26 more (~5752 tok)
- `models.py` — CharsetMatch: multi_byte_usage, add_submatch, encoding, encoding_aliases + 18 more (~3550 tok)
- `py.typed` (~0 tok)
- `utils.py` — is_accentuated, remove_accent, unicode_range, is_latin + 24 more (~3398 tok)
- `version.py` (~23 tok)

## venv/lib/python3.13/site-packages/charset_normalizer/cli/

- `__init__.py` (~29 tok)
- `__main__.py` — URL configuration (~2975 tok)

## venv/lib/python3.13/site-packages/click-8.1.7.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE.rst` (~369 tok)
- `METADATA` — Declares toolkit (~804 tok)
- `RECORD` (~666 tok)
- `top_level.txt` (~2 tok)
- `WHEEL` (~25 tok)

## venv/lib/python3.13/site-packages/click/

- `__init__.py` (~897 tok)
- `_compat.py` — URL configuration (~5356 tok)
- `_termui_impl.py` — ProgressBar: render_finish, pct, time_per_iteration, eta + 11 more (~6877 tok)
- `_textwrap.py` — TextWrapper: extra_indent, indent_only (~387 tok)
- `_winconsole.py` — This module is based on the excellent work by Adam Bartoš who (~2246 tok)
- `core.py` — ParameterSource: batch, augment_usage_errors, iter_params_for_processing, sort_key (~32596 tok)
- `decorators.py` — to: pass_context, new_func, pass_obj, new_func + 24 more (~5349 tok)
- `exceptions.py` — ClickException: format_message, show, show, format_message + 3 more (~2650 tok)
- `formatting.py` — Can force a width.  This is used by the test system (~2774 tok)
- `globals.py` — get_current_context, get_current_context, get_current_context, push_context + 2 more (~561 tok)
- `parser.py` — Option: split_opt, normalize_opt, split_arg_string, takes_value + 5 more (~5448 tok)
- `py.typed` (~0 tok)
- `shell_completion.py` — CompletionItem: shell_complete, func_name, source_vars, source + 12 more (~5275 tok)
- `termui.py` — object: hidden_prompt_func, prompt, prompt_func, confirm + 2 more (~8093 tok)
- `testing.py` — EchoingStdin: read, read1, readline, readlines + 13 more (~4596 tok)
- `types.py` — ParamType: to_info_dict, get_metavar, get_missing_message, convert + 13 more (~10398 tok)
- `utils.py` — URL configuration (~5799 tok)

## venv/lib/python3.13/site-packages/cryptography-43.0.3.dist-info/

- `INSTALLER` (~2 tok)
- `METADATA` (~1451 tok)
- `RECORD` (~4131 tok)
- `WHEEL` (~29 tok)

## venv/lib/python3.13/site-packages/cryptography-43.0.3.dist-info/license_files/

- `LICENSE` — Project license (~53 tok)
- `LICENSE.APACHE` — Declares name (~3030 tok)
- `LICENSE.BSD` (~409 tok)

## venv/lib/python3.13/site-packages/cryptography/

- `__about__.py` — This file is dual licensed under the terms of the Apache License, Version (~128 tok)
- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~104 tok)
- `exceptions.py` — This file is dual licensed under the terms of the Apache License, Version (~311 tok)
- `fernet.py` — This file is dual licensed under the terms of the Apache License, Version (~1914 tok)
- `py.typed` (~0 tok)
- `utils.py` — This file is dual licensed under the terms of the Apache License, Version (~1122 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~130 tok)
- `_oid.py` — This file is dual licensed under the terms of the Apache License, Version (~4344 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/backends/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~104 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/backends/openssl/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~88 tok)
- `backend.py` — This file is dual licensed under the terms of the Apache License, Version (~2757 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/bindings/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~52 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/bindings/_rust/

- `__init__.pyi` — This file is dual licensed under the terms of the Apache License, Version (~197 tok)
- `_openssl.pyi` — This file is dual licensed under the terms of the Apache License, Version (~62 tok)
- `asn1.pyi` — This file is dual licensed under the terms of the Apache License, Version (~95 tok)
- `exceptions.pyi` — This file is dual licensed under the terms of the Apache License, Version (~171 tok)
- `ocsp.pyi` — This file is dual licensed under the terms of the Apache License, Version (~232 tok)
- `pkcs12.pyi` — This file is dual licensed under the terms of the Apache License, Version (~372 tok)
- `pkcs7.pyi` — This file is dual licensed under the terms of the Apache License, Version (~260 tok)
- `test_support.pyi` — This file is dual licensed under the terms of the Apache License, Version (~250 tok)
- `x509.pyi` — This file is dual licensed under the terms of the Apache License, Version (~947 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/bindings/_rust/openssl/

- `__init__.pyi` — This file is dual licensed under the terms of the Apache License, Version (~365 tok)
- `aead.pyi` — This file is dual licensed under the terms of the Apache License, Version (~681 tok)
- `ciphers.pyi` — This file is dual licensed under the terms of the Apache License, Version (~347 tok)
- `cmac.pyi` — This file is dual licensed under the terms of the Apache License, Version (~151 tok)
- `dh.pyi` — This file is dual licensed under the terms of the Apache License, Version (~418 tok)
- `dsa.pyi` — This file is dual licensed under the terms of the Apache License, Version (~347 tok)
- `ec.pyi` — This file is dual licensed under the terms of the Apache License, Version (~451 tok)
- `ed25519.pyi` — This file is dual licensed under the terms of the Apache License, Version (~132 tok)
- `ed448.pyi` — This file is dual licensed under the terms of the Apache License, Version (~127 tok)
- `hashes.pyi` — This file is dual licensed under the terms of the Apache License, Version (~153 tok)
- `hmac.pyi` — This file is dual licensed under the terms of the Apache License, Version (~177 tok)
- `kdf.pyi` — This file is dual licensed under the terms of the Apache License, Version (~146 tok)
- `keys.pyi` — This file is dual licensed under the terms of the Apache License, Version (~233 tok)
- `poly1305.pyi` — This file is dual licensed under the terms of the Apache License, Version (~144 tok)
- `rsa.pyi` — This file is dual licensed under the terms of the Apache License, Version (~364 tok)
- `x25519.pyi` — This file is dual licensed under the terms of the Apache License, Version (~130 tok)
- `x448.pyi` — This file is dual licensed under the terms of the Apache License, Version (~125 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/bindings/openssl/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~52 tok)
- `_conditional.py` — This file is dual licensed under the terms of the Apache License, Version (~1476 tok)
- `binding.py` — This file is dual licensed under the terms of the Apache License, Version (~1155 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/decrepit/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~62 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/decrepit/ciphers/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~62 tok)
- `algorithms.py` — This file is dual licensed under the terms of the Apache License, Version (~720 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/primitives/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~52 tok)
- `_asymmetric.py` — This file is dual licensed under the terms of the Apache License, Version (~152 tok)
- `_cipheralgorithm.py` — This file is dual licensed under the terms of the Apache License, Version (~428 tok)
- `_serialization.py` — This file is dual licensed under the terms of the Apache License, Version (~1470 tok)
- `cmac.py` — This file is dual licensed under the terms of the Apache License, Version (~97 tok)
- `constant_time.py` — This file is dual licensed under the terms of the Apache License, Version (~121 tok)
- `hashes.py` — This file is dual licensed under the terms of the Apache License, Version (~1455 tok)
- `hmac.py` — This file is dual licensed under the terms of the Apache License, Version (~121 tok)
- `keywrap.py` — This file is dual licensed under the terms of the Apache License, Version (~1615 tok)
- `padding.py` — This file is dual licensed under the terms of the Apache License, Version (~1577 tok)
- `poly1305.py` — This file is dual licensed under the terms of the Apache License, Version (~102 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/primitives/asymmetric/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~52 tok)
- `dh.py` — This file is dual licensed under the terms of the Apache License, Version (~978 tok)
- `dsa.py` — This file is dual licensed under the terms of the Apache License, Version (~1128 tok)
- `ec.py` — This file is dual licensed under the terms of the Apache License, Version (~2980 tok)
- `ed25519.py` — This file is dual licensed under the terms of the Apache License, Version (~978 tok)
- `ed448.py` — This file is dual licensed under the terms of the Apache License, Version (~988 tok)
- `padding.py` — This file is dual licensed under the terms of the Apache License, Version (~825 tok)
- `rsa.py` — This file is dual licensed under the terms of the Apache License, Version (~2182 tok)
- `types.py` — This file is dual licensed under the terms of the Apache License, Version (~856 tok)
- `utils.py` — This file is dual licensed under the terms of the Apache License, Version (~226 tok)
- `x25519.py` — This file is dual licensed under the terms of the Apache License, Version (~955 tok)
- `x448.py` — This file is dual licensed under the terms of the Apache License, Version (~964 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/primitives/ciphers/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~195 tok)
- `aead.py` — This file is dual licensed under the terms of the Apache License, Version (~182 tok)
- `algorithms.py` — This file is dual licensed under the terms of the Apache License, Version (~1207 tok)
- `base.py` — This file is dual licensed under the terms of the Apache License, Version (~1204 tok)
- `modes.py` — This file is dual licensed under the terms of the Apache License, Version (~2341 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/primitives/kdf/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~215 tok)
- `concatkdf.py` — This file is dual licensed under the terms of the Apache License, Version (~1054 tok)
- `hkdf.py` — This file is dual licensed under the terms of the Apache License, Version (~862 tok)
- `kbkdf.py` — This file is dual licensed under the terms of the Apache License, Version (~2614 tok)
- `pbkdf2.py` — This file is dual licensed under the terms of the Apache License, Version (~558 tok)
- `scrypt.py` — This file is dual licensed under the terms of the Apache License, Version (~673 tok)
- `x963kdf.py` — This file is dual licensed under the terms of the Apache License, Version (~570 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/primitives/serialization/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~473 tok)
- `base.py` — This file is dual licensed under the terms of the Apache License, Version (~176 tok)
- `pkcs12.py` — This file is dual licensed under the terms of the Apache License, Version (~1284 tok)
- `pkcs7.py` — This file is dual licensed under the terms of the Apache License, Version (~3184 tok)
- `ssh.py` — This file is dual licensed under the terms of the Apache License, Version (~14833 tok)

## venv/lib/python3.13/site-packages/cryptography/hazmat/primitives/twofactor/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~74 tok)
- `hotp.py` — This file is dual licensed under the terms of the Apache License, Version (~851 tok)
- `totp.py` — This file is dual licensed under the terms of the Apache License, Version (~415 tok)

## venv/lib/python3.13/site-packages/cryptography/x509/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~2280 tok)
- `base.py` — This file is dual licensed under the terms of the Apache License, Version (~10595 tok)
- `certificate_transparency.py` — This file is dual licensed under the terms of the Apache License, Version (~646 tok)
- `extensions.py` — This file is dual licensed under the terms of the Apache License, Version (~19249 tok)
- `general_name.py` — This file is dual licensed under the terms of the Apache License, Version (~2239 tok)
- `name.py` — This file is dual licensed under the terms of the Apache License, Version (~4238 tok)
- `ocsp.py` — This file is dual licensed under the terms of the Apache License, Version (~5716 tok)
- `oid.py` — This file is dual licensed under the terms of the Apache License, Version (~253 tok)
- `verification.py` — This file is dual licensed under the terms of the Apache License, Version (~228 tok)

## venv/lib/python3.13/site-packages/deprecated/

- `__init__.py` — -*- coding: utf-8 -*- (~101 tok)
- `classic.py` — -*- coding: utf-8 -*- (~3032 tok)
- `sphinx.py` — coding: utf-8 (~3174 tok)

## venv/lib/python3.13/site-packages/dotenv/

- `__init__.py` — load_ipython_extension, get_cli_string (~370 tok)
- `__main__.py` — Entry point for cli, enables execution with `python -m dotenv` (~37 tok)
- `cli.py` — enumerate_env, cli, stream_file, list + 5 more (~1660 tok)
- `ipython.py` — class: dotenv, load_ipython_extension (~373 tok)
- `main.py` — View: get (~3457 tok)
- `parser.py` — Original: make_regex, start, set, advance + 13 more (~1482 tok)
- `py.typed` — Marker file for PEP 561 (~7 tok)
- `variables.py` — Atom: resolve, resolve, resolve, parse_variables (~671 tok)
- `version.py` (~7 tok)

## venv/lib/python3.13/site-packages/fastapi-0.115.4.dist-info/

- `entry_points.txt` (~16 tok)
- `INSTALLER` (~2 tok)
- `METADATA` — Declares hints (~7150 tok)
- `RECORD` (~1774 tok)
- `REQUESTED` (~0 tok)
- `WHEEL` (~24 tok)

## venv/lib/python3.13/site-packages/fastapi-0.115.4.dist-info/licenses/

- `LICENSE` — Project license (~290 tok)

## venv/lib/python3.13/site-packages/fastapi/

- `__init__.py` — FastAPI framework, high performance, easy to learn, fast to code, ready for production (~309 tok)
- `__main__.py` (~11 tok)
- `_compat.py` — Pydantic model (43 fields) (~6835 tok)
- `applications.py` — API: GET (2 endpoints) (~50376 tok)
- `background.py` — API: POST (1 endpoints) (~506 tok)
- `cli.py` — main (~120 tok)
- `concurrency.py` — contextmanager_in_threadpool (~401 tok)
- `datastructures.py` — API: POST (2 endpoints) (~1648 tok)
- `encoders.py` — isoformat, decimal_encoder, generate_encoders_by_class_tuples, jsonable_encoder (~3163 tok)
- `exception_handlers.py` — http_exception_handler, request_validation_exception_handler, websocket_request_validation_exception_handler (~381 tok)
- `exceptions.py` — API: GET (1 endpoints) (~1420 tok)
- `logger.py` (~16 tok)
- `param_functions.py` — API: GET (1 endpoints) (~18292 tok)
- `params.py` — Declares import (~8054 tok)
- `py.typed` (~0 tok)
- `requests.py` (~41 tok)
- `responses.py` — UJSONResponse: render, render (~504 tok)
- `routing.py` — async: merged_lifespan, serialize_response, run_endpoint_function, get_request_handler + 1 more (~50346 tok)
- `staticfiles.py` (~20 tok)
- `templating.py` (~22 tok)
- `testclient.py` (~19 tok)
- `types.py` — Declares import (~110 tok)
- `utils.py` — URL configuration (~2271 tok)
- `websockets.py` (~64 tok)

## venv/lib/python3.13/site-packages/fastapi/dependencies/

- `__init__.py` (~0 tok)
- `models.py` — Declares class (~431 tok)
- `utils.py` — from: ensure_multipart_is_installed, get_param_sub_dependant, get_parameterless_sub_dependant, get_sub_dependant + 8 more (~10166 tok)

## venv/lib/python3.13/site-packages/fastapi/middleware/

- `__init__.py` (~17 tok)
- `cors.py` (~23 tok)
- `gzip.py` (~23 tok)
- `httpsredirect.py` (~33 tok)
- `trustedhost.py` (~32 tok)
- `wsgi.py` (~23 tok)

## venv/lib/python3.13/site-packages/fastapi/openapi/

- `__init__.py` (~0 tok)
- `constants.py` (~44 tok)
- `docs.py` — get_swagger_ui_html, get_redoc_html, get_swagger_ui_oauth2_redirect_html (~2957 tok)
- `models.py` — Pydantic: BaseModelWithConfig (158 fields) (~4400 tok)
- `utils.py` — URL configuration (~6622 tok)

## venv/lib/python3.13/site-packages/fastapi/security/

- `__init__.py` (~252 tok)
- `api_key.py` — API: GET (3 endpoints) (~2677 tok)
- `base.py` — Declares SecurityBase (~41 tok)
- `http.py` — API: GET (3 endpoints) (~3861 tok)
- `oauth2.py` — TODO: import from typing when deprecating Python 3.9 (~6168 tok)
- `open_id_connect_url.py` — Declares OpenIdConnect (~778 tok)
- `utils.py` — get_authorization_scheme_param (~84 tok)

## venv/lib/python3.13/site-packages/h11-0.14.0.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE.txt` (~281 tok)
- `METADATA` (~2180 tok)
- `RECORD` (~909 tok)
- `top_level.txt` (~1 tok)
- `WHEEL` (~25 tok)

## venv/lib/python3.13/site-packages/h11/

- `__init__.py` — A highish-level implementation of the HTTP/1.1 wire protocol (RFC 7230), (~431 tok)
- `_abnf.py` — We use native strings for all the re patterns, to take advantage of string (~1376 tok)
- `_connection.py` — This contains the main Connection class. Everything in h11 revolves around (~7583 tok)
- `_events.py` — High level events that make up HTTP/1.1 conversations. Loosely inspired by (~3376 tok)
- `_headers.py` — Headers: raw_items, normalize_and_validate, normalize_and_validate, normalize_and_validate + 4 more (~2923 tok)
- `_readers.py` — Code to read HTTP data (~2396 tok)
- `_receivebuffer.py` — ReceiveBuffer: maybe_extract_at_most, maybe_extract_next_line, maybe_extract_lines, is_next_line_obviously_invalid_request_line (~1501 tok)
- `_state.py` — ############################################################### (~3800 tok)
- `_util.py` — ProtocolError: validate, bytesify (~1397 tok)
- `_version.py` — This file must be kept very simple, because it is consumed from several (~196 tok)
- `_writers.py` — Code to read HTTP data (~1452 tok)
- `py.typed` (~2 tok)

## venv/lib/python3.13/site-packages/h11/tests/

- `__init__.py` (~0 tok)
- `helpers.py` — ConnectionPair: get_all_events, receive_and_get, normalize_data_events, conns + 1 more (~959 tok)
- `test_against_stdlib_http.py` — URL configuration (~1142 tok)
- `test_connection.py` — Tests: _keep_alive, _body_framing, Connection_basics_and_content_length, chunked + 5 more (~11063 tok)
- `test_events.py` — Tests: events, intenum_status_code, header_casing (~1331 tok)
- `test_headers.py` — Tests: normalize_and_validate, get_set_comma_header, has_100_continue (~1604 tok)
- `test_helpers.py` — Tests: normalize_data_events (~227 tok)
- `test_io.py` — Tests: writers_simple, readers_simple, writers_unusual, readers_unusual + 4 more (~4682 tok)
- `test_receivebuffer.py` — Tests: receivebuffer, receivebuffer_for_invalid_delimiter (~987 tok)
- `test_state.py` — Tests: ConnectionState, ConnectionState_keep_alive, ConnectionState_keep_alive_in_DONE, ConnectionState_switch_denied + 6 more (~2551 tok)
- `test_util.py` — Tests: ProtocolError, LocalProtocolError, validate, validate_formatting + 2 more (~849 tok)

## venv/lib/python3.13/site-packages/h11/tests/data/

- `test-file` (~18 tok)

## venv/lib/python3.13/site-packages/idna-3.10.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE.md` (~386 tok)
- `METADATA` — Declares issue (~2675 tok)
- `RECORD` (~370 tok)
- `WHEEL` (~22 tok)

## venv/lib/python3.13/site-packages/idna/

- `__init__.py` (~248 tok)
- `codec.py` — Codec: encode, decode, search_function (~978 tok)
- `compat.py` — ToASCII, ToUnicode, nameprep (~91 tok)
- `core.py` — IDNAError: valid_label_length, valid_string_length, check_bidi, check_initial_combiner + 9 more (~3783 tok)
- `idnadata.py` — This file is automatically generated by tools/idna-data (~22374 tok)
- `intranges.py` — intranges_from_list, intranges_contain (~543 tok)
- `package_data.py` (~6 tok)
- `py.typed` (~0 tok)
- `uts46data.py` — This file is automatically generated by tools/idna-data (~65835 tok)

## venv/lib/python3.13/site-packages/importlib_resources-6.4.5.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE` — Project license (~3029 tok)
- `METADATA` — Declares Requires (~1060 tok)
- `RECORD` (~1448 tok)
- `top_level.txt` (~5 tok)
- `WHEEL` (~25 tok)

## venv/lib/python3.13/site-packages/importlib_resources/

- `__init__.py` (~201 tok)
- `_adapters.py` — URL configuration (~1281 tok)
- `_common.py` — URL configuration (~1607 tok)
- `_functional.py` — Simplified function-based API for importlib.resources (~758 tok)
- `_itertools.py` — from more_itertools 9.0 (~365 tok)
- `abc.py` — URL configuration (~1475 tok)
- `py.typed` (~0 tok)
- `readers.py` — URL configuration (~1786 tok)
- `simple.py` — URL configuration (~740 tok)

## venv/lib/python3.13/site-packages/importlib_resources/compat/

- `__init__.py` (~0 tok)
- `py38.py` (~66 tok)
- `py39.py` (~44 tok)

## venv/lib/python3.13/site-packages/importlib_resources/future/

- `__init__.py` (~0 tok)
- `adapters.py` — TraversableResourcesLoader: wrapper, get_resource_reader, wrap_spec (~840 tok)

## venv/lib/python3.13/site-packages/importlib_resources/tests/

- `__init__.py` (~0 tok)
- `_path.py` — from jaraco.path 3.7.1 (~654 tok)
- `test_compatibilty_files.py` — URL configuration (~947 tok)
- `test_contents.py` — Tests: contents (~240 tok)
- `test_custom.py` — Tests: custom_loader (~349 tok)
- `test_files.py` — URL patterns: 5 routes (~1656 tok)
- `test_functional.py` — Since the functional API forwards to Traversable, we only test (~2533 tok)
- `test_open.py` — URL configuration (~766 tok)
- `test_path.py` — URL configuration (~568 tok)
- `test_read.py` — URL patterns: 7 routes (~870 tok)
- `test_reader.py` — URL patterns: 8 routes (~1330 tok)
- `test_resource.py` — URL patterns: 13 routes (~2196 tok)
- `util.py` — URL configuration (~1733 tok)
- `zip.py` — make_zip_file, walk (~165 tok)

## venv/lib/python3.13/site-packages/importlib_resources/tests/compat/

- `__init__.py` (~0 tok)
- `py312.py` — isolated_modules (~104 tok)
- `py39.py` (~126 tok)

## venv/lib/python3.13/site-packages/jwt/

- `__init__.py` (~477 tok)
- `algorithms.py` — Algorithm: get_default_algorithms, compute_hash_digest, prepare_key, sign + 21 more (~8529 tok)
- `api_jwk.py` — PyJWK: from_dict, from_json, key_type, key_id + 5 more (~1272 tok)
- `api_jws.py` — PyJWS: register_algorithm, unregister_algorithm, get_algorithms, get_algorithm_by_name + 4 more (~3265 tok)
- `api_jwt.py` — PyJWT: encode, decode_complete, decode (~3679 tok)
- `exceptions.py` — Declares PyJWTError (~315 tok)
- `help.py` — info, main (~500 tok)
- `jwk_set_cache.py` — View: put, get (~274 tok)
- `jwks_client.py` — PyJWKClient: fetch_data, get_jwk_set, get_signing_keys, get_signing_key + 2 more (~1207 tok)
- `py.typed` (~0 tok)
- `types.py` (~29 tok)
- `utils.py` — force_bytes, base64url_decode, base64url_encode, to_base64url_uint + 8 more (~1013 tok)
- `warnings.py` — Declares RemovedInPyjwt3Warning (~17 tok)

## venv/lib/python3.13/site-packages/limits-3.13.0.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE.txt` (~266 tok)
- `METADATA` (~1912 tok)
- `RECORD` (~1228 tok)
- `top_level.txt` (~2 tok)
- `WHEEL` (~25 tok)

## venv/lib/python3.13/site-packages/limits/

- `__init__.py` (~208 tok)
- `_version.py` — This file was generated by 'versioneer.py' (0.22) from (~143 tok)
- `errors.py` — Declares ConfigurationError (~179 tok)
- `limits.py` — Granularity: safe_string, check_granularity_string, get_expiry, key_for (~1413 tok)
- `py.typed` (~0 tok)
- `strategies.py` — RateLimiter: hit, test, get_window_stats, clear + 7 more (~1986 tok)
- `typing.py` — View: get, delete, get, delete (~940 tok)
- `util.py` — URL configuration (~1641 tok)
- `version.py` (~14 tok)

## venv/lib/python3.13/site-packages/limits/aio/

- `__init__.py` (~24 tok)
- `strategies.py` — RateLimiter: hit, test, get_window_stats, clear + 7 more (~1934 tok)

## venv/lib/python3.13/site-packages/limits/aio/storage/

- `__init__.py` (~170 tok)
- `base.py` — View: get (~1377 tok)
- `etcd.py` — View: get (~1369 tok)
- `memcached.py` — View: get (~1372 tok)
- `memory.py` — View: get (~1674 tok)
- `mongodb.py` — View: get (~2684 tok)
- `redis.py` — View: get (~4472 tok)

## venv/lib/python3.13/site-packages/limits/resources/redis/lua_scripts/

- `acquire_moving_window.lua` (~129 tok)
- `clear_keys.lua` (~50 tok)
- `incr_expire.lua` (~52 tok)
- `moving_window.lua` (~107 tok)

## venv/lib/python3.13/site-packages/limits/storage/

- `__init__.py` — based: storage_from_string (~733 tok)
- `base.py` — View: get (~1322 tok)
- `etcd.py` — View: get (~1282 tok)
- `memcached.py` — View: get (~1898 tok)
- `memory.py` — View: get (~1589 tok)
- `mongodb.py` — View: get (~2633 tok)
- `redis_cluster.py` — RedisClusterStorage: reset (~1538 tok)
- `redis_sentinel.py` — View: get (~1108 tok)
- `redis.py` — View: get (~2415 tok)
- `registry.py` — Declares StorageRegistry (~203 tok)

## venv/lib/python3.13/site-packages/packaging-24.2.dist-info/

- `INSTALLER` (~2 tok)
- `LICENSE` — Project license (~53 tok)

## venv/lib/python3.13/site-packages/packaging/

- `__init__.py` — This file is dual licensed under the terms of the Apache License, Version (~142 tok)
- `_elffile.py` — ELFInvalid: interpreter (~945 tok)
- `_manylinux.py` — _GLibCVersion: platform_tags (~2747 tok)
- `_musllinux.py` — PEP 656 support. (~770 tok)
- `_parser.py` — Handwritten parser of dependency specifiers. (~2925 tok)
- `_structures.py` — This file is dual licensed under the terms of the Apache License, Version (~409 tok)
- `_tokenizer.py` — from: consume, check, expect, read + 2 more (~1507 tok)
- `markers.py` — This file is dual licensed under the terms of the Apache License, Version (~3017 tok)
- `metadata.py` — ExceptionGroup: parse_email (~9932 tok)
- `py.typed` (~0 tok)
- `requirements.py` — This file is dual licensed under the terms of the Apache License, Version (~842 tok)
- `specifiers.py` — This file is dual licensed under the terms of the Apache License, Version (~11450 tok)
- `tags.py` — This file is dual licensed under the terms of the Apache License, Version (~6004 tok)
- `utils.py` — This file is dual licensed under the terms of the Apache License, Version (~1443 tok)
- `version.py` — This file is dual licensed under the terms of the Apache License, Version (~4765 tok)

## venv/lib/python3.13/site-packages/packaging/licenses/

- `__init__.py` — ###################################################################################### (~1633 tok)
- `_spdx.py` — Declares SPDXLicense (~13828 tok)
