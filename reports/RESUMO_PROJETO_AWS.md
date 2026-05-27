# Relatório de Implementação: Pipeline de Dados SRE na AWS

Este documento resume a transição do ambiente de desenvolvimento local para uma infraestrutura profissional na nuvem AWS, utilizando boas práticas de SRE e Engenharia de Dados.

---

## 1. Visão Geral da Solução

A solução consiste em um pipeline de dados ponta a ponta que ingere dados brutos do **Amazon S3**, processa-os em um banco de dados analítico de alta performance (**ClickHouse**) e visualiza os resultados em um dashboard interativo (**Streamlit**), tudo orquestrado via **Docker** em uma instância **EC2**.

### Componentes Principais:
*   **Armazenamento**: AWS S3 (Substituindo o MinIO local).
*   **Processamento/Banco**: ClickHouse (Rodando em container Docker).
*   **Visualização**: Streamlit Dashboard (Python).
*   **Infraestrutura**: AWS EC2 (t3.medium) provisionada via CloudFormation.
*   **Segurança**: IAM LabRole (acesso sem chaves fixas).

---

## 2. Pontos Chave da Arquitetura

1.  **Infraestrutura como Código (IaC)**: Todo o provisionamento é automatizado, garantindo que o ambiente possa ser destruído e recriado sem perda de configuração.
2.  **Segurança Nativa (IAM)**: A instância EC2 utiliza um `Instance Profile` vinculado à `LabRole`. Isso permite que o ClickHouse e o Ingestor leiam do S3 usando permissões temporárias automáticas, eliminando o risco de vazar credenciais.
3.  **Ingestão de Alta Performance**: Utilizamos a função nativa `s3()` do ClickHouse, que permite ao banco de dados "puxar" os dados diretamente do S3 para a memória/disco com latência mínima.
4.  **Automação de Subida (UserData)**: O script de UserData automatiza a instalação de dependências (Docker, Git) e prepara os arquivos de ambiente (`.env`) no primeiro boot da máquina.

---

## 3. Guia de Replicação (Prompts Sugeridos)

Para replicar este projeto do zero, você pode utilizar a seguinte sequência de comandos/prompts com um assistente de IA:

### Passo 1: Configuração Inicial
> "Configure meu ambiente de trabalho com as seguintes credenciais de AWS Student Lab: [Cole suas credenciais aqui]. Certifique-se de atualizar o arquivo .env e o config do AWS CLI."

### Passo 2: Geração da Infraestrutura
> "Com base no meu docker-compose.yml atual, crie um template CloudFormation para AWS. O template deve:
> 1. Criar um Bucket S3 para os CSVs.
> 2. Criar uma EC2 t3.medium com Security Group liberando portas 22, 8123 e 8501.
> 3. Usar a LabRole pré-existente para permissões de IAM.
> 4. No UserData, instalar Docker e preparar a pasta /home/ec2-user/app com o .env correto."

### Passo 3: Deploy e Setup do App
> "Execute o deploy do stack no CloudFormation. Após a subida, acesse a instância via SSH e realize o build da imagem Docker do Streamlit, configurando o docker-compose para usar as credenciais 'dashboard'/'dashboard' no ClickHouse."

### Passo 4: Gatilho do Pipeline (Ingestão)
> "Agora que o ambiente está pronto, dispare a ingestão dos dados. Use comandos 'docker exec' no ClickHouse para criar tabelas que apontem diretamente para os arquivos CSV no S3: `SELECT * FROM s3('url-do-bucket/arquivo.csv', 'CSVWithNames')`."

---

## 4. Detalhes Técnicos da Instalação Atual

*   **URL do Dashboard**: `http://98.92.240.221:8501`
*   **Portas Ativas**: 22 (SSH), 8123 (ClickHouse HTTP), 9000 (ClickHouse Native), 8501 (Streamlit).
*   **Credenciais do Banco**:
    *   **Usuário**: `dashboard`
    *   **Senha**: `dashboard`
    *   **Banco**: `olist`
*   **Caminho dos Arquivos na EC2**: `/home/ec2-user/app/`

---

## 5. Próximos Passos (SRE Roadmap)

- [ ] **Configurar Backups**: Criar um cronjob para snapshots do EBS da EC2.
- [ ] **Monitoramento**: Instalar o CloudWatch Agent para alertas de consumo de memória.
- [ ] **DNS**: Mapear o IP para um nome amigável (ex: via DuckDNS ou Route53).
