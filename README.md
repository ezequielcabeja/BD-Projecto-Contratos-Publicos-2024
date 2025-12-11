# Base de Dados de Contratos Públicos
Este projeto foi desenvolvido como parte da disciplina Base de Dados do curso de Ciência de Computadores e de Inteligência Artificial e Ciência de Dados da Faculdade de Ciências da Universidade do Porto. O objetivo foi modelar, povoar e interagir com uma base de dados de contratos públicos, seguindo boas práticas de modelagem e normalização.

![alt text](images/image.png)

## Objetivo
O projeto é uma oportunidade de experimentação das matérias expostas na unidade curricular, em particular a especificação de um modelo ER e respectiva tradução para um modelo relacional e a criação, o povoamento e a interrogação de uma BD (Base de Dados) utilizando a linguagem SQL, a partir de um dataset em Excel (.xslx).

## Tecnologias Utilizadas
- SQLite: Banco de dados utilizado.
- SQLite3: Biblioteca para interação com o SQLite.
- Flask: Framework para criação da interface web.

## Funcionalidades
### Modelagem de Dados:
- Diagramas ER
- Modelo relacional

Seguindo os padrões da 3ª Forma Normal (3ªFN).

### Povoamento:
- Dados gerados e inseridos automaticamente na BD usando Python, através das bibliotecas sqlite3, pandas e re.

### Consultas SQL:
- 10 perguntas organizadas em 3 níveis de dificuldade (Fáceis, Médias e Díficeis).

### Interface Web:
- Pesquisa de contratos públicos por ID.
![alt text](images/image-1.png)
- Visualização das perguntas.
![alt text](images/image-2.png)


## Estrutura do Projeto 
```
/pasta-do-projeto
├── /data
│   ├── ContratosPublicos2024.txt     # Informações sobre o dataset
│   └── ContratosPublicos2024.xlsx    # Dataset utilizado     
├── /images                           # Imagens usadas no README
│   ├──image.png
│   ├──image-1.png
│   └──image-2.png
├── /interface      
│   ├── app.py                        # Aplicação Flask
│   ├──contratos_publicos.db          # BD gerada 
│   ├── db.py                         # Conexão com a base de dados
│   └── server.py                     # Servidor do projeto
├── /modelagem
│   ├── Contratos_Publicos.drawio     # Modelo ER
├── /povoamento
│   ├── Scheme.py                     # Script para criar as tabelas
│   └── Seed.py                       # Script para povoamento automatico do banco de dados
├── /static
│   ├──style.css
├── /templates                         # Templates HTML
│   ├── base.html
│   ├── contrato.html
│   ├── contratos.html
│   ├── index.html
│   ├── Q1.html
|   |   ...   
│   └── Q10.html
|── README.md                         # Este arquivo
|── README.html                       # Versão HTML deste arquivo
|── Relatorio.docx                    # Relatório do projeto
└── style.css
```

## Como Executar
### Pré-requisitos
- Python 3.10 ou superior
- SQLite instalado

### Passo a Passo
1. Clone o Repositório:
  - Baixe pelo link https://github.com/vituvvl/BD-Projecto-Contratos-Publicos-2024.git
  - Extraia o .zip e entre no diretório
    ```
    cd BD-Projecto-Contratos-Publicos-2024
    ```

2.  Instale as Bibliotecas Necessárias:
    ```
    pip install pandas flask openpyxl
    ```

3. Criação e Povoamento do Banco de Dados:
    - Criar a base de dados: 
    ```
    python povoamento/Scheme.py
    ```
    - Popular a base de dados:
    ```
    python povoamento/Seed.py
    ```

4. Entre no diretório da interface:
    ```
    cd ./interface
    ```

5. Inicie a Interface Web:
    ```
    python server.py
    ```
A aplicação estará disponível no navegador através do endereço http://127.0.0.1:9000

## Participantes do Projeto 
- [Victor de Vargas Lopes](https://github.com/vituvvl) (up202400863)
- [Ezequiel Tchimbaya Cachapeu Paulo](https://github.com/ezequielcabeja) (up202400891)
- [Sérgio Gomes Pinto](https://github.com/sergiogp12) (up202309160)

