"""
This script just prints the system prompts and in-context examples for all the experiments.
"""

from litellm import completion

from src.constants import IC_EXAMPLES, INGREDIENTS, SYSTEM_PROMPTS, TOOLS

instruction = """I am developing a paradigm for a psychology experiment, which is an AI-powered crafting game.
I want the task to have rules that participants can learn over multiple trials of crafting things together and trying to make the best item they can.
Each setting has tools, which are constant frm trial to trial, and ingredients, of which six are chosen at random for each trial. Each item is represented by an emoji.
I wan the rules to be learnable, but not immediately obvious. Participants should keep learning new things over multiple trials.
Here are the settings I have so far. Could you please generate another for me?"""

if __name__ == "__main__":
    for experiment_name in SYSTEM_PROMPTS.keys():
        print(instruction, "\n\n")
        print(f"Experiment: {experiment_name}")
        print("System Prompt:")
        print(SYSTEM_PROMPTS[experiment_name])
        print("Tools:")
        print(TOOLS[experiment_name])
        print("Ingredients:")
        print(INGREDIENTS[experiment_name])
        print("In-Context Examples:")
        print(IC_EXAMPLES[experiment_name])
        print("\n\n")

    messages = [
        {"role": "system", "content": instruction},
    ]

    for experiment_name in SYSTEM_PROMPTS.keys():
        messages.append(
            {
                "role": "user",
                "content": "Please generate a new experimental setting.",
            }
        )

        ic_response = f'''```python
system_prompt = """{SYSTEM_PROMPTS[experiment_name]}"""
tools = {TOOLS[experiment_name]}
ingredients = {INGREDIENTS[experiment_name]}
ic_examples = {IC_EXAMPLES[experiment_name]}
```'''
        messages.append(
            {
                "role": "assistant",
                "content": ic_response,
            }
        )

    for i in range(5):
        messages.append(
            {"role": "user", "content": "Please generate a new experimental setting."}
        )
        response = completion(
            model="anthropic/claude-3-7-sonnet-latest",
            messages=messages,
        )
        res_content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": res_content})
        print(res_content)
        print("\n\n")
