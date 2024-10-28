from google.cloud import bigquery
import json

def upload_to_bigquery(json_file_path, dataset_id, table_id):
    client = bigquery.Client()
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    rows_to_insert = [
        {
            "headline": article["headline"],
            "text": article["text"],
            "author": article["author"],
            "url": article["url"]
        }
        for article in articles
    ]

    table_ref = f"{client.project}.{dataset_id}.{table_id}"

    # Testar para caso tenha erros, entender quais foram
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors == []:
        print("Os dados foram carregados com sucesso no BigQuery.")
    else:
        print("Erro ao carregar os dados:", errors)

# Executar 
upload_to_bigquery('articles.json', 'data_eng_test', 'articles_table')
