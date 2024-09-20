import streamlit as st
from openai import OpenAI

with open('style.css') as f:
    css = f.read()
client = OpenAI(api_key=st.secrets["OPENAIAPIKEY"])
# Number to keep track of prompts
if "promptNum" not in st.session_state:
    st.session_state.promptNum  = 0
# Prompt to be carried over to the next session
if "prompt" not in st.session_state:
    st.session_state.prompt  = ""
# Story so far
if "story" not in st.session_state:
    st.session_state.story  = ""
# Memory of character 1
if "memory1" not in st.session_state:
    st.session_state.story  = ""
# Memory of character 2
if "memory2" not in st.session_state:
    st.session_state.story  = ""

if "dialog1" not in st.session_state:
    st.session_state.story  = ""

if "dialog2" not in st.session_state:
    st.session_state.story  = ""

if "messages" not in st.session_state:
    st.session_state.messages = [
        "Starting"
    ]

st.title("Narrator Simulator")
def narrator(prompt):
    global promptNum
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages= [
            {'role':'system', 'content':"""You are a highly successful author and Narrator. 
             Given a starting scenario. create a short introduction to the story, about 150-200 words long,
              that takes inspiration from the scenario. 
             Create 2 characters in this world. given them a name,desciption of their looks and general
             personality.
             Your output should follow the following format:
             1.Story
             2. character 1
                - name
                - description
                - personality
             3. character 2
                - name
                - description
                - personality"""},
            {'role':'user', 'content':prompt},
        ],
        n=1,
        max_tokens=1000
    )
    st.session_state.promptNum  += 1
    return response.choices[0].message.content

def createCharacter(prompt, memory, Pastdialog = ""):
    name = memory[:memory.find('Name')]
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {'role':'system', 'content':"""You are a fictional character. Given a desciption of the character and their memories,
             Deliver dialog and actions as if your really are this character.
             The output should focus on reacting to the most recent action. 
             Your output should be between 1-50 words
             Your output should end with a clear space followed by one of the 4 emotion angry, neutral, sad, happy.
             Include the emotions in curly brackets"""},
            {'role':'user', 'content':f"You is: {name}. Your memory: {memory}. Your previous dialog {Pastdialog}. The action : {prompt}"}
        ],
        temperature=1.4,
        max_tokens=1000
    )
    return response.choices[0].message.content

st.session_state.story = f"{st.session_state.story} Part {st.session_state.promptNum}: {st.session_state.prompt}"

if st.session_state.promptNum  == 0:
    st.caption("""Hello! I am a professional narrator! Let's have some fun role-playing!
                Give me a scenario and I'll help you get started!
                Your on your own after that!""")

    st.session_state.prompt = st.text_input("Give me a scenario")

    if st.session_state.prompt:

        output = narrator(st.session_state.prompt)
        firstCharIndex = output.find('2.')
        secondCharIndex = output.find('3.')
        st.session_state.story = output[:firstCharIndex]
        st.session_state.memory1 = output[firstCharIndex:secondCharIndex]
        st.session_state.memory2 = output[secondCharIndex:]
        st.write(st.session_state.story)
        st.write(st.session_state.memory1)
        st.write(st.session_state.memory2)
        char1 = createCharacter(st.session_state.story, st.session_state.memory1)
        char2 = createCharacter(st.session_state.story, st.session_state.memory2)
        st.write(char1)
        st.write(char2)
        st.session_state.dialog1=char1
        st.session_state.dialog2=char2
        st.session_state.prompt = st.text_input("Continue the Story")
        if st.session_state.prompt:
            st.session_state.messages.append(st.session_state.story)
            st.session_state.messages.append(st.session_state.dialog1)
            st.session_state.messages.append(st.session_state.dialog2)
            st.session_state.promptNum  += 1

elif st.session_state.promptNum  == 9:
    st.write("Story Over")
else:
    for message in st.session_state.messages:
        st.write(message)
    char1 = createCharacter(st.session_state.story, st.session_state.memory1,st.session_state.dialog1)
    char2 = createCharacter(st.session_state.story, st.session_state.memory2,st.session_state.dialog1)
    st.write(char1)
    st.write(char2)