import asyncio
import os
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from enums import GRUPO_E_SERVIDOR

load_dotenv()


async def main():
    def configurar_proxy():
        proxy_url = os.getenv("PROXY_URL")
        proxy_porta = os.getenv("PROXY_PORTA")
        proxy_usuario = os.getenv("PROXY_USUARIO")
        proxy_senha = os.getenv("PROXY_SENHA")
        proxy_config = None

        if (proxy_url is not None and proxy_porta is not None and
                proxy_usuario is not None and proxy_senha is not None):
            proxy_config = {
                "server": f"{proxy_url}:{proxy_porta}",
                "username": proxy_usuario,
                "password": proxy_senha
            }

        return proxy_config

    async def acessar_pagina_grupos_e_servidores(pagina, enumeracao):
        # await page.locator('#sistemas').click()
        await pagina.locator('#gruposservidores').click()
        await pagina.get_by_role("link", name=enumeracao, exact=True).click()

    async def pesquisar_por_cpf(pagina, cpf):
        await pagina.get_by_placeholder("CPF ou e-mail").fill(cpf)
        await pagina.get_by_text("search").click()

    async def acessar_papeis(pagina):
        await pagina.get_by_role("link", name="assignment_ind").click()

    async def cadastrar_papel(pagina):
        # https://stackoverflow.com/questions/77014199/python-playwright-want-to-print-all-text-in-table-but-finds-0-rows
        tabela_papeis = pagina.locator("table")
        linhas_papeis = tabela_papeis.locator("tbody tr")

        posicao_coluna_botoes_acoes = 4
        coluna_botoes_acoes = None
        link_editar_papel = None
        botao_excluir_papel = None

        for i in range(await linhas_papeis.count()):
            colunas_papeis = linhas_papeis.nth(i).locator("td")
            for j in range(await colunas_papeis.count()):
                if await colunas_papeis.nth(j).inner_text() == "TESTE DO CALDARA":
                    coluna_botoes_acoes = colunas_papeis.nth(
                        posicao_coluna_botoes_acoes)
                    break

        if coluna_botoes_acoes is not None:
            link_editar_papel = coluna_botoes_acoes.locator("a")
            formulario_acoes = coluna_botoes_acoes.locator("form")
            botao_excluir_papel = formulario_acoes.locator("button")

            if link_editar_papel is not None:
                await link_editar_papel.click()
                await pagina.get_by_role("link", name="add_circle").click()
                # await page.get_by_role("textbox").click()
                # await page.get_by_role("textbox").fill("SMC-SM")
                # await page.get_by_label("Só permitidos").check()
                # await page.wait_for_timeout(tempo_espera_padrao)

                await pagina.get_by_title("SMC-SM").locator("#Selecionado").click()
                await pagina.get_by_role("button", name="Selecionar").click()
                await pagina.get_by_label("Voltar").click()

    async def adicionar_papel(page):
        await page.get_by_role("link", name="Adicionar", exact=True).click()
        await page.get_by_text("Selecione um período 1 mês").click()
        await page.get_by_role("option", name="ano (máximo)").click()
        await page.get_by_label("Nome").fill("TESTE DO CALDARA")
        await page.get_by_role("button", name="Adicionar").click()

    async with async_playwright() as p:
        navegador = await p.chromium.launch(
            headless=False, slow_mo=50, args=['--start-maximized'], proxy=configurar_proxy())
        contexto = await navegador.new_context(no_viewport=True)
        pagina = await contexto.new_page()
        await pagina.goto(os.getenv("ACESSO_CIDADAO_URL"))
        await pagina.get_by_role("button", name="Login via Acesso Cidadão").click()
        await pagina.get_by_placeholder("CPF").fill(os.getenv("ACESSO_CIDADAO_LOGIN"))
        await pagina.get_by_placeholder("Senha").fill(
            os.getenv("ACESSO_CIDADAO_SENHA"))
        await pagina.get_by_role("button", name="Entrar", exact=True).click()
        botao_acesso_cidadao_admin = pagina.get_by_title(
            "Acessar: Acesso Cidadão (")
        javascript_acesso_cidadao_admin = await botao_acesso_cidadao_admin.get_attribute(
            "onclick")
        url_acesso_cidadao_admin = re.search(
            r"(?P<url>https?://[^\s]+)", javascript_acesso_cidadao_admin).group("url")
        await pagina.goto(url_acesso_cidadao_admin)

        await acessar_pagina_grupos_e_servidores(pagina, GRUPO_E_SERVIDOR.SERVIDOR.value)
        await pesquisar_por_cpf(pagina, "104.093.137-50")
        await acessar_papeis(pagina)

        await pagina.pause()
    # browser.close()

if __name__ == "__main__":
    asyncio.run(main())
