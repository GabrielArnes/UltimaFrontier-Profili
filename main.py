import discord
from discord import app_commands
import random
import json
import os
from dotenv import load_dotenv



intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True  # Necessario per accedere ai membri in voice chat

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

#Bersaglio

# Funzione helper: logica del comando, NON decorata
async def bersaglio_logic(interaction: discord.Interaction, numero: int):
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

# Comando /bersaglio
@client.tree.command(name="bersaglio", description="Ping casuale di persone nella tua voice chat (escludendo chi ha zz)")
@app_commands.describe(numero="Quante persone vuoi pingare?")
async def bersaglio(interaction: discord.Interaction, numero: int = 1):
    await bersaglio_logic(interaction, numero)

# Comando /br (alias)
@client.tree.command(name="br", description="Alias per bersaglio")
@app_commands.describe(numero="Quante persone vuoi pingare?")
async def br(interaction: discord.Interaction, numero: int = 1):
    await bersaglio_logic(interaction, numero)

# Comando /rt (alias)
@client.tree.command(name="rt", description="Alias per bersaglio")
@app_commands.describe(numero="Quante persone vuoi pingare?")
async def rt(interaction: discord.Interaction, numero: int = 1):
    await bersaglio_logic(interaction, numero)


# Alchimia

@client.tree.command(name="alchimia", description="Tira da 2 a 4 d20 e mostra tutti gli effetti unici delle coppie.")
@app_commands.describe(num_dice="Numero di d20 da tirare (tra 2 e 4)")
async def alchimia(interaction: discord.Interaction, num_dice: int = 2):
    import itertools
    import random
    from collections import defaultdict
    import discord

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

    # Tiri dei dadi
    rolls = [random.randint(1, 20) for _ in range(num_dice)]

    # Crea set per escludere duplicati (coppie identiche con ordine invertito)
    seen_pairs = set()
    unique_pairs = []

    for a, b in itertools.permutations(rolls, 2):
        pair_key = (a, b)
        if pair_key not in seen_pairs:
            seen_pairs.add(pair_key)
            unique_pairs.append((a, b))

    # Raggruppa effetti per target
    from collections import defaultdict
    target_effects = defaultdict(set)  # target → set di effetti

    for target, effect in unique_pairs:
        target_effects[target].add(effect)

    # Crea Embed
    embed = discord.Embed(
        title="Risultati della Pozione",
        description=f"🎲 Tiri effettuati: {', '.join(str(r) for r in rolls)}",
        color=discord.Color.purple()
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

# Delizie

@client.tree.command(name="delizia", description="Tira da 1 a 4 d12 e ottieni effetti speciali dolci o tremendi.")
@app_commands.describe(num_dice="Numero di d12 da tirare (tra 1 e 4)")
async def delizia(interaction: discord.Interaction, num_dice: int = 1):
    import random

    if not (1 <= num_dice <= 4):
        await interaction.response.send_message("Puoi tirare solo tra 1 e 4 dadi.", ephemeral=True)
        return

    # Tabella degli effetti di "delizia"
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

    # Tira d12 senza duplicati
    results = set()
    while len(results) < num_dice:
        results.add(random.randint(1, 12))

    results = sorted(results)

    # Crea Embed
    embed = discord.Embed(
        title="🍭 Effetti della Delizia",
        description=f"🎲 Tiri effettuati: {', '.join(str(r) for r in results)}",
        color=discord.Color.magenta()
    )

    for r in results:
        effect_text = delizia_effects.get(r, "effetto misterioso...")
        embed.add_field(name=f"Effetto {r}", value=effect_text, inline=False)

    await interaction.response.send_message(embed=embed)


# Opportunità

def crea_embed_opportunita_compatta():
    embed = discord.Embed(
        title="Tabella Opportunità",
        color=discord.Color.blue()
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

    # Aggiungi i campi a due colonne
    for i in range(len(colonne_1)):
        nome1, desc1 = colonne_1[i]
        nome2, desc2 = colonne_2[i]
        embed.add_field(name=nome1, value=desc1, inline=True)
        embed.add_field(name=nome2, value=desc2, inline=True)

    return embed


@client.tree.command(name="opportunità", description="Mostra la tabella Opportunità")
async def opportunita(interaction: discord.Interaction):
    embed = crea_embed_opportunita_compatta()
    await interaction.response.send_message(embed=embed, ephemeral=False)

@client.tree.command(name="opp", description="Alias per opportunità")
async def opp(interaction: discord.Interaction):
    embed = crea_embed_opportunita_compatta()
    await interaction.response.send_message(embed=embed, ephemeral=False)


# PROFILI V0.1

import discord
from discord import app_commands,Embed, app_commands, Interaction
import os
import json
from discord.ui import View, Select, Button

LOG_CHANNEL_ID = 1380217123825123338  # metti qui l’ID canale dedicato

class ShowProfileView(View):
    def __init__(self, user: discord.User, profiles: dict):
        super().__init__(timeout=120)
        self.user = user
        self.profiles = profiles

        options = [
            discord.SelectOption(label=name, description="Clicca per visualizzare", value=name)
            for name in profiles.keys()
        ]

        self.add_item(ProfileSelect(user, profiles, options))


class ProfileSelect(Select):
    def __init__(self, user: discord.User, profiles: dict, options: list):
        super().__init__(placeholder="Scegli un profilo da mostrare...", options=options)
        self.user = user
        self.profiles = profiles

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Non puoi visualizzare i profili di un altro utente.", ephemeral=True)
            return

        profile_name = self.values[0]
        profile_data = self.profiles[profile_name]

        embed = self.create_embed(profile_name, profile_data)

        await interaction.response.send_message(
            embed=embed,
            view=PublishProfileView(self.user, profile_name, embed),
            ephemeral=True
        )

    def create_embed(self, profile_name: str, data: dict) -> discord.Embed:
        embed = discord.Embed(title=profile_name, color=discord.Color.blue())

        embed.set_image(url=data.get("immagine_url", ""))

        embed.add_field(name="Livello", value=data.get("livello", "-"), inline=True)
        embed.add_field(name="Identità", value=data.get("identità", "-"), inline=True)
        embed.add_field(name="Tema", value=data.get("tema", "-"), inline=True)

        embed.add_field(name="Origine", value=data.get("origine", "-"), inline=True)
        embed.add_field(name="Classi", value=data.get("classi", "-"), inline=True)
        embed.add_field(name="Abilità eroiche", value=data.get("abilità_eroiche", "-"), inline=True)

        embed.add_field(name="Descrizione fisica", value=data.get("descrizione_fisica", "-"), inline=False)
        embed.add_field(name="Link scheda", value=data.get("link_scheda", "-"), inline=False)

        return embed

class PublishProfileView(View):
    def __init__(self, user: discord.User, profile_name: str, embed: discord.Embed):
        super().__init__(timeout=None)
        self.user = user
        self.profile_name = profile_name
        self.embed = embed

    @discord.ui.button(label="📣 Pubblica", style=discord.ButtonStyle.primary)
    async def publish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Solo l'autore può pubblicare il profilo.", ephemeral=True)
            return

        sent_msg = await interaction.channel.send(
            f"{self.user.mention} ha pubblicato il profilo **{self.profile_name}**:",
            embed=self.embed,
            view=DeleteMessageView(self.user)
        )
        await interaction.response.send_message("Profilo pubblicato nel canale.", ephemeral=True)

class DeleteMessageView(View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="❌ Cancella messaggio", style=discord.ButtonStyle.danger)
    async def delete_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Solo l'autore può cancellare questo messaggio.", ephemeral=True)
            return

        try:
            await interaction.message.delete()
        except discord.NotFound:
            await interaction.response.send_message("Messaggio già cancellato.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Non ho i permessi per cancellare il messaggio.", ephemeral=True)
        else:
            self.stop()

# --- Classe View e Bottoni ---

class PGCreationView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=None)
        self.author = author
        self.data = {
            "pg_nome": None,
            "livello": None,
            "identità": None,
            "tema": None,
            "origine": None,
            "classi": None,
            "abilità_eroiche": None,
            "descrizione_fisica": None,
            "link_scheda": None,
            "immagine_url": None,
            "message_id": None  # per tenere traccia del messaggio nel canale dedicato
        }

    def get_embed(self) -> discord.Embed:
        nome_pg = self.data.get("pg_nome") or "Profilo senza nome"
        embed = discord.Embed(title=nome_pg, color=discord.Color.blue())
        embed.description = f"Creato da {self.author.mention}"

        inline_fields = [
            ("Livello", self.data.get("livello", "*Non specificato*")),
            ("Identità", self.data.get("identità", "*Non specificato*")),
            ("Tema", self.data.get("tema", "*Non specificato*")),
            ("Origine", self.data.get("origine", "*Non specificato*")),
            ("Classi", self.data.get("classi", "*Non specificato*")),
            ("Abilità Eroiche", self.data.get("abilità_eroiche", "*Non specificato*")),
        ]

        for name, value in inline_fields:
            embed.add_field(name=name, value=value, inline=True)

        embed.add_field(name="Descrizione Fisica", value=self.data.get("descrizione_fisica", "*Non specificato*"), inline=False)
        embed.add_field(name="Link Scheda", value=self.data.get("link_scheda", "*Non specificato*"), inline=False)

        immagine_url = self.data.get("immagine_url")
        if immagine_url:
            embed.set_image(url=immagine_url)

        return embed

    def setup_buttons(self):
        for key in self.data:
            if key == "message_id":
                continue  # non serve bottone per message_id
            self.add_item(ProfileFieldButton(key, self))
        self.add_item(SaveProfileButton(self))


class ProfileFieldButton(discord.ui.Button):
    def __init__(self, field_name: str, view_ref: PGCreationView):
        label_map = {
            "pg_nome": "Nome Personaggio",
            "livello": "Livello",
            "identità": "Identità",
            "tema": "Tema",
            "origine": "Origine",
            "classi": "Classi",
            "abilità_eroiche": "Abilità Eroiche",
            "descrizione_fisica": "Descrizione Fisica",
            "link_scheda": "Link Scheda",
            "immagine_url": "URL Immagine",
        }
        super().__init__(label=label_map.get(field_name, field_name), style=discord.ButtonStyle.secondary)
        self.field_name = field_name
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view_ref.author:
            await interaction.response.send_message("Non puoi modificare questo profilo.", ephemeral=True)
            return

        modal = FieldModal(self.field_name, self.view_ref)
        await interaction.response.send_modal(modal)


class FieldModal(discord.ui.Modal):
    def __init__(self, field_name: str, view_ref: PGCreationView):
        super().__init__(title=f"Imposta {field_name.replace('_', ' ').title()}")
        self.field_name = field_name
        self.view_ref = view_ref

        current_value = self.view_ref.data.get(field_name) or ""
        multiline_fields = {"descrizione_fisica", "link_scheda", "immagine_url", "abilità_eroiche"}

        self.input = discord.ui.TextInput(
            label=f"Inserisci {field_name.replace('_', ' ').title()}",
            default=current_value,
            required=False,
            style=discord.TextStyle.paragraph if field_name in multiline_fields else discord.TextStyle.short,
            max_length=500
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view_ref.data[self.field_name] = self.input.value.strip()
        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)


class SaveProfileButton(discord.ui.Button):
    def __init__(self, view_ref: PGCreationView):
        super().__init__(label="Salva", style=discord.ButtonStyle.success)
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view_ref.author:
            await interaction.response.send_message("Non puoi salvare questo profilo.", ephemeral=True)
            return

        saved_data = self.view_ref.data
        if not saved_data.get("pg_nome"):
            await interaction.response.send_message("⚠️ Inserisci almeno il nome del personaggio prima di salvare!", ephemeral=True)
            return

        filepath = "pg_profiles.json"
        all_profiles = {}
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                all_profiles = json.load(f)

        user_id_str = str(self.view_ref.author.id)
        pg_nome = saved_data["pg_nome"].strip()

        if user_id_str not in all_profiles:
            all_profiles[user_id_str] = {}

        # Cancella vecchio messaggio embed nel canale dedicato (se esiste)
        channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        old_msg_id = all_profiles.get(user_id_str, {}).get(pg_nome, {}).get("message_id")
        if channel and old_msg_id:
            try:
                old_msg = await channel.fetch_message(old_msg_id)
                await old_msg.delete()
            except Exception:
                pass  # se non riesce a cancellare, ignora

        # Salva dati aggiornati
        all_profiles[user_id_str][pg_nome] = saved_data

        # Invia nuovo embed nel canale dedicato e salva nuovo message_id
        embed = self.view_ref.get_embed()
        if channel:
            msg = await channel.send(embed=embed)
            all_profiles[user_id_str][pg_nome]['message_id'] = msg.id

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(all_profiles, f, ensure_ascii=False, indent=4)

        await interaction.response.edit_message(content=f"✅ Profilo **{pg_nome}** salvato con successo!", embed=None, view=None)



# --- Funzioni per caricare e salvare dati ---

DATA_FILE = 'pg_profiles.json'

def save_profiles(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Caricamento profili dal file JSON (funzione d'appoggio)
def load_profiles():
    try:
        with open("pg_profiles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# --- Comandi /pg ---


class PGCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="test", description="Gestisci i tuoi profili PG")

    @app_commands.command(name="crea", description="Crea un nuovo profilo PG")
    async def crea(self, interaction: discord.Interaction):
        view = PGCreationView(interaction.user)
        view.setup_buttons()
        await interaction.response.send_message(
            embed=view.get_embed(),
            view=view,
            ephemeral=True
        )


    @app_commands.command(name="modifica", description="Modifica un profilo PG esistente")
    async def modifica(self, interaction: discord.Interaction):
        filepath = "pg_profiles.json"
        if not os.path.exists(filepath):
            await interaction.response.send_message("Non ci sono profili salvati.", ephemeral=True)
            return

        with open(filepath, "r", encoding="utf-8") as f:
            all_profiles = json.load(f)

        user_id_str = str(interaction.user.id)
        if user_id_str not in all_profiles or not all_profiles[user_id_str]:
            await interaction.response.send_message("Non hai profili salvati da modificare.", ephemeral=True)
            return

        pg_names = list(all_profiles[user_id_str].keys())

        class ProfileSelect(discord.ui.Select):
            def __init__(self):
                options = [discord.SelectOption(label=name) for name in pg_names]
                super().__init__(placeholder="Seleziona il profilo da modificare", options=options, min_values=1, max_values=1)

            async def callback(self, select_interaction: discord.Interaction):
                pg_name = self.values[0]
                profile_data = all_profiles[user_id_str][pg_name]

                view = PGCreationView(interaction.user)
                view.data = profile_data
                view.setup_buttons()

                await select_interaction.response.edit_message(embed=view.get_embed(), view=view)

        view = discord.ui.View()
        view.add_item(ProfileSelect())

        await interaction.response.send_message("Seleziona il profilo da modificare:", view=view, ephemeral=True)

    @app_commands.command(name="lista", description="Vedi tutti i profili salvati (nome + immagine)")
    async def lista(self, interaction: discord.Interaction):
        profiles = load_profiles()  # {user_id: {nome_pg: profilo_dict}}
        embeds = []

        for user_id, profili_utente in profiles.items():
            for nome_pg, profilo in profili_utente.items():
                if not isinstance(profilo, dict):
                    continue  # Ignora dati malformati

                nome = profilo.get("pg_nome", nome_pg)
                immagine = profilo.get("immagine_url")

                embed = discord.Embed(title=nome)
                if immagine:
                    embed.set_image(url=immagine)

                embed.set_footer(text=f"Creato da <@{user_id}>")
                embeds.append(embed)

        if not embeds:
            await interaction.response.send_message(
                "Nessun profilo trovato.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            content="Ecco tutti i profili salvati:",
            embeds=embeds[:10],
            ephemeral=True
        )

        for i in range(10, len(embeds), 10):
            await interaction.followup.send(
                embeds=embeds[i:i+10],
                ephemeral=True
            )

   # /pg mostra
    @app_commands.command(name="mostra", description="Mostra uno dei tuoi profili PG")
    async def mostra(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        profiles = load_profiles().get(user_id)

        if not profiles:
            await interaction.response.send_message("Non hai ancora salvato nessun profilo.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Scegli un profilo da mostrare:",
            view=ShowProfileView(interaction.user, profiles),
            ephemeral=True
        )

    # /pg cancella
    @app_commands.command(name="cancella", description="Cancella uno dei tuoi profili")
    async def cancella(self, interaction: Interaction):
        profiles = load_profiles()
        user_id = str(interaction.user.id)
        user_profiles = profiles.get(user_id, {})

        if not user_profiles:
            await interaction.response.send_message("❌ Non hai profili da cancellare.", ephemeral=True)
            return

        # View e Select per scegliere quale profilo eliminare
        view = View(timeout=60)

        select = Select(
            placeholder="Scegli un profilo da cancellare",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=nome_pg, description="Seleziona per cancellare")
                for nome_pg in user_profiles.keys()
            ]
        )

        async def select_callback(select_interaction: Interaction):
            if select_interaction.user.id != interaction.user.id:
                await select_interaction.response.send_message("Non puoi interagire con questo menu.", ephemeral=True)
                return

            selected_name = select.values[0]
            selected_profile = user_profiles[selected_name]

            embed = Embed(title=selected_profile.get("pg_nome", selected_name))
            if selected_profile.get("immagine_url"):
                embed.set_image(url=selected_profile["immagine_url"])

            # Bottoni di conferma e annulla
            class ConfermaButton(Button):
                def __init__(self):
                    super().__init__(label="Conferma Cancellazione", style=discord.ButtonStyle.danger)

                async def callback(self, btn_interaction: Interaction):

                    del user_profiles[selected_name]
                    profiles[user_id] = user_profiles
                    save_profiles(profiles)

                    await btn_interaction.response.edit_message(
                        content=f"✅ Profilo **{selected_name}** eliminato.",
                        embed=None,
                        view=None
                    )

            class AnnullaButton(Button):
                def __init__(self):
                    super().__init__(label="Annulla", style=discord.ButtonStyle.secondary)

                async def callback(self, btn_interaction: Interaction):
                    if btn_interaction.user.id != interaction.user.id:
                        await btn_interaction.response.send_message("Non puoi annullare per un altro utente.", ephemeral=True)
                        return

                    await btn_interaction.response.edit_message(
                        content="Cancellazione annullata.",
                        embed=None,
                        view=None
                    )

            confirm_view = View(timeout=60)
            confirm_view.add_item(ConfermaButton())
            confirm_view.add_item(AnnullaButton())

            await select_interaction.response.edit_message(
                content=f"⚠️ Sei sicuro di voler eliminare il profilo **{selected_name}**?",
                embed=embed,
                view=confirm_view
            )

        select.callback = select_callback
        view.add_item(select)

        await interaction.response.send_message(
            content="Seleziona un profilo da eliminare:",
            view=view,
            ephemeral=True
        )



# --- Registrazione gruppo comandi ---

client.tree.add_command(PGCommands())

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client.run(TOKEN)
