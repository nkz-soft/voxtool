You are evaluating a text request for tool use.

Available tools:
```json
{tools_json}
```

Return JSON only with keys `needs_tool`, `tool_call`, and `final_answer`.
If the request needs a conversion, use exactly one registered tool call.
If no tool is needed, set `needs_tool` to false and `tool_call` to null.

Request:
{input_text}
