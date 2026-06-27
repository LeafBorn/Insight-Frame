import os

from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY not found. Please add it to your .env file."
        )

    return ChatMistralAI(
        model="mistral-small-latest",
        api_key=api_key,
        temperature=0.3,
    )


def split_transcript(transcript: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Summarize the following portion of a meeting transcript in concise bullet points.",
            ),
            ("human", "{text}"),
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    partial_summaries = []

    for chunk in chunks:
        summary = map_chain.invoke({"text": chunk})
        partial_summaries.append(summary)

    combined_text = "\n\n".join(partial_summaries)

    reduce_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Combine the following partial summaries into one professional meeting summary. "
                "Use bullet points and remove duplicate information.",
            ),
            ("human", "{text}"),
        ]
    )

    reduce_chain = reduce_prompt | llm | StrOutputParser()

    return reduce_chain.invoke({"text": combined_text})


def generate_title(transcript: str) -> str:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Generate a short professional meeting title."
                "Maximum 8 words."
                "Return only the title.",
            ),
            ("human", "{text}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"text": transcript[:2000]})