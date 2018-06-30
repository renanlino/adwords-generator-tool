from fileUtils import *
import os
from datetime import datetime
import re

MIN_TAIL = 2

conectors = initConectors()
print(conectors)

def genCampaigns(camps):
    campaigns = []
    for midia in camps[0]:
        for objetivo in camps[1]:
            for local in camps[2]:
                sigla = ""
                if len(local) < 3:
                    rg = local
                    sigla = local
                else:
                    rg = local.replace("de","").split(" ")
                    for part in rg:
                        if len(part) > 0:
                            sigla += part[0]
                for estrategia in camps[3]:
                    for ordem in camps[4]:
                        ordem = "%03d" %int(ordem)
                        for alvo in camps[5]:
                            for carreira in camps[6]:
                                campaign = "-".join( [midia, objetivo, sigla.lower(),
                                            estrategia, ordem, alvo, carreira] )

                            campaigns.append(campaign)
    return campaigns

def genAdgroups(n, n_max = 3000):
    adg_name = input("Digite o radical para compor o Adgroup: ")

    i = 0
    adgroups = []
    while i < n:
        adgroups.append(adg_name + "-%04d" %(i // n_max))
        i += n_max
    return adgroups

def genSKAG(c, seeds):
    print()
    print("1 CTA")
    print("2 Genéricos")
    print("3 Cargo")
    print("4 Qualidade")
    print("5 Curso")
    print("6 Linguagem")
    print("7 Framework")
    print("8 Área")
    print("9 Device")
    print("10 Plataforma")
    print("11 Serviços")
    print("12 Senioridade")
    print("13 Local")
    anchor = int(input("Digite o nome da coluna de referência: "))
    anchor = anchor - 1

    skagControl = loadSKAGControl(c)

    if skagControl is None:
        return None

    lastVersion = skagControl["versions"][-1]
    newVersion = {"adgroups":{},"date":datetime.now().strftime("%d/%m/%y %H:%M")}

    for adgroup_name in lastVersion["adgroups"]:
        newVersion["adgroups"][adgroup_name] = lastVersion["adgroups"][adgroup_name]

    skags = []

    for anchorSeed in seeds[anchor]:
        seedGroup = []
        for i in range(len(seeds)):
            if i != anchor:
                seedGroup.append(seeds[i])
            else:
                seedGroup.append([anchorSeed])
        skag_fname = "_tempSKAG_%s.csv" %anchorSeed

        generatedSeeds = genKeywords(seedGroup, skag_fname, passUser = True, returnSeed = True)

        keywords = [cleanGenerated(k) for k in generatedSeeds]

        os.remove(skag_fname)

        anchorSeed = anchorSeed.replace("-","_")
        print(anchorSeed)
        cores = {}
        for i in range (len(keywords)):
            keyword = keywords[i]
            keywordCore = keyword
            for word in conectors:
                keywordCore = keywordCore.replace(" " + word + " ", " ")

            if keywordCore not in cores:
                if anchorSeed in newVersion["adgroups"]:
                    newVersion["adgroups"][anchorSeed] += 1
                    cores[keywordCore] =  "-%04d" %newVersion["adgroups"][anchorSeed]
                else:
                    newVersion["adgroups"][anchorSeed] = 0
                    cores[keywordCore] =  "-%04d" %newVersion["adgroups"][anchorSeed]
            adg_associate = cores[keywordCore]

            entry = {
                "keyword" : keyword,
                "adg_name" : anchorSeed + adg_associate,
                "seed" : generatedSeeds[i]
            }
            print("\t%s (%s)" %(entry["keyword"], entry["adg_name"]))
            skags.append(entry)

    skagControl["versions"].append(newVersion)
    saveSKAGControl(skagControl)

    return skags

def cleanGenerated(seed):
    for i in range(len(seed)):
        if seed[i] == "*":
            seed[i] = ""
    # Conta entradas não vazias:
    notNull = 0
    for s in seed:
        if s != '':
            notNull += 1
    # Limite de tail:
    #if notNull < MIN_TAIL:
        #return None
    seedString = " ".join(seed) + "\r\n"
    # Remove espaços duplos
    while(True):
        newSeed = seedString.replace("  ", " ")
        if newSeed == seedString:
            break
        else:
            seedString = newSeed
    # Remove espaços iniciais e finais
    if seedString[0] == " ":
        seedString = seedString[1:len(seedString)]
    if seedString[-1] == " ":
        seedString = seedString[0:-1]

    seedString = seedString.replace("\r","").replace("\n","")

    return seedString

def genKeywords(seeds, out_filename="_temp_genKeywords.csv", passUser = False,
        returnSeed = False):
    prev = 1
    if returnSeed:
        toReturn = []
    for col in seeds:
        prev *= len(col)
    if not passUser:
        print("Vai gerar %d combinações. Pressione Enter para continuar" %prev)
        input()
    try:
        output = open(out_filename, "w", encoding="utf-16-le")
    except IOError:
        print("Erro ao abrir o arquivo temporário %s!" %out_filename)
        sys.exit(0)
    n = 0
    for cta in seeds[0]:
        for generic in seeds[1]:
            for cargo in seeds[2]:
                for qualidade in seeds[3]:
                    for curso in seeds[4]:
                        for linguagem in seeds[5]:
                            for framework in seeds[6]:
                                for area in seeds[7]:
                                    for device in seeds[8]:
                                        for plataforma in seeds[9]:
                                            for servicos in seeds[10]:
                                                for senioridade in seeds[11]:
                                                    for local in seeds[12]:
                                                        seed = [cta, generic, cargo, qualidade,
                                                        curso, linguagem, framework, area, device,
                                                        plataforma, servicos, senioridade, local]
                                                        if returnSeed:
                                                            toReturn.append(seed)
                                                        else:
                                                            seedString = cleanGenerated(seed)
                                                            if seedString is not None:
                                                                output.write(seedString + "\r\n")
                                                                n += 1
                                                            else:
                                                                continue
                                                            if not passUser:
                                                                print("%d (%.4f%%)" %(n, 100*n/prev) )
    output.close()
    if returnSeed:
        return toReturn
    else:
        return n

def genContent(templates, skag, strategy):
    content = []
    patternToSearch = '##.*##'
    patternToSearch = re.compile(patternToSearch)
    for template in templates:
        if template[6] == strategy:
            ad = []
            for i in range(len(template)-1):
                temp = template[i]
                for field in range(len(skag["seed"])):
                    if skag["seed"][field] == '':
                        continue
                    for function in ["u", "l", "t", "s", ""]:
                        pattern = "##%s%d##" %(function,field+1)
                        sWord = skag["seed"][field].replace("+","")
                        if function == "u":
                            temp = temp.replace(pattern, sWord.upper())
                        elif function == "l":
                            temp = temp.replace(pattern, sWord.lower())
                        elif function == "t":
                            temp = temp.replace(pattern, sWord.title())
                        elif function == "s":
                            if len(sWord) < 3:
                                sigla = sWord.upper()
                            else:
                                if sWord == "fortaleza":
                                    sigla = "ce"
                                else:
                                    complete_field = sWord.split(" ")
                                    sigla = ""
                                    for word in complete_field:
                                        if word in conectors:
                                            continue
                                        sigla += word[0].upper()
                            temp = temp.replace(pattern, sigla)
                        else:
                            temp = temp.replace(pattern, sWord)
                ad.append(temp)

            if len(ad[2]) > 80:
                print("\tAtenção! 'Descrição' do criativo para %s excede 80 caracteres." %skag["adg_name"])
                print("\t\t%s" %ad[2])
            good = True
            for field in ad:
                if patternToSearch.search(field):
                    good = False
                    print("\tAtenção! Criativo para %s contém padrão não substituído. Ignorando." %skag["adg_name"])
                    print("\t\t%s" %field)
                    break
            if good:
                content.append(ad)
    return content

def fixedCombination(campaigns, keywords):
    out_filename = input("Digite o nome do arquivo de saída (output.csv): ")
    if out_filename == "":
        out_filename = "output.csv"
    try:
        output = open(out_filename, "w", encoding="utf-16-le")
    except IOError:
        print("Erro ao abrir o arquivo de saída %s. Talvez ele esteja aberto em outro programa?" %out_filename)
        return None

    writeCSVEntry(output, output_hdr)
    for c in campaigns:
        print(c)
        initCampaing(c, output)
        for entry in keywords:
            adg_name = entry[1]
            initAdgroup(c, adg_name, output)
            writeKeywordEntry(c, adg_name, entry[0], output)
    output.close()

def associate(camps, adg, n_key, n_max = 3000, keyword_filename = "_temp_genKeywords.csv"):

    out_filename = input("Digite o nome do arquivo de saída (output.csv): ")
    if out_filename == "":
        out_filename = "output.csv"

    try:
        output = open(out_filename, "w", encoding="utf-16-le")
    except IOError:
        print("Erro ao abrir o arquivo de saída %s. Talvez ele esteja aberto em outro programa?" %out_filename)
        return None

    try:
        keywords_file = open(keyword_filename, "r", encoding="utf-16-le")
    except IOError:
        print("Erro ao abrir o arquivo temporário %s" %keyword_filename)
        return None

    writeCSVEntry(output, output_hdr)

    for c in camps:
        initCampaing(c, output)
        for a in adg:
            initAdgroup(c, a, output)

    for c in camps:
        print(c)
        keywords_file.seek(0,0)
        for a in adg:
            print("\t" + a)
            i = 0
            while i < n_max and i < n_key:
                k = keywords_file.readline().replace("\r", "").replace("\n","")
                print("\t\t" + k)
                writeKeywordEntry(c, a, k, output)
                i += 1

    output.close()

def associateSKAG(c, skags, templates):
    c_list = c.split("-")
    defult_fname = "%s %s %s.csv" %(c_list[2].upper(), c_list[3].title(), c_list[4])
    out_filename = input("Digite o nome do arquivo de saída (%s): " %defult_fname)
    if out_filename == "":
        out_filename = defult_fname

    try:
        output = open(out_filename, "w", encoding="utf-16-le")
    except IOError:
        print("Erro ao abrir o arquivo de saída %s. Talvez ele esteja aberto em outro programa?" %out_filename)
        return None

    writeCSVEntry(output, output_hdr)

    initCampaing(c, output)
    for skag in skags:
        strat = c.split("-")[3]
        ads = genContent(templates, skag, strat)
        if len(ads) > 0:
            initAdgroup(c, skag["adg_name"], output)
            writeKeywordEntry(c, skag["adg_name"], skag["keyword"], output)
            for ad in ads:
                writeAdEntry(c, skag["adg_name"], ad, output)
        else:
            print("Ad Group %s (%s) não contém anúncios válidos. Pulando." %(skag["adg_name"], skag["keyword"]))

    output.close()

def initCampaing(c, output, dailybudget = 10.0):
    to_output = [k for k in output_template]
    to_output[output_map["Campaign"]]=c
    to_output[output_map["Campaign Daily Budget"]] = "%.2f" %dailybudget
    to_output[output_map["Campaign Type"]] = "Search Network only"
    to_output[output_map["Networks"]] = "Google search;Search Partners"
    to_output[output_map["Languages"]] = "pt"
    to_output[output_map["Bid Strategy Type"]] = "Manual CPC"
    to_output[output_map["Enhanced CPC"]] = "Enabled"
    to_output[output_map["Ad rotation"]] = "Optimize for clicks"
    to_output[output_map["Delivery method"]] = "Standard"
    to_output[output_map["Targeting method"]] = "Location of presence or Area of interest"
    to_output[output_map["Exclusion method"]] = "Location of presence or Area of interest"
    to_output[output_map["DSA targeting source"]] = "Google"
    to_output[output_map["Flexible Reach"]] = "[]"
    to_output[output_map["Campaign Status"]] = "Enabled"
    writeCSVEntry(output, to_output)

def initAdgroup(c, a, output, cpc = 0.9, cpm = 5.0):
    to_output = [k for k in output_template]
    to_output[output_map["Campaign"]]=c
    to_output[output_map["Ad Group"]]=a
    to_output[output_map["Max CPC"]]="%.2f" %cpc
    to_output[output_map["Max CPM"]]="%.2f" %cpm
    to_output[output_map["CPA Bid"]]="%.2f" %(0.0)
    to_output[output_map["Flexible Reach"]]="[]"
    to_output[output_map["Targeting optimization"]]="Disabled"
    to_output[output_map["Ad Group Type"]]="Default"
    writeCSVEntry(output, to_output)
