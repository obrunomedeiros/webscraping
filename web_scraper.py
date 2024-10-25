from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import pandas as pd
import numpy as np
import json
import time
import os
import sys
from math import ceil
from unicodedata import normalize
import re
import random


class SiteScraper:

    def __init__(self, url_geral, url_consulta, paginas_busca, usuario, navegador="Firefox", robo_execucao="Bot 01"):
        self.url = url_geral
        self.url_consulta = url_consulta
        self.paginas_busca = paginas_busca
        self.usuario = usuario
        self.navegador = navegador
        self.bot = robo_execucao
        #Carrega os caminhos de pastas 
        with open(r'caminhos_pastas.json', encoding='utf-8') as File:
            self.pastas_arquivos = json.load(File)
        # Carrega as credenciais do Site
        with open(f'{self.pastas_arquivos["cred_path"]}credenciais_*******.json') as File:
            self.creds_site = json.load(File)
        # Inicializa o driver do Selenium

    def cria_driver(self):
    
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"]

        my_user_agent = random.choice(user_agents)  # Escolhe um user agent aleatoriamente_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        
        try:
            
            if str.lower(self.navegador) == "chrome":
                chrome_options = uc.ChromeOptions()
                #chrome_options.add_argument("--headless")
                #chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument(f"user-agent={my_user_agent}")
                # Criação do driver do navegador
                driver = uc.Chrome(options=chrome_options)
                
            elif str.lower(self.navegador) == "firefox":
                #informações do webdriver do modulo selenium
                # Configuração do navegador
                firefox_options = webdriver.FirefoxOptions()
                #firefox_options.add_argument("-headless")
                firefox_options.set_preference("general.useragent.override", my_user_agent)
                # Criação do driver do navegador
                driver = webdriver.Firefox(options=firefox_options)    
            elif str.lower(self.navegador) == "edge":
                #informações do webdriver do modulo selenium
                # Configuração do navegador
                edge_options = webdriver.EdgeOptions()
                #edge_options.add_argument("-headless")
                edge_options.add_argument(f"user-agent={my_user_agent}")
                # Criação do driver do navegador
                driver = webdriver.Edge(options=edge_options)   
            else:
                raise ValueError("Navegador inválido. Escolha 'Chrome', 'Firefox' ou 'Edge'.")
            
            # Espera explícita para o carregamento da página (opcional, mas recomendado)
            driver.get(self.url)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Espera até que a tag <body> esteja presente

            return driver
        
        except ValueError as e:
            self.notifica_erro('erro', 'Robô raspagem', 'Criação de webdriver', str(e))
            sys.exit(str(e))
        
        except Exception as e:
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Não foi possível criar o webdriver - {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['geral_path'], 'Log_Execução.text')
            self.notifica_erro('erro', 'Robô raspagem', 'Criação de webdriver', mensagem_erro)
            sys.exit("Erro na criação do Driver")

    def encerra_driver(self):
        try:
            if self.driver:
                self.driver.quit()  # Usamos quit() para fechar todas as janelas e encerrar o driver
        except Exception as e:
            # Lida com erros durante o encerramento do driver
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro ao encerrar o driver: {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['geral_path'], 'Log_Execução.txt')

    def notifica_erro(self,tipo, app, titulo, mensagem):

        try:
             # Carrega as credenciais do Gmail
            with open(f'{self.pastas_arquivos["cred_path"]}credenciais_gmail.json') as File:
                creds = json.load(File)
            
            # Define o ícone de acordo com o tipo de notificação
            icon = self.pastas_arquivos['geral_path'] + ('check.png' if tipo == "pass" else 'close.png')

            # Conecta ao servidor SMTP do Gmail
            server = smtplib.SMTP(creds['host_name'],creds['port_num'])
            server.starttls()
            server.login(user=creds['username'],password=creds['password'])

            html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{self.bot} - {titulo}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); }}
                        h1 {{ color: #333333; }}
                        p {{ line-height: 1.6; }}
                        .footer {{ text-align: center; margin-top: 20px; color: #777777; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>{app}: {self.bot} - {titulo}</h1>
                        <p>{mensagem}</p>
                        <img src="cid:image1" alt="Ícone">  
                        <div class="footer">
                            <p>Esta é uma notificação automática. Por favor, não responda a este e-mail.</p>
                        </div>
                    </div>
                </body>
                </html>
            """
            # Cria a mensagem MIME
            email_msg = MIMEMultipart()
            email_msg['From'] = creds['username']
            email_msg['To'] = 'seu.nome@servidor.com'
            email_msg['Subject'] = f"{app}: {self.bot} - {titulo}"
            email_msg.attach(MIMEText(html,'HTML'))

            # Anexa o conteúdo HTML e a imagem
            email_msg.attach(MIMEText(html, 'html'))
            with open(icon, 'rb') as img:
                email_msg.attach(MIMEImage(img.read(),'png', nome='image1'))

            # Envia o e-mail
            server.sendmail(email_msg['From'],email_msg['To'],email_msg.as_string())
        
        except Exception as e:
            # Lida com erros de envio de e-mail
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro ao enviar notificação de erro: {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['geral_path'], 'Log_Execução.text')
        finally:
            # Garante que o servidor SMTP seja fechado, mesmo em caso de erro
            if server:
                server.quit()

    def gravalog(self,conteudo,path,arquivo):
        try:
            # Define o caminho completo do arquivo de log
            nome_arquivo = os.path.join(path, arquivo)

            # Verifica se o arquivo existe
            modo = 'a' if os.path.isfile(nome_arquivo) else 'w'  # 'a' para append, 'w' para escrever novo

            # Abre o arquivo no modo apropriado e escreve o conteúdo
            with open(nome_arquivo, modo, newline='', encoding='utf-8') as arquivo_log:
                arquivo_log.write(conteudo + '\n')

        except Exception as e:
            # Lida com erros de gravação em log
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro ao gravar log: {e}'
            print(mensagem_erro)  # Imprime o erro no console para depuração
            self.notifica_erro('erro', 'Robô Raspagem', 'Gravação de Log', mensagem_erro)

    def conecta_site(self):

        try:
            # Obtém as credenciais do usuário específico
            data = self.creds_site.get(self.usuario)
            if not data:
                raise ValueError(f"Credenciais não encontradas para o usuário: {self.usuario}")

            # Acessa a página de login do site
            self.driver.get('https://site.com.br/login/#/')

            try:
                botao = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')) 
                )
                # Se o botão for encontrado, clique nele
                botao.click()
                
                # Espera adicional após o clique (opcional, ajuste o tempo conforme necessário)
                time.sleep(2)  # Aguarda 2 segundos para a página carregar após o clique

            except TimeoutException:
                # Se o botão não aparecer em 10 segundos, ignore e continue
                print("Botão não encontrado. Continuando...")
            

            try:
                # Verifica qual versão da pagina de login
                self.driver.find_element(By.NAME, 'formularioLogin')
                version_login = 'old'
            except:
                version_login = 'new'

            if version_login == 'old':

                try:
                    # Encontrar o popup
                    iframe = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, 'beamerAnnouncementPopup')) 
                    )
                    # Se o popup for encontrado, entra nele
                    self.driver.switch_to.frame(iframe)
                    # encontrfa o botão e clica nele
                    botao_close = self.driver.find_element(By.CLASS_NAME, 'popupClose').click()
                    botao_close.click()
                    # volta para o conteudo default
                    self.driver.switch_to.default_content()

                except TimeoutException:
                    # Se o botão não aparecer em 10 segundos, ignore e continue
                    print("Botão fechar não encontrado. Continuando...")

                # Preenche os campos de login e senha e clica em "Entrar"                
                print("Pagina antiga")
                self.driver.find_element(By.ID, "login").send_keys(data['login'])
                self.driver.find_element(By.ID, "senha").send_keys(data['senha'])
                self.driver.find_element(By.NAME, "go").click()

            elif version_login == "new":

                url_atual = self.driver.current_url

                # Preenche os campos de login e senha e clica em "Entrar"
                print("Pagina nova")
                username_field = self.driver.find_element(By.ID, "username")
                username_field.send_keys(data['login'])

                password_field = self.driver.find_element(By.ID, "password")
                password_field.send_keys(data['senha'])

                form_login = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "kc-form-login"))
                )
                form_login.click()

                shadow_root = self.driver.execute_script("return document.querySelector('#kc-login').shadowRoot")
                login_button = shadow_root.find_element(By.CSS_SELECTOR, ".button--primary")
                login_button.click()

           
            # Espera explícita para garantir que o login foi bem-sucedido (opcional)
            WebDriverWait(self.driver, 5).until(
                EC.url_changes('https://site.com.br/login/#/')  # Verifica se a URL mudou após o login
            )

            return


        except ValueError as e:
            # Lida com o caso de credenciais inválidas
            self.notifica_erro('erro', 'Robô Raspagem', 'Conexão Site', str(e))
            sys.exit(str(e))

        except Exception as e:
            # Lida com outros erros de conexão
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Não foi possível conectar ao Site: {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.text')
            self.notifica_erro('erro', 'Robô Raspagem', 'Conexão Site', mensagem_erro)
            sys.exit()
    
    def desconecta_site(self):
        try:
            self.driver.get('https://site.com.br/sso/src/logout.php')

            # Espera explícita para garantir que o logout foi bem-sucedido (opcional)
            WebDriverWait(self.driver, 5).until(
                EC.url_changes('https://site.com.br/')  # Verifica se a URL mudou após o login
            )
            
        except Exception as e:
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Não foi possível desconectar do Site: {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.text')
            self.notifica_erro('erro', 'Robô Raspagem', 'Desconectar Site', mensagem_erro)
            self.encerra_driver()

    def process_json_files(self):
        # Data de duas semanas atrás
        two_weeks_ago = datetime.strptime((datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d'),'%Y-%m-%d')
        # DataFrame para armazenar os dados
        root_dir = self.pastas_arquivos['json_path']
        lista = []
        df = pd.DataFrame()

        # Percorre todas as subpastas no diretório raiz
        for subdir in os.listdir(root_dir):
            subdir_path = os.path.join(root_dir, subdir)
            
            # Verifica se é uma pasta e se a data é de até duas semanas atrás
            if os.path.isdir(subdir_path):
                try:
                    subdir_date = datetime.strptime(subdir, '%Y-%m-%d')
                    if subdir_date >= two_weeks_ago:
                        # Percorre todos os arquivos JSON na subpasta
                        for file in os.listdir(subdir_path):
                            if file.endswith('.json'):
                                file_path = os.path.join(subdir_path, file).replace('/','\\')
                                # Abre o arquivo JSON e adiciona ao DataFrame
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    lista.append(data)
                except ValueError:
                    print("erro leitura de arquivo")
                    pass  # Ignora a subpasta se não puder converter o nome para uma data

        df = pd.DataFrame(lista)
        # Retorna o DataFrame
        return df

    def remove_escape_sequences(self, text):
        if text is None or text == 0 or text == '':
            return None
        else:
            # Remove sequências de escape (como \n, \t, \r, etc.)
            text = re.sub(r'[\n\t\r\\\'"\b\f\v\0]', '', text)

            # Remove caracteres especiais
            text = ''.join(char for char in text if char.isalnum() or char.isspace())

            # Normaliza a string para remover acentos e caracteres especiais
            text = normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

            return text

    def salva_json(self, dado):

        try:
            
            # Extrai a data e o ID do frete do dado
            data = dado['data']
            id_frete = dado['id_frete']

            # Remove caracteres especiais e espaços da empresa
            empresa = self.remove_escape_sequences(dado['empresa'].replace(" ","-").replace("/","-"))

            # Cria o caminho completo para o arquivo JSON, usando a data como subpasta
            caminho_completo = os.path.join(self.pastas_arquivos['json_path'], data).replace('/',os.sep)

            # Cria o diretório se ele não existir
            os.makedirs(caminho_completo, exist_ok=True)

            # Define o nome do arquivo JSON
            nome_arquivo = f"site_{data}_{empresa}_{id_frete}.json"
            caminho_arquivo = os.path.join(caminho_completo, nome_arquivo)

            # Salva os dados em formato JSON no arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dado, arquivo, ensure_ascii=False, indent=4)  # Formatação para facilitar a leitura

        except Exception as e:
            id_frete = dado['id_frete']
            print(f'Raspagem anuncio {id_frete} não foi salva')
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro ao salvar arquivo JSON (ID {id_frete}): {e}'
            self.gravalog(mensagem_erro,self.pastas_arquivos['path_scraping'],'Log_Execução.text')
            self.notifica_erro('erro','Robô Raspagem','Salvamento de JSON',mensagem_erro)
            pass

    def captura_dados_iniciais(self, page):
        try:
            # Acessa a página
            self.driver.get(page)

            # Espera explícita (combinando as duas abordagens)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            #leitura do codigo html da pagina:
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extrai o número de anúncios
            anuncios_text = bs.find('h1', {'class': 'typography typography--body typography--body-md typography--neutral-strong sc-fuel-typography sc-fuel-typography-s'}).find('span').text
            anuncios = int(anuncios_text.replace('.', '')) if anuncios_text else 0

            # Calcula o número máximo de páginas
            try:
                max_page = int(bs.find('p',{'class':'typography typography--caption typography--neutral-default sc-fuel-typography sc-fuel-typography-s'}).text.split(" ")[1])
            except:
                max_page = ceil(anuncios / 20)

            return anuncios, max_page

        except AttributeError as e:
            # Lida com o caso de não encontrar os elementos esperados na página
            print(f'Erro ao capturar dados iniciais (URL: {page})')
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro ao capturar dados iniciais (URL: {page}): {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.txt')
            self.notifica_erro('erro', 'Robô Raspagem', 'Captura de Dados Iniciais', mensagem_erro)
            return None, None  # Retorna None para indicar que houve um erro
                    
        except Exception as e:
            # Lida com outros erros inesperados
            print(f'Erro inesperado ao capturar dados iniciais (URL: {page})')
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro inesperado ao capturar dados iniciais (URL: {page}): {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.txt')
            self.notifica_erro('erro', 'Robô Raspagem', 'Captura de Dados Iniciais', mensagem_erro)
            return None, None  # Retorna None para indicar que houve um erro

    def scrap_link(self, pages_url):

        try:        
            temp_ini = time.time()
            # Acessa a página
            self.driver.get(pages_url)
           # Espera explícita 1: Presença da tag <body>
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, 'a'))
            )

            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'grid-item'))
            )

            # Espera explícita 2: Estado do documento "complete" (via JavaScript)
            WebDriverWait(self.driver, 60).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Analisa o conteúdo da página com BeautifulSoup
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')

            list_url = [] 
            
            # Tenta encontrar os links usando o primeiro seletor CSS
            links = bs.find_all('fuel-grid-item', {'class': 'grid-item'})[3].find_all('a')
            
            if not links:
                # Se não encontrar, tenta usar o segundo seletor CSS
                links = bs.find('div', {'class': 'lista-resultado'}).find_all('a')
            
            # Extrai os links e IDs dos fretes
            for link in links:
                _url = link.attrs['href']
                id_frete = _url.split('/')[-2].rstrip('/')
                suffix = _url.replace(self.url, '').replace(id_frete+'/', '')
                list_url.append({'id_frete': id_frete, 'url_suffix':suffix})
            
            temp_fim = time.time()
            temp_exec = round(temp_fim - temp_ini, 3)
            print(f'Buscando Links {temp_exec}')
            
            return list_url
                     
        except Exception as e:
            # Lida com erros durante a raspagem dos links
            print(f'Erro ao raspar os links (URL: {pages_url})')
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - Erro ao raspar os links (URL: {pages_url}): {e}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.txt')
            self.notifica_erro('erro', 'Robô Raspagem', 'Captura dos links', mensagem_erro)
            return []  # Retorna uma lista vazia em caso de erro
            
    def scrape_data(self, page_url, id_frete):
        
        timer_inicio_raspagem = time.time()

        try:
            # Acessa a página
            self.driver.get(page_url)

            # Espera Explícita 1: Presença da tag <body>
            # WebDriverWait(self.driver, 60).until(
            #     EC.presence_of_element_located((By.TAG_NAME, 'body'))
            # )
            # Espera Explícita 2: Estado do documento "complete" (via JavaScript)
            WebDriverWait(self.driver, 60).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Analisa o conteúdo da página com BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
            frete = soup.find('div', {'class': 'site'})
            origem = frete.find('div', {'class': 'origem'}).find('span').text
            destino = frete.find('div', {'class':'destino'}).find('span').text
            data = frete.find('div', {'class': 'data-carga'}).find('span').text
            produto = frete.find('div', {'class':'carga-preco barra-vert triangulo'}).find('span', {'class':'frete-dados frete-carga'}).text
            preco_anun = frete.find('div', {'class':'carga-preco barra-vert triangulo'}).find('span', {'class' : 'frete-dados frete-preco'}).text
            veiculo = frete.find('span', {'class':'frete-dados frete-veiculos'}).text
            carroceria = frete.find('span', {'class':'frete-dados frete-carrocerias'}).text
            distancia = frete.find('span', {'class':'frete-dados frete-km'}).text
            especie = frete.find('span', {'class':'frete-dados frete-especie'}).text
            try:
                tipocarga = frete.find('div', {'class': 'quadro_esquerdo'}).find('span', {'class': 'frete-dados frete-complemento'}).text
            except:
                tipocarga = ""
            try:
                rastreamento = frete.find('div', {'class': 'quadro_esquerdo'}).find('span', {'class': 'frete-dados frete-rastreamento'}).text
            except:
                rastreamento = ""
            try:
                textervacao = frete.find('div', {'class': 'quadro_esquerdo'}).find('span', {'class': 'frete-dados frete-text'}).text
            except:
                textervacao = ""
            try:
                empresa = frete.find('div', {'class': 'quadro_esquerdo'}).find('div', {'class': 'total'}).find('span').find('a').text
            except:
                empresa = frete.find('div', {'class': 'quadro_esquerdo'}).find('div', {'class': 'total'}).find_all('a')[1].text

            try:
                peso_anunciado = ""
                dados_frete = frete.find('div', {'class': 'quadro_esquerdo'}).find_all('div',{'class':'detalhe-frete frt-details'})[1].find_all('div',{'class':'detalhe_item'})
                for n in dados_frete:
                    if n.find('strong').text.startswith('PESO TOTAL DA CARGA'):
                        peso_anunciado = n.find('span').text
                    else:
                        continue
            except:
                print('excecpt peso anunciado')
                peso_anunciado = ""

            lst_preco = preco_anun.split()
            preco = preco_anun.split()[0].replace('.', '').replace(',','.')

            unidade_preco = ''
            # Verifique se 'TON' está na lista
            if 'TON' in lst_preco:
                unidade_preco = 'P/ TON'
            else:
                unidade_preco = 'P/ VIAGEM'
            
            pedagio_preco = ''
            # Verifique se 'PED' está na lista
            if 'PED' in lst_preco:
                pedagio_preco = 'SIM'
            else:
                pedagio_preco = 'NÂO'

            dia, mes, ano = data.split('/')
            data = f'{ano}-{mes}-{dia}'

            empresa = empresa.replace("/","-")

            # lock.acquire()
            dados_frete = [{
                'id_frete': str(id_frete), 'data': data, 'origem': origem, 'destino': destino,
                'distancia': distancia, 'preco': preco, 'unidade_preco': unidade_preco, 'c_pedagio': pedagio_preco, 'empresa': empresa, 
                'veiculo': veiculo, 'carroceria': carroceria, 'produto': produto, 'especie': especie, 'Tipo de Carga': tipocarga,
                'Rastreamento': rastreamento, 'textervação': textervacao, 'Peso Anunciado': peso_anunciado
            }]

            timer_fim_raspagem = time.time()
            tempo_raspagem = round(timer_fim_raspagem - timer_inicio_raspagem, 3)
            print(f'Raspagem anuncio {id_frete} {tempo_raspagem}')

            return dados_frete

        except Exception as e:
            # Lida com erros durante a raspagem dos dados
            print(f'{id_frete} não raspado')
            quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_erro} - {id_frete} não raspado - {e}\n\n{page_url}'
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.txt')
            self.notifica_erro('erro', 'Robô Raspagem', 'Captura do anuncio', mensagem_erro)
            return {'id_frete': id_frete, 'erro': str(e)}  # Retorna um dicionário com o ID do frete e a mensagem de erro

    def executar_raspagem(self):
        try:
            print(datetime.now())
            tempo_inicio = time.time()
            quando_iniciado = datetime.now().strftime("%d/%m/%Y %H:%M")
            anuncios = 0
            baixados = 0
            amostra = 0
            erros_raspagem = []

            print("Captura das últimas extrações")
            tb_scraping = self.process_json_files()

            self.driver = self.cria_driver()

            print("Fazendo a conexão com o Site")
            self.conecta_site()

            for page in self.url_consulta:
                inicio_fluxo = time.time()

                qde_anuncios, num_paginas = self.captura_dados_iniciais(page)

                if qde_anuncios is None or num_paginas is None:
                    continue

                if qde_anuncios != 0:
                    max_page = min(num_paginas, self.paginas_busca)
                    print(f'Site novo, {max_page} páginas do fluxo')

                    for i in range(1, max_page):
                        print(page + str(i) + '/')

                        dict_url = self.scrap_link(page + str(i) + '/')
                        print(dict_url)
                        amostra += len(dict_url)
                        print(tb_scraping)

                        for link in dict_url:
                            print(link['id_frete'])
                            if (tb_scraping['id_frete'] == link['id_frete']).any():
                                baixados += 1
                                print("Anúncio já está na base!")
                            else:
                                print(self.url + link['url_suffix'] + link['id_frete'] + "/")
                                try:
                                    dados_frete = self.scrape_data(self.url + link['url_suffix'] + link['id_frete'] + "/", link['id_frete'])
                                    if isinstance(dados_frete, dict) and 'erro' in dados_frete:
                                        print("Sem dados para salvar")
                                        # erros_raspagem.append(dados_frete)
                                        continue
                                    else:
                                        self.salva_json(dados_frete[0])
                                        tb_scraping = pd.concat([tb_scraping, pd.DataFrame.from_dict(dados_frete)], ignore_index=True, sort=False)
                                        anuncios += 1
                                except Exception as e:
                                    print(f'Erro no link do anúncio {link["id_frete"]}')
                                    quando_erro = datetime.now().strftime("%d/%m/%Y %H:%M")
                                    mensagem_erro = f'{quando_erro} - Erro no link do anúncio {link["id_frete"]} - {e}'
                                    self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.txt')
                                    self.notifica_erro('erro', 'Robô Raspagem', 'Erro na raspagem', mensagem_erro)
                                    continue

                fim_fluxo = time.time()
                tempo_fluxo = round(fim_fluxo - inicio_fluxo, 3)
                print(f'Tempo de execução do fluxo {tempo_fluxo}')

            self.desconecta_site()
            self.encerra_driver()
            tempo_fim = time.time()
            tempo_execucao = round(tempo_fim - tempo_inicio, 3)
            print(f'Tempo raspagem {tempo_execucao}')
            quando_finalizado = datetime.now().strftime("%d/%m/%Y %H:%M")

            log_raspagem = f'Início: {quando_iniciado} | Fim: {quando_finalizado} | Total de links: {amostra} | Estão na base: {baixados} | Novos: {anuncios} | Tempo total: {tempo_execucao}s'
            self.gravalog(log_raspagem, self.pastas_arquivos['path_scraping'], 'Log_Raspagem.txt')

            if erros_raspagem:
                mensagem_erros = "\n".join([f"Erro ao raspar frete {erro['id_frete']}: {erro['erro']}" for erro in erros_raspagem])
                self.notifica_erro('erro', 'Robô Raspagem', 'Erros na Raspagem', mensagem_erros)

        except Exception as e:
            tempo_fim = time.time()
            tempo_execucao = round(tempo_fim - tempo_inicio, 3)
            print(f'Raspagem interrompida - Tempo raspagem {tempo_execucao}')
            quando_finalizado = datetime.now().strftime("%d/%m/%Y %H:%M")
            mensagem_erro = f'{quando_finalizado} - Raspagem interrompida - {e}'
            self.notifica_erro('erro', 'Robô Raspagem', 'Raspagem Interrompida', mensagem_erro)
            self.gravalog(mensagem_erro, self.pastas_arquivos['path_scraping'], 'Log_Execução.txt')





