import requests


def base_info(pokemon):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"Pokemon id: {data['id']}")
        print(f"Base stats: {data['stats'][0]['base_stat']} hp")
        print(f"Max stats : {data['stats'][5]['base_stat']} hp")
        print(f"Type of pokemon : {data['types'][0]['type']['name']}")
        print(f"Moves: {data['moves'][0]['move']['name']}")
    else:
        print("error")


print("Welcome to PokeDex")
pokemon = input("Pokemon : ")
base_info(pokemon)
print("-----")

