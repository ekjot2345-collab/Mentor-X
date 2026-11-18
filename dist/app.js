const hints = [
  "Before you reach for nested loops, pause. What information from each number could make the next lookup feel instant?",
  "If you have already seen a number, you can ask whether its complement has appeared. What would you store to answer that quickly?",
  "Sketch a map: number → its index. As you scan, check target − current number before you add the current number.",
  "Now explain why checking before inserting avoids using the same element twice. You have the shape of the O(n) solution."
];

let hintIndex = 0;
const hintButton = document.querySelector('#next-hint');
const hintCopy = document.querySelector('#hint-copy');
const toast = document.querySelector('#toast');
const stages = [...document.querySelectorAll('.hint-stage span')];

// MentorX USP: turn observable learning friction into the gentlest useful intervention.
// The MVP keeps this local; a production Python service can receive the same event data.
const struggleEngine = {
  state: { minutesStuck: 38, retries: 2, hintRequests: 0, recoverySignals: 0 },
  score() {
    const { minutesStuck, retries, hintRequests, recoverySignals } = this.state;
    const timeWeight = Math.min(minutesStuck / 45, 1) * 34;
    const retryWeight = Math.min(retries / 4, 1) * 28;
    const hintWeight = Math.min(hintRequests / 3, 1) * 28;
    const recoveryCredit = Math.min(recoverySignals / 2, 1) * 18;
    return Math.max(0, Math.min(100, Math.round(timeWeight + retryWeight + hintWeight - recoveryCredit)));
  },
  recommendation(score) {
    if (score >= 72) return { label: 'Guided reset', title: 'Recommended next move', copy: 'Pause the solution path. Ask the learner to name the input, target, and one useful lookup in their own words.' };
    if (score >= 45) return { label: 'Gentle pause', title: 'Recommended next move', copy: 'Ask a question that narrows the search space without naming the data structure.' };
    return { label: 'Momentum found', title: 'Momentum detected', copy: 'Invite the learner to sketch the approach, then validate the reasoning before they code.' };
  },
  render() {
    const score = this.score();
    const advice = this.recommendation(score);
    document.querySelector('#friction-score').textContent = score;
    document.querySelector('#friction-bar').style.width = `${score}%`;
    document.querySelector('#friction-label').textContent = advice.label;
    document.querySelector('#time-signal').textContent = `${this.state.minutesStuck}m`;
    document.querySelector('#retry-signal').textContent = this.state.retries;
    document.querySelector('#hint-signal').textContent = this.state.hintRequests;
    document.querySelector('#cue-title').textContent = advice.title;
    document.querySelector('#cue-copy').textContent = advice.copy;
  },
  record(signal) {
    this.state[signal] += 1;
    this.render();
  }
};

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2600);
}

function setHint(index) {
  hintIndex = index;
  hintCopy.textContent = hints[index];
  stages.forEach((stage, stageIndex) => stage.classList.toggle('active', stageIndex === index));
  hintButton.innerHTML = index === hints.length - 1 ? 'Reflect on the approach <span>→</span>' : 'I need another hint <span>→</span>';
}

hintButton.addEventListener('click', () => {
  if (hintIndex < hints.length - 1) {
    setHint(hintIndex + 1);
    struggleEngine.record('hintRequests');
    showToast(`Hint ${hintIndex + 1} of ${hints.length} — one step closer.`);
  } else {
    showToast('Nice work. Say the approach in your own words.');
  }
});

document.querySelector('#understand-button').addEventListener('click', () => {
  struggleEngine.record('recoverySignals');
  showToast('Great. Explain your idea before you code it.');
});

document.querySelector('#retry-button').addEventListener('click', () => {
  struggleEngine.record('retries');
  showToast('Retry signal noted — MentorX will narrow the next prompt.');
});

document.querySelector('#breakthrough-button').addEventListener('click', () => {
  struggleEngine.record('recoverySignals');
  showToast('Momentum detected — shift from hints to explanation.');
});

document.querySelectorAll('.topic-card').forEach((card) => {
  card.addEventListener('click', () => {
    document.querySelectorAll('.topic-card').forEach((item) => item.classList.remove('selected'));
    card.classList.add('selected');
    document.querySelector('#problem-title').textContent = card.dataset.title;
    document.querySelector('#problem-context').textContent = card.dataset.context;
    hints[0] = card.dataset.hint;
    setHint(0);
    document.querySelector('#mentor-space').scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
});

struggleEngine.render();
