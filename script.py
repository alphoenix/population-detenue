import xlrd,csv,sys,urllib,requests,PyPDF2,re,pandas,time
from tabula import read_pdf


## MISE EN FORME DE LA DATE
def setDate(date):
    d,m,y = date.split(" ")
    if(d=="1er"):
        d="01"
    mois = {"janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","août":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12"}
    return d+"/"+mois.get(m)+"/"+y


## RÉCUPÉRATION DES DONNÉES SUR LES ÉTABLISSEMENTS DANS LES FICHIERS EXCEL
def getFileEtab(liste):
    ## Variables
    localisation = ["tab14 Bordeaux","tab15 Dijon","tab16 Lille","tab17 Lyon","tab18 marseille","tab19 paris","tab20 Rennes","tab21 Strasbourg","tab22 Toulouse","tab23 DOM"]
    etabs = ["MA","qMA","CD","qCD","MC","qMC","CPA","qCPA","CSL","qCSL","EPM","qM","CNE","qCNE"]

    print("Ouverture du fichier csv")
    mon_csv = open('population-detenue-all.csv','w')
    wr = csv.writer(mon_csv,quoting=csv.QUOTE_ALL)

    wr.writerow(["Direction","Màj Effectif","Màj Capacité","Établissement","Lieu","Capacité norme","Capacité opérationelle","Valeur","Densité"])

    print("Accès aux fichiers")
    for url in liste:
        print("Téléchargement de "+url)
        fichier, headers = urllib.request.urlretrieve(url)
        classeur = xlrd.open_workbook(fichier)
        feuilles = classeur.sheet_names()

        print("Récupération des feuilles")
        for feuille in feuilles:
            if(feuille in localisation):
                print("Traitement de "+feuille)
                feuille_act = classeur.sheet_by_name(feuille)
                if(feuille_act.cell_value(1,5) == ""):
                    direction = feuille_act.cell_value(1,4)
                else:
                    direction = feuille_act.cell_value(1,5)
                if(feuille_act.cell_value(2,0)=="Effectif au :"):
                    date_effectif = setDate(feuille_act.cell_value(2,1).strip())
                elif(feuille_act.cell_value(3,0)=="Effectif au :"):
                    date_effectif = setDate(feuille_act.cell_value(3,1).strip())
                else:
                    date_effectif = ""
                if(feuille_act.cell_value(5,0)=="Capacités au :"):
                    date_capacite = setDate(feuille_act.cell_value(5,1).strip())
                else:
                    date_capacite = ""
                for ligne in range(8,feuille_act.nrows):
                    if(feuille_act.cell_value(ligne,1) in etabs):
                        etab = feuille_act.cell_value(ligne,1)
                        lieu = feuille_act.cell_value(ligne,2)
                        capacite_norme = feuille_act.cell_value(ligne,3)
                        capacite_ope = feuille_act.cell_value(ligne,4)
                        personnes = feuille_act.cell_value(ligne,5)
                        densite = feuille_act.cell_value(ligne,6)
                        wr.writerow([direction,date_effectif,date_capacite,etab,lieu,capacite_norme,capacite_ope,personnes,densite])
                    ligne += 1

    mon_csv.close()

## RÉCUPÉRATION DES DONNÉES SUR LA DENSITÉ DANS LES FICHIERS EXCEL
def getFileDensite(liste):
    ## Variables
    print("Ouverture du fichier csv")
    mon_csv = open('densite-all.csv','w')
    wr = csv.writer(mon_csv,quoting=csv.QUOTE_ALL)

    wr.writerow(["Màj Effectif","Capacité opérationelle","Détenus","Prévenus"])

    print("Accès aux fichiers")
    for url in liste:
        print("Téléchargement de "+url)
        time.sleep(5)
        fichier, headers = urllib.request.urlretrieve(url)
        classeur = xlrd.open_workbook(fichier)
        feuilles = classeur.sheet_names()

        print("Récupération des feuilles")

        if("Les chiffres du mois" in feuilles):
            feuille = "Les chiffres du mois"
        elif("les chiffres du mois" in feuilles):
            feuille = "les chiffres du mois"
        elif("chiffres du mois" in feuilles):
            feuille = "chiffres du mois"

        feuille_act = classeur.sheet_by_name(feuille)

        if(feuille_act.cell_value(0,-1)!=""):
            date_effectif = setDate(feuille_act.cell_value(0,-1).strip())
        else:
            date_effectif = ""

        if(feuille_act.cell_value(-1,0)=="nombre de places opérationnelles : "):
            capacite_ope = feuille_act.cell_value(-1,3)
        elif(feuille_act.cell_value(15,0)=="Nombre de places opérationnelles"):
            capacite_ope = feuille_act.cell_value(15,3)
        elif(feuille_act.cell_value(30,0)=="Nombre de places opérationnelles : "):
            capacite_ope = feuille_act.cell_value(30,3)
        else:
            capacite_ope = ""

        if(feuille_act.cell_value(10,0)=="Ecroués détenus"):
            detenus = feuille_act.cell_value(10,2)
        elif(feuille_act.cell_value(12,0)=="écroués détenus"):
            detenus = feuille_act.cell_value(12,2)
        elif(feuille_act.cell_value(13,0)=="écroués détenus"):
            detenus = feuille_act.cell_value(13,2)
        elif(feuille_act.cell_value(14,0)=="écroués détenus"):
            detenus = feuille_act.cell_value(13,2)
        else:
            detenus = ""

        if(feuille_act.cell_value(11,0)=="dont prévenus"):
            prevenus = feuille_act.cell_value(11,2)
        elif(feuille_act.cell_value(13,0)=="dont prévenus"):
            prevenus = feuille_act.cell_value(13,2)
        elif(feuille_act.cell_value(14,0)=="dont prévenus"):
            prevenus = feuille_act.cell_value(14,2)
        elif(feuille_act.cell_value(15,0)=="dont prévenus"):
            prevenus = feuille_act.cell_value(15,2)
        else:
            prevenus = ""

        print("Infos récupérées pour le "+date_effectif)

        wr.writerow([date_effectif,capacite_ope,detenus,prevenus])

    mon_csv.close()

## SUPPRIMER LES ESPACES ET RETOURNER DEUX COLONNES
def getSpace(string):
    if(re.search("^[0-9]+ [0-9]+$",string)):
        text = re.split("\s",string)
        return text[0],text[1]
    elif(re.search("^[0-9]+ [0-9]+ [0-9]+ [0-9]+$",string)):
        text = re.split("\s",string)
        return text[0]+text[1],text[2]+text[3]
    else:
        return "",""

## CREER UN DATAFRAME À PARTIR DES PDF
def createDF(pageNumber,url,args):
    df = read_pdf(url,pages=pageNumber)

    ## Ajout des trois colonnes dans les arguments
    df['direction'] = args[0]
    if(args[1]!=""):
        df['date_effectif'] = setDate(args[1])
    else:
        df['date_effectif'] = ""
    if(args[2]!=""):
        df['date_capacite'] = setDate(args[2])
    else:
        df['date_capacite'] = ""

    ### Réorganisation et nettoyage
    if(len(df.columns) == 9 and args[0] != "Mission Outre-Mer"): ## Normal
        print("Cas normal, avec neuf colonnes")
        df.columns = ["Établissement","","Capacité norme","Capacité opérationelle","Valeur","Densité","Direction","Màj Effectif","Màj Capacité"]

    elif(len(df.columns) == 8): ## Paris / Marseille
        print("Cas particulier, avec huit colonnes")
        df["Capacité norme"],df["Capacité opérationelle"] = zip(*df.iloc[:,2].apply(getSpace))
        df = df.drop(df.columns[2],axis=1)
        df = df.iloc[1:]
        df.columns = ["Établissement","","Valeur","Densité","Direction","Màj Effectif","Màj Capacité","Capacité norme","Capacité opérationelle"]
        df = df[["Établissement","","Capacité norme","Capacité opérationelle","Valeur","Densité","Direction","Màj Effectif","Màj Capacité"]]

    elif(len(df.columns) == 9 and args[0] == "Mission Outre-Mer"):
        print("Cas particulier de l'outre-mer, avec neuf colonnes")
        df["Capacité norme"],df["Capacité opérationelle"] = zip(*df.iloc[:,3].apply(getSpace))
        df = df.drop(df.columns[3],axis=1)
        df = df.iloc[1:]
        df = df.drop(df.columns[0],axis=1)
        df.columns = ["Établissement","","Valeur","Densité","Direction","Màj Effectif","Màj Capacité","Capacité norme","Capacité opérationelle"]
        df = df[["Établissement","","Capacité norme","Capacité opérationelle","Valeur","Densité","Direction","Màj Effectif","Màj Capacité"]]   

    elif(len(df.columns) == 10): ## Outre-mer
        print("Cas particulier de l'outre-mer, avec dix colonnes")
        df = df.drop(df.columns[0],axis=1)
        df.columns = ["Établissement","","Capacité norme","Capacité opérationelle","Valeur","Densité","Direction","Màj Effectif","Màj Capacité"]

    df["Densité"] = df["Densité"].str.replace(' ','').str.replace(',','.')
    df["Valeur"] = df["Valeur"].str.replace(' ','').str.replace(',','.')
    df["Capacité norme"] = df["Capacité norme"].str.replace(' ','')
    df = df[df["Établissement"].str.startswith(("MA","qMA","CD","qCD","MC","qMC","CPA","qCPA","CSL","qCSL","EPM","qM","CNE","qCNE"),na=False)]
    df["Établissement"],df["Lieu"] = zip(*df["Établissement"].str.split(' ',1))
    df = df.drop(df.columns[1],axis=1)

    df = df[["Direction","Màj Effectif","Màj Capacité","Établissement","Lieu","Capacité norme","Capacité opérationelle","Valeur","Densité"]]

    return df

## RÉCUPÉRER LES DONNÉES SUR LES ÉTABLISSEMENTS DANS LES PDFS
def getFilePDFEtab(url,nom):
    # fichier, headers = urllib.request.urlretrieve(url)
    fichier = open(url,'rb')
    data  = pandas.DataFrame()

    for i in range(0,20):
        pageNumber = 17+i
        pdfReader = PyPDF2.PdfFileReader(fichier)
        pagePDF = pdfReader.getPage(pageNumber-1)
        text = pagePDF.extractText()
        try:
            d = re.search('Tableau ([0-9]+)\s*(Répartition des personnes détenues|Population écrouée détenue) par établissemen\s*t\s*(Dire\s*cti\s*on In\s*terrégionale de \w+|Mission\s+Outre-Mer)',text)
            direction = d.group(3)
        except:
            direction = ""
        try:
            e = re.search('Effectif au :\s*(\w+ \w+ \w+)',text)
            date_effectif = e.group(1)
        except:
            date_effectif = ""
        try:
            c = re.search('Capacités au :\s*(\w+ \w+ \w+)',text)
            date_capacite = c.group(1)
        except:
            date_capacite = ""
        
        if(direction != ""):
            print("Lecture de la page "+direction+" ("+str(pageNumber)+")")
            df = createDF(pageNumber,url,[direction,date_effectif,date_capacite])
            data = data.append(df)

    data.to_csv('population-detenue-'+nom+'.csv',index=False)

## RÉCUPÉRER LES INFOS SUR LA DENSITÉ DANS LES PDF
def getPDFdens(url):
    fichier, headers = urllib.request.urlretrieve(url)
    pdfReader = PyPDF2.PdfFileReader(fichier)

    pagePDF = pdfReader.getPage(0)
    text = pagePDF.extractText()

    try:
        d = re.search('situation au (\w+ \w+ [0-9]{4})',text)
        date_effectif = setDate(d.group(1))
    except:
        date_effectif = ""

    pagePDF = pdfReader.getPage(2)
    text = pagePDF.extractText()
    
    try:
        d = re.search('nombre de places opérationnelles : ([0-9]+ [0-9]+)',text)
        capacite_ope = d.group(1).replace(' ','')
    except:
        capacite_ope = ""

    df = read_pdf(fichier,pages=3,lattice=True)

    detenus = (df.iloc[4,0]).replace(' ','')
    prevenus = (df.iloc[5,0]).replace(' ','')

    return [date_effectif,capacite_ope,detenus,prevenus]

## FONCTION QUI RÉCUPÈRE TOUTES LES INFOS SUR LES ÉTABLISSEMENTS
def populationDetenue():
    ### Récupérer les derniers chiffres
    print("Récupérer les derniers chiffres (PDF)")
    getFilePDFEtab('./docs/mensuelle_decembre_2018.pdf','dec')
    getFilePDFEtab('./docs/mensuelle_novembre_2018.pdf','nov')
    getFilePDFEtab('./docs/mensuelle_octobre_2018_.pdf','oct')
    getFilePDFEtab('./docs/mensuelle_septembre_2018.pdf','sep')
    getFilePDFEtab('./docs/mensuelle_aout_2018.pdf','aug')

    ### Récupérer les chiffres disponibles avant le 1er décembre 2013
    print("Récupérer les chiffres dispos pour 2012 et 2013 (PDF)")
    getFilePDFEtab('./docs/mensuelle_novembre_2012.pdf','nov2012')

    getFilePDFEtab('./docs/mensuelle_novembre_2013.pdf','nov2013')
    getFilePDFEtab('./docs/mensuelle_octobre_2013.pdf','oct2013')
    getFilePDFEtab('./docs/mensuelle_septembre_2013.pdf','sep2013')

    ### Récupérer tous les chiffres sur Excels
    print("Récupérer les derniers chiffres (Excels)")
    urls=["https://www.data.gouv.fr/fr/datasets/r/9cdc7757-c565-4bd4-88ba-54aa35e61af9","https://www.data.gouv.fr/fr/datasets/r/9913894c-9e12-4892-9ae6-f79f203e0d24","https://www.data.gouv.fr/fr/datasets/r/01b12ffb-981f-4ae0-b97b-cc29b91410ab","https://www.data.gouv.fr/fr/datasets/r/919e67bf-cf18-4c88-a164-24fd09139597","https://www.data.gouv.fr/fr/datasets/r/4b3fac9c-5dfc-425a-92a1-a1b57701a874","https://www.data.gouv.fr/fr/datasets/r/a3148c2f-e838-4edc-a61c-61d5bb136f4b","https://www.data.gouv.fr/fr/datasets/r/753d2701-3915-42f5-b916-213828a2dc66","https://www.data.gouv.fr/fr/datasets/r/abe5b1ec-b132-46f0-bf66-1062098ab114","https://www.data.gouv.fr/fr/datasets/r/acc4a891-7810-4995-8e35-51d5bb18a0ae","https://www.data.gouv.fr/fr/datasets/r/a689de85-e50b-48cc-aa3c-4b8a3e159ee4","https://www.data.gouv.fr/fr/datasets/r/577023e9-a888-47eb-8ff2-bb2b4db7b691","https://www.data.gouv.fr/fr/datasets/r/44c1665d-c4e6-475f-9422-0822368b83c0","https://www.data.gouv.fr/fr/datasets/r/c8765aaa-0dfb-40e1-ad53-f8346743cfe5","https://www.data.gouv.fr/fr/datasets/r/dbda0a65-4462-45c8-b911-44ceea0ff1ad","https://www.data.gouv.fr/fr/datasets/r/7c12395b-62a0-4eed-873f-4314281f1906","https://www.data.gouv.fr/fr/datasets/r/f190f91b-64cb-436b-ac28-1f0c6639d9bc","https://www.data.gouv.fr/fr/datasets/r/85fb09e0-5889-48e6-9879-358f356957bb","https://www.data.gouv.fr/fr/datasets/r/69c1f4b7-1e07-4344-b83e-84c0964ed169","https://www.data.gouv.fr/fr/datasets/r/92b78872-3579-4c92-8f34-a513f8ab1cbf","https://www.data.gouv.fr/fr/datasets/r/d785bb79-895e-48e2-b3d1-790f53f9c858","https://www.data.gouv.fr/fr/datasets/r/a5ef683a-25d9-4730-a0a6-cd0c623d307a","https://www.data.gouv.fr/fr/datasets/r/7d3c0318-6ee7-4ca9-887b-476e6bcf569e","https://www.data.gouv.fr/fr/datasets/r/991756d0-a599-4952-8fbb-b7026bcf8e73","https://www.data.gouv.fr/fr/datasets/r/af0e1e64-cf9d-4ece-8966-ffc9a628ff41","https://www.data.gouv.fr/fr/datasets/r/ee8d4ef0-f668-4f68-a602-2af89d9e49d7","https://www.data.gouv.fr/fr/datasets/r/e107d387-b88a-4ede-9630-113b25ce52c1","https://www.data.gouv.fr/fr/datasets/r/b34aeea6-3613-4a2b-959e-e1489b8bb630","https://www.data.gouv.fr/fr/datasets/r/51eb8a05-2100-4d25-89cb-cb7dfc77096b","https://www.data.gouv.fr/fr/datasets/r/a8e4b083-c84a-437d-a380-5f72362774b0","https://www.data.gouv.fr/fr/datasets/r/4be3c427-55f3-4e21-ac91-afb876913d23","https://www.data.gouv.fr/fr/datasets/r/cf48e810-f15d-4ffc-b762-b41a91fd04af","https://www.data.gouv.fr/fr/datasets/r/ca31dddc-0a33-40ca-aec0-2cffc50182eb","https://www.data.gouv.fr/fr/datasets/r/9c756d6b-3467-4a9d-9354-c80c62949b43","https://www.data.gouv.fr/fr/datasets/r/89de43fb-9a43-4cfd-9ccd-7e602a263115","https://www.data.gouv.fr/fr/datasets/r/06eb8195-6816-4efc-bd4e-619f915b1e15","https://www.data.gouv.fr/fr/datasets/r/518386a6-d846-4f8c-80eb-169bdab46087","https://www.data.gouv.fr/fr/datasets/r/9740af0a-f31c-4358-b6f5-df94b67bdbe4","https://www.data.gouv.fr/fr/datasets/r/c262a3d8-bd79-460c-92c7-ee9ea659d409","https://www.data.gouv.fr/fr/datasets/r/3dfba73c-e672-4f23-8932-afe7d2130644","https://www.data.gouv.fr/fr/datasets/r/b3c7a161-3c17-4d39-b84f-987abe733c8b","https://www.data.gouv.fr/fr/datasets/r/2c279519-db10-4de8-bb53-d74b606109d8","https://www.data.gouv.fr/fr/datasets/r/6b8f8695-7fb9-48b2-b845-4fb6cea4478c","https://www.data.gouv.fr/fr/datasets/r/cfdeb184-39d9-4c7d-94e4-5e8487b203dd","https://www.data.gouv.fr/fr/datasets/r/f9316d50-5c4d-4779-9cdb-c3eb9a452a1b","https://www.data.gouv.fr/fr/datasets/r/20089aea-2aef-493d-a464-f8f3137d1a56","https://www.data.gouv.fr/fr/datasets/r/2b81ef56-9b57-4e05-adbc-6c030cf7b312","https://www.data.gouv.fr/fr/datasets/r/b7a5c653-6c4f-498f-9ab8-c84864dcf375","https://www.data.gouv.fr/fr/datasets/r/37a5db74-fdcb-4304-bb29-8d5f9782b608","https://www.data.gouv.fr/fr/datasets/r/25c57bc4-3e37-4a1b-b2a0-70b3816d829d","https://www.data.gouv.fr/fr/datasets/r/ec671caf-2681-4900-893b-f541ee682d84","https://www.data.gouv.fr/fr/datasets/r/7e5d2323-e2e1-4033-9d0a-1849df89d8a4","https://www.data.gouv.fr/fr/datasets/r/b5ce0b39-aa03-4c05-8af6-f2ada34bc5a0","https://www.data.gouv.fr/fr/datasets/r/80f83ef3-b23f-47d4-8f15-375c9617b77d","https://www.data.gouv.fr/fr/datasets/r/d31abf7c-618d-4fe8-ac74-f7f7e532f147","https://www.data.gouv.fr/fr/datasets/r/d3bbf32e-eac2-4a6f-bd2f-8357ca975765","https://www.data.gouv.fr/fr/datasets/r/4ef96c71-98a1-40c3-9947-b01b30b92fa2","https://www.data.gouv.fr/fr/datasets/r/ff18ab5e-8449-44cc-bc6d-6e6a72b3ffb5","https://www.data.gouv.fr/fr/datasets/r/97bf0922-8504-44b8-a44b-1b90ed82dde4","https://www.data.gouv.fr/fr/datasets/r/00f11b94-ab6e-417f-a045-5ad71451ea10","https://www.data.gouv.fr/fr/datasets/r/7da2d9ce-4467-48a5-b331-c7eb2d738a40","https://www.data.gouv.fr/fr/datasets/r/ca9a8121-6614-4e99-98f7-0fe7f9c87f9e","https://www.data.gouv.fr/fr/datasets/r/0525cefa-67be-4a42-acc8-cba1ce343e14","https://www.data.gouv.fr/fr/datasets/r/8e8d614a-7f05-426f-8134-451a0f4da05e","https://www.data.gouv.fr/fr/datasets/r/5d2732d1-7ca7-4836-b3cc-ad98f092abc7","https://www.data.gouv.fr/fr/datasets/r/2f08e290-13b5-4cec-bda0-8ac847ef4cc2","https://www.data.gouv.fr/fr/datasets/r/122eaed1-af0e-40d2-b9f0-854e04117672","https://www.data.gouv.fr/fr/datasets/r/e357cfb4-3ed0-42b5-b46b-e80942e5c121","https://www.data.gouv.fr/fr/datasets/r/3f1c0f6b-4122-49cc-9ef1-33384d4bc74f","https://www.data.gouv.fr/fr/datasets/r/717d3e44-24bf-43a8-935c-0ed824fa61c5","https://www.data.gouv.fr/fr/datasets/r/288fc251-cafc-4803-be66-8038050bbae9","https://www.data.gouv.fr/fr/datasets/r/a50754c0-5f0d-4051-8e48-3a5a802ad860","https://www.data.gouv.fr/fr/datasets/r/99ff38d2-e0bd-4503-a57d-c6b657404c31","https://www.data.gouv.fr/fr/datasets/r/3fd3b9dc-5a94-4f61-acb4-a79f4c04e3bb","https://www.data.gouv.fr/fr/datasets/r/70ec7f0a-f92d-4145-91dd-7e5ede6fd9a4","https://www.data.gouv.fr/fr/datasets/r/27a238bd-0282-412c-bf7d-5d8988511069","https://www.data.gouv.fr/fr/datasets/r/229f8f3e-81ed-4d55-b1a4-bab6e4e400ad","https://www.data.gouv.fr/fr/datasets/r/fa2ee610-c08b-459e-8423-cf3409b4c3b5","https://www.data.gouv.fr/fr/datasets/r/81dc6b33-d585-4b6e-bc19-4c8363033032","https://www.data.gouv.fr/fr/datasets/r/04f4f815-b5ae-475d-877c-842cc46fa0b7","https://www.data.gouv.fr/fr/datasets/r/05cd4e66-4bae-488a-93ad-5c5e748f89db","https://www.data.gouv.fr/fr/datasets/r/f76f0ca6-4a0e-40c8-8231-c95d94f0dd91","https://www.data.gouv.fr/fr/datasets/r/75c5ca27-57d7-4ded-88e7-50a41d567e57","https://www.data.gouv.fr/fr/datasets/r/39596a0e-9854-4286-80ca-5257c5f83fc4","https://www.data.gouv.fr/fr/datasets/r/0d86fafa-37f8-4571-bc51-0978b42a4dbd","https://www.data.gouv.fr/fr/datasets/r/0af68264-17a4-40b0-834b-9e04d7501d79","https://www.data.gouv.fr/fr/datasets/r/5456fd17-d8ac-4533-a5b1-c8d431d2f46e","https://www.data.gouv.fr/fr/datasets/r/5592a5dc-04b6-42a0-88bb-c514699bae05","https://www.data.gouv.fr/fr/datasets/r/cf095e7d-9f18-4007-a1f2-7026714fa631","https://www.data.gouv.fr/fr/datasets/r/58d4e6b6-fa2c-437f-b08e-b993ead1f28d","https://www.data.gouv.fr/fr/datasets/r/c28e1f19-47eb-46cd-bd99-311951a2d422","https://www.data.gouv.fr/fr/datasets/r/7001e0dd-5a5a-47b9-9812-04ce38a00406","https://www.data.gouv.fr/fr/datasets/r/ff7a9197-9436-4a93-9d84-356b44fd338a","https://www.data.gouv.fr/fr/datasets/r/c344de59-0240-44d4-b10f-e8a68fbd547b","https://www.data.gouv.fr/fr/datasets/r/02850685-ed28-4083-a7db-9b322f3504f9","https://www.data.gouv.fr/fr/datasets/r/f27b421e-ed3a-4415-a7d7-7c061693cfd9","https://www.data.gouv.fr/fr/datasets/r/836dd173-c78e-426a-9cee-397b9864a71f","https://www.data.gouv.fr/fr/datasets/r/75ca86a5-a332-460c-9dab-b2a3e8c1f905","https://www.data.gouv.fr/fr/datasets/r/d868d268-5444-4380-b0c2-72c746205695","https://www.data.gouv.fr/fr/datasets/r/246e2242-3a80-4048-bf07-acf6a60d5804","https://www.data.gouv.fr/fr/datasets/r/f33cffd7-f772-4b38-99ee-60da38ff3f1b","https://www.data.gouv.fr/fr/datasets/r/68f46314-7719-429d-b9ad-d8297fd390e8","https://www.data.gouv.fr/fr/datasets/r/3404ea8e-12ef-4958-abf4-5563d966c3de","https://www.data.gouv.fr/fr/datasets/r/42eb2b68-b448-4c54-8139-04188bbcf898"]
    # getFileEtab(urls)

## RÉCUPÉRER LES DENSITÉS DANS LES PDF (PAS OPTIMAL)
def getDens():
    # urls09 = ["http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_decembre09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_nov09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_oct09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_sept09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_aout09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERne_juillet09t.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_juin09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_mai09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_avr09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_mars09.pdf","http://www.justice.gouv.fr/art_pix/stat_population_ecrouee_detenue_France_internet_fevrier09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_janv09.pdf"]
    urls09 = ["http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_aout09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERne_juillet09t.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_juin09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_mai09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_avr09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_mars09.pdf","http://www.justice.gouv.fr/art_pix/stat_population_ecrouee_detenue_France_internet_fevrier09.pdf","http://www.justice.gouv.fr/art_pix/mensuelle_inTERnet_janv09.pdf"]

    print("Ouverture du fichier csv")
    mon_csv = open('densite-09.csv','w')
    wr = csv.writer(mon_csv,quoting=csv.QUOTE_ALL)

    wr.writerow(["Màj Effectif","Capacité opérationelle","Détenus","Prévenus"])

    for url in urls09:
        print("Analyse de "+url)
        wr.writerow(getPDFdens(url))
        time.sleep(20)

## DIVERS TESTS

# populationDetenue()

# urls=["https://www.data.gouv.fr/fr/datasets/r/9cdc7757-c565-4bd4-88ba-54aa35e61af9","https://www.data.gouv.fr/fr/datasets/r/9913894c-9e12-4892-9ae6-f79f203e0d24","https://www.data.gouv.fr/fr/datasets/r/01b12ffb-981f-4ae0-b97b-cc29b91410ab","https://www.data.gouv.fr/fr/datasets/r/919e67bf-cf18-4c88-a164-24fd09139597","https://www.data.gouv.fr/fr/datasets/r/4b3fac9c-5dfc-425a-92a1-a1b57701a874","https://www.data.gouv.fr/fr/datasets/r/a3148c2f-e838-4edc-a61c-61d5bb136f4b","https://www.data.gouv.fr/fr/datasets/r/753d2701-3915-42f5-b916-213828a2dc66","https://www.data.gouv.fr/fr/datasets/r/abe5b1ec-b132-46f0-bf66-1062098ab114","https://www.data.gouv.fr/fr/datasets/r/acc4a891-7810-4995-8e35-51d5bb18a0ae","https://www.data.gouv.fr/fr/datasets/r/a689de85-e50b-48cc-aa3c-4b8a3e159ee4","https://www.data.gouv.fr/fr/datasets/r/577023e9-a888-47eb-8ff2-bb2b4db7b691","https://www.data.gouv.fr/fr/datasets/r/44c1665d-c4e6-475f-9422-0822368b83c0","https://www.data.gouv.fr/fr/datasets/r/c8765aaa-0dfb-40e1-ad53-f8346743cfe5","https://www.data.gouv.fr/fr/datasets/r/dbda0a65-4462-45c8-b911-44ceea0ff1ad","https://www.data.gouv.fr/fr/datasets/r/7c12395b-62a0-4eed-873f-4314281f1906","https://www.data.gouv.fr/fr/datasets/r/f190f91b-64cb-436b-ac28-1f0c6639d9bc","https://www.data.gouv.fr/fr/datasets/r/85fb09e0-5889-48e6-9879-358f356957bb","https://www.data.gouv.fr/fr/datasets/r/69c1f4b7-1e07-4344-b83e-84c0964ed169","https://www.data.gouv.fr/fr/datasets/r/92b78872-3579-4c92-8f34-a513f8ab1cbf","https://www.data.gouv.fr/fr/datasets/r/d785bb79-895e-48e2-b3d1-790f53f9c858","https://www.data.gouv.fr/fr/datasets/r/a5ef683a-25d9-4730-a0a6-cd0c623d307a","https://www.data.gouv.fr/fr/datasets/r/7d3c0318-6ee7-4ca9-887b-476e6bcf569e","https://www.data.gouv.fr/fr/datasets/r/991756d0-a599-4952-8fbb-b7026bcf8e73","https://www.data.gouv.fr/fr/datasets/r/af0e1e64-cf9d-4ece-8966-ffc9a628ff41","https://www.data.gouv.fr/fr/datasets/r/ee8d4ef0-f668-4f68-a602-2af89d9e49d7","https://www.data.gouv.fr/fr/datasets/r/e107d387-b88a-4ede-9630-113b25ce52c1","https://www.data.gouv.fr/fr/datasets/r/b34aeea6-3613-4a2b-959e-e1489b8bb630","https://www.data.gouv.fr/fr/datasets/r/51eb8a05-2100-4d25-89cb-cb7dfc77096b","https://www.data.gouv.fr/fr/datasets/r/a8e4b083-c84a-437d-a380-5f72362774b0","https://www.data.gouv.fr/fr/datasets/r/4be3c427-55f3-4e21-ac91-afb876913d23","https://www.data.gouv.fr/fr/datasets/r/cf48e810-f15d-4ffc-b762-b41a91fd04af","https://www.data.gouv.fr/fr/datasets/r/ca31dddc-0a33-40ca-aec0-2cffc50182eb","https://www.data.gouv.fr/fr/datasets/r/9c756d6b-3467-4a9d-9354-c80c62949b43","https://www.data.gouv.fr/fr/datasets/r/89de43fb-9a43-4cfd-9ccd-7e602a263115","https://www.data.gouv.fr/fr/datasets/r/06eb8195-6816-4efc-bd4e-619f915b1e15","https://www.data.gouv.fr/fr/datasets/r/518386a6-d846-4f8c-80eb-169bdab46087","https://www.data.gouv.fr/fr/datasets/r/9740af0a-f31c-4358-b6f5-df94b67bdbe4","https://www.data.gouv.fr/fr/datasets/r/c262a3d8-bd79-460c-92c7-ee9ea659d409","https://www.data.gouv.fr/fr/datasets/r/3dfba73c-e672-4f23-8932-afe7d2130644","https://www.data.gouv.fr/fr/datasets/r/b3c7a161-3c17-4d39-b84f-987abe733c8b","https://www.data.gouv.fr/fr/datasets/r/2c279519-db10-4de8-bb53-d74b606109d8","https://www.data.gouv.fr/fr/datasets/r/6b8f8695-7fb9-48b2-b845-4fb6cea4478c","https://www.data.gouv.fr/fr/datasets/r/cfdeb184-39d9-4c7d-94e4-5e8487b203dd","https://www.data.gouv.fr/fr/datasets/r/f9316d50-5c4d-4779-9cdb-c3eb9a452a1b","https://www.data.gouv.fr/fr/datasets/r/20089aea-2aef-493d-a464-f8f3137d1a56","https://www.data.gouv.fr/fr/datasets/r/2b81ef56-9b57-4e05-adbc-6c030cf7b312","https://www.data.gouv.fr/fr/datasets/r/b7a5c653-6c4f-498f-9ab8-c84864dcf375","https://www.data.gouv.fr/fr/datasets/r/37a5db74-fdcb-4304-bb29-8d5f9782b608","https://www.data.gouv.fr/fr/datasets/r/25c57bc4-3e37-4a1b-b2a0-70b3816d829d","https://www.data.gouv.fr/fr/datasets/r/ec671caf-2681-4900-893b-f541ee682d84","https://www.data.gouv.fr/fr/datasets/r/7e5d2323-e2e1-4033-9d0a-1849df89d8a4","https://www.data.gouv.fr/fr/datasets/r/b5ce0b39-aa03-4c05-8af6-f2ada34bc5a0","https://www.data.gouv.fr/fr/datasets/r/80f83ef3-b23f-47d4-8f15-375c9617b77d","https://www.data.gouv.fr/fr/datasets/r/d31abf7c-618d-4fe8-ac74-f7f7e532f147","https://www.data.gouv.fr/fr/datasets/r/d3bbf32e-eac2-4a6f-bd2f-8357ca975765","https://www.data.gouv.fr/fr/datasets/r/4ef96c71-98a1-40c3-9947-b01b30b92fa2","https://www.data.gouv.fr/fr/datasets/r/ff18ab5e-8449-44cc-bc6d-6e6a72b3ffb5","https://www.data.gouv.fr/fr/datasets/r/97bf0922-8504-44b8-a44b-1b90ed82dde4","https://www.data.gouv.fr/fr/datasets/r/00f11b94-ab6e-417f-a045-5ad71451ea10","https://www.data.gouv.fr/fr/datasets/r/7da2d9ce-4467-48a5-b331-c7eb2d738a40","https://www.data.gouv.fr/fr/datasets/r/ca9a8121-6614-4e99-98f7-0fe7f9c87f9e","https://www.data.gouv.fr/fr/datasets/r/0525cefa-67be-4a42-acc8-cba1ce343e14","https://www.data.gouv.fr/fr/datasets/r/8e8d614a-7f05-426f-8134-451a0f4da05e","https://www.data.gouv.fr/fr/datasets/r/5d2732d1-7ca7-4836-b3cc-ad98f092abc7","https://www.data.gouv.fr/fr/datasets/r/2f08e290-13b5-4cec-bda0-8ac847ef4cc2","https://www.data.gouv.fr/fr/datasets/r/122eaed1-af0e-40d2-b9f0-854e04117672","https://www.data.gouv.fr/fr/datasets/r/e357cfb4-3ed0-42b5-b46b-e80942e5c121","https://www.data.gouv.fr/fr/datasets/r/3f1c0f6b-4122-49cc-9ef1-33384d4bc74f","https://www.data.gouv.fr/fr/datasets/r/717d3e44-24bf-43a8-935c-0ed824fa61c5","https://www.data.gouv.fr/fr/datasets/r/288fc251-cafc-4803-be66-8038050bbae9","https://www.data.gouv.fr/fr/datasets/r/a50754c0-5f0d-4051-8e48-3a5a802ad860","https://www.data.gouv.fr/fr/datasets/r/99ff38d2-e0bd-4503-a57d-c6b657404c31","https://www.data.gouv.fr/fr/datasets/r/3fd3b9dc-5a94-4f61-acb4-a79f4c04e3bb","https://www.data.gouv.fr/fr/datasets/r/70ec7f0a-f92d-4145-91dd-7e5ede6fd9a4","https://www.data.gouv.fr/fr/datasets/r/27a238bd-0282-412c-bf7d-5d8988511069","https://www.data.gouv.fr/fr/datasets/r/229f8f3e-81ed-4d55-b1a4-bab6e4e400ad","https://www.data.gouv.fr/fr/datasets/r/fa2ee610-c08b-459e-8423-cf3409b4c3b5","https://www.data.gouv.fr/fr/datasets/r/81dc6b33-d585-4b6e-bc19-4c8363033032","https://www.data.gouv.fr/fr/datasets/r/04f4f815-b5ae-475d-877c-842cc46fa0b7","https://www.data.gouv.fr/fr/datasets/r/05cd4e66-4bae-488a-93ad-5c5e748f89db","https://www.data.gouv.fr/fr/datasets/r/f76f0ca6-4a0e-40c8-8231-c95d94f0dd91","https://www.data.gouv.fr/fr/datasets/r/75c5ca27-57d7-4ded-88e7-50a41d567e57","https://www.data.gouv.fr/fr/datasets/r/39596a0e-9854-4286-80ca-5257c5f83fc4","https://www.data.gouv.fr/fr/datasets/r/0d86fafa-37f8-4571-bc51-0978b42a4dbd","https://www.data.gouv.fr/fr/datasets/r/0af68264-17a4-40b0-834b-9e04d7501d79","https://www.data.gouv.fr/fr/datasets/r/5456fd17-d8ac-4533-a5b1-c8d431d2f46e","https://www.data.gouv.fr/fr/datasets/r/5592a5dc-04b6-42a0-88bb-c514699bae05","https://www.data.gouv.fr/fr/datasets/r/cf095e7d-9f18-4007-a1f2-7026714fa631","https://www.data.gouv.fr/fr/datasets/r/58d4e6b6-fa2c-437f-b08e-b993ead1f28d","https://www.data.gouv.fr/fr/datasets/r/c28e1f19-47eb-46cd-bd99-311951a2d422","https://www.data.gouv.fr/fr/datasets/r/7001e0dd-5a5a-47b9-9812-04ce38a00406","https://www.data.gouv.fr/fr/datasets/r/ff7a9197-9436-4a93-9d84-356b44fd338a","https://www.data.gouv.fr/fr/datasets/r/c344de59-0240-44d4-b10f-e8a68fbd547b","https://www.data.gouv.fr/fr/datasets/r/02850685-ed28-4083-a7db-9b322f3504f9","https://www.data.gouv.fr/fr/datasets/r/f27b421e-ed3a-4415-a7d7-7c061693cfd9","https://www.data.gouv.fr/fr/datasets/r/836dd173-c78e-426a-9cee-397b9864a71f","https://www.data.gouv.fr/fr/datasets/r/75ca86a5-a332-460c-9dab-b2a3e8c1f905","https://www.data.gouv.fr/fr/datasets/r/d868d268-5444-4380-b0c2-72c746205695","https://www.data.gouv.fr/fr/datasets/r/246e2242-3a80-4048-bf07-acf6a60d5804","https://www.data.gouv.fr/fr/datasets/r/f33cffd7-f772-4b38-99ee-60da38ff3f1b","https://www.data.gouv.fr/fr/datasets/r/68f46314-7719-429d-b9ad-d8297fd390e8","https://www.data.gouv.fr/fr/datasets/r/3404ea8e-12ef-4958-abf4-5563d966c3de","https://www.data.gouv.fr/fr/datasets/r/42eb2b68-b448-4c54-8139-04188bbcf898"]
# getFileDensite(urls)

# urls1113 = ["https://www.data.gouv.fr/fr/datasets/r/97bf0922-8504-44b8-a44b-1b90ed82dde4","https://www.data.gouv.fr/fr/datasets/r/00f11b94-ab6e-417f-a045-5ad71451ea10","https://www.data.gouv.fr/fr/datasets/r/7da2d9ce-4467-48a5-b331-c7eb2d738a40","https://www.data.gouv.fr/fr/datasets/r/ca9a8121-6614-4e99-98f7-0fe7f9c87f9e","https://www.data.gouv.fr/fr/datasets/r/0525cefa-67be-4a42-acc8-cba1ce343e14","https://www.data.gouv.fr/fr/datasets/r/8e8d614a-7f05-426f-8134-451a0f4da05e","https://www.data.gouv.fr/fr/datasets/r/5d2732d1-7ca7-4836-b3cc-ad98f092abc7","https://www.data.gouv.fr/fr/datasets/r/2f08e290-13b5-4cec-bda0-8ac847ef4cc2","https://www.data.gouv.fr/fr/datasets/r/122eaed1-af0e-40d2-b9f0-854e04117672","https://www.data.gouv.fr/fr/datasets/r/e357cfb4-3ed0-42b5-b46b-e80942e5c121","https://www.data.gouv.fr/fr/datasets/r/3f1c0f6b-4122-49cc-9ef1-33384d4bc74f","https://www.data.gouv.fr/fr/datasets/r/717d3e44-24bf-43a8-935c-0ed824fa61c5","https://www.data.gouv.fr/fr/datasets/r/288fc251-cafc-4803-be66-8038050bbae9","https://www.data.gouv.fr/fr/datasets/r/a50754c0-5f0d-4051-8e48-3a5a802ad860","https://www.data.gouv.fr/fr/datasets/r/99ff38d2-e0bd-4503-a57d-c6b657404c31","https://www.data.gouv.fr/fr/datasets/r/3fd3b9dc-5a94-4f61-acb4-a79f4c04e3bb","https://www.data.gouv.fr/fr/datasets/r/70ec7f0a-f92d-4145-91dd-7e5ede6fd9a4","https://www.data.gouv.fr/fr/datasets/r/27a238bd-0282-412c-bf7d-5d8988511069","https://www.data.gouv.fr/fr/datasets/r/229f8f3e-81ed-4d55-b1a4-bab6e4e400ad","https://www.data.gouv.fr/fr/datasets/r/fa2ee610-c08b-459e-8423-cf3409b4c3b5","https://www.data.gouv.fr/fr/datasets/r/81dc6b33-d585-4b6e-bc19-4c8363033032","https://www.data.gouv.fr/fr/datasets/r/04f4f815-b5ae-475d-877c-842cc46fa0b7","https://www.data.gouv.fr/fr/datasets/r/05cd4e66-4bae-488a-93ad-5c5e748f89db","https://www.data.gouv.fr/fr/datasets/r/f76f0ca6-4a0e-40c8-8231-c95d94f0dd91","https://www.data.gouv.fr/fr/datasets/r/75c5ca27-57d7-4ded-88e7-50a41d567e57","https://www.data.gouv.fr/fr/datasets/r/39596a0e-9854-4286-80ca-5257c5f83fc4","https://www.data.gouv.fr/fr/datasets/r/0d86fafa-37f8-4571-bc51-0978b42a4dbd","https://www.data.gouv.fr/fr/datasets/r/0af68264-17a4-40b0-834b-9e04d7501d79","https://www.data.gouv.fr/fr/datasets/r/5456fd17-d8ac-4533-a5b1-c8d431d2f46e","https://www.data.gouv.fr/fr/datasets/r/5592a5dc-04b6-42a0-88bb-c514699bae05","https://www.data.gouv.fr/fr/datasets/r/cf095e7d-9f18-4007-a1f2-7026714fa631","https://www.data.gouv.fr/fr/datasets/r/58d4e6b6-fa2c-437f-b08e-b993ead1f28d","https://www.data.gouv.fr/fr/datasets/r/c28e1f19-47eb-46cd-bd99-311951a2d422","https://www.data.gouv.fr/fr/datasets/r/7001e0dd-5a5a-47b9-9812-04ce38a00406","https://www.data.gouv.fr/fr/datasets/r/ff7a9197-9436-4a93-9d84-356b44fd338a","https://www.data.gouv.fr/fr/datasets/r/c344de59-0240-44d4-b10f-e8a68fbd547b","https://www.data.gouv.fr/fr/datasets/r/02850685-ed28-4083-a7db-9b322f3504f9","https://www.data.gouv.fr/fr/datasets/r/f27b421e-ed3a-4415-a7d7-7c061693cfd9","https://www.data.gouv.fr/fr/datasets/r/836dd173-c78e-426a-9cee-397b9864a71f","https://www.data.gouv.fr/fr/datasets/r/75ca86a5-a332-460c-9dab-b2a3e8c1f905","https://www.data.gouv.fr/fr/datasets/r/d868d268-5444-4380-b0c2-72c746205695","https://www.data.gouv.fr/fr/datasets/r/246e2242-3a80-4048-bf07-acf6a60d5804","https://www.data.gouv.fr/fr/datasets/r/f33cffd7-f772-4b38-99ee-60da38ff3f1b","https://www.data.gouv.fr/fr/datasets/r/68f46314-7719-429d-b9ad-d8297fd390e8","https://www.data.gouv.fr/fr/datasets/r/3404ea8e-12ef-4958-abf4-5563d966c3de","https://www.data.gouv.fr/fr/datasets/r/42eb2b68-b448-4c54-8139-04188bbcf898"]
# getFileDensite(urls)

### Lignes de test

# df = createDF(29,'./mensuelle_novembre_2012.pdf',["Mission Outre-Mer","1er décembre 2018","1er décembre 2018"])
# df.to_csv('ecrouee-detenue-nov2012.csv',index=False)

# getFile()

# fichier = open('./docs/mensuelle_novembre_2013.pdf','rb')
# pdfReader = PyPDF2.PdfFileReader(fichier)
# pagePDF = pdfReader.getPage(20)
# text = pagePDF.extractText()
# print(text)

# getFilePDFEtab('./docs/mensuelle_novembre_2013.pdf','nov2013')

# getDens()