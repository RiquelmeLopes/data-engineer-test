from bs4 import BeautifulSoup
import requests
import json
from readability import Document

## Configurar cabeçalho da requisição para evitar bloqueios
headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

def extrair_links_recentes():
    url_base = 'https://www.bbc.com/news'
    response = requests.get(url_base)
        
    if response.status_code != 200:
        print(f"Erro ao acessar {url_base}")
            
    soup = BeautifulSoup(response.text, 'html.parser')
        
    ## Encontrar todas as tags 'a' com classe 'sc-2e6baa30-0 gILusN' que são referentes a links
    artigos = soup.find_all('a', class_='sc-2e6baa30-0 gILusN', limit=40)
        
    ## Extrair os links dos artigos, apenas salvando os que possuem /news no começo para excluir os links de navegação da bbc, e retirando os que são tópicos e não notícias em si.
    links = ['https://www.bbc.com' + artigo['href'] for artigo in artigos if artigo.get('href', '').startswith('/news/articles')]
    print('Links extraídos com sucesso')
    return links

def extrair_dados(url):    
    request_result = requests.get(url, headers=headers)

    ## Aviso para caso tenha algum erro de requisição  
    if request_result.status_code != 200:
        print(f"Erro ao acessar {url}")
        return None

    doc = Document(request_result.text)
    soup = BeautifulSoup(request_result.text, 'html.parser')

    ## Extrair titulo com o Readability pela simplicidade  
    headline = doc.title()
        
    ## Extrair informações do artigo diretamente da div 'text-block' para evitar conteúdo indesejado  
    text_blocks = soup.find_all('div', {'data-component': 'text-block'})
        
    texto_bruto = []
    for block in text_blocks:
        paragraphs = block.find_all('p')
        for paragraph in paragraphs:
            texto_bruto.append(paragraph.get_text(strip=True))

    article_text = ' '.join(texto_bruto)

    ## O nome do autor está configurando dentro de um JSON embutido na página, então vamos extrair diretamente de lá
    script_tag = soup.find('script', type='application/ld+json')    
    if script_tag:
        data = json.loads(script_tag.string)

        ## Verificar previamente se o JSON existe. Caso não encontre um JSON dentro do artigo (ou seja, o autor não está listado) ele retorne "Autor não encontrado"
        if 'author' in data and isinstance(data['author'], list) and data['author']:
            author = data['author'][0]['name']
        else:
            author = 'Autor não encontrado'
            
    ## Estruturar os dados do artigo em um dicionário
    article_data = {
        'headline': headline,
        'text': article_text,
        'author': author,
        'url': url
    }

    print(f'Dados do artigo "{headline}" extraídos com sucesso')
    return article_data

## Loop em todos os links adquiridos para fazer a extração em todos de uma vez
links = extrair_links_recentes()
articles = []
for link in links:
    article_data = extrair_dados(link)
    if article_data:
        articles.append(article_data)

## Armazenar tudo em um JSON 
with open('articles.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=4)