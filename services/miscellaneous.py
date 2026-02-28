from datetime import datetime, timezone, timedelta


def current_time_utc_offset(offset_hours: int) -> int:
    tz = timezone(timedelta(hours=offset_hours))
    now = datetime.now(tz)
    return f'{now.hour}:{now.minute}'


def format_repair_text_minimal(d: dict) -> str:
    return f"""
Новая заявка на ремонт Samsonite

👤 Клиент: {d['name']}
📞 Телефон: {d['phone']}
🏙 Город: {d['city']}

🧳 Изделие: {d['model']}

🔧 Проблема: {d['problem']}
"""