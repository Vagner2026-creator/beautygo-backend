# BeautyGO — Frontend Flutter

App mobile do marketplace de serviços de beleza.

## Pré-requisitos

1. [Flutter SDK](https://docs.flutter.dev/get-started/install/windows) (versão 3.x ou superior)
2. Android Studio ou VS Code com extensão Flutter
3. Emulador Android ou dispositivo físico
4. Backend rodando em `http://localhost:8000`

## Configuração

### 1. Instalar Flutter

- Baixe em: https://docs.flutter.dev/get-started/install/windows
- Extraia em `C:\flutter`
- Adicione `C:\flutter\bin` ao PATH do sistema
- Execute `flutter doctor` para verificar a instalação

### 2. Configurar o endereço da API

Abra `lib/core/api/api_client.dart` e ajuste `baseUrl`:

- **Emulador Android**: `http://10.0.2.2:8000/api/v1` (já configurado)
- **Dispositivo físico**: `http://SEU_IP_LOCAL:8000/api/v1`
  - Descubra seu IP: `ipconfig` no Windows → IPv4 (ex: 192.168.1.100)

### 3. Rodar o app

```bash
# Na pasta frontend/
flutter pub get
flutter run
```

## Estrutura do projeto

```
lib/
  core/
    api/         → Cliente HTTP (Dio)
    theme/       → Cores e estilos globais
  features/
    auth/        → Login e cadastro
    home/        → Tela inicial com lista de profissionais
    search/      → Busca com filtros
    professional/→ Perfil do profissional
    appointments/→ Agendamentos (criar, listar, confirmar, cancelar)
    notifications/→ Notificações
    profile/     → Perfil do usuário
  models/        → Classes de dados (Professional, Appointment, etc.)
  providers/     → Estado global (auth, appointments, notifications)
  widgets/       → Componentes reutilizáveis
```

## Telas implementadas

- **Login / Cadastro** (cliente ou profissional)
- **Home** — lista de profissionais com categorias
- **Busca** — keyword + filtros (salão/domicílio)
- **Perfil do profissional** — serviços, avaliação, localização
- **Agendamento** — fluxo em 3 passos (data → contato → confirmação)
- **Meus agendamentos** — ativos e histórico, com confirmar/cancelar
- **Notificações** — marcar como lido
- **Perfil** — dados do usuário e logout
