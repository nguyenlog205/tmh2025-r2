# News Specialization Module

## 🔬 Description
This directory contains the entire business process pipeline for processing and analyzing financial news, focusing on assessing risks related to specific entities (e.g., Credit Suisse).

## 🔑 High-Level Approach
The process is divided into distinct, sequential steps:

```txt
  [News Ingestion]
         |
         v
[News Preprocessing]
         |
         v
[News Summarizing]
         |
         v
[News Analyzing]
```

## ⛏️File Descriptions

> Each script file handles a specific step in the pipeline:

### 1. `ingest_news.py`
- **Purpose**: To collect raw news data.
- **Function**: Uses Selenium to automate a browser, access Google News, and search by keyword (e.g., "Credit Suisse").
- **Output**: Saves a list of articles (including title, source, URL, and detailed content extracted with newspaper3k) to a JSON file.

### 2. `preprocess_news.py`
- **Purpose**: To clean and standardize the raw data.
- **Function**: Loads the JSON file from Step 1. Performs tasks such as:
    - Normalizing Unicode (NFC) for Vietnamese.
    - Removing duplicate articles based on the title.
    - Filtering out irrelevant articles (e.g., filtering by the "Credit Suisse" keyword).
    - Cleaning text (removing URLs, HTML tags, special characters, and junk phrases like "Photo:...", "Source:...").
    - Removing articles with content that is too short (word_count > 20).
- **Output**: A new JSON file containing the cleaned data (`cleaned_news_data.json`).

### 3. `summarize_news.py`
- **Purpose**: To summarize news content to reduce noise and focus on the main points.
- **Function**: Uses the `VietAI/vit5-large-vietnews-summarization` model (running on GPU if available) to generate concise summaries for the (cleaned) content of each article.
- **Output**: A new JSON file (`summarized_credit_suisse.json`) containing all original information plus a summarision field.

### 4. `analyze_news.py`
- **Purpose**: To analyze financial risk from the news content (either summarized or full text).
- **Function**: Defines the FinancialRiskAnalyzer class. This class uses the Groq API (with the llama-3.3-70b-versatile model) to analyze the text.
- **Output**: Returns a structured JSON object including:
    - `risk_score` (1-10)
    - `risk_category` (Liquidity, Legal, Reputation, Market, etc.)
    - `sentiment` (Negative, Neutral, Positive)
    - `key_entities` (Affected organizations/companies)
    - `publication_date` (Extracted from text)
    - `keywords` (List of 5-7 keywords)
    - `reasoning` (Brief explanation for the risk score)

### 5. `utils.py`
> *Contains small utility functions; currently a placeholder file.*

## 🫠 Usage
To run the entire pipeline, execute the scripts in the following order:
- **Ingest**: `python src/news_specialization/ingest_news.py`
- **Clean**: `python src/news_specialization/preprocess_news.py` (You may need to update the input/output file paths in the main function)
- **Summarize**: Run the `summarize_for_file()` function in `summarize_news.py`.
- **Analyze**: Use the `FinancialRiskAnalyzer` class from `analyze_news.py` to analyze the summarized data.