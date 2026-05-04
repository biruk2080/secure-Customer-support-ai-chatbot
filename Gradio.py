# from State import run_agent
# import gradio as gr

# iface = gr.Interface(
#     fn=run_agent,
#     inputs=["text"],
#     outputs="text",
#     live=False,
# )
# iface.launch(share=True)

# from tavily import TavilyClient

# client = TavilyClient("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")
# response = client.search(
#     query="who is leo messi's wife?",
#     search_depth= "fast"
# )
# print(response[].content)


# # Step 2. Defining the list of URLs to extract content from
# urls = [
#     "https://en.wikipedia.org/wiki/Artificial_intelligence",
#     "https://en.wikipedia.org/wiki/Machine_learning",
#     "https://en.wikipedia.org/wiki/Data_science",
#     "https://en.wikipedia.org/wiki/Quantum_computing",
#     "https://en.wikipedia.org/wiki/Climate_change"
# ] # You can provide up to 20 URLs simultaneously

# # Step 3. Executing the extract request
# response = client.extract(urls=urls, include_images=True)

# # Step 4. Printing the extracted raw content
# for result in response["results"]:
#     print(f"URL: {result['url']}")
#     print(f"Raw Content: {result['raw_content']}")
#     print(f"Images: {result['images']}\n")

# # Step 2. Creating a streaming research task
# stream = client.research(
#     input="Research the latest developments in AI",
#     model="pro",
#     stream=True
# )

# # Step 3. Processing the stream as it arrives
# for chunk in stream:
#     print(chunk.decode('utf-8'))

from llmlingua import PromptCompressor

from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_community.document_compressors import LLMLinguaCompressor

# Initialize the compressor
llm_lingua = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    use_llmlingua2=True,
    device_map="cpu"
)

# Compress the prompt
prompt = "Sam bought a dozen boxes, each with 30 highlighter pens inside, for $10 each box..."

compressed_prompt = llm_lingua.compress_prompt(prompt, instruction="", question="", target_token=200)

print(compressed_prompt)