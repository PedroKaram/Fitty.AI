from flask import Flask, request, jsonify
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import yaml

# Carrega config.yaml
with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Flask app
app = Flask(__name__)

# LLM do LangChain
llm = ChatOpenAI(
    api_key=cfg["api_key"]["key"],
    model=cfg["model"]["name"]
)

# Buffer de memória do LangChain
memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True
)

# Template do prompt
prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
Você é um nutricionista virtual amigável, prático e direto.

No início da conversa, colete: peso (kg), altura (cm), idade, sexo e nível de atividade física.
Use essas informações para calcular TMB e TDEE. Apresente resultados de forma resumida, sem contas detalhadas.
Depois, peça detalhes das refeições do dia, estime calorias consumidas, diga se está em déficit ou superávit.

Histórico da conversa até agora:
{history}

Nova mensagem do usuário:
{input}

Responda de forma amigável, prática e sem repetir perguntas já respondidas.
"""
)

# Cria o chain
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

# Endpoint Flask
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")

    # Executa o chain
    response = chain.run(input=user_input)

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)
