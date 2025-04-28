const questionList = document.getElementById('question-list');
const addQuestionButton = document.getElementById('add-question-button');
const saveFormButton = document.getElementById('save-form-button');
const formNameInput = document.getElementById('form-name');

let questionCounter = 0;

addQuestionButton.addEventListener('click', () => {
    questionCounter++;
    const newQuestion = createQuestionElement(questionCounter);
    questionList.appendChild(newQuestion);
});

saveFormButton.addEventListener('click', () => {
    const formName = formNameInput.value;
    const questions = [];
    const questionItems = questionList.querySelectorAll('.question-item');

    questionItems.forEach(item => {
        const questionText = item.querySelector('.question-text').value;
        const questionType = item.querySelector('.question-type').value;
        const questionId = item.dataset.questionId;

        const questionData = {
            id: questionId,
            type: questionType,
            label: questionText,
        };

        if (questionType === 'radio' || questionType === 'checkbox') {
            const options = [];
            const optionInputs = item.querySelectorAll('.option-input');
            optionInputs.forEach(input => {
                options.push(input.value);
            });
            questionData.options = options;
        }

        questions.push(questionData);
    });

    if (!formName) {
        alert('Please enter a form name.');
        return;
    }
    if (questions.length === 0) {
        alert('Please add at least one question.');
        return;
    }


    const formData = {
        name: formName,
        questions: questions
    };

    fetch('/admin/save_form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Form saved successfully! Form ID: ' + data.form_id);
            window.location.href = '/admin/dashboard'; // Redirect to dashboard
        } else {
            alert('Error saving form: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the form.');
    });
});

function createQuestionElement(questionId) {
    const questionItem = document.createElement('li');
    questionItem.classList.add('question-item');
    questionItem.dataset.questionId = questionId;

    const questionContent = `
        <h3>Question ${questionId}</h3>
        <button class="question-item-delete">×</button>
        <label>Question Text:</label>
        <input type="text" class="question-text" placeholder="Enter question text" required>
        <label>Question Type:</label>
        <select class="question-type">
            <option value="text">Text Input</option>
            <option value="textarea">Textarea</option>
            <option value="radio">Multiple Choice</option>
            <option value="checkbox">Checkboxes</option>
        </select>
        <div class="question-options" style="display: none;">
            <label>Options:</label>
            <div class="option-group">
                <input type="text" class="option-input" placeholder="Option 1" required>
            </div>
            <div class="option-group">
                <input type="text" class="option-input" placeholder="Option 2" required>
            </div>
            <button class="add-option-button">Add Option</button>
        </div>
    `;
    questionItem.innerHTML = questionContent;

    const questionTypeSelect = questionItem.querySelector('.question-type');
    const questionOptionsDiv = questionItem.querySelector('.question-options');
    const addOptionButton = questionItem.querySelector('.add-option-button');
    const deleteButton = questionItem.querySelector('.question-item-delete');

    questionTypeSelect.addEventListener('change', () => {
        if (questionTypeSelect.value === 'radio' || questionTypeSelect.value === 'checkbox') {
            questionOptionsDiv.style.display = 'block';
            // Ensure the first two options are present
            const optionInputs = questionOptionsDiv.querySelectorAll('.option-input');
            if (optionInputs.length < 2) {
                if (!optionInputs[0]) {
                    const optionGroup1 = document.createElement('div');
                    optionGroup1.className = 'option-group';
                    optionGroup1.innerHTML = `<input type="text" class="option-input" placeholder="Option 1" required>`;
                    questionOptionsDiv.appendChild(optionGroup1);
                }
                if (!optionInputs[1]){
                    const optionGroup2 = document.createElement('div');
                    optionGroup2.className = 'option-group';
                    optionGroup2.innerHTML = `<input type="text" class="option-input" placeholder="Option 2" required>`;
                    questionOptionsDiv.appendChild(optionGroup2);
                }

            }
        } else {
            questionOptionsDiv.style.display = 'none';
        }
    });

    addOptionButton.addEventListener('click', () => {
        const newOptionGroup = document.createElement('div');
        newOptionGroup.className = 'option-group';
        newOptionGroup.innerHTML = `<input type="text" class="option-input" placeholder="Option ${questionOptionsDiv.querySelectorAll('.option-group').length + 1}" required>`;
        questionOptionsDiv.appendChild(newOptionGroup);
    });

    deleteButton.addEventListener('click', () => {
        questionItem.remove();
    });

    return questionItem;
}
