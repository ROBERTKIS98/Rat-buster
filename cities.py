"""
City data for Ratbuster: World Tour.

300 cities total: 50 Asia, 70 Africa, 70 Europe, and 110 split across
Americas / Oceania / Caribbean. Order is fixed (Asia -> Africa -> Europe ->
the rest) so level number maps 1:1 to a city, same as the original web
version of this game.
"""

ASIA = ["Tokyo", "Delhi", "Shanghai", "Mumbai", "Beijing", "Osaka", "Karachi", "Dhaka", "Istanbul", "Bangkok",
        "Jakarta", "Manila", "Seoul", "Tehran", "Hanoi", "Ho Chi Minh City", "Kuala Lumpur", "Singapore", "Yangon", "Riyadh",
        "Baghdad", "Ankara", "Taipei", "Hong Kong", "Shenzhen", "Guangzhou", "Chengdu", "Wuhan", "Xi'an", "Nanjing",
        "Chongqing", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Ahmedabad", "Pune", "Surat", "Lahore", "Faisalabad",
        "Colombo", "Kathmandu", "Dubai", "Abu Dhabi", "Doha", "Kuwait City", "Muscat", "Amman", "Beirut", "Jerusalem"]

AFRICA = ["Lagos", "Cairo", "Kinshasa", "Johannesburg", "Nairobi", "Addis Ababa", "Dar es Salaam", "Khartoum", "Casablanca", "Alexandria",
          "Abidjan", "Accra", "Luanda", "Algiers", "Tunis", "Rabat", "Kano", "Ibadan", "Kampala", "Mogadishu",
          "Dakar", "Yaoundé", "Douala", "Bamako", "Ouagadougou", "Lusaka", "Harare", "Maputo", "Antananarivo", "Kigali",
          "Bujumbura", "Lomé", "Cotonou", "Conakry", "Freetown", "Monrovia", "Niamey", "N'Djamena", "Bangui", "Brazzaville",
          "Libreville", "Malabo", "Windhoek", "Gaborone", "Maseru", "Mbabane", "Bloemfontein", "Durban", "Cape Town", "Port Elizabeth",
          "Pretoria", "Tripoli", "Benghazi", "Port Said", "Giza", "Asmara", "Djibouti City", "Nouakchott", "Banjul", "Bissau",
          "Praia", "São Tomé", "Juba", "Entebbe", "Jinja", "Mwanza", "Zanzibar City", "Mbeya", "Kisumu", "Eldoret",
          "Tamale", "Kumasi", "Sekondi-Takoradi", "Bulawayo", "Ndola", "Kitwe", "Blantyre", "Lilongwe", "Mzuzu", "Beira"]

EUROPE = ["London", "Paris", "Berlin", "Madrid", "Rome", "Amsterdam", "Vienna", "Warsaw", "Budapest", "Prague",
          "Lisbon", "Athens", "Dublin", "Brussels", "Copenhagen", "Stockholm", "Oslo", "Helsinki", "Zurich", "Geneva",
          "Munich", "Hamburg", "Frankfurt", "Cologne", "Milan", "Naples", "Turin", "Barcelona", "Valencia", "Seville",
          "Porto", "Bucharest", "Sofia", "Belgrade", "Zagreb", "Ljubljana", "Bratislava", "Vilnius", "Riga", "Tallinn",
          "Kyiv", "Minsk", "Moscow", "Saint Petersburg", "Reykjavik", "Edinburgh", "Glasgow", "Manchester", "Birmingham", "Liverpool",
          "Marseille", "Lyon", "Nice", "Toulouse", "Rotterdam", "The Hague", "Antwerp", "Gothenburg", "Malmö", "Bergen",
          "Krakow", "Wroclaw", "Gdansk", "Poznan", "Thessaloniki", "Valletta", "Nicosia", "Luxembourg City", "Monaco", "San Marino",
          "Andorra la Vella", "Basel", "Lausanne", "Bern", "Graz", "Salzburg", "Bilbao", "Palma", "Nantes", "Strasbourg"]

REST = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin",
        "Toronto", "Montreal", "Vancouver", "Ottawa", "Mexico City", "Guadalajara", "Monterrey", "Bogotá", "Medellín", "Cali",
        "Lima", "Santiago", "Buenos Aires", "Córdoba", "Rosario", "São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza",
        "Belo Horizonte", "Curitiba", "Caracas", "Quito", "Guayaquil", "La Paz", "Santa Cruz", "Asunción", "Montevideo", "Panama City",
        "San José", "Managua", "Tegucigalpa", "San Salvador", "Guatemala City", "Havana", "Santo Domingo", "Port-au-Prince", "Kingston", "Nassau",
        "Bridgetown", "Port of Spain", "San Juan", "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Gold Coast",
        "Auckland", "Wellington", "Christchurch", "Suva", "Port Moresby", "Honolulu", "Anchorage", "Seattle", "Portland", "Denver",
        "Atlanta", "Miami", "Orlando", "Tampa", "Nashville", "Memphis", "New Orleans", "Detroit", "Minneapolis", "Kansas City",
        "St. Louis", "Charlotte", "Washington D.C.", "Boston", "Baltimore", "Pittsburgh", "Cleveland", "Cincinnati", "Columbus", "Indianapolis",
        "Milwaukee", "Las Vegas", "Salt Lake City", "Sacramento", "San Francisco", "San Jose", "Oakland", "Fresno", "Tucson", "Albuquerque",
        "Oklahoma City", "Tulsa", "Omaha", "Winnipeg", "Calgary", "Edmonton", "Halifax", "Quebec City", "Hamilton", "Willemstad",
        "Oranjestad", "George Town", "Road Town", "Basseterre", "St. John's", "Castries", "Kingstown", "Roseau", "Belize City", "San Pedro Sula",
        "Georgetown", "Paramaribo", "Cayenne", "Darwin", "Hobart", "Newcastle", "Wollongong", "Cairns", "Townsville", "Apia"]

CARIBBEAN_SET = {"Havana", "Santo Domingo", "Port-au-Prince", "Kingston", "Nassau", "Bridgetown", "Port of Spain", "San Juan",
                  "Willemstad", "Oranjestad", "George Town", "Road Town", "Basseterre", "St. John's", "Castries", "Kingstown", "Roseau"}
OCEANIA_SET = {"Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Gold Coast", "Auckland", "Wellington",
               "Christchurch", "Suva", "Port Moresby", "Darwin", "Hobart", "Newcastle", "Wollongong", "Cairns", "Townsville", "Apia"}


def region_of(name):
    if name in CARIBBEAN_SET:
        return "Caribbean"
    if name in OCEANIA_SET:
        return "Oceania"
    return "Americas"


def _build_cities():
    cities = []
    for n in ASIA[:50]:
        cities.append({"name": n, "continent": "Asia"})
    for n in AFRICA[:70]:
        cities.append({"name": n, "continent": "Africa"})
    for n in EUROPE[:70]:
        cities.append({"name": n, "continent": "Europe"})
    for n in REST[:110]:
        cities.append({"name": n, "continent": region_of(n)})
    for i, c in enumerate(cities):
        c["level"] = i + 1
    return cities


CITIES = _build_cities()
assert len(CITIES) == 300

CONTINENTS = ["Asia", "Africa", "Europe", "Americas", "Oceania", "Caribbean"]

# background image + accent color per continent/region
CONTINENT_THEME = {
    "Asia":      {"bg": "bg_asia.png",      "accent": (0.88, 0.64, 0.24, 1)},
    "Africa":    {"bg": "bg_africa.png",    "accent": (0.91, 0.64, 0.24, 1)},
    "Europe":    {"bg": "bg_europe.png",    "accent": (0.56, 0.72, 0.84, 1)},
    "Americas":  {"bg": "bg_americas.png",  "accent": (0.31, 0.82, 0.69, 1)},
    "Oceania":   {"bg": "bg_oceania.png",   "accent": (0.37, 0.75, 0.91, 1)},
    "Caribbean": {"bg": "bg_caribbean.png", "accent": (0.24, 0.86, 0.75, 1)},
}


def get_city(level):
    return CITIES[max(1, min(level, 300)) - 1]
