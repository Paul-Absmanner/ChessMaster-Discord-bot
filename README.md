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
2. Create a new application.
3. On the left sidebar, select Bot, scroll down to **Privileged Gateway Intents**.
4. Enable **Server Members Intent** (Required for processing message content directly)
5. Scroll up and press **Reset Token** and save it for later.
6. On the left sidebar, select OAuth2. From the **OAuth2 URL Generator** under **scopes List** select **bot** and **applications.commands**
7. Select the permissions under **OAuth2 URL Generator** under **bot permission List**

To operate correctly, the BOT requires the following permissions to be enabled on the server where it is hosted:

- Send Messages
- Attach Files
- View Channels

8. Copy the generated URL and add the bot to your discord server.



### Step 3: Copy the Server(GUILD_ID) ID from your discord server

1. Right-click the server icon.
2. Click **Copy Server ID**.



# Setup the Python File

1. Open the `.env.example` file in the project directory and rename it to `.env`.
2. Replace the placeholders with your bot token and discord server ID:
   ```bash
   TOKEN=YOUR_BOT_TOKEN
   GUILD_ID=YOUR_GUILD_ID
   ```
