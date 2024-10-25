from web_scraper import SiteScraper

url_geral = 'https://www.site.com.br/'
url_consulta = ['https://www.site.com.br/']
paginas_busca = 800
usuario = "data_total"
navegador = "Edge"
robo_execucao = "Bot 02"

scraper = SiteScraper(url_geral, url_consulta, paginas_busca, usuario, navegador, robo_execucao)
scraper.executar_raspagem()