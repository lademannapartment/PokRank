import datetime as dt
import gspread
import os
import sys
import json
import time
import socket
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError
from config_listings import SPREADSHEET_URL, CREDENTIALS_FILE
from config_listings import MMRENT_COUNT_COLUMN_GDANSK

# Global gspread client
gc = None

# ---------------------------------------------
# Функция для перевода номера колонки в букву
# ---------------------------------------------
def col_to_letter(col: int) -> str:
    result = ""
    while col > 0:
        col, rem = divmod(col - 1, 26)
        result = chr(65 + rem) + result
    return result

# ---------------------------------------------
# Авторизация gspread
# ---------------------------------------------
def authorize_gspread():
    global gc

    if "GOOGLE_CREDS" in os.environ:
        try:
            creds_json = json.loads(os.environ["GOOGLE_CREDS"])
            creds = Credentials.from_service_account_info(
                creds_json,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            print("✅ GOOGLE_CREDS загружены из переменной окружения.")
        except json.JSONDecodeError:
            print("❌ Ошибка: переменная GOOGLE_CREDS не является корректным JSON.")
            sys.exit(1)
    else:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"❌ Критическая ошибка: файл учетных данных '{CREDENTIALS_FILE}' не найден.")
            sys.exit(1)
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        print(f"✅ GOOGLE_CREDS загружены из локального файла {CREDENTIALS_FILE}")

    try:
        gc = gspread.authorize(creds)
    except Exception as e:
        print(f"❌ Критическая ошибка авторизации gspread: {e}")
        sys.exit(1)

# ---------------------------------------------
# Инициализация Google Sheet
# ---------------------------------------------
def initialize_gspread(sheet_name: str):
    if gc is None:
        authorize_gspread()
        if gc is None:
            return None
    try:
        sh = gc.open_by_url(SPREADSHEET_URL)
        ws = sh.worksheet(sheet_name)
        return ws
    except Exception as e:
        print(f"❌ Ошибка при работе с Google Sheets (Лист: {sheet_name}): {e}")
        return None

# ---------------------------------------------
# Поиск строки по дате с ретраями
# ---------------------------------------------
def find_row_by_date(ws, target_date: dt.date, retries: int = 3):
    for attempt in range(1, retries + 1):
        try:
            values = ws.col_values(1)
            for idx, cell in enumerate(values, start=1):
                if not cell.strip():
                    continue
                try:
                    try:
                        cell_date = dt.datetime.strptime(cell.strip(), "%d.%m.%Y").date()
                    except ValueError:
                        cell_date = dt.datetime.strptime(cell.strip(), "%Y-%m-%d").date()
                    if cell_date == target_date:
                        return idx
                except ValueError:
                    continue
            return None  # дата реально не найдена
        except (APIError, ConnectionError, socket.error) as e:
            print(f"⚠️ Ошибка соединения при поиске даты {target_date} "
                  f"(попытка {attempt}/{retries}): {e}")
            time.sleep(2)
    raise RuntimeError(f"❌ Не удалось получить данные из Google Sheets для даты {target_date}")
SHEET_NAME_PBN = "Rank PBN"
# ---------------------------------------------
# Обновление данных в Google Sheet
# ---------------------------------------------
def update_spreadsheet_data(
        ws: gspread.Worksheet,
        row_index: int,
        ranks_map: dict,
        listings_map: dict,
        city_name: str,
        mmrent_count: int = None,
):
    data_to_run_main = []  # Для основного листа
    data_to_run_pbn = []  # Для листа Rank PBN

    # Нормализованная карта рангов
    norm_ranks = {str(k).strip(): v for k, v in ranks_map.items() if v is not None}

    # Список всех найденных рангов наших объектов (для вычитания)
    our_found_ranks = sorted([v for v in norm_ranks.values()])

    # Инициализируем лист PBN только если это Гданьск
    ws_pbn = None
    if city_name == "Гданьск":
        ws_pbn = initialize_gspread(SHEET_NAME_PBN)

    for listing_title, col_idx in listings_map.items():
        clean_title = str(listing_title).strip()
        rank = norm_ranks.get(clean_title)

        col_letter = col_to_letter(col_idx)

        # --- ЛОГИКА ОЧИСТКИ И ЗАПИСИ ---
        if rank is not None:
            # 1. Основной ранг (как есть)
            data_to_run_main.append({
                'range': f"{col_letter}{row_index}",
                'values': [[rank]]
            })

            # 2. Логика для Rank PBN (только Гданьск)
            if ws_pbn:
                # Считаем сколько НАШИХ объектов выше (ранг меньше текущего)
                higher_than_us = len([r for r in our_found_ranks if r < rank])
                pbn_rank = rank - higher_than_us

                data_to_run_pbn.append({
                    'range': f"{col_letter}{row_index}",
                    'values': [[pbn_rank]]
                })
                print(f"      📊 PBN пересчет: {clean_title} -> {rank} - {higher_than_us} = {pbn_rank}")
        else:
            # ЕСЛИ НЕ НАШЛИ - ОЧИЩАЕМ ЯЧЕЙКИ (удаляем старый скан)
            data_to_run_main.append({
                'range': f"{col_letter}{row_index}",
                'values': [[""]]
            })
            if ws_pbn:
                data_to_run_pbn.append({
                    'range': f"{col_letter}{row_index}",
                    'values': [[""]]
                })

    # --- ОТПРАВКА В ТАБЛИЦУ ---

    # Обновляем основной лист
    if data_to_run_main:
        try:
            ws.batch_update(data_to_run_main, value_input_option='USER_ENTERED')
            print(f"✅ [GSheets] {city_name}: Основной лист обновлен (с очисткой ненайденных).")
        except Exception as e:
            print(f"❌ Ошибка основного листа {city_name}: {e}")

    # Обновляем лист Rank PBN (только Гданьск)
    if ws_pbn and data_to_run_pbn:
        try:
            ws_pbn.batch_update(data_to_run_pbn, value_input_option='USER_ENTERED')
            print(f"✅ [GSheets] {city_name}: Лист Rank PBN обновлен.")
        except Exception as e:
            print(f"❌ Ошибка листа Rank PBN: {e}")

    # 3. MMRent Count (только Гданьск)
    if city_name == "Гданьск" and mmrent_count is not None:
        try:
            mmrent_col_letter = col_to_letter(MMRENT_COUNT_COLUMN_GDANSK)
            ws.update(range_name=f"{mmrent_col_letter}{row_index}",
                      values=[[mmrent_count]],
                      value_input_option='USER_ENTERED')
        except Exception as e:
            print(f"   ⚠️ Ошибка записи MMRent: {e}")
