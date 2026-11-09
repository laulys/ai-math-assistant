# Records docs/demo.gif with VHS (https://github.com/charmbracelet/vhs).
# Run from the repo root, with Ollama running:  vhs docs/demo.tape

Output docs/demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 720
Set Padding 24
Set Theme "Catppuccin Mocha"
Set TypingSpeed 45ms
Set PlaybackSpeed 1.5

# Setup (not recorded): activate the venv and use a simple prompt.
# Tip: ask the assistant one question first so the model is already loaded.
Hide
Type "source .venv/bin/activate && export PS1='$ ' && clear"
Enter
Sleep 2s
Show

Type "python -m math_assistant"
Sleep 500ms
Enter
Wait+Screen@30s /You:/
Sleep 1s

Type "Add 25 and 15, then multiply by 2"
Sleep 500ms
Enter
Wait+Screen@120s /Assistant:[\s\S]*You:/
Sleep 3s

Type "¿Cuánto es 2 elevado a 10?"
Sleep 500ms
Enter
Wait+Screen@120s /Assistant:[\s\S]*Assistant:[\s\S]*You:/
Sleep 3s

Ctrl+L
Type "What is the population of Canada? Multiply it by 0.75"
Sleep 500ms
Enter
Wait+Screen@180s /Assistant:[\s\S]*You:/
Sleep 5s
