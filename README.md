# Webscraping personalizado


## Problemas de negocio
* Falta de dados para auxiliar na tomada de decisões:
** Falta de informações relevantes para auxiliar na tomada de decisões.
* Visão momentânea do site.com.br: 
** Por se tratar de um site dinâmico, com muitos in e out das informações, não se tinha uma visão dos dados que haviam sido ocultos, desta forma a visão dos dados era do momento que se abria o site.
* Necessidade de visualizar outros períodos:
** Havia uma necessidade real de se visualizar os dados que haviam sido ocultos no site.com.br. Esses dados eram fundamentais para tomadas de decisão 





## Solução adotada

Para sanar essas dores, foi criado um webscraping, que rodava a cada hora no site, coletando as informações divulgadas. A raspagem dos dados foi automatizada através de um script pyhton, e programada uma execução via cron do sistema operacional.

Esse script capturava dado por dado e registrava em arquivos JSON separados, esse procedimento foi tomado para se guardar a informação original (RAW), com ocada informação havia uma data de publicação, os arquivos eram separados por data, sendo organizados numa estrutura que cada pasta era de um dia de extração. Uma particularidade, que as informações antigas ainda poderiam ser exibidas, assim, o script verificava se o dado já havia sido baixado, caso sim, o ignorava.

Esse BOT rodou por mais de um ano, conseguindo capturar mais de 400mil informações diferentes, e num segundo processo era realizado o ETL das informações, limpando dados inconsistentes, tratando, agregando outras informações, e melhorando a qualidade do dado.
