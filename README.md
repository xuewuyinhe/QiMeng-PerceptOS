# **QiMeng-PerceptOS**：Semantic-Aware Kernel Optimization for OS-Intensive Workloads via Hardware-Software Alignment

**Authors**: Huilai Chen, Yuanbo Wen, Liangfeng Li, Shaohui Peng, Jingzhe Zhu, Jun Bi,  Xuzhi Zhang, Qi Guo, Ling Li, Yunji Chen


---

QiMeng-PerceptOS is the successor to AutoOS by the same team. Whereas AutoOS performs heuristic static general tuning of Linux kernel compile-time configurations, QiMeng-PerceptOS enables deep semantic-aware tuning tailored to specific workloads(especially when the workload is new and has no documents). This work shifts the optimization paradigm of large models from static open-loop to semantically aware closed-loop, delivering targeted software performance gains. Critically, unlike conventional methods that rely solely on numerical feedback (e.g., performance metrics), QiMeng-PerceptOS prioritizes semantic signals.
**Our work has been published at ICML 2026.**.



## Requirements
- Linux kernel source code 
- Python 3.10+
- `.config` file from your OS distribution for initial configuration
- LLM API key: You can use GPT-4o-mini for its fast speed, low cost, and solid performance .
  
## Quick start
0. Make sure you can replace the configuration of the OS by mannual in your environment. 
1. Inspect the Linux kernel version and .config file of the OS distribution that needs optimization.
2. Prepare the corresponding Linux version's source code repository. Then, clone and download this project, placing all files within the Linux kernel source repository.
   ```bash
   git clone [insert link to Linux kernel source repository]
   cd linux
   git clone [this project]
   mv QiMeng-PerceptOS/perceptos/* ./
   
3. Copy the .config file from the OS distribution that needs optimization to the Linux version's source code repository, then change the name  using the command below:
   ```bash
   cp .config .config_base
   cp .config_base files/myconfig
   
   
4. Init the environment
   
   The init_env.sh is as follows:
   ~~~bash
   export srctree=.
   export CC=gcc
   export LD=ld
   export ARCH=x86
   export SRCARCH=x86
   ~~~
   Modify the ARCH and SRCARCH variable to your architecture name. Make sure that your architecture name matches the architecture name in the Linux source code. You can use the following command to view all supported architecture names in the Linux source code
   ~~~bash
   ls arch/
   ~~~
   put your openai url and openai key in key.txt (two lines), then init the environment using the command below:
   ~~~bash
   source ./init_env.sh
   ~~~

5. Run the following commands 
   Run python3 hardware_info/arch.py , then save the hardware information to hardware.txt in the current linux/ directory.
   Run the call stack parsing script, then place the generated xx.perf file under the current linux/ directory. For details, please refer to test_commands.txt. Example: 
   ~~~bash
   source ab_perf.sh
   ~~~
    
   
6. Run:
   
   Use the command below，where <round> should be iterated from 1 to 13.
   ~~~bash
   python3 perceptos.py <round>
   ~~~
   When first run it, the error message will appear as follows:
   ~~~bash
   kconfiglib.KconfigError: kernel/module/Kconfig:4: error: couldn't parse 'modules': unrecognized construct
   ~~~
   To disable module functionality, delete the problematic code located under kernel/module/Kconfig (The place is according to the message). The code to remove is as follows:
   ~~~bash
   menuconfig MODULES
              bool "Enable loadable module support"
              modules
              help
                Kernel modules are small pieces of compiled code which can
                be inserted in the running kernel, rather than being
                permanently built into the kernel.  You use the "modprobe"
                tool to add (and sometimes remove) them.  If you say Y here,
                many parts of the kernel can be built as modules (by
                answering M instead of Y where indicated): this is most
                useful for infrequently used options which are not required
                for booting.  For more information, see the man pages for
                modprobe, lsmod, modinfo, insmod and rmmod.
      
                If you say Y here, you will need to run "make
                modules_install" to put the modules under /lib/modules/
                where modprobe can find them (you may need to be root to do
                this).
      
                If unsure, say Y.
    ~~~
    Then use  the command below again to start one global search:
    ~~~bash
    python3 perceptos.py <round>
    ~~~
7. Generate new config files using the command below, where the round here must be same as step 6:
    ~~~bash
    ./gen.sh <round>
    ~~~
    The newly generated configuration file is located at ./files/myconfig
    After the program runs in step7, it will prompt you to input whether the performance of this test has improved compared to the historical best. Enter up if it has improved, or down if not after step 9.  At this point, proceed to Step 8.
 
8. Using the following command, load the newly generated ./files/myconfig file, and then save it as ./.config in the current directory.
    ~~~bash
    menuconfig ARCH=x86 (change riscv to the arch you use) 
    ~~~
9. Compile and install a new OS with the new config， then evaluate it using benchmark of the software, For details, please refer to test_commands.txt. Then results in  program running in step7
    

10. If the current performance exceeds the historical best, go back to Step 5; otherwise, proceed directly to Step 6. Then, begin the second iteration of the global search sequentially.
Steps 5-10 or 6-10 constitute a single search, with 13 searches recommended. If the generated OS fails to boot, you can return the errors and modified options to your LLM for identification. If not successful, use a binary search to identify the problematic option . Remember the previously identified options(save them into the boot variable in append.py) and filter out those in subsequent generated configurations autimatically（Empirically, the number of incorrectly configured options in the first search iteration typically ranges from 0 to 7, while errors in subsequent iterations are largely repetitive.）.  The modified options in one search is in ./output.txt  generated after running gen.sh. Remove the the problematic options in output.txt and run append.py again to generated a viable OS configuration.

11. After completing the 13 search iterations, run fusion.py <round> for 2 rounds of posterior enhancement, with <round> set to 0 and 1, respectively.
The generated configuration files are located in files/myconfigfusion0 and files/myconfigfusion1, respectively. Then test the  configuration files like step 8-9.

You can use the above commands according to your own environment to write a shell script that fully automates the process of searching, compiling, installing and testing.

## Citation
If you are using our framework or code for your project , please cite the following paper:
~~~
blank
~~~
