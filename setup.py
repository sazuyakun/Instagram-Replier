from setuptools import setup, find_packages

setup(
    name="instagram-replier",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langgraph",
        "langchain[google-genai]",
        "langchain-core",
        "dotenv",
        "ipython",
        "instagrapi",
    ],
    python_requires=">=3.8",
)
