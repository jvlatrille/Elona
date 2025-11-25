"""Utilities for showing typing indicators before sending messages."""

import discord
from typing import Awaitable, Callable, Optional


async def send_with_typing(
    channel: Optional[discord.abc.Messageable],
    send_action: Callable[[], Awaitable],
):
    """
    Show a typing indicator in the given channel before executing ``send_action``.

    The typing indicator is attempted on a best-effort basis: if it fails for any
    reason, the send action is still executed.
    """

    typing = getattr(channel, "typing", None)

    if callable(typing):
        try:
            async with typing():
                return await send_action()
        except Exception:
            # If typing fails, fall back to sending without it.
            pass

    return await send_action()
