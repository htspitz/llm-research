# LLM & Data Science Research

本リポジトリは、LLM（大規模言語模型）の活用検証、およびデータサイエンスの実践的な前処理スクリプトをまとめたリサーチログです。

## 📂 構成

### 1. analysis_tools
銀行明細（住信SBIネット銀行）などの実データを対象とした、データエンジニアリング用スクリプト群です。
- **data_normalization.py**: 日本語データ特有のゆらぎ（全角・半角、不要な空白、特殊記号等）を正規表現を用いて一括変換し、分析に適した正規化データを作成します。
- **merge_csv.py**: 複数期間のCSVを統合し、エンコーディング修正や金額のクレンジング、日付によるソートを自動化します。
- **extract_debit.py / extract_high_priority.py**: 統合データからデビット利用明細や振込、高優先度の経費項目を特定条件で抽出します。

### 2. notebooks
LLM（Claude/Gemini/Llama/Qwen等）を活用した、多角的な技術検証ノートブック群です。Google ColabのSecrets（環境変数）を利用し、APIキーの秘匿化を行っています。

- **llm-amazon-item-classification.ipynb**: Amazonの購入履歴をLLMに渡し、商品カテゴリの自動分類や家計簿データへの整形を試行した記録です。
- **lora-finetuning-llama3.2/qwen2.5.ipynb**: 軽量なモデル（Llama 3.2やQwen 2.5）を対象に、LoRA（Low-Rank Adaptation）を用いた特定のタスクへのファインチューニング検証です。
- **rag-amazon-order-search.ipynb**: 注文履歴データをベクトル化し、自然言語で情報を検索するためのRAG（検索拡張生成）のプロトタイプ検証です。
- **ocr-financial-statement-analysis.ipynb**: 財務諸表や領収書の画像からテキストを抽出し、LLMで構造化データへと変換するOCR連携の試行です。
- **vllm-inference-benchmark.ipynb**: vLLMを用いた推論効率の計測など、実運用を見据えたパフォーマンス検証の記録です。

## 🛠️ 技術スタック
本リポジトリでは、実戦的なデータ処理から最新のLLM推論・学習技術まで、以下の広範な技術を活用しています。

### 1. LLM 推論・学習 (Fine-tuning & Inference)
- **Unsloth**: Llama 3.2 や Qwen 2.5 の高速なLoRAファインチューニングに使用
- **vLLM**: 高スループットな推論サービングとベンチマーク計測に使用
- **Anthropic (Claude API)**: `AsyncAnthropic` を用いた大規模データの非同期分類処理
- **Hugging Face (transformers, peft, trl)**: モデル制御および学習最適化

### 2. RAG & ベクトルデータベース
- **LangChain (community/core)**: RAGパイプラインの構築、ドキュメントの構造化
- **ChromaDB**: ベクトルデータの保存および類似性検索
- **Sentence-Transformers**: 多言語モデル（`multilingual-e5-large` 等）を用いた埋め込み生成

### 3. データ処理・エンジニアリング
- **pandas**: 大規模データの統合、クレンジング、統計分析
- **re (Regular Expression)**: 正規表現を用いた高度なテキスト正規化
- **tqdm / tqdm.asyncio**: 処理進捗の可視化および非同期処理の制御
- **Concurrent.futures**: 並列処理によるデータ処理の高速化

### 4. OCR & 画像処理
- **Tesseract OCR (pytesseract)**: 画像・PDFからの日本語テキスト抽出
- **pdfplumber / pdf2image**: PDFの解析およびレンダリング処理

### 5. Methodologies & Environment
- **Methodology**: 
    - **AI-DLC (AI Driven Life Cycle)**: AIを単なる補助ではなく、設計・実装・テストの各工程に組み込んだ爆速開発フローの実践
- **Infrastructure**: 
    - **Google Colab (Secrets管理)**: `google.colab.userdata` によるAPIキーのセキュアな管理
    - **Asyncio**: 非同期I/OによるAPIアクセスの効率化

## ⚡ セキュリティについて
- 本リポジトリ内のコードは、APIキーや個人情報をハードコードせず、環境変数またはシークレット管理機能を利用して実行する構成としています。
