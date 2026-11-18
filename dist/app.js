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
    showToast(`Hint ${hintIndex + 1} of ${hints.length} — one step closer.`);
  } else {
    showToast('Nice work. Say the approach in your own words.');
  }
});

document.querySelector('#understand-button').addEventListener('click', () => showToast('Great. Explain your idea before you code it.'));

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
