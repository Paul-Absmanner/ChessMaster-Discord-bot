## Getting Started

### Prerequisites

Make sure you have the following installed:

   ```bash
   pip install -r requirements.txt
   ```


## Create a Discord Bot

### Step 1: Enable Developer Mode

1. Go to **User Settings** in Discord.
2. Navigate to **Advanced** and enable **Developer Mode**.

[Guide for enabling Developer Mode](https://www.partitionwizard.com/partitionmagic/discord-developer-mode.html)

---

### Step 2: Create a Bot in the Discord Developer Portal

1. Visit the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application, then add a bot user.
3. On the left sidebar, select Bot und press **Reset Token**. Replace the **TOKEN** value in the **.env** with it.
4. On the left sidebar, select OAuth2. From the **OAuth2 URL Generator** scopes List select **bot** and **applications.commands**


To operate correctly, the BOT requires the following permissions to be enabled on the server where it is hosted:

1. **View Channels Permission**  
   This permission allows the BOT to access all text channels where games can be played.

2. **Send Messages Permission**  
   Enables the BOT to send messages for game invitations, updates, and statistics in the text channels.

3. **Attach Files Permission**  
   Allows the BOT to share images of the chessboard, showing the current game state, within the text channels.

Select the permissions under **OAuth2 URL Generator** bot permission List

[Detailed guide to creating a bot](https://www.ionos.at/digitalguide/server/knowhow/discord-bot-erstellen/#:~:text=Aktivieren%20Sie%20in%20Ihrem%20Discord,und%20klicken%20Sie%20%E2%80%9ECreate%E2%80%9C.)


### Step 3: Copy the Server(GUILD_ID) ID from your discord server

1. Right-click the server icon.
2. Click **Copy Server ID**.



# Setup the Python Discord Bot

## Replace `TOKEN` and `GUILD_ID`

1. Open the `.env` file in the project directory.
2. Replace the placeholders with your bot token and discord server ID:
   ```bash
   TOKEN=YOUR_BOT_TOKEN
   GUILD_ID=YOUR_GUILD_ID
   ```
