import pygame
import json
pygame.init()

citiesFilePath = r"C:\Users\bodit\Documents\WebProjects\CityQuiz\src\assets\cities.json"
mapImagePath = r"C:\Users\bodit\Documents\WebProjects\CityQuiz\src\assets\hungaryCities.png"

def loadCities() -> list[dict]:
    with open(citiesFilePath, "r", encoding = "UTF-8") as citiesFile:
        return json.load(citiesFile)
    
def storeCities(cities: list[dict]):
    with open(citiesFilePath, "w", encoding = "UTF-8") as citiesFile:
        cities.sort(key = lambda e: e["name"])
        json.dump(cities, citiesFile, ensure_ascii = False, indent = 4)

def main():
    pygame.key.set_repeat(500, 50)
    image = pygame.image.load(mapImagePath)
    surfaceSize = image.get_size()
    font = pygame.sysfont.SysFont("Arial", 30)
    mousePos = (0, 0)
    clickedMousePos = (0, 0)
    copied = False
    cityName = ""

    surface = pygame.display.set_mode(surfaceSize, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED | pygame.RESIZABLE)
    pygame.scrap.init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEMOTION:
                mousePos = event.pos
                copied = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    pygame.scrap.put(pygame.SCRAP_TEXT, bytes(f"[{mousePos[0]}, {mousePos[1]}]", "ascii"))
                    clickedMousePos = mousePos
                    copied = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if cityName:
                        cityName = cityName[0:-1]
                elif event.key == pygame.K_z and event.mod & pygame.K_LCTRL:
                    cities = loadCities()
                    if cities:
                        cities.pop(-1)
                    storeCities(cities)
                elif event.key == pygame.K_RETURN:
                    cities = loadCities()
                    cities.append({
                        "name": cityName,
                        "position": clickedMousePos
                    })
                    storeCities(cities)
                    cityName = ""
                else:
                    cityName += event.unicode

        surface.fill(0)
        surface.blit(image, (0, 0))
        pygame.draw.circle(surface, (255, 0, 255), clickedMousePos, 3)
        pygame.draw.circle(surface, (0, 255, 0), mousePos, 3)

        cities = loadCities()
        
        for city in cities:
            pygame.draw.circle(surface, (0, 0, 255), city["position"], 3)

        mousePosSurf = font.render(f"Mouse position: ({mousePos[0]}, {mousePos[1]})", True, (255, 0, 0) if not copied else (0, 0, 255), (0, 0, 0))
        surface.blit(mousePosSurf, (0, 0))

        mousePosSurf = font.render(f"Városnév: {cityName}", True, (0, 255, 0), (0, 0, 0))
        surface.blit(mousePosSurf, (0, surfaceSize[1] - mousePosSurf.get_height()))

        numCitiesSurf = font.render(f"Városok száma: {len(cities)}", True, (255, 255, 0), (0, 0, 0))
        surface.blit(numCitiesSurf, (surfaceSize[0] - numCitiesSurf.get_width(), 0))

        pygame.display.flip()

main()