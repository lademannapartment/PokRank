import asyncio
import datetime as dt
from typing import Tuple, Dict, Optional
from playwright.async_api import Page, TimeoutError
from config_listings import STAY_NIGHTS, MAX_RANK
import re

# ============================================================
#                 BOOKING URL BUILDERS
# ============================================================

import urllib.parse

def build_gdansk_url(checkin: dt.date, checkout: dt.date) -> str:
    base_url = "https://www.booking.com/searchresults.pl.html?"
    params = {
        "ss": "Gdańsk",
        "dest_id": "-501400",
        "dest_type": "city",
        "checkin_year": checkin.year,
        "checkin_month": checkin.month,
        "checkin_monthday": checkin.day,
        "checkout_year": checkout.year,
        "checkout_month": checkout.month,
        "checkout_monthday": checkout.day,
        "group_adults": "2",
        "no_rooms": "1",
        "sb_price_type": "total",
        "sort_by": "price",  # Для новых версий
        "order": "price"     # Для старых версий
    }
    return base_url + urllib.parse.urlencode(params)


def build_sopot_url(checkin: dt.date, checkout: dt.date) -> str:
    """Builds the search URL for Sopot on Booking.com."""
    base_url = "https://www.booking.com/searchresults.pl.html?"
    params = (
        f"ss=Sopot"
        f"&label=gdansk-9Jl3D827XtlVbxAFIIe8xQS630498147482"
        f"&aid=1610698"
        f"&dest_id=-529430&dest_type=city"
        f"&group_adults=2&group_children=0&no_rooms=1"
        f"&order=price"
        f"&checkin_year={checkin.year}&checkin_month={checkin.month}&checkin_monthday={checkin.day}"
        f"&checkout_year={checkout.year}&checkout_month={checkout.month}&checkout_monthday={checkout.day}"
    )
    return base_url + params


def build_gdynia_url(checkin: dt.date, checkout: dt.date) -> str:
    """Builds the search URL for Gdynia on Booking.com using the latest working parameters."""
    checkin_str = checkin.strftime("%Y-%m-%d")
    checkout_str = checkout.strftime("%Y-%m-%d")

    # Вставляем параметры ТОЧНО из вашей новой ссылки
    base_params = (
        f"label=gdynia-E6X5Vbw_4WOULlmMVnmwBwS438032525202%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atiaud-2382347442848%3Akwd-329594768370%3Alp9067427%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YcUc3ZfdbbfENZlBRQl9eqQ"
        f"&aid=1610698"
        f"&ss=Gdynia"
        f"&ssne=Gdynia"
        f"&ssne_untouched=Gdynia"
        f"&efdco=1"
        f"&lang=pl"
        f"&sb=1"
        f"&src_elem=sb"
        f"&dest_id=-501414"
        f"&dest_type=city"
        f"&group_adults=2"
        f"&no_rooms=1"
        f"&group_children=0"
        f"&sb_travel_purpose=leisure"
        f"&sb_lp=1"
        f"&order=price" # Сортировка по цене (от самой низкой)
    )

    return f"https://www.booking.com/searchresults.pl.html?{base_params}&checkin={checkin_str}&checkout={checkout_str}"

def build_gdynia_apartments_url(checkin: dt.date, checkout: dt.date) -> str:
    """Builds the search URL for Gdynia Apartments only (ht_id=201)."""
    checkin_str = checkin.strftime("%Y-%m-%d")
    checkout_str = checkout.strftime("%Y-%m-%d")

    base_params = (
        "label=gdynia-E6X5Vbw_4WOULlmMVnmwBwS438032525202%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atiaud-2382347442848%3Akwd-329594768370%3Alp9067427%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YcUc3ZfdbbfENZlBRQl9eqQ"
        "&aid=1610698"
        "&ss=Gdynia"
        "&ssne=Gdynia"
        "&ssne_untouched=Gdynia"
        "&lang=pl"
        "&dest_id=-501414"
        "&dest_type=city"
        "&group_adults=2"
        "&no_rooms=1"
        "&group_children=0"
        "&sb_travel_purpose=leisure"
        "&order=price"
        "&nflt=ht_id%3D201"   # 🔥 ТОЛЬКО АПАРТАМЕНТЫ
    )

    return (
        "https://www.booking.com/searchresults.pl.html?"
        f"{base_params}&checkin={checkin_str}&checkout={checkout_str}"
    )
async def block_heavy_resources(page: Page) -> None:
    """Блокирует картинки, медиа, шрифты и трекеры: страница грузится быстрее, подгрузка надёжнее."""
    blocked_types = {"image", "media", "font"}
    blocked_hosts = ("doubleclick", "google-analytics", "googletagmanager", "facebook", "hotjar")

    async def handler(route):
        req = route.request
        if req.resource_type in blocked_types or any(h in req.url for h in blocked_hosts):
            await route.abort()
        else:
            await route.continue_()

    await page.route("**/*", handler)


# ============================================================
#              CORE SCRAPING LOGIC
# ============================================================

async def scrape_cards_and_get_ranks(page: Page, listings_map: dict, MAX_RANK: int = 400) -> Tuple[Optional[Dict[str, int]], int]:
    """Возвращает (ranks_map, mmrent_count). ranks_map = None, если карточки не загрузились."""
    import html
    import re

    def clean_text(text: str) -> str:
        if not text: return ""
        decoded = html.unescape(text)
        cleaned = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', ' ', decoded.lower())
        return " ".join(cleaned.split())

    TITLE_SELECTOR = 'h2, h3, [data-testid="title"], [class*="PropertyCardTitle"]'
    PROPERTY_CARD_SELECTOR = 'div[data-testid="property-card"]'
    # Расширенный селектор кнопки "Показать еще"
    SHOW_MORE_SELECTOR = "button:has-text('Załaduj więcej wyników'), button:has-text('Załaduj'), [role='button']:has-text('Załaduj więcej wyników'), button:has-text('Show more'), button:has-text('результатов'), button:has-text('больше')"

    # Диагностика: счётчик результатов Booking (сколько объектов всего по запросу)
    try:
        total_text = await page.evaluate("""() => {
            const el = document.querySelector('[data-testid="pagination"], [data-testid="results-count"], h1');
            const all = Array.from(document.querySelectorAll('h1, div, span'))
                .map(e => e.children.length === 0 ? e.textContent.trim() : '')
                .filter(t => /\\d+\\s+(obiekt|wynik|property|properties|результат)/i.test(t));
            return all.length ? all[0] : (el ? el.textContent.trim().slice(0, 120) : 'нет');
        }""")
        print(f"   📋 Счётчик результатов на странице: {total_text}")
    except Exception as e:
        print(f"   ⚠️ Не удалось прочитать счётчик результатов: {e}")

    found_ranks = {name: None for name in listings_map.keys()}
    remaining_to_find = {clean_text(name): name for name in listings_map.keys()}
    mmrent_count = 0
    already_scanned_count = 0
    retries = 0

    print(f"   📈 Начинаю онлайн-анализ (цель: {MAX_RANK})...")

    # Ждем появления первой карточки
    try:
        await page.wait_for_selector(PROPERTY_CARD_SELECTOR, timeout=30000)
    except:
        print("   ⚠️ Карточки не появились на странице.")
        return None, 0

    # Используем фиксированное количество итераций (как в вашем примере),
    # но с условиями выхода
    for iteration in range(50):
        # 1. Скролл к низу страницы (ленивая подгрузка срабатывает от скролла)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)

        # 2. Получаем текущие заголовки через JS
        current_titles = await page.evaluate(f"""
            () => {{
                const cards = document.querySelectorAll('{PROPERTY_CARD_SELECTOR}');
                return Array.from(cards).map(card => {{
                    const t = card.querySelector('{TITLE_SELECTOR}');
                    return t ? t.innerText : "";
                }});
            }}
        """)

        new_total = len(current_titles)
        print(f"      [Итерация {iteration}] карточек в DOM: {new_total}, новых с прошлого раза: {new_total - already_scanned_count}, пустых подряд: {retries}")

        # 3. Анализ новых карточек
        if new_total > already_scanned_count:
            # Берем срез от последнего просканированного до MAX_RANK
            new_chunk = current_titles[already_scanned_count:MAX_RANK]

            for i, raw_title in enumerate(new_chunk):
                current_rank = already_scanned_count + i + 1
                c_title = clean_text(raw_title)

                if "mmrent" in c_title:
                    mmrent_count += 1

                for clean_target, original_name in list(remaining_to_find.items()):
                    # Поиск по первым 3 словам (самый надежный вариант)
                    keywords = " ".join(clean_target.split()[:3])

                    if keywords in c_title:
                        if found_ranks[original_name] is None:
                            found_ranks[original_name] = current_rank
                            print(f"      ✨ #{current_rank}: {original_name}")
                            del remaining_to_find[clean_target]

            already_scanned_count = min(new_total, MAX_RANK)
            print(f"      [Страница] Загружено карточек: {already_scanned_count}")
            retries = 0
        else:
            retries += 1

        # Выход, если всё нашли или достигли лимита
        # Останавливаемся, если всё найдено, достигнут лимит или 10 итераций подряд нет новых карточек
        if not remaining_to_find or already_scanned_count >= MAX_RANK or retries >= 10:
            break

        # 4. Нажимаем видимую кнопку "Załaduj więcej wyników" и ждём роста числа карточек
        try:
            btn = page.locator("text=Załaduj więcej wyników")
            clicked = False
            for i in range(await btn.count()):
                el = btn.nth(i)
                if await el.is_visible():
                    await el.scroll_into_view_if_needed()
                    box = await el.bounding_box()
                    # Что реально находится в точке центра кнопки (перекрывает ли её что-то)
                    covering = await page.evaluate(
                        "([x, y]) => { const e = document.elementFromPoint(x, y); return e ? (e.tagName + ' ' + (e.className || '').toString().slice(0, 60)) : 'null'; }",
                        [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2],
                    ) if box else "нет координат"
                    print(f"      🔎 Кнопка #{i}: в точке клика элемент = {covering}")
                    try:
                        await el.click(force=True, timeout=5000)
                        method = "force"
                    except Exception as click_err:
                        # Запасной вариант: клик через JS по самому элементу
                        await el.evaluate("e => e.click()")
                        method = f"js (после ошибки: {str(click_err)[:80]})"
                    clicked = True
                    print(f"      🖱️ Клик методом: {method}")
                    break

            if clicked:
                cards_before = await page.evaluate(f"document.querySelectorAll('{PROPERTY_CARD_SELECTOR}').length")
                print(f"      🔘 Клик #{iteration} 'Załaduj więcej wyników' (карточек до клика: {cards_before})")
                try:
                    await page.wait_for_function(
                        f"document.querySelectorAll('{PROPERTY_CARD_SELECTOR}').length > {cards_before}",
                        timeout=8000,
                    )
                    print("         ↳ карточки появились")
                except TimeoutError:
                    print("         ↳ за 8 с новых карточек не появилось")
                await asyncio.sleep(1)
                cards_after = await page.evaluate(f"document.querySelectorAll('{PROPERTY_CARD_SELECTOR}').length")
                still_visible = await btn.first.is_visible() if await btn.count() else False
                print(f"         ↳ карточек после клика: {cards_after}, кнопка видна: {still_visible}")
            elif iteration == 0:
                print("      ⚠️ Кнопка 'Załaduj więcej wyników' не найдена на странице.")
        except Exception as e:
            print(f"      ⚠️ Ошибка кнопки 'Załaduj': {e}")

    # --- ФИНАЛЬНЫЙ ОТЧЕТ ---
    print("\n" + "-" * 30)
    if remaining_to_find:
        print(f"   ❌ НЕ НАЙДЕНО ({len(remaining_to_find)} объектов):")
        for orig_name in remaining_to_find.values():
            print(f"      - {orig_name}")
    else:
        print(f"   🎯 ВСЕ объекты найдены!")
    print("-" * 30 + "\n")

    # Защита таблицы: при неполной загрузке (мало карточек) не возвращаем результат,
    # иначе ненайденные комнаты очистятся
    MIN_CARDS = 50
    if already_scanned_count < MIN_CARDS:
        print(f"   ⚠️ Загружено только {already_scanned_count} карточек (< {MIN_CARDS}). Результат не используется.")
        return None, 0

    return found_ranks, mmrent_count