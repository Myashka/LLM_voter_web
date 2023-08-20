function beforeSubmit() {
  convertRightsToBoolean();
  if (hasDuplicateRanks()) {
    alert("Please ensure that all ranks are unique.");
    return false;
  }
  return true;
}

function validateForm(event) {
  let totalGeneratedAnswers = document.querySelectorAll(".answer-block").length;

  let rightsChecked = document.querySelectorAll(
    '[name^="rights_"]:checked'
  ).length;
  let ranksChecked = document.querySelectorAll(
    '[name^="rating_"]:checked'
  ).length;

  if (
    rightsChecked === totalGeneratedAnswers &&
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

  validateForm();
}

document.addEventListener("DOMContentLoaded", function () {
  let rights = document.querySelectorAll('[name^="rights_"]');
  let ranks = document.querySelectorAll('[name^="rating_"]');

  rights.forEach((radio) => radio.addEventListener("click", validateForm));
  ranks.forEach((radio) => radio.addEventListener("click", validateForm));
});
