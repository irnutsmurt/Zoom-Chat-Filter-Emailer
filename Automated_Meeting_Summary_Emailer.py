import json
import requests
import logging
import openai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from datetime import timedelta


# Initialize your OpenAI API key here
openai.api_key = "api key here"

def filter_private_messages(input_file):
    print("Starting to filter private messages...")
    filtered_chat = []
    skip_next = False
    with open(input_file, 'r', encoding='utf-8') as infile:  # Specify encoding here
        for line in infile:
            if '(Privately)' in line:
                skip_next = True
                continue
            if skip_next:
                skip_next = False
                continue
            filtered_chat.append(line)
    
    today = datetime.today().strftime('%Y-%m-%d')
    
    print("Saving filtered chat...")
    with open(f"meeting_saved_chat_{today}.txt", 'w', encoding='utf-8') as outfile:
        outfile.write(''.join(filtered_chat))

    print("Filtered chat saved.")
    return ''.join(filtered_chat)

def generate_response(filtered_chat_content):
    print("Generating summary using OpenAI API...")
    try:
        prompt = (
            "You are a helpful assistant. At the top of the message, start with a random greeting. Doesn't need to be this exact greeting but should not be offensive\n"
            "Read the chat and under the greeting generate message about the meeting that is one sentence that doesn't mention the chat, just gives a general vibe for the day but is not offensive.\n"
            "Summarize the chat with the following sections:\n"
            "Chat Summary: Bullet point summary of the chat for the day\n"
            "Highlights: Positive things in chat\n"
            "Topic: Topics shared\n"
            "Links posted in chat today:\n\n"
            f"Chat Content:\n{filtered_chat_content}"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}",
        }

        data = json.dumps({
            "model": "gpt-4",
            "messages": [{"role": "system", "content": "You are a helpful assistant."},
                         {"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "n": 1,
            "stop": None,
            "temperature": 0.3,
        })

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=data)
        response_json = response.json()
        
        if "choices" in response_json:
            response_text = response_json["choices"][0]["message"]["content"]
            today = datetime.today().strftime('%Y-%m-%d')
            print("Saving generated summary...")
            with open(f"meeting_summary_{today}.txt", 'w') as outfile:
                outfile.write(response_text)
            print("Summary saved.")
        else:
            logging.error(f"Error in API response: {response_json}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error answering question: {e}")
        return None
    print("Summary generation complete.")
    return response_text.strip()

def next_meeting_date():
    print("Calculating next meeting date...")
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    first_saturday = datetime(current_year, current_month, 1)
    third_saturday = datetime(current_year, current_month, 15)
    
    # Finding the first Saturday of the month
    # To adjust for different days, change the number 5 to the desired weekday
    # (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    while first_saturday.weekday() != 5:
        first_saturday += timedelta(days=1)
    
    # Finding the third Saturday of the month
    # To adjust for weekly meetings, you could use a loop to find every Nth desired weekday of the month
    while third_saturday.weekday() != 5:
        third_saturday += timedelta(days=1)
    
    # Adjust these conditionals to set your specific meeting schedule
    if today <= first_saturday:
        return first_saturday.strftime('%m-%d-%Y')
    elif today <= third_saturday:
        return third_saturday.strftime('%m-%d-%Y')
    else:
        # If today's date is past the third Saturday, find the first Saturday of the next month
        # For monthly meetings, modify this section to find the desired weekday of the next month
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
        next_first_saturday = datetime(current_year, current_month, 1)
        while next_first_saturday.weekday() != 5:
            next_first_saturday += timedelta(days=1)
        return next_first_saturday.strftime('%m-%d-%Y')
        # The print statement below won't be reached; it can be removed or adjusted as needed
        # print(f"Next meeting date is {next_first_saturday.strftime('%m-%d-%Y')}")

def send_email(subject, body, recipients, file_to_attach):
    print("Starting to send emails...")
    
    from_email = "email here"
    from_name = "name here"
    password = "password here" #gmail requires the users to create an app password

    print("Calculating next meeting date...")
    next_meeting = next_meeting_date()
    body += f"\n\nSee you at the next meeting on {next_meeting}!"
    body += f"\nName here"
    print(f"Next meeting date calculated: {next_meeting}")

    print("Preparing email components...")
    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{from_email}>"
    msg["Subject"] = subject

    print("Attaching body text...")
    msg.attach(MIMEText(body, 'plain'))

    print("Attaching file...")
    with open(file_to_attach, 'rb') as f:
        attach_file = MIMEApplication(f.read(), Name=file_to_attach.split('/')[-1])
        attach_file['Content-Disposition'] = f'attachment; filename="{file_to_attach.split("/")[-1]}"'
        msg.attach(attach_file)
    print("File attached.")

    print("Connecting to email server...")
    server = smtplib.SMTP("smtp.gmail.com", 587) #replace with the email server and port if its not using gmail.
    server.starttls()
    server.login(from_email, password)
    print("Connected to email server.")

    print(f"Sending emails to: {', '.join(recipients)}")
    msg["To"] = ', '.join(recipients)
    
    response = server.sendmail(from_email, recipients, msg.as_string())
    print(f"Response from Gmail: {response}") #Change the gmail to whatever email service you might be using
    
    if not response:
        print("Emails sent successfully.")
    else:
        print(f"Failed to send emails to: {response}")

    server.quit()
    print("Closing connection.")

# First filter out private messages
filtered_chat_content = filter_private_messages('meeting_saved_chat.txt')

# Then generate a response based on the filtered chat content
response = generate_response(filtered_chat_content)
print(response)

# Read emails from emails.txt
with open('emails.txt', 'r') as f:
    email_list = f.read().splitlines()

# Get today's date
today = datetime.today().strftime('%Y-%m-%d')

# Send the email
send_email(
    subject=f"Meeting Summary for {today}",
    body=response,
    recipients=email_list,
    file_to_attach=f"meeting_saved_chat_{today}.txt"
)


