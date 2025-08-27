<div align="center">
  <img src="https://storage.googleapis.com/golden-wind/bootcamp-gostack/header-desafio-conceitos.png" alt="logo-django" border="0">
  <h1 align="center">API de Delivery em Tempo Real</h1>
  <p align="center">
    Um backend robusto para uma aplicação de delivery, construído com Django, PostgreSQL e Firebase.
  </p>
</div>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Django" src="https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white">
  <img alt="Firebase" src="https://img.shields.io/badge/Firebase-Realtime_DB-FFCA28?style=for-the-badge&logo=firebase&logoColor=black">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-24-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

## 📖 Tabela de Conteúdos
* [Sobre o Projeto](#-sobre-o-projeto)
* [Funcionalidades](#-funcionalidades-principais)
* [Arquitetura e Tech Stack](#-arquitetura-e-tech-stack)
* [Começando](#-começando)
* [Endpoints da API](#-endpoints-da-api)
* [Como Testar](#-como-testar)
* [Próximos Passos](#-próximos-passos)
* [Licença](#-licença)
* [Autor](#-autor)

---

## 💻 Sobre o Projeto

Este projeto é o backend completo para uma aplicação de delivery de comida, similar a iFood ou Uber Eats. A API foi desenvolvida seguindo as melhores práticas de design de software, com um sistema de autenticação seguro, permissões baseadas em papéis de usuário e uma arquitetura híbrida que une a robustez de um banco de dados relacional (PostgreSQL) para dados transacionais com a velocidade de um banco de dados NoSQL (Firebase Realtime Database) para funcionalidades em tempo real, como o rastreamento de entregadores.

---

## ✨ Funcionalidades Principais

-   🔐 **Autenticação Segura:** Sistema completo de registro e login com Tokens **JWT (JSON Web Tokens)**.
-   👤 **Múltiplos Papéis de Usuário:** Sistema de permissões granulares para três tipos de usuários:
    -   **Cliente:** Navega, cria pedidos e acompanha a entrega.
    -   **Dono de Restaurante:** Gerencia seu estabelecimento, cardápio e pedidos.
    -   **Entregador:** Visualiza e aceita corridas disponíveis.
-   🍽️ **Gerenciamento de Restaurantes e Cardápios:** Endpoints para que donos possam controlar totalmente suas operações.
-   🛒 **Fluxo de Pedidos Completo:** Lógica de negócio para criação, listagem e atualização de status de pedidos (`Pendente`, `Em Preparo`, `Saiu para Entrega`, etc.).
-   📍 **Rastreamento em Tempo Real:** Integração com **Firebase Realtime Database** para que entregadores enviem sua geolocalização e clientes acompanhem ao vivo.

---

## 🛠️ Arquitetura e Tech Stack

A arquitetura foi projetada para ser escalável e eficiente, separando as responsabilidades.

   Cliente (Mobile/Web)
          |
          |--- Requisições HTTP/S ---> [ Firebase Hosting ] ---> [ Google Cloud Run ]
          |                                                           |
          |                                                     [ Django API ]
          |                                                     /           \
          |                                                    /             \
          |--- Conexão Realtime ---> [ Firebase Realtime DB ]  <-- [ PostgreSQL (Docker) ]

As principais tecnologias utilizadas foram:

* **Backend:** Django, Django REST Framework
* **Banco de Dados:** PostgreSQL (gerenciado via Docker)
* **Autenticação:** djangorestframework-simplejwt
* **Funcionalidades Real-time:** Firebase Admin SDK (Realtime Database)
* **Variáveis de Ambiente:** python-dotenv

---

## 🚀 Começando

Siga as instruções para configurar e rodar o projeto em seu ambiente local.

### **Pré-requisitos**
* Python 3.10+
* Docker e Docker Compose
* Uma conta no Firebase

### **Instalação**
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
    cd NOME_DO_REPOSITORIO
    ```
2.  **Crie o arquivo de variáveis de ambiente:**
    * Crie uma cópia do arquivo `.env.example` e renomeie para `.env`.
    * Preencha o arquivo `.env` com suas credenciais do PostgreSQL e do Firebase.
    
    **.env.example**
    ```env
    # PostgreSQL
    DB_NAME=dbdelivery
    DB_USER=postgres
    DB_PASSWORD=supersecret
    DB_HOST=localhost
    DB_PORT=5433
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
    FIREBASE_DATABASE_URL=[https://SEU-PROJETO-default-rtdb.firebaseio.com/](https://SEU-PROJETO-default-rtdb.firebaseio.com/)
    ```

3.  **Adicione suas credenciais do Firebase:**
    * Baixe o arquivo JSON de credenciais do seu projeto no Firebase (em "Configurações do Projeto" > "Contas de serviço").
    * Salve-o na raiz do projeto com o nome `firebase-credentials.json`.

4.  **Crie o ambiente virtual e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS ou .\\venv\\Scripts\\activate no Windows
    pip install -r requirements.txt
    ```

5.  **Inicie o banco de dados com Docker:**
    ```bash
    docker run --name db_delivery -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=supersecret -e POSTGRES_DB=dbdelivery -p 5433:5432 -d postgres
    ```

6.  **Aplique as migrações e crie um superusuário:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    A API estará rodando em `http://127.0.0.1:8000/`.

---

## 🔌 Endpoints da API

A URL base para todos os endpoints é `/api/`.

<details>
  <summary><strong>🔑 Autenticação e Usuários</strong></summary>
  
| Método | URL | Proteção | Descrição |
| :--- | :--- | :--- | :--- |
| `POST` | `/register/` | Pública | Registra um novo usuário (`customer`, `owner`, `driver`). |
| `POST` | `/token/` | Pública | Realiza login e retorna tokens JWT. |
| `GET`, `PUT`, `PATCH` | `/profile/` | `IsAuthenticated` | Permite que um usuário logado veja e atualize seu perfil. |
</details>

<details>
  <summary><strong>🍽️ Público (Clientes e Visitantes)</strong></summary>
  
| Método | URL | Proteção | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/public/restaurants/` | Pública | Lista todos os restaurantes ativos. |
| `GET` | `/public/restaurants/<id>/menu/` | Pública | Lista os itens do cardápio de um restaurante específico. |
</details>

<details>
  <summary><strong>🛒 Cliente (`role: customer`)</strong></summary>
  
| Método | URL | Proteção | Descrição |
| :--- | :--- | :--- | :--- |
| `POST`, `GET` | `/orders/` | `IsCustomer` | Cria um novo pedido ou lista os pedidos antigos do cliente. |
| `GET` | `/customer/orders/<id>/track/` | `IsCustomer` | Obtém as informações para rastrear um pedido em tempo real. |
</details>

<details>
  <summary><strong>🏪 Dono de Restaurante (`role: owner`)</strong></summary>
  
| Método | URL | Proteção | Descrição |
| :--- | :--- | :--- | :--- |
| `POST`, `GET` | `/restaurants/` | `IsRestaurantOwner` | Cria ou lista o restaurante do dono. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/restaurants/<id>/` | `IsRestaurantOwner` | Gerencia os detalhes do seu restaurante. |
| `POST`, `GET` | `/restaurants/<id>/menu/` | `IsRestaurantOwner` | Adiciona ou lista itens do cardápio. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/restaurants/<rid>/menu/<iid>/` | `IsRestaurantOwner` | Gerencia um item específico do cardápio. |
| `GET` | `/restaurant/orders/` | `IsRestaurantOwner` | Lista todos os pedidos recebidos pelo restaurante. |
| `PATCH` | `/restaurant/orders/<id>/` | `IsRestaurantOwner` | Atualiza o status de um pedido. |
</details>

<details>
  <summary><strong>🛵 Entregador (`role: driver`)</strong></summary>
  
| Método | URL | Proteção | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/driver/available-orders/` | `IsDriver` | Lista todos os pedidos prontos para entrega. |
| `PATCH` | `/driver/claim-order/<id>/` | `IsDriver` | Aceita um pedido para realizar a entrega. |
| `PATCH` | `/driver/orders/<id>/location/` | `IsDriver` | Atualiza a geolocalização para um pedido em andamento. |
</details>

---

## 🧪 Como Testar
Para interagir com a API, utilize uma ferramenta como [Insomnia](https://insomnia.rest/) ou [Postman](https://www.postman.com/). O fluxo de teste ideal é:
1.  **Cadastre** um usuário para cada `role` (`customer`, `owner`, `driver`).
2.  **Faça login** como `owner` e cadastre um restaurante e alguns itens no cardápio.
3.  **Faça login** como `customer` e crie um pedido para o restaurante.
4.  **Faça login** como `owner` novamente e atualize o status do pedido para `out_for_delivery`.
5.  **Faça login** como `driver`, veja a lista de pedidos disponíveis e aceite o pedido.
6.  **(Como `driver`)** Envie atualizações de localização e verifique os dados aparecendo no seu Firebase Realtime Database.

---

## 🔮 Próximos Passos
* [ ] Fazer o deploy da aplicação no Google Cloud Run.
* [ ] Construir um frontend em React ou Vue.js para consumir a API.
* [ ] Integrar um gateway de pagamento (Stripe, Mercado Pago).
* [ ] Implementar notificações push via Firebase Cloud Messaging.
* [ ] Adicionar testes automatizados.

---

## 📄 Licença
Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

## 👨‍💻 Autor
**[Seu Nome Aqui]**
* **LinkedIn:** [https://linkedin.com/in/seu-usuario](https://linkedin.com/in/seu-usuario)
* **GitHub:** [@seu-usuario](https://github.com/seu-usuario)