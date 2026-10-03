"""Atualiza a seção "Projetos em destaque" do README com os repositórios do usuário.

Lê os repositórios públicos pela API do GitHub (mais recentes primeiro), ignora
forks, arquivados e o próprio repositório de perfil, e reescreve o bloco entre
<!-- REPOS:START --> e <!-- REPOS:END --> com um card por repositório.
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

USER = os.environ.get("GITHUB_USER", "Gstorres22")
MAX_REPOS = int(os.environ.get("MAX_REPOS", "6"))
README = Path(__file__).resolve().parents[2] / "README.md"
CARD = (
    '<a href="{url}"><img width="49%" src="https://github-readme-stats.vercel.app/api/pin/'
    '?username={user}&repo={name}&theme=tokyonight&hide_border=true&border_radius=10" alt="{name}" /></a>'
)


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main():
    repos = [
        r for r in fetch_repos()
        if not r["fork"] and not r["archived"] and r["name"].lower() != USER.lower()
    ][:MAX_REPOS]

    cards = "\n".join(CARD.format(url=r["html_url"], user=USER, name=r["name"]) for r in repos)
    block = f'<!-- REPOS:START -->\n<p align="center">\n{cards}\n</p>\n<!-- REPOS:END -->'

    text = README.read_text(encoding="utf-8")
    new_text, count = re.subn(r"<!-- REPOS:START -->.*?<!-- REPOS:END -->", lambda _: block, text, flags=re.S)
    if count == 0:
        sys.exit("Marcadores REPOS:START/REPOS:END não encontrados no README.")

    if new_text != text:
        README.write_text(new_text, encoding="utf-8")
        print(f"README atualizado com {len(repos)} repositórios.")
    else:
        print("Nenhuma mudança.")


if __name__ == "__main__":
    main()
