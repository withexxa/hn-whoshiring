# HackerNews Job Market Analysis

This repository contains an analysis of the job market trends based on HackerNews "Who is hiring?" threads, using Exxa API to process the data.
This code is provided "as is", and is not production ready. An other API than Exxa could be used, but the code would need to be adapted.
The project is divided into three main components:

## 1. HackerNews Parsing

Located in the `hacker_news_parsing` directory, this component is responsible for:
- Scraping the "Who is hiring?" threads from HackerNews
- Extracting relevant job posting comments
- Storing the raw data for further processing

Runing the script `hacker_news_parsing/fetch_offers.py` will do all the steps for you.

## 2. LLM Processing

Found in the `HackerNews-study-llm-processing.py` file, this stage involves:
- Utilizing the Exxa API to process each job posting comment
- Extracting structured information from the results of the LLM
- Transforming the data into a format suitable for analysis

## 3. Data Analysis

The `HackerNews-study-data-analysis.py` file contains scripts for:
- Analyzing the processed data to identify trends
- Generating visualizations and statistics
- Producing insights about the job market over time

## How it Works

1. The Hacker News parser collects job postings from monthly "Who is hiring?" threads.
2. Each job posting is then processed using a Large Language Model (LLM) via the Exxa API to extract key information such as job titles, required skills, locations, and more.
3. The extracted data is then analyzed to reveal trends in the tech job market, including popular technologies, salary ranges, and geographical distribution of opportunities.

## Getting Started

To run this analysis:

1. Clone the repository
2. Install the required dependencies (`pip install -r requirements.txt`). Tested with python 3.10 on linux.
3. Run the scripts in the following order:
   - Hacker News parsing script `hacker_news_parsing/fetch_offers.py`
   - LLM processing script `HackerNews-study-llm-processing.py` (in two steps, you should first only run `start_process_whole_directory()`, then the rest only when the API has processed all the data)
   - Data analysis script `HackerNews-study-data-analysis.py`

## Results

The results of this analysis provide valuable insights into the evolving landscape of the tech job market, as reflected in HackerNews job postings. These insights can be useful for job seekers, recruiters, and anyone interested in tech industry trends.

For detailed findings, please refer to the generated charts and reports in the `results` directory.
