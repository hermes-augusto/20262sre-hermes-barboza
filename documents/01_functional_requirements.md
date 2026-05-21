# Especificação de Requisitos Funcionais (RF) — Olist SRE Pipeline

## 1. Introdução
Este documento detalha os requisitos funcionais para o pipeline de dados da Olist, focando em garantir a confiabilidade, resiliência e transparência do processo de ETL (Extração, Transformação e Carga).

## 2. Metodologia
- **EARS (Easy Approach to Requirements Syntax):** Para redação clara e inequívoca.
- **Gherkin:** Para definição de critérios de aceitação.
- **MoSCoW:** Para priorização dos requisitos.

---

## 3. Detalhamento dos Requisitos

### RF-01: Ingestão de Arquivos CSV
- **Descrição EARS:** O sistema deve ingerir arquivos CSV brutos contendo pedidos do marketplace. (Ubíquo)
- **Atores:** Time de Dados, Sistema de Ingestão.
- **Pré-condições:** Arquivos CSV disponíveis no diretório de entrada.
- **Pós-condições:** Dados lidos e preparados para carga.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Ingestão bem-sucedida de arquivo válido
    Given um arquivo CSV válido no diretório de entrada
    When o processo de ingestão é iniciado
    Then os dados devem ser extraídos corretamente para processamento posterior
  ```
- **Prioridade:** Must (Essencial)

### RF-02: Carga de Dados no Postgres
- **Descrição EARS:** Quando os dados forem ingeridos, o sistema deve carregá-los no banco de dados Postgres (Stage). (Evento)
- **Atores:** Sistema de Carga.
- **Pré-condições:** Dados ingeridos com sucesso.
- **Pós-condições:** Dados persistidos na camada de stage do Postgres.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Carga de dados na camada de stage
    Given dados extraídos de um CSV
    When a tarefa de carga é executada
    Then os registros devem estar disponíveis na tabela de stage do Postgres
  ```
- **Prioridade:** Must (Essencial)

### RF-03: Transformação Analítica de Dados
- **Descrição EARS:** O sistema deve transformar os dados da camada de stage para o formato analítico. (Ubíquo)
- **Atores:** Time de Dados.
- **Pré-condições:** Dados disponíveis na camada de stage.
- **Pós-condições:** Tabelas analíticas populadas e prontas para consumo.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Processamento de transformações analíticas
    Given dados brutos na tabela de stage
    When o job de transformação é disparado
    Then os dados devem ser agregados e movidos para as tabelas analíticas
  ```
- **Prioridade:** Must (Essencial)

### RF-04: Idempotência no Reprocessamento
- **Descrição EARS:** Quando uma execução do pipeline for repetida para o mesmo período, o sistema deve garantir que o estado final seja idêntico ao de uma única execução bem-sucedida. (Evento)
- **Atores:** Time de SRE, Time de Dados.
- **Pré-condições:** Execução anterior (completa ou parcial) para o mesmo período.
- **Pós-condições:** Dados sem duplicidade ou inconsistência.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Reprocessamento de período já existente
    Given que um período já foi processado e carregado
    When o pipeline é executado novamente para o mesmo período
    Then o sistema deve limpar os dados antigos antes da carga ou ignorar duplicatas
    And o resultado final no dashboard deve ser o mesmo
  ```
- **Prioridade:** Must (Essencial)

### RF-05: Atualização de Dashboards (Grafana)
- **Descrição EARS:** Quando as transformações analíticas forem concluídas, o sistema deve disponibilizar os dados atualizados no Grafana. (Evento)
- **Atores:** Consumidores dos Dashboards.
- **Pré-condições:** Transformação concluída com sucesso.
- **Pós-condições:** Dashboards refletindo os dados mais recentes.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Visualização de dados atualizados
    Given que a transformação analítica terminou
    When o usuário acessa o dashboard no Grafana
    Then os números apresentados devem refletir a última carga realizada
  ```
- **Prioridade:** Must (Essencial)

### RF-06: Tratamento de Arquivos Inválidos/Corrompidos
- **Descrição EARS:** Se um arquivo CSV estiver parcial ou corrompido, o sistema deve registrar o erro e interromper a tarefa de ingestão específica. (Indesejado)
- **Atores:** Sistema de Ingestão, Time de SRE.
- **Pré-condições:** Arquivo CSV malformado detectado.
- **Pós-condições:** Erro logado e interrupção segura do processo.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Detecção de arquivo corrompido
    Given um arquivo CSV corrompido
    When o processo de ingestão tenta ler o arquivo
    Then o sistema deve gerar um log de erro detalhado
    And a execução daquele arquivo deve ser marcada como falha
  ```
- **Prioridade:** Should (Importante)

### RF-07: Monitoramento e Telemetria (SLA)
- **Descrição EARS:** O sistema deve fornecer telemetria (logs e métricas) sobre a saúde e performance do pipeline. (Ubíquo)
- **Atores:** Time de SRE.
- **Pré-condições:** Pipeline em execução.
- **Pós-condições:** Métricas visíveis nas ferramentas de observabilidade.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Monitoramento de duração do pipeline
    Given o pipeline iniciou uma execução
    When cada etapa (Ingestão, Carga, Transformação) termina
    Then o sistema deve emitir uma métrica de tempo de execução
  ```
- **Prioridade:** Must (Essencial)

### RF-08: Resiliência a Falhas de Infraestrutura
- **Descrição EARS:** Se ocorrer uma falha de infraestrutura (ex: queda de instância), o sistema deve permitir a retomada do processamento a partir de um estado íntegro. (Indesejado)
- **Atores:** Time de SRE, Infraestrutura.
- **Pré-condições:** Falha durante a execução do pipeline.
- **Pós-condições:** Pipeline reiniciado sem corrupção de dados.
- **Critérios de Aceitação (Gherkin):**
  ```gherkin
  Scenario: Retomada após queda de instância
    Given que o pipeline falhou no meio de uma transformação
    When o sistema é reiniciado
    Then o pipeline deve ser capaz de detectar o ponto de falha ou reiniciar de forma idempotente
  ```
- **Prioridade:** Should (Importante)

---

## 4. Tabela Resumo (MoSCoW)

| ID | Requisito Funcional | Ator Principal | Prioridade |
| :--- | :--- | :--- | :--- |
| RF-01 | Ingestão de Arquivos CSV | Time de Dados | Must |
| RF-02 | Carga de Dados no Postgres | Sistema | Must |
| RF-03 | Transformação Analítica | Time de Dados | Must |
| RF-04 | Idempotência no Reprocessamento | Time de SRE | Must |
| RF-05 | Atualização de Dashboards | Consumidor Final | Must |
| RF-06 | Tratamento de Arquivos Inválidos | Time de SRE | Should |
| RF-07 | Monitoramento e Telemetria | Time de SRE | Must |
| RF-08 | Resiliência a Falhas de Infra | Time de SRE | Should |

---

## 5. Riscos e Ambiguidades
1. **Definição de "Arquivo Corrompido":** É necessário definir tecnicamente o que invalida um arquivo (ex: colunas ausentes, tipos de dados errados, EOF prematuro).
2. **Janela de Processamento:** Não foi especificado o tempo máximo aceitável para o processamento dos 100 mil registros diários.
3. **Volume de Dados:** Embora 100 mil pedidos/dia seja o alvo, o sistema deve ser testado para picos sazonais (ex: Black Friday).
4. **Mecanismo de Retomada:** A estratégia exata de "checkpointing" ou limpeza prévia para garantir idempotência precisa de definição técnica no design do sistema.
