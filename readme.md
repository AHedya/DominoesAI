# DominoAI - DomA
![einstein in coffee shpo](https://github.com/user-attachments/assets/333d9f76-3f9e-493d-a3ef-5e812d0d9149)

## 1. About the Project
This Python-based project is a game engine of the classic domino , allowing players to challenge a sophisticated AI opponent. The AI comes equipped with four distinct strategies:
  1. Rule-Based
  2. Monte Carlo Tree Search (MCTS)
  3. Blind
  4. Alpha-Beta Pruning(:warning: not implemented yet)
   
Users can customize the parameters of each algorithm to modify the AI’s behavior and tailor the difficulty or strategic depth of the game.
The project supports both casual and analytical gameplay, you can let AI compete with another AI.

## 2. Getting started :rocket: 
First install requirements. Not much, numpy and colorama mainly. You can reproduce same results using `environment.yml` file.

 ```bash
 conda env create -f environment.yml
```
or 
 ```bash
 pip install numpy colorama pyyaml python-dotenv
```

activate generated environment (in case using `conda env create`) 
 ```anaconda
 conda activate Domino_ai
```

change working directory to /src
 ```bash
 cd ./src
```

Now run the package
 ```bash
 python -m domino_ai
```
![image](https://github.com/user-attachments/assets/4ec29390-6097-45f6-b63f-a0f474117c65)

:x: Don't change terminal size after running the script, it might corrupt view.

### configuration 
You can configure game through `src/config.yaml` file, or you can over-write it using arg parser
Example:
 ```bash
 python -m domino_ai --score 151 --strategy mcts
```

### AI configuration 
You can control algorithms hyper-parameters through `src/domino_ai/ai/hyper_parameters.yaml` file

## 3. AI algorithms
**MCTS**: sophisticated algorithm balancing between exploraion and exploitation, through the parameter `C`. This implementation differes alot from the original one, due to the nature of uncertaininty in domino
:warning: current implementation emphsizes only lowering the value of computer hand.
:x: it's not supported in AI-to-AI matches. it's hard-coded to evaluate `second-player hand` in each state.

**RULE-BASED**: Classic algorithm, giving score to each placible tile based on some criterias( pips count, double, blocking potential ... ).
You can control how aggressive or defencive the algorithm is by modifing `src/domino_ai/ai/hyper_parameters.yaml` file

**BLIND**: nothing smart about it, just choose random possibe tile.

**LLMs**: Large Language Models are tested to play domino, The task of playing domino relies mainly on reasoning,so. The better the model is in reasoning, the better it is in playing domino. Notebooks are provided to test LLMs, either through `google genai api` or `ollama` if local development.
:warning: using LLMs to play domino is an insane idea, the cost will be massive, so didn't bother add this feature, alghough it's quite easy.

**Alpha-Beta prunning**: :o: Not implemented yet


## 4. GUI
:warning: is currently under developement 
![domino_gui_pic](https://github.com/user-attachments/assets/e7751286-7c19-4ad6-8afa-c7abbc40fc91)

## 5. Future plans
 1. GUI
 2. alpha-beta pruning
 3. reverse play feature
 4. multiplayer
 
 ## 6. Notes
 :warning: project is still under developement
 
 :warning: some code snippets need refactoring
 
