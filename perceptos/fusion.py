import openai
import time
import os
import sys
import json
import re

# ================= setting =================

from openai import OpenAI

try: 
        with open('key.txt', 'r') as file:
                        lines = [line.strip() for line in file if line.strip()]
        
                        if len(lines) == 2:
                                url = lines[0]  
                                key = lines[1]
                        else:
                               print('api format error')
                               exit(1)
                     
except FileNotFoundError:
                print("key File not found. Creating a new counter with value 0.")
        


client = OpenAI(
    base_url=url,
    api_key=key,
)

SEED_LIST = [1, 2]


ARCH_INFO = ""
try:
    with open('hardware.txt', 'r') as file:
        ARCH_INFO = file.read().strip()
except FileNotFoundError:
    print("hardware File not found.")


if len(ARCH_INFO) == 0:
    print("hardware File is empty.")

from soft.FlameGraph.stack import analyze_stacks

STACK_INFO = analyze_stacks()
with open('target.txt', 'r') as f:
        lines = f.read().strip().splitlines()


TARGET_OBJECT= lines[1] if len(lines) > 1 else ""
#print(TARGET_OBJECT)
if len(TARGET_OBJECT)==0:
           print('please set target')
           exit

print('***')
print(ARCH_INFO)
print(TARGET_OBJECT)

BATCH_SIZE = 30 
TEMPERATURE = 1.0
PATTERN = "#///////////////////////////////"
# ===========================================


class Chat:
    def __init__(self, model_name, seed):
        self.conversation_list = []
        self.model_name = model_name
        self.seed = seed

    def ask(self, prompt):
        self.conversation_list.append({"role": "user", "content": prompt})
    

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_list,
                temperature=TEMPERATURE,
                seed=self.seed,
            )
            answer = response.choices[0].message.content
            self.conversation_list.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            print(f"LLM Error: {e}")
            return ""


class FusionAgent:
    PROMPT_TEMPLATE = """My hardware is {arch_info}
{perf_info}
This is the top 20 call stacks of the program I'm optimizing. I want to enhance {target_object}.
I tried adding the following options to the .config.
{config_list}

I am optimizing the Linux kernel configuration to improve {target_object} and have added the aforementioned options to the .config file. 
Please analyze one by one which potentially unfavorable options which I added may reduce throughput and cause bad effects. 
When analyzing, please analyze the direct impact of the configuration. 
Assuming security is not a concern.
Now analyze considering my hardware and stack, and then output the configuration I need to remove to enhance throughput.

**Output Requirements**:
After your analysis, you must strictly follow the format below to output the final removal list.
Please start your final list with the marker `### JSON Result:`, followed by a standard JSON list of strings (the configuration items to remove).

Example format:
... (your analysis) ...

### JSON Result:
["CONFIG_AAA=y", "CONFIG_BBB=n"]

If no items should be removed, output an empty list:
### JSON Result:
[]
"""

    def __init__(self, model_name, seed):
        self.chat_bot = Chat(model_name, seed)

    def extract_new_items(self, input_config_path):

        if not os.path.exists(input_config_path):
            print(f"Error: no file - {input_config_path}")
            return []

        lines_to_process = []
        processing_mode = False

        with open(input_config_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == PATTERN:
                    processing_mode = True
                    continue
                if processing_mode:
                    lines_to_process.append(line.strip())

        if not lines_to_process:
            return []

     
        seen_keys = set()
        unique_lines = []

        for line in reversed(lines_to_process):
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                if key and key not in seen_keys:
                    seen_keys.add(key)
                    unique_lines.append(line)

        unique_lines.reverse()
        return unique_lines

    def analyze_configs(
        self, configs, arch_info, perf_info, target_object, batch_size=BATCH_SIZE
    ):
        all_bad_configs = []
        total_batches = (len(configs) + batch_size - 1) // batch_size

        print(f"total num {len(configs)} ， total batch{total_batches} ...")

        for i in range(0, len(configs), batch_size):
            batch_config = configs[i : i + batch_size]
            current_batch = i // batch_size + 1

            prompt = self.PROMPT_TEMPLATE.format(
                arch_info=arch_info,
                perf_info=perf_info,
                target_object=target_object,
                config_list="\n".join(batch_config),
            )

            print(f"processing{current_batch}/{total_batches} ...")
            self.chat_bot.conversation_list = []  
            response = self.chat_bot.ask(prompt)

            print(f"\n[LLM Response Batch {current_batch}]:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            sys.stdout.flush()

            extracted = self.parse_llm_response(response)
            if extracted:
                all_bad_configs.extend(extracted)
                print(f"  -> filter numberL{len(extracted)} ")
            else:
                print(f"  -> does not filter")

        return list(set(all_bad_configs))

    def parse_llm_response(self, response):
        marker = "### JSON Result:"
        if marker in response:
            target_content = response.split(marker)[-1].strip()
        else:
            target_content = response

       
        target_content = (
            re.sub(r"```(?:json)?", "", target_content).replace("```", "").strip()
        )

        try:
            start_idx = target_content.find("[")
            end_idx = target_content.rfind("]")
            if start_idx != -1 and end_idx != -1:
                json_str = target_content[start_idx : end_idx + 1]
                return json.loads(json_str)
        except:
            pass

       
        return re.findall(r"CONFIG_[A-Z0-9_]+=[yn\d\.]+", target_content)

    def generate_result_file(self, input_path, output_path, bad_configs):
     
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        pattern_index = -1
        for i, line in enumerate(lines):
            if PATTERN in line:
                pattern_index = i
                break

        if pattern_index == -1:
            print("can not find PATTERN")
            return

        bad_set = {cfg.split("=")[0].strip() for cfg in bad_configs}

        output_lines = lines[: pattern_index + 1]

       
        processed_keys = set()
        for i in range(pattern_index + 1, len(lines)):
            line = lines[i]
            if "=" in line and not line.strip().startswith("#"):
                key = line.split("=")[0].strip()
                
                if key in bad_set:
                    output_lines.append("#" + line)
                else:
                    output_lines.append(line)
            else:
                output_lines.append(line)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(output_lines)
            f.write("\n#fusion\n")

    def run(self, input_path, round_num):
        print(f"Input Config: {input_path}")
        sys.stdout.flush()

        if not os.path.exists(input_path):
            print(f"Error: Input config not found at {input_path}")
            return

        candidates = self.extract_new_items(input_path)
        if not candidates:
            print("no new config。")
            return

        bad_configs = self.analyze_configs(
            candidates, ARCH_INFO, STACK_INFO, TARGET_OBJECT
        )

        output_path = input_path + "fusion"+rounds
        self.generate_result_file(input_path, output_path, bad_configs)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <round>")
        sys.exit(1)

    filen = './files/myconfig'
    rounds = sys.argv[1]

    seed = SEED_LIST[int(rounds)]

    agent = FusionAgent(model_name="gpt-4o-mini", seed=seed)
    agent.run(filen, rounds)
