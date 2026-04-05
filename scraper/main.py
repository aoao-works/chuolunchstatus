import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def parse_shokudo(url, target_date, campus_name):
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    
    current_month = target_date.month
    today = target_date.day
    
    rows = soup.select("table.small tr")
    headers = None
    today_row = None
    is_correct_month = False
    
    for row in rows:
        cols = row.select("td")
        if not cols: continue
        
        first_col = cols[0]
        if first_col.get("colspan") == "2" and "月" in first_col.text:
            month_str = first_col.text.replace("月", "").strip()
            if month_str.isdigit() and int(month_str) == current_month:
                is_correct_month = True
                headers = cols
            else:
                is_correct_month = False
            continue
        
        if is_correct_month and len(cols) > 1:
            try:
                if int(cols[0].text.strip()) == today:
                    today_row = row
                    break
            except ValueError:
                pass
    
    results = []
    if today_row and headers:
        data_cols = today_row.select("td")
        for i in range(1, len(headers)):
            data_index = i + 1
            if data_index < len(data_cols):
                name = headers[i].text.strip()
                hours = data_cols[data_index].text.strip()
                results.append({
                    "name": name,
                    "hours": hours,
                    "campus": campus_name
                })
    return results

def parse_library(target_date):
    libraries = {
        "10": ["中央図書館", "多摩キャンパス"],
        "51": ["理工図書館", "後楽園キャンパス"],
        "60": ["法学部図書館", "茗荷谷キャンパス"],
        "30": ["市ヶ谷図書館", "市ヶ谷田町キャンパス"]
    }
    results = []
    for code, info in libraries.items():
        url = f"https://ufinity.library.chuo-u.ac.jp/iwjs0002opc/xmlcldday.do?dispArea={code}"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'xml')
            group_ids = soup.select("group_id")
            group_names = soup.select("group_name")
            hours = "休館"
            
            if len(group_ids) > 2:
                today_group_id = group_ids[-2].text
                for i in range(len(group_ids) - 2):
                    if group_ids[i].text == today_group_id:
                        hours = group_names[i].text
                        break
            
            results.append({
                "name": info[0],
                "hours": hours.replace("：", ":").replace("～", "~"),
                "campus": info[1]
            })
        except Exception:
            pass
    return results

def main():
    now = datetime.now()
    
    facilities = []
    facilities.extend(parse_shokudo("https://www.chudai-seikyo.or.jp/time/index_time.php", now, "多摩キャンパス"))
    facilities.extend(parse_shokudo("https://www.chudai-seikyo.or.jp/time/index_time2.php", now, "都心キャンパス"))
    facilities.extend(parse_library(now))
    
    data = {
        "last_updated": now.strftime("%Y/%m/%d %H:%M"),
        "facilities": facilities
    }

    os.makedirs('public', exist_ok=True)
    with open('public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()