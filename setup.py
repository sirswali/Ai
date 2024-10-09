import setuptools
import os
from dotenv import load_dotenv

load_dotenv()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="multi-agent-task-management",
    version="0.1.0",
    author=os.getenv("AUTHOR_NAME", "Your Name"),
    author_email=os.getenv("AUTHOR_EMAIL", "your.email@example.com"),
    description="A multi-agent system for task management with Slack and Jira integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multi-agent-task-management",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv",
        "slackclient",
        "jira",
        "sqlalchemy",
        "transformers",
        "torch",
        "flask",
        "flask-bcrypt",
        "flask-wtf",
        "flask-paginate",
        "aiohttp",
        "numpy",
        "scipy",
        "tkinter",
        # Add other dependencies as needed
    ],
    entry_points={
        "console_scripts": [
            "run-task-management=main:main",
            "run-chat-interface=chat_interface:main",
        ],
    },
)