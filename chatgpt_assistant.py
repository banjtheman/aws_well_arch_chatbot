import os
import re
import time
from openai import OpenAI


class AwsSolutionsArchitectAssistant:
    def __init__(self, open_ai_org):
        self.client = OpenAI(organization=open_ai_org)
        self.assistant_id = None
        self.thread = None

    def load_assistant(self, assistant_id):
        self.assistant_id = assistant_id

    def create_well_architected_framework_agent(self):
        # Upload AWS Well Architected Framework PDF
        well_arch_pdf = self.client.files.create(
            file=open("pdfs/wellarchitected-framework.pdf", "rb"), purpose="assistants"
        )
        # Setup assistant
        assistant = self.client.beta.assistants.create(
            name="AWS Certified Solutions Architect",
            instructions="You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You will always reference the AWS Well-Architected Framework when customers ask questions on building on AWS.",
            model="gpt-4-1106-preview",
            tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
            file_ids=[well_arch_pdf.id],
        )

        self.assistant_id = assistant.id

    def check_run_status(self, thread_id, run_id):
        done = False
        while not done:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id,
            )
            status = run.status
            print(run)
            print(status)

            if status in ["completed", "failed", "expired", "cancelled"]:
                print(f"Run {status}")
                done = True
            time.sleep(5)

    def run_ai_message_on_thread(self, user_message):
        if not self.thread:
            self.thread = self.client.beta.threads.create()

        # Send user message to thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message,
        )

        # Run the AI message on thread
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id,
        )

        # Loop until the run is done
        self.check_run_status(self.thread.id, run.id)

        # Get the returned responses
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        last_message = messages.data[0]

        message_content = self.get_message_citations(self.thread.id, last_message.id)

        print(message_content)

        return message_content

    def parse_content_for_streamlit(self, text):
        # Regex to find all [NUMBER] followed by text, non-greedy (shortest match)
        citations = re.findall(r"(\[\d+\].+?)(?=\[\d+\]|$)", text)

        # If citations are found, split the text at the first citation index
        if citations:
            # Find the index where the first citation starts in the text
            first_citation_index = text.find(citations[0])
            # Everything before this index is main content
            main_content = text[:first_citation_index].strip()
            # The rest are the citation texts
            caption_texts = [citation.strip() for citation in citations]
        else:
            # If no citations are found, the whole text is considered main content
            main_content = text.strip()
            caption_texts = []

        return main_content, caption_texts

    def get_message_citations(self, thread_id, message_id):
        # Retrieve the message object
        message = self.client.beta.threads.messages.retrieve(
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
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(
                    f"[{index}] {file_citation.quote} from {cited_file.filename}"
                )
            elif file_path := getattr(annotation, "file_path", None):
                cited_file = self.client.files.retrieve(file_path.file_id)
                citations.append(
                    f"[{index}] Click <here> to download {cited_file.filename}"
                )
                # Note: File download functionality not implemented above for brevity

        # Add footnotes to the end of the message before displaying to user
        message_content.value += "\n" + "\n".join(citations)

        return message_content.value

    def main(self):
        print("Starting AWS Solutions Architect Assistant")
        AGENT_ID = os.environ["AGENT_ID"]

        self.load_assistant(AGENT_ID)
        # self.create_well_architected_framework_agent()
        query = "What does the AWS Well-Architected Framework say about how to create secure VPCs?"
        message_content = self.run_ai_message_on_thread(query)
        print(message_content)


# Usage
# open_ai_org = os.environ["OPENAI_ORG"]
# assistant = AwsSolutionsArchitectAssistant(open_ai_org)
# assistant.main()
