# Python Script for Email Processing and Task/Note Creation in Notion

This Python script provides a way to automate task and note creation in Notion based on incoming emails in a Gmail account. It supports Gmail's labels for categorization and can optionally use OpenAI's GPT-3 or GPT-4 for processing email content. `Readme.md` generated using GPT-4.

## Dependencies

Please refer to the `requirements.txt` file for the list of dependencies. Here is a summary:

- `google-api-python-client`, `google-auth-httplib2`, and `google-auth-oauthlib`: Libraries needed for interacting with Gmail's API.
- `requests`: A standard Python library for making HTTP requests.
- `openai`: The official Python client library for the OpenAI API, used for text processing with GPT models.

Additionally, the script uses the custom modules `read_emails`, `mlfiles`, `notion_fx`, and `gpt_fx`, which you need to have in your project.

## Installation

Before running the script, ensure you have Python installed on your machine. You will also need the required dependencies installed in your Python environment. If you haven't installed the dependencies yet, open your terminal/command prompt and navigate to the project directory.

Then, run the following command:

```bash
pip install -r requirements.txt
```

This command installs all the dependencies listed in the `requirements.txt` file.

## Settings

Settings are loaded from a `settings.yml` file using the `mlfiles` module. Required settings include:

- `gmail.task_label`: Gmail label used for tasks.
- `gmail.note_label`: Gmail label used for notes.
- `gdrive.folder_id`: Google drive folder ID where to store attachments to make available in notion.
- `notion.task_db`: ID of the Notion database where tasks are stored.
- `notion.note_db`: ID of the Notion database where notes are stored.
- `openai.use_gpt`: A flag indicating whether to use OpenAI's GPT for processing email content. I personally prefer to use ai blocks in notion instead.
- `notion.token`: Token for the Notion API.

A `settings_template.yml` file is provided as a starting point. Make a copy of this file, rename it to `settings.yml`, and fill in your details.

## Gmail and Google Drive Setup

To interact with Gmail and Google Drive, you need to set up OAuth2 credentials. Here are the steps:

1. Go to Google Cloud Console.
2. Create a new project or select an existing one.
3. Go to the OAuth consent screen, fill in the necessary details, and save.
4. Go to Credentials, click "Create Credentials", and choose "OAuth client ID".
5. Choose "Desktop app" as the application type, name it, and create.	
6. Ensure you allow the scopes for Gmail and Google Drive (see below).
7. Download the JSON file of your credentials (`credentials.json`).

After downloading the credentials, run the provided `quickstart.py` script to get the access token. This script should be in the same directory as `credentials.json`.

The `quickstart.py` script requests Gmail and Google Drive access scopes, goes through the OAuth2 flow, and saves the access token in `token.json` for later use. You will need to authorize the app with a Google account that has access to the emails and the drive you want to process.

Please note that the script requests the following scopes: 'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/drive', and 'https://www.googleapis.com/auth/gmail.modify'. If you change these scopes in your script, you need to delete the `token.json` file, and a new one will be created with the updated scopes the next time you run your script.

## Gmail Filter Setup

You can set up a filter in Gmail so that any messages sent to `email_address+note@gmail.com` will be automatically labeled for import into Notion. This way, you can simply forward emails into Notion. To create this filter, follow these steps:

1. Go to Settings > Filters and Blocked Addresses in Gmail.
2. Click on Create a new filter.
3. In the "To" field, put your `email_address+note@gmail.com`.
4. Click on Create filter.
5. Check the box that says "Apply the label" and select the `note_label` you have defined in the `settings.yml`.
6. Click on Create filter.

## How it Works

The script processes unread emails with specified labels, namely `task_label` and `note_label`SS. These emails are transformed into tasks and notes in Notion and attachments are linked and saved in the google drive folder. If the `use_gpt` flag is set to True, GPT models are used to process the email content.

For each processed email, a page is created in the specified Notion database with various properties and blocks. Attachments in the email are also appended as blocks.

## Usage

Ensure you have the required dependencies and the `settings.yml` file correctly set up before running the script. Then simply execute the script. The script can be set up to run at regular intervals, for instance, by using a cron job.

Please note that this script requires proper API keys and access to the Gmail and Notion accounts, as well as OpenAI's API if the `use_gpt` flag is set to true. Make sure to handle these sensitive data securely.

To run the script, open your terminal/command prompt, navigate to the directory containing the script, and run:

```bash
py emails_to_tasks.py
```

This command initiates the script that processes your emails and creates tasks/notes in Notion.

Remember to handle your API keys and sensitive account access data securely.

## Contributing

Contributions, issues, and feature requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

## Author Information

Michael Larsen - Initial work - [Email](mailto:drlarsen215+code@gmail.com)

