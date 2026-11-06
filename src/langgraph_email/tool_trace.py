from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def tool_trace(messages):
    start = max(
        (
            i for i, msg in enumerate(messages)
            if isinstance(msg, HumanMessage)
        ),
        default=-1,
    )

    current_turn = messages[start + 1:]

    print("\n=== Tool Execution Trace ===")

    tool_names = {}
    count = 0

    for msg in current_turn:
        if isinstance(msg, AIMessage):
            for call in msg.tool_calls:
                count += 1
                name = call["name"]

                tool_names[call["id"]] = name

                print(f"{count}. CALL: {name}")

        elif isinstance(msg, ToolMessage):
            name = tool_names.get(
                msg.tool_call_id,
                msg.name or "unknown",
            )

            print(
                f"   RESULT: {name} "
                f"({getattr(msg, 'status', 'unknown')})"
            )

    if count == 0:
        print("No tools called.")

    print("============================\n")