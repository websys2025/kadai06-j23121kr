import requests
import pandas as pd

# e-Stat APIのアプリケーションID
APP_ID = "c08b6afaf1c01f97d8be79e9960a6c9fb5dd1266"


TARGET_STATS_DATA_ID = "0003421913" 
TARGET_CD_CAT01 = None


TARGET_CD_AREA = "12100"


DATA_LIMIT = "10"

API_URL = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# APIリクエストのパラメータを設定
params = {
    "appId": APP_ID,
    "statsDataId": TARGET_STATS_DATA_ID, # 設定した統計データIDを使用
    "cdArea": TARGET_CD_AREA,            # 設定した地域コードを使用
    "limit": DATA_LIMIT,                 # 取得するデータ数を制限
    # "cdCat01": TARGET_CD_CAT01,         # 特定のカテゴリコードが必要な場合は有効化
    "metaGetFlg": "Y",                   # メタ情報を取得
    "cntGetFlg": "N",                    # カウント情報を取得しない
    "explanationGetFlg": "Y",            # 説明情報を取得
    "annotationGetFlg": "Y",             # 注釈情報を取得
    "sectionHeaderFlg": "1",             # セクションヘッダーフラグ
    "replaceSpChars": "0",               # 特殊文字を置換しない
    "lang": "J"                          # 日本語を指定
}

if TARGET_CD_CAT01:
    params["cdCat01"] = TARGET_CD_CAT01

# APIリクエストを送信
print(f"APIリクエストを送信中... (統計データID: {TARGET_STATS_DATA_ID}, 地域: {TARGET_CD_AREA}, 制限: {DATA_LIMIT}件)")
response = requests.get(API_URL, params=params)

# レスポンスの確認と処理
if response.status_code == 200:
    data = response.json()

    if 'GET_STATS_DATA' not in data:
        print("エラー: APIレスポンスの構造が予期せぬものです。")
        result_info = data.get('RESULT', {})
        print(f"APIエラーコード: {result_info.get('STATUS', 'なし')}")
        print(f"APIエラーメッセージ: {result_info.get('ERROR_MSG', 'なし')}")
        exit() 
    if 'STATISTICAL_DATA' not in data['GET_STATS_DATA']:
        print("エラー: 指定された条件で統計データが見つかりませんでした。")
        print(f"APIエラーメッセージ: {data['GET_STATS_DATA'].get('RESULT', {}).get('ERROR_MSG', 'なし')}")
        exit()

    if 'DATA_INF' not in data['GET_STATS_DATA']['STATISTICAL_DATA']:
        print("エラー: データ情報（DATA_INF）が見つかりませんでした。データが存在しない可能性があります。")
        exit()

    values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']

    if not values:
        print("取得されたデータが空です。指定した条件に合致するデータがない可能性があります。")
        exit()

    df = pd.DataFrame(values)

    meta_info = data['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']

    for class_obj in meta_info:
        try:
            column_name = '@' + class_obj['@id']
        except TypeError: 
            print(f"警告: 不正な形式のCLASS_OBJをスキップしました: {class_obj}")
            continue

        id_to_name_dict = {}
        if 'CLASS' in class_obj:
            if isinstance(class_obj['CLASS'], list):
                for obj in class_obj['CLASS']:
                    if isinstance(obj, dict) and '@code' in obj and '@name' in obj:
                        id_to_name_dict[obj['@code']] = obj['@name']
            elif isinstance(class_obj['CLASS'], dict):
                if '@code' in class_obj['CLASS'] and '@name' in class_obj['CLASS']:
                    id_to_name_dict[class_obj['CLASS']['@code']] = class_obj['CLASS']['@name']

        if column_name in df.columns and id_to_name_dict: 
            df[column_name] = df[column_name].astype(str).replace(id_to_name_dict)

    col_replace_dict = {'@unit': '単位', '$': '値'}
    for class_obj in meta_info:
        try:
            org_col = '@' + class_obj['@id']
            new_col = class_obj['@name']
            col_replace_dict[org_col] = new_col
        except TypeError:
            continue 
    new_columns = []
    for col in df.columns:
        if col in col_replace_dict:
            new_columns.append(col_replace_dict[col])
        else:
            new_columns.append(col)

    df.columns = new_columns
    print("\n--- 取得したデータ（整形後）---")
    print(df)

else:
    print(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
    print(response.text) 