import asyncio
import operator
import os
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from enums import ACESSO_CIDADAO_ADMIN, GRUPO_E_SERVIDOR
from helpers import retornar_linhas_tabela

load_dotenv()


async def main():
    def configurar_proxy():
        proxy_url = os.getenv("PROXY_URL")
        proxy_porta = os.getenv("PROXY_PORTA")
        proxy_usuario = os.getenv("PROXY_USUARIO")
        proxy_senha = os.getenv("PROXY_SENHA")
        proxy_config = None

        if (proxy_url is not '' and proxy_porta is not '' and
                proxy_usuario is not '' and proxy_senha is not ''):
            proxy_config = {
                "server": f"{proxy_url}:{proxy_porta}",
                "username": proxy_usuario,
                "password": proxy_senha
            }

        return proxy_config

    async def configurar_navegador():
        navegador = await p.chromium.launch(
            headless=False, slow_mo=50, args=['--start-maximized'], proxy=configurar_proxy())
        contexto = await navegador.new_context(no_viewport=True)
        pagina = await contexto.new_page()
        return pagina

    async def buscar_url_acesso_cidadao_admin(pagina):
        botao_acesso_cidadao_admin = pagina.get_by_title(
            "Acessar: Acesso Cidadão (")
        javascript_acesso_cidadao_admin = await botao_acesso_cidadao_admin.get_attribute(
            "onclick")
        url = re.search(
            r"(?P<url>https?://[^\s]+)", javascript_acesso_cidadao_admin).group("url")
        return url

    async def acessar_pagina(pagina, url):
        return await pagina.goto(url)

    async def acessar_pagina_sistemas(pagina, acesso_cidadao_admin):
        await pagina.locator(f"#{acesso_cidadao_admin}").click()
        await pagina.get_by_role("link", name="E-Docs sigades").click()
        await pagina.get_by_role("link", name="Verificar").click()

    async def acessar_pagina_grupos_e_servidores(pagina, acesso_cidadao_admin, grupo_e_servidor):
        await pagina.locator(f"#{acesso_cidadao_admin}").click()
        await pagina.get_by_role("link", name=grupo_e_servidor, exact=True).click()

    async def pesquisar_por_cpf_pagina_sistemas(pagina, cpf):
        await pagina.get_by_role("link", name="Adicionar").click()
        await pagina.get_by_label("CPF ou e-mail").fill(cpf)
        await pagina.get_by_role("button", name="Pesquisar").click()

    async def realizar_login(pagina):
        await pagina.get_by_role("button", name="Login via Acesso Cidadão").click()
        await pagina.get_by_placeholder("CPF").fill(os.getenv("ACESSO_CIDADAO_LOGIN"))
        await pagina.get_by_placeholder("Senha").fill(
            os.getenv("ACESSO_CIDADAO_SENHA"))
        await pagina.get_by_role("button", name="Entrar", exact=True).click()

    async def pesquisar_por_cpf_pagina_servidor(pagina, cpf):
        await pagina.get_by_placeholder("CPF ou e-mail").fill(cpf)
        await pagina.get_by_text("search").click()

    async def acessar_papeis(pagina):
        await pagina.get_by_role("link", name="assignment_ind").click()

    async def verificar_papel(pagina, papel):
        papel_existe = False
        linhas_papeis = await retornar_linhas_tabela(pagina)
        quantidade_linhas = await linhas_papeis.count()

        for i in range(quantidade_linhas):
            colunas_papeis = linhas_papeis.nth(i).locator("td")
            for j in range(await colunas_papeis.count()):
                if operator.contains(await colunas_papeis.nth(j).inner_text(), papel):
                    papel_existe = True
                    break

        return papel_existe

    async def adicionar_papel(pagina, papel):
        await pagina.get_by_role("link", name="Adicionar", exact=True).click()
        await pagina.get_by_text("Selecione um período 1 mês").click()
        await pagina.get_by_role("option", name="ano (máximo)").click()
        await pagina.get_by_label("Nome").fill(papel)
        await pagina.get_by_role("button", name="Adicionar").click()

    async def remover_papel(pagina, papel):
        linhas_papeis = await retornar_linhas_tabela(pagina)
        quantidade_linhas = await linhas_papeis.count()
        botao_excluir_papel = None
        posicao_coluna_botoes_acoes = 4

        for i in range(quantidade_linhas):
            colunas_papeis = linhas_papeis.nth(i).locator("td")
            for j in range(await colunas_papeis.count()):
                if operator.contains(await colunas_papeis.nth(j).inner_text(), papel):
                    coluna_botoes_acoes = colunas_papeis.nth(
                        posicao_coluna_botoes_acoes)
                    break

        if coluna_botoes_acoes is not None:
            formulario_acoes = coluna_botoes_acoes.locator("form")
            botao_excluir_papel = formulario_acoes.locator("button")

            if botao_excluir_papel is not None:
                await botao_excluir_papel.click()

    async def cadastrar_lotacao(pagina, papel, lotacao):
        # https://stackoverflow.com/questions/77014199/python-playwright-want-to-print-all-text-in-table-but-finds-0-rows
        tabela_papeis = pagina.locator("table")
        linhas_papeis = tabela_papeis.locator("tbody tr")

        posicao_coluna_botoes_acoes = 4
        coluna_botoes_acoes = None
        link_editar_papel = None

        for i in range(await linhas_papeis.count()):
            colunas_papeis = linhas_papeis.nth(i).locator("td")
            for j in range(await colunas_papeis.count()):
                if operator.contains(await colunas_papeis.nth(j).inner_text(), papel):
                    coluna_botoes_acoes = colunas_papeis.nth(
                        posicao_coluna_botoes_acoes)
                    break

        if coluna_botoes_acoes is not None:
            link_editar_papel = coluna_botoes_acoes.locator("a")

            if link_editar_papel is not None:
                await link_editar_papel.click()
                await pagina.get_by_role("link", name="add_circle").click()
                await pagina.get_by_label("Só permitidos").check()
                await pagina.get_by_title(lotacao).locator("#Selecionado").click()
                await pagina.get_by_role("button", name="Selecionar").click()
                await pagina.get_by_label("Voltar").click()

    async with async_playwright() as p:
        pagina = await configurar_navegador()
        await acessar_pagina(pagina, os.getenv("ACESSO_CIDADAO_URL"))
        await realizar_login(pagina)
        url_acesso_cidadao_admin = await buscar_url_acesso_cidadao_admin(pagina)
        await acessar_pagina(pagina, url_acesso_cidadao_admin)

        # await acessar_pagina_sistemas(pagina, ACESSO_CIDADAO_ADMIN.SISTEMAS.value)
        # await pesquisar_por_cpf_pagina_sistemas(pagina, "104.093.137-50")

        await acessar_pagina_grupos_e_servidores(pagina, ACESSO_CIDADAO_ADMIN.GRUPOS_E_SERVIDORES.value, GRUPO_E_SERVIDOR.SERVIDOR.value)
        await pesquisar_por_cpf_pagina_servidor(pagina, "104.093.137-50")
        await acessar_papeis(pagina)

        # papel_existe = await verificar_papel(pagina, "TESTE DO CALDARA")
        # print("papel_existe ", papel_existe)
        # if not papel_existe:
        #     await adicionar_papel(pagina, "TESTE DO CALDARA")
        #     await cadastrar_lotacao(pagina, "TESTE DO CALDARA", "LAB TOX")
        # else:
        #     await remover_papel(pagina, "TESTE DO CALDARA")

        await pagina.pause()
    # browser.close()

if __name__ == "__main__":
    asyncio.run(main())
