import sys
import io
import asyncio
import traceback
from core.decorators import omni_cmd


@omni_cmd(
    pattern="eval",
    desc="Evaluates live Python code asynchronously in userbot runtime.",
    usage=".eval <python code>",
    category="Developer"
)
async def eval_python(event):
    cmd = event.text_args.strip()
    if not cmd:
        await event.reply_or_edit("🐍 **Usage:** `.eval <python code>`")
        return

    msg = await event.reply_or_edit("⚙️ **Evaluating Python code...**")

    # Capture stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    # Prepare async wrapper
    code_lines = "\n".join(f"    {line}" for line in cmd.splitlines())
    body = f"async def __ex(event, client):\n{code_lines}"

    try:
        exec(body)
        res = await locals()["__ex"](event, event.client)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = f"**Exception:**\n`{exc}`"
    elif stderr:
        evaluation = f"**Stderr:**\n`{stderr}`"
    elif stdout:
        evaluation = f"**Stdout:**\n`{stdout}`"
    else:
        evaluation = f"**Result:**\n`{res}`"

    out = (
        f"🐍 **Python Evaluation:**\n\n"
        f"**Input:**\n```python\n{cmd}\n```\n\n"
        f"**Output:**\n{evaluation}"
    )

    if len(out) > 4000:
        out = out[:3900] + "\n... *(Output truncated)*"

    await msg.edit(out)


@omni_cmd(
    pattern="sh",
    desc="Executes terminal commands on the host machine asynchronously.",
    usage=".sh <shell command>",
    category="Developer",
    aliases=["exec", "terminal", "bash"]
)
async def exec_terminal(event):
    cmd = event.text_args.strip()
    if not cmd:
        await event.reply_or_edit("💻 **Usage:** `.sh <shell command>`")
        return

    msg = await event.reply_or_edit(f"💻 **Running:** `{cmd}`...")

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    output = stdout.decode("utf-8", errors="replace").strip()
    err = stderr.decode("utf-8", errors="replace").strip()

    result_text = ""
    if output:
        result_text += f"**Output:**\n```bash\n{output}\n```\n"
    if err:
        result_text += f"**Errors:**\n```bash\n{err}\n```\n"
    if not result_text:
        result_text = "*(Command finished with no output)*"

    out = f"💻 **Terminal Execution:**\n`{cmd}`\n\n{result_text}"
    if len(out) > 4000:
        out = out[:3900] + "\n```\n... *(Output truncated)*"

    await msg.edit(out)
