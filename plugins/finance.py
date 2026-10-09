import aiohttp
from core.decorators import omni_cmd


@omni_cmd(
    pattern="currency",
    desc="Converts currencies in real-time.",
    usage=".currency <amount> <from> <to> (e.g. .currency 100 USD INR)",
    category="Tools"
)
async def currency_cmd(event):
    args = event.text_args.strip().split()
    if len(args) < 3:
        await event.reply_or_edit("⚠️ Usage: `.currency <amount> <from> <to>`\nExample: `.currency 100 USD EUR`")
        return

    try:
        amount = float(args[0])
    except ValueError:
        await event.reply_or_edit("❌ Invalid amount specified.")
        return

    from_curr = args[1].upper()
    to_curr = args[2].upper()

    status = await event.reply_or_edit("⏳ Fetching live exchange rates...")
    try:
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_curr}&to={to_curr}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    res_amount = data["rates"].get(to_curr)
                    rate_date = data.get("date", "Today")
                    out = (
                        f"💱 **Currency Conversion**\n\n"
                        f"• **Source:** `{amount:,.2f} {from_curr}`\n"
                        f"• **Result:** `{res_amount:,.2f} {to_curr}`\n"
                        f"• **Rate Date:** `{rate_date}`"
                    )
                    await status.edit(out)
                else:
                    await status.edit(f"❌ Could not convert `{from_curr}` to `{to_curr}`.")
    except Exception as e:
        await status.edit(f"❌ Currency error: `{e}`")


@omni_cmd(
    pattern="crypto",
    desc="Fetches real-time cryptocurrency price and 24h market stats.",
    usage=".crypto <symbol> (e.g. .crypto btc)",
    category="Tools"
)
async def crypto_cmd(event):
    symbol = event.text_args.strip().upper() or "BTC"
    pair = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol

    status = await event.reply_or_edit(f"⏳ Fetching price for {symbol}...")
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    last_price = float(data["lastPrice"])
                    price_change = float(data["priceChangePercent"])
                    high = float(data["highPrice"])
                    low = float(data["lowPrice"])
                    volume = float(data["volume"])

                    indicator = "🟢" if price_change >= 0 else "🔴"
                    out = (
                        f"🪙 **{symbol}/USDT Market Data**\n\n"
                        f"• **Price:** `${last_price:,.4f}`\n"
                        f"• **24h Change:** {indicator} `{price_change:+.2f}%`\n"
                        f"• **24h High:** `${high:,.4f}`\n"
                        f"• **24h Low:** `${low:,.4f}`\n"
                        f"• **24h Volume:** `{volume:,.2f} {symbol}`"
                    )
                    await status.edit(out)
                else:
                    # Fallback to coingecko simple lookup
                    cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd&include_24hr_change=true"
                    async with session.get(cg_url, timeout=aiohttp.ClientTimeout(total=5)) as cg_resp:
                        if cg_resp.status == 200:
                            cg_data = await cg_resp.json()
                            s_key = symbol.lower()
                            if s_key in cg_data:
                                p = cg_data[s_key]["usd"]
                                ch = cg_data[s_key].get("usd_24h_change", 0.0)
                                ind = "🟢" if ch >= 0 else "🔴"
                                await status.edit(f"🪙 **{symbol} Price:** `${p:,.4f}` ({ind} `{ch:+.2f}%`)")
                                return
                    await status.edit(f"❌ Symbol `{symbol}` not found.")
    except Exception as e:
        await status.edit(f"❌ Crypto error: `{e}`")
