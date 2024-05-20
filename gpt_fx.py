from openai import OpenAI
import os
import mlfiles

def process_email(body):
    apikey = mlfiles.load_setting("openai", "api")
    gpt_model = mlfiles.load_setting("openai", "model")
    input_cost_per_mil = mlfiles.load_setting("openai", "input_cost_per_mil")
    output_cost_per_mil = mlfiles.load_setting("openai", "output_cost_per_mil")
    
    client = OpenAI(api_key=apikey)
    completion = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": "You are an assistant that only speaks in markdown format"},
            {"role": "system", "content": get_email_system_prompt()},
            {"role": "user", "content": body}
        ]
    )
    
    total_tokens = completion.usage.total_tokens
    input_tokens = completion.usage.prompt_tokens
    output_tokens = total_tokens - input_tokens
    
    input_cost = (input_tokens / 1_000_000) * input_cost_per_mil
    output_cost = (output_tokens / 1_000_000) * output_cost_per_mil
    total_cost = input_cost + output_cost
    
    update_log(f"Ran a GPT request. It cost {total_tokens} tokens (${total_cost:.6f}).")
    
    result = {
        "content": completion.choices[0].message.content,
        "cost": total_cost
    }
    
    return result

def get_email_system_prompt():
    text = """
    You will be provided with an email. Analyze the email and return the following: 

    # Summary
    - Summarize the important points of the email in an outline format.

    ## Action Items
    - List action items from the email. For each action item, include:
      - A checkbox prior to the action.
      - Any mentioned deadline.
      - The estimated time required.
      - The estimated importance on a scale of 0-100 (less than 50 being less important, 50 being average, and 100 being very important).

    ## Hyperlinks
    - List any important hyperlinks in the email. Exclude hyperlinks from the email signature area, URLs without proper context, and attachments (handled separately).

    ## Calendar Events
    - List any calendar events in the email as clickable Google Calendar hyperlinks. Each individual event should be a link that will add the event to my google calendar. Each hyperlink should include:
      - Title
      - Date/time
      - Location (if available)
      - Details (e.g., conference call information)

    # Original Email
    - Present the original email formatted for enhanced readability without using a code block.

    Focus on delivering concise, structured summaries with actionable insights. Maintain confidentiality and avoid speculations.
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
    print(result["content"])
    print(f"Cost: ${result['cost']:.6f}")
