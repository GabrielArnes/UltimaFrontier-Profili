import os
import json
import discord
from discord import app_commands
from discord.ui import View, Select, Button
from discord import Interaction, Embed

from utils import load_profiles, save_profiles
from pg_views import PGCreationView, ShowProfileView
DATA_FILE = "pg_profiles.json"
DEFAULT_COLOR = 0x3498db  
LOG_CHANNEL_ID = 1380097036246061086  # metti qui l’ID canale dedicato

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
            ephemeral=True,
        )

    @app_commands.command(name="modifica", description="Modifica un profilo PG esistente")
    async def modifica(self, interaction: discord.Interaction):
        filepath = DATA_FILE
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

                embed = discord.Embed(title=nome, color=DEFAULT_COLOR)
                if immagine:
                    embed.set_image(url=immagine)
                embeds.append(embed)

        if not embeds:
            await interaction.response.send_message(
                "Nessun profilo trovato.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            content="Ecco tutti i profili salvati:",
            embeds=embeds[:10],
            ephemeral=True,
        )

        for i in range(10, len(embeds), 10):
            await interaction.followup.send(
                embeds=embeds[i : i + 10],
                ephemeral=True,
            )

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
            ephemeral=True,
        )

    @app_commands.command(name="elimina", description="Cancella uno dei tuoi profili")
    async def cancella(self, interaction: discord.Interaction):
        profiles = load_profiles()
        user_id = str(interaction.user.id)
        user_profiles = profiles.get(user_id, {})

        if not user_profiles:
            await interaction.response.send_message("❌ Non hai profili da cancellare.", ephemeral=True)
            return

        view = View(timeout=60)

        select = Select(
            placeholder="Scegli un profilo da cancellare",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=nome_pg, description="Seleziona per cancellare")
                for nome_pg in user_profiles.keys()
            ],
        )

        async def select_callback(select_interaction: discord.Interaction):
            if select_interaction.user.id != interaction.user.id:
                await select_interaction.response.send_message("Non puoi interagire con questo menu.", ephemeral=True)
                return

            selected_name = select.values[0]
            selected_profile = user_profiles[selected_name]

            embed = discord.Embed(title=selected_profile.get("pg_nome", selected_name), color=DEFAULT_COLOR)
            if selected_profile.get("immagine_url"):
                embed.set_image(url=selected_profile["immagine_url"])

            class ConfermaButton(Button):
                def __init__(self):
                    super().__init__(label="Conferma Cancellazione", style=discord.ButtonStyle.danger)

                async def callback(self, btn_interaction: Interaction):
                    # Elimina il messaggio nel canale log se esiste
                    message_id = selected_profile.get("message_id")
                    if message_id:
                        channel = btn_interaction.client.get_channel(LOG_CHANNEL_ID)
                        if channel:
                            try:
                                msg = await channel.fetch_message(message_id)
                                await msg.delete()
                            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                                pass  # Ignora errori cancellando messaggio

                    # Elimina il profilo e salva
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



def setup_commands(client: discord.Client):
    client.tree.add_command(PGCommands())
