import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from core.decorators import omni_cmd


def _create_local_code_card(code_text: str, theme: str = "dark") -> io.BytesIO:
    lines = code_text.split("\n")
    max_line_len = max(len(l) for l in lines) if lines else 20
    char_width = 9
    line_height = 24
    padding_x = 35
    header_height = 55
    padding_bottom = 25

    width = max(650, padding_x * 2 + max_line_len * char_width + 50)
    height = header_height + (len(lines) * line_height) + padding_bottom

    bg_color = "#181824" if theme == "rgb" else "#1E1E1E"
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Mac terminal window control dots
    draw.ellipse([20, 20, 32, 32], fill="#FF5F56")
    draw.ellipse([40, 20, 52, 32], fill="#FFBD2E")
    draw.ellipse([60, 20, 72, 32], fill="#27C93F")

    # Draw code lines
    y = header_height
    for i, line in enumerate(lines, 1):
        num_str = f"{i:>2} | "
        draw.text((padding_x, y), num_str, fill="#606070")
        line_color = "#76E4F7" if any(kw in line for kw in ["def ", "import ", "from ", "class ", "return "]) else "#D8DEE9"
        draw.text((padding_x + 40, y), line, fill=line_color)
        y += line_height

    bio = io.BytesIO()
    bio.name = "carbon.png"
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio


@omni_cmd(
    pattern="carbon",
    desc="Generates a beautiful Carbon code snippet image from text or replied message.",
    usage=".carbon <code> or reply to code",
    category="Media",
    aliases=["karb"]
)
async def carbon_cmd(event):
    code_text = event.text_args.strip()
    if not code_text and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        code_text = reply.raw_text or ""

    if not code_text:
        await event.reply_or_edit("⚠️ Usage: `.carbon <code>` or reply to a code message.")
        return

    status = await event.reply_or_edit("🎨 Generating code card...")
    try:
        bio = None
        # Try Carbonara API with short timeout
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"code": code_text}
                async with session.post("https://carbonara.solopov.dev/api/cook", json=payload, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        bio = io.BytesIO(content)
                        bio.name = "carbon.png"
        except Exception:
            bio = None

        if not bio:
            is_rgb = "karb" in event.raw_text
            bio = _create_local_code_card(code_text, theme="rgb" if is_rgb else "dark")

        await event.client.send_file(
            event.chat_id,
            bio,
            caption="**Code Card Generated**",
            reply_to=event.reply_to_msg_id or event.id
        )
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Failed to generate carbon card: `{e}`")
