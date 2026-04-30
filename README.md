# TeamsReaver: Teams Forensic Investigation & Data Export Tool

**TeamsReaver** é uma ferramenta de perícia computacional e exfiltração de dados desenvolvida para análise, busca e extração automatizada de informações do Microsoft Teams através da Microsoft Graph API.

## Funcionalidades Principais

A ferramenta oferece três modos principais de operação para investigações:

*   **Busca por Termos com Extração de Contexto:** Ao realizar uma busca por termos (ex: `apikey`, `secretkey`, `password`), a ferramenta não extrai apenas a mensagem isolada. Caso um "match" seja encontrado, o histórico completo daquela conversa é baixado automaticamente para que o analista tenha o contexto total da exposição.
*   **Extração Completa 1:1:** Permite baixar todo o histórico de mensagens e arquivos trocados entre dois usuários específicos, sendo ideal para investigações direcionadas de conduta ou vazamento de informações.
*   **Flexibilidade de Varredura Temporal:**
    *   **Deep Sweep (Padrão):** Se nenhum filtro de data for aplicado, a ferramenta realiza uma varredura completa desde a primeira mensagem do usuário.
    *   **Fast Search (`-Fast`):** Varredura focada nos últimos X dias.
    *   **Data Específica (`-Date`):** Alvo em um dia exato de incidente.

## Público-Alvo e Casos de Uso

1.  **Defensivo (Hunting, CTI, DLP e Blue Team):** Projetado para investigações onde o Microsoft Purview se mostra limitado. O Purview pode levar horas para processar buscas e frequentemente entrega resultados fragmentados. O TeamsReaver entrega os dados de forma imediata, organizada em pastas e com todos os anexos vinculados.
2.  **Ofensivo (Pentesters e Red Teamers):** Essencial em cenários de Cloud Pentest. Se uma Enterprise Application for comprometida com permissões de leitura, a ferramenta permite exfiltrar comunicações sensíveis de forma rápida e silenciosa.

## Como Utilizar

### Exemplos Práticos

```bash
# Busca por múltiplos termos sensíveis em um alvo (Ex: Hunting de credenciais)
python TeamsReaver.py -TargetUPN usuario -SearchTerms "apikey","secretkey","access_token","password","senha_servidor"

# Extração total de histórico entre dois alvos (Ex: Investigação de fraude)
python TeamsReaver.py -TargetUPN alvo_principal -TargetTwo cumplice

# Investigação de incidente ocorrido na última semana
python TeamsReaver.py -TargetUPN usuario -SearchTerms "vazamento","confidencial" -Fast 7

# Busca em uma data específica de um log de acesso
python TeamsReaver.py -TargetUPN usuario -SearchTerms "login" -Date "29/04/2026"
```

## Configuração de Permissões (Microsoft Graph)

A ferramenta requer permissões de nível de **Application** no Microsoft Graph:

### Módulo de Mensagens
*   `User.Read.All`: Mapeamento de usuários.
*   `Chat.Read.All`: Leitura de históricos de chat.

### Módulo de Arquivos e Anexos
*   `Files.Read.All`: Download de anexos.
*   `Sites.Read.All`: Acesso a arquivos em canais/SharePoint.
*   `Group.Read.All`: Metadados de grupos.

**Nota sobre acessos:**
*   Se possuir apenas `Chat.Read.All`, a ferramenta extrairá todos os textos, mas não baixará os arquivos.
*   Caso tenha apenas acesso a arquivos (`Files.Read.All`) sem acesso aos chats, utilize a ferramenta **GraphDump** ([LINK_AQUI]).

## Instalação e Configuração Inicial

1.  **Requisitos:** Python 3.8+
2.  **Dependências:** No terminal, execute `pip install -r requirements.txt`.
3.  **Configuração Facilitada (Auto-Setup):** 
    Na primeira execução, se a ferramenta não encontrar o arquivo `.reaverconf`, ela iniciará um **modo interativo** no terminal solicitando o `Client ID`, `Secret`, `Tenant ID` e o `Domínio Padrão`. O arquivo será criado automaticamente e salvo para uso futuro.

    *Caso prefira configurar manualmente, basta criar o arquivo `.reaverconf` na raiz com o seguinte formato:*
    ```text
    CLIENT_ID = "seu_id"
    CLIENT_SECRET = "seu_secret"
    TENANT_ID = "seu_tenant"
    DEFAULT_DOMAIN = "@empresa.com.br"
    ```

## Estrutura de Exportação

Os resultados são organizados para facilitar a custódia da prova:
```text
Matches_Export_usuario/
├── Nome_Participante_ID/
│   ├── Nome_Participante.txt  <-- Histórico completo do chat onde houve o match
│   └── Files/                 <-- Todos os anexos daquela conversa
```

---

## Disclaimer

O uso desta ferramenta para fins ilícitos não é apoiado. O TeamsReaver foi criado exclusivamente para auxiliar estudos, técnicas de segurança e profissionais de Blue e Red Team em atividades autorizadas. O desenvolvedor não se responsabiliza pelo uso indevido da ferramenta.
