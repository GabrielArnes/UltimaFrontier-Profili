import discord
from discord import ui, ButtonStyle
from discord.ui import Modal, TextInput, View, Button, Select
import json
import os

LOG_CHANNEL_ID = 1380217123825123338  # metti qui l’ID canale dedicato
DATA_FILE = "pg_profiles.json"
DEFAULT_COLOR = 0x3498db  

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
            "colore": None,
            "message_id": None,  # per tenere traccia del messaggio nel canale dedicato
        }

    def get_embed(self) -> discord.Embed:
        nome_pg = self.data.get("pg_nome") or "Profilo senza nome"

        # gestisco colore: se hex valido usa quello, altrimenti default azzurro
        colore_raw = self.data.get("colore")
        color_int = DEFAULT_COLOR
        if colore_raw:
            try:
                # Può essere esadecimale con # oppure no
                colore_str = str(colore_raw).strip()
                if colore_str.startswith("#"):
                    colore_str = colore_str[1:]
                color_int = int(colore_str, 16)
                if not (0 <= color_int <= 0xFFFFFF):
                    color_int = DEFAULT_COLOR
            except Exception:
                color_int = DEFAULT_COLOR

        embed = discord.Embed(title=nome_pg, color=color_int)
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
            "colore": "Colore (hex)",  # nuovo campo
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
            max_length=500,
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

        filepath = DATA_FILE
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
            all_profiles[user_id_str][pg_nome]["message_id"] = msg.id

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(all_profiles, f, ensure_ascii=False, indent=4)

        await interaction.response.edit_message(content=f"✅ Profilo **{pg_nome}** salvato con successo!", embed=None, view=None)


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
            ephemeral=True,
        )

    def create_embed(self, profile_name: str, data: dict) -> discord.Embed:
        colore_raw = data.get("colore")
        color_int = DEFAULT_COLOR
        if colore_raw:
            try:
                colore_str = str(colore_raw).strip()
                if colore_str.startswith("#"):
                    colore_str = colore_str[1:]
                color_int = int(colore_str, 16)
                if not (0 <= color_int <= 0xFFFFFF):
                    color_int = DEFAULT_COLOR
            except Exception:
                color_int = DEFAULT_COLOR

        embed = discord.Embed(title=profile_name, color=color_int)

        embed.add_field(name="Livello", value=data.get("livello", "-"), inline=True)
        embed.add_field(name="Identità", value=data.get("identità", "-"), inline=True)
        embed.add_field(name="Tema", value=data.get("tema", "-"), inline=True)

        embed.add_field(name="Origine", value=data.get("origine", "-"), inline=True)
        embed.add_field(name="Classi", value=data.get("classi", "-"), inline=True)
        embed.add_field(name="Abilità eroiche", value=data.get("abilità_eroiche", "-"), inline=True)

        embed.add_field(name="Descrizione fisica", value=data.get("descrizione_fisica", "-"), inline=False)
        embed.add_field(name="Link scheda", value=data.get("link_scheda", "-"), inline=False)

        immagine_url = data.get("immagine_url")
        if immagine_url:
            embed.set_image(url=immagine_url)

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
            view=DeleteMessageView(self.user),
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

