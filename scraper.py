import os
import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup

# Regex
num_pattern = re.compile(r"#(?P<num>\d{3})")
rel_url_pattern = re.compile(r"^/pokedex/\w+")


class PokemonInfo:
    def __init__(self, img_url, number, name, type_list, full_url):
        self.img_url = img_url
        self.number = number
        self.name = name
        self.type_list = type_list
        self.full_url = full_url

    def __str__(self):
        return f"<Pokemon: {self.name} (#{self.number:03d})>"


def href_relpath(href):
    return href and rel_url_pattern.match(href)


base_url = "https://pokemondb.net"
url = f"{base_url}/pokedex/national"
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

info_cards = soup.find_all("div", class_="infocard")

pokemon_list = []

for ic in info_cards:
    print(ic)
    img_url = ic.find("span", class_="img-sprite")["data-src"]
    number = int(ic.find("small", string=lambda x: num_pattern.match(x)).text.replace("#", ""))
    name = ic.find("a", class_="ent-name").text
    types = ic.find_all("a", class_="itype")
    type_list = []
    for t in types:
        type_list.append(t.text)

    pokemon_url = ic.find_all("a")
    full_url = None
    for pu in pokemon_url:
        if rel_url_pattern.match(pu["href"]):
            full_url = f"{base_url}{pu['href']}"
            break

    pokemon = PokemonInfo(img_url, number, name, type_list, full_url)
    pokemon_list.append(pokemon)

if not os.path.exists("images"):
    os.makedirs("images")

for pokemon in pokemon_list:
    img_data = requests.get(pokemon.img_url)
    with open(f"images/{pokemon.name}.png", "wb") as fp:
        fp.write(img_data.content)
