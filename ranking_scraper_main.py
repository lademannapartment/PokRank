import asyncio
import datetime as dt
import gspread
from playwright.async_api import async_playwright, Page
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_listings import (
    SHEET_NAME_GDANSK, SHEET_NAME_SOPOT, SHEET_NAME_GDYNIA,
    DAYS_FORWARD, STAY_NIGHTS, TIMEOUT_SEC,
    LISTING_COLUMNS_GDANSK, LISTING_COLUMNS_SOPOT, LISTING_COLUMNS_GDYNIA,
)

from gsheet_service import (
    initialize_gspread,
    find_row_by_date,
    update_spreadsheet_data,
    authorize_gspread
)

from scraper_core import (
    build_gdansk_url,
    build_sopot_url,
    build_gdynia_url,
    scrape_cards_and_get_ranks, block_heavy_resources
)


# ---------------------------------------------------------
#   СКАН ОДНОЙ ДАТЫ ДЛЯ ОДНОГО ГОРОДА
# ---------------------------------------------------------
async def process_date_for_city(
    page: Page,
    city_name: str,
    ws: gspread.Worksheet,
    url_builder: callable,
    listings_map: dict,
    date_obj: dt.date
):
    print(f"\n>>>> ДАТА: {date_obj.strftime('%d.%m.%Y')}  —  {city_name} <<<<")

    if ws is None:
        print(f"⚠️ Лист для {city_name} не открыт. Пропуск {date_obj.strftime('%d.%m.%Y')}.")
        return

    try:
        row_index = find_row_by_date(ws, date_obj)
    except RuntimeError as e:
        print(f"❌ {e}. Пропуск.")
        return

    if not row_index:
        print(f"⚠️ Дата {date_obj.strftime('%d.%m.%Y')} отсутствует в листе {ws.title}. Пропуск.")
        return

    checkin = date_obj
    checkout = checkin + dt.timedelta(days=STAY_NIGHTS)
    url = url_builder(checkin, checkout)

    try:
        await page.goto(url, timeout=120000, wait_until="domcontentloaded")
        await page.wait_for_selector('div[data-testid="property-card"]', timeout=15000)
        await asyncio.sleep(2)

        # cookies
        try:
            cookie_btn = page.locator('button#onetrust-accept-btn-handler')
            if await cookie_btn.is_visible(timeout=5000):
                await cookie_btn.click()
                print("🍪 Cookies закрыты.")
        except:
            pass

        ranks_map, mmrent_count = await scrape_cards_and_get_ranks(page, listings_map)

        # Карточки не загрузились — не трогаем таблицу, иначе данные за день очистятся
        if ranks_map is None:
            print(f"⚠️ {city_name} на {date_obj.strftime('%d.%m.%Y')}: карточки не загрузились, таблица не изменена.")
            return

        # ← исправлено: используются row_index, ranks_map, listings_map
        update_spreadsheet_data(
            ws,
            row_index,
            ranks_map,
            listings_map,
            city_name,
            mmrent_count=mmrent_count
        )

    except Exception as e:
        print(f"❌ Ошибка при обработке {city_name} на дату {date_obj}: {e}")
        await asyncio.sleep(3)



# ---------------------------------------------------------
#   ГЛАВНАЯ ФУНКЦИЯ — САМЫЙ ВАЖНЫЙ БЛОК
# ---------------------------------------------------------
async def main_async():

    authorize_gspread()
    now = dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    start_message = f"📅 Skanowanie rozpoczęło się: {now}"

    # --- Инициализация листов перед циклом ---
    ws_gdansk = initialize_gspread(SHEET_NAME_GDANSK)
    ws_sopot = initialize_gspread(SHEET_NAME_SOPOT)
    ws_gdynia = initialize_gspread(SHEET_NAME_GDYNIA)


    # Запись стартового времени
    try:
        if ws_gdansk:
            ws_gdansk.update_cell(1, 1, start_message)
        if ws_sopot:
            ws_sopot.update_cell(1, 1, start_message)
        if ws_gdynia:
            ws_gdynia.update_cell(1, 1, start_message)

        print("✅ Время старта записано.")
    except Exception as e:
        print(f"❌ Ошибка записи стартового времени: {e}")

    # ---------------- PLAYWRIGHT ----------------
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ],
            timeout=TIMEOUT_SEC * 1000
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="pl-PL",
            viewport={"width": 1920, "height": 1080}
        )

        page = await context.new_page()
        await block_heavy_resources(page)

        today = dt.date.today()
        #today = dt.date(2026, 2, 10)
        # ——— основной цикл по дням ———
        for i in range(DAYS_FORWARD):

            date_obj = today + dt.timedelta(days=i)

            print("\n====================================")
            print(f"📅 ДЕНЬ {i+1} — {date_obj.strftime('%d.%m.%Y')}")
            print("====================================")

            # 1 — Гданьск
            await process_date_for_city(
              page, "Гданьск", ws_gdansk, build_gdansk_url, LISTING_COLUMNS_GDANSK, date_obj
             )

            # 2 — Сопот
            await process_date_for_city(
              page, "Сопот", ws_sopot, build_sopot_url, LISTING_COLUMNS_SOPOT, date_obj
          )

            # 3 — Гдыня
            await process_date_for_city(
                page, "Гдыня", ws_gdynia, build_gdynia_url, LISTING_COLUMNS_GDYNIA, date_obj
            )


    print("\n🏁 ГОТОВО — ВСЕ ГОРОДА ОБРАБОТАНЫ\n")


if __name__ == "__main__":
    asyncio.run(main_async())


