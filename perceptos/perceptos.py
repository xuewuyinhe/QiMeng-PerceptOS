# -*- coding: utf-8 -*-
import openai
import random
import os
import easygui as g
from menuconfig import MenuConfig
import re
import readline
import sys
import time
import fire
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import os
from openai import AzureOpenAI
import json
from openai import BadRequestError
import tiktoken
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


def num_tokens_from_string(string: str, encoding_name: str) -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens



###############################
iter_count=-1
seed_pool=[47]
ask_seed=seed_pool[iter_count]
def load_json_safe(filename: str):
  
    if not os.path.exists(filename):
        print(f" {filename} does not exit")
        return {}

    
    with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

class Chat:
    def __init__(self,conversation_list=[]):
        self.conversation_list = [[],[],[],[],[],[],[]]  # initialize the dialogue list
        self.costs_list = [] 
        self.bre=False
        self.naive=[]
   # print dialogue
    def show_conversation(self,msg_list):
        for msg in msg_list[-2:]:
            if msg['role'] == 'user': 
                message = msg['content']
                if msg['content']=="exit":
                     
                     self.bre=True
                     print("usr exit!")
            else: 
                   message = msg['content']
                   print(f"LLM: {message}")           
            print()

    def  last_step(self,ty,first):
            if first==1:
                        self.conversation_list[ty].pop(-3)
                        self.conversation_list[ty].pop(-3)
            else:
                        self.conversation_list[ty].pop(-1)
                        self.conversation_list[ty].pop(-1)
   
    def clear(self):
        for i in range(len(self.naive)):
            self.naive.pop()

    def naive_ask(self,prompt):
        self.naive.append({"role":"user","content":prompt})
       
       

        max_retries = 15
        retry_delay = 1
        response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.naive,
                    seed=0,
                    temperature=0,                   
        )
 
        answer = response.choices[0].message.content
        self.naive.append({"role":"assistant","content":answer})
        return answer


    def ask(self,prompt,ty=0):
        print('prompt')
        print(ty)
        if ty==0 or ty==5:
                print(len(self.conversation_list[ty]))
                if len(self.conversation_list[ty])>5:
                    print('*****0')
                    for j in range(6):
                            self.conversation_list[ty].pop(0)
                    print('*****/////')
                    print(self.conversation_list[ty])
        elif ty==6:

                if len(self.conversation_list[ty])>3:
                    print('*****6')
                    for j in range(4):
                            self.conversation_list[ty].pop(0)
                    print('*****/////')
                    print(self.conversation_list[ty])
        
        else:
                if len(self.conversation_list[ty])>3:
                    for j in range(2):
                            self.conversation_list[ty].pop(2)
            
        self.conversation_list[ty].append({"role":"user","content":prompt})
                
   

        a=time.time()
        response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.conversation_list[ty],
                    temperature=1.0,
                    seed=ask_seed                   
        )
        b=time.time()
        print("time")
        print(b-a)
        answer = response.choices[0].message.content
 

        global output_token_total
        global input_token_total
        global ask_total
           
        input_messages = self.conversation_list[ty]
        input_text = ""
        for msg in input_messages:
                  input_text += msg['content']

        input_tokens = num_tokens_from_string(input_text, "o200k_base")


       
        output_tokens = num_tokens_from_string(answer, "o200k_base")

  
        with output_token_lock:
                    ask_total=1
                    input_token_total += input_tokens
                    output_token_total += output_tokens



      #  print('****')
      #  print(input_token_total)
      # print(output_token_total)

        self.conversation_list[ty].append({"role":"assistant","content":answer})

        self.show_conversation(self.conversation_list[ty])
 
        if de==2:
                print("conversation_list after ask:")
                print(self.conversation_list[0])
                print(self.conversation_list[1])



        print()
        return answer

def total_counts(response):    
    
    tokens_nums = int(response['usage']['total_tokens']) 
    price = 0.002/1000 
    sp = '{:.5f}'.format(price * tokens_nums * 7.5)
    total = f"spend {tokens_nums} token,and spend {sp} yuan)"


    return float(sp)


#global var

de = 1
we = 3000
save_cycle = 5
input_token_total=0
output_token_total=0
output_token_lock = threading.Lock()
input_token_lock = threading.Lock()
ask_total=0

#from arch.arch import get_arch
from soft.FlameGraph.stack import analyze_stacks
from template.temp import PromptBuilder




def generate_words_caidan(caidan, i):
    start_index = i * 5
    end_index = (i + 1) * 5
    items = list(caidan.items())[start_index:end_index]
    
   
    if items:
        words_caidan = "\n".join([f"{index_t} {name_t}" for name_t, index_t in items])
        return words_caidan
    else:
        return ""  


def main(tt=0,de = 1, we = 3000, save_cycle = 5):

    
    de=de #Setting de=2 outputs more detailed information
    menu_config = MenuConfig("Kconfig")    
   
    with open('target.txt', 'r') as f:
        lines = f.read().strip().splitlines()    

    target = lines[0] if len(lines) > 0 else ""
    target_object = lines[1] if len(lines) > 1 else ""

    print('***')
    print(target)
    print(target_object)
    if len(target)==0 or len( target_object)==0:
           print('please set target')
           return
   

    talk = Chat()
    print()    

 #   archii = get_arch()
    archii=""
    try:
        with open('hardware.txt', 'r') as file:
                        archii = file.read().strip()

                        
    except FileNotFoundError:
                print("hardware File not found.")

    if len(archii)==0:
        print("hardware File not found.")
        return
    apa_gong = analyze_stacks()
    stack_template = PromptBuilder.stack_template()
    hardware_template = PromptBuilder.hardware_template()
    subinfo_template = PromptBuilder.subinfo_template()

    ans1=talk.naive_ask(apa_gong+stack_template)

    ans3=talk.naive_ask("The previous simplification may have been too aggressive. Rethinking and retain the critical words and essential details in stack. Now output again without other words:")
    
    talk.clear()
    ans2=talk.naive_ask(archii+hardware_template)
    talk.clear()

    print("before")
    print(apa_gong)
    print(archii)
    print(ans1)
    print(ans3)
    print(ans2)
    apa_gong=ans3
    archii=ans2

    dir_cache=load_json_safe("dir_cache.json")
       # return 
    caidan_pool=[]
    caidan=dict([])
    xuanxiang=dict([])
    mul_xuanxiang=dict([])
    val_xuanxiang=dict([])
    bi_xuanxiang=dict([])
    tri_xuanxiang=dict([])
    sub_option=dict([])
    result=dict([]) #Result of the modified options
    result1=dict([])  #Invisible options because subtree is removed
    result2=dict([]) # Originel setting of the modified options
    result_notchange=dict([]) #Options are proposed but not actually modified, because the settings recommended  are the same as the original settings.
    inc=dict([]) #enabled options in proposal
    dec=dict([]) #disabled options in proposal
    pattern = r"^(\d+)\s+(\[\s+\]|\[\*\]|\(.*?\)|\<.*?\>|\({.*?}\)|\-\*\-|\-\-\>)?\s*([A-Za-z].*?)\s*($|\n)"
    pattern1 = r"(.*?)\s+([\[\(\<\{]?(?:on|off|M|\d+|\-\-\>)[\]\)\}\>]?)\s*($|\n)"
    pattern2 = r".*?\(([A-Za-z\_\d\.]+)\)$"
    pattern3 = r"\(\d+\)s*($|\n)" 
    pattern4 = r"\{M\}|\{\*\}"
    pattern5 = r"\<.*?\>"
    pattern6 = r".*?(\d)"
    pattern7 = r"\s*(\[\s+\]|\[\*\]|\(.*?\)|\<.*?\>|\({.*?}\)|\-\*\-|\-\-\>)?\s*([A-Za-z].*?)\s*($|\n)"
    pattern8 = r"\((\d+)\)" 
    pattern9 = r"(.*?)\s*($|\n)"
    pattern10 = r"^(\d+)\s+(\[\s+\]|\[\*\]|\(.*?\)|\<.*?\>|\({.*?}\)|\-\*\-|\-\-\>)?\s*(.*?)\s*($|\n)"
    pattern11 = r".*?\(([A-Za*--z\_\d\.]+)\)\s*\:\s*[\(\[\{\<]?([A-Za-z\_\d\.\-\>]+)[\)\]\}\>]?$"
    pattern12 = r"(\d+)\s+(\[\s+\]|\[\*\]|\(.*?\)|\<.*?\>|\({.*?}\)|\-\*\-|\-\-\>)?\s*([A-Za-z].*?)\s*($|\n)"
    pattern13 = r".*?\(([A-Za*--z\_\d\.]+)\)\s*$"
   

    xuanxing_pre1 = PromptBuilder.xuanxing_pre1(target, target_object)
    xuanxiang_pre2 = PromptBuilder.xuanxing_pre2(target_object, archii, apa_gong)
    xuanxiang_prompt = PromptBuilder.xuanxiang_prompt(target_object)
    caidan_pre11 = PromptBuilder.caidan_pre11(target, target_object, apa_gong)
    caidan_prompt = PromptBuilder.caidan_prompt(target, target_object)
    mul_xuanxiang_prompt = PromptBuilder.mul_xuanxiang_prompt(target, target_object, archii, apa_gong)
    bi_xuanxiang_prompt = PromptBuilder.bi_xuanxiang_prompt(target, target_object)
    tri_xuanxiang_prompt = PromptBuilder.tri_xuanxiang_prompt(target, target_object)
    val_xuanxiang_prompt = PromptBuilder.val_xuanxiang_prompt(target, target_object, archii, apa_gong)

    prompt_set=[xuanxiang_prompt,mul_xuanxiang_prompt,val_xuanxiang_prompt,bi_xuanxiang_prompt,tri_xuanxiang_prompt,xuanxiang_prompt]

  
    next=["",[['root','']]]
   
    wb=0 
    we=we #maximum expansion limit for leaf nodes  
    save_cycle=save_cycle

    br=False
    new = [] #save the one which exists newly: 0:option 1:mul_option 2:value_option 3:bi_option 4:tri_option
    for t in range(5):
        new.append(dict([]))
    count=1
    _,c=menu_config.run("load_config .config_base")

    print('*************de')
    print(de)
    if de==1:
           print('load config:')
           print(c)
         
    menu_config_lock = threading.Lock()
    while True:
          count+=1                
       
          sta,words = menu_config.run("pwd")
          if de==1:
              print("pwd result")
              print(words)
          words_line=words.split('\n')
          for line_t in words_line:
             matches = re.findall(pattern,line_t)
             if len(matches)==0:
                   continue
             match=matches[0]
             if match[1] == '' :
                   caidan[match[2]] = match[0]
             elif match[1] == '-*-': 
                   menu_config.run(f"{match[0]}")
                   _,content = menu_config.run("pwd")
                   match_t=[]
                   lines = content.split("\n")
                   for t in lines:
                          c=re.findall(pattern10 ,t)
                          if len(c)!=0:
                                match_t.append(c.pop())    
                   is_mul_xuanxiang = False
                   sub_name=dict([])
                   for t in match_t:
                             if t[1] == "-->":
                                       is_mul_xuanxiang = True
                             sub_name[t[2]]=t[1]          
                   if is_mul_xuanxiang == True:
                             mul_xuanxiang[match[2]] = sub_name
                   else:
                             caidan[match[2]] = match[0]
                   menu_config.run("up")
                   menu_config.run("pwd")
             elif match[1] == '[ ]':
                   xuanxiang[match[2]] = '[off]'
             elif match[1] == '[*]': 
                   xuanxiang[match[2]] = '[on]'
                   menu_config.run(f"{match[0]}")
                   _,content=menu_config.run("pwd")
                   match_t = re.findall(pattern12,content)
                   dict_t=dict([])
                   if len(match_t)!=0:
                       is_all_option=True
                       for t in match_t:
                             if t[1] != '[ ]' and t[1] != '[*]':
                                       is_all_option=False                                
                             else:
                                       if t[1] == '[ ]':
                                               dict_t[t[2]] = '[off]'
                                       else:
                                               dict_t[t[2]] = '[on]' 

                       if is_all_option == False:
                              caidan[match[2]] = match[0]
                       else:
                              sub_option.update(dict_t)
                   menu_config.run("up")
                   menu_config.run("pwd")                         
             elif re.match(pattern3, match[1]):
                   val_xuanxiang[match[2]] = match[1]
             elif re.match(pattern4, match[1]):
                   bi_xuanxiang[match[2]] = match[1]
             elif re.match(pattern5, match[1]):
                   tri_xuanxiang[match[2]] = match[1]
             else:
                 print("unexpected match:")
                 print(match[1])
                   

         
          if len(caidan) != 0:
                    print(len(caidan))
                    
                 
                    def process_menu_task(caidan_dict):
                     
                        if len(caidan_dict) < 6:
                            print("111")
                            msg = 'The subdirectory of current directory is as follows:\n'
                            inx_tt = {index_t: name_t for name_t, index_t in caidan_dict.items()}
                            

                            def process_sub_dir(i):                                        
                                        name_t = index_tt[i]
                                        
                                       
                                        if name_t in dir_cache:
                                            #print("hit")

                                            return "The sub directory of " + name_t + " is:" + dir_cache[name_t] + "\n"
                                        
                                       
                                        content = ""
                                        talks=Chat()
                                        with menu_config_lock:
                                            menu_config.run(i)
                                            _, content = menu_config.run("pwd")
                                            menu_config.run("up")
                                            menu_config.run("pwd")

                                                                 
                                        ans_dir = talks.naive_ask(content + subinfo_template)                                        
                                        talks.clear()
                                        
                                   
                                        dir_cache[name_t] = ans_dir
                                        return "The sub directory of '" + name_t + "' is:" + ans_dir + "\n"

                                  
                            with concurrent.futures.ThreadPoolExecutor(max_workers=len(index_tt)) as executor_dir:
                                       
                                        results = executor_dir.map(process_sub_dir, index_tt.keys())
                                    
                                  
                            msg += "".join(results)

                            #print(msg)                        
                            words_caidan = "\n".join([f"{index_t} {name_t}" for name_t, index_t in caidan_dict.items()])
                            
                            if de == 1:
                                print("pwd directory")
                                print(words_caidan)
                                t = words_caidan
                            
                            words_caidan = caidan_prompt + words_caidan
                            
                            if de == 1:
                                print("directory answer:")
                            
                            tt = talk.ask(msg + caidan_pre11 + t, 6)
                            ans1 = talk.ask(words_caidan, 6)
                            
                        else:
                            print(222)
                            
                            def process_cycle(while_i, caidan_dict):
                                talkt = Chat()
                                start_index = while_i * 5
                                end_index = (while_i + 1) * 5
                                items1 = list(caidan_dict.items())[start_index:end_index]
                                index_tt = {index_t: name_t for name_t, index_t in items1}
                                msg = 'The subdirectory of current directory is as follows:\n'
                                
                                def process_sub_dir(i):                                        
                                        name_t = index_tt[i]
                                        
                                  
                                        if name_t in dir_cache:
                                            #print("hit")
                                            return "The sub directory of " + name_t + " is:" + dir_cache[name_t] + "\n"
                                        
                                      
                                        talks=Chat()
                                        content = ""
                                        with menu_config_lock:
                                            menu_config.run(i)
                                            _, content = menu_config.run("pwd")
                                            menu_config.run("up")
                                            menu_config.run("pwd")

                                                               
                                        ans_dir = talks.naive_ask(content + subinfo_template)                                        
                                        talks.clear()
                                        
                            
                                        dir_cache[name_t] = ans_dir
                                        return "The sub directory of '" + name_t + "' is:" + ans_dir + "\n"

                                with concurrent.futures.ThreadPoolExecutor(max_workers=len(index_tt)) as executor_dir1:
                                  
                                        results = executor_dir1.map(process_sub_dir, index_tt.keys())
                                    
                                
                                 
                                msg += "".join(results)

                            
                                words_caidan = generate_words_caidan(caidan_dict, while_i)
                                t = words_caidan
                                
                                words_caidan = caidan_prompt + words_caidan
                                print("directory answer:")

                                tt = talkt.ask(msg + caidan_pre11 + t, 6)
                                ans1_part = '\n' + talkt.ask(words_caidan, 6)
                                
                                return ans1_part
                            
                            while_cycle = int((len(caidan_dict) - 1) / 5) + 1
                            
                       
                            
                            with ThreadPoolExecutor(max_workers=while_cycle) as executor:
                                ans1_parts = list(executor.map(
                                    lambda i: process_cycle(i, caidan_dict), 
                                    range(while_cycle)
                                ))                                
                                ans1 = ''.join(ans1_parts)
                        
                        return ans1                   
                    menu_future = None
                    executor_menu = ThreadPoolExecutor(max_workers=1)
    
                   
                    menu_future = executor_menu.submit(process_menu_task, caidan)
                    
                  
                    print("后台任务已提交，主程序继续运行...")
                    
                        

          option_set=[xuanxiang, mul_xuanxiang, val_xuanxiang, bi_xuanxiang, tri_xuanxiang, sub_option]
          
          iter_number=-1          
          new=[dict([]), dict([]), dict([]), dict([]), dict([])]  #0:xuanxiang 1:mul 2:value 3:bi 4:tri
          while True:
                  if len(option_set[0])==0 and len(option_set[1])==0 and len(option_set[2])==0 and len(option_set[3])==0 and len(option_set[4])==0 and len(option_set[5])==0:
                            if len(new[0])==0 and len(new[1])==0 and len(new[2])==0 and len(new[3])==0 and len(new[4])==0:
                                 break
                            else:
                                  for t in range(5):
                                        option_set[t]=new[t]
                                  new=[dict([]), dict([]), dict([]), dict([]), dict([])]
                  iter_number += 1
                  if iter_number == 6:
                         iter_number = 0
                  if len(option_set[iter_number]) != 0:
                         if iter_number==3 or iter_number==4:
                                words_xuanxiang = "\n".join([name for name in option_set[iter_number].keys()])
                                if de==1:
                                               print('iter_number')
                                               print(iter_number)
                                               print("pwd bi/tri option:")
                                               print(words_xuanxiang)
                                words_xuanxiang = prompt_set[iter_number]+words_xuanxiang
                                if de==1:
                                               print("option answer:")
                                        
                                ans2=talk.ask(words_xuanxiang,iter_number)
                         if iter_number==0 or  iter_number==5:
                                 num=len(option_set[iter_number])//10
                                 if len(option_set[iter_number])%10!=0:
                                                num+=1
                                 dic=[]
                                 for i in range(num):
                                       dic.append({})
                                 t=0
                                 for key, value in option_set[iter_number].items():
                                          if len(dic[t])<10:
                                                dic[t][key]=value
                                          else:
                                                t+=1
                                                dic[t][key]=value
                                 
                                 ans2_parts = [""] * num  
                                 option_lock = threading.Lock()  

                                 def process_chunk(i, dic_i, iter_number, de, xuanxing_pre1, xuanxiang_pre2, xuanxiang_prompt, pattern13):
                                             
                                            talk = Chat()
                                            
                                            words_xuanxiang = "\n".join([f"{name}" for name, se in dic_i.items()])
                                            if de == 1:
                                                print('iter_number')
                                                print(iter_number)
                                                print("pwd option:")
                                                print(words_xuanxiang)
                                            
                                            tt1 = words_xuanxiang
                                            words_xuanxiang = xuanxing_pre1 + words_xuanxiang
                                            
                                            if de == 1:
                                                print("option answer:")
                                            
                                            
                                            talk.ask(words_xuanxiang, iter_number)
                                            talk.ask(xuanxiang_pre2+tt1, iter_number)
                                            ans_t = talk.ask(xuanxiang_prompt, iter_number)
                                            
                                            first_try = 1
                                            while True:
                                                lines = ans_t.split('\n')
                                                check = False
                                                check1 = True
                                                for line in lines:
                                                 
                                                    if line == "increase:" or line == "Increase:" or line == "decrease:" or line == "Decrease:":
                                                        pass
                                                    elif line:
                                                        if line.startswith("- "):
                                                            line = line[2:]
                                                        res = re.findall(pattern13, line)
                                                        if len(res) == 1:
                                                            check = True
                                                
                                                if check == False:
                                                    talk.last_step(iter_number, first_try)
                                                    if de == 1:
                                                        print(f'name is uncompleted, retry {first_try}')
                                                    ans_t = talk.ask('the name that your output is uncompleted,format:name(xx), please output complete name,retry:', iter_number)
                                                    first_try += 1
                                                    if first_try < 5:
                                                        continue
                                                
                                                processing_increase = False
                                                processing_decrease = False
                                                inc_t = {}
                                                dec_t = {}
                                                for line in lines:
                                                    line = line.strip()
                                                  
                                                    if line == "increase:" or line == "Increase:":
                                                        processing_increase = True
                                                        processing_decrease = False
                                                    elif line == "decrease:" or line == "Decrease:":
                                                        processing_increase = False
                                                        processing_decrease = True
                                                    elif line:
                                                        if line.startswith("- "):
                                                            line = line[2:]
                                                        res = re.findall(pattern13, line)
                                                        if len(res) != 0:
                                                            if line not in tt1:
                                                                if de == 1:
                                                                    print(f'The case inconsistency, retry {first_try}')
                                                                    print("check1")
                                                                    print(line)
                                                                    print(tt1)
                                                                talk.last_step(iter_number, first_try)
                                                                ans_t = talk.ask('The case inconsistency, please output the result with consistent case. Output must be consistent with ' + tt1 + ". Now output again", iter_number)
                                                                first_try += 1
                                                                check1 = False
                                                                break
                                                            
                                                            if processing_increase:
                                                                inc_t[line] = '[on]'
                                                            elif processing_decrease:
                                                                dec_t[line] = '[off]'
                                                
                                                if check1 == False and first_try < 5:
                                                    continue
                                                if (check == True and check1 == True) or first_try >= 5:
                                                    break
                                            
                                            
                                            part_ans = "\n".join([f"{name} {se}" for name, se in inc_t.items()])
                                            part_ans += "\n"
                                            part_ans += "\n".join([f"{name} {se}" for name, se in dec_t.items()])
                                            
                                          
                                            with option_lock:
                                                inc.update(inc_t)
                                                dec.update(dec_t)
                                                ans2_parts[i] = part_ans
                                            
                                            return part_ans

                              
                                 with ThreadPoolExecutor() as executor:
                                        futures = []
                                        for i in range(num):                                          
                                            futures.append(
                                                executor.submit(
                                                    process_chunk, 
                                                    i, 
                                                    dic[i], 
                                                    iter_number, 
                                                    de, 
                                                    xuanxing_pre1, 
                                                    xuanxiang_pre2, 
                                                    xuanxiang_prompt, 
                                                    pattern13
                                                )
                                            )
                                        
                                      
                                 for future in as_completed(futures):
                                            future.result()  

                                    
                                 ans2 = ""
                                 for i in range(num):
                                        ans2 += ans2_parts[i]
                                        if i != num - 1:
                                            ans2 += "\n"
                                 
                                 
                                 if de==1:
                                       print("total option answer mul:")
                                 print(ans2)

                                 
                         if iter_number==1:
                                 words_xuanxiang=""
                    
                                 for name,item in option_set[iter_number].items():
                                         words_xuanxiang += "\n".join([name for name in item.keys()]) 
                                         words_xuanxiang +='\n///\n'
                                 words_xuanxiang=words_xuanxiang[:-5]
                                 if de==1:
                                        print('iter_number')
                                        print(iter_number)
                                        print("pwd option:")
                                        print(words_xuanxiang)
                                 words_xuanxiang = prompt_set[iter_number]+words_xuanxiang

                                 if de==1:
                                      print("option answer:")
                                 ans2=talk.ask(words_xuanxiang,iter_number)

                                 mat1=re.findall(pattern9,ans2)
                                 ans2=""
                                 for i, m in enumerate(mat1):
                                         if i != len(mat1) - 1:
                                              ans2+=f"{m[0]} -->\n"
                                         else :
                                              ans2+=m[0]
                                 print("mul answer")
                                 print(ans2)  
                         if iter_number==2:
                                words_xuanxiang = "\n".join([f"{name} {item}" for name,item in option_set[iter_number].items()])
                        
                                if de==1:
                                        print('iter_number')
                                        print(iter_number)
                                        print("pwd option:")
                                        print(words_xuanxiang)
                                help_info=""
                                for name,_ in option_set[iter_number].items():
                                         t = re.findall(pattern2, name)
                                         if len(t)==0:
                                                 continue
                                         name_t = t[0] 
                                         with menu_config_lock:                                 
                                                   _,he=menu_config.run(f"{name_t}")
                                         help_info+=he+"\n"
                                words_xuanxiang = "Here is value options information:"+help_info+prompt_set[iter_number]+words_xuanxiang

                                if de==1:                                      
                                        print("option answer:")
                                ans2=talk.ask(words_xuanxiang,iter_number)
                               
                                

                         ans2_filter = re.findall(pattern1,ans2)
                         
                                                                           
                         remove=set({})
                         for match in ans2_filter:
                              if match[0] in remove:
                                  continue   
                              unchanged=False      
                                              
                              if iter_number in [0,2,3,4,5]:  #when the recommodation is similar to the origin
                                   if  match[0] not in option_set[iter_number]:
                                             print('key error:')
                                             print(option_set[iter_number])
                                             print(match[0])
                                             continue    
                                   if option_set[iter_number][match[0]]== match[1]:
                                                 result_notchange[match[0]] = match[1]
                                                 unchanged=True   
                                   else:
                                           result2[match[0]] = option_set[iter_number][match[0]]                 
                                              
                              elif  iter_number in [1] :
                                   for mul in option_set[iter_number].values():
                                          if match[0] in mul and mul[match[0]]==match[1]:
                                                unchanged=True   
                                                result_notchange[match[0]] = match[1]
                                          if match[0] in mul and mul[match[0]]!=match[1]:
                                                 result2[match[0]] = mul[match[0]]   

                              if unchanged==False:
                                  t = re.findall(pattern2, match[0])
                                  if len(t)==0:
                                      continue
                                  name_t = t[0]
                                  with menu_config_lock:
                                          _, vis = menu_config.run(f"vis {name_t}")
                                  t = re.findall(pattern6, vis)    
                                  if len(t)==0:
                                      print('vis name error')
                                      continue
                                  visibility_t = t[0]
                                  if visibility_t == "1":
                                      print(f"visible is 1: {name_t}")

                                  if visibility_t == "0":
                                      print(f"visible is 0: {name_t}")
                                      result1[match[0]] = match[1]
                                    
                                  if visibility_t == "2" or visibility_t == "1":     #only when visible                     
                                       result[match[0]] = match[1]
                                       with menu_config_lock:
                                                if iter_number in {0, 1, 3, 4, 5} and match[1] in {'[on]','-->'}:     
                                                            menu_config.run(f"write {name_t} y")
                                                elif iter_number in {0, 3, 4, 5} and match[1]=='[off]':  
                                                            menu_config.run(f"write {name_t} n")
                                                elif iter_number ==4 and match[1]=='M':     
                                                            menu_config.run(f"write {name_t} m")
                                                elif iter_number ==2:
                                                            t = re.findall(pattern8,match[1])  
                                                            menu_config.run(f"write {name_t} {t[0]}")
                                                _, option_state = menu_config.run("get_last_changes") #option_state:[0->2, 2->0]
                                      
                                       if de==2:
                                             print("option_state0")
                                             print(option_state[0])
                                             print("option_state1")
                                             print(option_state[1])
                                             print("option_state2")
                                             print(option_state[2])
                                             print("option_state3")
                                             print(option_state[3])

                                       if de==1:
                                             print("option_state2")
                                             print(option_state[2])
                                             print("option_state3")
                                             print(option_state[3])
                                       for option in option_state[0]:
                                           mat_t = re.findall(pattern7, option)
                                           mat_t = mat_t[0]
                                           if mat_t[0] == '[ ]':
                                                 new[0][mat_t[1]] = '[off]'
                                           elif mat_t[0] == '[*]':
                                                 new[0][mat_t[1]] = '[on]'                                      
                                           elif re.match(pattern3, mat_t[0]): #value
                                                 new[2][mat_t[1]] = mat_t[0]                                                 
                                           elif re.match(pattern4, mat_t[0]):
                                                 new[3][mat_t[1]] = mat_t[0]
                                           elif re.match(pattern5, mat_t[0]):
                                                 new[4][mat_t[1]] = mat_t[0]
                                           else:  
                                               pass     
                                       for option in option_state[1]:
                                           mat_t = re.findall(pattern7, option)
                                           mat_t = mat_t[0]
                                           remove.add(mat_t[1])
                                           if mat_t[0] == '[ ]' or mat_t[0] == '[*]':
                                                 if mat_t[1] in option_set[0]:
                                                     del option_set[0][mat_t[1]] 
                                                 if mat_t[1] in new[0]:
                                                     del new[0][mat_t[1]]
                                                 if mat_t[1] in option_set[5]:
                                                     del option_set[5][mat_t[1]]
                                           elif re.match(pattern3, mat_t[0]): #value
                                                 if mat_t[1] in option_set[2]:
                                                     del option_set[2][mat_t[1]]
                                                 if mat_t[1] in new[2]:
                                                     del new[2][mat_t[1]]
                                           elif re.match(pattern4, mat_t[0]):
                                                 if mat_t[1] in option_set[3]:  
                                                     del option_set[3][mat_t[1]]
                                                 if mat_t[1] in new[3]:
                                                     del new[3][mat_t[1]]
                                           elif re.match(pattern5, match[0]):
                                                 if mat_t[1] in option_set[4]:
                                                     del option_set[4][mat_t[1]]
                                                 if mat_t[1] in new[4]:
                                                     del new[4][mat_t[1]]
                                           else:
                                               pass  
                                                                          
                                       for option in option_state[2]:
                                                            mul_name=''
                                                            sub_name=dict([])
                                                            words_line= option.split('\n')
                                                            for line_t in words_line:
                                                                            matches = re.findall(pattern7,line_t)
                                                                            if len(matches)==0:
                                                                                continue
                                                                            match=matches[0]
                                                                            if match[0]=='-*-':
                                                                                   mul_name=match[1]
                                                                            else:
                                                                                   sub_name[match[1]]=match[0]
                                                            if len(sub_name)!=0:
                                                                      new[1][mul_name] = sub_name
                                                                      if de==1:
                                                                                    print('option_state2:subname')
                                                                                    print(sub_name)                                                   

                                       for t in option_state[3].keys():
                                                          t = re.findall(pattern7, t)
                                                          t=t[0]
                                                          if t in option_set[1]:
                                                                for j_t in option_state[3].values():
                                                                      j_t  = re.findall(pattern7, j_t)
                                                                      j_t =j_t[0]   
                                                                      if j_t in  option_set[1][t]:
                                                                                 del option_set[1][t][j_t]
                                                          if t in new[1]:
                                                                for j_t in option[t]:
                                                                      j_t  = re.findall(pattern7, j_t)
                                                                      j_t =j_t[0]  
                                                                      if j_t in new[1][t]:
                                                                                 del new[1][t][j_t]

                                                
                         option_set[iter_number]=dict([])                


          if 'menu_future' in locals() and menu_future:
                                print("waiting...")
                       
                                ans1 = menu_future.result()
                                executor_menu.shutdown()
                                menu_future = None
                                print('***')
                                print(ans1)
                                
                               
                                with menu_config_lock:
                                    menu_config.run("pwd")
                                
                                caidan = dict([])
                                mem = next[1]
                                
                               
                                words_line = ans1.split('\n')
                                for line_t in words_line:
                                    matches = re.findall(pattern, line_t)
                                    if len(matches) == 0:
                                        continue
                                    match = matches[0]
                                    mem_t = mem.copy()
                                    mem_t.append([match[2], match[0]])
                                    caidan_pool.append([match[2], mem_t])

          if len(caidan_pool)==0:
              br=True
          else: 
              cond = True
              up_type=0
              while cond:              
                            if up_type==0:
                                        le=len(next[1])
                                        if le>1:
                                                for i in range(le-1):
                                                        menu_config.run("up")
                                        if de==1:
                                            print("up finish")
                            else:
                                      for j in range(i):
                                            print(next[1][j])
                                      for j in range(i-1):
                                            menu_config.run("up")
                                      if de==1:
                                              print("not exit: up finish")
                                      up_type=0
                            if len(caidan_pool)==0:
                                    br=True
                                    break

                            next=caidan_pool.pop()
                            if de==1:
                                print("go into next directory")
                                print(next)
                            i=0
                            leng=len(next[1])
                            for action in next[1]:
                                i+=1
                                if action[0]=="root":
                                            continue
                                _,con=menu_config.run("pwd")
                               
                                t=[]
                                ok=False
                                
                                words_line=con.split('\n')
                                for line_t in words_line:
                                       matches = re.findall(pattern,line_t)
                                       if len(matches)==0:
                                              continue
                                       match=matches[0]                                
                                       if match[2]==action[0]:  
                                                sta,_=menu_config.run(match[0])
                                                if de==1:
                                                    print("actual number")
                                                    print(match[0])
                                                    print("mem number")
                                                    print(action[1])
                                                    
                                                if sta==False:
                                                    print("error")
                                                    print(_)
                                                    break
                                                else:
                                                    ok=True                                                
                                                    break
                                
                                if ok==False:
                                        break
                            if ok== True and i==leng:
                                        cond = False
                            if ok==False:
                                    print("option does not exit anymore:")
                                    _,con=menu_config.run("pwd")
                                    print(con)
                                    up_type=1


          if sta==False:
                print("error,exit!")
                break

          wb+=1

          if wb%save_cycle==0 or br==True or wb==we:
                
                 with open(f"outputt_myconfig_{iter_count}.txt", "w") as file:     #Result of the modified options
                         for key, value in result.items():
                                    file.write(f"{key}: {value}\n")
                 file.close()
                 with open("output1.txt", "w") as file:    
                           for key, value in result_notchange.items():
                                    file.write(f"{key}: {value}\n")
                 file.close()
                 with open("output2.txt", "w") as file:
                           for key, value in result2.items():
                                    file.write(f"{key}: {value}\n")
                 file.close()
                 with open("inc.txt", "w") as file:
                           for key, value in inc.items():
                                    file.write(f"{key}: {value}\n")
                 file.close()
                 with open("dec.txt", "w") as file:
                           for key, value in dec.items():
                                    file.write(f"{key}: {value}\n")
                 file.close()

          if br==True:
              with open('dir_cache.json', 'w', encoding='utf-8') as f:
                          json.dump(dir_cache, f, ensure_ascii=False, indent=4)

          if wb==we:
              print("up to iteration limit")
              break

          if br==True:
              print("finish iteration ")
              break

          xuanxiang=dict([])
          mul_xuanxiang=dict([])
          val_xuanxiang=dict([])
          bi_xuanxiang=dict([])
          tri_xuanxiang=dict([])
          sub_option=dict([])

          time.sleep(0.1)
    
       
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"add: {sys.argv[0]} <Current Turn> ")
        sys.exit(1)

    iter_count = sys.argv[1]
    
    print(f"iter_count: {iter_count}")

   
    fire.Fire(main)
  
