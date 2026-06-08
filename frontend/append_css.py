css = """
.flashcard-empty-state {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--text-muted);
}

/* Flashcard 3D Flip Effects */
.flashcard-container {
  perspective: 1000px;
  width: 100%;
  max-width: 600px;
  height: 350px;
  margin: var(--spacing-xl) auto;
  cursor: pointer;
}

.flashcard {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1);
  transform-style: preserve-3d;
}

.flashcard.flipped {
  transform: rotateY(180deg);
}

.flashcard-front, .flashcard-back {
  width: 100%;
  height: 100%;
  position: absolute;
  backface-visibility: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  background: var(--bg-tertiary);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-md);
  text-align: center;
}

.flashcard-back {
  transform: rotateY(180deg);
  background: var(--bg-secondary);
  border-color: var(--primary-main);
}

.flashcard-label {
  position: absolute;
  top: var(--spacing-md);
  left: var(--spacing-md);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--primary-main);
}

.flashcard-text {
  font-size: 1.25rem;
  line-height: 1.6;
  color: var(--text-primary);
}

.flashcard-hint {
  position: absolute;
  bottom: var(--spacing-md);
  font-size: 0.85rem;
  color: var(--text-muted);
}

.flashcard-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.flashcard-progress {
  font-weight: 500;
  color: var(--text-secondary);
  min-width: 80px;
  text-align: center;
}
"""

with open('C:/AI Study Assistant/frontend/src/App.css', 'a', encoding='utf-8') as f:
    f.write(css)
print("CSS appended successfully.")
