import random
import itertools
from discord import app_commands, Interaction, Embed

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

    if not valid_members:
        await interaction.response.send_message("Non c'è nessuno da pingare (o tutti hanno 'zz' nel nome).", ephemeral=True)
        return

    numero = max(1, min(numero, len(valid_members)))

    chosen = random.sample(valid_members, numero)
    mentions = "🎯"+'\n🎯'.join(m.mention for m in chosen)

    await interaction.response.send_message(f"{mentions}", ephemeral=False)


# Funzione per registrare i comandi nel bot
def setup_commands(client):

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
