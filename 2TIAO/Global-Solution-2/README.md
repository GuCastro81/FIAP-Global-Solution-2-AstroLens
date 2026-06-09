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

## Integrantes

- Amandha Nery - RM560030
- Gustavo Castro - RM560831
- Kild Fernandes - RM560615

## Professores

### Tutor(a)

- Leonardo Ruiz

### Coordenador(a)

- André Godoy

## Resumo executivo

AstroLens AI é uma plataforma inteligente para análise de imagens astronômicas e interpretação educacional de dados atmosféricos de exoplanetas. A solução utiliza IA Generativa, Visão Computacional e Sistemas Multiagentes para democratizar o acesso ao conhecimento astronômico, permitindo que usuários explorem imagens públicas da NASA, recebam classificações automáticas de objetos celestes e compreendam conceitos científicos por meio de relatórios em linguagem acessível.

O projeto também incorpora um módulo dedicado à interpretação de visualizações científicas do James Webb Space Telescope (JWST), com foco no exoplaneta K2-18 b. Esse recurso demonstra como dados de missões espaciais podem ser transformados em comunicação científica, apoiando educação, divulgação astronômica e interesse social por exploração espacial.

AstroLens AI posiciona a tecnologia como ponte entre pesquisa científica e sociedade. Ao automatizar etapas de análise, recuperação de conhecimento e geração textual, a plataforma facilita o entendimento de fenômenos astronômicos complexos e reforça o papel da inteligência artificial como ferramenta de apoio à educação, ciência cidadã e exploração do espaço.

## Descrição da solução

AstroLens AI é uma aplicação desenvolvida em Python com interface Streamlit para análise inteligente de dados astronômicos. A plataforma integra:

- IA Generativa para criação de explicações científicas.
- Visão Computacional com Gemini Vision para análise de imagens.
- Arquitetura multiagente para separação de responsabilidades.
- Recuperação de conhecimento científico em estilo RAG.
- Geração de linguagem natural para relatórios educacionais.
- APIs públicas de dados espaciais.
- Dados da NASA e visualizações do JWST.
- Geração opcional de conceitos artísticos de exoplanetas com Google Imagen.
- Comunicação científica voltada ao público acadêmico e educacional.
- Pipelines de dados com persistência estruturada em JSON.

O fluxo principal permite que o usuário envie uma imagem astronômica ou selecione um recurso da NASA Image and Video Library. Em seguida, agentes especializados classificam o objeto observado, recuperam conhecimento científico de uma base curada, geram um relatório explicativo e armazenam os resultados para consulta posterior.

Além do pipeline de imagens astronômicas, o projeto inclui um módulo independente chamado Exoplanet Atmosphere Visualizer, responsável por interpretar uma visualização publicada sobre a composição atmosférica do exoplaneta K2-18 b. Após a análise, o módulo gera um prompt científico aprimorado e pode criar uma imagem de conceito artístico com Google Imagen, quando o recurso está disponível para a chave configurada. O módulo não realiza medições científicas reais nem ajuste espectral; seu objetivo é demonstrar interpretação educacional baseada em dados científicos publicados.

## Arquitetura da solução

A arquitetura do AstroLens AI foi organizada em módulos independentes, mantendo baixo acoplamento entre interface, agentes, serviços externos, recuperação de conhecimento e persistência.

```text
Dados NASA/JWST ou imagem enviada pelo usuário
                |
                v
        Interface Streamlit
                |
                v
     Orquestração Multiagente
                |
   +------------+-------------+
   |                          |
   v                          v
Pipeline de Imagens     Visualizador de Exoplanetas
   |                          |
   v                          v
VisionAgent             ExoplanetSpectrumAgent
   |                          |
   v                          v
ResearchAgent           ExoplanetReporter
   |                          |
   v                          v
ScienceWriterAgent      ArtistConceptPromptEnhancer
                              |
                              v
                       ImageGenerationAgent
                |
                v
     ResultStorageService
                |
                v
      Dashboard e histórico
```

### Módulo 1: NASA Explorer

O NASA Explorer permite consultar a NASA Image and Video Library, visualizar resultados reais da base pública da NASA e encaminhar imagens selecionadas para o pipeline de análise astronômica. Esse módulo demonstra integração com API pública, consumo de dados espaciais e aplicação prática de IA sobre acervos científicos.

### Módulo 2: Análise de Imagens Astronômicas

Esse módulo executa o pipeline principal do AstroLens AI. Uma imagem local ou uma imagem obtida via NASA Explorer é processada pelo `VisionAgent`, enriquecida pelo `ResearchAgent` e convertida em relatório pelo `ScienceWriterAgent`.

### Módulo 3: Exoplanet Atmosphere Visualizer

Módulo independente para interpretação educacional da visualização atmosférica do exoplaneta K2-18 b baseada em dados do JWST. Ele utiliza o `ExoplanetSpectrumAgent` para identificar informações visíveis no gráfico, o `ExoplanetReporter` para gerar uma explicação estruturada e o `ArtistConceptPromptEnhancer` para produzir um prompt visual com restrições científicas. Opcionalmente, o `ImageGenerationAgent` envia esse prompt ao Google Imagen, exibe o resultado no dashboard e disponibiliza o arquivo PNG para download.

### Módulo 4: Knowledge Base / Scientific Retrieval Layer

Camada de recuperação de conhecimento científico composta por arquivos curados em `data/knowledge_base/`. Essa base fornece contexto astronômico para a geração de explicações, seguindo princípios de Retrieval-Augmented Generation.

### Módulo 5: Multi-Agent Orchestration

A orquestração multiagente separa tarefas de visão, pesquisa, redação e interpretação de exoplanetas. Essa divisão reduz ambiguidades, melhora a rastreabilidade dos resultados e permite evolução independente de cada componente.

A descrição técnica detalhada também está disponível em [`docs/architecture.md`](docs/architecture.md).

## Sistema Multiagente

| Agente                   | Responsabilidade                                                     | Entrada                                    | Saída                                                                                      |
| ------------------------ | -------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `VisionAgent`            | Classificar imagens astronômicas usando Gemini Vision.               | Imagem local ou imagem obtida da NASA.     | Classe astronômica, confiança, descrição, objetos e tags científicas.                      |
| `ResearchAgent`          | Recuperar conhecimento científico da base curada.                    | Resultado do `VisionAgent`.                | Definição, importância científica, relevância para exploração espacial e impacto na Terra. |
| `ScienceWriterAgent`     | Gerar relatório científico em linguagem acessível.                   | Saídas do `VisionAgent` e `ResearchAgent`. | Resumo científico, importância espacial, impacto e curiosidades.                           |
| `ExoplanetSpectrumAgent` | Interpretar a visualização atmosférica de K2-18 b com Gemini Vision. | Gráfico `atmosphere_composition.jpg`.      | JSON com planeta, tipo, moléculas detectadas, confiança e resumo.                          |
| `ImageGenerationAgent`   | Gerar opcionalmente um conceito artístico com Google Imagen.         | Prompt aprimorado, estilo e prompt negativo. | Arquivo PNG ou retorno estruturado informando indisponibilidade.                         |

## Arquitetura de Recuperação de Conhecimento (RAG)

O AstroLens AI adota princípios de Retrieval-Augmented Generation. Antes de gerar explicações finais, o `ResearchAgent` consulta uma base de conhecimento astronômica curada, localizada em `data/knowledge_base/`.

Essa etapa reduz a dependência exclusiva do modelo generativo e fornece contexto científico estruturado para o `ScienceWriterAgent`. Na prática, o sistema recupera informações relevantes sobre galáxias, nebulosas, estrelas, aglomerados e planetas antes da geração textual.

```text
Classificação do VisionAgent
          |
          v
Busca na base de conhecimento
          |
          v
Contexto científico recuperado
          |
          v
Geração aumentada por recuperação
```

## Visualizador de Atmosferas de Exoplanetas

O Exoplanet Atmosphere Visualizer é um módulo educacional dedicado ao exoplaneta K2-18 b, um objeto de grande interesse em estudos de atmosferas planetárias fora do Sistema Solar.

O módulo utiliza a imagem:

```text
data/images/exoplanets/k2-18b/atmosphere_composition.jpg
```

A visualização contém informações associadas à composição atmosférica observada em dados publicados do JWST. O sistema interpreta os rótulos presentes no gráfico, incluindo:

- Methane, ou metano.
- Carbon Dioxide, ou dióxido de carbono.
- Dimethyl Sulfide, ou sulfeto de dimetila.

O objetivo é gerar uma interpretação científica educacional, um relatório estruturado e um prompt de conceito artístico com restrições científicas e elementos visuais a evitar. Quando a API e a configuração da conta permitem acesso ao Google Imagen, o usuário também pode gerar, visualizar e baixar um conceito artístico em PNG. Se a geração não estiver disponível, o dashboard preserva o prompt aprimorado para uso manual sem interromper a análise. O sistema não realiza cálculo espectral, ajuste de picos, estimativa de abundância química nem validação científica independente.

## Pipeline de Dados

```text
NASA/JWST Data
      ↓
Vision Analysis
      ↓
Knowledge Retrieval
      ↓
Scientific Interpretation
      ↓
Report Generation
      ↓
Dashboard
```

| Etapa                     | Descrição                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| NASA/JWST Data            | Dados públicos da NASA, imagens astronômicas e visualização atmosférica do JWST.         |
| Vision Analysis           | Análise visual com Gemini Vision para classificação ou extração de informações visíveis. |
| Knowledge Retrieval       | Recuperação de conteúdo científico em base local curada.                                 |
| Scientific Interpretation | Interpretação educacional dos resultados por agentes especializados.                     |
| Report Generation         | Geração de relatórios em linguagem natural com tom científico.                           |
| Dashboard                 | Apresentação interativa, histórico e inspeção dos JSONs estruturados.                    |

## Tecnologias e conceitos FIAP implementados

| Conceito               | Status                  | Aplicação no projeto                                                            |
| ---------------------- | ----------------------- | ------------------------------------------------------------------------------- |
| IA Generativa          | ✔ Implementado          | Geração de relatórios científicos e explicações educacionais.                   |
| Visão Computacional    | ✔ Implementado          | Análise de imagens astronômicas e gráfico atmosférico.                          |
| Sistemas Multiagentes  | ✔ Implementado          | Agentes especializados para visão, pesquisa, redação e exoplanetas.             |
| NLP                    | ✔ Implementado          | Geração e estruturação de linguagem natural.                                    |
| RAG                    | ✔ Implementado          | Recuperação de conhecimento científico antes da geração textual.                |
| APIs Cognitivas        | ✔ Implementado          | Integração com Google Gemini.                                                   |
| Integração de APIs     | ✔ Implementado          | Consumo da NASA Image and Video Library API.                                    |
| Pipeline de Dados      | ✔ Implementado          | Fluxo completo de entrada, análise, interpretação, persistência e visualização. |
| Computação em Nuvem    | ✔ Arquitetura preparada | Aplicação preparada para deploy em ambiente cloud.                              |
| Exploração Espacial    | ✔ Implementado          | Uso de dados NASA e visualização baseada em JWST.                               |
| Comunicação Científica | ✔ Implementado          | Relatórios educacionais e linguagem acessível.                                  |

## Funcionalidades

- Upload e pré-visualização de imagens astronômicas.
- Classificação de galáxias, nebulosas, estrelas, aglomerados e planetas.
- Pesquisa de imagens na biblioteca pública da NASA.
- Pipeline multiagente para análise e geração de relatório.
- Recuperação de conhecimento científico em base curada.
- Persistência dos resultados de visão, pesquisa, relatório e exoplanetas.
- Consulta de análises anteriores.
- Exibição dos dados estruturados usados por cada agente.
- Visualizador educacional de atmosfera do exoplaneta K2-18 b.
- Geração e inspeção de prompt aprimorado, restrições científicas e prompt negativo.
- Geração opcional de conceito artístico de exoplaneta com Google Imagen.
- Pré-visualização e download da imagem gerada em formato PNG.
- Tratamento de indisponibilidade da geração de imagens sem interromper o fluxo.

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
│   ├── generated_images/
│   ├── images/
│   │   └── exoplanets/
│   │       └── k2-18b/
│   └── knowledge_base/
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   ├── data-sources.md
│   ├── glossary.md
│   ├── nasa_service.md
│   └── exoplanet_visualizer.md
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

- **docs**: documentação técnica, arquitetura, fontes, planejamento e módulo de exoplanetas.
- **src**: agentes, serviços, persistência, RAG, relatórios e demais módulos da aplicação.
- **data**: imagens, base de conhecimento, gráfico de K2-18 b, resultados estruturados e conceitos artísticos gerados.
- **tests**: testes unitários dos serviços, agentes, relatórios e armazenamento.
- **scripts**: testes de integração, smoke tests e utilitários de execução.
- **configs**: configurações auxiliares.
- **app.py**: ponto de entrada do dashboard Streamlit.

## Tecnologias utilizadas

| Tecnologia                         | Uso                                                  |
| ---------------------------------- | ---------------------------------------------------- |
| Python 3.11                        | Linguagem principal da solução.                      |
| Streamlit 1.58                     | Interface web e dashboard interativo.                |
| Google Gemini API (`google-genai`) | IA generativa, visão multimodal, geração textual e acesso opcional ao Imagen. |
| NASA Image and Video Library API   | Pesquisa e uso de imagens astronômicas públicas.     |
| Plotly                             | Base para visualizações e evolução analítica.        |
| `unittest`                         | Testes automatizados.                                |
| JSON                               | Persistência estruturada dos resultados dos agentes. |

## Como executar

### Pré-requisitos

- Python 3.11 ou compatível.
- Chave válida para a API Gemini.
- Acesso à internet para Gemini e NASA Image Library.

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

A aplicação será disponibilizada normalmente em:

```text
http://localhost:8501
```

### Testes unitários

```bash
python -m unittest discover -s tests -v
```

### Smoke test da NASA

```bash
python scripts/test_nasa_service.py
```

Esse teste realiza consultas reais para `andromeda`, `orion nebula` e `jupiter`, valida os campos obrigatórios e verifica a disponibilidade das URLs das imagens.

### Smoke test do Exoplanet Atmosphere Visualizer

```bash
python scripts/test_exoplanet_agent.py
```

Esse teste carrega `data/images/exoplanets/k2-18b/atmosphere_composition.jpg`, executa o `ExoplanetSpectrumAgent`, salva o resultado pelo `ResultStorageService` e imprime o JSON estruturado.

### Smoke test da geração opcional de imagem

```bash
python scripts/test_image_generation_agent.py
```

Esse teste monta um relatório de K2-18 b, aprimora o prompt de conceito artístico e tenta gerar uma imagem com Google Imagen. O resultado é impresso em JSON e informa `generated` ou `unavailable`, sem exigir uma API OpenAI.

## Persistência de resultados

Os resultados são armazenados pelo `ResultStorageService` seguindo a convenção:

```text
data/analysis_results/<nome_da_imagem>/
```

Cada agente salva sua saída em arquivo JSON separado, permitindo auditoria, rastreabilidade e consulta posterior no dashboard.

## Links e observações

- **Repositório:** `PREENCHER: URL do repositório final`
- **Vídeo de apresentação:** `PREENCHER: URL do vídeo`
- **Aplicação publicada:** `PREENCHER: URL, se houver`
- **Documentação da NASA:** <https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf>

### Decisões técnicas

- A interface foi centralizada em Streamlit para permitir demonstração rápida do pipeline e inspeção dos resultados.
- Os agentes trocam estruturas tipadas para reduzir ambiguidades entre etapas.
- Os resultados são persistidos separadamente por imagem e por agente.
- O cliente NASA usa apenas a biblioteca padrão do Python, evitando uma dependência HTTP adicional.
- O módulo de exoplanetas foi mantido isolado para não interferir no pipeline original de análise de imagens.
- A geração de imagens é opcional e retorna um estado estruturado de indisponibilidade quando o modelo, a chave ou a conta não oferecem acesso ao Imagen.
- Imagens geradas são armazenadas localmente em `data/generated_images/` e podem ser baixadas pelo dashboard.
- Segredos locais não devem ser versionados. O arquivo `.env.example` documenta apenas as variáveis necessárias.

## Trabalhos futuros

1. Integração com mais datasets do JWST.
2. Expansão da base de conhecimento astronômica.
3. Deploy em cloud pública.
4. Simulações avançadas de atmosferas.
5. Persistência de metadados e histórico das imagens geradas.

### Aplicações Futuras de Computação Quântica

As aplicações abaixo são conceituais e não estão implementadas nesta versão do projeto.

- **Simulação de atmosferas de exoplanetas:** uso futuro de métodos quânticos ou híbridos para explorar modelos atmosféricos complexos.
- **Modelagem do interior de estrelas de nêutrons:** investigação conceitual de algoritmos quânticos aplicados a estados extremos da matéria.
- **Otimização de cálculos astrofísicos complexos:** apoio a busca de parâmetros, seleção de modelos e problemas de otimização de grande escala.
- **Apoio a futuras missões espaciais:** estudo de técnicas quânticas para planejamento, análise de dados e simulações em contextos de exploração espacial.

## Histórico de lançamentos

- **1.2.0 - 09/06/2026**
  - Inclusão do `ImageGenerationAgent` com Google Imagen.
  - Geração opcional, pré-visualização e download de conceitos artísticos.
  - Tratamento resiliente para contas sem acesso à geração de imagens.
  - Inclusão de testes unitários e smoke test específico.
- **1.1.0 - 07/06/2026**
  - Inclusão do Exoplanet Atmosphere Visualizer.
  - Interpretação educacional do gráfico atmosférico de K2-18 b.
  - Geração de relatório e prompt de conceito artístico.
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
