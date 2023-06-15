# We are importing necessary modules
import read_emails
import mlfiles
import notion_fx
import gpt_fx

# Loading settings from settings.yml. 
task_label = mlfiles.load_setting("gmail","task_label") #"task_label" is the label for the tasks in the Gmail account
note_label = mlfiles.load_setting("gmail","note_label") #"note_label" is the label for the notes in the Gmail account")
folder_id = mlfiles.load_setting("gdrive","folder_id") #"folder_id" is the id for the folder in the Gmail account
task_db = mlfiles.load_setting("notion","task_db") #"database_id" is the id for the Notion database where tasks are stored
note_db = mlfiles.load_setting("notion","note_db") #"database_id" is the id for the Notion database where notes are stored
use_gpt = mlfiles.load_setting("openai","use_gpt") #"use_gpt" is a flag indicating whether to use GPT for processing

# ----------------- Tasks -----------------
# Fetching unread emails with the specified "task_label" from the specified "folder_id"
emails = read_emails.get_unread_emails_with_label(task_label, folder_id)

# Getting headers for making requests to the Notion API
headers = notion_fx.get_headers()




# Looping over the fetched emails
for email in emails:
	# Printing the subject of the email
	print(email['subject'])
	
	# Creating a task in the Notion database from the email content
	# If "use_gpt" is true, GPT will be used for processing the email content
	notion_fx.task_from_email(task_db, email, headers, use_gpt)
	
	# Marking the email as read after creating the task
	read_emails.mark_email_as_read(email['message_id'])



# ----------------- Notes -----------------
# Fetching unread emails with the specified "note_label" from the specified "folder_id"
emails = read_emails.get_unread_emails_with_label(note_label, folder_id)

for email in emails:
	print(email['subject'])
	notion_fx.note_from_email(note_db, email, headers, use_gpt)
	read_emails.mark_email_as_read(email['message_id'])
