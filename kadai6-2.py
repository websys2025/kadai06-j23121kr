import requests
import json
import pandas as pd

def get_weather_forecast(area_code="130000"):
 
    # 天気予報データが格納されているJSONのURL
    # forecast/data/forecast/ の後に続くのが予報区コード.json
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        
        # JSONデータを解析
        weather_data = response.json()
        return weather_data

    except requests.exceptions.RequestException as e:
        print(f"ウェブページの取得中にエラーが発生しました: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSONデータの解析中にエラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return None

def display_weather_info(data):
    """
    取得した天気予報データを整形して表示する関数。
    """
    if not data:
        print("表示するデータがありません。")
        return

    # 最初の要素が短期予報（今日・明日）、次の要素が週間予報
    # 今回は短期予報（最初の要素）に着目
    forecast_today_tomorrow = data[0]

    # 発表日時
    report_datetime = forecast_today_tomorrow.get('reportDatetime')
    print(f"発表日時: {report_datetime}\n")

    # 天気予報
    time_series = forecast_today_tomorrow.get('timeSeries', [])
    if time_series:
        # timeSeries[0] に天気、風、波の情報
        # timeSeries[1] に降水確率
        # timeSeries[2] に気温の情報
        
        # 天気情報
        weather_info = time_series[0].get('areas', [])
        if weather_info:
            area_name = weather_info[0].get('area', {}).get('name')
            weathers = weather_info[0].get('weathers', [])
            pops = time_series[1].get('areas', [])[0].get('pops', []) # 降水確率
            temps = time_series[2].get('areas', [])[0].get('temps', []) # 気温

            print(f"地域: {area_name}")
            print("-" * 20)

            # 日付ごとの予報表示
            time_defines = time_series[0].get('timeDefines', [])
            
            weather_list = []
            for i, dt in enumerate(time_defines):
                date_str = pd.to_datetime(dt).strftime('%Y年%m月%d日')
                weather = weathers[i] if i < len(weathers) else "N/A"
                pop = pops[i] if i < len(pops) else "N/A"
                
                # 気温は日によって最高気温と最低気温のセットの場合がある
                # timeDefines[2]は気温の予報期間に対応
                temp_min = "N/A"
                temp_max = "N/A"
                if i * 2 < len(temps): # tempsは[最低, 最高, 最低, 最高...]のように格納されることが多い
                    temp_min = temps[i*2]
                    temp_max = temps[i*2+1] if (i*2+1) < len(temps) else "N/A"

                weather_list.append({
                    '日付': date_str,
                    '天気': weather,
                    '降水確率': f"{pop}%",
                    '最低気温': temp_min,
                    '最高気温': temp_max
                })
            
            df = pd.DataFrame(weather_list)
            print(df.to_string(index=False)) # DataFrameで整形して表示

    else:
        print("天気予報データが見つかりませんでした。")


if __name__ == "__main__":
    # 例: 東京の予報区コード
    tokyo_area_code = "130000"
    
    weather_data = get_weather_forecast(tokyo_area_code)

    if weather_data:
        display_weather_info(weather_data)
    else:
        print("天気予報データの取得に失敗しました。")