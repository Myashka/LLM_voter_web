function convertCritToBoolean() {
  let criteria = [
    "relevance_",
    "correctness_",
    "usefulness_",
    "justification_",
  ];

  criteria.forEach((prefix) => {
    let radios = document.querySelectorAll(`[name^="${prefix}"]:checked`);
    radios.forEach((radio) => {
      if (radio.value === "true") {
        radio.value = true;
      } else if (radio.value === "false") {
        radio.value = false;
      }
    });
  });
}

function beforeSubmit() {
  if (hasDuplicateRanks()) {
    alert("Please ensure that all ranks are unique.");
    return false;
  }
  return true;
}

function validateForm(event) {
  let totalGeneratedAnswers = document.querySelectorAll(".answer-block").length;

  let relevanceChecked = document.querySelectorAll(
    '[name^="relevance_"]:checked'
  ).length;
  let correctnessChecked = document.querySelectorAll(
    '[name^="correctness_"]:checked'
  ).length;
  let usefulnessChecked = document.querySelectorAll(
    '[name^="usefulness_"]:checked'
  ).length;
  let justificationChecked = document.querySelectorAll(
    '[name^="justification_"]:checked'
  ).length;
  let ranksChecked = document.querySelectorAll(
    '[name^="rating_"]:checked'
  ).length;

  if (
    relevanceChecked === totalGeneratedAnswers &&
    correctnessChecked === totalGeneratedAnswers &&
    usefulnessChecked === totalGeneratedAnswers &&
    justificationChecked === totalGeneratedAnswers &&
    ranksChecked === totalGeneratedAnswers &&
    !hasDuplicateRanks()
  ) {
    document.getElementById("submit").disabled = false;
  } else {
    document.getElementById("submit").disabled = true;
  }
}

function hasDuplicateRanks() {
  let ranks = document.querySelectorAll('[name^="rating_"]:checked');
  let rankValues = [...ranks].map((rank) => rank.value);
  return new Set(rankValues).size !== rankValues.length;
}

function updateAnswerColor(radioInput) {
  let answerBlock = radioInput.closest(".answer-block");
  if (radioInput.value === "true") {
    answerBlock.classList.add("bg-success-light");
    answerBlock.classList.remove("bg-danger-light");
  } else if (radioInput.value === "false") {
    answerBlock.classList.add("bg-danger-light");
    answerBlock.classList.remove("bg-success-light");
  } else {
    answerBlock.classList.remove("bg-danger-light", "bg-success-light");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  let criteria = [
    '[name^="relevance_"]',
    '[name^="correctness_"]',
    '[name^="usefulness_"]',
    '[name^="justification_"]',
    '[name^="rating_"]',
  ];

  criteria.forEach((selector) => {
    document.querySelectorAll(selector).forEach((radio) => {
      radio.addEventListener("click", validateForm);
    });
  });
});