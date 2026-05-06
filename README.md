![TeamsReaver Banner](https://i.imgur.com/xuGHbkh.jpeg)

# TeamsReaver: Teams Forensic Investigation & Data Export Tool

**TeamsReaver** é uma ferramenta de perícia computacional e exfiltração de dados desenvolvida para análise, busca e extração automatizada de informações do Microsoft Teams através da Microsoft Graph API.

## Funcionalidades Principais

A ferramenta oferece três modos principais de operação para investigações:

*   **Busca por Termos e Arquivos com Extração de Contexto:** Ao realizar uma busca por termos (ex: `apikey`, `senha`) ou nomes de arquivos específicos (ex: `documento.pdf`, `planilha.xlsx`), a ferramenta não extrai apenas a mensagem ou anexo isolado. Caso um "match" seja encontrado no conteúdo da mensagem ou no nome de um arquivo, o histórico completo daquela conversa é baixado automaticamente, incluindo todos os anexos vinculados.
*   **Extração Completa 1:1:** Permite baixar todo o histórico de mensagens e arquivos trocados entre dois usuários específicos, sendo ideal para investigações direcionadas de conduta ou vazamento de informações.
*   **Flexibilidade de Varredura Temporal:**
    *   **Deep Sweep (Padrão):** Se nenhum filtro de data for aplicado, a ferramenta realiza uma varredura completa desde a primeira mensagem do usuário.
    *   **Fast Search (`-Fast`):** Varredura focada nos últimos X dias.
    *   **Data Específica (`-Date`):** Alvo em um dia exato de incidente.

## Público-Alvo e Casos de Uso

1.  **Defensivo (Hunting, CTI, DLP e Blue Team):** Projetado para investigações onde o Microsoft Purview se mostra limitado. O Purview pode levar horas para processar buscas e frequentemente entrega resultados fragmentados. O TeamsReaver entrega os dados de forma imediata, organizada em pastas e com todos os anexos vinculados.
2.  **Ofensivo (Pentesters e Red Teamers):** Essencial em cenários de Cloud Pentest. Se uma Enterprise Application for comprometida com permissões de leitura, a ferramenta permite exfiltrar comunicações sensíveis de forma rápida e silenciosa.

## Instalação e Configuração

### Via Pip (Recomendado)

Agora você pode instalar o **TeamsReaver** diretamente via pip:

```bash
pip install teamsreaver
```

Após a instalação, o comando `teamsreaver` estará disponível globalmente no seu terminal. Você não precisa mais baixar o script manualmente ou rodar com `python3 script.py`.

> **Dica (Windows/Linux/Mac):** Caso receba um erro de "comando não encontrado" após instalar, você pode rodar a ferramenta utilizando o Python diretamente:
> ```bash
> python -m teamsreaver -TargetUPN usuario ...
> ```

### Adicionando ao PATH (Caso o comando acima falhe)

Se você deseja usar apenas o comando `teamsreaver` e o sistema não o reconhecer, adicione a pasta de scripts do Python ao seu PATH:

#### Windows (PowerShell)
```powershell
# Descubra onde o Python guarda os scripts
$path = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
# Adicione ao PATH do usuário atual
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$path", "User")
```
*Reinicie o terminal após rodar os comandos.*

#### Linux / macOS (Bash/Zsh)
```bash
# Adicione ao seu .bashrc ou .zshrc
echo 'export PATH="$PATH:$(python3 -m site --user-base)/bin"' >> ~/.zshrc
source ~/.zshrc
```

### Configuração Inicial

Na primeira execução, a ferramenta iniciará um **modo interativo** no terminal solicitando as credenciais da sua Enterprise Application no Azure (`Client ID`, `Secret`, `Tenant ID` e o `Domínio Padrão`). 

As configurações serão salvas automaticamente em `~/.reaverconf` no seu diretório de usuário.

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

---

## Como Utilizar

### Exemplos Práticos

```bash
# Busca termos especificos em um usuario alvo:
teamsreaver -TargetUPN usuario -SearchTerms "senha","chave"

# Busca um termo em TODOS os usuarios em uma data especifica:
teamsreaver -SearchTerms "senha" -Date "01/05/2026"

# Extrai toda a conversa entre dois usuarios:
teamsreaver -TargetUPN usuario -TargetTwo outro_usuario

# Busca parcial (ex: AKIA) em todos nos ultimos 30 dias:
teamsreaver -Fast 30 -SearchTerms "AKIA"

# Busca por um nome de arquivo especifico em todo o tenant:
teamsreaver -SearchTerms "relatorio.xlsx"

# Busca combinando alvo, termo e data:
teamsreaver -TargetUPN "admin" -SearchTerms "backup" -Date "20/04/2026"
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
