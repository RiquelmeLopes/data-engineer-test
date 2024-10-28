from flask import Flask, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)
client = bigquery.Client()

@app.route('/search', methods=['GET'])
def search_articles():
    keyword = request.args.get('keyword')
    
    ## Verificar se a keyword foi fornecida
    if not keyword:
        return jsonify({"error": "É necessário uma keyword."}), 400

    ## Definir a query para fazer a busca usando a keyword
    query = f"""
    SELECT headline, author, url, text
    FROM `xenon-pager-439914-k7.data_eng_test.articles_table`
    WHERE LOWER(text) LIKE '%{keyword.lower()}%'
    """

    ## Executar a consulta
    query_job = client.query(query)
    results = query_job.result()

    articles = [
        {
            'headline': row.headline,
            'author': row.author,
            'url': row.url,
            'text': row.text
        }
        for row in results
    ]

    return jsonify(articles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
