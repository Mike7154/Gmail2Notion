import requests
import mlfiles
import gpt_fx


def get_headers(token=None):
    if token is None:
        token = mlfiles.load_setting('notion', 'token')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    return headers

def task_from_email(database_id, email, headers, use_gpt=False):
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
        "Tags": {
            "multi_select": [
                {
                    "name": "Email"
                }
            ]
        }
    }
    return create_page_from_email(database_id, email, headers, properties, use_gpt)

def note_from_email(database_id, email, headers, use_gpt=False):
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

def create_page_from_email(database_id, email, headers, properties, use_gpt=False):
    page = create_page(database_id, headers, properties)
    page_id = page['id']
    update_page_icon(page_id, headers)
    attachments = email.get('attachments', [])
    
    if attachments:
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
        gpt_out =  gpt_fx.process_email(body)
        body = gpt_out['content']
        cost = gpt_out['cost']
        cost_block = text_block("AI Cost: $"+str(cost))
        append_block(page_id, headers, cost_block)
        
    
    notion_blocks = markdown_to_notion_blocks(body)
    append_blocks_to_notion(page_id, notion_blocks, headers)
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
    response = requests.patch(url, headers=headers, json=data)  # Use json instead of data
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
import requests
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

class MarkdownToNotionProcessor(Treeprocessor):
    def run(self, root):
        blocks = []
        for element in root:
            blocks.extend(self.process_element(element))
        return blocks

    def process_element(self, element):
        blocks = []
        text_content = self.get_text_content(element)
        if element.tag == 'h1':
            blocks.append(self.create_heading_block(element, 'heading_1'))
        elif element.tag == 'h2':
            blocks.append(self.create_heading_block(element, 'heading_2'))
        elif element.tag == 'h3':
            blocks.append(self.create_heading_block(element, 'heading_3'))
        elif element.tag == 'p':
            blocks.append(self.create_paragraph_block(element))
        elif element.tag == 'ul' or element.tag == 'ol':
            for item in element:
                blocks.extend(self.process_element(item))
        elif element.tag == 'li':
            if '[ ]' in text_content or '- [ ]' in text_content:
                blocks.append(self.create_todo_block(element, False))
            elif '[x]' in text_content or '- [x]' in text_content:
                blocks.append(self.create_todo_block(element, True))
            else:
                blocks.append(self.create_list_item_block(element))
        elif element.tag == 'blockquote':
            blocks.append(self.create_quote_block(element))
        return blocks

    def get_text_content(self, element):
        if element.text:
            return element.text
        text_content = ""
        for sub_element in element.iter():
            if sub_element.text:
                text_content += sub_element.text
            if sub_element.tail:
                text_content += sub_element.tail
        return text_content

    def create_heading_block(self, element, heading_type):
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": self.convert_to_rich_text(element)
            }
        }

    def create_paragraph_block(self, element):
        rich_text = self.convert_to_rich_text(element)
        if rich_text:
            return {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            }
        return None

    def create_list_item_block(self, element):
        rich_text = self.convert_to_rich_text(element)
        if rich_text:
            return {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": rich_text
                }
            }
        return None

    def create_quote_block(self, element):
        rich_text = self.convert_to_rich_text(element)
        if rich_text:
            return {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": rich_text
                }
            }
        return None

    def create_todo_block(self, element, checked):
        content = self.get_text_content(element).replace('[ ]', '').replace('[x]', '').replace('- [ ]', '').replace('- [x]', '').strip()
        rich_text = self.convert_to_rich_text_content(content)
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": rich_text,
                "checked": checked
            }
        }

    def convert_to_rich_text(self, element):
        return self.convert_to_rich_text_content(self.get_text_content(element))

    def convert_to_rich_text_content(self, text):
        rich_text = []
        while text:
            if text.startswith('**'):
                end_index = text.find('**', 2)
                if end_index != -1:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": text[2:end_index]},
                        "annotations": {"bold": True}
                    })
                    text = text[end_index+2:]
                else:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": text}
                    })
                    break
            elif '[' in text and ']' in text and '(' in text and ')' in text:
                start_index = text.find('[')
                end_index = text.find(']', start_index)
                url_start = text.find('(', end_index)
                url_end = text.find(')', url_start)
                if start_index != -1 and end_index != -1 and url_start != -1 and url_end != -1:
                    rich_text.append({
                        "type": "text",
                        "text": {
                            "content": text[start_index+1:end_index],
                            "link": {
                                "url": text[url_start+1:url_end]
                            }
                        }
                    })
                    text = text[url_end+1:]
                else:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": text}
                    })
                    break
            else:
                next_index = text.find('**')
                if next_index != -1:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": text[:next_index]}
                    })
                    text = text[next_index:]
                else:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": text}
                    })
                    break
        return rich_text

class MarkdownToNotionExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(MarkdownToNotionProcessor(md), 'md_to_notion', 15)

def markdown_to_notion_blocks(markdown_text):
    md = markdown.Markdown(extensions=[MarkdownToNotionExtension()])
    root = md.parser.parseDocument(markdown_text.split("\n")).getroot()
    processor = MarkdownToNotionProcessor(md)
    blocks = processor.run(root)
    return [block for block in blocks if block]  # Filter out any None blocks


def append_blocks_to_notion(page_id, blocks, headers=None):
    if headers is None:
        headers = get_headers()
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    data = {
        "children": blocks
    }
    response = requests.patch(url, headers=headers, json=data)
    return response.json()

