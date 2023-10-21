# Meeting Summary Automation with OpenAI and Python

This Python script automates the process of creating and sending meeting summaries. It filters out private messages from a chat log, uses OpenAI's API to generate a meeting summary, and sends the summary via email. The emails also include the date of the next meeting.

## Features
Filter Private Messages: Remove lines that are private conversations from the meeting chat log.
Generate Summary: Utilizes OpenAI API to generate a concise summary of the meeting based on the chat log.
Email Automation: Sends out the generated summary to a list of recipients via email.
Next Meeting Date: Calculates the next meeting date and includes it in the email.
Dependencies
The following Python libraries are used:

json
requests
logging
openai
smtplib
email
datetime

Install libraries using the requirements.txt file with the following content to install:
```
requests 
openai
```

Using the command below:

`pip install requirements.txt`



### Setup
1. Replace the placeholders for the OpenAI API key, email, and password.
2. Move the exported Zoom chat log to the same folder as your script.
3. Prepare an emails.txt file with the email addresses of the recipients you want to send this to with address on a different line
Example below:
```
email1@gmail.com
email2@gmail.com
email3@gmail.com
email4@email.com
etc
etc
```

### How To Run
Execute the script by running:

`python Automated_Meeting_Summary_Emailer.py`

### Detailed Functionality
**filter_private_messages(input_file)**: Filters out private messages from the meeting chat.
**generate_response(filtered_chat_content)**: Generates a summary using OpenAI API.
**next_meeting_date()**: Calculates the date of the next meeting.
**send_email(subject, body, recipients, file_to_attach)**: Sends the summary email to recipients.

### Logging
The script prints messages on screen for each of its major steps, making it easier to debug or trace the execution flow.

### Troubleshooting
Make sure your [OpenAI API key](https://platform.openai.com/docs/introduction) is valid.
Gmail requires users to generate [app password](https://support.google.com/accounts/answer/185833?hl=en). Ensure you're using one.
