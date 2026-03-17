# Architecture decision record 
# Project : Resume AI Coach 
# Author : Vaishali Bhardwaj
# Started: March 2026

## Decision 1 - Project Folder Structure 

### What we created 
- chains/ - Langchain files (parser, matcher, rewriter)
- toos/ - Langchain agent tools (PDF reader , jobs API , cover letter)
- docs/ - Documentation (descision/ architecture)
- .env - API keys (never goes to Github)
- .gitignore - Tells Git which files to ignore 

### Why this strucutre 
Seperations of concerns - each folder has one responsibiity 
Clean architecture makes the project readable , maintainable and impressive to technical reviewers

### Gen AI Concepts it maps to 
- chains/ -> Langchain chain concepts
- tools/ -> Langchian Agent and Tools concepts
- .env -> API security and key management

## Descision 2 - Model Choice : Claude Sonnet (claude -sonnet -4-6)
### Why claude sonnet over GPT-4o
1. 200,000 token context windo vs GTP-4o's 128,000
-> Entire resume + JD + Full chat hisotry fits in one call 
-> No complex memory management needed for most sessions 

2. Superior Strucutre JSON extraction 
-> Resume parsing requires requires reliable JSON output
-> Claude Sonnet produces cleaner structured  data 

3. Deliberate differentiation 
-> Every tutorial uses openAI
-> Using claude shows reasoned descision making (PM thinking)

### Cost per session 
- Average session ~ 5000 tokens
- Cost at sonnet pricing ~ 0.02 per session 
- $5 credit ~~ 250 full test sessions 

## Decision 3 - Framwork : Langchain 
### Why Langchain over raw Anthropic  SDK 
Raw SDK = send text , get text back .That is all .
Langchain adds :-
- Chains : sequence multiple steps cleanly 
- Agents : model decides what tool to call 
- Memory : conversation hisotry managed automatically 
- Tools : give model access to real functions 
- Langsmith : observer every reasoning step (chain of thought)

Building all of this from sratch = week of work 
Langchain is industry standard for production LLM apps 

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept Clarification  - SDK vs Langchain vs Claude 
ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically
Stack order:
Our Python code → LangChain → Anthropic SDK → Claude API

# Day 1 Learning - First API call 
### What I built 
day1_raw_api.py - a pythin file that calls Claude directly using Anthropic SDK and prints the response in terminal 

### What I learned 
- import os - reads environmental variables from Mac's memory 
- load_dotenv() - load .env file into memory at runtime 
- os.getenv() - retireves the API key safely 
- anthropic.Anthropic(api_key=) - creates the client connection 
- client.messages.create() - sends the actual request to claude 
- message.content[0].text - extract Claude's text response 

### Debugging I did 
- Fixed space after = sign in .env file (API key )
- Created fresh API key when old one was not working 
- used cat.env command to verify file contents 

### Key Insight
The code never runs claude locally . My mac sends text to Anthropic's servers , Claude thinks there, response come back. My Mac is just a messenger 

