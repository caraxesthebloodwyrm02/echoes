# PHASE 2 PROTOTYPE: Responses API Migration Implementation

## Overview

Phase 2 focuses on implementing working prototypes for each API call pattern, allowing side-by-side testing with the existing Chat Completions API. All changes will be feature-flag controlled for safe rollback.

## Migration Strategy

### Feature Flag Architecture
```python
# Add to EchoesAssistantV2.__init__
self.use_responses_api = os.getenv("USE_RESPONSES_API", "false").lower() in ("1", "true", "yes")
```

### Prototype Implementation Order
1. **Tool Calling Loop** (Highest Impact) - Lines 788-834
2. **Streaming Pipeline** (User Experience) - Line 891
3. **Value Guard Integration** (Quality) - Line 613
4. **Final Response Generation** (Core) - Line 914
5. **Directory Analysis** (Specialized) - Line 1402

## 1. Tool Calling Loop Migration

### Current Implementation (Lines 788-834)
```python
response = self.client.chat.completions.create(
    model=selected_model,
    messages=messages,
    tools=tools if tool_calling_enabled else None,
    tool_choice="auto" if (tools and tool_calling_enabled) else None,
    temperature=self.temperature,
    max_completion_tokens=self.max_tokens if 'o3' in selected_model else None,
    max_tokens=self.max_tokens if 'o3' not in selected_model else None,
    stream=False,
)

response_message = response.choices[0].message
tool_calls = getattr(response_message, "tool_calls", None)
```

### Responses API Implementation
```python
if self.use_responses_api:
    # NEW: Responses API implementation
    response = self.client.responses.create(
        model=selected_model,
        input=messages,  # messages array becomes input
        tools=tools if tool_calling_enabled else None,
        tool_choice="auto" if (tools and tool_calling_enabled) else None,
        temperature=self.temperature,
        max_output_tokens=self.max_tokens,  # renamed parameter
        stream=False,
    )

    # NEW: Response structure changes
    tool_calls = []
    for output_item in response.output:
        if output_item.type == "tool_call":
            tool_calls.append(output_item.content)
else:
    # EXISTING: Chat Completions implementation
    response = self.client.chat.completions.create(...)
    response_message = response.choices[0].message
    tool_calls = getattr(response_message, "tool_calls", None)
```

## 2. Streaming Pipeline Migration

### Current Implementation (Lines 891-906)
```python
response_stream = self.client.chat.completions.create(
    model=selected_model,
    messages=messages,
    temperature=self.temperature,
    stream=True,
)

for chunk in response_stream:
    delta = chunk.choices[0].delta
    if hasattr(delta, "content") and delta.content:
        chunk_content = delta.content
        print(chunk_content, end="", flush=True)
        full_response += chunk_content
```

### Responses API Implementation
```python
if self.use_responses_api:
    # NEW: Event-based streaming
    with self.client.responses.stream(
        model=selected_model,
        input=messages,
        temperature=self.temperature,
    ) as stream:
        for event in stream:
            if event.type == "text.delta":
                chunk_content = event.delta
                print(chunk_content, end="", flush=True)
                full_response += chunk_content
else:
    # EXISTING: Chunk-based streaming
    response_stream = self.client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=self.temperature,
        stream=True,
    )
    # ... existing chunk processing
```

## 3. Value Guard Integration Migration

### Current Implementation (Line 613)
```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=len(original) + 100
)

improved = response.choices[0].message.content.strip()
```

### Responses API Implementation
```python
if self.use_responses_api:
    response = self.client.responses.create(
        model=self.model,
        input=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_output_tokens=len(original) + 100
    )

    # NEW: Aggregate text content from output array
    improved = ""
    for output_item in response.output:
        if output_item.type == "text":
            improved += output_item.content
    improved = improved.strip()
else:
    # EXISTING implementation
    response = self.client.chat.completions.create(...)
    improved = response.choices[0].message.content.strip()
```

## 4. Final Response Generation Migration

### Current Implementation (Line 914)
```python
final_response = self.client.chat.completions.create(
    model=selected_model,
    messages=messages,
    temperature=self.temperature
)
assistant_response = final_response.choices[0].message.content
```

### Responses API Implementation
```python
if self.use_responses_api:
    final_response = self.client.responses.create(
        model=selected_model,
        input=messages,
        temperature=self.temperature
    )

    # NEW: Aggregate response content
    assistant_response = ""
    for output_item in final_response.output:
        if output_item.type == "text":
            assistant_response += output_item.content
else:
    # EXISTING implementation
    final_response = self.client.chat.completions.create(...)
    assistant_response = final_response.choices[0].message.content
```

## 5. Directory Analysis Migration

### Current Implementation (Line 1402)
```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": analysis_prompt},
    ],
    temperature=0.3,
    max_completion_tokens=3000 if 'o3' in self.model else None,
    max_tokens=3000 if 'o3' not in self.model else None,
)
analysis["analysis"] = response.choices[0].message.content
```

### Responses API Implementation
```python
if self.use_responses_api:
    response = self.client.responses.create(
        model=self.model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_prompt},
        ],
        temperature=0.3,
        max_output_tokens=3000
    )

    # NEW: Aggregate analysis content
    analysis_text = ""
    for output_item in response.output:
        if output_item.type == "text":
            analysis_text += output_item.content
    analysis["analysis"] = analysis_text
else:
    # EXISTING implementation
    response = self.client.chat.completions.create(...)
    analysis["analysis"] = response.choices[0].message.content
```

## Implementation Checklist

### Tool Calling Loop
- [ ] Feature flag conditional logic
- [ ] Parameter mapping (messages → input, max_tokens → max_output_tokens)
- [ ] Response parsing (choices[0].message → response.output array)
- [ ] Tool call extraction (tool_calls attribute → content items)
- [ ] Fallback handling compatibility

### Streaming Pipeline
- [ ] Event-based streaming implementation
- [ ] Text delta event handling
- [ ] Response aggregation logic
- [ ] Error handling for streaming failures

### Value Guard Integration
- [ ] Text content aggregation from output array
- [ ] Response length handling
- [ ] Improvement scoring compatibility

### Final Response Generation
- [ ] Text content aggregation
- [ ] Response structure compatibility
- [ ] Error handling preservation

### Directory Analysis
- [ ] Analysis text aggregation
- [ ] Token limit handling
- [ ] Model-specific parameter handling

## Testing Strategy

### Glimpse Tests
- Test each API call pattern individually
- Verify response parsing accuracy
- Confirm tool call handling
- Validate streaming behavior

### Integration Tests
- End-to-end chat workflows
- Tool calling sequences
- Streaming response delivery
- Value guard improvements

### Performance Tests
- Response time comparisons
- Memory usage monitoring
- Error rate tracking

## Rollback Procedures

1. **Immediate Rollback**: Set `USE_RESPONSES_API=false`
2. **Gradual Rollback**: Reduce traffic to Responses API calls
3. **Clean Rollback**: Remove feature flag conditionals (post-migration)

## Success Criteria

- [ ] All 6 API call patterns migrated
- [ ] Feature flag controls working
- [ ] Performance meets baseline targets
- [ ] Behavioral compatibility maintained
- [ ] Error handling preserved
- [ ] Rollback capability verified

*Phase 2 Prototype Implementation Plan*
*Status: Ready for implementation*
