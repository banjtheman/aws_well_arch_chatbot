import os
import time
from openai import OpenAI


OPEN_AI_ORG = os.environ["OPENAI_ORG"]
AGENT_ID = os.environ["AGENT_ID"]

def aws_solutions_architect_agent(client):
    # Upload AWS Well Architected Framework PDF
    well_arch_pdf = client.files.create(
        file=open("pdfs/wellarchitected-framework.pdf", "rb"), purpose="assistants"
    )

    # Setup agent
    agent = client.beta.assistants.create(
        name="AWS Certified Solutions Architect",
        instructions="You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You will always reference the AWS Well-Architected Framework when customers ask questions on building on AWS.",
        model="gpt-4-1106-preview",
        # model="gpt-3.5-turbo-1106",
        tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
        file_ids=[well_arch_pdf.id],
    )

    return agent


def check_run_status(client, thread_id, run_id):
    done = False
    while not done:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )

        status = run.status
        print(run)
        print(status)

        if status == "completed":
            print("Run completed")
            done = True
        # same for cancelled, failed or expired
        elif status == "failed":
            print("Run failed")
            done = True
        elif status == "expired":
            print("Run expired")
            done = True
        elif status == "cancelled":
            print("Run cancelled")
            done = True

        # sleep for 5 seconds
        time.sleep(5)


def run_ai_message_on_thread(client, thread, agent_id):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=agent_id,
    )

    # Loop until the run is done
    check_run_status(client, thread.id, run.id)

    # Get the returned responses
    client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Get messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Get the last message (its the first in the list)
    last_message = messages.data[0]

    message_content = get_message_citations(client, thread.id, last_message.id)

    return message_content


def send_user_message_to_thread(client, thread, user_message):
    # Send message to thread
    message_object = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )

    return message_object


def get_message_citations(client, thread_id, message_id):
    # Retrieve the message object
    message = client.beta.threads.messages.retrieve(
        thread_id=thread_id, message_id=message_id
    )

    # Extract the message content
    message_content = message.content[0].text
    annotations = message_content.annotations
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(
            annotation.text, f" [{index}]"
        )

        # Gather citations based on annotation attributes
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(
                f"[{index}] {file_citation.quote} from {cited_file.filename}"
            )
        elif file_path := getattr(annotation, "file_path", None):
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(
                f"[{index}] Click <here> to download {cited_file.filename}"
            )
            # Note: File download functionality not implemented above for brevity

    # Add footnotes to the end of the message before displaying to user
    message_content.value += "\n" + "\n".join(citations)

    return message_content.value


def main():
    print("Staring openAI")

    client = OpenAI(
        organization=OPEN_AI_ORG,
    )

    # Init Agent
    # agent_aws = aws_solutions_architect_agent(client)

    agent_id = AGENT_ID

    # Create new Thread
    thread = client.beta.threads.create()

    # send message to agent
    query = "What does the AWS Well-Architected Framework say about how to create secure VPCs?"
    user_message = send_user_message_to_thread(client, thread, query)

    # Send message to thread
    message_content = run_ai_message_on_thread(client, thread, agent_id)

    print(message_content)


# Run the main function
if __name__ == "__main__":
    main()
