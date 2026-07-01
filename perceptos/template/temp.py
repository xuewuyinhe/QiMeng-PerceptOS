class PromptBuilder:    
    
    @staticmethod
    def stack_template():       
        return '''This is my program's call stack. I now want to use an LLM to modify menuconfig configurations to optimize the program's throughput. Therefore, I need to first remove redundant information from this call stack to reduce the number of tokens and minimize context. Please organize the call stack information according to the following guidelines:

1 Library function compression: [xx];[xx]->[xx]×2

2 Framework boundary truncation: python3;[...10 Python internal functions, details irrelevant for OS optimization...];[onnxruntime.so] →py3;[critical detail];[onnxrt.so]

3 Similar call stack merging: Thread 1: python3;abc;__xxx 100 & Thread 2: python3;abc;__yyy 200 → python3;abc;__xxx (100) | __yyy (200)

4 Abbreviation for frequently occurring common words: When every call stack starts with python3, specify py3: python3 at the very beginning, then change the start of each subsequent call stack to py3. (Note: This is an example. Apply this to any other frequently occurring words that can be abbreviated without causing confusion.)

5 For numbers with suffixes like 'k' at the end of call stacks, use abbreviations to reduce token usage.

6 Retain keywords crucial for identifying bottlenecks and system status, ensuring precise localization even after significant trimming.

7 remove [unknown],  simplify overly long function names.

8 "Retain" the critical sys call path and essential details for each operation

Please now output the call stack adhering to the above criteria.
Example 1
Before processing:

text
python3;[unknown];[onnxruntime_pybind11_state.cpython-310-x86_64-linux-gnu.so];[unknown];[onnxruntime_pybind11_state.cpython-310-x86_64-linux-gnu.so];read;entry_SYSCALL_64_after_hwframe;do_syscall_64;x64_sys_call;__x64_sys_read;ksys_read;vfs_read;ext4_file_read_iter;generic_file_read_iter;filemap_read;copy_page_to_iter;_copy_to_iter 20929292720
After processing:

text
py3;[onnxrt.so];sys_read;vfs_read;ext4_read_iter;generic_file_read_iter;filemap_read;copy_to_iter 20.9G
Processing explanation:

Applied principle 2: Truncated Python interpreter internals, directly targeting ONNX Runtime library

Applied principle 4: Simplified python3 to py3, onnxruntime... to onnxrt.so

Applied principle 5: Number abbreviated to 20.9G

Example 2
Before processing:

text
python3;[unknown];[onnxruntime_pybind11_state.cpython-310-x86_64-linux-gnu.so];[unknown];[unknown];[unknown];_mid_memalign.isra.0;_int_memalign;[onnxruntime_pybind11_state.cpython-310-x86_64-linux-gnu.so];__memmove_avx512_unaligned_erms 22595959370
After processing:

text
py3;[ort.so];_mid_memalign;_int_memalign;memmove_avx512_unalignederms 22.6G
Processing explanation:

Applied principle 7: remove multiple [unknown] representations

Applied principle 2: Focused on ONNX Runtime library boundary

Applied principle 6: Preserved memory allocation and memory movement key operations

Applied principle 5: Number abbreviated to 22.6G

Removed redundant .isra.0 and other compiler-generated symbols

These two examples demonstrate how to significantly reduce token count through compress.

Now first analyze and output directly without other words:'''
    
    @staticmethod
    def hardware_template():
        return '''Now you need to compress the arch info concisely to reduce the number of tokens . Please apply: 1) Hierarchy summarization 2) Value range merging 3) Category grouping. Express in a few concise lines.
Ensure clarity. Output directly in brief English without other words: '''
    
    @staticmethod
    def subinfo_template():
        return '''This is the information from the subdir, which I need to input as context for the LLM. Currently, it's taking up too many tokens, so I want to reduce the information. Now, please keep only the directory descriptions, remove the serial numbers, statuses, and the names inside (). Then, based on the directory descriptions, create a concise summary without including the status, using a few lines to briefly describe it, with fewer tokens. Now, please output summary directly.'''
    
    @classmethod
    def xuanxing_pre1(cls, target, target_object):
        return f" For {target}  , analyze each of the following settings separately to determine whether they will increase or decrease {target_object} if the setting(the following settings) is enabled:"
    
    @classmethod
    def xuanxing_pre2(cls, target_object,archii,apa_gong):
        return f"I will give you the top 20 hot call stacks obtained from the perf program.Based on the stacks , analysis and experience above, provide the options that could potentially affect {target_object} and analyse whether enabling the  settings will increase or decrease {target_object} while ensure successfully booting up os after modification.Analyze while considering the hardware I use."+archii+".The stacks are follows:"+apa_gong+"The options are:"
    
    @classmethod
    def xuanxiang_prompt(cls, target_object):
        return f"According to the above analysis,for the options that could potentially impact {target_object} , determine whether each option will increase or decrease {target_object}, Output format: 'increase: \n Option Name1 \n Option Name2 \n  decrease: \n Option Name1 \n Option Name2'. No explation, no extra useless words. \
    For example，when related option is： IO Schedulers (IOS) \n  DYNAMIC_DEBUG(DD)   \n, the analysis is that IO Schedulers (IOS)   will increase the score and  DYNAMIC_DEBUG(DD)   will decrease the score   your answer : 'increase: \n IO Schedulers (IOS) \n  decrease: \n DYNAMIC_DEBUG(DD)  \n.Output complete name ,for example,output 'IO Schedulers (IOS) ',do not output 'IOS ' only! Complete name is important,you need attention. In the output, the assessment of enabling each option should align with the previous analysis, indicating whether it will increase or decrease {target_object}.\
    Do not mention reason.Do noy output options about Peripheral drives, just ignore.And skip the options which may lead to boot failure. The option names should maintain consistent capitalization!!!.  Please obey the rules. Output complete name as I said .please  output:"
    
    @classmethod
    def caidan_pre11(cls, target,target_object, apa_gong):
        return f"I want to explore the configuration of the Linux kernel's 'config' to {target}. I will give you the top 20 hot call stacks obtained from the perf program."+apa_gong+f"I will sequentially show you each level of menuconfig's directories, and I need you to tell me which directories(Do not tell me sub directories,only the father directories)  are possibly related to {target_object}  based on your existing knowledge.\
    Here's how I'll show you the directories which is in some level in menuconfig:\n  [number] [directory name] \n, please analyze."

    @classmethod
    def caidan_prompt(cls, target, target_object):
        return f"I want to explore the configuration of the Linux kernel's 'config' to {target}. I will sequentially show you each level of menuconfig's directories, and I need you to tell me which directories are possibly related to {target_object}  based on the previous conversiation.\
    Here's how I'll show you the directories which is in some level in menuconfig:\n  [number] [directory name] \n  \
    Your response format: \n For relevant directories: [number] [directory name] \n \
    For example，when I give:0 memory setting(mem) \n  1 computer name(Name) \n   your answer :' 0 memory setting(mem) \n' because the memory setting is related to {target} but the name is not. \n \
    The name in the response should be complete, which is the same as I gave you; for example, if the menu name is ‘IP: TCP syncookie support (SYN_COOKIES)’, it should not only show ‘TCP syncookie support (SYN_COOKIES)’, it must show ‘IP: TCP syncookie support (SYN_COOKIES)’. \n \
    No extra explanations needed. Do not recommend any directory related to Soc selection,device driver, platform type  directories.\
    Do not mention reason.When the number of directory is one,do not output sub directory.Please obey the rules.Here are some directories,please  recommend:"

    @classmethod
    def mul_xuanxiang_prompt(cls, target, target_object,archii,apa_gong): 
        return f"I'm exploring the Linux kernel's menuconfig for configurations to {target}. I will give you the top 20 hot call stacks obtained from the perf program."+apa_gong+"Analyze while considering the hardware I use."+archii+f"Here are  multiple 'select one option' choices in menuconfig. Please select one suitable option at a time to potentially {target_object}. My format:\n [option1 name] \n  \ [option2 name] \n  ..  \n  Your response format: \n '[recommended option name]\n' \n \
    for example:  when I give: 'reveive buffer（rbuf）  \n log buffer(lbuf) \n /// \n  CPU schedule(cs) \n  CPU  default(cd) \n /// \n SLAB (SLAB) \n SLUB (Unqueued Allocator) (SLUB)'. This means there are three   'select one option' choices, and considering to {target} ,your answer is :receive buffer(rbuf)\n CPU schedule(cs) \n SLUB (Unqueued Allocator) (SLUB)\n  \
    Remember to choose the recommended setting to possibly {target_object} for each option: No extra explanations needed. Only suggest options which may be related. \
    Do not mention reason.Output complete name ,for example,output 'CPU schedule(cs)',do not optput 'cs' only! Complete name is important,you need attention.Please obey the rules. Here are some  'select one option' choices,please choose:"  

    @classmethod 
    def bi_xuanxiang_prompt(cls, target, target_object): 
        return  f"I'm exploring the Linux kernel's menuconfig for configurations that might {target}. \
    Here are  multiple binary choice options in menuconfig. There are two settings for an option: 'M' or 'on', which ‘M’ means configuring this option as a module and 'on' means compiling this option into the kernel image to make it a part of the kernel. .Please set the  options at a time to potentially {target_object}. My format:\n [option name]   \n  Your response format: \n [option name]  {{M or on}}\n \
    for example:  when I give: 'reveive buffer(rbuf) \n log buffer(lbuf)\n ',your answer is 'receive buffer(rbuf) {{on}} \n log buffer(lbuf) {{M}}' \n  \
    Remember to  recommend settings to possibly {target_object} for each option: No extra explanations needed. Only suggest options which may be related. \
    Do not mention reason. Please obey the rules. Here are some binary choice options ,please  recommend:"
   
    @classmethod
    def tri_xuanxiang_prompt(cls, target, target_object):   
        return f"I'm exploring the Linux kernel's menuconfig for configurations that might {target}. \
    Here are  multiple ternary choice options in menuconfig. There are three settings for an option: 'M' ，'on' or 'off', which ‘M’ means configuring this option as a module , 'on' means compiling this option into the kernel image to make it a part of the kernel. and 'off' means disabling this option, not compiling it as a kernel component.Please set the  options at a time to potentially {target_object}. My format:\n [option name]   \n  Your response format: \n [option name]  <M or on or  off>\n \
    for example:  when I give: 'reveive buffer(rbuf)  \n log buffer(lbuf) \n Debug Filesystem(DFile) ',your answer is 'receive buffer(rbuf) <on> \n  log buffer(lbuf) <M> \n Debug Filesystem(DFile) <off>'   \n  \
    Remember to  recommend settings to possibly {target_object} for each option: No extra explanations needed. Only suggest options which may be tie to {target_object}. \
    Do not mention reason. Please obey the rules. Here are some ternary choice options ,please  recommend:"
    
    @classmethod
    def val_xuanxiang_prompt(cls, target, target_object,archii,apa_gong):   
        return f"I'm exploring the Linux kernel's menuconfig for configurations that might {target}. I will give you the top 20 hot call stacks obtained from the perf program."+apa_gong+"Analyze while considering the hardware I use."+archii+f"Here are  multiple numeric  options in menuconfig.I have given you the range of each option value in the information above. Please set the  options at a time to potentially {target}. \
    If the option is not rellated to {target_object}, then remain the defalut value. \n My format:\n  [option name] (default value)  \n  Your response format: \n [option name] (recommended  value)   \n \
     for example:  when I give: 'maximum CPU number(1=>2 2=>4)  (cpunum) (1)',your answer is 'maximum CPU number(1=>2 2=>4)  (cpunum) (2)'   . Because  when the CPU number is more, the speed is usually better.\n \
    Remember to  recommend settings to possibly {target_object} for each option: No extra explanations needed. Only suggest options which maybe {target_object}. \
    Do not mention reason. Do not add units near number in the output.Please obey the rules. Here are some numeric options ,please  recommend: "














