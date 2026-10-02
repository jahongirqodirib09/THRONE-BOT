from __future__ import annotations


ROLES = [
    # 👑 KRON — 12
    ("shoh", "👑 Shoh", "KRON", "Qirollikning markaziy figurasi."),
    ("malika", "👸 Malika", "KRON", "Tunda bir o‘yinchini himoya qiladi."),
    ("shahzoda", "🤴 Shahzoda", "KRON", "Shoh halok bo‘lsa, maxsus himoyaga ega bo‘ladi."),
    ("vazir", "🏛️ Vazir", "KRON", "Tanlangan o‘yinchining jamoasini aniqlaydi."),
    ("bosh_qomondon", "⚔️ Bosh qo‘mondon", "KRON", "Tunda bir dushmanga hujum qiladi."),
    ("qirol_qoriqchisi", "🛡️ Qirol qo‘riqchisi", "KRON", "Muhim o‘yinchini maxsus himoya qiladi."),
    ("qozi", "⚖️ Qozi", "KRON", "Ovoz berish jarayoniga ta’sir qiluvchi maxsus rol."),
    ("xazinachi", "💰 Xazinachi", "KRON", "Qirollik iqtisodini himoya qiladi."),
    ("ritsar", "🏰 Ritsir", "KRON", "Bir marta kuchli shaxsiy himoyadan foydalanadi."),
    ("xizmatkor", "🧹 Xizmatkor", "KRON", "Tanlangan o‘yinchining tungi harakati haqida ma’lumot oladi."),
    ("tinch_aholi", "🏘️ Tinch aholi", "KRON", "Qirollikning oddiy fuqarosi."),
    ("aygoqchi", "🕵️ Ayg‘oqchi", "KRON", "Tanlangan o‘yinchining jamoasini tekshiradi."),

    # 🦅 SOYA — 10
    ("soya_boshligi", "🦅 Soya boshlig‘i", "SOYA", "Soya guruhining rahbari."),
    ("qotil", "🗡️ Qotil", "SOYA", "Tunda bir o‘yinchiga hujum qiladi."),
    ("josus", "🕵️ Josus", "SOYA", "Tanlangan o‘yinchining kim bilan harakat qilganini aniqlaydi."),
    ("soxta_maslahatchi", "🎭 Soxta maslahatchi", "SOYA", "Tekshiruvlarda o‘zini boshqa jamoaga ko‘rsatishi mumkin."),
    ("xoin", "🩸 Xoin", "SOYA", "Qirollik ichidan yashirincha Soya tomonida ishlaydi."),
    ("qora_vazir", "🖤 Qora vazir", "SOYA", "Soya guruhining strategik maslahatchisi."),
    ("dushman_qiroli", "👑 Dushman qiroli", "SOYA", "Soya tomonining maxsus kuchli hujumchisi."),
    ("dushman_qomondoni", "⚔️ Dushman qo‘mondoni", "SOYA", "Kuchli tungi hujumni amalga oshiradi."),
    ("dushman_josusi", "🕵️ Dushman josusi", "SOYA", "Tanlangan o‘yinchida maxsus rol bor-yo‘qligini aniqlaydi."),
    ("dushman_suiqasdchisi", "🗡️ Dushman suiqasdchisi", "SOYA", "Kuchli suiqasd amalga oshiradi."),

    # 🐺 YAKKA — 7
    ("ovchi", "🐺 Ovchi", "YAKKA", "Tunda tanlagan o‘yinchisiga hujum qiladi."),
    ("telba", "🃏 Telba", "YAKKA", "O‘zining maxsus g‘alaba shartiga ega."),
    ("sayyoh", "👤 Sayyoh", "YAKKA", "Qirollikdan tashqarida o‘z maqsadi bilan harakat qiladi."),
    ("yollanma_jangchi", "⚔️ Yollanma jangchi", "YAKKA", "Pul va shart asosida harakat qiluvchi mustaqil jangchi."),
    ("surgun_shahzoda", "🤴 Surgun shahzoda", "YAKKA", "Maxsus «Qaytish» qobiliyatiga ega."),
    ("taxt_davogari", "👑 Taxt da’vogari", "YAKKA", "Taxt uchun o‘ziga xos g‘alaba shartiga ega."),
    ("qaroqchi", "🥷 Qaroqchi", "YAKKA", "Tunda tanlangan o‘yinchidan oltin o‘g‘irlaydi."),

    # 🛡️ LEGION — 7
    ("tabib", "🩺 Tabib", "LEGION", "Tunda bir o‘yinchini davolaydi."),
    ("kuzatuvchi", "👁️ Kuzatuvchi", "LEGION", "Tanlangan o‘yinchiga kimlar tashrif buyurganini ko‘radi."),
    ("qorovul", "🔒 Qorovul", "LEGION", "Ayrim tungi harakatlarni nishonga yetib borishidan to‘sadi."),
    ("solnomachi", "📜 Solnomachi", "LEGION", "Oldingi tunning muhim voqealari haqida ma’lumot oladi."),
    ("savdogar", "💰 Savdogar", "LEGION", "Iqtisodiy imkoniyatlarga ega."),
    ("suiqasdchi", "🗡️ Suiqasdchi", "LEGION", "Tunda tanlangan o‘yinchiga hujum qiladi."),
    ("oshpaz", "🍳 Oshpaz", "LEGION", "Tunda bir o‘yinchini tanlab, unga ovqat tayyorlaydi."),
]


TEAM_LABELS = {
    "KRON": "KRON",
    "SOYA": "SOYA",
    "YAKKA": "YAKKA",
    "LEGION": "LEGION",
}


ROLE_MAP = {
    role_id: {
        "id": role_id,
        "name": name,
        "team": team,
        "side": TEAM_LABELS[team],
        "description": description,
    }
    for role_id, name, team, description in ROLES
}


ROLE_KEYS = tuple(ROLE_MAP.keys())


TEAM_ROLES = {
    team: tuple(
        role_id
        for role_id, _, role_team, _ in ROLES
        if role_team == team
    )
    for team in TEAM_LABELS
}


assert len(ROLES) == 36
assert len(ROLE_MAP) == 36

assert len(TEAM_ROLES["KRON"]) == 12
assert len(TEAM_ROLES["SOYA"]) == 10
assert len(TEAM_ROLES["YAKKA"]) == 7
assert len(TEAM_ROLES["LEGION"]) == 7


def get_role(role_id: str) -> dict | None:
    """Rol ID orqali rol ma’lumotini qaytaradi."""
    return ROLE_MAP.get(role_id)


def get_roles_by_team(team: str) -> list[dict]:
    """Berilgan jamoaning barcha rollarini qaytaradi."""
    return [
        ROLE_MAP[role_id]
        for role_id in TEAM_ROLES.get(team, ())
    ]


def all_roles() -> list[dict]:
    """Barcha 36 rolni qaytaradi."""
    return list(ROLE_MAP.values())
