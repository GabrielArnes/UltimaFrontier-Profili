import random
import itertools
from discord import app_commands, Interaction, Embed
import discord
from utils import extra_bersagli


ID_APPROVATORE = 1379925458237264013  # Team Approvazione
ID_NUOVO_ARRIVATO = 1377232973190926467  # Nuovo arrivato
ID_CUSTODE = 1375834279694827541  # Custode

# Funzione helper: logica del comando bersaglio
async def bersaglio_logic(interaction: Interaction, numero: int):
    if not interaction.guild:
        await interaction.response.send_message("Questo comando funziona solo nei server.", ephemeral=True)
        return

    member = interaction.guild.get_member(interaction.user.id)
    if not member or not member.voice or not member.voice.channel:
        await interaction.response.send_message("Non sei in una chat vocale!", ephemeral=True)
        return

    voice_channel = member.voice.channel

    valid_members = [
        m for m in voice_channel.members
        if m != member and not m.display_name.lower().startswith("zz") and not m.bot
    ]

    # Aggiungi anche bersagli extra salvati dall'utente
    extra = list(extra_bersagli.get(interaction.user.id, set()))
    valid_targets = valid_members + extra

    if not valid_targets:
        await interaction.response.send_message("Non c'è nessuno da pingare (o la tua lista è vuota).", ephemeral=True)
        return

    numero = max(1, min(numero, len(valid_targets)))

    chosen = random.sample(valid_targets, numero)

    mentions = []
    for c in chosen:
        if isinstance(c, discord.Member):
            mentions.append(c.mention)
        else:
            mentions.append(str(c))

    result = "🎯 " + "\n🎯 ".join(mentions)
    await interaction.response.send_message(f"{result}", ephemeral=False)

async def bersagliox_logic(interaction: Interaction, numero: int, da_escludere: discord.Member):
    if not interaction.guild:
        await interaction.response.send_message("Questo comando funziona solo nei server.", ephemeral=True)
        return

    member = interaction.guild.get_member(interaction.user.id)
    if not member or not member.voice or not member.voice.channel:
        await interaction.response.send_message("Non sei in una chat vocale!", ephemeral=True)
        return

    voice_channel = member.voice.channel

    valid_members = [
        m for m in voice_channel.members
        if m != member and m != da_escludere and not m.display_name.lower().startswith("zz") and not m.bot
    ]

    # Aggiungi anche bersagli extra salvati dall'utente
    extra = list(extra_bersagli.get(interaction.user.id, set()))
    valid_targets = valid_members + extra

    if not valid_targets:
        await interaction.response.send_message("Non c'è nessuno da pingare (o la tua lista è vuota).", ephemeral=True)
        return

    numero = max(1, min(numero, len(valid_targets)))

    chosen = random.sample(valid_targets, numero)

    mentions = []
    for c in chosen:
        if isinstance(c, discord.Member):
            mentions.append(c.mention)
        else:
            mentions.append(str(c))

    result = "🎯 " + "\n🎯 ".join(mentions)
    await interaction.response.send_message(f"{result}", ephemeral=False)


# Funzione per registrare i comandi nel bot
def setup_commands(client):

# FARE ZENIT
    @client.tree.command(name="fare_zenit", description="Tira 2d8 e calcola lo Zenit guadagnato in base al livello.")
    @app_commands.describe(livello="Il livello del personaggio")
    async def fare_zenit(interaction: Interaction, livello: int):
        import random
        if livello < 1:
            await interaction.response.send_message("❌ Il livello deve essere almeno 1.", ephemeral=True)
            return

        # Tiro dei dadi
        dado1 = random.randint(1, 8)
        dado2 = random.randint(1, 8)
        somma = dado1 + dado2

        # Calcolo base
        base_zenit = somma * 5 * livello
        risultato = base_zenit
        tipo_esito = "Normale"

        # Fallimento critico → doppio 1
        if dado1 == 1 and dado2 == 1:
            risultato = 0
            tipo_esito = "💀 Fallimento Critico"

        # Successo critico → doppio 6, 7 o 8
        elif (dado1 == dado2) and (dado1 in [6, 7, 8]):
            risultato *= 2
            tipo_esito = "🌟 Successo Critico"

        # Embed di risposta
        embed = Embed(
            title="🎲 Risultato Fare Zenit",
            color=discord.Color.gold()
        )
        embed.add_field(name="Tiri", value=f"{dado1} e {dado2}", inline=True)
        embed.add_field(name="Somma", value=str(somma), inline=True)
        embed.add_field(name="Esito", value=tipo_esito, inline=False)
        embed.add_field(name="Zenit Guadagnati", value=f"💰 {risultato}", inline=False)
        embed.set_footer(text=f"Livello personaggio: {livello}")

        await interaction.response.send_message(embed=embed)

# Bersaglio e ALIAS

    @client.tree.command(name="bersaglio", description="Ping casuale di persone nella tua voice chat (escludendo chi ha zz)")
    @app_commands.describe(numero="Quante persone vuoi pingare?")
    async def bersaglio(interaction: Interaction, numero: int = 1):
        await bersaglio_logic(interaction, numero)

    @client.tree.command(name="br", description="Alias per bersaglio")
    @app_commands.describe(numero="Quante persone vuoi pingare?")
    async def br(interaction: Interaction, numero: int = 1):
        await bersaglio_logic(interaction, numero)

    @client.tree.command(name="rt", description="Alias per bersaglio")
    @app_commands.describe(numero="Quante persone vuoi pingare?")
    async def rt(interaction: Interaction, numero: int = 1):
        await bersaglio_logic(interaction, numero)

# Bersaglio con Esclusione

    @client.tree.command(name="bersagliox", description="Ping casuale nella voice chat, escludendo anche un utente taggato")
    @app_commands.describe(da_escludere="Chi vuoi escludere oltre te stesso")
    @app_commands.describe(numero="(Opzionale) Quante persone vuoi pingare?")
    async def bersagliox(interaction: Interaction, da_escludere: discord.Member, numero: int = 1):
        await bersagliox_logic(interaction, numero, da_escludere)
    
    @client.tree.command(name="brx", description="Alias per bersagliox")
    @app_commands.describe(da_escludere="Chi vuoi escludere oltre te stesso")
    @app_commands.describe(numero="(Opzionale) Quante persone vuoi pingare?")
    async def brx(interaction: Interaction, da_escludere: discord.Member, numero: int = 1):
        await bersagliox_logic(interaction, numero, da_escludere)
    
    @client.tree.command(name="rtx", description="Alias per bersagliox")
    @app_commands.describe(da_escludere="Chi vuoi escludere oltre te stesso")
    @app_commands.describe(numero="(Opzionale) Quante persone vuoi pingare?")
    async def rtx(interaction: Interaction, da_escludere: discord.Member, numero: int = 1):
        await bersagliox_logic(interaction, numero, da_escludere)

# Nuovo comando: aggiungere bersagli extra
    @client.tree.command(name="bersaglio_aggiungi", description="Aggiungi un nome o utente alla tua lista di bersagli extra")
    async def bersaglio_aggiungi(interaction: Interaction, bersaglio: str):
        user_id = interaction.user.id
        if user_id not in extra_bersagli:
            extra_bersagli[user_id] = set()
        extra_bersagli[user_id].add(bersaglio)

        await interaction.response.send_message(f"Aggiunto **{bersaglio}** alla tua lista di bersagli extra.", ephemeral=True)

# Nuovo comando: rimuovere bersagli extra
    @client.tree.command(name="bersaglio_rimuovi", description="Rimuovi un nome o utente dalla tua lista di bersagli extra")
    async def bersaglio_rimuovi(interaction: Interaction, bersaglio: str):
        user_id = interaction.user.id
        if user_id in extra_bersagli and bersaglio in extra_bersagli[user_id]:
            extra_bersagli[user_id].remove(bersaglio)
            # Se la lista diventa vuota, rimuoviamo l'entry per pulizia
            if not extra_bersagli[user_id]:
                del extra_bersagli[user_id]
            await interaction.response.send_message(f"Rimosso **{bersaglio}** dalla tua lista di bersagli extra.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ **{bersaglio}** non era presente nella tua lista di bersagli extra.", ephemeral=True)

# MOSTRA LISTA BERSAGLI EXTRA

    @client.tree.command(name="bersaglio_status", description="Mostra la tua lista di bersagli extra.")
    async def bersaglio_status(interaction: Interaction):
        user_id = interaction.user.id
        bersagli = extra_bersagli.get(user_id, set())

        if not bersagli:
            await interaction.response.send_message("ℹ️ La tua lista di bersagli extra è vuota.", ephemeral=True)
        else:
            lista = "\n".join(f"• {b}" for b in bersagli)
            await interaction.response.send_message(
                f"I tuoi bersagli extra attuali:\n{lista}",
                ephemeral=True
            )

# ALCHIMIA
    @client.tree.command(name="alchimia", description="Tira da 2 a 4 d20 e mostra tutti gli effetti unici delle coppie.")
    @app_commands.describe(num_dice="Numero di d20 da tirare (tra 2 e 4)")
    async def alchimia(interaction: Interaction, num_dice: int = 2):
        if not (2 <= num_dice <= 4):
            await interaction.response.send_message("Puoi tirare solo tra 2 e 4 dadi.", ephemeral=True)
            return

        # Tabelle di riferimento
        target_table = [
            (1, 6, "di te oppure un alleato a te visibile presente nella scena"),
            (7, 11, "un nemico a te visibile presente nella scena"),
            (12, 16, "di te e ciascun alleato presente nella scena"),
            (17, 20, "ciascun nemico presente nella scena")
        ]

        effect_table = {
            1: "considera i suoi dadi di Destrezza e Vigore incrementati di una taglia (massimo d12) fino al termine del tuo prossimo turno.",
            2: "considera i suoi dadi di Intuito e Volontà incrementati di una taglia (massimo d12) fino al termine del tuo prossimo turno.",
            3: "subisce 20 danni da aria. Questo ammontare aumenta a 30 se sei di livello 20 o superiore, oppure 40 se sei di livello 40 o superiore.",
            4: "subisce 20 danni da fulmine. Questo ammontare aumenta a 30 se sei di livello 20 o superiore, oppure 40 se sei di livello 40 o superiore.",
            5: "subisce 20 danni da ombra. Questo ammontare aumenta a 30 se sei di livello 20 o superiore, oppure 40 se sei di livello 40 o superiore.",
            6: "subisce 20 danni da terra. Questo ammontare aumenta a 30 se sei di livello 20 o superiore, oppure 40 se sei di livello 40 o superiore.",
            7: "subisce 20 danni da fuoco. Questo ammontare aumenta a 30 se sei di livello 20 o superiore, oppure 40 se sei di livello 40 o superiore.",
            8: "subisce 20 danni da ghiaccio. Questo ammontare aumenta a 30 se sei di livello 20 o superiore, oppure 40 se sei di livello 40 o superiore.",
            9: "ottiene Resistenza ai danni da aria e fuoco fino al termine della scena.",
            10: "ottiene Resistenza ai danni da fulmine e ghiaccio fino al termine della scena.",
            11: "ottiene Resistenza ai danni da ombra e terra fino al termine della scena.",
            12: "subisce lo status furente.",
            13: "subisce lo status avvelenato.",
            14: "subisce gli status confuso, debole, lento e scosso.",
            15: "guarisce da tutti gli status.",
            16: "recupera 50 Punti Vita e 50 Punti Mente.",
            17: "recupera 50 Punti Vita e 50 Punti Mente.",
            18: "recupera 100 Punti Vita.",
            19: "recupera 100 Punti Mente.",
            20: "recupera 100 Punti Vita e 100 Punti Mente."
        }

        rolls = [random.randint(1, 20) for _ in range(num_dice)]

        seen_pairs = set()
        unique_pairs = []

        for a, b in itertools.permutations(rolls, 2):
            pair_key = (a, b)
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                unique_pairs.append((a, b))

        from collections import defaultdict
        target_effects = defaultdict(set)

        for target, effect in unique_pairs:
            target_effects[target].add(effect)

        embed = Embed(
            title="Risultati della Pozione",
            description=f"🎲 Tiri effettuati: {', '.join(str(r) for r in rolls)}",
            color=0x800080
        )

        for target in sorted(target_effects.keys()):
            effects = sorted(target_effects[target])
            target_text = next((text for (low, high, text) in target_table if low <= target <= high), "qualcosa di misterioso")

            description_lines = []
            for effect in effects:
                effect_text = effect_table.get(effect, "subisce un effetto sconosciuto.")
                description_lines.append(f"- {effect_text}")

            full_text = (
                f"La pozione ha effetto su **{target_text}**.\n"
                f"Ciascuna creatura affetta dalla pozione:\n" +
                "\n".join(description_lines)
            )

            embed.add_field(name=f"🎯 Target {target}", value=full_text, inline=False)

        await interaction.response.send_message(embed=embed)

# DELIZIA (Gourmet)
    @client.tree.command(name="delizia", description="Tira da 1 a 4 d12 e ottieni effetti speciali dolci o tremendi.")
    @app_commands.describe(num_dice="Numero di d12 da tirare (tra 1 e 4)")
    async def delizia(interaction: Interaction, num_dice: int = 1):
        if not (1 <= num_dice <= 4):
            await interaction.response.send_message("Puoi tirare solo tra 1 e 4 dadi.", ephemeral=True)
            return

        delizia_effects = {
            1: "Ciascun bersaglio di questa delizia guarisce dallo status (scegliere uno tra: **avvelenato**, **confuso**, **debole**, **furente**, **lento**, **scosso**).",
            2: "Ciascun bersaglio di questa delizia subisce lo status (scegliere uno tra: **confuso**, **debole**, **lento**, **scosso**).",
            3: "Ciascun bersaglio di questa delizia recupera **40 Punti Vita**. Questo ammontare aumenta a **50** se sei di livello 30 o superiore.",
            4: "Ciascun bersaglio di questa delizia recupera **40 Punti Mente**. Questo ammontare aumenta a **50** se sei di livello 30 o superiore.",
            5: "Ciascun bersaglio di questa delizia subisce **20 danni** da (scegliere uno tra: **aria**, **fulmine**, **fuoco**, **ghiaccio**, **terra**, **veleno**). Questo ammontare aumenta a **30** se sei di livello 30 o superiore.",
            6: "Fino al termine del tuo prossimo turno, tutte le fonti che infliggono danno da (scegliere uno tra: **aria**, **fulmine**, **fuoco**, **ghiaccio**, **terra**, **veleno**) infliggono **5 danni extra** a ciascun bersaglio di questa delizia (prima delle affinità).",
            7: "Ciascun bersaglio di questa delizia **non può eseguire l’azione di Abilità** durante il suo prossimo turno.",
            8: "Ciascun bersaglio di questa delizia **non può eseguire l’azione di Guardia** durante il suo prossimo turno.",
            9: "Ciascun bersaglio di questa delizia **non può eseguire l’azione di Incantesimo** durante il suo prossimo turno.",
            10: "Ciascun bersaglio di questa delizia ottiene **Resistenza al danno** da (scegliere uno tra: **aria**, **fulmine**, **fuoco**, **ghiaccio**, **terra**, **veleno**) fino al termine del tuo prossimo turno.",
            11: "Ciascun bersaglio di questa delizia considera il suo (scegliere uno tra: **Destrezza**, **Intuito**, **Vigore**, **Volontà**) come incrementato di una taglia di dado (massimo d12) fino al termine del tuo prossimo turno.",
            12: "Durante il prossimo turno di ciascun bersaglio di questa delizia, tutto il danno che infligge diventa di tipo (scegliere uno tra: **aria**, **fulmine**, **fuoco**, **ghiaccio**, **terra**, **veleno**) e non può cambiare tipo."
        }

        NON_ESPANDIBILI = {3, 4, 7, 8, 9}
        results = []

        while len(results) < num_dice:
            roll = random.randint(1, 12)
            
            # Se il numero è già stato tirato
            if roll in results:
                # Controlliamo se **entrambi** sono tra i non espandibili
                if roll in NON_ESPANDIBILI:
                    # Quanti roll identici abbiamo già?
                    count = results.count(roll)
                    # Se ce n'è già almeno uno, e *entrambi* sono da NON ripetere
                    if count >= 1:
                        continue  # salta e ritira
            results.append(roll)

        results.sort()

        embed = Embed(
            title="🍭 Effetti della Delizia",
            description=f"🎲 Tiri effettuati: {', '.join(str(r) for r in results)}",
            color=0xFF00FF
        )

        for r in results:
            effect_text = delizia_effects.get(r, "effetto misterioso...")
            embed.add_field(name=f"Effetto {r}", value=effect_text, inline=False)

        await interaction.response.send_message(embed=embed)


    def crea_embed_opportunita_compatta():
        embed = Embed(
            title="Tabella Opportunità",
            color=0x0000FF
        )

        colonne_1 = [
            ("Afflizione", "Una creatura subisce uno status tra **confuso, debole, lento** e **scosso**."),
            ("Colpo di Scena", "Qualcuno o qualcosa a tua scelta appare all’improvviso in scena."),
            ("Favore", "Con le tue azioni guadagni l’appoggio o l’ammirazione di qualcuno."),
            ("Informazione", "Noti un indizio o dettaglio utile. Il Game Master può spiegarti di cosa si tratta o chiederti di inventarlo."),
            ("Legame", "Stringi un Legame con qualcuno o qualcosa, oppure aggiungi un sentimento a un Legame già esistente."),
            ("Oggetto Perso", "Un oggetto viene distrutto, perso, rubato o abbandonato.")
        ]

        colonne_2 = [
            ("Passo Falso", "Scegli una creatura in scena, che finisce per fare un’affermazione compromettente decisa da chi la controlla.."),
            ("Progresso", "Puoi riempire o svuotare 2 sezioni di un Orologio."),
            ("Rivelazione", "Scopri obiettivi e motivazioni di una creatura a scelta."),
            ("Scansione", "Scopri una Vulnerabilità o un Tratto di una creatura a te visibile."),
            ("Vantaggio", "Il prossimo Test effettuato da te o un tuo alleato riceve un bonus di +4."),
            ("Altro", "Qualcosa fuori dalle opzioni precedenti, che il GM reputa adatta.")
        ]

        for i in range(len(colonne_1)):
            nome1, desc1 = colonne_1[i]
            nome2, desc2 = colonne_2[i]
            embed.add_field(name=nome1, value=desc1, inline=True)
            embed.add_field(name=nome2, value=desc2, inline=True)

        return embed


    @client.tree.command(name="opportunità", description="Mostra la tabella Opportunità")
    async def opportunita(interaction: Interaction):
        embed = crea_embed_opportunita_compatta()
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @client.tree.command(name="opp", description="Alias per opportunità")
    async def opp(interaction: Interaction):
        embed = crea_embed_opportunita_compatta()
        await interaction.response.send_message(embed=embed, ephemeral=False)

# INFO SERVER

    def crea_embed_info():
        embed = Embed(
            title="📚 Link utili del server",
            description=(
                "[📖 Regolamento](https://docs.google.com/document/d/1TiqMb0bXczUmhdvSPWtp6MCw_U0ZDJ3z_EkFzEcYsIw/edit?tab=t.7es1uo54qojl#heading=h.9yali37idpb8)\n"
                "[🗺️ Ambientazione (Legendkeeper)](https://www.legendkeeper.com/app/cmbqao6g13mpw0zl9g53ghyet/b44zw30f/)\n"
                "[🎲 Press Start!](https://docs.google.com/document/d/1TiqMb0bXczUmhdvSPWtp6MCw_U0ZDJ3z_EkFzEcYsIw/edit?tab=t.y1x8fkqo1yqd#heading=h.noi3t77uckpr)\n"
                "[🧙 Formato Scheda](https://docs.google.com/spreadsheets/d/16UMPL6OBRfNQnZKIBfQQ1feLZ_sJtIWtqvjyatbE3xU/edit?gid=0#gid=0)\n"
                "[💬 Contatta lo staff!](https://discord.com/channels/1374015176554057728/1379788714812768266)\n"
            ),
            color=0x3498db
        )
        return embed
    
    @client.tree.command(name="info", description="Info del server")
    async def info(interaction: Interaction):
        embed = crea_embed_info()
        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @client.tree.command(name="server", description="Info del server")
    async def server(interaction: Interaction):
        embed = crea_embed_info()
        await interaction.response.send_message(embed=embed, ephemeral=False)

# APPROVA PERSONAGGIO

    @client.tree.command(
    name="approva",
    description="Approva un utente: rimuove 'Nuovo arrivato' e assegna 'Custode'."
    )
    @app_commands.describe(membro="L'utente che vuoi approvare")
    async def approva(interaction: discord.Interaction, membro: discord.Member):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Questo comando funziona solo nei server.", ephemeral=True)
            return

        # 🔹 Ruolo autorizzato per usare il comando
        approvatore_role = guild.get_role(ID_APPROVATORE)
        member_approvatore = guild.get_member(interaction.user.id)

        if not approvatore_role:
            await interaction.response.send_message(
                "⚠️ Ruolo 'Team Approvazione' non trovato sul server!", ephemeral=True
            )
            return

        if approvatore_role not in member_approvatore.roles:
            await interaction.response.send_message(
                "❌ Non hai il permesso di usare questo comando.", ephemeral=True
            )
            return

        # 🔹 Ruoli fissi da rimuovere/aggiungere
        ruolo_da_rimuovere = guild.get_role(ID_NUOVO_ARRIVATO)
        ruolo_da_aggiungere = guild.get_role(ID_CUSTODE)

        if not ruolo_da_rimuovere or not ruolo_da_aggiungere:
            await interaction.response.send_message(
                "⚠️ Ruoli 'Nuovo arrivato' o 'Custode' non trovati sul server!", ephemeral=True
            )
            return

        # 🔹 Rimuove ruolo se presente
        if ruolo_da_rimuovere in membro.roles:
            await membro.remove_roles(ruolo_da_rimuovere)

        # 🔹 Aggiunge ruolo nuovo
        await membro.add_roles(ruolo_da_aggiungere)

        # 🔹 Embed conferma
        embed = Embed(
            title="✅ Utente Approvato",
            description=f"{membro.mention} è stato approvato!",
            color=discord.Color.green()
        )
        embed.add_field(name="Rimosso", value=ruolo_da_rimuovere.mention, inline=True)
        embed.add_field(name="Assegnato", value=ruolo_da_aggiungere.mention, inline=True)
        embed.set_footer(text=f"Azione eseguita da {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)
    
# RITUALI
    def crea_embed_rituali():
        embed = Embed(
            title="📜 Tabella Rituali",
            color=0x9932CC
        )

        # Tabella Potenza: raggruppiamo due valori in uno stesso field
        embed.add_field(
            name="⚡ Potenza",
            value="",
            inline=False
        )

        embed.add_field(
            name="",
            value=(
                "**Minore**: 20 PM | LD 7\nCreare lampi, bloccare passaggi, rompere vetri.\n\n"
                "**Media**: 30 PM | LD 10\nIllusioni, curare malattie, trovare qualcosa, percepire emozioni."
            ),
            inline=True
        )
        embed.add_field(
            name="",
            value=(
                "**Maggiore**: 40 PM | LD 13\nLeggere pensieri, spezzare maledizioni, alterare clima.\n\n"
                "**Estrema**: 50 PM | LD 16\nIndebolire divinità, prevenire catastrofi, modificare luoghi/creature."
            ),
            inline=True
        )

        # Tabella Area: stesso trucco
        embed.add_field(
            name="💠 Area",
            value="",
            inline=False
        )

        embed.add_field(
            name="",
            value=(
                "**Individuale** ×1: Una creatura, una porta, un albero, un’arma.\n\n"
                "**Piccola** ×2: Gruppo di umani, creatura grande, stanza, capanna."
            ),
            inline=True
        )
        embed.add_field(
            name="",
            value=(
                "**Grande** ×3: Folla, piccola foresta, galeone, sala di castello, gigante.\n\n"
                "**Enorme** ×4: Fortezza, lago, montagna, villaggio, quartiere."
            ),
            inline=True
        )

        return embed


    @client.tree.command(name="rituali", description="Mostra la tabella dei rituali")
    async def rituali(interaction: Interaction):
        embed = crea_embed_rituali()
        await interaction.response.send_message(embed=embed, ephemeral=False)

    
