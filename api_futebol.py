import requests
import json
from datetime import datetime
import os
import glob
from collections import defaultdict, Counter
import statistics
import math

# ============================================================================
# 🔐 CONFIGURAÇÃO DA API (mantenha sua chave aqui)
# ============================================================================
SUA_CHAVE_API = "f578bdac06mshb948f23a84f1b8bp117d92jsnde1c375f5b9e"
URL_BASE = "https://futebol-virtual-bet3651.p.rapidapi.com"

CABECALHOS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-RapidAPI-Key": SUA_CHAVE_API,
    "X-RapidAPI-Host": "futebol-virtual-bet3651.p.rapidapi.com"
}

# ============================================================================
# 🛠️ FUNÇÃO PRINCIPAL PARA OBTER DADOS COM ODDS
# ============================================================================
def obter_dados_com_odds(liga="copa", quantidade=1):
    """Obtém dados dos jogos com todas as odds (probabilidades)"""
    print(f"\n📊 Buscando {quantidade} jogo(s) da liga '{liga}' com odds...")
    print("="*70)
    
    if quantidade < 1:
        quantidade = 1
    elif quantidade > 1500:
        print("⚠️  Quantidade ajustada para o máximo de 1500 jogos")
        quantidade = 1500
    
    parametros = {
        "league": liga,
        "home": "bet365",
        "sport_id": 1,
        "limit": quantidade,
        "activate_odds": "true"
    }
    
    try:
        resposta = requests.post(
            f"{URL_BASE}/matchs",
            data=parametros,
            headers=CABECALHOS,
            timeout=10
        )
        resposta.raise_for_status()
        dados = resposta.json()
        
        if dados and dados.get("status"):
            print(f"✅ Sucesso! {dados['returned_matchs']} jogo(s) retornado(s).")
            return dados
        else:
            print("❌ A API não retornou dados válidos.")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

# ============================================================================
# 📊 FUNÇÕES PARA VISUALIZAR AS ODDS (do código original)
# ============================================================================

def mostrar_odds_principais(dados):
    """Mostra as odds mais importantes de forma organizada"""
    if not dados or "matchs" not in dados:
        print("⚠️  Nenhum dado para mostrar.")
        return
    
    for i, jogo in enumerate(dados["matchs"], 1):
        print(f"\n{'='*60}")
        print(f"🎯 JOGO {i}: {jogo['timeA']} vs {jogo['timeB']}")
        print(f"{'='*60}")
        print(f"📅 Horário: {jogo['horario']} | ID: {jogo['id']}")
        print(f"📈 Resultado: {jogo.get('resultado', 'N/A')}")
        print(f"📊 Total de odds: {len(jogo.get('odds', {}))} tipos")
        print("-"*50)
        
        odds = jogo.get("odds", {})
        if not odds:
            print("⚠️  Este jogo não tem odds disponíveis.")
            continue
        
        # Grupo 1: Resultado Final (as mais importantes)
        print("\n🏆 RESULTADO FINAL:")
        print("-"*30)
        if "odd_resultado_final_casa" in odds:
            print(f"  • Vitória de {jogo['timeA']}: {odds['odd_resultado_final_casa']}")
        if "odd_resultado_final_empate" in odds:
            print(f"  • Empate: {odds['odd_resultado_final_empate']}")
        if "odd_resultado_final_fora" in odds:
            print(f"  • Vitória de {jogo['timeB']}: {odds['odd_resultado_final_fora']}")
        
        # Grupo 2: Over/Under (total de gols)
        print("\n⚽ TOTAL DE GOLS (OVER/UNDER):")
        print("-"*30)
        over_under_pares = [
            ("odd_over_0.5", "odd_under_0.5", "0.5 gols"),
            ("odd_over_1.5", "odd_under_1.5", "1.5 gols"),
            ("odd_over_2.5", "odd_under_2.5", "2.5 gols"),
            ("odd_over_3.5", "odd_under_3.5", "3.5 gols")
        ]
        
        for over_key, under_key, desc in over_under_pares:
            if over_key in odds and under_key in odds:
                print(f"  • Over {desc}:  {odds[over_key]:<6} | Under {desc}: {odds[under_key]}")
        
        # Grupo 3: Ambos marcam
        print("\n🔀 AMBOS OS TIMES MARCAM:")
        print("-"*30)
        if "odd_ambas_sim" in odds:
            print(f"  • SIM (ambos marcam): {odds['odd_ambas_sim']}")
        if "odd_ambas_nao" in odds:
            print(f"  • NÃO (não marcam ambos): {odds['odd_ambas_nao']}")
        
        # Grupo 4: Dupla chance
        print("\n🎲 DUPLA CHANCE:")
        print("-"*30)
        dupla_chance = [
            ("odd_dupla_hipotese_casa_ou_empate", "Casa ou Empate"),
            ("odd_dupla_hipotese_fora_ou_empate", "Fora ou Empate"),
            ("odd_dupla_hipotese_casa_ou_fora", "Casa ou Fora")
        ]
        
        for key, desc in dupla_chance:
            if key in odds:
                print(f"  • {desc}: {odds[key]}")

def mostrar_todas_odds(dados, limite_por_jogo=20):
    """Mostra TODAS as odds disponíveis (até um limite por jogo)"""
    if not dados or "matchs" not in dados:
        print("⚠️  Nenhum dado para mostrar.")
        return
    
    for i, jogo in enumerate(dados["matchs"], 1):
        print(f"\n{'='*70}")
        print(f"📈 TODAS AS ODDS - JOGO {i}: {jogo['timeA']} vs {jogo['timeB']}")
        print(f"{'='*70}")
        
        odds = jogo.get("odds", {})
        if not odds:
            print("⚠️  Este jogo não tem odds disponíveis.")
            continue
        
        total_odds = len(odds)
        print(f"📊 Total de odds disponíveis: {total_odds}")
        print(f"📅 Mostrando as primeiras {min(limite_por_jogo, total_odds)}:")
        print("-"*70)
        
        # Organiza as odds em ordem alfabética
        odds_ordenadas = sorted(odds.items(), key=lambda x: x[0])
        
        for idx, (nome_odd, valor) in enumerate(odds_ordenadas[:limite_por_jogo], 1):
            # Formata o nome para melhor legibilidade
            nome_formatado = nome_odd.replace("odd_", "").replace("_", " ").title()
            print(f"{idx:3d}. {nome_formatado:<50} → {valor}")
        
        if total_odds > limite_por_jogo:
            print(f"\n📝 ... e mais {total_odds - limite_por_jogo} odds não mostradas.")
        
        print("-"*70)

# ============================================================================
# 🔮 ANALISADOR AVANÇADO COM MÚLTIPLAS ESTRATÉGIAS
# ============================================================================

def analise_avançada_tendencias(file_path=None, dados_diretos=None):
    """
    ANÁLISE AVANÇADA com múltiplas estratégias para aumentar probabilidade
    """
    print("\n" + "="*80)
    print("🎯 ANALISADOR AVANÇADO - ESTRATÉGIAS PARA APOSTAS CERTAS")
    print("="*80)
    
    dados = None
    
    if dados_diretos:
        dados = dados_diretos
        print("📊 Analisando dados diretamente da API...")
    elif file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            print(f"📁 Analisando arquivo: {file_path}")
        except:
            print(f"❌ Erro ao ler arquivo: {file_path}")
            return
    else:
        arquivos_json = glob.glob("odds_detalhadas_*.json")
        if arquivos_json:
            arquivo_mais_recente = max(arquivos_json, key=os.path.getctime)
            try:
                with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                print(f"📁 Usando arquivo mais recente: {arquivo_mais_recente}")
            except:
                print("❌ Erro ao ler arquivo JSON.")
                return
        else:
            print("❌ Nenhum dado disponível.")
            return
    
    if not dados or "matchs" not in dados:
        print("❌ Dados inválidos para análise.")
        return
    
    jogos = dados["matchs"]
    total_jogos = len(jogos)
    
    if total_jogos < 5:
        print(f"⚠️  Poucos jogos para análise ({total_jogos}). Busque pelo menos 10 jogos.")
        return
    
    print(f"📊 Analisando {total_jogos} jogos da liga '{dados.get('league', 'desconhecida')}'")
    print("-"*80)
    
    # ============================================================================
    # 📈 ANÁLISE ESTATÍSTICA AVANÇADA
    # ============================================================================
    
    stats = {
        'ambas_marcam': {'sim': 0, 'nao': 0},
        'over_2.5': {'sim': 0, 'nao': 0},
        'over_1.5': {'sim': 0, 'nao': 0},
        'under_2.5': {'sim': 0, 'nao': 0},
        'total_gols': 0,
        'gols_por_jogo': [],
        'placares': [],
        'vitorias_casa': 0,
        'vitorias_fora': 0,
        'empates': 0,
        'gols_primeiro_tempo': 0,
        'gols_segundo_tempo': 0,
        'times_marcam_casa': 0,
        'times_marcam_fora': 0,
        'clean_sheets_casa': 0,
        'clean_sheets_fora': 0,
        'ambas_marcam_primeiro_tempo': {'sim': 0, 'nao': 0},
        'ambas_marcam_segundo_tempo': {'sim': 0, 'nao': 0},
    }
    
    # Dados por tempo de jogo
    horario_stats = defaultdict(lambda: {
        'total_jogos': 0,
        'ambas_marcam': {'sim': 0, 'nao': 0},
        'over_2.5': {'sim': 0, 'nao': 0},
        'total_gols': 0
    })
    
    # Dados por combinação de times (últimos 20 caracteres do nome)
    combinação_stats = defaultdict(lambda: {
        'total_jogos': 0,
        'ambas_marcam': {'sim': 0, 'nao': 0},
        'over_2.5': {'sim': 0, 'nao': 0},
        'total_gols': 0
    })
    
    print("\n🎯 ANÁLISE DETALHADA DOS JOGOS:")
    print("-"*80)
    
    for i, jogo in enumerate(jogos, 1):
        try:
            resultado = jogo.get('resultado', '0-0')
            resultadoHt = jogo.get('resultadoHt', '0-0')
            timeA = jogo.get('timeA', 'Time A')
            timeB = jogo.get('timeB', 'Time B')
            horario = jogo.get('horario', '0.0')
            
            if '-' in resultado:
                gols_a, gols_b = map(int, resultado.split('-'))
                total_gols = gols_a + gols_b
                
                # Resultado primeiro tempo
                if '-' in resultadoHt:
                    gols_ht_a, gols_ht_b = map(int, resultadoHt.split('-'))
                    stats['gols_primeiro_tempo'] += gols_ht_a + gols_ht_b
                    stats['gols_segundo_tempo'] += (gols_a - gols_ht_a) + (gols_b - gols_ht_b)
                    
                    # Ambas marcam no primeiro tempo
                    if gols_ht_a > 0 and gols_ht_b > 0:
                        stats['ambas_marcam_primeiro_tempo']['sim'] += 1
                    else:
                        stats['ambas_marcam_primeiro_tempo']['nao'] += 1
                    
                    # Ambas marcam no segundo tempo
                    if (gols_a - gols_ht_a) > 0 and (gols_b - gols_ht_b) > 0:
                        stats['ambas_marcam_segundo_tempo']['sim'] += 1
                    else:
                        stats['ambas_marcam_segundo_tempo']['nao'] += 1
                
                # Estatísticas básicas
                ambas_marcou = gols_a > 0 and gols_b > 0
                over_25 = total_gols > 2.5
                over_15 = total_gols > 1.5
                under_25 = total_gols < 2.5
                
                stats['total_gols'] += total_gols
                stats['gols_por_jogo'].append(total_gols)
                stats['placares'].append((gols_a, gols_b))
                
                if gols_a > 0:
                    stats['times_marcam_casa'] += 1
                if gols_b > 0:
                    stats['times_marcam_fora'] += 1
                
                if gols_a == 0:
                    stats['clean_sheets_casa'] += 1
                if gols_b == 0:
                    stats['clean_sheets_fora'] += 1
                
                # Resultado final
                if gols_a > gols_b:
                    stats['vitorias_casa'] += 1
                elif gols_b > gols_a:
                    stats['vitorias_fora'] += 1
                else:
                    stats['empates'] += 1
                
                # Atualiza contagens
                if ambas_marcou:
                    stats['ambas_marcam']['sim'] += 1
                else:
                    stats['ambas_marcam']['nao'] += 1
                
                if over_25:
                    stats['over_2.5']['sim'] += 1
                else:
                    stats['over_2.5']['nao'] += 1
                
                if over_15:
                    stats['over_1.5']['sim'] += 1
                else:
                    stats['over_1.5']['nao'] += 1
                
                if under_25:
                    stats['under_2.5']['sim'] += 1
                else:
                    stats['under_2.5']['nao'] += 1
                
                # Análise por horário
                try:
                    hora_float = float(horario)
                    if hora_float < 1.0:
                        hora_key = "Madrugada (0-1h)"
                    elif hora_float < 6.0:
                        hora_key = "Manhã (1-6h)"
                    elif hora_float < 12.0:
                        hora_key = "Tarde (6-12h)"
                    elif hora_float < 18.0:
                        hora_key = "Noite (12-18h)"
                    else:
                        hora_key = "Noite (18-24h)"
                    
                    horario_stats[hora_key]['total_jogos'] += 1
                    horario_stats[hora_key]['total_gols'] += total_gols
                    if ambas_marcou:
                        horario_stats[hora_key]['ambas_marcam']['sim'] += 1
                    else:
                        horario_stats[hora_key]['ambas_marcam']['nao'] += 1
                    if over_25:
                        horario_stats[hora_key]['over_2.5']['sim'] += 1
                    else:
                        horario_stats[hora_key]['over_2.5']['nao'] += 1
                except:
                    pass
                
                # Análise por combinação de times (usando últimos caracteres)
                comb_key = f"{timeA[-10:]}_{timeB[-10:]}"
                combinação_stats[comb_key]['total_jogos'] += 1
                combinação_stats[comb_key]['total_gols'] += total_gols
                if ambas_marcou:
                    combinação_stats[comb_key]['ambas_marcam']['sim'] += 1
                else:
                    combinação_stats[comb_key]['ambas_marcam']['nao'] += 1
                if over_25:
                    combinação_stats[comb_key]['over_2.5']['sim'] += 1
                else:
                    combinação_stats[comb_key]['over_2.5']['nao'] += 1
                
                # Exibe jogo
                simbolo_ambas = "✅" if ambas_marcou else "❌"
                simbolo_over = "✅" if over_25 else "❌"
                print(f"{i:2d}. {timeA[:15]:<15} {gols_a}-{gols_b} {timeB[:15]:<15} "
                      f"| Ambas: {simbolo_ambas} | Over2.5: {simbolo_over} | Total: {total_gols}g")
                
        except Exception as e:
            print(f"{i:2d}. ⚠️  Erro: {str(e)[:30]}...")
            continue
    
    # ============================================================================
    # 📊 CÁLCULO DAS PROBABILIDADES
    # ============================================================================
    
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS DETALHADAS:")
    print("="*80)
    
    # Probabilidades básicas
    prob_ambas = calcular_probabilidade(stats['ambas_marcam'])
    prob_over25 = calcular_probabilidade(stats['over_2.5'])
    prob_over15 = calcular_probabilidade(stats['over_1.5'])
    prob_under25 = calcular_probabilidade(stats['under_2.5'])
    
    media_gols = stats['total_gols'] / total_jogos if total_jogos > 0 else 0
    media_gols_ht = stats['gols_primeiro_tempo'] / total_jogos if total_jogos > 0 else 0
    media_gols_st = stats['gols_segundo_tempo'] / total_jogos if total_jogos > 0 else 0
    
    # Desvio padrão dos gols
    desvio_gols = statistics.stdev(stats['gols_por_jogo']) if len(stats['gols_por_jogo']) > 1 else 0
    
    print(f"\n🎯 PROBABILIDADES PRINCIPAIS:")
    print(f"   • Ambas Marcam:        {prob_ambas:.1f}%")
    print(f"   • Over 2.5 gols:       {prob_over25:.1f}%")
    print(f"   • Over 1.5 gols:       {prob_over15:.1f}%")
    print(f"   • Under 2.5 gols:      {prob_under25:.1f}%")
    
    print(f"\n⚽ ESTATÍSTICAS DE GOLS:")
    print(f"   • Média total:         {media_gols:.2f} gols/jogo")
    print(f"   • 1º Tempo:            {media_gols_ht:.2f} gols")
    print(f"   • 2º Tempo:            {media_gols_st:.2f} gols")
    print(f"   • Desvio padrão:       {desvio_gols:.2f}")
    print(f"   • Times marcam em casa: {stats['times_marcam_casa']}/{total_jogos} ({(stats['times_marcam_casa']/total_jogos*100):.1f}%)")
    print(f"   • Times marcam fora:    {stats['times_marcam_fora']}/{total_jogos} ({(stats['times_marcam_fora']/total_jogos*100):.1f}%)")
    
    print(f"\n🏆 RESULTADOS:")
    print(f"   • Vitórias Casa:       {stats['vitorias_casa']} ({(stats['vitorias_casa']/total_jogos*100):.1f}%)")
    print(f"   • Vitórias Fora:       {stats['vitorias_fora']} ({(stats['vitorias_fora']/total_jogos*100):.1f}%)")
    print(f"   • Empates:             {stats['empates']} ({(stats['empates']/total_jogos*100):.1f}%)")
    
    # ============================================================================
    # 🔍 PADRÕES OCULTOS E CORRELAÇÕES
    # ============================================================================
    
    print("\n" + "="*80)
    print("🔍 PADRÕES OCULTOS E CORRELAÇÕES:")
    print("="*80)
    
    # Padrão: Ambas Marcam + Over 2.5 juntos
    ambas_over_count = 0
    for jogo in jogos:
        try:
            resultado = jogo.get('resultado', '0-0')
            if '-' in resultado:
                gols_a, gols_b = map(int, resultado.split('-'))
                if gols_a > 0 and gols_b > 0 and (gols_a + gols_b) > 2.5:
                    ambas_over_count += 1
        except:
            continue
    
    prob_ambas_over = (ambas_over_count / total_jogos * 100) if total_jogos > 0 else 0
    
    # Padrão: Under 2.5 + Ambas Não Marcam
    under_ambas_nao_count = 0
    for jogo in jogos:
        try:
            resultado = jogo.get('resultado', '0-0')
            if '-' in resultado:
                gols_a, gols_b = map(int, resultado.split('-'))
                if (gols_a + gols_b) < 2.5 and (gols_a == 0 or gols_b == 0):
                    under_ambas_nao_count += 1
        except:
            continue
    
    prob_under_ambas_nao = (under_ambas_nao_count / total_jogos * 100) if total_jogos > 0 else 0
    
    print(f"\n🎲 CORRELAÇÕES IMPORTANTES:")
    print(f"   • Ambas Marcam E Over 2.5:   {prob_ambas_over:.1f}% dos jogos")
    print(f"   • Under 2.5 E Ambas Não:     {prob_under_ambas_nao:.1f}% dos jogos")
    
    # Padrão de placares mais comuns
    placar_counter = Counter(stats['placares'])
    placares_comuns = placar_counter.most_common(5)
    
    print(f"\n📊 PLACARES MAIS COMUNS:")
    for placar, count in placares_comuns:
        porcentagem = (count / total_jogos) * 100
        print(f"   • {placar[0]}-{placar[1]}: {count} vezes ({porcentagem:.1f}%)")
    
    # ============================================================================
    # 📈 ANÁLISE POR HORÁRIO
    # ============================================================================
    
    if horario_stats:
        print("\n" + "="*80)
        print("⏰ ANÁLISE POR HORÁRIO DO JOGO:")
        print("="*80)
        
        for horario, dados_hora in sorted(horario_stats.items()):
            if dados_hora['total_jogos'] >= 3:  # Só mostra se tiver pelo menos 3 jogos
                prob_ambas_hora = calcular_probabilidade(dados_hora['ambas_marcam'])
                prob_over_hora = calcular_probabilidade(dados_hora['over_2.5'])
                media_gols_hora = dados_hora['total_gols'] / dados_hora['total_jogos'] if dados_hora['total_jogos'] > 0 else 0
                
                print(f"\n   🕒 {horario}:")
                print(f"      • Jogos: {dados_hora['total_jogos']}")
                print(f"      • Ambas Marcam: {prob_ambas_hora:.1f}%")
                print(f"      • Over 2.5: {prob_over_hora:.1f}%")
                print(f"      • Média gols: {media_gols_hora:.2f}")
                
                # Sugestão baseada no horário
                if prob_ambas_hora > 60:
                    print(f"      💡 SUGESTÃO: FORTE para Ambas Marcam neste horário!")
                elif prob_ambas_hora < 30:
                    print(f"      💡 SUGESTÃO: EVITAR Ambas Marcam neste horário!")
    
    # ============================================================================
    # 📊 TENDÊNCIA TEMPORAL
    # ============================================================================
    
    print("\n" + "="*80)
    print("📈 TENDÊNCIA TEMPORAL (últimos vs primeiros jogos):")
    print("="*80)
    
    stats_primeira = {'prob_ambas': 0, 'prob_over25': 0, 'media_gols': 0}
    stats_segunda = {'prob_ambas': 0, 'prob_over25': 0, 'media_gols': 0}
    
    if total_jogos >= 10:
        metade = total_jogos // 2
        primeira_metade = jogos[metade:]
        segunda_metade = jogos[:metade]
        
        stats_primeira = analisar_conjunto_jogos(primeira_metade)
        stats_segunda = analisar_conjunto_jogos(segunda_metade)
        
        print(f"\n📅 Primeira metade ({len(primeira_metade)} jogos mais antigos):")
        print(f"   • Ambas Marcam: {stats_primeira['prob_ambas']:.1f}%")
        print(f"   • Over 2.5: {stats_primeira['prob_over25']:.1f}%")
        print(f"   • Média gols: {stats_primeira['media_gols']:.2f}")
        
        print(f"\n📅 Segunda metade ({len(segunda_metade)} jogos mais recentes):")
        print(f"   • Ambas Marcam: {stats_segunda['prob_ambas']:.1f}%")
        print(f"   • Over 2.5: {stats_segunda['prob_over25']:.1f}%")
        print(f"   • Média gols: {stats_segunda['media_gols']:.2f}")
        
        # Calcula tendência
        tendencia_ambas = stats_segunda['prob_ambas'] - stats_primeira['prob_ambas']
        tendencia_over = stats_segunda['prob_over25'] - stats_primeira['prob_over25']
        
        print(f"\n📊 TENDÊNCIA (recente - antigo):")
        print(f"   • Ambas Marcam: {tendencia_ambas:+.1f}%", end=" ")
        if tendencia_ambas > 5:
            print("📈 FORTE ASCENDENTE")
        elif tendencia_ambas > 0:
            print("↗️  Leve ascensão")
        elif tendencia_ambas < -5:
            print("📉 FORTE DESCENDENTE")
        elif tendencia_ambas < 0:
            print("↘️  Leve descida")
        else:
            print("➡️  Estável")
        
        print(f"   • Over 2.5: {tendencia_over:+.1f}%", end=" ")
        if tendencia_over > 5:
            print("📈 FORTE ASCENDENTE")
        elif tendencia_over > 0:
            print("↗️  Leve ascensão")
        elif tendencia_over < -5:
            print("📉 FORTE DESCENDENTE")
        elif tendencia_over < 0:
            print("↘️  Leve descida")
        else:
            print("➡️  Estável")
    
    # ============================================================================
    # 🎯 ESTRATÉGIAS DE APOSTA RECOMENDADAS
    # ============================================================================
    
    print("\n" + "="*80)
    print("💰 ESTRATÉGIAS RECOMENDADAS PARA APOSTAS:")
    print("="*80)
    
    estrategias = []
    
    # Estratégia 1: Baseada em probabilidade simples
    if prob_ambas > 55:
        estrategias.append(("🎯 ESTRATÉGIA 1: Ambas Marcam SIM", 
                          f"Probabilidade alta ({prob_ambas:.1f}%)", 
                          "CONSIDERE apostar em Ambas Marcam - SIM"))
    elif prob_ambas < 35:
        estrategias.append(("🎯 ESTRATÉGIA 1: Ambas Marcam NÃO", 
                          f"Probabilidade baixa ({prob_ambas:.1f}%)", 
                          "CONSIDERE apostar em Ambas Marcam - NÃO"))
    
    # Estratégia 2: Baseada em Over/Under
    if prob_over25 > 55:
        estrategias.append(("🎯 ESTRATÉGIA 2: Over 2.5 SIM", 
                          f"Probabilidade alta ({prob_over25:.1f}%)", 
                          "CONSIDERE apostar em Over 2.5 - SIM"))
    elif prob_under25 > 60:
        estrategias.append(("🎯 ESTRATÉGIA 2: Under 2.5 SIM", 
                          f"Probabilidade alta ({prob_under25:.1f}%)", 
                          "CONSIDERE apostar em Under 2.5 - SIM"))
    
    # Estratégia 3: Baseada em correlação
    if prob_ambas_over > 40:
        estrategias.append(("🎯 ESTRATÉGIA 3: Combo Ambas+Over", 
                          f"Correlação forte ({prob_ambas_over:.1f}%)", 
                          "CONSIDERE apostar em Ambas SIM E Over 2.5"))
    
    # Estratégia 4: Baseada em padrão de horário
    melhor_horario = None
    melhor_prob = 0
    for horario, dados_hora in horario_stats.items():
        if dados_hora['total_jogos'] >= 3:
            prob = calcular_probabilidade(dados_hora['ambas_marcam'])
            if prob > melhor_prob:
                melhor_prob = prob
                melhor_horario = horario
    
    if melhor_horario and melhor_prob > 60:
        estrategias.append(("🎯 ESTRATÉGIA 4: Aposta por Horário", 
                          f"Melhor horário: {melhor_horario} ({melhor_prob:.1f}%)", 
                          f"FOQUE em jogos no horário {melhor_horario}"))
    
    # Estratégia 5: Baseada em tendência
    if total_jogos >= 10:
        if tendencia_ambas > 10:
            estrategias.append(("🎯 ESTRATÉGIA 5: Seguir Tendência", 
                              f"Tendência forte ascendente ({tendencia_ambas:+.1f}%)", 
                              "APOSTE na CONTINUAÇÃO da tendência de Ambas Marcam"))
        elif tendencia_over > 10:
            estrategias.append(("🎯 ESTRATÉGIA 5: Seguir Tendência", 
                              f"Tendência forte ascendente ({tendencia_over:+.1f}%)", 
                              "APOSTE na CONTINUAÇÃO da tendência de Over 2.5"))
    
    # Exibe estratégias
    if estrategias:
        print("\n🏆 MELHORES ESTRATÉGIAS DETECTADAS:")
        for i, (titulo, info, acao) in enumerate(estrategias, 1):
            print(f"\n{i}. {titulo}")
            print(f"   📊 {info}")
            print(f"   💰 {acao}")
    else:
        print("\n⚠️  Nenhuma estratégia clara detectada.")
        print("   Analise as odds atuais para encontrar valor.")
    
    # ============================================================================
    # ⚠️ ALERTAS E RISCOS
    # ============================================================================
    
    print("\n" + "="*80)
    print("⚠️  ALERTAS E RISCOS DETECTADOS:")
    print("="*80)
    
    alertas = []
    
    if media_gols < 1.0:
        alertas.append("❌ MÉDIA DE GOLS MUITO BAIXA - Risco de jogos sem gols")
    
    if desvio_gols > 2.0:
        alertas.append("⚠️  ALTA VOLATILIDADE - Resultados imprevisíveis")
    
    if stats['clean_sheets_casa'] / total_jogos > 0.5:
        alertas.append("⚠️  MUITOS CLEAN SHEETS em casa - Cuidado com Ambas Marcam")
    
    if len(set(stats['placares'])) > total_jogos * 0.8:
        alertas.append("⚠️  MUITA VARIEDADE DE PLACARES - Padrão difícil de detectar")
    
    if alertas:
        for alerta in alertas:
            print(f"   • {alerta}")
    else:
        print("   ✅ Nenhum risco significativo detectado")
    
    # ============================================================================
    # 📝 RESUMO FINAL E RECOMENDAÇÃO
    # ============================================================================
    
    print("\n" + "="*80)
    print("📋 RESUMO FINAL E RECOMENDAÇÃO PRINCIPAL:")
    print("="*80)
    
    # Determina a melhor aposta baseada em múltiplos fatores
    fatores_ambas = [
        prob_ambas,
        stats_segunda['prob_ambas'] if total_jogos >= 10 else prob_ambas,
        melhor_prob if melhor_horario else prob_ambas
    ]
    
    fatores_over = [
        prob_over25,
        stats_segunda['prob_over25'] if total_jogos >= 10 else prob_over25
    ]
    
    media_fator_ambas = sum(fatores_ambas) / len(fatores_ambas)
    media_fator_over = sum(fatores_over) / len(fatores_over)
    
    print(f"\n📊 ANÁLISE CONSIDERANDO TODOS OS FATORES:")
    print(f"   • Ambas Marcam (ponderado): {media_fator_ambas:.1f}%")
    print(f"   • Over 2.5 (ponderado):     {media_fator_over:.1f}%")
    
    # Recomendação final
    print(f"\n🎯 RECOMENDAÇÃO FINAL:")
    
    if media_fator_ambas > 55 and media_fator_ambas > media_fator_over:
        print(f"   🏆 APOSTE EM: AMBAS MARCAM - SIM")
        print(f"   📈 Confiança: {(media_fator_ambas/100*90):.0f}%")
        print(f"   💡 Motivo: Alta probabilidade em múltiplas análises")
    
    elif media_fator_over > 55 and media_fator_over > media_fator_ambas:
        print(f"   🏆 APOSTE EM: OVER 2.5 - SIM")
        print(f"   📈 Confiança: {(media_fator_over/100*90):.0f}%")
        print(f"   💡 Motivo: Alta probabilidade em múltiplas análises")
    
    elif media_fator_ambas < 35:
        print(f"   🏆 APOSTE EM: AMBAS MARCAM - NÃO")
        print(f"   📈 Confiança: {((100-media_fator_ambas)/100*90):.0f}%")
        print(f"   💡 Motivo: Baixa probabilidade histórica")
    
    elif media_fator_over < 35:
        print(f"   🏆 APOSTE EM: UNDER 2.5 - SIM")
        print(f"   📈 Confiança: {((100-media_fator_over)/100*90):.0f}%")
        print(f"   💡 Motivo: Baixa probabilidade histórica")
    
    else:
        print(f"   ⚖️  NENHUMA APOSTA CLARA RECOMENDADA")
        print(f"   💡 Sugestão: Analise as odds específicas do próximo jogo")
    
    print("\n" + "="*80)
    print("✅ ANÁLISE AVANÇADA CONCLUÍDA!")
    print("="*80)
    
    # Retorna estatísticas para uso futuro
    return {
        'prob_ambas': prob_ambas,
        'prob_over25': prob_over25,
        'media_gols': media_gols,
        'estrategias': estrategias,
        'recomendacao': "Ambas SIM" if media_fator_ambas > 55 else 
                       "Over 2.5 SIM" if media_fator_over > 55 else 
                       "Ambas NÃO" if media_fator_ambas < 35 else 
                       "Under 2.5" if media_fator_over < 35 else 
                       "Neutro"
    }

def calcular_probabilidade(contagem):
    """Calcula probabilidade a partir de contagem sim/não"""
    total = contagem['sim'] + contagem['nao']
    if total > 0:
        return (contagem['sim'] / total) * 100
    return 0

def analisar_conjunto_jogos(jogos):
    """Analisa um conjunto específico de jogos"""
    stats = {
        'ambas_marcam': {'sim': 0, 'nao': 0},
        'over_2.5': {'sim': 0, 'nao': 0},
        'total_gols': 0,
        'total_jogos': len(jogos)
    }
    
    for jogo in jogos:
        try:
            resultado = jogo.get('resultado', '0-0')
            if '-' in resultado:
                gols_a, gols_b = map(int, resultado.split('-'))
                total = gols_a + gols_b
                
                stats['total_gols'] += total
                
                if gols_a > 0 and gols_b > 0:
                    stats['ambas_marcam']['sim'] += 1
                else:
                    stats['ambas_marcam']['nao'] += 1
                
                if total > 2.5:
                    stats['over_2.5']['sim'] += 1
                else:
                    stats['over_2.5']['nao'] += 1
        except:
            continue
    
    return {
        'prob_ambas': calcular_probabilidade(stats['ambas_marcam']),
        'prob_over25': calcular_probabilidade(stats['over_2.5']),
        'media_gols': stats['total_gols'] / stats['total_jogos'] if stats['total_jogos'] > 0 else 0
    }

# ============================================================================
# 📋 MENU INTERATIVO ATUALIZADO
# ============================================================================

def menu_interativo():
    """Menu interativo principal"""
    dados_atual = None
    
    while True:
        print("\n" + "="*70)
        print("🎲 ANALISADOR AVANÇADO - FUTEBOL VIRTUAL BET365")
        print("="*70)
        
        if dados_atual:
            print(f"📊 Dados atuais: {dados_atual.get('returned_matchs', 0)} jogos da liga '{dados_atual.get('league', 'N/A')}'")
            print("-"*70)
        
        print("\n📋 MENU PRINCIPAL:")
        print("1. 🔍 Buscar novos dados da API")
        print("2. 📊 Ver odds principais dos dados atuais")
        print("3. 📈 Ver todas as odds dos dados atuais")
        print("4. 💾 Salvar dados atuais em JSON")
        print("5. 🔮 Análise RÁPIDA de tendências")
        print("6. 🎯 Análise AVANÇADA (aumentar probabilidade)")
        print("7. 🚪 Sair")
        
        escolha = input("\n🔢 Escolha uma opção (1-7): ").strip()
        
        if escolha == "1":
            liga = input("\n🔍 Qual liga? (copa/premier/euro/super/express): ").strip().lower() or "copa"
            quantidade = input("📊 Quantos jogos? (1-1500, padrão: 20): ").strip()
            quantidade = int(quantidade) if quantidade.isdigit() and 1 <= int(quantidade) <= 1500 else 20
            
            print(f"\n⏳ Buscando {quantidade} jogo(s) da liga '{liga}'...")
            dados_atual = obter_dados_com_odds(liga=liga, quantidade=quantidade)
            input("\n⏎ Pressione Enter para continuar...")
        
        elif escolha == "2":
            if dados_atual:
                mostrar_odds_principais(dados_atual)
            else:
                print("❌ Nenhum dado disponível. Busque dados primeiro.")
            input("\n⏎ Pressione Enter para continuar...")
        
        elif escolha == "3":
            if dados_atual:
                limite = input("Quantas odds por jogo mostrar? (padrão: 20): ").strip()
                limite = int(limite) if limite.isdigit() and int(limite) > 0 else 20
                mostrar_todas_odds(dados_atual, limite)
            else:
                print("❌ Nenhum dado disponível.")
            input("\n⏎ Pressione Enter para continuar...")
        
        elif escolha == "4":
            if dados_atual:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"odds_detalhadas_{timestamp}.json"
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(dados_atual, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Salvo em: '{nome_arquivo}'")
            else:
                print("❌ Nenhum dado para salvar.")
            input("\n⏎ Pressione Enter para continuar...")
        
        elif escolha == "5":
            if dados_atual:
                # Análise rápida simples
                analise_rapida(dados_atual)
            else:
                print("❌ Nenhum dado disponível.")
            input("\n⏎ Pressione Enter para continuar...")
        
        elif escolha == "6":
            print("\n" + "="*70)
            print("🎯 ANÁLISE AVANÇADA PARA AUMENTAR PROBABILIDADE")
            print("="*70)
            print("1. Analisar dados atuais da API")
            print("2. Analisar arquivo JSON específico")
            print("3. Analisar arquivo JSON mais recente")
            
            sub_escolha = input("\n🔢 Escolha (1-3, padrão: 1): ").strip() or "1"
            
            if sub_escolha == "1":
                if dados_atual:
                    resultado = analise_avançada_tendencias(dados_diretos=dados_atual)
                    # Oferece salvar análise
                    salvar = input("\n💾 Salvar esta análise em arquivo? (s/n): ").strip().lower()
                    if salvar == 's':
                        salvar_analise(resultado, dados_atual.get('league', 'desconhecida'))
                else:
                    print("❌ Nenhum dado disponível.")
            
            elif sub_escolha == "2":
                arquivo = input("Nome do arquivo JSON: ").strip()
                if arquivo and os.path.exists(arquivo):
                    analise_avançada_tendencias(file_path=arquivo)
                else:
                    print("❌ Arquivo não encontrado.")
            
            elif sub_escolha == "3":
                arquivos_json = glob.glob("odds_detalhadas_*.json")
                if arquivos_json:
                    arquivo_mais_recente = max(arquivos_json, key=os.path.getctime)
                    analise_avançada_tendencias(file_path=arquivo_mais_recente)
                else:
                    print("❌ Nenhum arquivo JSON encontrado.")
            
            input("\n⏎ Pressione Enter para continuar...")
        
        elif escolha == "7":
            print("\n👋 Até mais! Boas apostas! 🎯")
            break
        
        else:
            print("❌ Opção inválida.")

def analise_rapida(dados):
    """Análise rápida simplificada"""
    if not dados or "matchs" not in dados:
        return
    
    jogos = dados["matchs"]
    total_jogos = len(jogos)
    
    ambas_sim = 0
    over25_sim = 0
    
    for jogo in jogos:
        resultado = jogo.get('resultado', '0-0')
        if '-' in resultado:
            gols_a, gols_b = map(int, resultado.split('-'))
            if gols_a > 0 and gols_b > 0:
                ambas_sim += 1
            if (gols_a + gols_b) > 2.5:
                over25_sim += 1
    
    prob_ambas = (ambas_sim / total_jogos * 100) if total_jogos > 0 else 0
    prob_over = (over25_sim / total_jogos * 100) if total_jogos > 0 else 0
    
    print(f"\n📊 ANÁLISE RÁPIDA ({total_jogos} jogos):")
    print(f"   • Ambas Marcam: {prob_ambas:.1f}%")
    print(f"   • Over 2.5: {prob_over:.1f}%")
    
    if prob_ambas > 55:
        print("   💡 SUGESTÃO: Apostar em Ambas Marcam - SIM")
    elif prob_ambas < 35:
        print("   💡 SUGESTÃO: Apostar em Ambas Marcam - NÃO")
    
    if prob_over > 55:
        print("   💡 SUGESTÃO: Apostar em Over 2.5 - SIM")
    elif prob_over < 35:
        print("   💡 SUGESTÃO: Apostar em Under 2.5 - SIM")

def salvar_analise(resultado, liga):
    """Salva a análise em arquivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"analise_avancada_{liga}_{timestamp}.txt"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"ANÁLISE AVANÇADA - Liga: {liga}\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*80 + "\n")
        f.write(f"Probabilidade Ambas Marcam: {resultado.get('prob_ambas', 0):.1f}%\n")
        f.write(f"Probabilidade Over 2.5: {resultado.get('prob_over25', 0):.1f}%\n")
        f.write(f"Média de gols: {resultado.get('media_gols', 0):.2f}\n")
        f.write(f"Recomendação: {resultado.get('recomendacao', 'Neutro')}\n")
        f.write("\nEstratégias:\n")
        for estrategia in resultado.get('estrategias', []):
            f.write(f"- {estrategia[0]}: {estrategia[1]}\n")
    
    print(f"💾 Análise salva em: {nome_arquivo}")

# ============================================================================
# ▶️ EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🎯 ANALISADOR AVANÇADO DE ODDS - FUTEBOL VIRTUAL")
    print("="*70)
    
    menu_interativo()
    
    print("\n" + "="*70)
    print("✅ Programa encerrado!")
    print("="*70)