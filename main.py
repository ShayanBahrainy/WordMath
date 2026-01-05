from flask import Flask, render_template, abort
from token_embedding import TokenEmbedding

embed = TokenEmbedding("glove.2024.wikigiga.50d")
print("Loaded TokenEmbedding! Now initializing Flask...")

app = Flask(__name__)
app.config['RELOAD_TEMPLATES'] = True


TOKEN_CHARS = [char for char in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"]
OPERATOR_CHARS = ["+", "-"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process/<expression>")
def process(expression: str):
    answer = " = "

    expression = expression.replace(' ', '').replace('\n', '').replace('\t','').lower()

    #Abort on unknown characters
    for char in expression:
        if char not in TOKEN_CHARS and char not in OPERATOR_CHARS:
            print("ab1: " + char)
            return abort(400)

    tokens = [""]

    i = 0
    while i < len(expression):
        if expression[i] in TOKEN_CHARS:
            tokens[-1] += expression[i]

        if expression[i] == "-":
            tokens.append("-")

        if expression[i] == "+":
            tokens.append("")
        i += 1

    #Abort if there's a missing token
    for token in tokens:
        if token == "":
            return abort(400)

    vectors = embed[[token if token[0] != "-" else token[1:] for token in tokens]]

    vectors = [vectors[i] if tokens[i][0] != "-" else -vectors[i] for i in range(len(tokens))]

    sum = 0
    for vector in vectors:
        sum += vector

    #Exclude provided tokens
    answer += embed.get_closest_token(sum, exclude=[token if token[0] != "-" else token[1:] for token in tokens])

    return answer


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)