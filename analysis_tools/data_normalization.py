import pandas as pd
import glob
import os
import numpy as np
import re
import unicodedata 

# --- 設定 ---
file_pattern = 'meisai_*.csv' 
columns_to_drop = [
    'お取引通貨', 'お取引手数料', 'ATM手数料', 
    '海外事務手数料', 'ご利用通貨', 'ご利用金額', 'ご利用手数料', '換算レート'
]
output_file = 'final_journal_sheet_ready_for_review_ver2.csv'


# --- 処理関数：表記統一（変更なし） ---
def normalize_transaction_name_core(name):
    if pd.isna(name): return None
    name = str(name).strip()
    name = unicodedata.normalize('NFKC', name)
    name = name.upper()
    name = re.sub(r'[-.\*\\()、，]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

custom_mapping = {
    'AMAZON CO JP': 'AMAZON', 'AMAZONCOM': 'AMAZON', 'AMAZON DOWNLOADS': 'AMAZON DOWNLOAD',
    'AMAZON PRIME KAIHI': 'AMAZON PRIME', 'AMAZON プライム会費': 'AMAZON PRIME', 
    'GOOGLE GSUITE PARALLEL': 'GOOGLE GSUITE', 'GOOGLE PLAY JAPAN': 'GOOGLE PLAY',
    'UBER EATS': 'UBER EATS', 'GO タクシーアプリ': 'GO TAXI', 
    'ｷﾖｾｼｺﾜｰｷﾝｸﾞｽﾍﾟｰｽｺﾄﾘﾊﾞ': '清瀬市コワーキングスペース', 'ﾕ-ｳｴｱ': 'ユニウェア', 
    'Looopでんき': 'Looopでんき', 'Ｒｅｎｔｉｏ': 'RNTIO', 'ＡｎｏｔｈｅｒＡＤｒｅｓｓ': 'アナザーアドレス',
    'ＳＱ＊Ｄライフ': 'Dライフ', 'ｅｌｉｆｅ': 'イーライフ', 'ﾌﾘｰ': 'フリー', 'GOOGLE GOOGLE ONE': 'GOOGLE ONE'
}
custom_mapping_upper = {normalize_transaction_name_core(k): v for k, v in custom_mapping.items()}

def normalize_transaction_name(name):
    normalized_name = normalize_transaction_name_core(name)
    if normalized_name is None: return None
    return custom_mapping_upper.get(normalized_name, normalized_name)


# --- 用途分類ロジック（最終確定版） ---
usage_rules = {
    '事業用': ['GOOGLE GSUITE', 'BIZcomfort', '清瀬市コワーキングスペース', 'ｍｏｎｏｏＱ', 'フリー', 'RNTIO', 'FACEBOOK ADS', 'GO TAXI'],
    '私用': [
        'クリニックフォア', 'ニトリ', 'ニンテンドーEショップ', 'CHOKOZAP', 'ミケネコカフェ清瀬店', 
        'ZOZOTOWN', 'メルカリ', 'STARFLYER インターネット', 'AGODA', '楽天', 'DMM', 'ユニクロ', 
        'ユニクロ GU PLSTオンライン', 'ユニウェア', 'アナザーアドレス', 'イーライフ', 'ＣＨＥＥＲＺ', 
        'モバイルSuica', 'Dライフ', 'GOOGLE PLAY', 'YOUTUBE PREMIUM', 'UBER EATS', 'AMAZON DOWNLOAD', 
        'AMAZON PRIME', 'GOOGLE ONE' # Google One追加
    ],
    '按分': ['AMAZON', 'Looopでんき'] 
}
def classify_usage(name):
    if pd.isna(name): return '未分類'
    name = name.upper() 
    for usage, names in usage_rules.items():
        if name in [n.upper() for n in names]:
            return usage
    return '未分類'

# --- 勘定科目・按分ロジック ---

account_mapping = {
    'GOOGLE GSUITE': '通信費', 'BIZcomfort': '地代家賃', '清瀬市コワーキングスペース': '地代家賃',
    'ｍｏｎｏｏＱ': '消耗品費', 'フリー': '租税公課', 'RNTIO': '賃借料', 'FACEBOOK ADS': '広告宣伝費',
    'AMAZON': '消耗品費', # ※手動で修正を前提
    'Looopでんき': '水道光熱費', 'GO TAXI': '旅費交通費',
}

def calculate_business_amount(row):
    usage = row['用途分類']
    amount = row['お取引金額']
    name = row['お取引内容（統一済）']

    # マイナス取引も按分計算に含める（返金も割合に応じて事業用として相殺されるように）
    if usage == '事業用':
        return amount
    
    elif usage == '按分':
        if name == 'Looopでんき':
            # Looopでんき: 40%
            return amount * 0.40
        elif name == 'AMAZON':
            # AMAZON: 書籍(85%)とその他(0%)が混在するため、一旦85%で計算し、
            # CSV出力後に手動で修正することを前提とする。
            return amount * 0.85
            
    # 私用、未分類の場合は事業用金額はゼロ
    return 0.0

def assign_account(name, usage, amount):
    if usage == '私用':
        # マイナス（返金）の場合は事業主借、プラス（支払い）の場合は事業主貸
        return '事業主借' if amount < 0 else '事業主貸'
    
    account = account_mapping.get(name, '未割当')
    
    if account == '未割当':
        return '雑費' 
        
    return account


# --- 処理実行（メインフロー） ---

# 1. ファイル読み込み・結合
file_list = glob.glob(file_pattern)
if not file_list: exit()
all_data = []
for file_name in file_list:
    try:
        df = pd.read_csv(file_name, header=0, encoding='shift_jis', encoding_errors='replace', low_memory=False)
        if df.columns[0] == '1': df = df.drop(columns=[df.columns[0]])
        df = df.drop(columns=columns_to_drop, errors='ignore')
        df_cleaned = df.dropna(how='all', subset=df.columns.drop('お取引日'))
        all_data.append(df_cleaned)
    except Exception as e:
        continue
if not all_data: exit()
combined_df = pd.concat(all_data, ignore_index=True)

# 2. クレンジング・統一
combined_df['お取引日'] = combined_df['お取引日'].replace(' ', np.nan).fillna(method='ffill')
combined_df['お取引内容（統一済）'] = combined_df['お取引内容'].apply(normalize_transaction_name)

# 3. 用途分類の実行
combined_df['用途分類'] = combined_df['お取引内容（統一済）'].apply(classify_usage)

# 4. 🔥 Amazon 1000円以下を私用に強制変更 🔥
amazon_low_value = (combined_df['お取引内容（統一済）'] == 'AMAZON') & (combined_df['お取引金額'].abs() <= 1000)
combined_df.loc[amazon_low_value, '用途分類'] = '私用'


# 5. 勘定科目の割り当てと事業用金額の計算
# マイナス取引（返金）の勘定科目を考慮するため、amountを引数に追加
combined_df['勘定科目'] = combined_df.apply(lambda row: assign_account(
    row['お取引内容（統一済）'], row['用途分類'], row['お取引金額']
), axis=1)
combined_df['事業用金額'] = combined_df.apply(calculate_business_amount, axis=1)


# 6. 【最終調整】カラムの選択と並べ替え
final_columns_order = ['お取引日', '勘定科目', 'お取引内容（統一済）', 'お取引金額', '用途分類', '事業用金額']
combined_df_final = combined_df[final_columns_order]

# 7. 最終結果をCSVに出力
combined_df_final.to_csv(output_file, index=False, encoding='utf-8')

# --- 結果の確認と表示 ---
print("\n----------------------------------------------------")
print(f"✅ 🎉 最終仕訳データが完成しました！")
print(f"✨ Amazon 1,000円以下の取引は自動で私用に分類されています。")
print(f"💾 最終結果を '{output_file}' に保存しました。")
print("----------------------------------------------------")

print("\n--- 確認: 最終データのカラム構成 ---")
print(combined_df_final.columns.tolist())
print("\n--- 確認: 用途分類ごとの件数（Amazonの私用化後）---")
print(combined_df_final['用途分類'].value_counts())
print("\n--- 🚨 次のステップのヒント 🚨 ---")
print("1. 作成されたCSVを開いてください。")
print("2. 'お取引内容（統一済）'が 'AMAZON' の行で、書籍**ではない**と確認できた行の '事業用金額' を 0 に手動で修正してください。")
print("3. '用途分類'が '未分類' の取引（あれば）を確認し、勘定科目を修正してください。")
print("4. マイナス金額の行は、勘定科目が『事業主借』で正しいか確認してください。（私用返金の場合）")