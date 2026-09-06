
def process():
    with open("data/test.md") as file:
        source = file.read()
    print(source)
    i = 0

    while i < len(source):
        state = "par"
        text = source[i]

        if source[i] == "#":
            state = "title"
        elif source[i:i+2] == "```":
            state = "code"
            print("iis")

        j = i + 1
        while j < len(source):
            if source[j] == "#":
                state = "title"
            elif source[i:i+2] == "```":
                state = "code"

            if state in ["title", "par"] and source[j] == "\n":
                break
            if state == "code" and source[j:j+2] == "```" and j > i:
                break
                 
            text += source[j]
            j += 1

        i = j

        print({
            "type": state,
            "text": text
        })