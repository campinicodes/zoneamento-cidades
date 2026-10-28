import json
B="https://cdn.campogrande.ms.gov.br/portal/prod/uploads/sites/18"
fontes=[
 ("F01","Plano Diretor de Desenvolvimento Urbano Ambiental (PDDUA) – texto republicado/consolidado com as retificações da LC 349/2019 (inclui Anexos 1, 7.1, 8.1, 8.2)","Lei Complementar n. 341/2018 (republicada por força da LC n. 349/2019)","2018-12-04 (republicação DIOGRANDE n. 5.539, 2019-04-03)",B+"/2019/04/LEI-COMPLEMENTAR-n.-341-DE-4-DE-DEZEMBRO-DE-2018.-retifica%C3%A7%C3%A3o1.pdf"),
 ("F02","Retifica a LC 341/2018 (CAmín 0,10; Anexo 8.2; ZEIA2)","Lei Complementar n. 349/2019","2019-04-03",B+"/2019/04/LEI-COMPLEMENTAR-n.-349-DE-3-DE-ABRIL-DE-2019.1.pdf"),
 ("F03","PDDUA – publicação original","Lei Complementar n. 341/2018","2018-12-04",B+"/2018/12/Lei-Complementar-n.-341-de-4-de-dezembro-de-2018-PDDUA.pdf"),
 ("F04","PDDUA – republicação dos mapas (Anexos cartográficos: macrozonas, zonas urbanas, zonas ambientais, ZEIS, eixos, centralidades)","Lei Complementar n. 341/2018 (republicação de mapas)","2019-10",B+"/2019/10/Lei-341-republica%C3%A7%C3%A3o-mapas.pdf"),
 ("F05","Lei de Ordenamento do Uso e da Ocupação do Solo (LOUOS) – texto consolidado publicado no DIOGRANDE n. 3.672 (até LC 211/2012), incl. Anexos IV (categorias), V (compatibilidade locacional) e VI (vagas)","Lei Complementar n. 74/2005 e alterações","2005-09-06 (consolidação DIOGRANDE 2012-12-31)",B+"/2017/01/20130103102042.pdf"),
 ("F06","Normas para gestão das Zonas Especiais de Interesse Social (ZEIS 2)","Lei Complementar n. 421/2021","2021-11-11",B+"/2021/11/lei-complementar-421-zeis-1636722441.pdf"),
 ("F07","Altera a LC 421/2021 (ZEIS 2: índices da zona urbana; Z5 usa índices da Z4; mitigações)","Lei Complementar n. 516/2023","2023-12-29 (DIOGRANDE n. 7.334)",B+"/2024/01/Lei-Complementar-516-29.12.2023.pdf"),
 ("F08","Outorga Onerosa do Direito de Construir (OODC) – fórmula, fatores, isenções","Lei Complementar n. 469/2022","2022-09-05 (DIOGRANDE n. 6.760, 2022-09-06)",B+"/2022/09/leicomplementarn-469de5desetembrode2022-oodc-prefcg-1662467928.pdf"),
 ("F09","Regulamenta a aplicação das categorias de uso e índices (Anexos 8.1/8.2 PDDUA) em vias limítrofes, eixos e centralidades","Decreto n. 15.123/2022","2022-02-24 (DIOGRANDE n. 6.561)",B+"/2022/02/decreto-n-15123-24-de-fevereiro-de-2022-1645794243.pdf"),
 ("F10","Altera LC 74/2005 (art. 52 XIII; art. 54 – MZ3)","Lei Complementar n. 411/2021","2021-06",B+"/2021/06/lei-complementar-411-1623687882.pdf"),
 ("F11","Altera LC 74/2005 (definições pavimento térreo, subsolo, mezanino, empena; art. 37 III e V – empenas nas divisas até 6,5 m; garagens nos recuos em Z3/Z4/eixos)","Lei Complementar n. 445/2022","2022-03-31 (DIOGRANDE n. 6.602, 2022-04-01)",B+"/2022/04/leicomplementarn-445de31demarode2022-prefcg-1648844709.pdf"),
 ("F12","Altera LC 74/2005 (art. 32 VI; art. 37 §§3º-4º; art. 39; art. 48; Anexo IV Tabela 6, Anexo V e Anexo VI)","Lei Complementar n. 373/2019","2019-12-26 (DIOGRANDE n. 5.788, 2019-12-27)",B+"/2019/12/Lei-Complementar-n-373-de-26-de-dezembro-de-2019.pdf"),
 ("F13","Altera LC 74/2005 (art. 31 VIII – contrapartida parcelada; art. 54 VIII – TIO 4 anos) e LC 129/2008","Lei Complementar n. 486/2023","2023-06-22",B+"/2023/06/LEI-COMPLEMENTAR-n.-486-DE-22-DE-JUNHO-DE-2023..pdf"),
 ("F14","Altera LC 74/2005 (art. 41-A I d – postos de combustível)","Lei Complementar n. 472/2022","2022-10-07",B+"/2022/10/leicomplementarn-472-prefcg-1665665203.pdf"),
 ("F15","Altera a LC 341/2018 (parágrafo único do art. 172 – perímetro)","Lei Complementar n. 487/2023","2023-06-27",B+"/2023/06/LEI-COMPLEMENTAR-n.-487-DE-27-DE-JUNHO-DE-2023..pdf"),
 ("F16","Outorga Onerosa de Alteração do Uso do Solo na ZEU (OOAUS/ZEU)","Lei n. 6.795/2022","2022-03-24",B+"/2022/03/L-6795-DE-2022.pdf"),
 ("F17","Altera a Lei 6.795/2022 (requisitos de loteamento na ZEU; EIV para urbanização na ZEU)","Lei n. 7.253/2024","2024-05-22 (DIOGRANDE n. 7.510)",B+"/2024/05/LEI-n.-7.253-DE-22-DE-MAIO-DE-2024.-OOAUS-ZEU.pdf"),
 ("F18","Regulamenta o Índice de Relevância Ambiental (IA), equiparado à TRA do PDDUA","Lei n. 6.914/2022","2022-09-05 (DIOGRANDE n. 6.760)",B+"/2022/09/lein-6-914de5desetembrode2022-indicederelevanciaambiental-prefcg-1662468085.pdf"),
 ("F19","Regulamenta o art. 131 do PDDUA – audiências públicas de EIV/RIV e EIA/RIMA","Decreto n. 15.846/2024","2024-03-01 (DIOGRANDE n. 7.408, 2024-03-04)",B+"/2024/03/DECRETO-n.-15.846-DE-1o-DE-MARCO-DE-2024.-Audiencias-publicas-EIV.pdf"),
 ("F20","Nota Técnica 01/2024 – aplicação do §4º do art. 25 do PDDUA (permeabilidade excedente → TO/área construída)","Resolução SEMADUR n. 71/2024","2024-09-23 (DIOGRANDE n. 7.661, 2024-09-25)",B+"/2024/09/Resolucao-Semadur-71-2024-Nota-tecnica-1-2024.pdf"),
 ("F21","Nota Técnica 02/2024 – vagas de estacionamento e fachada ativa em empreendimentos HIS na ZEIS 2","Resolução SEMADUR n. 72/2024","2024-09-23 (DIOGRANDE n. 7.661, 2024-09-25)",B+"/2024/09/Resolucao-Semadur-72-2024-Nota-tecnica-2-2024.pdf"),
 ("F22","Nota Técnica 03/2024 – medição da compatibilidade locacional (LOUOS)","Resolução SEMADUR n. 73/2024","2024-09-23 (DIOGRANDE n. 7.661)",B+"/2024/09/Resolucao-Semadur-73-2024-Nota-tecnica-3-2024.pdf"),
 ("F23","Plano Diretor de Transporte e Mobilidade Urbana (PDTMU) / PMAU","Lei n. 7.282/2024","2024-07-15",B+"/2024/07/LEI-n.-7.282-DE-15-DE-JULHO-DE-2024.-PMAU-PDTMU-e-Anexos.pdf"),
 ("F24","Guia Prático de Isenções de IPTU 2026 (SEFAZ/GETRI) – cita Lei 5.680/2016, Decreto 15.220/2022 e LC 407/2021","Guia oficial SEFAZ (não é lei)","2026-01","https://cdn.campogrande.ms.gov.br/portal/prod/uploads/sites/29/2026/01/GuiaPratico-isencao-IPTU-2026.pdf"),
 ("F25","PLANURB – página oficial 'PDDUA Campo Grande 2018 – Legislação' (índice de leis vigentes do PDDUA e regulamentações)","Página oficial PLANURB","consultada 2026-10-27","https://www.campogrande.ms.gov.br/planurb/pddua-campo-grande-2018-legislacao/"),
 ("F26","PLANURB – página oficial 'Legislação de Ordenamento do Uso e Ocupação do Solo – histórico' (lista de alterações da LC 74/2005)","Página oficial PLANURB","consultada 2026-10-27","https://www.campogrande.ms.gov.br/planurb/legislacao-de-ordenamento-do-uso-e-ocupacao-do-solo-historico/"),
 ("F27","PLANURB – revisão da LOUOS (Decreto 15.948/2024; minuta em consulta pública jan–fev/2026; reunião pública 02/03/2026)","Página oficial PLANURB","consultada 2026-10-27","https://www.campogrande.ms.gov.br/planurb/e-mail-contribuicoes-revisao-legislacao-e-ordenamento-de-uso-e-da-ocupacao-do-solo/"),
 ("F28","Altera LC 74/2005 (art. 31 parágrafo único II)","Lei Complementar n. 261/2015","2015-05-27",B+"/2017/01/20150528134821.pdf"),
 ("F29","Plano Local para Qualificação Urbanística dos Polos de Desenvolvimento Econômico (PLDE) – Anexos III e IV (regime urbanístico específico, anterior ao PDDUA)","Lei Complementar n. 263/2015","2015-07-14 (DIOGRANDE n. 4.316)",B+"/2017/01/20150715084119.pdf"),
 ("F30","Altera LC 74/2005 (art. 14 – polígonos de zoneamento; Anexo II)","Lei Complementar n. 240/2014","2014-07-21",B+"/2017/01/20140723151045.pdf"),
 ("F31","Acrescenta serviços ao Anexo III da LC 74/2005 (zona Z4 antiga)","Lei Complementar n. 313/2018","2018-01-15",B+"/2018/01/edital-lei-complementar-n.313-de-15-de-janeiro-de-2018-repuplica%C3%A7%C3%A3o-16-de-janeiro-de-2018.pdf"),
]
F=[{"id":a,"titulo":b,"lei":c,"data":d,"url":e} for a,b,c,d,e in fontes]

A82="LC 341/2018 consolidada, Anexo 8.2 – Índices e Instrumentos Urbanísticos (p. 51 do PDF), c/c art. 26"
A81="LC 341/2018 consolidada, Anexo 8.1 – Categorias de Uso por Zonas e Eixos (p. 50 do PDF), c/c art. 26"
def v(val,fid,art,obs=None):
    d={"valor":val,"fonte_id":fid,"artigo_anexo":art}
    if obs: d["observacao"]=obs
    return d

ZA={"ZA1":"20%","ZA2":"25%","ZA3":"25%","ZA4":"30%","ZA5":"30%"}
TRA={"ZA1":0.36,"ZA2":0.38,"ZA3":0.40,"ZA4":0.45,"ZA5":0.50}
za_b={}
for za,bl in {"ZA1":"Amambaí,Centro,Jardim dos Estados","ZA2":"Cabreúva,Cruzeiro,Planalto,Santa Fé,São Francisco",
 "ZA3":"Aero Rancho,América,Autonomista,Bandeirantes,Bela Vista,Caiçara,Carandá,Carlota,Carvalho,Chácara Cachoeira,Glória,Guanandi,Itanhangá,Jacy,Jardim Paulista,Jockey Club,Leblon,Margarida,Mata do Jacinto,Monte Castelo,Monte Líbano,Nasser,Parati,Piratininga,São Bento,São Lourenço,Sobrinho,Taquarussu,Taveirópolis,Tiradentes,TV Morena,Vilasboas",
 "ZA4":"Alves Pereira,Batistão,Centro-Oeste,Coophavila II,Coronel Antonino,Dr. Albuquerque,Estrela Dalva,Maria Aparecida Pedrossian,Moreninha,Noroeste,Nova Lima,Novos Estados,Panamá,Pioneiros,Rita Vieira,Santo Amaro,Santo Antônio,Tijuca,União,Universitário",
 "ZA5":"Caiobá,Centenário,Chácara dos Poderes,José Abrão,Lajeado,Los Angeles,Mata do Segredo,Nova Campo Grande,Núcleo Industrial,Popular,São Conrado,Seminário,Tarumã,Veraneio"}.items():
    for b in bl.split(","): za_b[b]=za
Zb={"Z1":"Amambaí,Centro,Jardim dos Estados,Santa Fé",
 "Z2":"Bela Vista,Cabreúva,Carvalho,Cruzeiro,Glória,Itanhangá,Monte Líbano,Planalto,São Bento,São Francisco",
 "Z3":"Aero Rancho,América,Autonomista,Bandeirantes,Carandá,Carlota,Chácara Cachoeira,Guanandi,Jacy,Jardim Paulista,Jockey Club,Margarida,Mata do Jacinto,Parati,Piratininga,São Lourenço,Taquarussu,Tiradentes,TV Morena,Veraneio,Vilasboas",
 "Z4":"Alves Pereira,Batistão,Caiçara,Centenário,Centro-Oeste,Coophavila II,Coronel Antonino,Dr. Albuquerque,Estrela Dalva,José Abrão,Leblon,Maria Aparecida Pedrossian,Monte Castelo,Moreninha,Nasser,Noroeste,Nova Lima,Novos Estados,Panamá,Pioneiros,Popular,Rita Vieira,Santo Amaro,Santo Antônio,Seminário,Sobrinho,Taveirópolis,Tijuca,União,Universitário",
 "Z5":"Caiobá,Chácara dos Poderes,Lajeado,Los Angeles,Mata do Segredo,Nova Campo Grande,Núcleo Industrial,São Conrado,Tarumã"}
MZ={"MZ1":"Amambaí,Bela Vista,Cabreúva,Carvalho,Centro,Cruzeiro,Glória,Itanhangá,Jardim dos Estados,Monte Líbano,Planalto,Santa Fé,São Bento,São Francisco".split(","),
    "MZ3":"Caiobá,Chácara dos Poderes,Lajeado,Los Angeles,Mata do Segredo,Nova Campo Grande,Núcleo Industrial,São Conrado,Tarumã".split(",")}
def mz(b): return "MZ1" if b in MZ["MZ1"] else ("MZ3" if b in MZ["MZ3"] else "MZ2")
def perm(z):
    bl=Zb[z].split(",")
    groups={}
    for b in bl: groups.setdefault(za_b[b],[]).append(b)
    vals=sorted(set(ZA[k] for k in groups))
    det={k:{"taxa_permeabilidade":ZA[k],"tra_minima":TRA[k],"bairros":groups[k]} for k in sorted(groups)}
    val=vals[0] if len(vals)==1 else " a ".join(vals)+" (conforme a Zona Ambiental do bairro)"
    return val,det
def bairros_info(z):
    bl=Zb[z].split(",")
    return [{"bairro":b,"macrozona":mz(b),"zona_ambiental":za_b[b],"taxa_permeabilidade":ZA[za_b[b]]} for b in bl]

USOS_OBS="R1 = residencial unifamiliar (1 unidade); R2 = 2 a 25 unidades; R3 = 26 a 50 unidades; E1 = residencial 51–100 UH; E2 = 101–250 UH; E3 = acima de 251 UH (LC 74/2005, Anexo IV Tabelas 5 e 6, redação LC 205/2012 e LC 373/2019). Multirresidencial = mais de uma residência no lote (PDDUA Anexo 1)."
def usos(res,esp,lot,extra=""):
    mf=[x for x in res.split(",") if x in("R2","R3")]+[x for x in esp.split(",") if x in("E1","E2","E3")]
    return {"valor":{"residencial":res.split(",") if res else [],"especial":esp.split(",") if esp else [],"loteamento":lot.split(",") if lot else [],
       "multifamiliar_condominios_permitidos":mf,"multifamiliar_resumo":("Multifamiliar permitido: "+", ".join(mf)) if mf else "Multifamiliar NÃO previsto no Anexo 8.1 para esta zona"},
       "fonte_id":"F01","artigo_anexo":A81+"; categorias: LC 74/2005 Anexo IV (F05/F12)","observacao":(USOS_OBS+" "+extra).strip()}
VAGAS=v("1 vaga por unidade habitacional (residencial); +5% de vagas para visitantes em multirresidencial com mais de 50 moradias; +10% para bicicletas/motos em residencial com mais de 20 vagas; vaga mínima 2,40 x 4,80 m","F05","LC 74/2005, art. 38 (incisos VII e VIII, §§2º–4º) e Anexo VI (redação LC 107/2007/LC 205/2012; Anexo VI alterado pela LC 373/2019) – confirmado pela Nota Técnica 02/2024 (F21)","Em ZEIS 2 (HIS) há redução: MZ1 pode ser dispensada; MZ2 mínimo 25% das unidades; MZ3 mínimo 50% (LC 421/2021, art. 6º, III – F06; NT 02/2024 – F21).")

def recuos(fr,lat,latoodc,fid="F01"):
    return {"frontal":v(fr,fid,A82),"lateral":v(lat,fid,A82,"Coluna 'Recuos lateral e fundos' (sem OODC/TDC). Com OODC/TDC: "+latoodc+". h = altura da edificação. LC 74/2005 art. 37 III (redação LC 445/2022): empenas nas divisas laterais/fundos permitidas até 6,5 m do piso do térreo; acima, recuo mínimo 1,50 m."),
            "fundos":v(lat,fid,A82,"Mesma regra do recuo lateral (coluna única 'lateral e fundos'). Com OODC/TDC: "+latoodc+".")}

def zona(cod,nome,desc,TO,CAmin,CAbas,CAmax,oodc,IE,lote,test_esq,test_meio,fr,lat,latoodc,us,perm_val,perm_det,obs,gab_obs=None,extra=None):
    p={"ca_minimo":v(CAmin,"F01",A82,"CA mínimo 0,10 fixado pela retificação da LC 349/2019 (art. 15) – F02."),
       "ca_basico":v(CAbas,"F01",A82),
       "ca_maximo":v(CAmax,"F01",A82,"Acima do CA básico até o CA máximo somente mediante OODC (LC 469/2022) ou TDC (PDDUA arts. 98–102)."),
       "potencial_adicional_oodc_tdc":v(oodc,"F01",A82,"Coluna 'OODC/TDC' do Anexo 8.2 (acréscimo de CA obtido por outorga/transferência)."),
       "taxa_ocupacao":TO,
       "indice_elevacao":v(IE,"F01",A82,"IE = AC/AO (área construída / área ocupada) – PDDUA Anexo 1; funciona como controle de nº de pavimentos equivalentes."),
       "gabarito_altura_max":v(None,"F01",A82,gab_obs or "O Anexo 8.2 não fixa altura máxima em metros nem nº de pavimentos para a zona; a verticalização é controlada indiretamente pelo IE (AC/AO), pelo CA e pelos recuos proporcionais à altura (h/n). Restrições aeronáuticas (ZEPA, art. 27, Anexo 9 – planos do COMAER) podem limitar a altura em áreas próximas ao aeroporto."),
       "taxa_permeabilidade":v(perm_val,"F01","LC 341/2018 consolidada, art. 25 §§1º–4º e Anexo 7.1 (Taxa de Relevância Ambiental e Taxa de Permeabilidade por Zona Ambiental, p. 50 do PDF)","A permeabilidade é definida pela ZONA AMBIENTAL (ZA1–ZA5), não pela zona urbana. TRA mínima: ZA1 0,36; ZA2 0,38; ZA3 0,40; ZA4 0,45; ZA5 0,50 (IA = V^α × D^β – Lei 6.914/2022, F18). Permeabilidade acima da exigida pode ser convertida em TO/área construída (art. 25 §4º; NT 01/2024 – F20)."),
       "recuos":recuos(fr,lat,latoodc),
       "lote_minimo_m2":v(lote,"F01",A82,"Lote mínimo para parcelamento; Loteamento de Interesse Social (L2) admite lote de 200 m² com testada 10 m (meio) / 15 m (esquina) – LC 74/2005 art. 47 (F05)." if isinstance(lote,(int,float)) else None),
       "testada_minima_m":v({"meio_de_quadra":test_meio,"esquina":test_esq},"F01",A82),
       "usos_permitidos":us,"vagas":VAGAS}
    if perm_det: p["taxa_permeabilidade"]["detalhe_por_zona_ambiental"]=perm_det
    z={"codigo":cod,"nome":nome,"descricao":desc,"parametros":p,"observacoes":obs}
    if extra: z.update(extra)
    return z

TO_note="Nota (1) do Anexo 8.2: multirresidenciais com fachada ativa – TO térreo e 1º pavimento 0,7; demais 0,5. TO majorável mediante contrapartida financeira: 50% → até 60% (LC 74/2005 art. 31, parágrafo único – F05; pagamento parcelável, LC 486/2023 – F13), exceto em ZEIA e entorno de bens tombados."
zonas=[]
pv,pd=perm("Z1")
zonas.append(zona("Z1","Zona Urbana 1","Zona central de maior adensamento (MZ1). Bairros: "+Zb["Z1"]+" (art. 24 e Anexo 6).",
 v({"terreo_e_1o_pavimento":0.7,"demais_pavimentos":0.5},"F01",A82,"Nota (7): multirresidenciais com fachada ativa – TO do térreo até 0,8 mediante contrapartida financeira."),
 0.10,4,5,1,"Livre",250,15,10,"Térreo e 1º pavimento: livre; demais pavimentos: 5,00 m",
 "Térreo e 1º pav.: livre; IE de 2 a <6: h/6 (mín. 3,00 m); IE ≥6 a <12: h/8 (mín. 3,00 m); IE ≥12: h/10 (mín. 5,00 m)","idem (mesma regra)",
 usos("R1,R2,R3","E1,E2,E3,E4,E10,E13,E19,E20","L1,L2,L3,L5"),pv,pd,
 ["Nota (6) Anexo 8.2: multirresidenciais com fachada ativa ≥ 20% da TO têm desconto de 20% na OODC.","Fid (fator infraestrutura/densidade) da OODC = 0,100 (o menor da cidade) – LC 469/2022 art. 6º (F08).","Macrozona MZ1 – densidade líquida até 330 hab/ha (PDDUA art. 20); estímulo a adensamento e programas habitacionais (art. 21).","OODC isenta para HIS (LC 469/2022 art. 8º II – ver ambiguidade em outorga_onerosa).","Detalhe de bairros: "+json.dumps(bairros_info("Z1"),ensure_ascii=False)]))
pv,pd=perm("Z2")
zonas.append(zona("Z2","Zona Urbana 2","Zona de adensamento em bairros pericentrais (todos na MZ1). Bairros: "+Zb["Z2"]+".",
 v(0.5,"F01",A82,TO_note),0.10,3,5,2,"6 (com OODC/TDC passa a Livre – nota 3)",250,15,10,"IE > 2: 5,00 m (nota 2: edifícios com fachada ativa – térreo e 1º pav. livre, demais 5,00 m)",
 "Térreo e 1º pav.: livre; IE de 2 a 6: h/6 (mín. 3,00 m)","Térreo e 1º pav.: livre; IE 2 a <6: h/6 (mín. 3,00 m); IE ≥6 a <12: h/8 (mín. 3,00 m); IE ≥12: h/10 (mín. 5,00 m)",
 usos("R1,R2,R3","E1,E2,E3,E4,E8,E13,E19,E20","L1,L2,L3,L5"),pv,pd,
 ["Nota (8): multirresidenciais com fachada ativa ≥20% da TO – desconto de 20% após a compra do primeiro CA (OODC).","Fid OODC = 0,250 (F08).","Todos os bairros da Z2 estão na MZ1 (330 hab/ha).","Detalhe de bairros: "+json.dumps(bairros_info("Z2"),ensure_ascii=False)]))
pv,pd=perm("Z3")
zonas.append(zona("Z3","Zona Urbana 3","Zona intermediária (MZ2, adensamento prioritário). Bairros: "+Zb["Z3"]+".",
 v(0.5,"F01",A82,TO_note),0.10,2,4,2,"4 (com OODC/TDC passa a 8 – nota 4)",250,15,10,"IE > 2: 5,00 m (nota 2: fachada ativa – térreo e 1º pav. livre)",
 "IE até 2: livre; IE > 2: h/4 (mín. 3,00 m)","Térreo e 1º pav.: livre; IE 2 a <6: h/6 (mín. 3,00 m); IE ≥6: h/8 (mín. 5,00 m)",
 usos("R1,R2,R3","E1,E2,E3,E4,E8,E10,E11,E13,E18,E19,E20","L1,L2,L3,L5","E11 somente bairros Glória, Mata do Jacinto, Moreninhas, Sobrinho, Pioneiros, Centenário e Seminário; E18/E19/E20 exceto bairros Autonomista, São Bento, Bela Vista e Itanhangá (notas do Anexo 8.1)."),pv,pd,
 ["Fid OODC = 0,400 (F08).","LC 445/2022: garagens e depósitos admitidos nos recuos laterais e de fundos do térreo nas zonas Z3, Z4 e eixos de adensamento (LC 74 art. 37 V).","MZ2 – densidade líquida até 240 hab/ha (PDDUA art. 20).","Detalhe de bairros: "+json.dumps(bairros_info("Z3"),ensure_ascii=False)]))
pv,pd=perm("Z4")
zonas.append(zona("Z4","Zona Urbana 4","Zona periférica consolidada (MZ2). Bairros: "+Zb["Z4"]+".",
 v(0.5,"F01",A82,"Sem nota de fachada ativa para TO nesta zona. TO majorável mediante contrapartida 50%→60% (LC 74 art. 31 par. único – F05)."),0.10,2,3,1,"4 (com OODC/TDC passa a 6 – nota 5)",250,15,10,"IE > 2: 5,00 m",
 "IE até 2: livre; IE > 2: h/4 (mín. 3,00 m)","Térreo e 1º pav.: livre; IE de 2 a 6: h/6 (mín. 3,00 m)",
 usos("R1,R2,R3","E1,E2,E3,E4,E7,E8,E10,E11,E12,E13,E18,E19,E20,E21","L1,L2,L3,L5","E11 somente bairros Glória, Mata do Jacinto, Moreninhas, Sobrinho, Pioneiros, Centenário e Seminário; E12 e E21 somente bairro Taveirópolis."),pv,pd,
 ["Fid OODC = 0,500 (F08).","LC 445/2022: garagens/depósitos admitidos nos recuos laterais e de fundos do térreo (Z3, Z4 e eixos).","MZ2 – 240 hab/ha.","Detalhe de bairros: "+json.dumps(bairros_info("Z4"),ensure_ascii=False)]))
pv,pd=perm("Z5")
zonas.append(zona("Z5","Zona Urbana 5","Zona de urbanização restritiva/adensamento futuro (MZ3). Bairros: "+Zb["Z5"]+".",
 v(0.5,"F01",A82),0.10,1,1.5,0.5,"2 (com OODC/TDC passa a 3 – nota 9)",250,15,10,"Livre","Livre","IE até 2: livre; IE > 2: h/4 (mín. 3,00 m)",
 usos("R1,R2","E4,E5,E6,E7,E8,E10,E11,E13,E14,E16,E17,E18,E19,E20","L1,L2,L3,L5","Atenção: R3 e E1/E2/E3 NÃO constam do Anexo 8.1 para Z5 – residencial multifamiliar limitado a R2 (até 25 unidades). Em ZEIS 2 situada em Z5 aplicam-se os índices e usos da Z4 (LC 516/2023 art. 8º – F07)."),pv,pd,
 ["Fid OODC = 2,000 (F08).","MZ3 – densidade até 120 hab/ha; novos loteamentos exigem infraestrutura antecipada e venda só após TVO (PDDUA art. 23 §§2º–3º); áreas do Anexo 10.2 destinadas a HIS (art. 23 §4º).","LC 411/2021: na MZ3 só loteamento L3 (alteração do art. 54 da LC 74) – conferir aplicação caso a caso (F10).","Detalhe de bairros: "+json.dumps(bairros_info("Z5"),ensure_ascii=False)]))
zonas.append(zona("ZC","Zona de Centralidade","7 centralidades (Júlio de Castilho, Tamandaré, Coronel Antonino, Cidade Jardim, Guaicurus, Morenão, Aero Rancho) – PDDUA art. 33 e Anexo 14; densidade líquida até 330 hab/ha.",
 v(0.5,"F01",A82,TO_note),0.10,3,5,2,"6 (com OODC/TDC passa a Livre – nota 3)",250,15,10,"IE > 2: 5,00 m (nota 2: fachada ativa – térreo e 1º pav. livre)",
 "Térreo e 1º pav.: livre; IE de 2 a 6: h/6 (mín. 3,00 m)","Térreo e 1º pav.: livre; IE 2 a <6: h/6 (mín. 3,00 m); IE ≥6 a <12: h/8 (mín. 3,00 m); IE ≥12: h/10 (mín. 5,00 m)",
 usos("R1,R2,R3","E1,E2,E3,E4,E7,E8,E13,E18,E19,E20","L1,L2,L3,L5","Na ZC aplicam-se exclusivamente os usos da ZC (Decreto 15.123/2022 art. 4º – F09)."),
 "Variável – depende da Zona Ambiental (ZA1–ZA5) do bairro onde está a centralidade (Anexo 7.1)",None,
 ["Fid OODC = 0,250 (F08).","Nota (8): desconto de 20% na OODC para multirresidencial com fachada ativa ≥20% da TO.","Instrumentos: OODC, preempção, PEUC, desapropriação, OUC, OOAUS (art. 33 §2º).","Isenção de OODC (LC 469 art. 8º II) cita expressamente 'Zonas de Centralidades' – ver ambiguidade."]))
zonas.append(zona("ZEIE","Zona Especial de Interesse Econômico","Zonas industriais/econômicas (ZEIE 1 a 7 – PDDUA art. 32, Anexo 13).",
 v(0.7,"F01",A82),0.10,1,1.5,0.5,"Livre",500,20,20,"IE > 2: 5,00 m","Térreo e 1º pav.: livre; IE de 2 a 6: h/6 (mín. 3,00 m); IE > 6: h/8 (mín. 5,00 m)","idem",
 usos("R1","E4,E5,E6,E7,E13,E15,E16,E21","L4","Somente R1 residencial. Na ZEIE aplicam-se exclusivamente seus índices e usos (Decreto 15.123/2022 art. 6º)."),
 "Variável – depende da Zona Ambiental do local (Anexo 7.1)",None,["Fid OODC = 0,250. Não indicada para MCMV (uso residencial apenas R1)."]))
for cod,nome in [("EA1","Eixo de Adensamento 1"),("EA2","Eixo de Adensamento 2"),("EA3","Eixo de Adensamento 3")]:
    res="R1,R2,R3" if cod!="EA3" else "R1,R2"
    esp={"EA1":"E4,E5,E13,E18,E19","EA2":"E4,E5,E6,E7,E8,E11,E13,E17,E18,E19,E20","EA3":"E4,E5,E6,E7,E8,E9,E10,E11,E13,E17,E18,E19,E20,E21"}[cod]
    zonas.append(zona(cod,nome,"Eixos viários que induzem adensamento e diversificação de usos (PDDUA art. 44, Anexo 14). Aplicam-se exclusivamente os usos do eixo, independentemente da zona (Decreto 15.123/2022 art. 7º); opção de índices para lotes em vias limítrofes (art. 11).",
     v(0.5,"F01",A82),0.10,2.8,3.3,0.5,"5,6 (com OODC/TDC passa a 6,6 – nota 10)",None,None,None,"IE > 2: 5,00 m","IE até 2: livre; IE > 2: h/4 (mín. 3,00 m)","Térreo e 1º pav.: livre; IE de 2 a 6,6: h/6 (mín. 3,00 m)",
     usos(res,esp,"","Anexo 8.1 não prevê E1/E2/E3 nos eixos; residencial até R3 (50 UH) em EA1/EA2 e até R2 em EA3. Usos da zona admitidos em EA1/EA2 se o acesso for por outra via (Decreto 15.123 art. 9º)."),
     "Variável – depende da Zona Ambiental do lote (Anexo 7.1)",None,
     ["Lote mínimo/testada: Anexo 8.2 traz '-' para os eixos; aplica-se o lote existente/zona urbana de origem para parcelamento (Decreto 15.123 art. 8º).","Fid OODC = 0,250.","LC 445/2022: garagens/depósitos nos recuos laterais/fundos do térreo nos eixos."]))
    zonas[-1]["parametros"]["lote_minimo_m2"]["observacao"]="Anexo 8.2 indica '-' (não definido) para eixos; parcelamento segue a zona urbana da gleba (Decreto 15.123/2022 art. 8º – F09)."
zonas.append(zona("ANHANDUI","Distrito de Anhanduí","Área urbana do distrito de Anhanduí (MDA – Anexo 5.3; PDDUA art. 20 §1º).",
 v(0.5,"F01",A82),0.10,2,2,None,"4",250,15,10,"IE > 2: 5,00 m","IE até 2: livre; IE > 2: h/4 (mín. 3,00 m)","Não se aplica ('-': sem OODC/TDC)",
 usos("R1,R2,R3","E1,E2,E3,E4,E5,E7,E8,E9,E10,E11,E13,E17,E18","L1,L2,L3,L4,L5"),"Não definida no Anexo 7.1 para o distrito (ver lacunas)",None,
 ["CA básico = CA máximo = 2; coluna OODC/TDC '-' (sem outorga)."]))
zonas[-1]["parametros"]["potencial_adicional_oodc_tdc"]["valor"]=None
zonas[-1]["parametros"]["potencial_adicional_oodc_tdc"]["observacao"]="Anexo 8.2 indica '-' (instrumento não aplicável no distrito)."
zonas[-1]["parametros"]["taxa_permeabilidade"]["valor"]=None
zonas.append(zona("ZEU","Zona de Expansão Urbana","Áreas fora do perímetro urbano passíveis de urbanização mediante OOAUS (PDDUA arts. 15–16, Anexo 3; Lei 6.795/2022 e 7.253/2024).",
 v(0.5,"F01",A82),0.10,1,2,1,"Livre",250,15,10,"IE > 2: 5,00 m","IE até 2: livre; IE > 2: h/4 (mín. 3,00 m)","idem",
 usos("R1","E4,E5,E6,E7,E8,E9,E10,E11,E12,E13,E14,E15,E16,E17,E18,E19,E20,E21","L6,L7","Na ZEU os loteamentos L6/L7 não são permitidos (nota * do Anexo 8.1); urbanização depende de OOAUS + lei de novo perímetro (PDDUA art. 16 §§1º–2º)."),
 "Não definida no Anexo 7.1 (ZEU fora das ZA urbanas); IRA exigível para novos bairros (Lei 6.795 art. 14 par. único)",None,
 ["Fid OODC = 4,000 (o maior) e Vt = área × valor médio do m² da MZ3 (LC 469 art. 6º).","OOAUS: Voaus = ((A × VTu) × (P/100)) × Fn × Fl; Fn L1 0,70 / L2 0,50 / L3 1,00; Fl 1,00 (sem pavimentação) / 0,70 (com) – Lei 6.795/2022 art. 6º (F16). Loteamentos L1/L2 reservam 5% dos lotes privativos p/ comércio/serviço; L3 1,5% (Lei 7.253/2024 – F17). EIV obrigatório para urbanização na ZEU (art. 4º-A).","Lista de E-categorias da ZEU extraída do Anexo 8.1 (E4 a E21) – conferir no original."]))
zonas[-1]["parametros"]["taxa_permeabilidade"]["valor"]=None
zonas.append({"codigo":"ZEIS1","nome":"Zona Especial de Interesse Social 1","descricao":"Ocupações consolidadas há mais de 5 anos, para regularização fundiária (PDDUA art. 29 I, Anexo 10.1).",
 "parametros":{k:v(None,"F01","LC 341/2018 art. 28–29 e Anexo 10.1","Parâmetros próprios a serem definidos em plano de urbanização/regularização; não há tabela de índices específica no PDDUA. Aplicam-se os índices da zona urbana subjacente salvo norma de regularização.") for k in ["ca_basico","ca_maximo","taxa_ocupacao","gabarito_altura_max","taxa_permeabilidade","lote_minimo_m2","testada_minima_m","usos_permitidos","vagas"]} | {"recuos":{"frontal":None,"lateral":None,"fundos":None}},
 "observacoes":["Foco em regularização fundiária (REURB), não em produção de mercado."]})
zonas.append({"codigo":"ZEIS2","nome":"Zona Especial de Interesse Social 2","descricao":"Terrenos vazios ou subutilizados destinados à produção de HIS (PDDUA art. 29 II, Anexo 10.2; gestão pela LC 421/2021 alterada pela LC 516/2023).",
 "parametros":{
  "ca_basico":v("Igual ao da zona urbana/ZC onde a ZEIS 2 se localiza (Z5 → usa índices da Z4)","F07","LC 516/2023, art. 8º (altera LC 421/2021)"),
  "ca_maximo":v("Igual ao da zona urbana/ZC (Z5 → Z4: CAmáx 3); OODC pode ser autorizada como incentivo à HIS respeitando o CA máximo da zona","F01","LC 341/2018 art. 29 §1º; LC 516/2023 art. 8º (F07)"),
  "taxa_ocupacao":v("Igual à da zona urbana/ZC","F07","LC 516/2023 art. 8º"),
  "gabarito_altura_max":v(None,"F07","LC 516/2023 art. 8º","Sem altura em metros; segue IE da zona."),
  "taxa_permeabilidade":v("Conforme Zona Ambiental do terreno (Anexo 7.1)","F01","art. 25 e Anexo 7.1"),
  "recuos":{"frontal":v("Conforme zona urbana","F07","LC 516/2023 art. 8º"),"lateral":v("Conforme zona urbana","F07","LC 516/2023 art. 8º"),"fundos":v("Conforme zona urbana","F07","LC 516/2023 art. 8º")},
  "lote_minimo_m2":v("Conforme zona urbana; em loteamento L2: 200 m²","F05","LC 74/2005 art. 47"),
  "testada_minima_m":v({"meio_de_quadra":10,"esquina":15},"F05","LC 74/2005 art. 47 (L2)"),
  "usos_permitidos":v("Usos da zona urbana/ZC (Z5 → usos da Z4, o que libera R3/E1–E3 em ZEIS 2 situada em Z5); preferencialmente multirresidencial; mix de faixas: até 100% HBR (≥20% cadastro AMHASF), até 75% HMP (≥15%), até 50% HM (≥10%); se houver HMP/HM, mínimo 25% HBR; área máx. da UH 70 m²; 1 unidade comercial/serviço (mín. 12 m²) a cada 50 UH","F06","LC 421/2021 arts. 5º–7º; LC 516/2023 art. 8º; NT 02/2024 (F21)"),
  "vagas":v({"MZ1":"pode ser dispensada","MZ2":"mínimo 25% do total de unidades","MZ3":"mínimo 50% do total de unidades"},"F06","LC 421/2021 art. 6º III; NT 02/2024 (F21)","Dispensa/redução condicionada a ponto de ônibus a até 500 m (LC 421/2021 art. 6º). Redução vale também para as unidades comerciais; vagas de visitantes e motos calculadas sobre o total já reduzido (NT 02/2024).")},
 "observacoes":["Principal instrumento de incentivo a MCMV/HIS no município.","Renda: HBR até 3 SM; HMP >3 a 6 SM; HM >6 a 10 SM (LC 421/2021; PDDUA Anexo 1).","Percentual de cadastro AMHASF pode ser convertido em contrapartida ao FUNDHAB (LC 421 art. 5º §2º).","Mitigações em equipamentos comunitários com redução de 60% (MZ1), 30% (MZ2) e 15% (MZ3) – LC 516/2023 art. 7º 'e'.","Mapa das ZEIS 2: PDDUA Anexo 10.2 (F04) – lotes específicos devem ser conferidos no mapa/GeoPortal."]})
zonas.append({"codigo":"ZEIA2","nome":"Zona Especial de Interesse Ambiental 2","descricao":"Fragmentos de vegetação/áreas de interesse ambiental (PDDUA arts. 37–43, Anexo 15). ZEIA 1 = APPs; ZEIA 3 só TDC; ZEIA 4 OODC/TDC/preempção.",
 "parametros":{"ca_basico":v("Da zona urbana subjacente","F01","art. 43"),"ca_maximo":v("Da zona urbana subjacente","F01","art. 43"),
  "taxa_ocupacao":v(None,"F01","art. 38–40","Supressão máxima de 40% da vegetação (art. 40)."),
  "gabarito_altura_max":v("15 m (do piso do térreo à laje do último pavimento + 3 m)","F01","LC 341/2018 art. 38 (redação LC 349/2019 art. 8º – F02)"),
  "taxa_permeabilidade":v("60%","F01","art. 38"),"recuos":{"frontal":None,"lateral":None,"fundos":None},
  "lote_minimo_m2":v(5000,"F01","art. 38"),"testada_minima_m":v(None,"F01","art. 38","Não definida."),
  "usos_permitidos":v("Usos da zona urbana subjacente","F01","art. 43"),"vagas":VAGAS},
 "observacoes":["Restrição forte para MCMV: lotes ≥5.000 m², 60% permeável, 15 m de altura, sem compensação (art. 38 §2º)."]})

out={"municipio":"Campo Grande","uf":"MS","data_levantamento":"2026-10-27",
 "marco_legal_vigente":"PDDUA – LC 341/2018 (republicada/consolidada pela LC 349/2019) define zonas, usos (Anexo 8.1) e índices (Anexo 8.2); por força do art. 97 do PDDUA, até a revisão da legislação urbanística continuam aplicáveis os arts. 22 a 63-D da LOUOS (LC 74/2005 e alterações: categorias de uso, compatibilidade locacional, vagas, parcelamento, condomínios/URBIS). Revisão da LOUOS (e do Código de Obras) em andamento: minuta em consulta pública jan–fev/2026 e reunião pública em 02/03/2026; até 27/10/2026 não foi localizada publicação de nova LOUOS no DIOGRANDE (F27).",
 "fontes":F,"zonas":zonas,
 "macrozonas":{"MZ1":{"densidade_liquida_max_hab_ha":330,"diretriz":"compactação imediata/adensamento","fonte_id":"F01","artigo_anexo":"art. 20 I e art. 21"},
   "MZ2":{"densidade_liquida_max_hab_ha":240,"diretriz":"adensamento prioritário","fonte_id":"F01","artigo_anexo":"art. 20 II e art. 22"},
   "MZ3":{"densidade_liquida_max_hab_ha":120,"diretriz":"adensamento futuro; urbanização lenta e restritiva","fonte_id":"F01","artigo_anexo":"art. 20 III e art. 23"},
   "observacao":"Empreendimentos acima das densidades seguem critérios de legislação específica (art. 20 §2º) – não localizada."},
 "outorga_onerosa":{
  "base_legal":{"fonte_id":"F08","artigo_anexo":"LC 469/2022 (regulamenta PDDUA arts. 102–105)"},
  "aplicacao":{"valor":"Construção acima do CA básico até o CA máximo do Anexo 8.2; em todo o perímetro urbano e área de expansão; áreas não computáveis excluídas","fonte_id":"F01","artigo_anexo":"PDDUA arts. 102 §§4º–5º e 104"},
  "formula":{"valor":"VO = ((Ac − Ap) / At) × (Fid × Vt)","variaveis":{"Ac":"área construída computável total do projeto (m²)","Ap":"área permitida pelo CA básico (m²)","At":"área do terreno (m²)","Fid":"fator infraestrutura/densidade por zona","Vt":"valor do lote/gleba na guia do IPTU (ZEU: área × valor médio do m² da MZ3)"},"fonte_id":"F08","artigo_anexo":"LC 469/2022 art. 6º","observacao":"Definição literal de Ac/Ap conferir no art. 6º (texto em fonte com codificação corrompida, lido por imagem)."},
  "fator_fid_por_zona":{"valor":{"Z1":0.100,"Z2":0.250,"ZC":0.250,"EA1":0.250,"EA2":0.250,"EA3":0.250,"ZEIE":0.250,"Z3":0.400,"Z4":0.500,"Z5":2.000,"ZEU":4.000},"fonte_id":"F08","artigo_anexo":"LC 469/2022 art. 6º (tabela Fid)"},
  "limite":{"valor":"Até o CA máximo do Anexo 8.2","fonte_id":"F08","artigo_anexo":"LC 469/2022 art. 6º parágrafo único"},
  "descontos_fachada_ativa":{"valor":"Z1: desconto de 20% na OODC para multirresidencial com fachada ativa ≥20% da TO (nota 6); Z2/ZC: desconto de 20% após compra do 1º CA (nota 8)","fonte_id":"F01","artigo_anexo":"Anexo 8.2 notas 6 e 8"},
  "isencoes":{"valor":"I – órgãos da administração direta e indireta do município; II – empreendimentos de HIS; instituições de ensino superior; cinemas; centros de convenção e teatros localizados nas Zonas Urbanas 1 e nas Zonas de Centralidades","fonte_id":"F08","artigo_anexo":"LC 469/2022 art. 8º","observacao":"AMBIGUIDADE: a redação do inciso II não deixa claro se o recorte 'localizados nas Zonas Urbanas 1 e nas Zonas de Centralidades' se aplica também à HIS ou apenas aos demais usos listados. Confirmar com PLANURB antes de modelar viabilidade fora de Z1/ZC."},
  "pagamento":{"valor":"Pagamento via guia; certidão COODC emitida pela PLANURB em até 10 dias; pode ser substituído por obras/imóveis de interesse público (art. 7º); averbação na matrícula (art. 10); recursos ao FMDU, ≥30% para incisos VII/VIII do art. 158 do PDDUA (art. 12)","fonte_id":"F08","artigo_anexo":"LC 469/2022 arts. 5º, 7º, 9º–12; simulador: www.campogrande.ms.gov.br/planurb"},
  "incentivo_zeis":{"valor":"Nas ZEIS, o Executivo (ouvido o CMDU) pode autorizar OODC como incentivo à HIS, preferencialmente multirresidencial, respeitado o CA máximo da zona","fonte_id":"F01","artigo_anexo":"PDDUA art. 29 §1º"},
  "tdc":{"valor":"Transferência do Direito de Construir para fins incl. HIS; 5% ao FMDU em alienação entre particulares; mapas de áreas cedentes/receptoras Anexos 17.1/17.2; usa a mesma coluna OODC/TDC do Anexo 8.2","fonte_id":"F01","artigo_anexo":"PDDUA arts. 98–101, Anexo 17"},
  "ooaus":{"valor":"Voaus = ((A × VTu) × (P/100)) × Fn × Fl; Fn: L1 0,70, L2 0,50, L3 1,00; Fl: 1,00 lindeiro a área sem pavimentação, 0,70 com pavimentação; pagamento 40%/30%/30%","fonte_id":"F16","artigo_anexo":"Lei 6.795/2022 arts. 6º–7º; Lei 7.253/2024 (F17)"}},
 "zeis_his":{
  "definicoes":{"valor":"HBR: até 3 SM, máx. 1 vaga e 1 sanitário; HMP: >3 a 6 SM, máx. 1 vaga e até 2 sanitários; HM: >6 a 10 SM","fonte_id":"F01","artigo_anexo":"PDDUA Anexo 1 e art. 49; LC 421/2021 art. 6º"},
  "zeis1":{"valor":"Ocupações consolidadas (>5 anos) – regularização","fonte_id":"F01","artigo_anexo":"art. 29 I, Anexo 10.1"},
  "zeis2":{"valor":"Vazios/subutilizados para HIS; índices e usos da zona urbana/ZC, Z5→Z4","fonte_id":"F07","artigo_anexo":"PDDUA art. 29 II, Anexo 10.2; LC 421/2021; LC 516/2023 art. 8º"},
  "mix_obrigatorio":{"valor":"Até 100% HBR (mín. 20% p/ cadastro AMHASF); até 75% HMP (mín. 15%); até 50% HM (mín. 10%); com HMP/HM, mín. 25% HBR; percentual de cadastro conversível em contrapartida ao FUNDHAB","fonte_id":"F06","artigo_anexo":"LC 421/2021 art. 5º"},
  "area_max_uh_m2":{"valor":70,"fonte_id":"F06","artigo_anexo":"LC 421/2021 art. 6º"},
  "vagas":{"valor":{"MZ1":"dispensável","MZ2":"≥25% das UH","MZ3":"≥50% das UH"},"fonte_id":"F06","artigo_anexo":"LC 421/2021 art. 6º III; NT 02/2024 (F21)"},
  "comercio_local":{"valor":"1 unidade de comércio/serviço (mín. 12 m², acesso livre ao logradouro) a cada 50 UH em multirresidenciais ou URBIS","fonte_id":"F06","artigo_anexo":"LC 421/2021 art. 7º c; NT 02/2024 (F21)"},
  "mitigacao_equipamentos":{"valor":"Reduções de 60% (MZ1), 30% (MZ2), 15% (MZ3) nas mitigações em equipamentos comunitários","fonte_id":"F07","artigo_anexo":"LC 516/2023 art. 7º 'e'"},
  "loteamento_interesse_social_L2":{"valor":"Lote mín. 200 m²; testada 10 m (meio) / 15 m (esquina); 10% de áreas de domínio público (excluídas APPs); esgoto individualizado admitido","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 47"},
  "urbis":{"valor":"Urbanização Integrada de Interesse Social: infraestrutura reduzida (revestimento primário exceto vias de ônibus; esgoto individual), vias internas 9 m, 90 m²/unidade privativa (exceções R2), lazer 3 m²/UH na MZ1 e 6 m²/UH nas demais; dispensa dos equipamentos do art. 28","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 50-A"},
  "oodc_his":{"valor":"Isenção de OODC para HIS (com ambiguidade territorial) e OODC-incentivo em ZEIS","fonte_id":"F08","artigo_anexo":"LC 469/2022 art. 8º II; PDDUA art. 29 §1º"},
  "incentivos_fiscais":{"valor":"IPTU: isenção para mutuários do MCMV faixa social, desfavelamento e loteamentos sociais do poder público (valor venal ≤ R$ 83.000) – Lei 5.680/2016 e Decreto 15.220/2022; isenção de IPTU entre alvará e contrato com 1º beneficiário para HIS de iniciativa dos poderes públicos estadual/municipal – LC 407/2021","fonte_id":"F24","artigo_anexo":"Guia Prático de Isenções de IPTU 2026, itens 5 e 9","observacao":"Leis citadas não baixadas na íntegra; isenções de IPTU descritas para iniciativa pública/mutuários, não para incorporador privado. Isenções de ITBI/ISS para HIS não confirmadas em fonte oficial (ver lacunas)."}},
 "outros_parametros":{
  "eiv":{"valor":"Exigido p/ empreendimentos residenciais com mais de 100 unidades; área construída >20.000 m²; >200 vagas; lotação >600 pessoas; empreendimentos que usem OODC, TDC ou OUC; etc. EIV/RIV prévio à Guia de Diretrizes Urbanísticas (GDU), com audiência pública (convocação com 25 dias úteis)","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 24 §1º I–VII (redação LC 186/2011); PDDUA arts. 130–131; Decreto 15.846/2024 arts. 1º–3º (F19)"},
  "equipamentos_comunitarios":{"valor":"Empreendimentos residenciais >50 UH: escola 0,30 m²/UH, CEINF 0,30 m²/UH, UBS 0,05 m²/UH (UBS não exigida até 100 UH); substituível; dispensado em URBIS","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 28 (LC 87/2006) e art. 50-A par. único"},
  "categorias_porte":{"valor":"R1 = 1 un.; R2 = 2–25 un.; R3 = 26–50 un.; E1 = 51–100 UH; E2 = 101–250 UH; E3 = >251 UH","fonte_id":"F05","artigo_anexo":"LC 74/2005 Anexo IV, Tabelas 5 e 6 (LC 205/2012; Tabela 6 republicada pela LC 373/2019 – F12)"},
  "compatibilidade_locacional_via":{"valor":{"R1":"sem exigência","R2":"via com faixa de domínio ≥12 m (dispensada até 6 UH)","R3":"≥15 m","E1":"≥15 m","E2":"≥18 m (≥15 m até 200 UH)","E3":"≥22 m"},"infraestrutura":"R2/R3/E1: água, esgoto e energia; E2/E3: água, pavimentação, drenagem, esgoto e energia","fonte_id":"F12","artigo_anexo":"LC 74/2005 Anexo V (redação LC 373/2019, notas 4 e 5); medição: Res. SEMADUR 73/2024 (F22)"},
  "limites_condominio":{"valor":"Condomínio/Urbanização Integrada (R2, R3, E1–E3): vias internas 6 m + calçadas 1,5 m (9 m); 90 m²/unidade privativa em multirresidencial horizontal; lazer 3 m²/UH a partir de 10 UH; testada >100 m exige faixa non aedificandi de 2 m; não pode interromper hierarquia viária – glebas >20.000 m² em empreendimento residencial devem ser loteadas quando interromperem vias arteriais/coletoras projetadas","fonte_id":"F05","artigo_anexo":"LC 74/2005 arts. 36 IV, 37 VII e 50"},
  "doacao_areas":{"valor":"L1: 20% de áreas públicas; L2: 10%; L4: 12%; desmembramento >20.000 m²: 5% (abaixo de 5.000 m² conversível em dinheiro); quadras ≤250 m","fonte_id":"F05","artigo_anexo":"LC 74/2005 arts. 44–47 e 49"},
  "fachada_ativa":{"valor":"Ocupação da fachada junto ao passeio por comércio/serviço de acesso livre em edifício residencial; benefícios: TO térreo/1º 0,7 (Z1–Z3, ZC; até 0,8 em Z1 c/ contrapartida), recuo frontal livre no térreo/1º pav. e descontos de 20% na OODC (Z1/Z2/ZC)","fonte_id":"F01","artigo_anexo":"PDDUA Anexo 1 e Anexo 8.2 notas 1, 2, 6, 7, 8"},
  "empenas_divisa":{"valor":"Empenas nas divisas laterais/fundos até 6,5 m; acima, recuo mín. 1,50 m; até 3 m de extensão p/ dutos, caixa d'água, escada e elevador","fonte_id":"F11","artigo_anexo":"LC 74/2005 art. 37 III (redação LC 445/2022)"},
  "recuo_frontal_usos_admitidos":{"valor":"Lixeira, guarita ≤10 m², acessos, medidores, estacionamento descoberto","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 37 II"},
  "arborizacao_permeavel":{"valor":"25% da área permeável com vegetação arbórea; 1 árvore por unidade privativa em condomínio horizontal; alternativa: caixa de captação de 30 l/m² de terreno não atendido","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 37 VI"},
  "acessos_veiculos":{"valor":"2,80 m até 20 vagas; 5,00 m (ou 2×2,80) de 21 a 200; 3 m por pista acima de 200; 5 m da esquina; rebaixamento ≤60% da testada e ≤12 m","fonte_id":"F05","artigo_anexo":"LC 74/2005 art. 39"},
  "app_restricoes":{"valor":"Faixas de 30 m (cursos <10 m), 50 m (10–50 m e nascentes), 100 m (APA Lageado)","fonte_id":"F01","artigo_anexo":"PDDUA art. 39 (ZEIA1); LC 74/2005 arts. 36 e 43"},
  "peuc_iptu_progressivo":{"valor":"Aplicáveis em MZ1, MZ2, ZEIS e ZC (imóveis não edificados/subutilizados)","fonte_id":"F01","artigo_anexo":"PDDUA arts. 21–23, 29 §3º, 33 §2º, 120–127"},
  "regulamentacao_vias_limitrofes":{"valor":"Lotes em vias limítrofes de zonas/eixos podem optar por usos (8.1) e índices (8.2) de uma das zonas, sem opção parcial; exceto ZEIE/ZC","fonte_id":"F09","artigo_anexo":"Decreto 15.123/2022 arts. 3º–11"}},
 "resumo_mcmv":[
  "Maior potencial construtivo: Z1 (CAbás 4 / CAmáx 5, IE livre, Fid 0,10 – OODC mais barata) e Z2/ZC (CAbás 3 / CAmáx 5; IE 6 → livre com OODC; Fid 0,25). Porém terra cara e MZ1.",
  "Equilíbrio para MCMV: Z3 (CAbás 2 / CAmáx 4, IE 4→8 com OODC, Fid 0,40) e eixos EA1/EA2 (CAbás 2,8 / CAmáx 3,3, IE até 6,6; residencial até R3 = 50 UH por lote). Z4 (CAbás 2 / CAmáx 3, IE 4→6, Fid 0,50) – bairros periféricos com terra mais barata e uso E1–E3 liberado.",
  "Z5 (CAbás 1 / CAmáx 1,5; só R1/R2) é desfavorável – exceto se o terreno estiver em ZEIS 2, quando passa a usar índices e usos da Z4 (LC 516/2023).",
  "ZEIS 2: HIS com redução de vagas (MZ1 dispensável; MZ2 25%; MZ3 50%), mix HBR/HMP/HM, UH ≤70 m², mitigações reduzidas, OODC-incentivo; isenção de OODC p/ HIS (LC 469 art. 8º II, com ambiguidade).",
  "Gatilhos de custo: >50 UH equipamentos comunitários (exceto URBIS); >100 UH ou uso de OODC/TDC exige EIV + audiência pública; E2 exige via ≥18 m (15 m até 200 UH), E3 via ≥22 m; 1 vaga/UH fora de ZEIS."],
 "lacunas":[
  "Gabarito/altura máxima em metros: não existe no Anexo 8.2 para as zonas urbanas (controle por IE/CA/recuos) – valor null; exceção ZEIA2 (15 m). Limites aeronáuticos da ZEPA (Anexo 9) dependem dos planos do COMAER, não tabulados.",
  "Taxa de permeabilidade das ZC, ZEIE, eixos, Distrito de Anhanduí e ZEU depende da Zona Ambiental do lote (mapa Anexo 7) – não atribuída de forma única; Anhanduí e ZEU não constam da tabela do Anexo 7.1.",
  "LC 469/2022 art. 8º II: alcance territorial da isenção de OODC para HIS ambíguo (todo o município ou só Z1/ZC). Consultar PLANURB.",
  "Anexo VI (vagas) republicado pela LC 373/2019: o PDF oficial disponível termina na linha 'Indústria' (linha 'Residencial' não visível nessa publicação). Mantido 1 vaga/UH com base na LC 74 consolidada (LC 205/2012) e na NT 02/2024 (SEMADUR), que cita expressamente a regra.",
  "Densidades acima do limite da macrozona (art. 20 §2º PDDUA) – 'legislação específica' não localizada.",
  "Parâmetros específicos de ZEIS 1 (regularização) não tabelados no PDDUA – null.",
  "Isenções de ITBI/ISS para HIS/MCMV (citadas em fontes não oficiais como LC 328/2018 e LC 406/2021) não confirmadas em fonte oficial durante este levantamento.",
  "LC 263/2015 (PLDE – polos de desenvolvimento econômico) traz regime urbanístico específico anterior ao PDDUA; não verificado se permanece vigente após a LC 341/2018.",
  "LC 411/2021 (art. 54 da LC 74 – MZ3 apenas L3): texto lido por imagem; confirmar alcance antes de modelar loteamentos na MZ3.",
  "Lei 6.914/2022 (IA/IRA): fórmula IA = V^α × D^β registrada; anexos de pesos (CV/CD) não transcritos.",
  "Código de Obras (Lei 1.866/1979) não levantado em detalhe (citado na NT 02/2024 só para loja mín. 12 m²).",
  "Revisão da LOUOS/Código de Obras em tramitação (consulta pública jan–fev/2026, reunião 02/03/2026): não localizada sanção/publicação até 27/10/2026; parâmetros de LC 74/2005 podem mudar em breve.",
  "Delimitação exata por lote de ZEIS 2, eixos, centralidades e ZEIAs exige consulta aos mapas (F04) ou GeoPortal/GDU da PLANURB – não incluída no JSON."]}
json.dump(out,open("/workspace/legislacao/campo-grande-ms.json","w"),ensure_ascii=False,indent=2)
print(len(zonas))
import subprocess; subprocess.run(["python3","/workspace/legislacao/adicionar_geografico.py"], check=True)
