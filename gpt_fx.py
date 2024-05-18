from openai import OpenAI
import os
import mlfiles

def process_email(body):
    apikey = mlfiles.load_setting("openai", "api")
    gpt_model = mlfiles.load_setting("openai", "model")
    client = OpenAI(api_key=apikey)
    completion = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": "You are an assistant that only speaks in markdown format"},
            {"role": "system", "content": get_email_system_prompt()},
            {"role": "user", "content": body}
        ]
    )
    tokens = str(completion.usage.total_tokens)
    update_log(f"Ran a GPT request. It cost {tokens} tokens.")
    return completion.choices[0].message.content

def get_email_system_prompt():
    text = """
    You will be provided an email. Analyze the email and return the following: 
    - Write 'Summary' as a Heading 1 and provide a summary of the important points of the email in an outline format.
    - Write 'Action Items' as a Heading 2 and list action items from the email. For each action item, include:
      - A checkbox prior to the action.
      - Any deadline mentioned.
      - An estimated time required.
      - An estimated importance on a scale of 0-100 (less than 50 being less important, 50 being average, and 100 being very important).
    - List any important hyperlinks in the email. Do not include a hyperlink if it is from the email signature area, there is no proper URL, or if it is an attachment as those are handled separately.
    - Write 'Original Email' as a Heading 1 and output the original email formatted for enhanced readability without using a code block.
    Focus on delivering concise, structured summaries with actionable insights, maintaining confidentiality and avoiding speculations.
    """
    return text

def update_log(message):
    # Dummy implementation, replace with your logging mechanism
    print(message)

# Example usage
if __name__ == "__main__":
    email_body = """
    Dear Team,

    We need to finalize the report by Friday. The draft is attached. Please review it and provide feedback by Wednesday.

    Best regards,
    Alice
    """
    result = process_email(email_body)
    print(result)
