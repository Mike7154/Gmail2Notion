# Importing necessary modules and the logging module
import logging
import read_emails
import mlfiles
import notion_fx
import gpt_fx

# Set up a logger with the name of the current module.
# The logger records events related to the execution of the program.
logger = logging.getLogger(__name__)

# Configure the logger to report events of all severity levels and
# to output messages in a format that includes the time, logger name,
# event severity level, and the actual event message.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load the settings from settings.yml. This includes the labels for tasks and notes,
# the Google Drive folder ID, the Notion database IDs, and the flag for GPT usage.
try:
    task_label = mlfiles.load_setting("gmail","task_label")
    note_label = mlfiles.load_setting("gmail","note_label")
    folder_id = mlfiles.load_setting("gdrive","folder_id")
    task_db = mlfiles.load_setting("notion","task_db")
    note_db = mlfiles.load_setting("notion","note_db")
    use_gpt = mlfiles.load_setting("openai","use_gpt")
except Exception as e:
    # Log any exceptions that occur while loading the settings.
    logger.error('Error occurred while loading settings: %s', e)

# Fetch unread emails that have a specific label and are located in a specific folder.
# Also, retrieve headers for making requests to the Notion API.
try:
    emails = read_emails.get_unread_emails_with_label(task_label, folder_id)
    headers = notion_fx.get_headers()
except Exception as e:
    # Log any exceptions that occur during the email fetching or headers retrieval.
    logger.error('Error occurred while fetching emails or retrieving headers: %s', e)

# Process each email for tasks, create a task in Notion from each email,
# and then mark each email as read.
try:
    for email in emails:
        print(email['subject'])
        notion_fx.task_from_email(task_db, email, headers, use_gpt)
        read_emails.mark_email_as_read(email['message_id'])
except Exception as e:
    # Log any exceptions that occur while processing the task emails.
    logger.error('Error occurred while processing task emails: %s', e)

# Similar to tasks, process each email for notes, create a note in Notion from each email,
# and then mark each email as read.
try:
    emails = read_emails.get_unread_emails_with_label(note_label, folder_id)
    for email in emails:
        print(email['subject'])
        notion_fx.note_from_email(note_db, email, headers, use_gpt)
        read_emails.mark_email_as_read(email['message_id'])
except Exception as e:
    # Log any exceptions that occur while processing the note emails.
    logger.error('Error occurred while processing note emails: %s', e)
