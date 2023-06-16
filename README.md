# Python Script for Email Processing and Task/Note Creation in Notion

This Python script provides a way to automate task and note creation in Notion based on incoming emails in a Gmail account. It supports Gmail's labels for categorization and can optionally use OpenAI's GPT-3 or GPT-4 for processing email content. Readme.md generated using GPT-4.

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
py -m pip install -r requirements.txt
```
This command installs all the dependencies listed in the requirements.txt file.

## Settings

Settings are loaded from a `settings.yml` file using the `mlfiles` module. Required settings include:

- `gmail.task_label`: Gmail label used for tasks.
- `gmail.note_label`: Gmail label used for notes.
- `gdrive.folder_id`: Gmail folder id where the emails to be processed are stored.
- `notion.task_db`: ID of the Notion database where tasks are stored.
- `notion.note_db`: ID of the Notion database where notes are stored.
- `openai.use_gpt`: A flag indicating whether to use OpenAI's GPT for processing email content.
- `notion.token`: Token for the Notion API.

A `settings_template.yml` file is provided as a starting point. Make a copy of this file, rename it to `settings.yml`, and fill in your details.

## Gmail and Google Drive Setup

To interact with Gmail and Google Drive, you need to set up OAuth2 credentials. Here are the steps:

1. Go to Google Cloud Console.
2. Create a new project or select an existing one.
3. Go to the OAuth consent screen, fill in the necessary details, and save.
4. Go to Credentials, click "Create Credentials", and choose "OAuth client ID".
5. Choose "Desktop app" as the application type, name it, and create.
6. Download the JSON file of your credentials (`credentials.json`).

After downloading the credentials, run the provided `quickstart.py` script to get the access token. This script should be in the same directory as `credentials.json`.

The `quickstart.py` script requests Gmail and Google Drive access scopes, goes through the OAuth2 flow, and saves the access token in `token.json` for later use. You will need to authorize the app with a Google account that has access to the emails and the drive you want to process.

Please note that the script requests the following scopes: 'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/drive', and 'https://www.googleapis.com/auth/gmail.modify'. If you change these scopes in your script, you need to delete the `token.json` file, and a new one will be created with the updated scopes the next time you run your script.

## Contributing

Contributions, issues, and feature requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

## Author Information

Michael Larsen - Initial work - [Email](mailto:drlarsen215+code@gmail.com)
