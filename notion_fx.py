import requests
import mlfiles
import gpt_fx

def get_headers(token = mlfiles.load_setting('notion','token')):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    return headers
def task_from_email(database_id, email, headers, use_gpt = False):
    subject = email['subject']
    properties = {
      "Name": {
        "title": [
          {
            "text": {
              "content": subject
            }
          }
        ]
      },
      "Importance": {
        "number": 50
      },
      "Urgency": {
        "number": 50
      },
      "Tags": {
        "multi_select": [
          {
            "name": "Email"
          }
        ]
      }
    }
    return create_page_from_email(database_id, email, headers, properties, use_gpt)
def note_from_email(database_id, email, headers, use_gpt = False):
    subject = email['subject']
    properties = {
      "Name": {
        "title": [
          {
            "text": {
              "content": subject
            }
          }
        ]
      },
      "Tags": {
        "multi_select": [
          {
            "name": "Email"
          }
        ]
      }
    }
    return create_page_from_email(database_id, email, headers, properties, use_gpt)
def create_page_from_email(database_id, email, headers, properties, use_gpt = False):
    page = create_page(database_id, headers, properties)
    #print(page)
    page_id = page['id']
    update_page_icon(page_id, headers)
    attachments = email['attachments']
    if len(attachments)> 0:
        at_text = h2_block("Attachments")
        append_block(page_id, headers, at_text)
    for attachment in attachments:
        url = attachment['webViewLink']
        caption = attachment['name']
        data = link_block(url, caption)
        append_block(page_id, headers, data)
    body = email['body']
    if use_gpt:
        print("use_gpt is set to True. Using GPT to process email body")
        body = gpt_fx.process_email(body)
    body = split_paragraph(body)
    for b in body:
        data = text_block(b)
        append_block(page_id, headers, data)

    return page

def create_page(database_id, headers, properties):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {
            "database_id": database_id
        },
        "properties": properties
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def append_block(page_id, headers, data):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    cdata = {"children": [data]}
    response = requests.patch(url, headers=headers, json=cdata)
    return response.json()

def text_block(string, btype = "paragraph"):
   #btype can be "paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"
    return {
        "object": "block",
        "type": btype,
        btype: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": string
                    }
                }
            ]

        }
    }

def file_block(url, caption):
    return {
        "type": "file",
        "file": {
            "caption": [
                {
                    "type": "text",
                    "text": {
                        "content": caption
                    }
                }
            ],
            "type": "external",
            "external": {
                "url": url
            }
        }
    }

def link_block(url, caption):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                  "type": "text",
                  "text": {
                    "content": caption,
                    "link": {"url": url}
                  },
                  "annotations": {
                    "bold": True
                  },
                  "plain_text": caption,
                  "href": url
                }
            ]

        }
    }



def h3_block(string):
    return text_block(string, "heading_3")

def h1_block(string):
    return text_block(string, "heading_1")

def h2_block(string):
    return text_block(string, "heading_2")

def update_page_icon(page_id, headers):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "icon": {
            "type": "emoji",
            "emoji": "📧"
        }
    }
    response = requests.patch(url, headers=headers, data=data)
    return response.json()

def split_paragraph(paragraph):
    paragraphs = []
    while len(paragraph) > 2000:
        split_index = paragraph.rfind('\n', 0, 2000)
        if split_index == -1:
            # If there's no '\n' in the first 2000 characters, split at the 2000th character
            split_index = 2000
        paragraphs.append(paragraph[:split_index])
        # Skip past the '\n' character for the next paragraph
        paragraph = paragraph[split_index+1:]
    paragraphs.append(paragraph)  # Append the remainder of the paragraph
    return paragraphs

