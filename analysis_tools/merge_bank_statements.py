import pandas as pd
import os

# --- 設定 ---
# 統合対象のファイル名リスト
file_names = [
    "sumishin_syukkin_201801_202008.csv",
    "sumishin_syukkin_202009_202102.csv",
    "sumishin_syukkin_202103_202109.csv",
    "sumishin_syukkin_202110_202204.csv",
    "sumishin_syukkin_202205_202210.csv",
    "sumishin_syukkin_202211_202304.csv",
    "sumishin_syukkin_202305_202310.csv",
    "sumishin_syukkin_202311_202404.csv",
    "sumishin_syukkin_202405_202410.csv",
    "sumishin_syukkin_202411_202504.csv",
    "sumishin_syukkin_202505_20251103.csv",
]
output_file_name = "integrated_sumishin_syukkin.csv"

# 全データを格納するリスト
all_data = []

print("--- 処理開始 ---")

# 1. 最初のファイルを読み込み、列名（ヘッダー）を取得
try:
    print(f"1/11: '{file_names[0]}' を読み込み中...")
    # ★ 修正箇所: encoding='cp932' を追加
    first_df = pd.read_csv(file_names[0], encoding='cp932') 
    all_data.append(first_df)
    column_names = first_df.columns
except FileNotFoundError:
    print(f"エラー: ファイル '{file_names[0]}' が見つかりません。すべてのファイルが同じフォルダにあるか確認してください。")
    exit()
except Exception as e:
    print(f"エラー: 最初のファイルの読み込み中に予期せぬエラーが発生しました: {e}")
    exit()

# 2. 残りのファイルを読み込み、ヘッダーをスキップして追記
for i, file in enumerate(file_names[1:]):
    print(f"{i+2}/11: '{file}' を読み込み中...")
    try:
        # 2つ目以降のファイルはヘッダー行（1行目）をスキップして読み込む
        # ★ 修正箇所: encoding='cp932' を追加
        df = pd.read_csv(file, header=None, skiprows=1, encoding='cp932') 
        # 列名を最初のデータフレームに合わせる
        df.columns = column_names
        all_data.append(df)
    except FileNotFoundError:
        print(f"警告: ファイル '{file}' が見つかりませんでした。スキップします。")
    except Exception as e:
        print(f"警告: ファイル '{file}' の読み込み中にエラーが発生しました ({e})。スキップします。")

# 3. 全データを結合
integrated_df = pd.concat(all_data, ignore_index=True)

# 4. データクレンジングと型変換
print("データクレンジングと型変換を実行中...")

# 金額列のクレンジング（カンマ除去と数値型変換）
cols_to_clean = ['出金金額(円)', '入金金額(円)', '残高(円)']
for col in cols_to_clean:
    # 数値以外の文字（カンマなど）を削除
    integrated_df[col] = integrated_df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
    # 空白やハイフンをNaNに置換してから数値に変換
    integrated_df[col] = pd.to_numeric(integrated_df[col], errors='coerce').fillna(0)

# '日付' 列を日付型に変換
integrated_df['日付'] = pd.to_datetime(integrated_df['日付'], errors='coerce')
integrated_df.dropna(subset=['日付'], inplace=True)

# 5. 日付で昇順に並び替え
integrated_df = integrated_df.sort_values(by='日付').reset_index(drop=True)

# 6. 統合されたデータフレームを新しいCSVファイルとして保存
integrated_df.to_csv(output_file_name, index=False, encoding='utf-8-sig')

print("\n--- 処理完了 ---")
print(f"統合後の総行数: {len(integrated_df)}行")
print(f"ファイル '{output_file_name}' として保存されました。")