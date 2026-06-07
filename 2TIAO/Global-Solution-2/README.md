# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="../../assets/logo-fiap.png"
         alt="FIAP - Faculdade de Informática e Administração Paulista"
         width="40%">
  </a>
</p>

<br>

# AstroLens AI

## Nome do grupo

`PREENCHER: nome oficial do grupo`

## Integrantes

- `PREENCHER: nome, RM e link do LinkedIn do integrante 1`
- `PREENCHER: nome, RM e link do LinkedIn do integrante 2`
- `PREENCHER: nome, RM e link do LinkedIn do integrante 3`
- `PREENCHER: nome, RM e link do LinkedIn do integrante 4`
- `PREENCHER: nome, RM e link do LinkedIn do integrante 5`

## Professores

### Tutor(a)

- `PREENCHER: nome e link do tutor`

### Coordenador(a)

- `PREENCHER: nome e link do coordenador`

## Descrição

AstroLens AI é uma aplicação de inteligência artificial para análise de imagens
astronômicas e geração de relatórios científicos acessíveis. A solução combina
visão computacional multimodal, agentes especializados, consulta a fontes
astronômicas e uma interface interativa construída com Streamlit.

O fluxo principal começa com uma imagem enviada pelo usuário ou selecionada na
NASA Image and Video Library. O `VisionAgent`, apoiado pelo Gemini Vision,
classifica o objeto observado, estima a confiança da análise e identifica
objetos e tags científicas. Em seguida, o `ResearchAgent` consulta a base de
conhecimento local para recuperar definições, relevância científica,
contribuições para a exploração espacial e possíveis impactos na Terra. O
`ScienceWriterAgent` consolida essas informações em um relatório estruturado,
com resumo científico, importância para a exploração espacial, impacto
terrestre e curiosidades.

A página NASA Explorer permite pesquisar imagens reais da biblioteca pública da
NASA, visualizar os resultados e enviar uma imagem selecionada pelo mesmo
pipeline de análise. Os resultados de cada etapa são persistidos em JSON por
meio do `ResultStorageService`, permitindo auditoria e consulta posterior no
dashboard.

O projeto demonstra integração de IA generativa, visão multimodal, arquitetura
multiagente, consumo de API pública, persistência de resultados e comunicação
científica. Seu objetivo é aproximar conteúdos de astronomia do público e
evidenciar como tecnologias desenvolvidas para pesquisa espacial podem gerar
conhecimento e aplicações relevantes para a sociedade.

## Arquitetura da solução

```text
Imagem local ou NASA Image Library
              |
              v
         VisionAgent
              |
              v
        ResearchAgent
              |
              v
    ScienceWriterAgent
              |
              v
 ResultStorageService + Streamlit
```

A descrição detalhada dos módulos e contratos está em
[`docs/architecture.md`](docs/architecture.md).

## Estrutura de pastas

```text
Global-Solution-2/
├── README.md
├── app.py
├── requirements.txt
├── requirements-rag.txt
├── configs/
├── data/
│   ├── analysis_results/
│   ├── images/
│   └── knowledge_base/
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   ├── data-sources.md
│   ├── glossary.md
│   └── nasa_service.md
├── scripts/
├── src/
│   ├── agents/
│   ├── analytics/
│   ├── api/
│   ├── config/
│   ├── core/
│   ├── data/
│   ├── rag/
│   ├── reporting/
│   ├── services/
│   ├── storage/
│   ├── ui/
│   └── vision/
└── tests/
```

- **docs**: documentação técnica, arquitetura, fontes e planejamento.
- **src**: agentes, serviços, persistência e demais módulos da aplicação.
- **data**: imagens, base de conhecimento e resultados estruturados.
- **tests**: testes unitários dos serviços, agentes e armazenamento.
- **scripts**: testes de integração e utilitários de execução.
- **configs**: configurações auxiliares.
- **app.py**: ponto de entrada do dashboard Streamlit.

## Tecnologias utilizadas

- Python 3.11
- Streamlit 1.58
- Google Gemini API (`google-genai`)
- NASA Image and Video Library API
- Plotly
- `unittest`

## Como executar

### Pré-requisitos

- Python 3.11 ou compatível
- Chave válida para a API Gemini
- Acesso à internet para Gemini e NASA Image Library

### Instalação

```bash
cd 2TIAO/Global-Solution-2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` e informe:

```dotenv
GEMINI_API_KEY=sua_chave_gemini
```

### Dashboard

```bash
streamlit run app.py
```

A aplicação será disponibilizada normalmente em
`http://localhost:8501`.

### Testes unitários

```bash
python -m unittest discover -s tests -v
```

### Smoke test da NASA

```bash
python scripts/test_nasa_service.py
```

Esse teste realiza consultas reais para `andromeda`, `orion nebula` e
`jupiter`, valida os campos obrigatórios e verifica a disponibilidade das URLs
das imagens.

## Funcionalidades

- Upload e pré-visualização de imagens astronômicas.
- Classificação de galáxias, nebulosas, estrelas, aglomerados e planetas.
- Pesquisa de imagens na biblioteca pública da NASA.
- Pipeline multiagente para análise e geração de relatório.
- Persistência dos resultados de visão, pesquisa e redação científica.
- Consulta de análises anteriores.
- Exibição dos dados estruturados usados por cada agente.

## Links e observações

- **Repositório:** `PREENCHER: URL do repositório final`
- **Vídeo de apresentação:** `PREENCHER: URL do vídeo`
- **Aplicação publicada:** `PREENCHER: URL, se houver`
- **Documentação da NASA:** <https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf>

### Decisões técnicas

- A interface foi centralizada em Streamlit para permitir demonstração rápida
  do pipeline e inspeção dos resultados.
- Os agentes trocam estruturas tipadas para reduzir ambiguidades entre etapas.
- Os resultados são persistidos separadamente por imagem e por agente.
- O cliente NASA usa apenas a biblioteca padrão do Python, evitando uma
  dependência HTTP adicional.
- Segredos locais não devem ser versionados. O arquivo `.env.example` documenta
  apenas as variáveis necessárias.

## Histórico de lançamentos

- **1.0.0 - 06/06/2026**
  - Integração completa do pipeline multiagente.
  - Dashboard Streamlit e histórico de análises.
  - NASA Explorer com pesquisa e análise de imagens.
  - Persistência estruturada e testes automatizados.
- **0.5.0 - 01/06/2026**
  - Implementação inicial dos agentes e serviços Gemini.
- **0.1.0 - 01/06/2026**
  - Estrutura inicial e documentação de arquitetura.

## Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1">
<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">

Este trabalho acadêmico segue a licença
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
O modelo de organização foi baseado no
[template FIAP](https://github.com/SabrinaOtoni/TEMPLATE-FIAP-GRAD-ON-IA).
