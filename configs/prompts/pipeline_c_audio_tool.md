You are evaluating an audio request for tool use.

Available tools:
```json
{tools_json}
```

Return JSON only with keys `needs_tool`, `tool_call`, `final_answer`, and `transcript`.
If the audio asks for a conversion, use exactly one registered tool call.
If no tool is needed, set `needs_tool` to false and `tool_call` to null.
