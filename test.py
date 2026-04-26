import matplotlib.pyplot as plt
import numpy as np

# Metrics
labels = ['Relevance', 'Coherence', 'Fluency']

# Your model (NeuroDialogue)
neuro_scores = [4.6, 4.2, 4.6]

# Baseline LLM
baseline_scores = [3.6, 3.7, 3.2]

# Radar setup
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
neuro_scores += neuro_scores[:1]
baseline_scores += baseline_scores[:1]
angles += angles[:1]

plt.figure()
ax = plt.subplot(111, polar=True)

# Your model (BLUE)
ax.plot(angles, neuro_scores, label="NeuroDialogue ")
ax.fill(angles, neuro_scores, alpha=0.15)

# Baseline model (RED)
ax.plot(angles, baseline_scores, label="Baseline LLM")
ax.fill(angles, baseline_scores, alpha=0.10)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)

ax.set_yticks([1, 2, 3, 4, 5])
ax.set_ylim(0, 5)

# Cleaner academic title
plt.title("Generation Quality Comparison\nNeuroDialogue Generation Module vs Baseline LLM")

# Better legend placement (inside chart, top right)
plt.legend(loc="upper right")

plt.show()