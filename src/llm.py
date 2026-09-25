from transformers import pipeline


test = pipeline("text-generation", model="Qwen/Qwen3-0.6B")
# response = test(
#     "1 + 2 = ",
#     max_new_tokens=30,
#     do_sample=False, # remove sampling randomness
#     return_full_text=False # do not generate original prompt too.
#     )[0]['generated_text']

# print(response)