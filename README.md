# AWS Well-Architected Chatbot

The [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) is a set of best practices for designing and operating reliable, secure, efficient, and cost-effective systems in the cloud. However, finding the right answers to questions related to the framework can be time-consuming and challenging. 

This repo provides the code to stand up your own Chatbot that can awnser questions using the text from the Well-Architected Framework.

**NOTE:** You must have your own [OpenAI API Key](https://platform.openai.com/account/api-keys) to use the Chatbot

If your interested in how this was built, checkout the blog post [here](https://www.buildon.aws/posts/well-arch-chatbot).

## QuickStart

Here is how you can easily get started using the ChatBot

Checkout the code
```
git clone https://github.com/banjtheman/aws_well_arch_chatbot.git
cd aws_well_arch_chatbot
git checkout langchain_version
```

Run the Chatbot
```
pip install -r requirements.txt
export OPEN_AI_KEY=YOUR_KEY
streamlit run aws_well_arch_st.py
# View at localhost:8501
```

Run the ingest pipeline (**Note:** It has already been run in this repo)
```
pip install -r requirements.txt
python ingest.py
```

### About the Code

This repository contains the code for an AWS Well-Architected Chatbot, built using Streamlit. The purpose of this chatbot is to provide users with answers and resources related to the AWS Well-Architected Framework, which is designed to help cloud architects build secure, high-performing, resilient, and efficient infrastructure for a variety of applications and workloads.

Please note that this chatbot is a **prototype** application and is intended for demonstration purposes only.
