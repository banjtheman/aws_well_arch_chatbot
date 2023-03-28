# AWS Well-Architected Chatbot

The [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) is a set of best practices for designing and operating reliable, secure, efficient, and cost-effective systems in the cloud. However, finding the right answers to questions related to the framework can be time-consuming and challenging. 

This repo provides the code to stand up your own Chatbot that can awnser questions using the text from the Well-Architected Framework.

**NOTE:** You must have your own [OpenAI API Key](https://platform.openai.com/account/api-keys) to use the Chatbot

If your interested in how this was built, checkout the blog post here *TODO*

## QuickStart

Here is how you can easily get started using the ChatBot

```
git clone https://github.com/banjtheman/aws_well_arch_chatbot.git
cd aws_well_arch_chatbot
pip install -r requirements.txt
export OPEN_AI_KEY-YOUR_KEY
streamlit run aws_well_arch_st.py
# View at localhost:8501
```
