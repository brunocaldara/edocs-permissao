async def retornar_linhas_tabela(pagina):
    tabela_papeis = pagina.locator("table")
    linhas_papeis = tabela_papeis.locator("tbody tr")
    return linhas_papeis
