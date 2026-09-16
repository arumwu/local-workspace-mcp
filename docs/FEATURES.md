# Feature coverage

Full mode reuses the actual open-source Desktop Commander engine, rather than implementing a reduced
file-only imitation. Every `host_` tool retains the original input schema. Names are prefixed to distinguish
full OS access from document-mode tools. Coverage is not the same as complete upstream test coverage.

| Requested category | Tools / implementation | Verification |
|---|---|---|
| Read and explore | host_read_file, host_read_multiple_files, host_list_directory, host_get_file_info | Actual local stdio calls; PDF read included |
| Search | host_start_search, host_get_more_search_results, host_stop_search, host_list_searches | Search, page retrieval, list and stop exercised |
| Write and edit | host_write_file, host_edit_block, host_move_file, host_create_directory, host_write_pdf | Write/edit/move/create plus PDF creation/page insertion exercised |
| Terminal and processes | host_start_process, host_interact_with_process, host_read_process_output, host_list_sessions, host_list_processes, host_force_terminate, host_kill_process | Interactive input/output and termination of test-owned processes |
| Devices and account | list_paired_devices, current_user_info, ping_device, shutdown_device_agent; list_device_tools, call_device_tool | Two independent stdio agents tested; physical SSH machines pending. Identity is local OS identity, not a vendor account |
| Configuration and help | host_get_config, host_set_config_value, get_prompt_library, host_get_prompts, host_get_recent_tool_calls, host_get_usage_stats, submit_feedback | Read/write settings, bundled prompts, redacted history, usage and local feedback tested |
| Office and data work | run_python, list_artifacts, get_artifact_path; HTTP get_download_link | DOCX/XLSX/PPTX/PDF/PNG creation and reopening, Chinese DOCX rendering, spreadsheet recalculation |

Build apps, manage development servers and explore repositories through full-mode file/process tools.
Edit Office files by reading through Python/Office libraries, writing a verified edited copy, then using
host tools to replace the original path if requested. Isolated mode cannot replace input originals.
Context/documentation is ordinary files, not proprietary hosted memory.

Intentional differences: no proprietary remote relay, cloud account/subscription, vendor feedback sending,
automatic browser download, or document-content logs. Feedback is saved locally. Pairing is owner-configured
SSH/stdio rather than a vendor login portal. No browser/desktop clicking or extra AI credits.

Limits: full upstream feature behavior is inherited and not exhaustively tested. macOS is tested locally;
Linux CI is configured; native Windows is unsupported. Native ChatGPT client acceptance and physical
multi-Mac SSH checks remain outstanding. The primary target is ordinary ChatGPT conversations. This remains alpha; see the dated validation record.
