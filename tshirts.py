import sys
from collections import deque

sousede = [] # reprezentuje seznam sousedu, kde jsou jak lide, tak i jednotliva tricka
index_to_velikost = ["XS","S","M","L","XL","XXL"]
velikost_to_index = {"XS" : 0, "S" : 1, "M" : 2, "L" : 3, "XL" : 4, "XXL" : 5} # slouzi k vypoctu vrcholu, do ktereho jde z daneho cloveka hrana

tricek_celkem_pocet = 0
lidi_celkem = 0

partneri = [] # reprezentuje hrany naseho parovani, je indexovano vrcholy

def nacti_vstup():
    global tricek_celkem_pocet, lidi_celkem
    tricek_celkem_pocet, lidi_celkem = [int(x) for x in sys.stdin.readline().split()]
    #print(f"Tricek celkem: {tricek_celkem_pocet} Lidi celkem: {lidi_celkem}")
    nacti_graf_a_partnery(lidi_celkem,tricek_celkem_pocet)

def nacti_graf_a_partnery(lidi_celkem,tricek_celkem_pocet):
    global sousede
    jeden_druh_pocet = tricek_celkem_pocet // len(index_to_velikost)
    for index_vrcholu in range(lidi_celkem + tricek_celkem_pocet):
        sousede.append([])
        partneri.append(None)
    for index_cloveka in range(lidi_celkem):
        prvni_velikost, druha_velikost = [x for x in sys.stdin.readline().split()]
        #print(f"Prvni velikost: {prvni_velikost} Druha velikost: {druha_velikost}")
        for index_tricka in range(jeden_druh_pocet):
            cislo_prvni_velikosti = velikost_to_index[prvni_velikost]
            cislo_druhe_velikosti = velikost_to_index[druha_velikost]

            vrchol_prvniho_tricka = lidi_celkem + cislo_prvni_velikosti*jeden_druh_pocet+index_tricka
            vrchol_druheho_tricka = lidi_celkem + cislo_druhe_velikosti*jeden_druh_pocet+index_tricka

            sousede[index_cloveka].append(vrchol_prvniho_tricka)
            sousede[index_cloveka].append(vrchol_druheho_tricka)
            
            sousede[vrchol_prvniho_tricka].append(index_cloveka)
            sousede[vrchol_druheho_tricka].append(index_cloveka)
        sousede[index_cloveka].sort()
        
def vypis_graf(seznam_sousedu):
    i = 0
    for i in range(len(seznam_sousedu)):
        print(f"{i}:",end=" ")
        for j in range(len(seznam_sousedu[i])):
            print(seznam_sousedu[i][j], end=" ")
        print()
    
def vypis_seznam(seznam,text):
    print(f"{text}: ", end = " ")
    for i in range(len(seznam)):
        print(seznam[i], end = " ")
    print()

def existuje_clovek_bez_partnera():
    global lidi_celkem
    for index_cloveka in range(lidi_celkem):
        if partneri[index_cloveka] == None:
            return True
    return False

def vrat_seznam_volnych():
    global lidi_celkem
    volni = []
    for index_cloveka in range(lidi_celkem):
        if partneri[index_cloveka] == None:
            volni.append(index_cloveka)
    return volni

def vytvor_prazdne_partnery():
    global partneri
    novi_partneri = []
    for i in range(len(partneri)):
        novi_partneri.append(None)
    return novi_partneri

def vypis_frontu(fronta):
    print("Fronta: ",end="")
    for prvek in fronta:
        print(prvek,end=" ")
    print()

def vytvor_seznam_navstivenych():
    navstiveni = []
    for i in range(lidi_celkem + tricek_celkem_pocet):
        navstiveni.append(False)
    return navstiveni

# Budu pouzivat k rekonstrukci zlepsujici cesty abych zadny vrchol nepridaval omylem dvakrat
def vytvor_seznam_pridanych_do_noveho_parovani():
    pridani = []
    for i in range(lidi_celkem + tricek_celkem_pocet):
        pridani.append(False)
    return pridani

# Slouzi k rekonstrukci zlepsujici cesty abych vedel, kudy muze teoreticky vest
def vytvor_seznam_nasledniku():
    naslednici = []
    for i in range(lidi_celkem + tricek_celkem_pocet):
        naslednici.append([])
    return naslednici

# Po prohledani alternujiciho stromu nasledniku a nalezeni volneho tricka pomoci tohoto pole dotrackuju odkud jsem prisel
def vytvor_seznam_predchudcu():
    predchudci = []
    for i in range(lidi_celkem + tricek_celkem_pocet):
        predchudci.append(None)
    return predchudci


def vytvor_alternujici_strom_nasledniku(partneri):

    navstiveni_v_bfs = vytvor_seznam_navstivenych_bfs()
    naslednici = vytvor_seznam_nasledniku()
    predchudci = vytvor_seznam_predchudcu()
    volna_tricka = []

    fronta = deque()
    for volny in vrat_seznam_volnych():
        fronta.append(volny)
        navstiveni_v_bfs[volny] = True
    
    #vypis_frontu(fronta)
    volny_nalezen = False # pokud jsme nasli cestu koncici volnym trickem, tak uz nepridavame dalsi vrcholy do fronty, ale jeste ji doprohlizime
    
    # dokud fronta neni prazdna tak pomoci bfs hledam cesty do volnych tricek
    while len(fronta) != 0:
        aktualni = fronta.popleft()  
        # pro kazdeho souseda se koukneme, pokud po nem muzeme jit (tzn. ze uz neni v aktualnim parovani)
        for soused in sousede[aktualni]:
            if partneri[soused] != aktualni and not navstiveni_v_bfs[soused]: # tento soused neni v parovani se mnou a jeste jsem ho nenavstivil, takze muzu tedy tuto hranu prozkoumat
                naslednici[aktualni].append(soused) # nastavim, ze jsem predchudce souseda na ktereho prave koukam
                predchudci[soused] = aktualni
                navstiveni_v_bfs[soused] = True
                if partneri[soused] == None: # nasel jsem volne tricko (jeste neni sparovano s clovekem)
                    volny_nalezen = True
                    volna_tricka.append(soused)
                if not volny_nalezen:
                    fronta.append(soused)

    return volna_tricka, naslednici, predchudci

def vytvor_nova_parovani(volna_tricka, naslednici, partneri):
    novi_partneri = vytvor_prazdne_partnery()
    pridani_do_parovani = vytvor_seznam_pridanych_do_noveho_parovani()

    #pristi_cesta_je_parova = True # alternuje mezi 

    # pro kazde volne tricko chceme zkusit pridat celou jeho cestu do parovani
    for volne_tricko in volna_tricka: 
        aktualni = volne_tricko
        predchudce = naslednici[aktualni]
        while predchudce != None:
            if predchudce < lidi_celkem: # predchudce je clovek, takze toto bude nova hrana parovani
                novi_partneri[aktualni] = predchudce
                novi_partneri[predchudce] = aktualni
            aktualni = predchudce
            predchudce = naslednici




nacti_vstup()
vypis_graf(sousede)
print(f"Parovani: {partneri}")
volna_tricka, naslednici, predchudci = vytvor_alternujici_strom_nasledniku(partneri)
print(f"Volna tricka: {volna_tricka}")
print(f"Predchudci: {predchudci}")
print("Naslednici:")
vypis_graf(naslednici)

