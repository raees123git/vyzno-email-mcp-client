from langgraph.types import Command

SUPPORTED_ACTIONS = {
    "send_email",
    "delete_draft",
    "trash_email",
    "trash_thread",
    "permanently_delete_thread",
}


def approve_actions(actions):
    return [{"type": "approve"} for _ in actions]


def reject_actions(actions):
    return [
        {
            "type": "reject",
            "message": "Action not approved. Do not retry automatically.",
        }
        for _ in actions
    ]


async def load_preview(action, mcp_client):
    name = action["name"]
    args = action.get("args", {})

    if name in {"send_email", "delete_draft"}:
        draft_id = args.get("draft_id")

        if not isinstance(draft_id, str):
            raise ValueError("Invalid draft ID.")

        response = await mcp_client.call_tool(
            "get_draft",
            {"draft_id": draft_id},
        )

        if response.is_error or not isinstance(response.data, dict):
            raise ValueError("Unable to retrieve draft preview.")

        preview = response.data

        if preview.get("id") != draft_id:
            raise ValueError("Draft ID mismatch.")

        return {
            "type": "message",
            "data": preview,
        }

    if name == "trash_email":
        message_id = args.get("message_id")
        thread_id = args.get("thread_id")

        if not isinstance(message_id, str) or not isinstance(thread_id, str):
            raise ValueError("Invalid message or thread ID.")

        response = await mcp_client.call_tool(
            "get_thread",
            {"thread_id": thread_id},
        )

        if response.is_error or not isinstance(response.data, dict):
            raise ValueError("Unable to retrieve email preview.")

        messages = response.data.get("messages", [])

        if not isinstance(messages, list):
            raise ValueError("Invalid thread response.")

        preview = next(
            (
                message
                for message in messages
                if isinstance(message, dict)
                and message.get("id") == message_id
            ),
            None,
        )

        if preview is None:
            raise ValueError("Message was not found in the specified thread.")

        return {
            "type": "message",
            "data": preview,
        }

    if name in {"trash_thread", "permanently_delete_thread"}:
        thread_id = args.get("thread_id")

        if not isinstance(thread_id, str):
            raise ValueError("Invalid thread ID.")

        response = await mcp_client.call_tool(
            "get_thread",
            {"thread_id": thread_id},
        )

        if response.is_error or not isinstance(response.data, dict):
            raise ValueError("Unable to retrieve thread preview.")

        messages = response.data.get("messages", [])

        if not isinstance(messages, list) or not messages:
            raise ValueError("The thread contains no messages.")

        if name == "permanently_delete_thread" and any(
            not isinstance(message, dict)
            or message.get("trashed") is not True
            for message in messages
        ):
            raise ValueError(
                "The entire thread must be in Trash before permanent deletion."
            )

        return {
            "type": "thread",
            "data": response.data,
        }

    raise ValueError(f"Unsupported action: {name}")


def get_recipients(message):
    return [
        recipient["address"]
        for recipient in message.get("recipients", [])
        if isinstance(recipient, dict)
        and isinstance(recipient.get("address"), str)
    ]


def display_message_preview(action_name, message):
    recipients = get_recipients(message)

    print(f"\nAction: {action_name}")
    print(f"To: {', '.join(recipients) or 'Not specified'}")
    print(f"Subject: {message.get('subject') or '(none)'}")
    print("\nBody:")
    print(message.get("bodyText") or message.get("bodyHtml") or "(empty)")


def display_thread_preview(thread, action_name):
    print(f"\nAction: {action_name}")
    print(f"Subject: {thread.get('subject') or '(none)'}")

    for index, message in enumerate(thread["messages"], start=1):
        print(f"\n--- Message {index} ---")
        display_message_preview("Message", message)


def display_previews(previews):
    print("\n=== Human Approval Required ===")

    for preview in previews:
        if preview["type"] == "message":
            display_message_preview(
                preview["action"],
                preview["data"],
            )
        else:
            display_thread_preview(
                preview["data"],
                preview["action"],
            )


async def handle_approval(agent, result, config, mcp_client):
    while result.interrupts:
        actions = result.interrupts[0].value["action_requests"]

        try:
            if not actions:
                raise ValueError("No actions to approve.")

            for action in actions:
                action_name = action.get("name")

                if action_name not in SUPPORTED_ACTIONS:
                    raise ValueError(
                        f"Unsupported action: {action_name}"
                    )

            async with mcp_client:
                previews = []

                for action in actions:
                    preview = await load_preview(action, mcp_client)
                    preview["action"] = action["name"]
                    previews.append(preview)

            display_previews(previews)

            answer = input(
                "\nApprove all actions? (yes/no): "
            ).strip().lower()

            decisions = (
                approve_actions(actions)
                if answer == "yes"
                else reject_actions(actions)
            )

        except (EOFError, KeyboardInterrupt):
            print("\nApproval cancelled.")
            decisions = reject_actions(actions)

        except Exception as exc:
            print(f"\nApproval blocked: {exc}")
            decisions = reject_actions(actions)

        result = await agent.ainvoke(
            Command(resume={"decisions": decisions}),
            config=config,
            version="v2",
        )

    return result
