import openpyxl
import sys

from fileUtils import *
from generatorUtil import *

def main():
    print("Digite 's' para gerar a partir de seeds")
    print("Digite 'f' para gerar a partir de conteúdo fixo")
    print("Digite 'c' para apenas gerar as combinações via seeds")
    print("Digite 'k' para gerar por seeds com estratégia SKAG")
    action = input("Selecione a ação: ")

    inputData = readInputData()
    if inputData is None:
        sys.exit(0)

    if action == 's':
        n_keywords = genKeywords(inputData["Seeds"])
        adgroups = genAdgroups(n_keywords)
        campaigns = genCampaigns(inputData["Campanha"])
        associate(campaigns, adgroups, n_keywords)

    elif action == 'c':
        n_keywords = genKeywords(inputData["Seeds"], "genKeywords_output.csv")
        print("Gerou %d keywords e salvou em genKeywords_output.csv" %n_keywords)

    elif action == 'k':
        campaigns = genCampaigns(inputData["Campanha"])
        for c in campaigns:
            print(c)
            input("Digite ENTER para continuar.")
            skags = genSKAG(c, inputData["Seeds"])
            if skags is None:
                continue
            associateSKAG(c, skags, inputData["Templates"])

    elif action == 'f':
        campaigns = genCampaigns(inputData["Campanha"])
        for c in campaigns:
            fixedCombination(campaigns, inputData["Keywords"])
    else:
        main()
        return

    for f in os.listdir():
        if "_temp_" in f:
            os.remove(f)

main()
