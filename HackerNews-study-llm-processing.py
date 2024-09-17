import json
import time
import requests
import os
import threading
from datetime import datetime
import pandas as pd
from model import HNJobPosting
import math


URL = "https://api.withexxa.com"


json_req = [
        {"role": "system", "content": f"You are an helpful assistant, you will fill a json object from a Who's Hiring hackernews post. You will use the following json schema to answer: {HNJobPosting.model_json_schema()}"}
      ]


session = requests.Session()
session.headers.update({"X-API-Key": os.environ["EXXA_API_KEY"], "Content-Type": "application/json"})


def api_exxa_call(offer: str, id: int):
    url = f"{URL}/v1/requests"
    msg = json_req.copy()
    msg.append({"role": "user", "content": "Parse the following post to json: "+offer})
    payload = {
        "metadata": {
            "comment_id": str(id)
        },
        "request_body": {
            "model": "llama-3.1-70b-instruct-fp16",
            "messages": msg,
            "temperature": 0.1,
            "n": 1,
            "max_tokens": 10000,
            "response_schema": json.dumps(HNJobPosting.model_json_schema())
        }
    }
    response = session.post(url, json=payload)
    return response.json()


def call_api_one_month(comments_jsonl_file, write_to_file=False):
    total_time = 0
    with open(comments_jsonl_file, "r") as file:
        with open("exxa_api_response.jsonl", "w") as output_file:
            for line in file:
                comment = json.loads(line)
                if "deleted" not in comment or not comment["deleted"]:
                    if "text" not in comment:
                        continue
                    start_time = time.time()
                    timestamp = comment["time"]
                    datetime_obj = datetime.fromtimestamp(int(timestamp))
                    year = datetime_obj.year
                    month = datetime_obj.month
                    response = api_exxa_call(f"Year: {year}, Month: {month}, Comment: {comment['text']}", comment["id"])
                    end_time = time.time()
                    total_time += end_time - start_time
                    if write_to_file:
                        output_file.write(json.dumps(response)+"\n")
    print(f"Total time: {total_time} seconds")
    return response

def start_process_whole_directory(dir_path):
    threads = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".jsonl"):
                file_path = os.path.join(root, file)
                thread = threading.Thread(target=call_api_one_month, args=(file_path,))
                threads.append(thread)
                thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()


def result_to_jsonl(result_file="exxa_api_response_done.jsonl"):
    # Get all the raw result from the api in a jsonl file, for programmed request stored in exxa_api_response.jsonl
    with open("exxa_api_response.jsonl", "r") as output_file:
        with open(result_file, "w") as output_file_done:
            for line in output_file:
                result = json.loads(line)
                id = result["id"]
                result_done = session.get(f"https://api.dev.withexxa.com/v1/requests/{id}")
                output_file_done.write(json.dumps(result_done.json())+"\n")


def result_all_hackernews_to_jsonl(file_path="HN_case_study_response.jsonl"):
    # Get all the raw result from the api in a jsonl file, for all the request done on this account
    result = session.get("https://api.dev.withexxa.com/v1/requests", params={"full": "true"})
    with open(file_path, "w") as output_file:
        for line in result.iter_lines():
            try:
                result_json = json.loads(line)
                output_file.write(json.dumps(result_json)+"\n")
            except Exception as e:
                print(e)


def token_count():
    total_tokens = 0
    with open('exxa_api_response_done.jsonl', 'r') as file:
        for line in file:
            data = json.loads(line)["result_body"]
            if 'usage' in data and 'total_tokens' in data['usage']:
                total_tokens += data['usage']['total_tokens']
    print(f"Total tokens: {total_tokens}")


def extract_content(x):
    try:
        content = x["choices"][0]["message"]["content"]
        # Ensure the content starts with a JSON-like structure
        if not content.strip().startswith('{"'):
            if not content.strip().startswith('"'):
                content = '{"' + content
            else:
                content = '{' + content
        return {'extracted_content': content}
    except:
        return {'extracted_content': None}

def extract_date_from_request(x):
    # try:
    messages = x.get('messages')
    for message in messages:
        if message.get('role') == 'user':
            content = message.get('content', '')
            # if content.startswith('Parse the following post to json:'):
            # Extract year and month using string manipulation
            year_start = content.find('Year: ') + 6
            year_end = content.find(',', year_start)
            month_start = content.find('Month: ') + 7
            month_end = content.find(',', month_start)
            
            year = content[year_start:year_end].strip()
            month = content[month_start:month_end].strip()
            
            return {'year': year, 'month': month}
    return {'year': None, 'month': None}
    # except:
    #     return {'year': None, 'month': None}


def hackernews_result_to_csv(file_path="HN_case_study_response.jsonl"):
    # Read the JSON lines file
    df = pd.read_json(file_path, lines=True)
    
    # Parse the JSON strings in 'result_body' and create a new DataFrame
    result_bodies = df['result_body'].apply(extract_content)
    print(result_bodies.head())
    df_results = pd.json_normalize(result_bodies.tolist())
    
    # Extract date information
    date_info = df['request_body'].apply(extract_date_from_request)
    df_date = pd.json_normalize(date_info.tolist())
    
    # Concatenate the original DataFrame with the new results and date DataFrames
    df = pd.concat([df, df_results, df_date], axis=1)
    
    # Check if each "extracted_content" is a valid dictionary
    def is_valid_dict(content):
        try:
            # Parse the content if it's a string
            if isinstance(content, str):
                content = json.loads(content)
            
            # Check if it's a dictionary and has the required key
            return isinstance(content, dict) and "comment_status" in content
        except json.JSONDecodeError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

    valid_dicts = df['extracted_content'].apply(is_valid_dict)
    print(f"Valid dictionaries: {valid_dicts.sum()}")
    print(f"Invalid dictionaries: {(~valid_dicts).sum()}")
    print(df[~valid_dicts]["extracted_content"].head())

    # Sort the DataFrame by year and month
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['month'] = pd.to_numeric(df['month'], errors='coerce')
    df = df.sort_values(['year', 'month'])
    df = df.reset_index(drop=True)

    
    print(df.head())
    df.to_csv("HN_case_study_fullresponse.csv", index=False)


def extract_content(x):
    try:
        content = x["choices"][0]["message"]["content"]
        # Ensure the content starts with a JSON-like structure
        if not content.strip().startswith('{"'):
            if not content.strip().startswith('"'):
                content = '{"' + content
            else:
                content = '{' + content
        return {'extracted_content': content}
    except:
        return {'extracted_content': None}

def extract_date_from_request(x):
    # try:
    messages = x.get('messages')
    for message in messages:
        if message.get('role') == 'user':
            content = message.get('content', '')
            # if content.startswith('Parse the following post to json:'):
            # Extract year and month using string manipulation
            year_start = content.find('Year: ') + 6
            year_end = content.find(',', year_start)
            month_start = content.find('Month: ') + 7
            month_end = content.find(',', month_start)
            
            year = content[year_start:year_end].strip()
            month = content[month_start:month_end].strip()
            
            return {'year': year, 'month': month}
    return {'year': None, 'month': None}
    # except:
    #     return {'year': None, 'month': None}


def parse_hn_job_posting(content: str) -> pd.Series:
    try:
        data = json.loads(content)
        return pd.Series({
            'comment_status': data.get('comment_status'),
            'remote': data.get('remote'),
            'visa_sponsoring': data.get('visa_sponsoring'),
            'states': ','.join(data.get('states', [])),
            'countries': ','.join(data.get('countries', [])),
            'continents': ','.join(data.get('continents', [])),
            'cities': ','.join(data.get('cities', [])),
            'tech_stack': ','.join(data.get('tech_stack', [])),
            'job_title': ','.join(data.get('job_title', [])),
            'job_type': ','.join(data.get('job_type', [])),
            'seniority_level': ','.join(data.get('seniority_level', [])),
            'compensation_min': data.get('compensation_min'),
            'compensation_max': data.get('compensation_max'),
            'perks': ','.join(data.get('perks', [])),
            'hiring_company': data.get('hiring_company'),
            'company_size': data.get('company_size'),
            'fundraising_round': data.get('fundraising_round'),
            'fundraising_amount': data.get('fundraising_amount')
        })
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return pd.Series()
    except TypeError as e:
        if isinstance(content, float) and math.isnan(content):
            return pd.Series()
        print(f"Type error: {e}")
        print(f"Content: {content}")
        print(f"Type: {type(content)}")
        return pd.Series()


def expand_extracted_content():
    df = pd.read_csv("HN_case_study_response.csv")
    
    # Parse extracted_content and create new columns
    parsed_data = df['extracted_content'].apply(parse_hn_job_posting)
    expanded_df = pd.concat([df[['year', 'month', 'metadata']], parsed_data], axis=1)
    
    # Save the expanded DataFrame
    expanded_df.to_csv("HN_case_study_expanded.csv", index=False)
    print("Expanded data saved to HN_case_study_expanded.csv")
    print(f"Columns in expanded_df: {expanded_df.columns.tolist()}")


if __name__ == "__main__":
    # Call llm api for all the comments
    start_process_whole_directory("output")

    # Call the next function only once the API is done processing the requests

    # Get all the raw result from the api in a jsonl file
    result_all_hackernews_to_jsonl()
    # Parse the jsonl file to a csv
    hackernews_result_to_csv()
    # Reformat the csv to have content reformated in columns, and unused columns removed
    expand_extracted_content()
