import os
import re

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False, slow_mo=50, args=['--start-maximized'])
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    page.goto(os.getenv("ACESSO_CIDADAO_URL"))
    page.get_by_role("button", name="Login via Acesso Cidadão").click()
    page.get_by_placeholder("CPF").fill(os.getenv("ACESSO_CIDADAO_LOGIN"))
    page.get_by_placeholder("Senha").fill(os.getenv("ACESSO_CIDADAO_SENHA"))
    page.get_by_role("button", name="Entrar", exact=True).click()
    botao_acesso_cidadao_admin = page.get_by_title("Acessar: Acesso Cidadão (")
    javascript_acesso_cidadao_admin = botao_acesso_cidadao_admin.get_attribute(
        "onclick")
    url_acesso_cidadao_admin = re.search(
        r"(?P<url>https?://[^\s]+)", javascript_acesso_cidadao_admin).group("url")
    page.goto(url_acesso_cidadao_admin)

    # page.locator('#sistemas').click()

    page.locator('#gruposservidores').click()
    page.get_by_role("link", name="Servidor", exact=True).click()
    # page.get_by_role("link", name="Grupos", exact=True).click()

    page.get_by_placeholder("CPF ou e-mail").click()
    page.get_by_placeholder("CPF ou e-mail").fill("")
    page.get_by_text("search").click()
    page.get_by_role("link", name="assignment_ind").click()

    tds = page.locator("td")
    # PERITO OFICIAL CRIMINAL (LAB-TOX) - PCIES
    achou = tds.filter(has_text="TESTE DO CALDARA")
    # print(achou.count())
    # print(achou)

    # https://stackoverflow.com/questions/77014199/python-playwright-want-to-print-all-text-in-table-but-finds-0-rows
    table = page.locator("table")
    rows = table.locator("tbody tr")
    # print(rows.count())
    # print(rows.all_text_contents())

    td_botao_apagar = None

    for i in range(rows.count()):
        cols = rows.nth(i).locator("td")
        # print(cols.count())
        for j in range(cols.count()):
            if cols.nth(j).inner_text() == "TESTE DO CALDARA":
                td_botao_apagar = cols.nth(4)
                break

    if td_botao_apagar is not None:
        formulario = td_botao_apagar.locator("form")
        botao = formulario.locator("button")

        if botao is not None:
            botao.click()

    # REMOVER PAPEL
    # page.get_by_role("link", name="mode_edit").click()

    # ADICIONAR PAPEL
    # page.get_by_role("link", name="Adicionar", exact=True).click()
    # page.get_by_text("Selecione um período 1 mês").click()
    # page.get_by_role("option", name="ano (máximo)").click()
    # page.get_by_label("Nome").fill("TESTE DO CALDARA")
    # page.get_by_role("button", name="Adicionar").click()

    page.pause()
# browser.close()

# page.get_by_role("button", name="Login via Acesso Cidadão").click()
# page.get_by_placeholder("CPF").click()
# page.get_by_placeholder("CPF").fill("10279630727")
# page.get_by_placeholder("Senha").click()
# page.get_by_placeholder("Senha").fill("123")
# page.get_by_role("button", name="Entrar", exact=True).click()
