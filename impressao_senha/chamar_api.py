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

    def listar_senhas(self):
        """
        Faz requisição GET ao endpoint /listar_senhas/ e retorna a lista de senhas.

        Returns:
            list[dict]: Lista de senhas e informações associadas.

        Raises:
            Exception: Em caso de erro de conexão ou resposta inesperada.
        """
        url = f"{self.base_url}/listar_senhas/"
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