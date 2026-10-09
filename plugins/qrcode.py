import io
import os
import aiohttp
import qrcode
from PIL import Image
from core.decorators import omni_cmd


@omni_cmd(
    pattern="makeqr",
    desc="Generates a high-quality QR code image from text or replied message.",
    usage=".makeqr <text> or reply to message",
    category="Tools"
)
async def make_qr(event):
    text = event.text_args.strip()
    if not text and event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        text = reply_msg.raw_text or ""
    
    if not text:
        await event.reply_or_edit("⚠️ Please provide text or reply to a message: `.makeqr <text>`")
        return

    status = await event.reply_or_edit("⏳ Generating QR code...")
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        bio = io.BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, format="PNG")
        bio.seek(0)

        await event.client.send_file(
            event.chat_id,
            bio,
            caption=f"**QR Code Generated**\n`{text[:200]}`" if len(text) > 200 else f"**QR Code Generated**\n`{text}`",
            reply_to=event.reply_to_msg_id or event.id
        )
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Failed to generate QR code: `{e}`")


@omni_cmd(
    pattern="getqr",
    desc="Reads and decodes QR code from a replied image.",
    usage=".getqr (reply to QR image)",
    category="Tools"
)
async def read_qr(event):
    if not event.reply_to_msg_id:
        await event.reply_or_edit("⚠️ Reply to an image or document containing a QR code.")
        return

    reply = await event.get_reply_message()
    if not reply.media:
        await event.reply_or_edit("⚠️ The replied message does not contain media.")
        return

    status = await event.reply_or_edit("⏳ Scanning QR code...")
    temp_path = None
    try:
        temp_path = await event.client.download_media(reply, file="downloads/")
        if not temp_path or not os.path.exists(temp_path):
            await status.edit("❌ Failed to download replied media.")
            return

        # Use public decoding API
        url = "https://api.qrserver.com/v1/read-qr-code/"
        async with aiohttp.ClientSession() as session:
            with open(temp_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("file", f, filename="qr.png")
                async with session.post(url, data=data) as resp:
                    if resp.status == 200:
                        res = await resp.json()
                        parsed = res[0]["symbol"][0]["data"] if res and "symbol" in res[0] else None
                        if parsed:
                            await status.edit(f"🔍 **Decoded QR Code:**\n\n`{parsed}`")
                        else:
                            await status.edit("⚠️ No readable QR code detected in this image.")
                    else:
                        await status.edit("❌ Decoder service returned an error.")
    except Exception as e:
        await status.edit(f"❌ Error scanning QR code: `{e}`")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@omni_cmd(
    pattern="barcode",
    desc="Generates a barcode image from input text or numbers.",
    usage=".barcode <text>",
    category="Tools"
)
async def make_barcode(event):
    text = event.text_args.strip()
    if not text:
        await event.reply_or_edit("⚠️ Usage: `.barcode <text/numbers>`")
        return

    status = await event.reply_or_edit("⏳ Generating barcode...")
    try:
        api_url = f"https://barcodeapi.org/api/auto/{text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    bio = io.BytesIO(content)
                    bio.name = "barcode.png"
                    await event.client.send_file(
                        event.chat_id,
                        bio,
                        caption=f"**Barcode Generated**\n`{text}`",
                        reply_to=event.reply_to_msg_id or event.id
                    )
                    await status.delete()
                else:
                    await status.edit("❌ Failed to generate barcode.")
    except Exception as e:
        await status.edit(f"❌ Error generating barcode: `{e}`")
