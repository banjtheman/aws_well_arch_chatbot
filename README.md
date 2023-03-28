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
export OPEN_AI_KEY=YOUR_KEY
streamlit run aws_well_arch_st.py
# View at localhost:8501
```

### About the Code

This repository contains the code for an AWS Well-Architected Chatbot, built using Streamlit. The purpose of this chatbot is to provide users with answers and resources related to the AWS Well-Architected Framework, which is designed to help cloud architects build secure, high-performing, resilient, and efficient infrastructure for a variety of applications and workloads.

The main components of the code are:

**sidebar()**: This function displays the sidebar, which contains an image and a brief description of the AWS Well-Architected Framework.

**load_data_frame()**: This function reads a CSV file containing information about AWS Well-Architected Framework and returns a pandas DataFrame. The function uses Streamlit's @st.cache_data decorator to cache the result, speeding up the app's performance.

**load_embeddings()**: This function loads the precomputed document embeddings from a Pickle file. The embeddings are used to find relevant documents based on the user's query. This function also uses Streamlit's @st.cache_data decorator to cache the result.

**app()**: This function controls the app flow. It displays a text input for users to enter their query, and a button to submit the query. Upon submission, the app calls the utils.get_answer_from_chatgpt() function to fetch the ChatGPT-generated answer and relevant resources based on the query. The answer and resources are then displayed on the app interface.

**main()**: This function initializes the Streamlit app by setting the title, subheader, and calling the app() function to display the chatbot interface.

To run the Streamlit app, ensure you have the required dependencies installed, set the OPEN_AI_KEY environment variable, and execute the Python script. The chatbot will be accessible via a web browser at the specified URL.

Please note that this chatbot is a **prototype** application and is intended for demonstration purposes only.
