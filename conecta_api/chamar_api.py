import requests

class ChamarFusionAPI:
    """
    Classe cliente para acessar o endpoint SenhasPorUsuarioView.
    Retorna a lista de senhas vinculadas às filas e empresas do usuário autenticado.
    """

    def __init__(self, base_url: str = "http://localhost:8000/api/fusion", token: str = None):
        """
        Inicializa a classe com a URL base e o token de autenticação (se necessário).

        Args:
            base_url (str): URL base da API (ex: "https://meusistema.com/api/")
            token (str): Token JWT ou Token DRF (opcional)
        """
        self.base_url = base_url.rstrip('/')
        self.token = token

    def _headers(self):
        """Monta os headers para autenticação."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    def autenticar(self, username: str, password: str, token_url: str = "http://localhost:8000/api/token/") -> bool:
        """
        Autentica o usuário usando username e password e armazena o token recebido.
        Args:
            username (str): Nome de usuário
            password (str): Senha
            token_url (str): URL para autenticação (normalmente /api/token/)

        Returns:
            bool: True se autenticado com sucesso, False caso contrário
        """
        payload = {
            "username": username,
            "password": password
        }

        try:
            response = requests.post(token_url, json=payload, headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            })

            if response.status_code == 200:
                self.token = response.json().get("token")
                if self.token:
                    return True
                else:
                    print("Resposta recebida, mas token não encontrado.")
                    return False
            elif response.status_code == 400:
                print("Credenciais inválidas.")
                return False
            else:
                print(f"Erro ao autenticar: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão durante a autenticação: {e}")
            return False


    def buscar_senhas(self):
        """
        Faz requisição GET ao endpoint /listar_senhas/ e retorna a lista de senhas.

        Returns:
            list[dict]: Lista de senhas e informações associadas.

        Raises:
            Exception: Em caso de erro de conexão ou resposta inesperada.
        """
        url = f"{self.base_url}/buscar_senhas/"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise PermissionError("Não autorizado: verifique o token de acesso.")
            else:
                raise Exception(f"Erro ao acessar API: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão com a API: {e}")

    def atualizar_impresso(self, num_senha: int, impresso:bool) -> dict:
        """
        Atualiza o campo 'impresso' de uma senha.

        :param num_senha: ID da senha a ser atualizada
        :return: dicionário com o status ou erro
        """
        url = f"{self.base_url}/atualizar_impresso/{num_senha}/"
        payload = {"impresso": impresso}
        try:
            response = requests.patch(url, json=payload, headers=self._headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            return {'erro': f'HTTP Error: {errh}', 'status_code': response.status_code}
        except requests.exceptions.RequestException as err:
            return {'erro': f'Request Error: {err}'}
        


    def buscar_chamadas(self):
        """
        Faz requisição GET ao endpoint /buscar_chamadas/ e retorna a lista unificada de chamadas.

        Returns:
            list[dict]: Lista de chamadas contendo campos:
                - id (int)
                - texto (str)
                - origem (str) → 'fila_senhas' ou 'fusion'

        Raises:
            PermissionError: Se o token de autenticação for inválido (HTTP 401/403).
            TimeoutError: Se a requisição exceder o tempo limite.
            Exception: Para outros erros de conexão ou resposta inesperada.
        """
        url = f"{self.base_url}/buscar_chamadas/"

        try:
            response = requests.get(url, headers=self._headers(), timeout=10)

            # 200 → OK
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    raise Exception("Erro ao decodificar resposta JSON da API.")

            # 401 → não autorizado
            elif response.status_code == 401:
                raise PermissionError("Não autorizado: verifique o token de acesso.")

            # 403 → acesso negado
            elif response.status_code == 403:
                erro = response.json().get("erro", "Acesso negado ao recurso.")
                raise PermissionError(f"Permissão negada: {erro}")

            # 404 → endpoint não encontrado
            elif response.status_code == 404:
                raise Exception(f"Endpoint não encontrado: {url}")

            # 500 → erro interno do servidor
            elif response.status_code == 500:
                erro = response.json().get("erro", "Erro interno no servidor da API.")
                raise Exception(f"Erro interno da API: {erro}")

            # Outros códigos
            else:
                raise Exception(f"Erro ao acessar API: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            raise TimeoutError("Tempo limite excedido ao tentar conectar-se à API.")

        except requests.exceptions.ConnectionError:
            raise Exception("Falha de conexão com o servidor da API.")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de requisição à API: {e}")

    def atualizar_realizado(self, chamada_id: int, origem: str) -> dict:
        """
        Atualiza o campo 'realizado' de uma chamada.

        :param chamada_id: ID da SenhaChamada ou número da Fusion
        :param origem: "fila_senhas" ou "fusion"
        :return: dicionário com o status ou erro
        """
        url = f"{self.base_url}/atualizar_realizado/"
        payload = {"id": chamada_id, "origem": origem}

        try:
            response = requests.patch(url, json=payload, headers=self._headers(), timeout=10)
            response.raise_for_status()  # Lança exceção para status HTTP 4xx/5xx
            return response.json()

        except requests.exceptions.HTTPError as errh:
            try:
                erro_json = response.json()
            except Exception:
                erro_json = response.text
            return {
                'erro': f'HTTP Error: {errh}',
                'detalhes': erro_json,
                'status_code': response.status_code
            }

        except requests.exceptions.RequestException as err:
            return {'erro': f'Request Error: {err}'}
